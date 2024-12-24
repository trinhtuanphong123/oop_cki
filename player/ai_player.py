# ai/ai_player.py
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from .player import Player, PieceColor, PlayerStatus
from core.game_state import GameState 
from core.move import Move
from core.board import Board
from core.pieces.piece import Piece
from ai.chess_ai import AIStrategy

class AILevel(Enum):
    """Định nghĩa các cấp độ AI"""
    BEGINNER = 1     # Chỉ random moves
    EASY = 2         # Minimax độ sâu 2
    MEDIUM = 3       # Minimax độ sâu 3 + basic evaluation
    HARD = 4         # Minimax độ sâu 4 + advanced evaluation
    EXPERT = 5       # Minimax độ sâu 5 + full features

@dataclass
class AIConfig:
    """Cấu hình cho AI"""
    depth: int
    thinking_time: float
    use_opening_book: bool
    use_endgame_tablebase: bool
    evaluation_weights: Dict[str, float]

@dataclass
class MoveAnalysis:
    """Kết quả phân tích nước đi"""
    move: Move
    score: float
    depth: int
    nodes_searched: int
    time_spent: float
    principle_variation: List[Move]

class AIPlayer(Player):
    """
    Class AI Player trong hệ thống cờ vua.
    Sử dụng các chiến thuật khác nhau tùy theo cấp độ.
    """
    def __init__(self, 
                 name: str, 
                 color: PieceColor,
                 level: AILevel = AILevel.MEDIUM,
                 strategy: Optional['AIStrategy'] = None):
        """
        Khởi tạo AI Player
        Args:
            name: Tên AI
            color: Màu quân
            level: Cấp độ AI
            strategy: Chiến thuật cụ thể (optional)
        """
        super().__init__(name, color, f"ai_{name}", is_human=False)
        
        # AI specific attributes
        self._level = level
        self._strategy = strategy or self._get_default_strategy(level)
        self._config = self._get_default_config(level)
        
        # Performance tracking
        self._moves_analyzed = 0
        self._total_time_spent = 0.0
        self._position_cache = {}
        
        # Game phase tracking
        self._is_opening = True
        self._is_endgame = False
        self._opening_book_moves = []

    @property
    def level(self) -> AILevel:
        return self._level

    @property 
    def analysis_stats(self) -> Dict:
        """Thống kê về phân tích của AI"""
        return {
            "moves_analyzed": self._moves_analyzed,
            "avg_time_per_move": (self._total_time_spent / self._moves_analyzed 
                                if self._moves_analyzed > 0 else 0),
            "cache_hits": len(self._position_cache)
        }

    def get_move(self, game_state: GameState) -> Optional[Move]:
        """Lấy nước đi tốt nhất từ AI"""
        start_time = time.time()

        # Kiểm tra phase của game
        self._update_game_phase(game_state)

        # Thử tìm trong opening book
        if self._is_opening and self._config.use_opening_book:
            book_move = self._get_opening_book_move(game_state)
            if book_move:
                return self._finish_move(book_move, start_time)

        # Thử tìm trong endgame tablebase
        if self._is_endgame and self._config.use_endgame_tablebase:
            tablebase_move = self._get_tablebase_move(game_state)
            if tablebase_move:
                return self._finish_move(tablebase_move, start_time)

        # Tìm nước đi tốt nhất bằng strategy
        analysis = self._strategy.find_best_move(
            game_state,
            self._config.depth,
            self._config.thinking_time,
            self._config.evaluation_weights
        )

        if analysis and analysis.move:
            self._update_stats(analysis)
            return self._finish_move(analysis.move, start_time)

        return None

    def set_level(self, level: AILevel) -> None:
        """Thay đổi cấp độ AI"""
        self._level = level
        self._config = self._get_default_config(level)
        self._strategy = self._get_default_strategy(level)

    def analyze_position(self, game_state: GameState) -> MoveAnalysis:
        """Phân tích chi tiết vị trí hiện tại"""
        return self._strategy.analyze_position(
            game_state,
            self._config.depth,
            self._config.thinking_time
        )

    def _update_game_phase(self, game_state: GameState) -> None:
        """Cập nhật phase của game"""
        piece_count = len(game_state.board.get_all_pieces())
        
        # Kiểm tra opening
        if game_state.move_count < 10:
            self._is_opening = True
        else:
            self._is_opening = False

        # Kiểm tra endgame
        if piece_count <= 7:  # Ví dụ: ít hơn 7 quân -> endgame
            self._is_endgame = True
        else:
            self._is_endgame = False

    def _get_default_config(self, level: AILevel) -> AIConfig:
        """Lấy cấu hình mặc định cho mỗi cấp độ"""
        configs = {
            AILevel.BEGINNER: AIConfig(
                depth=1,
                thinking_time=1.0,
                use_opening_book=False,
                use_endgame_tablebase=False,
                evaluation_weights={"material": 1.0}
            ),
            AILevel.EXPERT: AIConfig(
                depth=5,
                thinking_time=3.0,
                use_opening_book=True,
                use_endgame_tablebase=True,
                evaluation_weights={
                    "material": 1.0,
                    "position": 0.5,
                    "mobility": 0.3,
                    "king_safety": 0.4,
                    "pawn_structure": 0.3
                }
            )
        }
        return configs.get(level, configs[AILevel.MEDIUM])

    def _get_default_strategy(self, level: AILevel) -> 'AIStrategy':
        """Lấy chiến thuật mặc định cho mỗi cấp độ"""
        from ..ai.strategies import (RandomStrategy, MinimaxStrategy, 
                               AlphaBetaStrategy, IterativeDeepeningStrategy)
        
        strategies = {
            AILevel.BEGINNER: RandomStrategy(),
            AILevel.EASY: MinimaxStrategy(),
            AILevel.MEDIUM: AlphaBetaStrategy(),
            #AILevel.HARD: IterativeDeepeningStrategy(),
            #AILevel.EXPERT: IterativeDeepeningStrategy(use_transposition_table=True)
        }
        return strategies.get(level, strategies[AILevel.MEDIUM])

    def _update_stats(self, analysis: MoveAnalysis) -> None:
        """Cập nhật thống kê"""
        self._moves_analyzed += 1
        self._total_time_spent += analysis.time_spent
        
        # Cache position nếu có giá trị
        if analysis.score != 0:
            self._position_cache[analysis.move.get_position_key()] = analysis.score

    def _finish_move(self, move: Move, start_time: float) -> Move:
        """Hoàn thành việc chọn nước đi"""
        self.add_move(move)
        self._total_time_spent += time.time() - start_time
        return move

    def __str__(self) -> str:
        return (f"AI {self._name} (Level: {self._level.name}) - "
                f"Analyzed moves: {self._moves_analyzed}")