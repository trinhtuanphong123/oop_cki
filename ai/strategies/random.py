# ai/strategies/random.py

import random
from typing import Optional, List, Callable
from .strategies import AIStrategy
from ...core.move import Move
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor, PieceType

class RandomStrategy(AIStrategy):
    """
    Chiến thuật chọn nước đi ngẫu nhiên.
    Dùng cho cấp độ beginner hoặc testing.
    """

    def find_best_move(self, 
                       game_state: GameState, 
                       time_limit: float, 
                       depth: int,
                       evaluation_fn: Callable[[GameState], float]) -> Optional[Move]:
        """
        Chọn nước đi ngẫu nhiên với trọng số
        Args:
            game_state: Trạng thái hiện tại
            time_limit: Thời gian giới hạn (không sử dụng)
            depth: Độ sâu tìm kiếm (không sử dụng) 
            evaluation_fn: Hàm đánh giá (không sử dụng)
        Returns:
            Nước đi ngẫu nhiên được chọn
        """
        legal_moves = self._get_legal_moves(game_state)
        if not legal_moves:
            return None

        # Tạo danh sách nước đi có trọng số
        weighted_moves = []
        for move in legal_moves:
            weight = self._calculate_move_weight(move, game_state)
            weighted_moves.append((move, weight))

        # Chọn nước đi theo trọng số
        total_weight = sum(w for _, w in weighted_moves)
        if total_weight == 0:
            return random.choice(legal_moves)

        r = random.uniform(0, total_weight)
        cumulative_weight = 0

        for move, weight in weighted_moves:
            cumulative_weight += weight
            if cumulative_weight >= r:
                return move

        return random.choice(legal_moves)

    def analyze_position(self, 
                        game_state: GameState,
                        depth: int,
                        time_limit: float) -> dict:
        """
        Phân tích vị trí (đơn giản)
        Returns:
            Dict chứa thông tin cơ bản về vị trí
        """
        legal_moves = self._get_legal_moves(game_state)
        return {
            "legal_move_count": len(legal_moves),
            "capture_moves": sum(1 for m in legal_moves if m.is_capture),
            "check_moves": sum(1 for m in legal_moves if game_state.causes_check(m)),
            "is_endgame": self._is_endgame(game_state)
        }

    def _calculate_move_weight(self, move: Move, game_state: GameState) -> float:
        """
        Tính trọng số cho nước đi
        Returns:
            Trọng số (cao = ưu tiên cao)
        """
        weight = 1.0

        # Ưu tiên ăn quân
        if move.is_capture:
            weight += 3.0
            
        # Ưu tiên phong tốt    
        if move.is_promotion:
            weight += 4.0

        # Ưu tiên nước chiếu
        if game_state.is_check():
            weight += 2.0

        # Ưu tiên kiểm soát trung tâm
        end_pos = move.end_square
        if 2 <= end_pos.row <= 5 and 2 <= end_pos.col <= 5:
            weight += 0.5

        return weight

    def __str__(self) -> str:
        return "Random Strategy"