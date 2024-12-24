# ai/chess_ai.py
from typing import Optional, List, Dict, Tuple, Type
from dataclasses import dataclass
from enum import Enum, auto
import time
import logging

# Absolute imports thay vì relative imports
from core.move import Move
from core.game_state import GameState
from core.pieces.piece import Piece, PieceColor, PieceType
from core.board import Board

logger = logging.getLogger(__name__)

class AILevel(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

@dataclass
class EvaluationConfig:
    """Cấu hình cho việc đánh giá vị trí"""
    material_weight: float = 1.0
    position_weight: float = 0.3
    pawn_structure_weight: float = 0.2
    center_control_weight: float = 0.1
    king_safety_weight: float = 0.2
    mobility_weight: float = 0.15

class ChessAi:
    """AI cho chess game với các mức độ khác nhau"""
    
    # Điểm cho từng loại quân
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }

    def __init__(self, level: AILevel = AILevel.MEDIUM):
        """
        Khởi tạo AI Strategy
        Args:
            level: Mức độ AI (EASY, MEDIUM, HARD)
        """
        self.level = level
        self._config = EvaluationConfig()
        self._position_cache: Dict[str, float] = {}
        
        # Độ sâu tìm kiếm theo level
        self._search_depth = {
            AILevel.EASY: 2,
            AILevel.MEDIUM: 3,
            AILevel.HARD: 4
        }[level]

    def get_best_move(self, game_state: GameState, thinking_time: float) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất trong thời gian cho phép
        Args:
            game_state: Trạng thái game hiện tại
            thinking_time: Thời gian suy nghĩ (giây)
        Returns:
            Nước đi tốt nhất hoặc None nếu không tìm thấy
        """
        start_time = time.time()
        best_move = None
        best_score = float('-inf')

        try:
            legal_moves = game_state.get_legal_moves_for_current_player()
            if not legal_moves:
                return None

            depth = self._search_depth
            for move in legal_moves:
                # Thử nước đi
                game_state.make_move(move)
                score = -self._minimax(game_state, depth-1, float('-inf'), float('inf'), False)
                game_state.undo_last_move()

                # Cập nhật nước đi tốt nhất
                if score > best_score:
                    best_score = score
                    best_move = move

                # Kiểm tra thời gian
                if time.time() - start_time > thinking_time:
                    break

        except Exception as e:
            logger.error(f"Error in get_best_move: {e}")
            return None

        return best_move

    def _minimax(self, game_state: GameState, depth: int, alpha: float, beta: float, 
                 maximizing: bool) -> float:
        """
        Thuật toán minimax với alpha-beta pruning
        """
        if depth == 0 or game_state.is_game_over():
            return self.evaluate_position(game_state)

        if maximizing:
            max_eval = float('-inf')
            for move in game_state.get_legal_moves_for_current_player():
                game_state.make_move(move)
                eval = self._minimax(game_state, depth-1, alpha, beta, False)
                game_state.undo_last_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in game_state.get_legal_moves_for_current_player():
                game_state.make_move(move)
                eval = self._minimax(game_state, depth-1, alpha, beta, True)
                game_state.undo_last_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_position(self, game_state: GameState) -> float:
        """Đánh giá vị trí"""
        board = game_state.board
        score = 0.0

        # Material evaluation
        for piece in board.get_all_pieces():
            piece_value = self.PIECE_VALUES[piece.piece_type]
            if piece.color == PieceColor.WHITE:
                score += piece_value
            else:
                score -= piece_value

        # Position evaluation
        score += self._evaluate_piece_positions(board)
        
        # Additional evaluations based on level
        if self.level != AILevel.EASY:
            score += self._evaluate_mobility(game_state)
            score += self._evaluate_king_safety(board)
            
        if self.level == AILevel.HARD:
            score += self._evaluate_pawn_structure(board)
            score += self._evaluate_center_control(board)

        return score

    def _evaluate_piece_positions(self, board: Board) -> float:
        """Đánh giá vị trí các quân"""
        score = 0.0
        # Implementation goes here
        return score

    def _evaluate_mobility(self, game_state: GameState) -> float:
        """Đánh giá khả năng di chuyển"""
        score = 0.0
        # Implementation goes here
        return score

    def _evaluate_king_safety(self, board: Board) -> float:
        """Đánh giá an toàn của vua"""
        score = 0.0
        # Implementation goes here
        return score

    def _evaluate_pawn_structure(self, board: Board) -> float:
        """Đánh giá cấu trúc tốt"""
        score = 0.0
        # Implementation goes here
        return score

    def _evaluate_center_control(self, board: Board) -> float:
        """Đánh giá kiểm soát trung tâm"""
        score = 0.0
        # Implementation goes here
        return score