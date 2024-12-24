from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING
from datetime import datetime
from core.pieces.piece import Piece,PieceColor
from core.move import Move
from core.game_rule import GameRule
from core.game_state import GameState
from core.board import Board

if TYPE_CHECKING:
    from core.square import Square

class PlayerStatus(Enum):
    """Trạng thái của người chơi"""
    ONLINE = "online"
    OFFLINE = "offline"
    IN_GAME = "in_game"
    SPECTATING = "spectating"

class PlayerStats:
    """Class lưu trữ thống kê của người chơi"""
    def __init__(self):
        self.games_played: int = 0
        self.games_won: int = 0
        self.games_lost: int = 0
        self.games_drawn: int = 0
        self.rating: int = 1200  # Elo rating
        self.win_streak: int = 0
        self.best_win_streak: int = 0
        self.total_pieces_captured: int = 0
        self.total_moves_made: int = 0
        self.average_move_time: float = 0
        self.last_active: datetime = datetime.utcnow()

class Player(ABC):
    """
    Class đại diện cho người chơi trong hệ thống
    Attributes:
        _user_id: ID người dùng trong hệ thống
        _username: Tên đăng nhập
        _display_name: Tên hiển thị
        _email: Email người dùng
        _status: Trạng thái người chơi
        _stats: Thống kê người chơi
    """
    def __init__(self, user_id: str, username: str, display_name: str, email: str):
        # Thông tin người dùng
        self._user_id = user_id
        self._username = username
        self._display_name = display_name
        self._email = email
        
        # Trạng thái game hiện tại
        self._color: Optional[PieceColor] = None
        self._status = PlayerStatus.ONLINE
        self._is_in_check = False
        self._selected_piece: Optional[Piece] = None
        self._legal_moves: List[Move] = []
        self._last_move: Optional[Move] = None
        self._move_start_time: Optional[datetime] = None
        
        # Thống kê và lịch sử
        self._stats = PlayerStats()
        self._current_game_moves: List[Move] = []
        self._captured_pieces: List[Piece] = []
        self._current_game_score = 0

        # Cài đặt người chơi
        self._preferences = {
            'show_legal_moves': True,
            'auto_queen_promotion': True,
            'move_confirmation': False,
            'sound_enabled': True,
            'animation_speed': 1.0
        }

    # === PROPERTIES ===
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def status(self) -> PlayerStatus:
        return self._status

    @property
    def stats(self) -> PlayerStats:
        return self._stats

    @property
    def selected_piece(self) -> Optional[Piece]:
        return self._selected_piece

    # === GAME INTERACTION METHODS ===
    def handle_square_click(self, square: 'Square', game_state: GameState) -> Optional[Move]:
        """
        Xử lý khi người chơi click vào một ô
        Args:
            square: Ô được click
            game_state: Trạng thái game hiện tại
        Returns:
            Move nếu là nước đi hợp lệ, None nếu không
        """
        if not self._is_my_turn(game_state):
            return None

        # Nếu đã chọn quân cờ trước đó
        if self._selected_piece:
            # Thử thực hiện nước đi
            move = self._try_make_move(square, game_state)
            if move:
                self._handle_successful_move(move)
                return move
            # Nếu click vào quân của mình, chọn quân mới
            elif square.piece and square.piece.color == self._color:
                self._select_piece(square.piece, game_state)
            # Click vào ô không hợp lệ, bỏ chọn
            else:
                self._deselect_piece()
        # Chọn quân mới
        elif square.piece and square.piece.color == self._color:
            self._select_piece(square.piece, game_state)

        return None

    def _select_piece(self, piece: Piece, game_state: GameState) -> None:
        """Chọn một quân cờ và tính các nước đi có thể"""
        self._selected_piece = piece
        self._legal_moves = game_state.get_legal_moves(piece)
        self._move_start_time = datetime.utcnow()

    def _deselect_piece(self) -> None:
        """Bỏ chọn quân cờ hiện tại"""
        self._selected_piece = None
        self._legal_moves.clear()
        self._move_start_time = None

    def _try_make_move(self, target_square: 'Square', game_state: GameState) -> Optional[Move]:
        """Thử thực hiện nước đi đến ô đích"""
        for move in self._legal_moves:
            if move.end_square == target_square:
                if move.needs_promotion():
                    move = self._handle_promotion(move)
                return move
        return None

    def _handle_successful_move(self, move: Move) -> None:
        """Xử lý sau khi thực hiện nước đi thành công"""
        self._last_move = move
        self._current_game_moves.append(move)
        self._update_move_statistics(move)
        self._deselect_piece()

    def _handle_promotion(self, move: Move) -> Move:
        """Xử lý phong cấp tốt"""
        from core.pieces.queen import Queen  # Import local để tránh circular
        if self._preferences['auto_queen_promotion']:
            move.promotion_piece = Queen
        else:
            # TODO: Hiện dialog cho người chơi chọn quân phong cấp
            move.promotion_piece = Queen
        return move

    # === GAME STATE METHODS ===
    def start_game(self, color: PieceColor) -> None:
        """Bắt đầu game mới"""
        self._color = color
        self._status = PlayerStatus.IN_GAME
        self._current_game_moves.clear()
        self._captured_pieces.clear()
        self._current_game_score = 0
        self._is_in_check = False
        self._stats.games_played += 1
        self._stats.last_active = datetime.utcnow()

    def end_game(self, result: str) -> None:
        """Kết thúc game và cập nhật thống kê"""
        if result == "win":
            self._stats.games_won += 1
            self._stats.win_streak += 1
            self._stats.best_win_streak = max(
                self._stats.win_streak,
                self._stats.best_win_streak
            )
        elif result == "loss":
            self._stats.games_lost += 1
            self._stats.win_streak = 0
        else:  # draw
            self._stats.games_drawn += 1

        self._status = PlayerStatus.ONLINE
        self._color = None

    # === HELPER METHODS ===
    def _is_my_turn(self, game_state: GameState) -> bool:
        """Kiểm tra có phải lượt của người chơi không"""
        return game_state.current_player == self._color

    def _update_move_statistics(self, move: Move) -> None:
        """Cập nhật thống kê sau mỗi nước đi"""
        if self._move_start_time:
            move_time = (datetime.utcnow() - self._move_start_time).total_seconds()
            total_time = self._stats.average_move_time * self._stats.total_moves_made
            self._stats.total_moves_made += 1
            self._stats.average_move_time = (total_time + move_time) / self._stats.total_moves_made

        if move.is_capture:
            self._stats.total_pieces_captured += 1
            self._captured_pieces.append(move.captured_piece)
            self._current_game_score += self._get_piece_value(move.captured_piece)

    def _get_piece_value(self, piece: Piece) -> int:
        """Lấy giá trị của quân cờ"""
        values = {'PAWN': 1, 'KNIGHT': 3, 'BISHOP': 3,
                 'ROOK': 5, 'QUEEN': 9, 'KING': 0}
        return values.get(piece.piece_type.upper(), 0)

    # === PREFERENCES METHODS ===
    def set_preference(self, key: str, value: any) -> None:
        """Cập nhật cài đặt người chơi"""
        if key in self._preferences:
            self._preferences[key] = value

    def get_preference(self, key: str) -> any:
        """Lấy giá trị cài đặt"""
        return self._preferences.get(key)

    # === REPRESENTATION ===
    def __str__(self) -> str:
        return f"{self._display_name} ({self._status.value})"

    def __repr__(self) -> str:
        return (f"Player(user_id='{self._user_id}', "
                f"username='{self._username}', "
                f"status={self._status})")