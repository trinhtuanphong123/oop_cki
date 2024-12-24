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
    PIECES_DIR = os.path.join("assets", "images", "imgs-80")

    def __init__(self, color: PieceColor, position: Square):
        """
        Khởi tạo quân cờ
        Args:
            color: Màu quân cờ
            position: Vị trí ban đầu
        """
        self._color = color
        self._position = position
        self._has_moved = False
        
        # Đặt piece_type trong class con
        self._piece_type: PieceType = None
        
        if position:
            position.place_piece(self)

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
    def symbol(self) -> str:
        """Symbol của quân cờ để hiển thị"""
        color_prefix = 'w' if self.color == PieceColor.WHITE else 'b'
        type_map = {
            PieceType.PAWN: 'P',
            PieceType.KNIGHT: 'N',
            PieceType.BISHOP: 'B',
            PieceType.ROOK: 'R',
            PieceType.QUEEN: 'Q',
            PieceType.KING: 'K'
        }
        return color_prefix + type_map[self.piece_type]

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
        """Kiểm tra có thể di chuyển đến ô đích không"""
        # Kiểm tra ô đích có quân cùng màu không
        if target.piece and target.piece.color == self.color:
            return False

        # Kiểm tra nước đi có hợp lệ không
        for move in self.get_possible_moves(board):
            if move.end_square == target:
                return True
        return False

    def can_attack_square(self, square: Square, board: Board) -> bool:
        """Kiểm tra có thể tấn công ô này không"""
        return self.can_move_to(square, board)

    def make_move(self, target: Square, board: Board) -> None:
        """Thực hiện di chuyển đến ô đích"""
        if self.position:
            self.position.remove_piece()
        
        captured_piece = target.piece
        if captured_piece:
            board.capture_piece(captured_piece)
            
        target.place_piece(self)
        self._position = target
        self._has_moved = True

    def get_moves_in_direction(self, board: Board, row_step: int, col_step: int) -> List[Move]:
        """Lấy các nước đi theo một hướng"""
        moves = []
        current_row = self.position.row + row_step
        current_col = self.position.col + col_step

        while board.is_valid_position(current_row, current_col):
            target = board.get_square(current_row, current_col)
            
            # Gặp quân cùng màu
            if target.piece and target.piece.color == self.color:
                break
                
            # Thêm nước đi
            from ..move import Move
            moves.append(Move(self.position, target, self))
            
            # Gặp quân địch
            if target.piece:
                break
                
            current_row += row_step
            current_col += col_step

        return moves

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.symbol

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return f"{self.__class__.__name__}(color={self.color.value}, position={self.position})"