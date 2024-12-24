# player/human_player.py

from typing import Optional, List
from .player import Player
from core.move import Move
from core.game_state import GameState
from core.pieces.piece import Piece, PieceColor
from core.square import Square

class HumanPlayer(Player):
    """
    Class đại diện cho người chơi thật.
    Chỉ tập trung xử lý các thao tác trong ván cờ.
    """
    def __init__(self, color: PieceColor):
        """
        Khởi tạo người chơi
        Args:
            color: Màu quân của người chơi (trắng/đen)
        """
        self._color = color
        self._selected_piece: Optional[Piece] = None
        self._legal_moves: List[Move] = []
        self._current_game: Optional[GameState] = None
        self._last_move: Optional[Move] = None

    def handle_square_click(self, clicked_square: Square, game_state: GameState) -> Optional[Move]:
        """
        Xử lý khi người chơi click vào một ô
        Args:
            clicked_square: Ô được click
            game_state: Trạng thái game hiện tại
        Returns:
            Move nếu là nước đi hợp lệ, None nếu chưa đủ thông tin
        """
        # Nếu chưa chọn quân
        if not self._selected_piece:
            # Kiểm tra xem ô có quân của mình không
            if (clicked_square.piece and 
                clicked_square.piece.color == self._color):
                # Chọn quân và lấy các nước đi hợp lệ
                self._selected_piece = clicked_square.piece
                self._legal_moves = game_state.get_legal_moves(self._selected_piece)
                return None
            return None

        # Nếu đã chọn quân trước đó
        if self._selected_piece:
            # Tạo nước đi từ vị trí đã chọn đến ô được click
            potential_move = Move(
                self._selected_piece.position,
                clicked_square,
                self._selected_piece
            )

            # Kiểm tra nước đi có hợp lệ không
            if potential_move in self._legal_moves:
                # Reset selection và trả về nước đi
                self._last_move = potential_move
                self._reset_selection()
                return potential_move
            
            # Nếu click vào quân khác cùng màu -> đổi selection
            if (clicked_square.piece and 
                clicked_square.piece.color == self._color):
                self._selected_piece = clicked_square.piece
                self._legal_moves = game_state.get_legal_moves(self._selected_piece)
            else:
                # Click vào ô không hợp lệ -> reset selection
                self._reset_selection()
            
            return None

    def _reset_selection(self) -> None:
        """Reset lại trạng thái chọn quân"""
        self._selected_piece = None
        self._legal_moves.clear()

    @property
    def selected_piece(self) -> Optional[Piece]:
        """Quân cờ đang được chọn"""
        return self._selected_piece

    @property
    def legal_moves(self) -> List[Move]:
        """Các nước đi hợp lệ của quân đang chọn"""
        return self._legal_moves

    @property 
    def last_move(self) -> Optional[Move]:
        """Nước đi cuối cùng"""
        return self._last_move

    @property
    def color(self) -> PieceColor:
        """Màu quân của người chơi"""
        return self._color