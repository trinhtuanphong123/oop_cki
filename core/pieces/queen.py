# pieces/queen.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType
from ..move import Move, MoveType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

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
        super().__init__(color, position)
        self._piece_type = PieceType.QUEEN

    def get_possible_moves(self, board: 'Board') -> List[Move]:
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

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân hậu dựa trên vị trí
        Returns:
            Giá trị của quân hậu
        """
        base_value = 900  # Giá trị cơ bản của hậu
        
        if not self.position or not self.position.board:
            return base_value

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho việc kiểm soát trung tâm
        center_squares = [
            (3, 3), (3, 4), (4, 3), (4, 4)
        ]
        if (self.position.row, self.position.col) in center_squares:
            position_bonus += 30

        # Thưởng cho việc kiểm soát nhiều ô
        controlled_squares = len(self.get_possible_moves(self.position.board))
        position_bonus += controlled_squares * 2

        # Phạt nếu ra quân hậu quá sớm
        if self.position.board.move_count < 10 and not self._is_starting_position():
            position_bonus -= 50

        return base_value + position_bonus

    def _is_starting_position(self) -> bool:
        """
        Kiểm tra hậu có đang ở vị trí ban đầu không
        Returns:
            True nếu hậu ở vị trí ban đầu
        """
        if not self.position:
            return False
            
        row = 7 if self.color == PieceColor.WHITE else 0
        return self.position.row == row and self.position.col == 3

    def get_attack_directions(self) -> List[tuple[int, int]]:
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
        return self.symbol