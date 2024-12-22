from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

class PieceColor(Enum):
    """Enum định nghĩa màu quân cờ"""
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> 'PieceColor':
        """Trả về màu đối diện"""
        return PieceColor.BLACK if self == PieceColor.WHITE else PieceColor.WHITE

class PieceType(Enum):
    """Enum định nghĩa loại quân cờ và giá trị của chúng"""
    PAWN = ("pawn", 1.0)
    KNIGHT = ("knight", 3.0)
    BISHOP = ("bishop", 3.0)
    ROOK = ("rook", 5.0)
    QUEEN = ("queen", 9.0)
    KING = ("king", float('inf'))  # Vua có giá trị vô cực

    def __init__(self, name: str, value: float):
        self._name = name
        self._value = value

    @property
    def value(self) -> float:
        """Giá trị điểm cơ bản của quân cờ"""
        return self._value

    @property
    def name(self) -> str:
        """Tên của quân cờ"""
        return self._name

@dataclass(frozen=True)
class Move:
    """
    Class bất biến lưu trữ thông tin về một nước đi
    Sử dụng frozen=True để đảm bảo immutability
    """
    start: Tuple[int, int]
    end: Tuple[int, int]
    is_capture: bool = False
    is_castle: bool = False
    is_promotion: bool = False
    promotion_piece: Optional[PieceType] = None
    is_en_passant: bool = False

    def __post_init__(self):
        """Validate nước đi sau khi khởi tạo"""
        for pos in (self.start, self.end):
            row, col = pos
            if not (0 <= row < 8 and 0 <= col < 8):
                raise ValueError(f"Invalid position: {pos}")

class Piece(ABC):
    """
    Lớp trừu tượng cơ sở cho tất cả các quân cờ.
    Sử dụng __slots__ để tối ưu bộ nhớ và kiểm soát thuộc tính.
    """
    __slots__ = ('_color', '_position', '_piece_type', '_texture', '_has_moved', 
                 '_captured', '_move_count')

    def __init__(self, color: PieceColor, position: 'Square', piece_type: PieceType):
        """
        Khởi tạo quân cờ với các thuộc tính cơ bản.
        
        Args:
            color: Màu của quân cờ
            position: Vị trí ban đầu
            piece_type: Loại quân cờ
        """
        if not isinstance(color, PieceColor):
            raise ValueError(f"Invalid color: {color}")
        if not isinstance(piece_type, PieceType):
            raise ValueError(f"Invalid piece type: {piece_type}")

        self._color = color
        self._position = position
        self._piece_type = piece_type
        self._has_moved = False
        self._captured = False
        self._move_count = 0
        self._texture = self._load_texture()

    # Basic properties
    @property
    def color(self) -> PieceColor:
        """Màu của quân cờ"""
        return self._color

    @property
    def position(self) -> 'Square':
        """Vị trí hiện tại"""
        return self._position

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return self._piece_type

    @property
    def has_moved(self) -> bool:
        """Đã di chuyển chưa"""
        return self._has_moved

    @property
    def is_captured(self) -> bool:
        """Đã bị bắt chưa"""
        return self._captured

    @property
    def move_count(self) -> int:
        """Số lần đã di chuyển"""
        return self._move_count

    # Movement related methods
    @abstractmethod
    def get_legal_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy danh sách các nước đi hợp lệ.
        Lớp con phải implement phương thức này.
        """
        pass

    def get_pseudo_legal_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy danh sách nước đi có thể trước khi kiểm tra chiếu.
        Lớp con có thể override để tối ưu.
        """
        return self.get_legal_moves(board)

    def move_to(self, new_square: 'Square', board: 'Board') -> None:
        """
        Di chuyển quân cờ đến ô mới và cập nhật trạng thái.
        
        Args:
            new_square: Ô đích
            board: Bàn cờ hiện tại
        """
        if new_square.has_friendly_piece(self._color):
            raise ValueError("Cannot move to square with friendly piece")

        old_square = self._position
        self._position = new_square
        self._has_moved = True
        self._move_count += 1

        # Cập nhật bàn cờ
        board.update_piece_position(self, old_square, new_square)

    # Combat related methods
    def can_capture(self, target_square: 'Square') -> bool:
        """Kiểm tra có thể bắt quân không"""
        return (target_square.is_occupied() and 
                target_square.piece.color != self._color)

    def get_attack_squares(self, board: 'Board') -> List['Square']:
        """Lấy danh sách các ô có thể tấn công"""
        return [board.get_square(*move.end) 
                for move in self.get_pseudo_legal_moves(board)
                if move.is_capture]

    # Value and position evaluation
    def get_material_value(self) -> float:
        """Tính giá trị vật chất cơ bản"""
        return self._piece_type.value

    def get_position_value(self, board: 'Board') -> float:
        """
        Tính điểm cộng thêm dựa trên vị trí.
        Lớp con nên override để tính toán chính xác hơn.
        """
        return 0.0

    def get_total_value(self, board: 'Board') -> float:
        """Tính tổng giá trị của quân cờ"""
        return self.get_material_value() + self.get_position_value(board)

    # Texture handling
    def _load_texture(self, size: int = 80) -> Path:
        """Load texture cho quân cờ"""
        texture_path = (Path('assets/images') / 
                       f"imgs-{size}" / 
                       f"{self._color.value}-{self._piece_type.name.lower()}.png")
        
        if not texture_path.exists():
            raise FileNotFoundError(f"Texture not found: {texture_path}")
        return texture_path

    # Utility methods
    def clone(self) -> 'Piece':
        """Tạo bản sao của quân cờ"""
        clone = self.__class__(self._color, self._position, self._piece_type)
        clone._has_moved = self._has_moved
        clone._move_count = self._move_count
        return clone

    def is_protecting_square(self, square: 'Square', board: 'Board') -> bool:
        """Kiểm tra có đang bảo vệ ô không"""
        return square in self.get_attack_squares(board)

    # Magic methods
    def __eq__(self, other: object) -> bool:
        """So sánh hai quân cờ"""
        if not isinstance(other, Piece):
            return NotImplemented
        return (self._color == other._color and 
                self._piece_type == other._piece_type and 
                self._position == other._position)

    def __hash__(self) -> int:
        """Hash của quân cờ"""
        return hash((self._color, self._piece_type, self._position))

    def __str__(self) -> str:
        """Chuỗi đại diện ngắn gọn"""
        return f"{self._color.value} {self._piece_type.name}"

    def __repr__(self) -> str:
        """Chuỗi đại diện chi tiết"""
        return (f"{self.__class__.__name__}("
                f"color={self._color.value}, "
                f"type={self._piece_type.name}, "
                f"pos={self._position})")