# game_state.py
from typing import List, Optional, Dict, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
from .board import Board
from .pieces.piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from .move import Move
    from .square import Square
    from .pieces.king import King

class GameStatus(Enum):
    """Enum định nghĩa trạng thái game"""
    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"
    TIMEOUT = "timeout"

@dataclass
class GameStateMemento:
    """
    Lưu trữ trạng thái game để có thể khôi phục
    Sử dụng Memento pattern
    """
    board_state: Board
    current_player: PieceColor
    move_history: List['Move']
    status: GameStatus

class GameState:
    """
    Quản lý trạng thái và luồng game cờ vua
    """
    def __init__(self):
        """Khởi tạo game mới"""
        self._board = Board()
        self._current_player = PieceColor.WHITE
        self._status = GameStatus.ACTIVE
        self._move_history: List['Move'] = []
        self._state_history: List[GameStateMemento] = []
        self._initialize_game()

    # Properties
    @property
    def board(self) -> Board:
        """Bàn cờ hiện tại"""
        return self._board

    @property
    def current_player(self) -> PieceColor:
        """Người chơi hiện tại"""
        return self._current_player

    @property
    def status(self) -> GameStatus:
        """Trạng thái game"""
        return self._status

    @property
    def move_count(self) -> int:
        """Số nước đã đi"""
        return len(self._move_history)

    @property
    def last_move(self) -> Optional['Move']:
        """Nước đi cuối cùng"""
        return self._move_history[-1] if self._move_history else None

    # Khởi tạo game
    def _initialize_game(self) -> None:
        """Khởi tạo game mới"""
        self._board.setup_initial_position()
        self._update_game_status()

    def reset_game(self) -> None:
        """Reset game về trạng thái ban đầu"""
        self._board.clear()
        self._board.setup_initial_position()
        self._current_player = PieceColor.WHITE
        self._status = GameStatus.ACTIVE
        self._move_history.clear()
        self._state_history.clear()
        self._update_game_status()

    # Quản lý nước đi
    def make_move(self, start_square: 'Square', end_square: 'Square') -> bool:
        """
        Thực hiện nước đi từ người chơi
        Args:
            start_square: Ô xuất phát
            end_square: Ô đích
        Returns:
            bool: True nếu nước đi hợp lệ và thành công
        """
        # Lưu trạng thái hiện tại
        self._save_state()

        # Kiểm tra điều kiện cơ bản
        piece = start_square.piece
        if not piece or piece.color != self._current_player:
            return False

        # Tạo và thực hiện nước đi
        from .move import Move
        move = Move(start_square, end_square, piece)
        
        if self._is_valid_move(move):
            if self._board.make_move(move):
                self._move_history.append(move)
                self._switch_player()
                self._update_game_status()
                return True
        
        return False

    def _is_valid_move(self, move: 'Move') -> bool:
        """
        Kiểm tra nước đi có hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        """
        from .game_rule import GameRule
        return GameRule.is_valid_move(self._board, move, self._current_player)

    def undo_move(self) -> bool:
        """
        Hoàn tác nước đi cuối cùng
        Returns:
            bool: True nếu hoàn tác thành công
        """
        if not self._state_history:
            return False

        # Khôi phục trạng thái trước đó
        previous_state = self._state_history.pop()
        self._board = previous_state.board_state
        self._current_player = previous_state.current_player
        self._move_history = previous_state.move_history
        self._status = previous_state.status
        return True

    def _switch_player(self) -> None:
        """Chuyển lượt cho người chơi tiếp theo"""
        self._current_player = (PieceColor.BLACK 
                              if self._current_player == PieceColor.WHITE 
                              else PieceColor.WHITE)

    # Quản lý trạng thái game
    def _update_game_status(self) -> None:
        """Cập nhật trạng thái game"""
        from .game_rule import GameRule

        if GameRule.is_checkmate(self._board, self._current_player):
            self._status = GameStatus.CHECKMATE
        elif GameRule.is_stalemate(self._board, self._current_player):
            self._status = GameStatus.STALEMATE
        elif GameRule.is_insufficient_material(self._board):
            self._status = GameStatus.DRAW
        elif GameRule.is_check(self._board, self._current_player):
            self._status = GameStatus.CHECK
        else:
            self._status = GameStatus.ACTIVE

    def get_legal_moves(self, square: 'Square') -> List['Move']:
        """
        Lấy danh sách nước đi hợp lệ cho quân cờ tại ô
        Args:
            square: Ô chứa quân cờ cần lấy nước đi
        """
        from .game_rule import GameRule
        piece = square.piece
        if not piece or piece.color != self._current_player:
            return []
        return GameRule.get_legal_moves(self._board, piece)

    def is_game_over(self) -> bool:
        """Kiểm tra game đã kết thúc chưa"""
        return self._status in {
            GameStatus.CHECKMATE,
            GameStatus.STALEMATE,
            GameStatus.DRAW,
            GameStatus.RESIGNED,
            GameStatus.TIMEOUT
        }

    # Memento pattern
    def _save_state(self) -> None:
        """Lưu trạng thái hiện tại"""
        memento = GameStateMemento(
            board_state=self._board.clone(),
            current_player=self._current_player,
            move_history=self._move_history.copy(),
            status=self._status
        )
        self._state_history.append(memento)

    # String representation
    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return (f"GameState(player={self._current_player.value}, "
                f"status={self._status.value})")

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"GameState(player={self._current_player.value}, "
                f"status={self._status.value}, "
                f"moves={len(self._move_history)})")