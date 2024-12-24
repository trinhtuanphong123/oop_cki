# piece.py
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from ..square import Square
    from ..board import Board
    from ..move import Move

class PieceColor(Enum):
    """Enum định nghĩa màu quân cờ"""
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> PieceColor:
        """Lấy màu đối lập"""
        return PieceColor.BLACK if self == PieceColor.WHITE else PieceColor.WHITE

class PieceType(Enum):
    """Enum định nghĩa loại quân cờ"""
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"

class Piece(ABC):
    """
    Class trừu tượng cho tất cả các quân cờ.
    Định nghĩa interface chung và triển khai các phương thức cơ bản.
    """
    # Đường dẫn tới thư mục chứa ảnh quân cờ
    PIECES_DIR = os.path.join("assets", "pieces")

    def __init__(self, color: PieceColor, position: Square, piece_type: PieceType):
        """
        Khởi tạo quân cờ
        Args:
            color: Màu quân cờ
            position: Vị trí ban đầu
            piece_type: Loại quân cờ
        """
        self._color = color
        self._position = position
        self._piece_type = piece_type
        self._has_moved = False
        self._image_path = self._get_image_path()

    @property
    def color(self) -> PieceColor:
        """Màu của quân cờ"""
        return self._color

    @property
    def position(self) -> Square:
        """Vị trí hiện tại"""
        return self._position

    @position.setter
    def position(self, new_position: Square) -> None:
        """Cập nhật vị trí"""
        self._position = new_position

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return self._piece_type

    @property
    def has_moved(self) -> bool:
        """Đã di chuyển chưa"""
        return self._has_moved

    @property
    def image_path(self) -> str:
        """Đường dẫn đến file ảnh"""
        return self._image_path

    def _get_image_path(self) -> str:
        """
        Lấy đường dẫn đến file ảnh quân cờ
        Format: {color}_{piece_type}.png
        """
        filename = f"{self._color.value}_{self._piece_type.value}.png"
        return os.path.join(self.PIECES_DIR, filename)

    @abstractmethod
    def get_possible_moves(self, board: Board) -> List[Move]:
        """
        Lấy tất cả các nước đi có thể của quân cờ
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        pass

    def can_move_to(self, target: Square, board: Board) -> bool:
        """
        Kiểm tra có thể di chuyển đến ô đích không
        Args:
            target: Ô đích
            board: Bàn cờ hiện tại
        """
        # Không thể đi vào ô có quân cùng màu
        if target.has_friendly_piece(self._color):
            return False

        # Kiểm tra nước đi có nằm trong danh sách nước đi có thể
        possible_moves = self.get_possible_moves(board)
        return any(move.end_square == target for move in possible_moves)

    def make_move(self, target: Square, board: Board) -> None:
        """
        Thực hiện di chuyển đến ô đích
        Args:
            target: Ô đích
            board: Bàn cờ hiện tại
        """
        # Cập nhật vị trí cũ
        self._position.remove_piece()
        
        # Cập nhật vị trí mới
        old_piece = target.piece
        if old_piece:
            board.remove_piece(old_piece)
        target.place_piece(self)
        self._position = target
        
        # Đánh dấu đã di chuyển
        self._has_moved = True

    def can_attack_square(self, square: Square, board: Board) -> bool:
        """
        Kiểm tra có thể tấn công ô này không
        Args:
            square: Ô cần kiểm tra
            board: Bàn cờ hiện tại
        """
        return self.can_move_to(square, board)

    def is_enemy(self, other: Optional[Piece]) -> bool:
        """
        Kiểm tra có phải quân địch không
        Args:
            other: Quân cờ cần kiểm tra
        """
        return other is not None and other.color != self._color

    def get_moves_in_direction(self, board: Board, row_step: int, col_step: int) -> List[Move]:
        """
        Lấy các nước đi theo một hướng cụ thể
        Args:
            board: Bàn cờ hiện tại
            row_step: Bước di chuyển theo hàng
            col_step: Bước di chuyển theo cột
        Returns:
            Danh sách các nước đi có thể theo hướng đó
        """
        moves = []
        current_row = self._position.row + row_step
        current_col = self._position.col + col_step

        while 0 <= current_row < 8 and 0 <= current_col < 8:
            target = board.get_square(current_row, current_col)
            
            # Nếu gặp quân cùng màu thì dừng
            if target.has_friendly_piece(self._color):
                break
                
            # Thêm nước đi vào danh sách
            from ..move import Move  # Import cục bộ để tránh circular import
            moves.append(Move(self._position, target, self))
            
            # Nếu gặp quân địch thì dừng sau khi thêm nước đi
            if target.has_enemy_piece(self._color):
                break
                
            current_row += row_step
            current_col += col_step

        return moves

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{self._color.value} {self._piece_type.value}"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"{self.__class__.__name__}("
                f"color={self._color.value}, "
                f"position={self._position}, "
                f"has_moved={self._has_moved})")