# square.py
from typing import Optional, TYPE_CHECKING, Tuple, List, Dict
import logging

if TYPE_CHECKING:
    from .pieces.piece import Piece, PieceColor
    from .board import Board

logger = logging.getLogger(__name__)

class Square:
    """Class đại diện cho một ô trên bàn cờ"""
    
    def __init__(self, row: int, col: int):
        """Khởi tạo một ô với tọa độ xác định"""
        if not self._is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
            
        self._row = row
        self._col = col
        self._piece: Optional['Piece'] = None
        self._board: Optional['Board'] = None
        self._attacked_by: Dict[str, List['Piece']] = {
            'WHITE': [],
            'BLACK': []
        }

    @staticmethod
    def _is_valid_position(row: int, col: int) -> bool:
        """Kiểm tra tọa độ có hợp lệ không"""
        return 0 <= row < 8 and 0 <= col < 8

    # Core Properties
    @property
    def row(self) -> int:
        """Chỉ số hàng (0-7)"""
        return self._row

    @property
    def col(self) -> int:
        """Chỉ số cột (0-7)"""
        return self._col

    @property
    def piece(self) -> Optional['Piece']:
        """Quân cờ đang ở trên ô"""
        return self._piece

    @property
    def position(self) -> Tuple[int, int]:
        """Vị trí dạng tuple (row, col)"""
        return (self._row, self._col)

    @property
    def algebraic(self) -> str:
        """Ký hiệu đại số (vd: 'e4')"""
        col_letter = chr(ord('a') + self._col)
        row_number = 8 - self._row
        return f"{col_letter}{row_number}"

    @property
    def board(self) -> Optional['Board']:
        """Bàn cờ chứa ô này"""
        return self._board

    @board.setter
    def board(self, board: 'Board') -> None:
        """Set bàn cờ chứa ô này"""
        self._board = board

    # Piece Management
    def place_piece(self, piece: Optional['Piece']) -> None:
        """Đặt quân cờ lên ô"""
        try:
            if piece:
                if self.is_occupied():
                    logger.warning(f"Square {self} already occupied, removing existing piece")
                    self.remove_piece()
                
                self._piece = piece
                piece.position = self
                self._update_attack_lines()
                logger.debug(f"Placed {piece} on {self}")
            else:
                self.remove_piece()
        except Exception as e:
            logger.error(f"Error placing piece on {self}: {e}")
            raise

    def remove_piece(self) -> Optional['Piece']:
        """Lấy quân cờ ra khỏi ô"""
        piece = self._piece
        if piece:
            self._piece = None
            piece.position = None
            self._update_attack_lines()
            logger.debug(f"Removed {piece} from {self}")
        return piece

    # State Checks
    def is_empty(self) -> bool:
        """Kiểm tra ô có trống không"""
        return self._piece is None

    def is_occupied(self) -> bool:
        """Kiểm tra ô có quân không"""
        return not self.is_empty()

    def has_enemy_piece(self, color: 'PieceColor') -> bool:
        """Kiểm tra ô có quân địch không"""
        return self.is_occupied() and self._piece.color != color

    def has_friendly_piece(self, color: 'PieceColor') -> bool:
        """Kiểm tra ô có quân cùng màu không"""
        return self.is_occupied() and self._piece.color == color

    # Attack Lines Management
    def _update_attack_lines(self) -> None:
        """Cập nhật các đường tấn công qua ô này"""
        if not self._board:
            return

        # Reset attack lines
        self._attacked_by = {
            'WHITE': [],
            'BLACK': []
        }

        # Update attack lines for all pieces that can attack this square
        for piece in self._board.get_all_pieces():
            if self in piece.get_attacked_squares():
                self._attacked_by[piece.color].append(piece)

    def is_attacked_by(self, color: 'PieceColor') -> bool:
        """Kiểm tra ô có bị tấn công bởi màu này không"""
        return len(self._attacked_by[color]) > 0

    def get_attackers(self, color: Optional['PieceColor'] = None) -> List['Piece']:
        """Lấy danh sách quân đang tấn công ô này"""
        if color:
            return self._attacked_by[color]
        return self._attacked_by['WHITE'] + self._attacked_by['BLACK']

    # Board Position Analysis
    def is_center(self) -> bool:
        """Kiểm tra ô có ở trung tâm không (e4,e5,d4,d5)"""
        return 3 <= self._row <= 4 and 3 <= self._col <= 4

    def is_edge(self) -> bool:
        """Kiểm tra ô có ở biên không"""
        return (self._row in (0, 7) or self._col in (0, 7))

    def get_adjacent_squares(self) -> List['Square']:
        """Lấy danh sách các ô liền kề"""
        if not self._board:
            return []

        adjacent = []
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0), 
                       (1,1), (1,-1), (-1,1), (-1,-1)]:
            new_row, new_col = self._row + dr, self._col + dc
            if self._is_valid_position(new_row, new_col):
                adjacent.append(self._board.get_square(new_row, new_col))
        return adjacent

    # Magic Methods
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Square):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        return hash((self._row, self._col))

    def __str__(self) -> str:
        piece_str = f"[{self._piece}]" if self._piece else "[ ]"
        return f"{self.algebraic}{piece_str}"

    def __repr__(self) -> str:
        return (f"Square(pos={self.algebraic}, "
                f"piece={self._piece}, "
                f"attacked_by={len(self.get_attackers())} pieces)")