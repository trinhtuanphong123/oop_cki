# pieces/knight.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from ..move import Move

class Knight(Piece):
    """
    Class đại diện cho quân Mã trong cờ vua.
    Đặc điểm:
    - Di chuyển theo hình chữ L
    - Có thể nhảy qua quân khác
    - Là quân duy nhất có thể nhảy qua quân khác
    - Đặc biệt mạnh ở vị trí trung tâm và trong tình huống bị chặn
    """

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Mã
        Args:
            color: Màu của quân Mã
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.KNIGHT)

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi có thể của quân Mã
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        
        # Tất cả các nước đi hình chữ L có thể
        knight_moves = [
            (-2, -1), (-2, 1),  # Lên 2 trái/phải 1
            (-1, -2), (-1, 2),  # Lên 1 trái/phải 2
            (1, -2), (1, 2),    # Xuống 1 trái/phải 2
            (2, -1), (2, 1)     # Xuống 2 trái/phải 1
        ]

        for row_step, col_step in knight_moves:
            new_row = self.position.row + row_step
            new_col = self.position.col + col_step

            if board.is_valid_position(new_row, new_col):
                target = board.get_square(new_row, new_col)
                if not target.has_friendly_piece(self.color):
                    moves.append(self._create_move(target))

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

        # Kiểm tra di chuyển hình chữ L
        row_diff = abs(target.row - self.position.row)
        col_diff = abs(target.col - self.position.col)

        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân mã dựa trên vị trí
        Returns:
            Giá trị của quân mã
        """
        base_value = 320  # Giá trị cơ bản của mã

        # Điểm thưởng cho các vị trí chiến lược
        position_bonus = 0

        # Thưởng cho vị trí trung tâm
        position_bonus += self._calculate_center_bonus()

        # Thưởng cho việc kiểm soát nhiều ô
        mobility_bonus = self._calculate_mobility_bonus(self.position.board)
        position_bonus += mobility_bonus

        # Thưởng cho outpost (vị trí tiền đồn được bảo vệ bởi tốt)
        if self._is_outpost(self.position.board):
            position_bonus += 30

        # Phạt cho việc ở gần góc bàn cờ
        if self._is_near_corner():
            position_bonus -= 20

        return base_value + position_bonus

    def _calculate_center_bonus(self) -> int:
        """
        Tính điểm thưởng cho vị trí trung tâm
        Returns:
            Điểm thưởng
        """
        row, col = self.position.row, self.position.col
        
        # Trung tâm (4 ô giữa)
        if (row in [3, 4] and col in [3, 4]):
            return 30
            
        # Trung tâm mở rộng
        if (row in [2, 3, 4, 5] and col in [2, 3, 4, 5]):
            return 15
            
        return 0

    def _calculate_mobility_bonus(self, board: 'Board') -> int:
        """
        Tính điểm thưởng cho khả năng di chuyển
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Điểm thưởng dựa trên số nước đi có thể
        """
        possible_moves = len(self.get_possible_moves(board))
        return possible_moves * 3  # 3 điểm cho mỗi nước đi có thể

    def _is_outpost(self, board: 'Board') -> bool:
        """
        Kiểm tra mã có đang ở vị trí tiền đồn không
        Args:
            board: Bàn cờ hiện tại
        Returns:
            True nếu mã đang ở vị trí tiền đồn
        """
        from .pawn import Pawn

        # Kiểm tra có được bảo vệ bởi tốt không
        row, col = self.position.row, self.position.col
        pawn_row = row + (1 if self.color == PieceColor.WHITE else -1)
        
        for pawn_col in [col-1, col+1]:
            if board.is_valid_position(pawn_row, pawn_col):
                piece = board.get_piece_at(pawn_row, pawn_col)
                if isinstance(piece, Pawn) and piece.color == self.color:
                    return True
        
        return False

    def _is_near_corner(self) -> bool:
        """
        Kiểm tra mã có gần góc bàn cờ không
        Returns:
            True nếu mã đang ở gần góc
        """
        row, col = self.position.row, self.position.col
        return (row in [0, 1, 6, 7] and col in [0, 1, 6, 7])

    def get_attack_squares(self, board: 'Board') -> List['Square']:
        """
        Lấy danh sách các ô mã có thể tấn công
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các ô có thể tấn công
        """
        attack_squares = []
        moves = self.get_possible_moves(board)
        
        for move in moves:
            attack_squares.append(move.end_square)
            
        return attack_squares

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{'W' if self.color == PieceColor.WHITE else 'B'}N"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"Knight(color={self.color.value}, "
                f"position={self.position}, "
                f"has_moved={self.has_moved})")