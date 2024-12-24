# pieces/pawn.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

if TYPE_CHECKING:
    from ..square import Square
    from ..board import Board
    from ..move import Move, MoveType

class Pawn(Piece):
    """
    Class quân tốt kế thừa từ Piece.
    Đặc điểm:
    - Chỉ đi thẳng về phía trước
    - Nước đầu có thể đi 2 ô
    - Bắt chéo
    - Phong cấp khi đến cuối bàn cờ
    """
    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân tốt
        Args:
            color: Màu quân tốt
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.PAWN)
        self._promotion_row = 0 if color == PieceColor.WHITE else 7

    @property
    def direction(self) -> int:
        """Hướng di chuyển: -1 cho trắng (đi lên), 1 cho đen (đi xuống)"""
        return -1 if self.color == PieceColor.WHITE else 1

    @property
    def start_row(self) -> int:
        """Hàng xuất phát: 6 cho trắng, 1 cho đen"""
        return 6 if self.color == PieceColor.WHITE else 1

    def get_possible_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả nước đi có thể của tốt
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        current_row = self.position.row
        current_col = self.position.col

        # Kiểm tra di chuyển thẳng
        moves.extend(self._get_forward_moves(board))
        
        # Kiểm tra bắt chéo
        moves.extend(self._get_capture_moves(board))
        
        # Kiểm tra bắt tốt qua đường
        moves.extend(self._get_en_passant_moves(board))

        return moves

    def _get_forward_moves(self, board: 'Board') -> List['Move']:
        """Lấy các nước đi thẳng"""
        moves = []
        next_row = self.position.row + self.direction

        # Kiểm tra nước đi thẳng 1 ô
        if 0 <= next_row < 8:
            front_square = board.get_square(next_row, self.position.col)
            if not front_square.is_occupied():
                moves.append(self._create_move(front_square))

                # Kiểm tra nước đi thẳng 2 ô (chỉ cho nước đi đầu)
                if not self.has_moved and self.position.row == self.start_row:
                    two_ahead = board.get_square(next_row + self.direction, 
                                              self.position.col)
                    if not two_ahead.is_occupied():
                        moves.append(self._create_move(two_ahead))

        return moves

    def _get_capture_moves(self, board: 'Board') -> List['Move']:
        """Lấy các nước bắt chéo"""
        moves = []
        next_row = self.position.row + self.direction

        # Kiểm tra 2 ô chéo
        for col_offset in [-1, 1]:
            if 0 <= next_row < 8:
                capture_col = self.position.col + col_offset
                if 0 <= capture_col < 8:
                    target = board.get_square(next_row, capture_col)
                    if target.has_enemy_piece(self.color):
                        moves.append(self._create_move(target, is_capture=True))

        return moves

    def _get_en_passant_moves(self, board: 'Board') -> List['Move']:
        """Lấy các nước bắt tốt qua đường"""
        moves = []
        
        # Kiểm tra điều kiện bắt tốt qua đường
        if board.last_move and isinstance(board.last_move.piece, Pawn):
            last_move = board.last_move
            if (abs(last_move.start_square.row - last_move.end_square.row) == 2 and
                self.position.row == last_move.end_square.row and
                abs(self.position.col - last_move.end_square.col) == 1):
                
                # Tạo nước đi en passant
                target_row = self.position.row + self.direction
                target = board.get_square(target_row, last_move.end_square.col)
                moves.append(self._create_move(target, is_en_passant=True))

        return moves

    def _create_move(self, end_square: 'Square', 
                    is_capture: bool = False,
                    is_en_passant: bool = False) -> 'Move':
        """
        Tạo nước đi cho tốt
        Args:
            end_square: Ô đích
            is_capture: Có phải nước bắt quân không
            is_en_passant: Có phải bắt tốt qua đường không
        Returns:
            Nước đi được tạo
        """
        # Import cục bộ để tránh circular import
        from ..move import Move, MoveType

        is_promotion = end_square.row == self._promotion_row
        move_type = MoveType(
            is_capture=is_capture,
            is_promotion=is_promotion,
            is_en_passant=is_en_passant
        )

        return Move(
            start_square=self.position,
            end_square=end_square,
            piece=self,
            move_type=move_type
        )

    def can_promote(self) -> bool:
        """Kiểm tra có thể phong cấp không"""
        return self.position.row == self._promotion_row

    def __str__(self) -> str:
        """String representation"""
        return f"{self.color.value} Pawn"
    
    def _get_capture_moves(self, board: 'Board') -> List[Move]:
        """Lấy các nước bắt chéo"""
        moves = []
        row = self.position.row
        col = self.position.col
        
        # Kiểm tra 2 ô chéo phía trước
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            new_row = row + self.direction
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_square(new_row, new_col)
                if target.has_enemy_piece(self.color):
                    move = self._create_move(target)
                    # Kiểm tra phong cấp
                    if new_row == self._promotion_row:
                        move._move_type.is_promotion = True
                    moves.append(move)
                    
        return moves

    def can_be_promoted(self) -> bool:
        """Kiểm tra tốt có thể phong cấp không"""
        return self.position.row == self._promotion_row