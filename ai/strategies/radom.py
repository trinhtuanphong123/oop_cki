# ai/strategies/random.py

import random
from typing import Optional, List
from strategies import AIStrategy
from ...core.move import Move
from ...core.game_rule import GameState
from ...core.pieces.piece import Piece, PieceColor

class RandomStrategy(AIStrategy):
    """
    Chiến thuật chọn nước đi ngẫu nhiên
    Đây là chiến thuật đơn giản nhất, thường dùng để test hoặc làm baseline
    """

    def find_best_move(self, game_state: GameState, time_limit: float, depth: int) -> Optional[Move]:
        """
        Chọn một nước đi ngẫu nhiên từ tất cả các nước đi hợp lệ
        Args:
            game_state: Trạng thái hiện tại của game
            time_limit: Thời gian suy nghĩ (không sử dụng trong random)
            depth: Độ sâu tìm kiếm (không sử dụng trong random)
        Returns:
            Một nước đi ngẫu nhiên hoặc None nếu không có nước đi hợp lệ
        """
        legal_moves = self._get_all_legal_moves(game_state)
        
        if not legal_moves:
            return None
            
        # Ưu tiên các nước đặc biệt với tỷ lệ cao hơn
        weighted_moves = []
        for move in legal_moves:
            weight = self._get_move_weight(move, game_state)
            weighted_moves.append((move, weight))
            
        # Chọn nước đi dựa trên trọng số
        total_weight = sum(weight for _, weight in weighted_moves)
        if total_weight == 0:
            return random.choice(legal_moves)
            
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        for move, weight in weighted_moves:
            current_weight += weight
            if current_weight >= r:
                return move
                
        return random.choice(legal_moves)

    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí hiện tại
        Args:
            game_state: Trạng thái cần đánh giá
        Returns:
            Điểm đánh giá ngẫu nhiên (để duy trì tính ngẫu nhiên của chiến thuật)
        """
        # Random strategy không quan tâm đến đánh giá vị trí
        # nhưng vẫn trả về giá trị dựa trên material để tuân thủ interface
        return self._evaluate_material(game_state)

    def _get_all_legal_moves(self, game_state: GameState) -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ cho người chơi hiện tại
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        current_player = game_state.current_player
        
        for piece in game_state.board.get_pieces(current_player):
            moves = game_state.get_legal_moves(piece)
            legal_moves.extend(moves)
            
        return legal_moves

    def _get_move_weight(self, move: Move, game_state: GameState) -> float:
        """
        Tính trọng số cho một nước đi để ưu tiên các nước đi đặc biệt
        Args:
            move: Nước đi cần tính trọng số
            game_state: Trạng thái game hiện tại
        Returns:
            Trọng số của nước đi (càng cao càng được ưu tiên)
        """
        weight = 1.0  # Trọng số cơ bản

        # Tăng trọng số cho các nước đi đặc biệt
        if move.is_capture:
            captured_value = self._get_piece_value(move.captured_piece.piece_type)
            moving_value = self._get_piece_value(move.moving_piece.piece_type)
            
            # Ưu tiên cao cho việc ăn quân có giá trị cao bằng quân có giá trị thấp
            if captured_value > moving_value:
                weight += (captured_value - moving_value) * 0.1
            
            # Cộng thêm trọng số cơ bản cho mọi nước ăn quân
            weight += 2.0

        # Ưu tiên phong tốt
        if move.is_promotion:
            weight += 5.0

        # Ưu tiên nước chiếu
        if game_state.causes_check(move):
            weight += 3.0

        # Ưu tiên kiểm soát trung tâm trong giai đoạn đầu
        if not self._is_endgame(game_state):
            end_row, end_col = move.end_square.row, move.end_square.col
            if 2 <= end_row <= 5 and 2 <= end_col <= 5:
                weight += 0.5

        return weight

    def __str__(self) -> str:
        return "Random Strategy"

    def __repr__(self) -> str:
        return "RandomStrategy()"