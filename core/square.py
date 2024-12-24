# square.py

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pieces.piece import Piece, PieceColor

class Square:
    """
    Class đại diện cho một ô trên bàn cờ.
    Quản lý vị trí và trạng thái của ô.
    """
    def __init__(self, row: int, col: int):
        """
        Khởi tạo một ô với tọa độ xác định
        Args:
            row: Hàng (0-7)
            col: Cột (0-7)
        """
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError(f"Invalid position: ({row}, {col})")
            
        self._row = row
        self._col = col
        self._piece: Optional['Piece'] = None

    # Properties cơ bản
    @property
    def row(self) -> int:
        """Lấy chỉ số hàng"""
        return self._row

    @property
    def col(self) -> int:
        """Lấy chỉ số cột"""
        return self._col

    @property
    def piece(self) -> Optional['Piece']:
        """Lấy quân cờ đang ở trên ô"""
        return self._piece

    @property
    def algebraic(self) -> str:
        """Chuyển đổi sang ký hiệu đại số (vd: 'e4')"""
        col_letter = chr(ord('a') + self._col)
        row_number = 8 - self._row
        return f"{col_letter}{row_number}"

    # Phương thức quản lý quân cờ
    def place_piece(self, piece: Optional['Piece']) -> None:
        """
        Đặt quân cờ lên ô
        Args:
            piece: Quân cờ cần đặt hoặc None để xóa quân cờ
        """
        self._piece = piece

    def remove_piece(self) -> Optional['Piece']:
        """
        Lấy quân cờ ra khỏi ô
        Returns:
            Piece hoặc None nếu ô trống
        """
        piece = self._piece
        self._piece = None
        return piece

    # Phương thức kiểm tra trạng thái
    def is_empty(self) -> bool:
        """Kiểm tra ô có trống không"""
        return self._piece is None

    def is_occupied(self) -> bool:
        """Kiểm tra ô có quân không"""
        return not self.is_empty()

    def has_enemy_piece(self, color: 'PieceColor') -> bool:
        """
        Kiểm tra ô có quân địch không
        Args:
            color: Màu quân cờ cần so sánh
        """
        return self.is_occupied() and self._piece.color != color

    def has_friendly_piece(self, color: 'PieceColor') -> bool:
        """
        Kiểm tra ô có quân cùng màu không
        Args:
            color: Màu quân cờ cần so sánh
        """
        return self.is_occupied() and self._piece.color == color

    # Magic methods
    def __eq__(self, other: object) -> bool:
        """So sánh hai ô có cùng vị trí không"""
        if not isinstance(other, Square):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        """Hash dựa trên vị trí của ô"""
        return hash((self._row, self._col))

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.algebraic

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return f"Square({self.algebraic}, piece={self._piece})"