# king.py

from typing import List
from .piece import Piece, PieceColor, PieceType
from ..square import Square
from ..move import Move
from .. board import Board

class King(Piece):
    """
    Class quân Vua kế thừa từ Piece.
    Đặc điểm:
    - Di chuyển 1 ô theo mọi hướng
    - Có thể nhập thành với xe
    - Không thể đi vào ô bị tấn công
    """
    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Vua
        Args:
            color: Màu quân Vua
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.KING)
        self._can_castle = True

    @property
    def can_castle(self) -> bool:
        """Khả năng nhập thành"""
        return self._can_castle and not self.has_moved

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy danh sách nước đi có thể của Vua
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        curr_row, curr_col = self.position.row, self.position.col

        # 8 hướng di chuyển của Vua
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        # Kiểm tra các nước đi thông thường
        for d_row, d_col in directions:
            new_row, new_col = curr_row + d_row, curr_col + d_col
            
            if not self._is_valid_position(new_row, new_col):
                continue

            target = board.get_square(new_row, new_col)
            if target.is_occupied() and not self.is_enemy(target.piece):
                continue

            moves.append(self._create_move(target))

        # Thêm nước nhập thành nếu có thể
        if self.can_castle:
            castle_moves = self._get_castle_moves(board)
            moves.extend(castle_moves)

        return moves

    def _get_castle_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy các nước nhập thành hợp lệ
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách nước nhập thành có thể
        """
        moves = []
        
        # Vị trí cơ bản cho nhập thành
        row = 7 if self.color == PieceColor.WHITE else 0
        king_col = 4

        # Kiểm tra nhập thành phải
        if self._can_castle_kingside(board, row):
            target = board.get_square(row, king_col + 2)
            moves.append(self._create_move(target, is_castle=True))

        # Kiểm tra nhập thành trái
        if self._can_castle_queenside(board, row):
            target = board.get_square(row, king_col - 2)
            moves.append(self._create_move(target, is_castle=True))

        return moves

    def _can_castle_kingside(self, board: 'Board', row: int) -> bool:
        """Kiểm tra có thể nhập thành cánh vua"""
        # Kiểm tra đường đi trống
        if not all(not board.get_square(row, col).is_occupied() 
                  for col in [5, 6]):
            return False

        # Kiểm tra xe còn tại vị trí
        rook_square = board.get_square(row, 7)
        return (rook_square.is_occupied() and
                rook_square.piece.piece_type == PieceType.ROOK and
                not rook_square.piece.has_moved)

    def _can_castle_queenside(self, board: 'Board', row: int) -> bool:
        """Kiểm tra có thể nhập thành cánh hậu"""
        # Kiểm tra đường đi trống
        if not all(not board.get_square(row, col).is_occupied() 
                  for col in [1, 2, 3]):
            return False

        # Kiểm tra xe còn tại vị trí
        rook_square = board.get_square(row, 0)
        return (rook_square.is_occupied() and
                rook_square.piece.piece_type == PieceType.ROOK and
                not rook_square.piece.has_moved)

    def _create_move(self, end_square: 'Square', is_castle: bool = False) -> 'Move':
        """
        Tạo nước đi cho Vua
        Args:
            end_square: Ô đích
            is_castle: Có phải nhập thành không
        Returns:
            Nước đi được tạo
        """
        return Move(
            start_square=self.position,
            end_square=end_square,
            moving_piece=self,
            is_capture=end_square.is_occupied(),
            is_castle=is_castle
        )

    def __str__(self) -> str:
        """String representation"""
        return f"{self.color.value} King"