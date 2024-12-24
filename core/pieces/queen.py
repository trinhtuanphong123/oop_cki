# pieces/queen.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from ..move import Move

class Queen(Piece):
    """
    Class đại diện cho quân Hậu trong cờ vua.
    Đặc điểm:
    - Kết hợp khả năng di chuyển của Xe và Tượng
    - Di chuyển theo đường thẳng và đường chéo
    - Không giới hạn số ô di chuyển
    - Không thể đi qua quân khác
    - Quân mạnh nhất sau Vua
    """

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Hậu
        Args:
            color: Màu của quân Hậu
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.QUEEN)

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi có thể của quân Hậu
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []

        # Các hướng di chuyển của hậu (kết hợp của xe và tượng)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Các hướng trên
            (0, -1),           (0, 1),    # Các hướng ngang
            (1, -1),  (1, 0),  (1, 1)     # Các hướng dưới
        ]

        # Lấy nước đi theo từng hướng
        for row_step, col_step in directions:
            moves.extend(self.get_moves_in_direction(board, row_step, col_step))

        return moves

    def can_move_to(self, target: 'Square', board: 'Board') -> bool:
        """
        Kiểm tra có thể di chuyển đến ô đích không
        Args:
            target: Ô đích
            board: Bàn cờ hiện tại
        Returns:
            True nếu có thể di chuyển đến ô đích
        """
        if target.has_friendly_piece(self.color):
            return False

        # Kiểm tra di chuyển theo đường thẳng hoặc đường chéo
        row_diff = target.row - self.position.row
        col_diff = target.col - self.position.col

        # Phải di chuyển theo đường thẳng hoặc đường chéo
        if not (abs(row_diff) == abs(col_diff) or  # Đường chéo
                row_diff == 0 or                    # Hàng ngang
                col_diff == 0):                     # Hàng dọc
            return False

        # Xác định bước di chuyển
        row_step = 0 if row_diff == 0 else (row_diff // abs(row_diff))
        col_step = 0 if col_diff == 0 else (col_diff // abs(col_diff))

        # Kiểm tra đường đi có bị chặn không
        current_row = self.position.row + row_step
        current_col = self.position.col + col_step

        while current_row != target.row or current_col != target.col:
            if board.get_piece_at(current_row, current_col):
                return False
            current_row += row_step
            current_col += col_step

        return True

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân hậu dựa trên vị trí
        Returns:
            Giá trị của quân hậu
        """
        base_value = 900  # Giá trị cơ bản của hậu

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho việc kiểm soát trung tâm
        center_squares = [
            (3, 3), (3, 4), (4, 3), (4, 4)
        ]
        if (self.position.row, self.position.col) in center_squares:
            position_bonus += 30

        # Thưởng cho việc kiểm soát nhiều ô
        controlled_squares = self._count_controlled_squares(self.position.board)
        position_bonus += controlled_squares * 2

        # Phạt nếu ra quân hậu quá sớm
        if self.position.board.move_count < 10 and not self._is_starting_position():
            position_bonus -= 50

        return base_value + position_bonus

    def _count_controlled_squares(self, board: 'Board') -> int:
        """
        Đếm số ô quân hậu kiểm soát
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Số ô kiểm soát
        """
        controlled = 0
        moves = self.get_possible_moves(board)
        return len(moves)

    def _is_starting_position(self) -> bool:
        """
        Kiểm tra hậu có đang ở vị trí ban đầu không
        Returns:
            True nếu hậu ở vị trí ban đầu
        """
        row = 7 if self.color == PieceColor.WHITE else 0
        return self.position.row == row and self.position.col == 3

    def get_attack_directions(self) -> List[tuple]:
        """
        Lấy các hướng tấn công của hậu
        Returns:
            Danh sách các hướng tấn công
        """
        return [
            (-1, -1), (-1, 0), (-1, 1),  # Các hướng trên
            (0, -1),           (0, 1),    # Các hướng ngang
            (1, -1),  (1, 0),  (1, 1)     # Các hướng dưới
        ]

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{'W' if self.color == PieceColor.WHITE else 'B'}Q"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"Queen(color={self.color.value}, "
                f"position={self.position}, "
                f"has_moved={self.has_moved})")