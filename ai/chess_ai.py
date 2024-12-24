# ai/chess_ai.py
from typing import Optional, List, Dict, Tuple, Type
from dataclasses import dataclass
from enum import Enum
import time
import logging

from ..core.move import Move
from ..core.game_state import GameState
from ..core.pieces.piece import Piece, PieceColor, PieceType
from ..core.board import Board

logger = logging.getLogger(__name__)

class AIEvaluationType(Enum):
    BASIC = "basic"           
    STANDARD = "standard"     
    ADVANCED = "advanced"     

@dataclass
class EvaluationConfig:
    material_weight: float = 1.0
    position_weight: float = 0.3
    pawn_structure_weight: float = 0.2
    center_control_weight: float = 0.1
    king_safety_weight: float = 0.2
    mobility_weight: float = 0.15
    development_weight: float = 0.1

class ChessAI:
    def __init__(self, evaluation_type: AIEvaluationType = AIEvaluationType.STANDARD):
        self._evaluation_type = evaluation_type
        self._config = EvaluationConfig()
        self._depth = 3
        self._position_cache: Dict[str, float] = {}
        self._evaluation_count = 0
        self._cache_hits = 0
        self._total_eval_time = 0.0

    def get_best_move(self, game_state: GameState, thinking_time: float) -> Optional[Move]:
        """Tìm nước đi tốt nhất trong thời gian cho phép"""
        start_time = time.time()
        best_move = None
        best_score = float('-inf')

        try:
            legal_moves = game_state.get_legal_moves_for_current_player()
            if not legal_moves:
                return None

            # Iterative deepening
            current_depth = 1
            while time.time() - start_time < thinking_time:
                current_score, current_move = self._minimax(
                    game_state,
                    current_depth,
                    float('-inf'),
                    float('inf'),
                    True
                )

                if current_score > best_score:
                    best_score = current_score
                    best_move = current_move

                current_depth += 1

        except TimeoutError:
            logger.info(f"AI search stopped at depth {current_depth}")
        except Exception as e:
            logger.error(f"Error in get_best_move: {e}")

        self._total_eval_time += time.time() - start_time
        return best_move

    def _minimax(self, game_state: GameState, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> Tuple[float, Optional[Move]]:
        """Minimax algorithm với alpha-beta pruning"""
        if depth == 0 or game_state.is_game_over():
            return self.evaluate_position(game_state), None

        legal_moves = game_state.get_legal_moves_for_current_player()
        if not legal_moves:
            return float('-inf') if is_maximizing else float('inf'), None

        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                game_state.make_move(move.start_square, move.end_square)
                eval_score, _ = self._minimax(game_state, depth - 1, alpha, beta, False)
                game_state.undo_last_move()

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                game_state.make_move(move.start_square, move.end_square)
                eval_score, _ = self._minimax(game_state, depth - 1, alpha, beta, True)
                game_state.undo_last_move()

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_position(self, game_state: GameState) -> float:
        """Đánh giá vị trí hiện tại"""
        self._evaluation_count += 1
        position_key = self._get_position_key(game_state)
        
        # Check cache
        if position_key in self._position_cache:
            self._cache_hits += 1
            return self._position_cache[position_key]

        score = 0.0
        board = game_state.board

        # Material evaluation (always included)
        score += self._evaluate_material(board) * self._config.material_weight

        # Position evaluation
        if self._evaluation_type != AIEvaluationType.BASIC:
            score += self._evaluate_position_control(board) * self._config.position_weight

        # Advanced evaluations
        if self._evaluation_type == AIEvaluationType.ADVANCED:
            score += self._evaluate_pawn_structure(board) * self._config.pawn_structure_weight
            score += self._evaluate_king_safety(board) * self._config.king_safety_weight
            score += self._evaluate_mobility(game_state) * self._config.mobility_weight

        self._position_cache[position_key] = score
        return score

    def _evaluate_material(self, board: Board) -> float:
        """Đánh giá giá trị vật chất"""
        piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0  # King's value not counted in material
        }
        
        score = 0
        for piece in board.get_all_pieces():
            value = piece_values[piece.piece_type]
            if piece.color == PieceColor.WHITE:
                score += value
            else:
                score -= value
        return score

    def _evaluate_position_control(self, board: Board) -> float:
        """Đánh giá kiểm soát vị trí"""
        score = 0
        for piece in board.get_all_pieces():
            if piece.color == PieceColor.WHITE:
                score += len(piece.get_possible_moves(board)) * 0.1
            else:
                score -= len(piece.get_possible_moves(board)) * 0.1
        return score

    def _evaluate_king_safety(self, board: Board) -> float:
        """Đánh giá an toàn của vua"""
        score = 0
        for piece in board.get_all_pieces():
            if piece.piece_type == PieceType.KING:
                # Đánh giá dựa trên số quân bảo vệ xung quanh vua
                protectors = len([p for p in board.get_pieces_around(piece.position) 
                                if p and p.color == piece.color])
                if piece.color == PieceColor.WHITE:
                    score += protectors * 0.2
                else:
                    score -= protectors * 0.2
        return score

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