# ai/strategies/negamax.py

import time
from typing import Optional, Tuple, List, Callable
from .strategies import AIStrategy
from ...core.move import Move
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor

class NegamaxStrategy(AIStrategy):
    """
    Chiến thuật sử dụng thuật toán Negamax với Alpha-Beta pruning.
    Phù hợp cho cấp độ trung bình và cao.
    """

    def __init__(self):
        self.CHECKMATE_SCORE = 100000
        self.STALEMATE_SCORE = 0
        self.nodes_searched = 0
        self.start_time = 0
        self.time_limit = 0

    def find_best_move(self, 
                       game_state: GameState, 
                       time_limit: float,
                       depth: int,
                       evaluation_fn: Callable[[GameState], float]) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất sử dụng Negamax
        Args:
            game_state: Trạng thái hiện tại
            time_limit: Thời gian giới hạn
            depth: Độ sâu tối đa
            evaluation_fn: Hàm đánh giá vị trí
        Returns:
            Nước đi tốt nhất
        """
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes_searched = 0
        
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        # Iterative deepening
        for current_depth in range(1, depth + 1):
            if self._is_out_of_time():
                break

            current_best_move = self._negamax_root(
                game_state,
                current_depth,
                alpha,
                beta,
                evaluation_fn
            )

            if current_best_move and not self._is_out_of_time():
                best_move = current_best_move

        return best_move

    def analyze_position(self,
                        game_state: GameState,
                        depth: int, 
                        time_limit: float) -> dict:
        """
        Phân tích chi tiết vị trí
        Returns:
            Dict chứa thông tin phân tích
        """
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes_searched = 0

        analysis = {
            "nodes_searched": 0,
            "depth_reached": 0,
            "best_line": [],
            "evaluation": 0,
            "time_spent": 0
        }

        for current_depth in range(1, depth + 1):
            if self._is_out_of_time():
                break

            move = self._negamax_root(
                game_state, 
                current_depth,
                float('-inf'),
                float('inf'),
                self._basic_evaluation
            )

            if not self._is_out_of_time():
                analysis["depth_reached"] = current_depth
                if move:
                    analysis["best_line"].append(str(move))

        analysis["nodes_searched"] = self.nodes_searched
        analysis["time_spent"] = time.time() - self.start_time

        return analysis

    def _negamax_root(self,
                      game_state: GameState,
                      depth: int,
                      alpha: float,
                      beta: float,
                      evaluation_fn: Callable[[GameState], float]) -> Optional[Move]:
        """First level of negamax search"""
        best_move = None
        max_score = float('-inf')

        for move in self._sort_moves(self._get_legal_moves(game_state), game_state):
            if self._is_out_of_time():
                break

            game_state.make_move(move)
            score = -self._negamax(
                game_state,
                depth - 1,
                -beta,
                -alpha,
                evaluation_fn
            )
            game_state.undo_move()

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_move

    def _negamax(self,
                 game_state: GameState,
                 depth: int,
                 alpha: float, 
                 beta: float,
                 evaluation_fn: Callable[[GameState], float]) -> float:
        """
        Negamax với alpha-beta pruning
        """
        self.nodes_searched += 1

        if self._is_out_of_time():
            return 0

        if depth == 0 or game_state.is_game_over():
            return evaluation_fn(game_state)

        max_score = float('-inf')

        for move in self._sort_moves(self._get_legal_moves(game_state), game_state):
            game_state.make_move(move)
            score = -self._negamax(
                game_state,
                depth - 1,
                -beta,
                -alpha,
                evaluation_fn
            )
            game_state.undo_move()

            max_score = max(max_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return max_score

    def _basic_evaluation(self, game_state: GameState) -> float:
        """Đánh giá cơ bản cho phân tích"""
        if game_state.is_checkmate():
            return -self.CHECKMATE_SCORE if game_state.is_white_turn() else self.CHECKMATE_SCORE
        if game_state.is_draw():
            return self.STALEMATE_SCORE
        
        return 0.0  # Để cho PositionEvaluator xử lý

    def _is_out_of_time(self) -> bool:
        """Kiểm tra thời gian"""
        return time.time() - self.start_time >= self.time_limit

    def __str__(self) -> str:
        return f"Negamax Strategy (nodes: {self.nodes_searched})"