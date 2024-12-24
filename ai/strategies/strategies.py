# ai/strategies/__init__.py

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Callable
from ...core.move import Move 
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor, PieceType

class AIStrategy(ABC):
    """
    Interface cho các chiến thuật AI cờ vua.
    Định nghĩa các phương thức cơ bản cho mọi chiến thuật.
    """
    
    @abstractmethod
    def find_best_move(self, 
                       game_state: GameState, 
                       time_limit: float, 
                       depth: int,
                       evaluation_fn: Callable[[GameState], float]) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất cho vị trí hiện tại
        Args:
            game_state: Trạng thái hiện tại của game
            time_limit: Thời gian tối đa cho phép suy nghĩ (giây)
            depth: Độ sâu tìm kiếm tối đa
            evaluation_fn: Hàm đánh giá vị trí
        Returns:
            Nước đi tốt nhất hoặc None
        """
        pass

    def analyze_position(self, 
                        game_state: GameState,
                        depth: int,
                        time_limit: float) -> dict:
        """
        Phân tích chi tiết vị trí
        Args:
            game_state: Trạng thái cần phân tích
            depth: Độ sâu phân tích
            time_limit: Thời gian giới hạn
        Returns:
            Dict chứa thông tin phân tích
        """
        pass

    def _get_legal_moves(self, game_state: GameState) -> List[Move]:
        """Lấy danh sách nước đi hợp lệ"""
        return game_state.get_legal_moves(game_state.current_player)

    def _sort_moves(self, moves: List[Move], game_state: GameState) -> List[Move]:
        """
        Sắp xếp nước đi theo độ ưu tiên
        """
        def move_score(move: Move) -> float:
            score = 0.0
            
            # Capture moves
            if move.is_capture:
                score += 10.0
                
            # Promotion
            if move.is_promotion:
                score += 8.0
                
            # Center control
            if move.end_square.is_center():
                score += 2.0
                
            # Development
            if not move.moving_piece.has_moved:
                score += 1.0
                
            return score
            
        return sorted(moves, key=move_score, reverse=True)

    def _is_endgame(self, game_state: GameState) -> bool:
        """
        Kiểm tra giai đoạn tàn cuộc
        """
        piece_count = len(game_state.board.get_all_pieces())
        queen_count = len([p for p in game_state.board.get_all_pieces() 
                         if p.piece_type == PieceType.QUEEN])
        
        return piece_count <= 12 or queen_count == 0

    def _is_quiet_position(self, game_state: GameState) -> bool:
        """
        Kiểm tra vị trí yên tĩnh (không có captures/checks)
        """
        for move in self._get_legal_moves(game_state):
            if move.is_capture or game_state.is_check():
                return False
        return True

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Strategy"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"