# pawn.py

from typing import List, Optional
from .piece import Piece, PieceType, PieceColor
from ..square import Square
from ..move import Move
from ..board import Board

class Pawn(Piece):
    """
    Class quân tốt kế thừa từ Piece.
    Có các đặc điểm riêng:
    - Đi thẳng về phía trước
    - Được đi 2 ô ở nước đầu
    - Bắt chéo
    - Phong cấp khi đến cuối bàn cờ
    """
    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân tốt
        Args:
            color: Màu quân tốt
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.PAWN)
        # Hàng cuối để phong cấp
        self._promotion_row = 0 if color == PieceColor.WHITE else 7 

    @property
    def direction(self) -> int:
        """Hướng di chuyển: -1 cho trắng (đi lên), 1 cho đen (đi xuống)"""
        return -1 if self.color == PieceColor.WHITE else 1

    @property 
    def start_row(self) -> int:
        """Hàng xuất phát: 6 cho trắng, 1 cho đen"""
        return 6 if self.color == PieceColor.WHITE else 1

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả nước đi có thể của tốt
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        row, col = self.position.row, self.position.col

        # Đi thẳng 1 ô
        next_row = row + self.direction
        if 0 <= next_row < 8:
            front = board.get_square(next_row, col)
            if not front.is_occupied():
                moves.append(self._create_move(front))

                # Đi thẳng 2 ô nếu là nước đầu
                if not self.has_moved and row == self.start_row:
                    two_ahead = board.get_square(next_row + self.direction, col)
                    if not two_ahead.is_occupied():
                        moves.append(self._create_move(two_ahead))

        # Bắt chéo
        for col_offset in [-1, 1]:
            capture_col = col + col_offset
            if 0 <= next_row < 8 and 0 <= capture_col < 8:
                target = board.get_square(next_row, capture_col)
                if target.is_occupied() and self.is_enemy(target.piece):
                    moves.append(self._create_move(target, is_capture=True))

        return moves

    def _create_move(self, end_square: 'Square', is_capture: bool = False) -> 'Move':
        """
        Tạo nước đi cho tốt
        Args:
            end_square: Ô đích
            is_capture: Có phải nước bắt quân không
        Returns:
            Nước đi được tạo
        """
        is_promotion = end_square.row == self._promotion_row
        return Move(
            start_square=self.position,
            end_square=end_square,
            moving_piece=self,
            is_capture=is_capture,
            is_promotion=is_promotion
        )

    def can_promote(self) -> bool:
        """Kiểm tra có thể phong cấp không"""
        return self.position.row == self._promotion_row

    def __str__(self) -> str:
        """String representation"""
        return f"{self.color.value} Pawn"