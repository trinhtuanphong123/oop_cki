# pieces/pawn.py
from typing import List, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType
from ..move import Move, MoveType

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

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
        super().__init__(color, position)
        self._piece_type = PieceType.PAWN
        self._promotion_row = 0 if color == PieceColor.WHITE else 7
    
    
    @property 
    def direction(self) -> int:
        """Hướng di chuyển: -1 cho trắng (đi lên), 1 cho đen (đi xuống)"""
        return -1 if self.color == PieceColor.WHITE else 1

    @property
    def start_row(self) -> int:
        """Hàng xuất phát: 6 cho trắng, 1 cho đen"""
        return 6 if self.color == PieceColor.WHITE else 1

    def get_possible_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả nước đi có thể của tốt
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi có thể
        """
        if not self.position or not board:
            return []

        moves = []
        moves.extend(self._get_forward_moves(board))
        moves.extend(self._get_capture_moves(board))
        moves.extend(self._get_en_passant_moves(board))
        return moves

    def _get_forward_moves(self, board: 'Board') -> List[Move]:
        """Lấy các nước đi thẳng"""
        moves = []
        next_row = self.position.row + self.direction

        if 0 <= next_row < 8:
            front_square = board.get_square(next_row, self.position.col)
            if not front_square.piece:
                move = self._create_move(
                    front_square, 
                    is_promotion=(next_row == self._promotion_row)
                )
                moves.append(move)

                if not self.has_moved and self.position.row == self.start_row:
                    two_ahead = board.get_square(
                        next_row + self.direction,
                        self.position.col
                    )
                    if not two_ahead.piece:
                        moves.append(self._create_move(two_ahead))

        return moves

    def _get_capture_moves(self, board: 'Board') -> List[Move]:
        """Lấy các nước bắt chéo"""
        moves = []
        next_row = self.position.row + self.direction

        if 0 <= next_row < 8:
            for col_offset in [-1, 1]:
                new_col = self.position.col + col_offset
                if 0 <= new_col < 8:
                    target = board.get_square(next_row, new_col)
                    if target.piece and target.piece.color != self.color:
                        move = self._create_move(
                            target,
                            is_capture=True,
                            is_promotion=(next_row == self._promotion_row)
                        )
                        moves.append(move)

        return moves

    def _get_en_passant_moves(self, board: 'Board') -> List[Move]:
        """Lấy các nước bắt tốt qua đường"""
        moves = []
        
        if not board.last_move or not isinstance(board.last_move.piece, Pawn):
            return moves

        last_move = board.last_move
        if (abs(last_move.start_square.row - last_move.end_square.row) == 2 and
            self.position.row == last_move.end_square.row and
            abs(self.position.col - last_move.end_square.col) == 1):
            
            target = board.get_square(
                self.position.row + self.direction,
                last_move.end_square.col
            )
            moves.append(self._create_move(target, is_en_passant=True))

        return moves

    def _create_move(self, 
                    end_square: 'Square', 
                    is_capture: bool = False,
                    is_promotion: bool = False,
                    is_en_passant: bool = False) -> Move:
        """Tạo một nước đi mới"""
        move_type = MoveType(
            is_capture=is_capture,
            is_promotion=is_promotion,
            is_en_passant=is_en_passant
        )
        return Move(self.position, end_square, self, move_type)

    def calculate_value(self) -> int:
        """Tính giá trị của quân tốt dựa trên vị trí"""
        base_value = 100  # Giá trị cơ bản của tốt

        if not self.position or not self.position.board:
            return base_value

        position_bonus = 0
        row, col = self.position.row, self.position.col

        # Thưởng cho việc tiến gần đích (phong cấp)
        distance_to_promotion = abs(self._promotion_row - row)
        position_bonus += (7 - distance_to_promotion) * 10

        # Thưởng cho tốt ở trung tâm
        center_distance = abs(3.5 - col)
        if center_distance <= 1.5:
            position_bonus += 20

        # Thưởng cho tốt đôi và thông thoáng
        if self._has_pawn_support(self.position.board):
            position_bonus += 15
        if self._is_passed_pawn(self.position.board):
            position_bonus += 50

        # Phạt cho tốt bị cô lập hoặc chậm
        if self._is_isolated(self.position.board):
            position_bonus -= 20
        if self._is_backward(self.position.board):
            position_bonus -= 15

        return base_value + position_bonus

    def _has_pawn_support(self, board: 'Board') -> bool:
        """Kiểm tra tốt có được hỗ trợ bởi tốt khác không"""
        if not self.position:
            return False

        row, col = self.position.row, self.position.col
        for adjacent_col in [col - 1, col + 1]:
            if 0 <= adjacent_col < 8:
                piece = board.get_piece_at(row, adjacent_col)
                if (piece and 
                    piece.piece_type == PieceType.PAWN and 
                    piece.color == self.color):
                    return True
        return False

    def _is_passed_pawn(self, board: 'Board') -> bool:
        """Kiểm tra có phải tốt thông thoáng không"""
        if not self.position:
            return False

        row, col = self.position.row, self.position.col
        enemy_direction = -self.direction

        for check_col in [col - 1, col, col + 1]:
            if not (0 <= check_col < 8):
                continue
            
            check_row = row
            while 0 <= check_row < 8:
                piece = board.get_piece_at(check_row, check_col)
                if (piece and 
                    piece.piece_type == PieceType.PAWN and 
                    piece.color != self.color):
                    return False
                check_row += enemy_direction
            
        return True

    def _is_isolated(self, board: 'Board') -> bool:
        """Kiểm tra có phải tốt cô lập không"""
        if not self.position:
            return False

        col = self.position.col
        for adjacent_col in [col - 1, col + 1]:
            if not (0 <= adjacent_col < 8):
                continue
            
            for row in range(8):
                piece = board.get_piece_at(row, adjacent_col)
                if (piece and 
                    piece.piece_type == PieceType.PAWN and 
                    piece.color == self.color):
                    return False
        return True

    def _is_backward(self, board: 'Board') -> bool:
        """Kiểm tra có phải tốt chậm không"""
        if not self.position:
            return False

        row, col = self.position.row, self.position.col
        for support_col in [col - 1, col + 1]:
            if not (0 <= support_col < 8):
                continue
            
            support_row = row + self.direction
            if 0 <= support_row < 8:
                piece = board.get_piece_at(support_row, support_col)
                if (piece and 
                    piece.piece_type == PieceType.PAWN and 
                    piece.color == self.color):
                    return False
        return True

    def can_promote(self) -> bool:
        """Kiểm tra có thể phong cấp không"""
        return self.position and self.position.row == self._promotion_row

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.symbol