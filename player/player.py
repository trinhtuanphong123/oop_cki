# player/player.py

from abc import ABC, abstractmethod
from typing import Optional, List
from core.pieces.piece import PieceColor
from core.move import Move
from core.game_state import GameState

class Player(ABC):
    """
    Class trừu tượng đại diện cho một người chơi trong ván cờ.
    Định nghĩa interface cơ bản cho cả Human và AI player.
    """
    def __init__(self, color: PieceColor):
        """
        Khởi tạo player
        Args:
            color: Màu quân của player (trắng/đen)
        """
        self._color = color
        self._current_game: Optional[GameState] = None
        self._last_move: Optional[Move] = None

    @property
    def color(self) -> PieceColor:
        """Màu quân của player"""
        return self._color

    @property
    def last_move(self) -> Optional[Move]:
        """Nước đi cuối cùng của player"""
        return self._last_move

    @property
    def current_game(self) -> Optional[GameState]:
        """Game state hiện tại"""
        return self._current_game

    @current_game.setter 
    def current_game(self, game_state: GameState) -> None:
        """Set game state mới"""
        self._current_game = game_state

    def can_move(self) -> bool:
        """Kiểm tra có phải lượt của player không"""
        return (self._current_game and 
                self._current_game.current_player == self._color)

    @abstractmethod
    def get_move(self, game_state: GameState) -> Optional[Move]:
        """
        Lấy nước đi của player
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            Nước đi được chọn hoặc None
        """
        pass