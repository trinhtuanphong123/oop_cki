# piece.py

from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum
from ..square import Square
from ..board import Board
from ..move import Move

class PieceColor(Enum):
    """Màu quân cờ"""
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> 'PieceColor':
        """Lấy màu đối lập"""
        return PieceColor.BLACK if self == PieceColor.WHITE else PieceColor.WHITE

class PieceType(Enum):
    """Loại quân cờ"""
    PAWN = "pawn"
    KNIGHT = "knight" 
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"

class Piece(ABC):
    """
    Class trừu tượng cho tất cả các quân cờ.
    Định nghĩa interface chung và logic cơ bản.
    """
    def __init__(self, color: PieceColor, position: 'Square', piece_type: PieceType):
        """
        Khởi tạo quân cờ.
        
        Args:
            color: Màu của quân cờ (trắng/đen)
            position: Ô hiện tại của quân cờ
            piece_type: Loại quân cờ
        """
        self._color = color
        self._position = position
        self._piece_type = piece_type
        self._has_moved = False

    # Properties cơ bản
    @property
    def color(self) -> PieceColor:
        """Màu của quân cờ"""
        return self._color

    @property
    def position(self) -> 'Square':
        """Vị trí hiện tại"""
        return self._position

    @position.setter
    def position(self, square: 'Square') -> None:
        """Cập nhật vị trí mới"""
        self._position = square

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return self._piece_type

    @property
    def has_moved(self) -> bool:
        """Đã di chuyển lần nào chưa"""
        return self._has_moved

    # Methods cho di chuyển
    @abstractmethod
    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả nước đi có thể của quân cờ.
        Mỗi quân cờ cụ thể sẽ implement theo cách di chuyển riêng.

        Args:
            board: Bàn cờ hiện tại

        Returns:
            Danh sách các nước đi có thể
        """
        pass

    def can_move_to(self, square: 'Square', board: 'Board') -> bool:
        """
        Kiểm tra quân cờ có thể di chuyển đến ô này không.

        Args:
            square: Ô đích
            board: Bàn cờ hiện tại

        Returns:
            True nếu có thể di chuyển đến ô đó
        """
        return square in [move.end_square for move in self.get_possible_moves(board)]

    def make_move(self, square: 'Square') -> None:
        """
        Thực hiện di chuyển đến ô mới.

        Args:
            square: Ô đích
        """
        self._position = square
        self._has_moved = True

    # Utility methods
    def is_enemy(self, other: Optional['Piece']) -> bool:
        """Kiểm tra có phải quân địch không"""
        return other is not None and other.color != self.color

    def is_friend(self, other: Optional['Piece']) -> bool:
        """Kiểm tra có phải quân cùng phe không"""
        return other is not None and other.color == self.color

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{self.color.value} {self.piece_type.value}"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"{self.__class__.__name__}("
                f"color={self.color.value}, "
                f"position={self.position}, "
                f"type={self.piece_type.value})")