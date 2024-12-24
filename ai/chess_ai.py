# ai/chess_ai.py
from typing import Optional, List, Dict, Tuple, Type
from dataclasses import dataclass
from enum import Enum
import time

from ..core.move import Move
from ..core.game_state import GameState
from ..core.game_rule import GameRule
from ..core.pieces.piece import Piece, PieceColor, PieceType
from ..core.board import Board
from .strategies.strategies import AIStrategy
from .evaluation.position_tables import PositionTables
from .evaluation.evaluator import PositionEvaluator

class AIEvaluationType(Enum):
    """Các loại đánh giá vị trí"""
    BASIC = "basic"           # Chỉ đánh giá quân
    STANDARD = "standard"     # Đánh giá quân + vị trí
    ADVANCED = "advanced"     # Đánh giá đầy đủ các yếu tố

@dataclass
class EvaluationConfig:
    """Cấu hình cho việc đánh giá vị trí"""
    material_weight: float = 1.0
    position_weight: float = 0.3
    pawn_structure_weight: float = 0.2
    center_control_weight: float = 0.1
    king_safety_weight: float = 0.2
    mobility_weight: float = 0.15
    development_weight: float = 0.1

class ChessAI:
    """
    Class quản lý AI cờ vua.
    Cung cấp interface cho các chiến thuật và đánh giá vị trí.
    """
    def __init__(self, 
                 strategy: AIStrategy,
                 evaluation_type: AIEvaluationType = AIEvaluationType.STANDARD):
        """
        Khởi tạo Chess AI
        Args:
            strategy: Chiến thuật AI sử dụng
            evaluation_type: Loại đánh giá vị trí
        """
        self._strategy = strategy
        self._evaluation_type = evaluation_type
        self._evaluator = PositionEvaluator()
        self._position_tables = PositionTables()
        
        # Cấu hình
        self._config = EvaluationConfig()
        self._depth = 3
        
        # Cache và thống kê
        self._position_cache: Dict[str, float] = {}
        self._evaluation_count = 0
        self._cache_hits = 0
        self._total_eval_time = 0.0

    @property
    def stats(self) -> Dict:
        """Thống kê về hoạt động của AI"""
        return {
            "evaluations": self._evaluation_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": (self._cache_hits / self._evaluation_count 
                             if self._evaluation_count > 0 else 0),
            "average_eval_time": (self._total_eval_time / self._evaluation_count 
                                if self._evaluation_count > 0 else 0)
        }

    def get_best_move(self, 
                      game_state: GameState, 
                      thinking_time: float) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất
        Args:
            game_state: Trạng thái game hiện tại
            thinking_time: Thời gian suy nghĩ (giây)
        Returns:
            Nước đi tốt nhất hoặc None
        """
        start_time = time.time()
        
        # Kiểm tra cache
        position_key = self._get_position_key(game_state)
        if position_key in self._position_cache:
            self._cache_hits += 1
        
        # Tìm nước đi tốt nhất
        best_move = self._strategy.find_best_move(
            game_state,
            thinking_time,
            self._depth,
            self.evaluate_position
        )
        
        # Cập nhật thống kê
        self._total_eval_time += time.time() - start_time
        
        return best_move

    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí hiện tại
        Args:
            game_state: Trạng thái cần đánh giá
        Returns:
            Điểm số đánh giá
        """
        self._evaluation_count += 1
        start_time = time.time()

        # Kiểm tra cache
        position_key = self._get_position_key(game_state)
        if position_key in self._position_cache:
            self._cache_hits += 1
            return self._position_cache[position_key]

        # Tính điểm đánh giá
        score = 0.0
        
        # Material evaluation
        material_score = self._evaluator.evaluate_material(
            game_state.board,
            self._position_tables.piece_values
        )
        score += material_score * self._config.material_weight

        # Position evaluation
        if self._evaluation_type != AIEvaluationType.BASIC:
            position_score = self._evaluator.evaluate_positions(
                game_state.board,
                self._position_tables.position_tables
            )
            score += position_score * self._config.position_weight

        # Advanced evaluation
        if self._evaluation_type == AIEvaluationType.ADVANCED:
            # Pawn structure
            pawn_score = self._evaluator.evaluate_pawn_structure(game_state.board)
            score += pawn_score * self._config.pawn_structure_weight

            # Center control
            center_score = self._evaluator.evaluate_center_control(game_state.board)
            score += center_score * self._config.center_control_weight

            # King safety
            king_safety_score = self._evaluator.evaluate_king_safety(game_state.board)
            score += king_safety_score * self._config.king_safety_weight

            # Mobility
            mobility_score = self._evaluator.evaluate_mobility(game_state)
            score += mobility_score * self._config.mobility_weight

        # Cache kết quả
        self._position_cache[position_key] = score
        self._total_eval_time += time.time() - start_time

        return score

    def set_evaluation_weights(self, weights: Dict[str, float]) -> None:
        """Cập nhật trọng số đánh giá"""
        for key, value in weights.items():
            if hasattr(self._config, f"{key}_weight"):
                setattr(self._config, f"{key}_weight", value)

    def set_evaluation_type(self, eval_type: AIEvaluationType) -> None:
        """Thay đổi loại đánh giá"""
        self._evaluation_type = eval_type
        self._position_cache.clear()

    def _get_position_key(self, game_state: GameState) -> str:
        """Tạo key duy nhất cho vị trí"""
        board = game_state.board
        pieces = board.get_all_pieces()
        return "_".join(
            f"{p.piece_type.value}{p.color.value}{p.position.row}{p.position.col}"
            for p in sorted(pieces, key=lambda x: (x.position.row, x.position.col))
        )

    def clear_cache(self) -> None:
        """Xóa cache"""
        self._position_cache.clear()
        self._cache_hits = 0
        self._evaluation_count = 0
        self._total_eval_time = 0.0