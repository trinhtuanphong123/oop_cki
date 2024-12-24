# pieces/rook.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType
from ..move import Move, MoveType
from typing import Optional

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

class Rook(Piece):
    """
    Class đại diện cho quân xe trong cờ vua.
    Đặc điểm di chuyển:
    - Di chuyển theo hàng ngang và dọc
    - Không giới hạn số ô di chuyển
    - Không thể đi qua quân khác
    - Có thể tham gia nhập thành với vua
    """

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân xe
        Args:
            color: Màu của quân xe
            position: Vị trí ban đầu
        """
        super().__init__(color, position)
        self._piece_type = PieceType.ROOK
    
    def get_possible_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi có thể của quân xe
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []

        # Các hướng di chuyển của xe (hàng ngang và dọc)
        directions = [
            (-1, 0),  # Lên
            (1, 0),   # Xuống
            (0, -1),  # Trái
            (0, 1)    # Phải
        ]

        # Lấy nước đi theo từng hướng
        for row_step, col_step in directions:
            moves.extend(self.get_moves_in_direction(board, row_step, col_step))

        return moves

    def can_castle(self) -> bool:
        """
        Kiểm tra xe có thể tham gia nhập thành không
        Returns:
            True nếu xe chưa di chuyển và ở vị trí ban đầu
        """
        return not self.has_moved and self._is_starting_position()

    def _is_starting_position(self) -> bool:
        """
        Kiểm tra xe có đang ở vị trí ban đầu không
        Returns:
            True nếu xe ở vị trí ban đầu
        """
        if not self.position:
            return False
            
        row = 7 if self.color == PieceColor.WHITE else 0
        return (self.position.row == row and 
                (self.position.col == 0 or self.position.col == 7))

    def get_castle_square(self, is_kingside: bool) -> Optional['Square']:
        """
        Lấy ô đích khi nhập thành
        Args:
            is_kingside: True nếu là nhập thành cánh vua
        Returns:
            Ô đích của xe sau khi nhập thành
        """
        if not self.position or not self.position.board:
            return None
            
        row = self.position.row
        col = 5 if is_kingside else 3
        return self.position.board.get_square(row, col)

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân xe dựa trên vị trí
        Returns:
            Giá trị của quân xe
        """
        base_value = 500  # Giá trị cơ bản của xe
        if not self.position:
            return base_value

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho việc kiểm soát cột mở
        if self._controls_open_file():
            position_bonus += 30

        # Thưởng cho việc ở hàng 7 hoặc 8 (tấn công)
        if self.color == PieceColor.WHITE and self.position.row <= 1:
            position_bonus += 20
        elif self.color == PieceColor.BLACK and self.position.row >= 6:
            position_bonus += 20

        return base_value + position_bonus

    def _controls_open_file(self) -> bool:
        """
        Kiểm tra xe có kiểm soát cột trống không
        Returns:
            True nếu xe kiểm soát cột trống
        """
        if not self.position or not self.position.board:
            return False
            
        col = self.position.col
        board = self.position.board
        
        # Kiểm tra từ vị trí xe đến cuối bàn cờ
        for row in range(8):
            if row == self.position.row:
                continue
            piece = board.get_piece_at(row, col)
            if piece and isinstance(piece, Rook):
                return False
        return True

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.symbol