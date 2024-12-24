# pieces/rook.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from ..move import Move

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
        super().__init__(color, position, PieceType.ROOK)

    def get_possible_moves(self, board: 'Board') -> List['Move']:
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
            True nếu xe chưa di chuyển
        """
        return not self.has_moved

    def _is_starting_position(self) -> bool:
        """
        Kiểm tra xe có đang ở vị trí ban đầu không
        Returns:
            True nếu xe ở vị trí ban đầu
        """
        row = 7 if self.color == PieceColor.WHITE else 0
        return (self.position.row == row and 
                (self.position.col == 0 or self.position.col == 7))

    def get_castle_square(self, is_kingside: bool) -> 'Square':
        """
        Lấy ô đích khi nhập thành
        Args:
            is_kingside: True nếu là nhập thành cánh vua
        Returns:
            Ô đích của xe sau khi nhập thành
        """
        row = self.position.row
        col = 5 if is_kingside else 3
        return self.position.board.get_square(row, col)

    def can_move_to(self, target: 'Square', board: 'Board') -> bool:
        """
        Kiểm tra có thể di chuyển đến ô đích không
        Args:
            target: Ô đích
            board: Bàn cờ hiện tại
        Returns:
            True nếu có thể di chuyển đến ô đích
        """
        # Kiểm tra di chuyển theo hàng hoặc cột
        if not (self.position.row == target.row or self.position.col == target.col):
            return False

        # Không thể đi vào ô có quân cùng màu
        if target.has_friendly_piece(self.color):
            return False

        # Kiểm tra có bị chặn không
        row_step = 0 if self.position.row == target.row else (
            1 if target.row > self.position.row else -1)
        col_step = 0 if self.position.col == target.col else (
            1 if target.col > self.position.col else -1)

        current_row = self.position.row + row_step
        current_col = self.position.col + col_step

        while (current_row != target.row or current_col != target.col):
            if board.get_piece_at(current_row, current_col):
                return False
            current_row += row_step
            current_col += col_step

        return True

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân xe dựa trên vị trí
        Returns:
            Giá trị của quân xe
        """
        base_value = 500  # Giá trị cơ bản của xe

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho việc kiểm soát cột mở
        if self._controls_open_file(self.position.board):
            position_bonus += 30

        # Thưởng cho việc ở hàng 7 hoặc 8 (tấn công)
        if self.color == PieceColor.WHITE and self.position.row <= 1:
            position_bonus += 20
        elif self.color == PieceColor.BLACK and self.position.row >= 6:
            position_bonus += 20

        return base_value + position_bonus

    def _controls_open_file(self, board: 'Board') -> bool:
        """
        Kiểm tra xe có kiểm soát cột trống không
        Args:
            board: Bàn cờ hiện tại
        Returns:
            True nếu xe kiểm soát cột trống
        """
        col = self.position.col
        
        # Kiểm tra từ vị trí xe đến cuối bàn cờ
        for row in range(8):
            if row == self.position.row:
                continue
            piece = board.get_piece_at(row, col)
            if isinstance(piece, Piece) and isinstance(piece, Rook):
                return False
        return True

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{'W' if self.color == PieceColor.WHITE else 'B'}R"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"Rook(color={self.color.value}, "
                f"position={self.position}, "
                f"has_moved={self.has_moved})")