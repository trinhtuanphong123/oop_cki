from typing import List, Optional
from enum import Enum
from core.pieces.piece import Piece, PieceColor, PieceType
from .board import Board
from .move import Move
from .square import Square
from .pieces.king import King
from .pieces.pawn import Pawn
from .pieces.bishop import Bishop
from .pieces.knight import Knight
from .pieces.rook import Rook
from .game_rule import GameRule

class GameState:
    """Quản lý trạng thái game cờ"""
    
    class Status(Enum):
        """Trạng thái của ván cờ"""
        ACTIVE = "active"         # Đang chơi
        CHECK = "check"          # Chiếu
        CHECKMATE = "checkmate"  # Chiếu hết
        STALEMATE = "stalemate"  # Hòa do hết nước đi
        DRAW = "draw"            # Hòa do các lý do khác

    def __init__(self, board: Board):
        # Khởi tạo trạng thái game
        self._board = board
        self._current_player = PieceColor.WHITE
        self._status = self.Status.ACTIVE
        self._last_move = None
        
        # Quản lý lịch sử
        self._move_count = 0
        self._fifty_move_counter = 0
        self._move_history = []
        self._position_history = []

    @property
    def board(self) -> Board:
        return self._board

    @property
    def current_player(self) -> PieceColor:
        return self._current_player

    @property
    def status(self) -> Status:
        return self._status

    @property
    def last_move(self) -> Optional[Move]:
        return self._last_move

    @property
    def is_game_over(self) -> bool:
        """Kiểm tra game kết thúc"""
        return self._status in (
            self.Status.CHECKMATE,
            self.Status.STALEMATE,
            self.Status.DRAW
        )

    def update_after_move(self, move: Move) -> None:
        """Cập nhật trạng thái sau nước đi"""
        # Cập nhật lịch sử
        self._move_count += 1
        self._move_history.append(move)
        self._last_move = move
        self._position_history.append(str(self._board))
        
        # Cập nhật fifty-move rule
        if isinstance(move.moving_piece, Pawn) or move.is_capture:
            self._fifty_move_counter = 0
        else:
            self._fifty_move_counter += 1

        # Chuyển lượt chơi
        self._current_player = self._current_player.opposite
        
        # Cập nhật trạng thái game
        self._update_status()

    def undo_last_move(self) -> Optional[Move]:
        """Hoàn tác nước đi cuối"""
        if not self._move_history:
            return None

        # Lấy và xóa nước đi cuối
        last_move = self._move_history.pop()
        self._position_history.pop()
        
        # Cập nhật trạng thái
        self._move_count -= 1
        self._last_move = self._move_history[-1] if self._move_history else None
        self._current_player = self._current_player.opposite
        self._update_status()
        
        return last_move

    def _update_status(self) -> None:
        """Cập nhật trạng thái game"""
        if GameRule.is_checkmate(self._board, self._current_player):
            self._status = self.Status.CHECKMATE
        elif GameRule.is_stalemate(self._board, self._current_player):
            self._status = self.Status.STALEMATE
        elif self._is_draw():
            self._status = self.Status.DRAW
        elif GameRule.is_check(self._board, self._current_player):
            self._status = self.Status.CHECK
        else:
            self._status = self.Status.ACTIVE

    def _is_draw(self) -> bool:
        """Kiểm tra điều kiện hòa"""
        return (
            self._fifty_move_counter >= 50 or
            GameRule.is_insufficient_material(self._board) or
            self._is_threefold_repetition()
        )

    def _is_threefold_repetition(self) -> bool:
        """Kiểm tra lặp vị trí 3 lần"""
        for position in self._position_history:
            if self._position_history.count(position) >= 3:
                return True
        return False

    def __str__(self) -> str:
        return (
            f"Game Status: {self._status.value}\n"
            f"Current Player: {self._current_player.value}\n"
            f"Move Count: {self._move_count}"
        )