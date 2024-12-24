# move.py
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .square import Square
    from .pieces.piece import Piece,PieceType
    from .pieces.pawn import Pawn
    from .pieces.king import King
    from .board import Board

@dataclass
class MoveType:
    """
    Value Object chứa thông tin về loại nước đi.
    Sử dụng @dataclass để tự động tạo __init__, __eq__, etc.
    """
    is_capture: bool = False      # Nước bắt quân
    is_castle: bool = False       # Nước nhập thành
    is_en_passant: bool = False   # Nước bắt tốt qua đường
    is_promotion: bool = False    # Nước phong cấp
    promotion_piece_type: Optional['PieceType'] = None  # Loại quân khi phong cấp

class Move:
    """
    Class đại diện cho một nước đi trong game.
    Lưu trữ thông tin về điểm đầu, điểm cuối và các đặc tính của nước đi.
    """
    def __init__(self, 
                 start_square: 'Square',
                 end_square: 'Square',
                 piece: 'Piece',
                 move_type: Optional[MoveType] = None):
        """
        Khởi tạo nước đi
        Args:
            start_square: Ô xuất phát
            end_square: Ô đích
            piece: Quân cờ di chuyển
            move_type: Loại nước đi (optional)
        """
        self._start_square = start_square
        self._end_square = end_square
        self._piece = piece
        self._move_type = move_type or MoveType()
        self._captured_piece: Optional['Piece'] = end_square.piece

    # Properties
    @property
    def start_square(self) -> 'Square':
        """Ô xuất phát"""
        return self._start_square

    @property
    def end_square(self) -> 'Square':
        """Ô đích"""
        return self._end_square

    @property
    def piece(self) -> 'Piece':
        """Quân cờ di chuyển"""
        return self._piece

    @property
    def captured_piece(self) -> Optional['Piece']:
        """Quân bị bắt (nếu có)"""
        return self._captured_piece

    @property
    def is_capture(self) -> bool:
        """Có phải nước bắt quân không"""
        return self._move_type.is_capture or self._captured_piece is not None

    @property
    def is_castle(self) -> bool:
        """Có phải nước nhập thành không"""
        return self._move_type.is_castle

    @property
    def is_en_passant(self) -> bool:
        """Có phải nước bắt tốt qua đường không"""
        return self._move_type.is_en_passant

    @property
    def is_promotion(self) -> bool:
        """Có phải nước phong cấp không"""
        return self._move_type.is_promotion

    @property
    def promotion_piece_type(self) -> Optional['PieceType']:
        """Loại quân khi phong cấp"""
        return self._move_type.promotion_piece_type

    def execute(self, board: 'Board') -> bool:
        """
        Thực hiện nước đi trên bàn cờ
        Args:
            board: Bàn cờ hiện tại
        Returns:
            bool: True nếu thực hiện thành công
        """
        try:
            # Xử lý trường hợp đặc biệt trước
            if self.is_castle:
                self._execute_castle(board)
            elif self.is_en_passant:
                self._execute_en_passant(board)
            elif self.is_promotion:
                self._execute_promotion(board)
            else:
                self._execute_normal_move(board)

            return True
        except Exception as e:
            print(f"Error executing move: {e}")
            return False

    def _execute_normal_move(self, board: 'Board') -> None:
        """Thực hiện nước đi thông thường"""
        # Lưu lại quân bị bắt (nếu có)
        if self._captured_piece:
            board.remove_piece(self._captured_piece)

        # Di chuyển quân cờ
        self._start_square.remove_piece()
        self._end_square.place_piece(self._piece)
        self._piece.position = self._end_square

    def _execute_castle(self, board: 'Board') -> None:
        """Thực hiện nước nhập thành"""
        king = self._piece
        if not isinstance(king, 'King'):
            raise ValueError("Castling must be performed with a king")

        # Di chuyển vua
        self._execute_normal_move(board)

        # Di chuyển xe
        rook_start_col = 7 if self._end_square.col > self._start_square.col else 0
        rook_end_col = 5 if self._end_square.col > self._start_square.col else 3

        rook_start = board.get_square(self._start_square.row, rook_start_col)
        rook_end = board.get_square(self._start_square.row, rook_end_col)
        rook = rook_start.piece

        if rook:
            rook_start.remove_piece()
            rook_end.place_piece(rook)
            rook.position = rook_end

    def _execute_en_passant(self, board: 'Board') -> None:
        """Thực hiện bắt tốt qua đường"""
        # Di chuyển tốt
        self._execute_normal_move(board)

        # Loại bỏ tốt bị bắt
        captured_pawn_square = board.get_square(
            self._start_square.row,
            self._end_square.col
        )
        captured_pawn = captured_pawn_square.piece
        if captured_pawn:
            board.remove_piece(captured_pawn)
            captured_pawn_square.remove_piece()

    def _execute_promotion(self, board: 'Board') -> None:
        """Thực hiện phong cấp"""
        if not self.promotion_piece_type:
            raise ValueError("Promotion piece type must be specified")

        # Di chuyển tốt
        self._execute_normal_move(board)

        # Tạo quân mới và thay thế tốt
        from .pieces.piece import create_piece
        new_piece = create_piece(
            self.promotion_piece_type,
            self._piece.color,
            self._end_square
        )
        self._end_square.place_piece(new_piece)
        board.remove_piece(self._piece)

    def undo(self, board: 'Board') -> None:
        """
        Hoàn tác nước đi
        Args:
            board: Bàn cờ hiện tại
        """
        # Hoàn tác di chuyển chính
        self._end_square.remove_piece()
        self._start_square.place_piece(self._piece)
        self._piece.position = self._start_square

        # Khôi phục quân bị bắt
        if self._captured_piece:
            if self.is_en_passant:
                captured_square = board.get_square(
                    self._start_square.row,
                    self._end_square.col
                )
                captured_square.place_piece(self._captured_piece)
            else:
                self._end_square.place_piece(self._captured_piece)
            board.add_piece(self._captured_piece)

        # Hoàn tác nhập thành
        if self.is_castle:
            rook_start_col = 7 if self._end_square.col > self._start_square.col else 0
            rook_end_col = 5 if self._end_square.col > self._start_square.col else 3
            
            rook_end = board.get_square(self._start_square.row, rook_end_col)
            rook_start = board.get_square(self._start_square.row, rook_start_col)
            rook = rook_end.piece

            if rook:
                rook_end.remove_piece()
                rook_start.place_piece(rook)
                rook.position = rook_start

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        move_type = ""
        if self.is_castle:
            move_type = " (castle)"
        elif self.is_en_passant:
            move_type = " (en passant)"
        elif self.is_promotion:
            move_type = f" (promotion to {self.promotion_piece_type.value})"
        
        return f"{self._piece} {self._start_square}->{self._end_square}{move_type}"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"Move(start={self._start_square}, end={self._end_square}, "
                f"piece={self._piece}, type={self._move_type})")