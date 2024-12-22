from typing import List, Optional, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor, Move

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

class Pawn(Piece):
    """
    Class đại diện cho quân tốt trong cờ vua.
    Quân tốt có những quy tắc di chuyển đặc biệt:
    - Chỉ đi thẳng về phía trước
    - Có thể đi 2 ô ở nước đầu tiên
    - Bắt quân theo đường chéo
    - Có thể phong cấp khi đến cuối bàn cờ
    - Có thể bắt tốt qua đường
    """
    __slots__ = ('_en_passant_vulnerable', '_promotion_row')

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân tốt
        
        Args:
            color: Màu của quân tốt
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.PAWN)
        self._en_passant_vulnerable = False
        # Hàng phong cấp (0 cho trắng, 7 cho đen)
        self._promotion_row = 0 if color == PieceColor.WHITE else 7

    @property
    def direction(self) -> int:
        """Hướng di chuyển của tốt (-1 cho trắng đi lên, 1 cho đen đi xuống)"""
        return -1 if self.color == PieceColor.WHITE else 1

    @property
    def start_row(self) -> int:
        """Hàng xuất phát của tốt (6 cho trắng, 1 cho đen)"""
        return 6 if self.color == PieceColor.WHITE else 1

    @property
    def en_passant_vulnerable(self) -> bool:
        """Kiểm tra tốt có thể bị bắt qua đường không"""
        return self._en_passant_vulnerable

    def get_legal_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân tốt
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        moves = []
        current_row, current_col = self.position.row, self.position.col

        # Di chuyển thẳng 1 ô
        next_row = current_row + self.direction
        if self._is_valid_position(next_row, current_col):
            front_square = board.get_square(next_row, current_col)
            if not front_square.is_occupied():
                moves.append(self._create_move((next_row, current_col)))
                
                # Di chuyển thẳng 2 ô ở nước đầu
                if not self.has_moved and current_row == self.start_row:
                    two_step_row = next_row + self.direction
                    two_step_square = board.get_square(two_step_row, current_col)
                    if not two_step_square.is_occupied():
                        moves.append(self._create_move((two_step_row, current_col)))

        # Bắt quân chéo
        for col_offset in [-1, 1]:
            capture_col = current_col + col_offset
            if self._is_valid_position(next_row, capture_col):
                target_square = board.get_square(next_row, capture_col)
                if target_square.has_enemy_piece(self.color):
                    moves.append(self._create_move(
                        (next_row, capture_col), 
                        is_capture=True
                    ))

        # Bắt tốt qua đường
        en_passant_moves = self._get_en_passant_moves(board)
        moves.extend(en_passant_moves)

        return moves

    def _get_en_passant_moves(self, board: 'Board') -> List[Move]:
        """
        Kiểm tra và trả về các nước đi bắt tốt qua đường
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Move]: Danh sách nước đi bắt tốt qua đường
        """
        moves = []
        current_row, current_col = self.position.row, self.position.col

        if current_row != (3 if self.color == PieceColor.WHITE else 4):
            return moves

        for col_offset in [-1, 1]:
            capture_col = current_col + col_offset
            if not self._is_valid_position(current_row, capture_col):
                continue

            adjacent_square = board.get_square(current_row, capture_col)
            if not adjacent_square.is_occupied():
                continue

            adjacent_piece = adjacent_square.piece
            if (isinstance(adjacent_piece, Pawn) and 
                adjacent_piece.color != self.color and 
                adjacent_piece.en_passant_vulnerable):
                
                moves.append(self._create_move(
                    (current_row + self.direction, capture_col),
                    is_capture=True,
                    is_en_passant=True
                ))

        return moves

    def move_to(self, new_square: 'Square', board: 'Board') -> None:
        """
        Di chuyển tốt đến ô mới và xử lý các trường hợp đặc biệt
        
        Args:
            new_square: Ô đích
            board: Bàn cờ hiện tại
        """
        old_row = self.position.row
        super().move_to(new_square, board)

        # Cập nhật trạng thái bắt tốt qua đường
        self._en_passant_vulnerable = (
            not self.has_moved and 
            abs(new_square.row - old_row) == 2
        )

        # Xử lý phong cấp
        if new_square.row == self._promotion_row:
            self._handle_promotion(board)

    def _handle_promotion(self, board: 'Board') -> None:
        """
        Xử lý việc phong cấp tốt
        
        Args:
            board: Bàn cờ hiện tại
        """
        # Logic phong cấp sẽ được xử lý ở lớp Board hoặc Game
        pass

    def _create_move(self, 
                    end: Tuple[int, int], 
                    is_capture: bool = False,
                    is_en_passant: bool = False) -> Move:
        """
        Tạo đối tượng Move với các thông tin cần thiết
        
        Args:
            end: Tọa độ đích
            is_capture: Có phải nước bắt quân không
            is_en_passant: Có phải bắt tốt qua đường không
            
        Returns:
            Move: Đối tượng Move được tạo
        """
        start = (self.position.row, self.position.col)
        is_promotion = end[0] == self._promotion_row

        return Move(
            start=start,
            end=end,
            is_capture=is_capture,
            is_en_passant=is_en_passant,
            is_promotion=is_promotion
        )

    def get_position_value(self, board: 'Board') -> float:
        """
        Tính điểm vị trí của quân tốt
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            float: Điểm vị trí
        """
        value = 0.0
        row, col = self.position.row, self.position.col

        # Khuyến khích tốt tiến lên
        value += 0.1 * abs(row - self.start_row)

        # Thưởng cho tốt ở trung tâm
        if 2 <= col <= 5:
            value += 0.1

        # Phạt tốt đôi/ba
        for offset in [-1, 1]:
            if (self._is_valid_position(row, col + offset) and
                isinstance(board.get_square(row, col + offset).piece, Pawn)):
                value -= 0.2

        return value

    def __str__(self) -> str:
        """Chuỗi đại diện của quân tốt"""
        return f"{self.color.value} Pawn at {self.position}"

    def clone(self) -> 'Pawn':
        """Tạo bản sao của quân tốt"""
        clone = Pawn(self.color, self.position)
        clone._has_moved = self._has_moved
        clone._en_passant_vulnerable = self._en_passant_vulnerable
        return clone