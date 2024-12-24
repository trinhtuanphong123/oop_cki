# pieces/king.py
from typing import List, Optional, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square
    from ..move import Move, MoveType
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
        super().__init__(color, position, PieceType.KING)

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi có thể của quân Vua
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
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

    def _get_normal_moves(self, board: 'Board', directions: List[tuple]) -> List['Move']:
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
                    moves.append(self._create_move(target))

        return moves

    def _get_castling_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy các nước nhập thành có thể
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước nhập thành có thể
        """
        moves = []
        if self.can_castle():
            # Kiểm tra nhập thành cánh vua
            kingside_rook = self._get_castling_rook(board, True)
            if self._can_castle_with_rook(board, kingside_rook, True):
                target = board.get_square(self.position.row, self.position.col + 2)
                moves.append(self._create_castle_move(target, True))

            # Kiểm tra nhập thành cánh hậu
            queenside_rook = self._get_castling_rook(board, False)
            if self._can_castle_with_rook(board, queenside_rook, False):
                target = board.get_square(self.position.row, self.position.col - 2)
                moves.append(self._create_castle_move(target, False))

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
        row = self.position.row
        col = 7 if kingside else 0
        piece = board.get_piece_at(row, col)
        
        from .rook import Rook
        if isinstance(piece, Rook) and piece.color == self.color:
            return piece
        return None

    def _can_castle_with_rook(self, board: 'Board', rook: Optional['Rook'], kingside: bool) -> bool:
        """
        Kiểm tra có thể nhập thành với xe không
        Args:
            board: Bàn cờ hiện tại
            rook: Xe để nhập thành
            kingside: True nếu là nhập thành cánh vua
        Returns:
            True nếu có thể nhập thành
        """
        if not rook or not rook.can_castle():
            return False

        # Kiểm tra đường đi có trống không
        direction = 1 if kingside else -1
        start_col = self.position.col + direction
        end_col = rook.position.col
        
        if not kingside:
            # Cánh hậu cần thêm một ô trống
            end_col += 1

        col = start_col
        while col != end_col:
            if board.get_piece_at(self.position.row, col):
                return False
            col += direction

        # Kiểm tra các ô vua đi qua có bị chiếu không
        return not self._path_is_attacked(board, kingside)

    def _path_is_attacked(self, board: 'Board', kingside: bool) -> bool:
        """
        Kiểm tra đường đi có bị tấn công không
        Args:
            board: Bàn cờ hiện tại
            kingside: True nếu là nhập thành cánh vua
        Returns:
            True nếu đường đi bị tấn công
        """
        direction = 1 if kingside else -1
        col = self.position.col
        end_col = col + (3 * direction)
        
        while col != end_col:
            square = board.get_square(self.position.row, col)
            if board.is_square_attacked(square, self.color.opposite):
                return True
            col += direction
            
        return False

    def _create_move(self, target: 'Square') -> 'Move':
        """Tạo nước đi thông thường"""
        from ..move import Move, MoveType
        return Move(self.position, target, self, MoveType())

    def _create_castle_move(self, target: 'Square', is_kingside: bool) -> 'Move':
        """Tạo nước nhập thành"""
        from ..move import Move, MoveType
        return Move(
            self.position,
            target,
            self,
            MoveType(is_castle=True)
        )

    def can_castle(self) -> bool:
        """Kiểm tra vua có thể nhập thành không"""
        return not self.has_moved

    def is_in_check(self, board: 'Board') -> bool:
        """Kiểm tra vua có đang bị chiếu không"""
        return board.is_square_attacked(self.position, self.color.opposite)

    def calculate_value(self) -> int:
        """
        Tính giá trị của quân vua
        Returns:
            Giá trị của quân vua
        """
        return 20000  # Giá trị tối đa vì vua là quân quan trọng nhất

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{'W' if self.color == PieceColor.WHITE else 'B'}K"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"King(color={self.color.value}, "
                f"position={self.position}, "
                f"has_moved={self.has_moved})")