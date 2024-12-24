# board.py
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from .square import Square
from .pieces.piece import Piece, PieceColor, PieceType
from .pieces.pawn import Pawn
from .pieces.rook import Rook
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.queen import Queen
from .pieces.king import King

if TYPE_CHECKING:
    from .move import Move

class Board:
    """
    Class đại diện cho bàn cờ và quản lý trạng thái game.
    """

    def __init__(self):
        """Khởi tạo bàn cờ trống"""
        self._initialize_board()
        self._move_history: List['Move'] = []
        self._captured_pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }
        self._last_move: Optional['Move'] = None

    # Properties
    @property
    def last_move(self) -> Optional['Move']:
        """Nước đi cuối cùng"""
        return self._last_move

    @property
    def move_count(self) -> int:
        """Số nước đã đi"""
        return len(self._move_history)

    # Phương thức khởi tạo
    def _initialize_board(self) -> None:
        """Khởi tạo bàn cờ và các ô"""
        self._squares = [[Square(row, col) for col in range(8)] for row in range(8)]
        self._pieces = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }

    def setup_initial_position(self) -> None:
        """Thiết lập vị trí ban đầu của các quân cờ"""
        # Setup pawns
        for col in range(8):
            self._setup_piece(Pawn, PieceColor.WHITE, 6, col)
            self._setup_piece(Pawn, PieceColor.BLACK, 1, col)

        # Setup other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(piece_order):
            self._setup_piece(piece_class, PieceColor.WHITE, 7, col)
            self._setup_piece(piece_class, PieceColor.BLACK, 0, col)

    def _setup_piece(self, piece_class: type, color: PieceColor, row: int, col: int) -> None:
        """Đặt một quân cờ mới lên bàn"""
        square = self.get_square(row, col)
        piece = piece_class(color, square)
        self.place_piece(piece, square)

    def clear(self) -> None:
        """Xóa toàn bộ quân cờ khỏi bàn"""
        for row in range(8):
            for col in range(8):
                square = self.get_square(row, col)
                if square.piece:
                    self.remove_piece(square.piece)
        self._move_history.clear()
        self._captured_pieces[PieceColor.WHITE].clear()
        self._captured_pieces[PieceColor.BLACK].clear()
        self._last_move = None

    # Phương thức truy cập
    def get_square(self, row: int, col: int) -> Square:
        """Lấy ô tại vị trí cụ thể"""
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return self._squares[row][col]

    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        """Lấy quân cờ tại vị trí"""
        return self.get_square(row, col).piece

    def get_pieces(self, color: PieceColor) -> List[Piece]:
        """Lấy danh sách quân cờ theo màu"""
        return self._pieces[color].copy()

    def get_king(self, color: PieceColor) -> Optional[King]:
        """Lấy quân vua theo màu"""
        for piece in self._pieces[color]:
            if isinstance(piece, King):
                return piece
        return None

    def get_captured_pieces(self, color: PieceColor) -> List[Piece]:
        """Lấy danh sách quân bị bắt theo màu"""
        return self._captured_pieces[color].copy()

    # Phương thức quản lý quân cờ
    def place_piece(self, piece: Piece, square: Square) -> None:
        """Đặt quân cờ lên ô"""
        if square.piece:
            self.remove_piece(square.piece)
        
        square.place_piece(piece)
        piece.position = square
        
        if piece not in self._pieces[piece.color]:
            self._pieces[piece.color].append(piece)

    def remove_piece(self, piece: Piece) -> None:
        """Lấy quân cờ ra khỏi bàn"""
        if piece.position:
            piece.position.remove_piece()
        
        if piece in self._pieces[piece.color]:
            self._pieces[piece.color].remove(piece)

    def capture_piece(self, piece: Piece) -> None:
        """Bắt quân cờ"""
        self.remove_piece(piece)
        self._captured_pieces[piece.color].append(piece)

    # Phương thức di chuyển
    def make_move(self, move: 'Move') -> bool:
        """
        Thực hiện nước đi
        Returns:
            bool: True nếu thực hiện thành công
        """
        if move.execute(self):
            self._move_history.append(move)
            self._last_move = move
            return True
        return False

    def undo_last_move(self) -> Optional['Move']:
        """
        Hoàn tác nước đi cuối
        Returns:
            Move hoặc None nếu không có nước để hoàn tác
        """
        if not self._move_history:
            return None

        last_move = self._move_history.pop()
        last_move.undo(self)
        self._last_move = self._move_history[-1] if self._move_history else None
        return last_move

    # Phương thức kiểm tra
    def is_valid_position(self, row: int, col: int) -> bool:
        """Kiểm tra tọa độ có hợp lệ không"""
        return 0 <= row < 8 and 0 <= col < 8

    def is_square_attacked(self, square: Square, by_color: PieceColor) -> bool:
        """Kiểm tra ô có bị tấn công bởi màu cụ thể không"""
        for piece in self._pieces[by_color]:
            if piece.can_attack_square(square, self):
                return True
        return False

    def get_attacking_pieces(self, square: Square, by_color: PieceColor) -> List[Piece]:
        """Lấy danh sách quân đang tấn công một ô"""
        return [piece for piece in self._pieces[by_color]
                if piece.can_attack_square(square, self)]

    # Clone và representation
    def clone(self) -> 'Board':
        """Tạo bản sao của bàn cờ"""
        new_board = Board()
        for color in PieceColor:
            for piece in self._pieces[color]:
                square = new_board.get_square(
                    piece.position.row,
                    piece.position.col
                )
                new_piece = piece.__class__(piece.color, square)
                new_board.place_piece(new_piece, square)
        return new_board

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        result = []
        for row in range(8):
            row_str = []
            for col in range(8):
                piece = self.get_piece_at(row, col)
                row_str.append(str(piece) if piece else '.')
            result.append(' '.join(row_str))
        return '\n'.join(result)

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return f"Board(pieces={len(self._pieces[PieceColor.WHITE]) + len(self._pieces[PieceColor.BLACK])})"