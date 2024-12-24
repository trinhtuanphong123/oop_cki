# pieces/bishop.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from ..move import Move

class Bishop(Piece):
    """
    Class đại diện cho quân Tượng trong cờ vua.
    Đặc điểm:
    - Di chuyển theo đường chéo
    - Không giới hạn số ô di chuyển
    - Không thể đi qua quân khác
    - Luôn ở trên ô cùng màu với ô xuất phát
    """

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Tượng
        Args:
            color: Màu của quân Tượng
            position: Vị trí ban đầu
        """
        super().__init__(color, position)
        self._piece_type = PieceType.BISHOP
   

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi có thể của quân Tượng
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []

        # Các hướng di chuyển chéo của tượng
        directions = [
            (-1, -1),  # Chéo trên trái
            (-1, 1),   # Chéo trên phải
            (1, -1),   # Chéo dưới trái
            (1, 1)     # Chéo dưới phải
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

        # Kiểm tra di chuyển theo đường chéo
        row_diff = abs(target.row - self.position.row)
        col_diff = abs(target.col - self.position.col)

        # Phải di chuyển theo đường chéo (row_diff == col_diff)
        if row_diff != col_diff:
            return False

        # Xác định hướng di chuyển
        row_step = 1 if target.row > self.position.row else -1
        col_step = 1 if target.col > self.position.col else -1

        # Kiểm tra đường đi có bị chặn không
        current_row = self.position.row + row_step
        current_col = self.position.col + col_step

        while current_row != target.row:
            if board.get_piece_at(current_row, current_col):
                return False
            current_row += row_step
            current_col += col_step

        return True

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân tượng dựa trên vị trí
        Returns:
            Giá trị của quân tượng
        """
        base_value = 330  # Giá trị cơ bản của tượng

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho việc kiểm soát đường chéo dài
        long_diagonal_bonus = self._calculate_long_diagonal_control(self.position.board)
        position_bonus += long_diagonal_bonus

        # Thưởng cho cặp tượng
        if self._has_bishop_pair(self.position.board):
            position_bonus += 50

        # Thưởng cho việc kiểm soát trung tâm mở rộng
        extended_center = [
            (2, 2), (2, 3), (2, 4), (2, 5),
            (3, 2), (3, 3), (3, 4), (3, 5),
            (4, 2), (4, 3), (4, 4), (4, 5),
            (5, 2), (5, 3), (5, 4), (5, 5)
        ]
        if (self.position.row, self.position.col) in extended_center:
            position_bonus += 20

        # Phạt cho việc bị chặn bởi quân tốt trung tâm
        if self._is_blocked_by_center_pawns(self.position.board):
            position_bonus -= 30

        return base_value + position_bonus

    def _calculate_long_diagonal_control(self, board: 'Board') -> int:
        """
        Tính điểm thưởng cho việc kiểm soát đường chéo dài
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Điểm thưởng
        """
        bonus = 0
        moves = self.get_possible_moves(board)
        
        # Đếm số ô kiểm soát trên đường chéo dài
        main_diagonals = [(0,0), (0,7), (7,0), (7,7)]
        for move in moves:
            if (move.end_square.row, move.end_square.col) in main_diagonals:
                bonus += 10
        return bonus

    def _has_bishop_pair(self, board: 'Board') -> bool:
        """
        Kiểm tra có cặp tượng không
        Args:
            board: Bàn cờ hiện tại
        Returns:
            True nếu có cặp tượng
        """
        bishop_count = 0
        for piece in board.get_pieces(self.color):
            if isinstance(piece, Bishop):
                bishop_count += 1
        return bishop_count >= 2

    def _is_blocked_by_center_pawns(self, board: 'Board') -> bool:
        """
        Kiểm tra có bị chặn bởi tốt trung tâm không
        Args:
            board: Bàn cờ hiện tại
        Returns:
            True nếu bị chặn
        """
        from .pawn import Pawn
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        
        for row, col in center_squares:
            piece = board.get_piece_at(row, col)
            if isinstance(piece, Pawn) and piece.color != self.color:
                # Kiểm tra tốt có chặn đường đi của tượng không
                if self._is_blocking_diagonal(piece.position):
                    return True
        return False

    def _is_blocking_diagonal(self, blocking_square: 'Square') -> bool:
        """
        Kiểm tra một ô có chặn đường chéo của tượng không
        Args:
            blocking_square: Ô cần kiểm tra
        Returns:
            True nếu ô đó chặn đường chéo
        """
        row_diff = abs(blocking_square.row - self.position.row)
        col_diff = abs(blocking_square.col - self.position.col)
        return row_diff == col_diff

    def get_attack_directions(self) -> List[tuple]:
        """
        Lấy các hướng tấn công của tượng
        Returns:
            Danh sách các hướng tấn công
        """
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{'W' if self.color == PieceColor.WHITE else 'B'}B"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"Bishop(color={self.color.value}, "
                f"position={self.position}, "
                f"has_moved={self.has_moved})")