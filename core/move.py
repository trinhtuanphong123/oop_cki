from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, TYPE_CHECKING
from core.pieces.piece import PieceType

if TYPE_CHECKING:
    from core.pieces.piece import Piece
    from .square import Square

class MoveType(Enum):
    """Định nghĩa các loại nước đi trong cờ vua"""
    NORMAL = auto()      # Nước đi thông thường
    CAPTURE = auto()     # Bắt quân
    CASTLE = auto()      # Nhập thành
    EN_PASSANT = auto()  # Bắt tốt qua đường
    PROMOTION = auto()   # Phong cấp
    DOUBLE_PUSH = auto() # Tốt đi 2 ô

@dataclass
class Move:
    """
    Class đại diện cho một nước đi trong cờ vua.
    Lưu trữ thông tin về vị trí bắt đầu, kết thúc và các đặc tính của nước đi.
    """
    start_square: 'Square'
    end_square: 'Square'
    moving_piece: 'Piece'
    move_type: MoveType
    captured_piece: Optional['Piece'] = None
    promotion_piece_type: Optional[PieceType] = None
    
    # Cho nhập thành
    castle_rook_start: Optional['Square'] = None
    castle_rook_end: Optional['Square'] = None

    def __post_init__(self):
        """
        Kiểm tra tính hợp lệ của nước đi sau khi khởi tạo.
        Raises:
            ValueError: Nếu nước đi không hợp lệ
        """
        # Kiểm tra các ô không được None
        if not all([self.start_square, self.end_square, self.moving_piece]):
            raise ValueError("Start square, end square and moving piece are required")

        # Kiểm tra vị trí hợp lệ
        for square in (self.start_square, self.end_square):
            if not (0 <= square.row < 8 and 0 <= square.col < 8):
                raise ValueError(f"Invalid square position: {square}")

        # Kiểm tra promotion
        if (self.move_type == MoveType.PROMOTION and 
            not self.promotion_piece_type):
            raise ValueError("Promotion move requires promotion piece type")

        # Kiểm tra castle
        if (self.move_type == MoveType.CASTLE and 
            not all([self.castle_rook_start, self.castle_rook_end])):
            raise ValueError("Castle move requires rook positions")

    @property
    def is_capture(self) -> bool:
        """Kiểm tra có phải nước bắt quân không"""
        return self.move_type in (MoveType.CAPTURE, MoveType.EN_PASSANT)

    @property
    def is_castle(self) -> bool:
        """Kiểm tra có phải nước nhập thành không"""
        return self.move_type == MoveType.CASTLE

    @property
    def is_promotion(self) -> bool:
        """Kiểm tra có phải nước phong cấp không"""
        return self.move_type == MoveType.PROMOTION

    @property
    def is_en_passant(self) -> bool:
        """Kiểm tra có phải nước bắt tốt qua đường không"""
        return self.move_type == MoveType.EN_PASSANT

    @property 
    def is_double_push(self) -> bool:
        """Kiểm tra có phải nước đi 2 ô của tốt không"""
        return self.move_type == MoveType.DOUBLE_PUSH

    def get_move_notation(self) -> str:
        """
        Trả về ký hiệu algebraic của nước đi.
        Ví dụ: e4, Nf3, O-O, exd5, etc.
        """
        if self.is_castle:
            return "O-O" if self.end_square.col > self.start_square.col else "O-O-O"

        piece_letter = self.moving_piece.piece_type.name[0]
        if self.moving_piece.piece_type == PieceType.PAWN:
            piece_letter = ''

        capture_notation = 'x' if self.is_capture else ''
        end_position = f"{chr(97 + self.end_square.col)}{8 - self.end_square.row}"
        
        promotion_notation = ''
        if self.is_promotion and self.promotion_piece_type:
            promotion_notation = f"={self.promotion_piece_type.name[0]}"

        return f"{piece_letter}{capture_notation}{end_position}{promotion_notation}"

    def clone(self) -> 'Move':
        """
        Tạo bản sao của nước đi.
        Returns:
            Move: Bản sao của nước đi
        """
        return Move(
            start_square=self.start_square,
            end_square=self.end_square,
            moving_piece=self.moving_piece,
            move_type=self.move_type,
            captured_piece=self.captured_piece,
            promotion_piece_type=self.promotion_piece_type,
            castle_rook_start=self.castle_rook_start,
            castle_rook_end=self.castle_rook_end
        )

    def __eq__(self, other: object) -> bool:
        """So sánh hai nước đi"""
        if not isinstance(other, Move):
            return NotImplemented
        return (self.start_square == other.start_square and
                self.end_square == other.end_square and
                self.move_type == other.move_type and
                self.moving_piece == other.moving_piece)

    def __hash__(self) -> int:
        """Hash của nước đi"""
        return hash((self.start_square, self.end_square, 
                    self.move_type, self.moving_piece))

    def __str__(self) -> str:
        """Chuỗi đại diện của nước đi"""
        return self.get_move_notation()

    def __repr__(self) -> str:
        """Chuỗi đại diện chi tiết của nước đi"""
        return (f"Move({self.moving_piece} from {self.start_square} "
                f"to {self.end_square}, type={self.move_type.name})")