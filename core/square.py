from dataclasses import dataclass
from typing import Optional, Tuple, List
from core.pieces.piece import Piece

@dataclass(frozen=True)
class Position:
    """
    Đại diện cho vị trí trên bàn cờ với ký hiệu đại số.
    Ví dụ: (0,0) -> 'a8', (7,7) -> 'h1'
    """
    row: int
    col: int

    def __post_init__(self):
        """Kiểm tra tính hợp lệ của vị trí sau khi khởi tạo"""
        if not self.is_valid():
            raise ValueError(f"Invalid position: ({self.row}, {self.col})")

    def is_valid(self) -> bool:
        """Kiểm tra vị trí có nằm trong bàn cờ không"""
        return 0 <= self.row <= 7 and 0 <= self.col <= 7

    @property
    def algebraic(self) -> str:
        """Chuyển đổi vị trí sang ký hiệu đại số cờ vua"""
        col_letter = chr(ord('a') + self.col)
        row_number = 8 - self.row
        return f"{col_letter}{row_number}"

    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """
        Tạo Position từ ký hiệu đại số.
        Ví dụ: 'e4' -> Position(4,4)
        """
        if not (len(notation) == 2 and 
                'a' <= notation[0] <= 'h' and 
                '1' <= notation[1] <= '8'):
            raise ValueError(f"Invalid algebraic notation: {notation}")

        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        return cls(row, col)

class Square:
    """
    Đại diện cho một ô trên bàn cờ.
    Quản lý vị trí, quân cờ và các thuộc tính của ô.
    """
    __slots__ = ['_position', '_piece', '_highlighted', '_legal_move']

    def __init__(self, row: int, col: int):
        """
        Khởi tạo ô với vị trí xác định.
        
        Args:
            row: Số hàng (0-7 từ trên xuống)
            col: Số cột (0-7 từ trái qua)
        """
        self._position = Position(row, col)
        self._piece: Optional[Piece] = None
        self._highlighted: bool = False  # Đánh dấu ô được chọn
        self._legal_move: bool = False   # Đánh dấu nước đi hợp lệ

    # Properties cơ bản
    @property
    def position(self) -> Position:
        """Vị trí của ô"""
        return self._position

    @property
    def row(self) -> int:
        """Số hàng của ô"""
        return self._position.row

    @property
    def col(self) -> int:
        """Số cột của ô"""
        return self._position.col

    @property
    def algebraic(self) -> str:
        """Ký hiệu đại số của ô (vd: 'e4')"""
        return self._position.algebraic

    @property
    def color(self) -> str:
        """Màu của ô (tính toán động)"""
        return 'dark' if (self.row + self.col) % 2 == 0 else 'light'

    @property
    def piece(self) -> Optional[Piece]:
        """Quân cờ trên ô"""
        return self._piece

    # Thuộc tính UI
    @property
    def is_highlighted(self) -> bool:
        """Kiểm tra ô có được highlight không"""
        return self._highlighted

    @property
    def is_legal_move(self) -> bool:
        """Kiểm tra ô có phải nước đi hợp lệ không"""
        return self._legal_move

    def highlight(self, state: bool = True) -> None:
        """Đánh dấu ô được chọn"""
        self._highlighted = state

    def mark_legal_move(self, state: bool = True) -> None:
        """Đánh dấu ô là nước đi hợp lệ"""
        self._legal_move = state

    # Các phương thức về quân cờ
    def is_occupied(self) -> bool:
        """Kiểm tra ô có quân không"""
        return self._piece is not None

    def has_enemy_piece(self, color: str) -> bool:
        """Kiểm tra có quân địch không"""
        return self.is_occupied() and self._piece.color != color

    def has_friendly_piece(self, color: str) -> bool:
        """Kiểm tra có quân đồng minh không"""
        return self.is_occupied() and self._piece.color == color

    def place_piece(self, piece: Optional[Piece]) -> None:
        """
        Đặt quân cờ lên ô.
        Args:
            piece: Quân cờ cần đặt hoặc None để xóa
        """
        self._piece = piece

    def clear(self) -> Optional[Piece]:
        """
        Lấy quân cờ ra khỏi ô.
        Returns:
            Quân cờ đã lấy ra hoặc None
        """
        piece = self._piece
        self._piece = None
        return piece

    # Phương thức so sánh
    def __eq__(self, other: object) -> bool:
        """So sánh hai ô dựa trên vị trí"""
        if not isinstance(other, Square):
            return NotImplemented
        return self._position == other._position

    def __hash__(self) -> int:
        """Hash của ô dựa trên vị trí"""
        return hash(self._position)

    def __str__(self) -> str:
        """Chuỗi đại diện ngắn gọn"""
        piece_str = str(self._piece) if self._piece else 'empty'
        return f"{self.algebraic}: {piece_str}"

    def __repr__(self) -> str:
        """Chuỗi đại diện đầy đủ"""
        return (f"Square(pos={self.algebraic}, "
                f"color={self.color}, "
                f"piece={self._piece})")