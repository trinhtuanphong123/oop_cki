# pieces/knight.py
from typing import List, Optional, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType
from ..move import Move, MoveType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

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
        super().__init__(color, position)
        self._piece_type = PieceType.KNIGHT

    def get_possible_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi có thể của quân Mã
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        
        if not self.position or not board:
            return moves

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
                    move_type = MoveType(is_capture=target.piece is not None)
                    moves.append(Move(self.position, target, self, move_type))

        return moves

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân mã dựa trên vị trí
        Returns:
            Giá trị của quân mã
        """
        base_value = 320  # Giá trị cơ bản của mã

        if not self.position or not self.position.board:
            return base_value

        position_bonus = 0

        # Thưởng cho vị trí trung tâm
        position_bonus += self._calculate_center_bonus()

        # Thưởng cho khả năng di chuyển
        possible_moves = len(self.get_possible_moves(self.position.board))
        position_bonus += possible_moves * 3

        # Thưởng cho outpost
        if self._is_outpost():
            position_bonus += 30

        # Phạt cho vị trí gần góc
        if self._is_near_corner():
            position_bonus -= 20

        return base_value + position_bonus

    def _calculate_center_bonus(self) -> int:
        """Tính điểm thưởng cho vị trí trung tâm"""
        if not self.position:
            return 0
            
        row, col = self.position.row, self.position.col
        
        # Trung tâm (4 ô giữa)
        if (row in [3, 4] and col in [3, 4]):
            return 30
            
        # Trung tâm mở rộng
        if (row in [2, 3, 4, 5] and col in [2, 3, 4, 5]):
            return 15
            
        return 0

    def _is_outpost(self) -> bool:
        """Kiểm tra mã có phải là outpost không"""
        if not self.position or not self.position.board:
            return False
            
        row, col = self.position.row, self.position.col
        pawn_row = row + (1 if self.color == PieceColor.WHITE else -1)
        board = self.position.board
        
        for pawn_col in [col-1, col+1]:
            if board.is_valid_position(pawn_row, pawn_col):
                piece = board.get_piece_at(pawn_row, pawn_col)
                if (piece and 
                    piece.piece_type == PieceType.PAWN and 
                    piece.color == self.color):
                    return True
        return False

    def _is_near_corner(self) -> bool:
        """Kiểm tra mã có gần góc bàn cờ không"""
        if not self.position:
            return False
            
        row, col = self.position.row, self.position.col
        return (row in [0, 1, 6, 7] and col in [0, 1, 6, 7])

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.symbol