# pieces/king.py
from typing import List, Optional, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType
from ..move import Move, MoveType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from .rook import Rook

class King(Piece):
    """
    Class đại diện cho quân Vua trong cờ vua.
    Đặc điểm:
    - Di chuyển một ô theo mọi hướng
    - Có thể nhập thành với xe
    - Không thể đi vào ô bị chiếu
    - Quan trọng nhất trong game
    """

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Vua
        Args:
            color: Màu của quân Vua
            position: Vị trí ban đầu
        """
        super().__init__(color, position)
        self._piece_type = PieceType.KING

    def get_possible_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi có thể của quân Vua
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        if not self.position or not board:
            return []

        moves = []

        # Tất cả các hướng di chuyển có thể của vua
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Các hướng trên
            (0, -1),           (0, 1),    # Các hướng ngang
            (1, -1),  (1, 0),  (1, 1)     # Các hướng dưới
        ]

        # Thêm các nước đi thông thường
        moves.extend(self._get_normal_moves(board, directions))

        # Thêm các nước nhập thành nếu có thể
        moves.extend(self._get_castling_moves(board))

        return moves

    def _get_normal_moves(self, board: 'Board', directions: List[tuple]) -> List[Move]:
        """
        Lấy các nước đi thông thường
        Args:
            board: Bàn cờ hiện tại
            directions: Danh sách các hướng di chuyển
        Returns:
            Danh sách các nước đi thông thường
        """
        moves = []
        for row_step, col_step in directions:
            new_row = self.position.row + row_step
            new_col = self.position.col + col_step

            if board.is_valid_position(new_row, new_col):
                target = board.get_square(new_row, new_col)
                if not target.has_friendly_piece(self.color):
                    move_type = MoveType(is_capture=target.piece is not None)
                    moves.append(Move(self.position, target, self, move_type))

        return moves

    def _get_castling_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy các nước nhập thành có thể
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước nhập thành có thể
        """
        moves = []
        if not self.can_castle():
            return moves

        # Kiểm tra nhập thành hai bên
        for is_kingside in [True, False]:
            rook = self._get_castling_rook(board, is_kingside)
            if self._can_castle_with_rook(board, rook, is_kingside):
                col_offset = 2 if is_kingside else -2
                target = board.get_square(
                    self.position.row, 
                    self.position.col + col_offset
                )
                move_type = MoveType(is_castle=True)
                moves.append(Move(self.position, target, self, move_type))

        return moves

    def _get_castling_rook(self, board: 'Board', kingside: bool) -> Optional['Rook']:
        """
        Lấy xe để nhập thành
        Args:
            board: Bàn cờ hiện tại
            kingside: True nếu là nhập thành cánh vua
        Returns:
            Xe để nhập thành hoặc None
        """
        if not self.position:
            return None

        row = self.position.row
        col = 7 if kingside else 0
        piece = board.get_piece_at(row, col)
        
        from .rook import Rook
        return piece if isinstance(piece, Rook) and piece.color == self.color else None

    def _can_castle_with_rook(self, board: 'Board', rook: Optional['Rook'], kingside: bool) -> bool:
        """
        Kiểm tra có thể nhập thành với xe không
        """
        if not rook or not rook.can_castle():
            return False

        # Kiểm tra đường đi trống và không bị chiếu
        direction = 1 if kingside else -1
        col = self.position.col
        
        while col != rook.position.col:
            col += direction
            if col == rook.position.col:
                break
                
            # Kiểm tra ô trống
            if board.get_piece_at(self.position.row, col):
                return False
                
            # Kiểm tra ô không bị chiếu
            square = board.get_square(self.position.row, col)
            if board.is_square_attacked(square, self.color.opposite):
                return False

        return True

    def can_castle(self) -> bool:
        """Kiểm tra vua có thể nhập thành không"""
        return not self.has_moved and not self.is_in_check(self.position.board)

    def is_in_check(self, board: 'Board') -> bool:
        """Kiểm tra vua có đang bị chiếu không"""
        return (board and self.position and 
                board.is_square_attacked(self.position, self.color.opposite))

    def calculate_value(self) -> int:
        """Giá trị của quân vua"""
        return 20000  # Giá trị tối đa

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.symbol