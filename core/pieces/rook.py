from typing import List, Optional, Tuple, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType, Move

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

class Rook(Piece):
    """
    Class đại diện cho quân Xe trong cờ vua.
    Quân Xe di chuyển theo chiều ngang và dọc.
    """
    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Xe.

        Args:
            color: Màu của quân Xe
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.ROOK)
        self._can_castle = True  # Khả năng nhập thành

    @property
    def can_castle(self) -> bool:
        """Kiểm tra còn quyền nhập thành không"""
        return self._can_castle and not self.has_moved

    def get_legal_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân Xe.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        moves = []
        current_row = self.position.row
        current_col = self.position.col

        # Các