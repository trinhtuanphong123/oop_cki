# ai/strategies/__init__.py

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from ...core.move import Move 
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor

class AIStrategy(ABC):
    """
    Interface cho các chiến thuật AI cờ vua
    Định nghĩa các phương thức mà mọi chiến thuật phải implement
    """
    
    @abstractmethod
    def find_best_move(self, game_state: GameState, time_limit: float, depth: int) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất cho vị trí hiện tại
        Args:
            game_state: Trạng thái hiện tại của game
            time_limit: Thời gian tối đa cho phép suy nghĩ (giây)
            depth: Độ sâu tìm kiếm tối đa
        Returns:
            Nước đi tốt nhất tìm được hoặc None nếu không có nước đi hợp lệ
        """
        pass

    @abstractmethod
    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá điểm số của vị trí hiện tại
        Args:
            game_state: Trạng thái cần đánh giá
        Returns:
            Điểm số đánh giá (dương = có lợi cho trắng, âm = có lợi cho đen)
        """
        pass

    def _get_legal_moves(self, game_state: GameState) -> List[Move]:
        """
        Lấy danh sách tất cả nước đi hợp lệ
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        for piece in game_state.board.get_pieces(game_state.current_player):
            legal_moves.extend(game_state.get_legal_moves(piece))
        return legal_moves

    def _is_endgame(self, game_state: GameState) -> bool:
        """
        Kiểm tra xem game có đang ở giai đoạn tàn cuộc không
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            True nếu là tàn cuộc, False nếu không
        """
        # Đếm tổng giá trị quân chủ chốt (không tính vua)
        major_pieces_value = 0
        for piece in game_state.board.get_all_pieces():
            if piece.piece_type not in ['KING', 'PAWN']:
                major_pieces_value += piece.get_piece_value()
        return major_pieces_value <= 1800  # Dưới ~2 xe hoặc tương đương

    def _get_piece_value(self, piece_type: str, is_endgame: bool = False) -> int:
        """
        Lấy giá trị của một loại quân cờ
        Args:
            piece_type: Loại quân cờ
            is_endgame: Có phải đang ở tàn cuộc không
        Returns:
            Giá trị của quân cờ
        """
        values = {
            'PAWN': 100,
            'KNIGHT': 320,
            'BISHOP': 330,
            'ROOK': 500,
            'QUEEN': 900,
            'KING': 20000 if not is_endgame else 19500
        }
        return values.get(piece_type, 0)

    def _sort_moves(self, moves: List[Move], game_state: GameState) -> List[Move]:
        """
        Sắp xếp các nước đi theo độ ưu tiên để cải thiện alpha-beta pruning
        Args:
            moves: Danh sách nước đi cần sắp xếp
            game_state: Trạng thái game hiện tại
        Returns:
            Danh sách nước đi đã sắp xếp
        """
        def move_value(move: Move) -> int:
            value = 0
            
            # Ưu tiên các nước ăn quân
            if move.is_capture:
                captured_value = self._get_piece_value(move.captured_piece.piece_type)
                moving_value = self._get_piece_value(move.moving_piece.piece_type)
                value += captured_value - moving_value/10
            
            # Ưu tiên phong tốt
            if move.is_promotion:
                value += 800
                
            # Ưu tiên các nước chiếu
            if game_state.causes_check(move):
                value += 300
                
            return value

        return sorted(moves, key=move_value, reverse=True)

    def _is_quiet_position(self, game_state: GameState) -> bool:
        """
        Kiểm tra xem vị trí có "yên tĩnh" không (không có trao đổi quân)
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            True nếu vị trí yên tĩnh, False nếu không
        """
        for move in self._get_legal_moves(game_state):
            if move.is_capture or game_state.causes_check(move):
                return False
        return True

    def _evaluate_material(self, game_state: GameState) -> float:
        """
        Đánh giá chênh lệch quân (material)
        Args:
            game_state: Trạng thái game cần đánh giá
        Returns:
            Điểm chênh lệch quân
        """
        score = 0
        is_endgame = self._is_endgame(game_state)
        
        for piece in game_state.board.get_all_pieces():
            value = self._get_piece_value(piece.piece_type, is_endgame)
            if piece.color == PieceColor.WHITE:
                score += value
            else:
                score -= value
                
        return score

    def _evaluate_piece_mobility(self, game_state: GameState) -> float:
        """
        Đánh giá khả năng di chuyển của các quân
        Args:
            game_state: Trạng thái game cần đánh giá
        Returns:
            Điểm đánh giá khả năng di chuyển
        """
        mobility_score = 0
        
        # Đếm số nước đi hợp lệ cho từng bên
        for color in [PieceColor.WHITE, PieceColor.BLACK]:
            move_count = 0
            for piece in game_state.board.get_pieces(color):
                move_count += len(game_state.get_legal_moves(piece))
            
            # Cộng/trừ điểm tùy theo màu
            multiplier = 1 if color == PieceColor.WHITE else -1
            mobility_score += multiplier * move_count * 0.1
            
        return mobility_score

    def __str__(self) -> str:
        return self.__class__.__name__