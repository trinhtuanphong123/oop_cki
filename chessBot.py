from typing import Optional
from .player import Player, PieceColor
from .core.move import Move
from .core.game_rule import GameState
from ..ai.strategies import AIStrategy
from ..ai.strategies.random import RandomStrategy

class AIPlayer(Player):
    """
    Class đại diện cho người chơi AI trong cờ vua
    Attributes:
        _strategy: Chiến thuật AI được sử dụng
        _thinking_time: Thời gian suy nghĩ cho mỗi nước đi (giây)
        _depth: Độ sâu tìm kiếm cho các thuật toán như Minimax
    """
    def __init__(self, name: str, color: PieceColor, strategy: Optional[AIStrategy] = None):
        """
        Khởi tạo AI player
        Args:
            name: Tên của AI
            color: Màu quân của AI (trắng/đen)
            strategy: Chiến thuật AI sử dụng (mặc định là RandomStrategy)
        """
        super().__init__(name, color, is_human=False)
        self._strategy = strategy or RandomStrategy()
        self._thinking_time = 2.0  # Thời gian suy nghĩ mặc định (giây)
        self._depth = 3  # Độ sâu tìm kiếm mặc định

    # === PROPERTIES ===
    @property
    def strategy(self) -> AIStrategy:
        """Lấy chiến thuật hiện tại của AI"""
        return self._strategy

    @property
    def thinking_time(self) -> float:
        """Lấy thời gian suy nghĩ cho mỗi nước đi"""
        return self._thinking_time

    @property
    def depth(self) -> int:
        """Lấy độ sâu tìm kiếm hiện tại"""
        return self._depth

    # === PUBLIC METHODS ===
    def get_move(self, game_state: GameState) -> Optional[Move]:
        """
        Lấy nước đi từ AI sử dụng chiến thuật đã chọn
        Args:
            game_state: Trạng thái hiện tại của game
        Returns:
            Nước đi được chọn hoặc None nếu không có nước đi hợp lệ
        """
        # Sử dụng chiến thuật để tìm nước đi tốt nhất
        move = self._strategy.find_best_move(
            game_state,
            self._thinking_time,
            self._depth
        )

        if move:
            self.add_move(move)
        return move

    def set_strategy(self, strategy: AIStrategy) -> None:
        """
        Thay đổi chiến thuật của AI
        Args:
            strategy: Chiến thuật mới
        """
        self._strategy = strategy

    def set_difficulty(self, level: int) -> None:
        """
        Thiết lập độ khó cho AI
        Args:
            level: Độ khó (1-5)
        """
        # Map độ khó 1-5 thành các tham số phù hợp
        difficulty_settings = {
            1: {"depth": 1, "time": 1.0},
            2: {"depth": 2, "time": 1.5},
            3: {"depth": 3, "time": 2.0},
            4: {"depth": 4, "time": 2.5},
            5: {"depth": 5, "time": 3.0}
        }

        if level in difficulty_settings:
            settings = difficulty_settings[level]
            self._depth = settings["depth"]
            self._thinking_time = settings["time"]

    def set_thinking_time(self, seconds: float) -> None:
        """
        Thiết lập thời gian suy nghĩ cho mỗi nước đi
        Args:
            seconds: Thời gian tính bằng giây
        """
        if seconds > 0:
            self._thinking_time = seconds

    def set_depth(self, depth: int) -> None:
        """
        Thiết lập độ sâu tìm kiếm
        Args:
            depth: Độ sâu tìm kiếm (>= 1)
        """
        if depth >= 1:
            self._depth = depth

    def analyze_position(self, game_state: GameState) -> dict:
        """
        Phân tích vị trí hiện tại
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            Dict chứa thông tin phân tích (điểm đánh giá, nước đi tốt nhất, etc)
        """
        evaluation = self._strategy.evaluate_position(game_state)
        best_move = self.get_move(game_state)
        
        return {
            "evaluation": evaluation,
            "best_move": best_move,
            "depth": self._depth,
            "thinking_time": self._thinking_time
        }

    def reset(self) -> None:
        """Reset trạng thái AI player"""
        super().reset()
        # Reset các thông số AI về mặc định
        self._depth = 3
        self._thinking_time = 2.0

    # === STRING METHODS ===
    def __str__(self) -> str:
        return (f"AI {self._name} ({self._color.value}) - "
                f"Strategy: {self._strategy.__class__.__name__}, "
                f"Depth: {self._depth}")

    def __repr__(self) -> str:
        return (f"AIPlayer(name='{self._name}', color={self._color}, "
                f"strategy={self._strategy.__class__.__name__})")