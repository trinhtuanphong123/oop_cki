# move.py

from dataclasses import dataclass
from typing import Optional
from core.pieces.piece import Piece, PieceType
from .square import Square

@dataclass(frozen=True)
class Move:
    """
    Class đại diện cho một nước đi trên bàn cờ.
    Sử dụng frozen=True để đảm bảo immutable.
    """
    # Thuộc tính cơ bản
    start_square: Square
    end_square: Square
    moving_piece: Piece
    
    # Các loại nước đi đặc biệt
    is_capture: bool = False
    is_castle: bool = False
    is_promotion: bool = False
    is_en_passant: bool = False
    promotion_piece_type: Optional[PieceType] = None

    def __post_init__(self):
        """Validate nước đi sau khi khởi tạo"""
        self._validate_move()

    def _validate_move(self) -> None:
        """
        Kiểm tra tính hợp lệ cơ bản của nước đi
        Raises:
            ValueError nếu nước đi không hợp lệ
        """
        # Kiểm tra ô xuất phát có quân di chuyển không
        if self.moving_piece != self.start_square.piece:
            raise ValueError("Start square must contain the moving piece")

        # Kiểm tra ô đích khác ô xuất phát
        if self.start_square == self.end_square:
            raise ValueError("Start and end squares must be different")

        # Kiểm tra nước promotion
        if self.is_promotion and not self.promotion_piece_type:
            raise ValueError("Promotion moves must specify the promotion piece type")

    @property
    def is_diagonal(self) -> bool:
        """Kiểm tra có phải nước đi chéo không"""
        row_diff = abs(self.end_square.row - self.start_square.row)
        col_diff = abs(self.end_square.col - self.start_square.col)
        return row_diff == col_diff and row_diff > 0

    @property
    def is_vertical(self) -> bool:
        """Kiểm tra có phải nước đi dọc không"""
        return (self.start_square.col == self.end_square.col and
                self.start_square.row != self.end_square.row)

    @property
    def is_horizontal(self) -> bool:
        """Kiểm tra có phải nước đi ngang không"""
        return (self.start_square.row == self.end_square.row and
                self.start_square.col != self.end_square.col)

    @property
    def algebraic_notation(self) -> str:
        """
        Chuyển đổi nước đi sang ký hiệu đại số
        Ví dụ: e2-e4, Nf3, O-O
        """
        # Nhập thành
        if self.is_castle:
            return "O-O" if self.end_square.col > self.start_square.col else "O-O-O"

        # Các nước đi thông thường
        piece_symbol = self.moving_piece.piece_type.name[0]
        if self.moving_piece.piece_type == PieceType.PAWN:
            piece_symbol = ''

        capture_symbol = 'x' if self.is_capture else ''
        end_position = self.end_square.algebraic

        # Thêm ký hiệu phong cấp
        promotion = ''
        if self.is_promotion and self.promotion_piece_type:
            promotion = f"={self.promotion_piece_type.name[0]}"

        return f"{piece_symbol}{self.start_square.algebraic}{capture_symbol}{end_position}{promotion}"

    def create_reverse_move(self) -> 'Move':
        """
        Tạo nước đi ngược lại (để undo)
        Returns:
            Move: Nước đi ngược lại
        """
        return Move(
            start_square=self.end_square,
            end_square=self.start_square,
            moving_piece=self.moving_piece
        )

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return self.algebraic_notation

    def __repr__(self) -> str:
        """String representation chi tiết"""
        move_type = []
        if self.is_capture:
            move_type.append("capture")
        if self.is_castle:
            move_type.append("castle")
        if self.is_promotion:
            move_type.append(f"promotion to {self.promotion_piece_type.name}")
        if self.is_en_passant:
            move_type.append("en passant")

        type_str = ", ".join(move_type) if move_type else "normal"
        return (f"Move({self.moving_piece} from {self.start_square} "
                f"to {self.end_square} [{type_str}])")