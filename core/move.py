# move.py
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Tuple
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .square import Square
    from .pieces.piece import Piece, PieceType
    from .pieces.pawn import Pawn
    from .pieces.king import King
    from .board import Board

@dataclass
class MoveType:
    """Value Object chứa thông tin về loại nước đi"""
    is_capture: bool = False
    is_castle: bool = False
    is_en_passant: bool = False
    is_promotion: bool = False
    promotion_piece_type: Optional['PieceType'] = None

    def __str__(self) -> str:
        types = []
        if self.is_capture: types.append("capture")
        if self.is_castle: types.append("castle")
        if self.is_en_passant: types.append("en passant")
        if self.is_promotion: types.append(f"promotion to {self.promotion_piece_type.value}")
        return f"[{' + '.join(types)}]" if types else "[normal]"

class Move:
    """Class đại diện cho một nước đi trong game"""
    
    def __init__(self, 
                 start_square: 'Square',
                 end_square: 'Square',
                 piece: 'Piece',
                 move_type: Optional[MoveType] = None):
        """Khởi tạo nước đi"""
        self._start_square = start_square
        self._end_square = end_square
        self._piece = piece
        self._move_type = move_type or MoveType()
        self._captured_piece: Optional['Piece'] = end_square.piece
        
        # Các thuộc tính bổ sung
        self._original_position: Tuple[int, int] = (start_square.row, start_square.col)
        self._target_position: Tuple[int, int] = (end_square.row, end_square.col)
        self._is_first_move = not piece.has_moved
        self._verify_move_type()

    def _verify_move_type(self) -> None:
        """Xác minh và cập nhật loại nước đi"""
        # Kiểm tra capture
        if self._captured_piece is not None:
            self._move_type.is_capture = True

        # Kiểm tra castling
        if isinstance(self._piece, 'King'):
            col_diff = abs(self._end_square.col - self._start_square.col)
            if col_diff == 2:
                self._move_type.is_castle = True

        # Kiểm tra en passant
        if isinstance(self._piece, 'Pawn'):
            if (abs(self._end_square.col - self._start_square.col) == 1 and
                not self._captured_piece):
                self._move_type.is_en_passant = True

        # Kiểm tra promotion
        if (isinstance(self._piece, 'Pawn') and 
            self._end_square.row in (0, 7)):
            self._move_type.is_promotion = True

    @property
    def original_position(self) -> Tuple[int, int]:
        """Vị trí ban đầu (row, col)"""
        return self._original_position

    @property
    def target_position(self) -> Tuple[int, int]:
        """Vị trí đích (row, col)"""
        return self._target_position

    @property
    def is_first_move(self) -> bool:
        """Có phải là nước đi đầu tiên của quân này không"""
        return self._is_first_move

    def execute(self, board: 'Board') -> bool:
        """Thực hiện nước đi trên bàn cờ"""
        try:
            logger.debug(f"Executing move: {self}")

            if self.is_castle:
                return self._execute_castle(board)
            elif self.is_en_passant:
                return self._execute_en_passant(board)
            elif self.is_promotion:
                return self._execute_promotion(board)
            else:
                return self._execute_normal_move(board)

        except Exception as e:
            logger.error(f"Failed to execute move: {e}")
            return False

    def _execute_normal_move(self, board: 'Board') -> bool:
        """Thực hiện nước đi thông thường"""
        try:
            # Capture handling
            if self._captured_piece:
                board.remove_piece(self._captured_piece)
                logger.debug(f"Captured piece: {self._captured_piece}")

            # Move piece
            self._start_square.remove_piece()
            self._end_square.place_piece(self._piece)
            self._piece.position = self._end_square
            self._piece.has_moved = True

            logger.debug(f"Completed normal move: {self._piece} to {self._end_square}")
            return True

        except Exception as e:
            logger.error(f"Error in normal move execution: {e}")
            return False

    def _execute_castle(self, board: 'Board') -> bool:
        """Thực hiện nước nhập thành"""
        try:
            king = self._piece
            if not isinstance(king, 'King'):
                raise ValueError("Castling must be performed with a king")

            # Determine rook positions
            is_kingside = self._end_square.col > self._start_square.col
            rook_start_col = 7 if is_kingside else 0
            rook_end_col = 5 if is_kingside else 3

            # Get rook
            rook_start = board.get_square(self._start_square.row, rook_start_col)
            rook = rook_start.piece
            if not rook:
                raise ValueError("No rook found for castling")

            # Move king
            if not self._execute_normal_move(board):
                return False

            # Move rook
            rook_end = board.get_square(self._start_square.row, rook_end_col)
            rook_start.remove_piece()
            rook_end.place_piece(rook)
            rook.position = rook_end
            rook.has_moved = True

            logger.debug(f"Completed castling: {self}")
            return True

        except Exception as e:
            logger.error(f"Error in castling execution: {e}")
            return False

    def _execute_en_passant(self, board: 'Board') -> bool:
        """Thực hiện bắt tốt qua đường"""
        try:
            # Remove captured pawn
            captured_square = board.get_square(
                self._start_square.row,
                self._end_square.col
            )
            captured_pawn = captured_square.piece
            if captured_pawn:
                board.remove_piece(captured_pawn)
                captured_square.remove_piece()
                self._captured_piece = captured_pawn

            # Move attacking pawn
            return self._execute_normal_move(board)

        except Exception as e:
            logger.error(f"Error in en passant execution: {e}")
            return False

    def _execute_promotion(self, board: 'Board') -> bool:
        """Thực hiện phong cấp"""
        try:
            if not self.promotion_piece_type:
                raise ValueError("Promotion piece type must be specified")

            # Move pawn
            if not self._execute_normal_move(board):
                return False

            # Create and place new piece
            from .pieces.piece import create_piece
            new_piece = create_piece(
                self.promotion_piece_type,
                self._piece.color,
                self._end_square
            )
            self._end_square.place_piece(new_piece)
            board.remove_piece(self._piece)

            logger.debug(f"Completed promotion: {self}")
            return True

        except Exception as e:
            logger.error(f"Error in promotion execution: {e}")
            return False

    def to_algebraic_notation(self) -> str:
        """Chuyển nước đi sang ký hiệu đại số"""
        notation = ""
        
        # Piece symbol
        if self._piece.piece_type.value != 'P':
            notation += self._piece.piece_type.value.upper()
            
        # Start position
        notation += chr(self._start_square.col + 97)  # a-h
        notation += str(8 - self._start_square.row)   # 1-8
        
        # Capture symbol
        if self.is_capture:
            notation += 'x'
            
        # End position
        notation += chr(self._end_square.col + 97)
        notation += str(8 - self._end_square.row)
        
        # Special moves
        if self.is_castle:
            notation = "O-O" if self._end_square.col == 6 else "O-O-O"
        elif self.is_promotion:
            notation += f"={self.promotion_piece_type.value.upper()}"
            
        return notation

    def __eq__(self, other: object) -> bool:
        """Kiểm tra hai nước đi có giống nhau không"""
        if not isinstance(other, Move):
            return NotImplemented
        return (self._start_square == other._start_square and
                self._end_square == other._end_square and
                self._piece == other._piece and
                self._move_type == other._move_type)

    def __hash__(self) -> int:
        """Hash value cho move"""
        return hash((self._start_square, self._end_square, 
                    self._piece, str(self._move_type)))