from typing import List, Optional, Dict, Tuple, Set, TYPE_CHECKING
from collections import defaultdict
from .square import Square
from core.pieces.piece import Piece, PieceColor, PieceType
from .move import Move, MoveType

if TYPE_CHECKING:
    from core.game_rule import GameRule
    from .pieces.king import King
    from .pieces.pawn import Pawn

class Board:
    """
    Class đại diện cho bàn cờ vua.
    Quản lý trạng thái bàn cờ, quân cờ và tương tác với luật chơi.
    """
    DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self):
        """Khởi tạo bàn cờ với trạng thái ban đầu"""
        # Cấu trúc dữ liệu cơ bản
        self._squares: List[List[Square]] = []
        self._pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }
        self._kings: Dict[PieceColor, 'King'] = {}
        
        # Lịch sử và theo dõi trạng thái
        self._move_history: List[Move] = []
        self._captured_pieces: List[Piece] = []
        self._position_history: Set[str] = set()
        
        # Trạng thái đặc biệt
        self._en_passant_square: Optional[Square] = None
        self._halfmove_clock: int = 0
        self._fullmove_number: int = 1
        
        # Luật chơi và validation
        self._game_rules: Optional['GameRule'] = None
        
        self._initialize_board()

    def _initialize_board(self) -> None:
        """Khởi tạo ma trận các ô trên bàn cờ"""
        self._squares = [[Square(row, col) for col in range(8)] 
                        for row in range(8)]

    # Properties và Getters
    @property
    def squares(self) -> List[List[Square]]:
        """Ma trận các ô trên bàn cờ"""
        return self._squares

    @property
    def move_history(self) -> List[Move]:
        """Lịch sử các nước đi"""
        return self._move_history.copy()

    @property
    def captured_pieces(self) -> List[Piece]:
        """Danh sách quân bị bắt"""
        return self._captured_pieces.copy()

    @property
    def en_passant_square(self) -> Optional[Square]:
        """Ô có thể bắt tốt qua đường"""
        return self._en_passant_square

    @property
    def halfmove_clock(self) -> int:
        """Số nước đi từ lần cuối bắt quân hoặc di chuyển tốt"""
        return self._halfmove_clock

    @property
    def fullmove_number(self) -> int:
        """Số lượt đi đầy đủ"""
        return self._fullmove_number

    # Phương thức truy cập và quản lý bàn cờ
    def get_square(self, row: int, col: int) -> Square:
        """
        Lấy ô tại vị trí chỉ định.
        
        Args:
            row: Số hàng (0-7)
            col: Số cột (0-7)
            
        Returns:
            Square: Ô tại vị trí chỉ định
            
        Raises:
            ValueError: Nếu vị trí không hợp lệ
        """
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return self._squares[row][col]

    def get_square_from_algebraic(self, notation: str) -> Square:
        """
        Lấy ô từ ký hiệu đại số (ví dụ: 'e4').
        
        Args:
            notation: Ký hiệu đại số của ô
            
        Returns:
            Square: Ô tương ứng
        """
        if len(notation) != 2:
            raise ValueError(f"Invalid algebraic notation: {notation}")
        
        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])
        
        return self.get_square(row, col)

    # Quản lý quân cờ
    def place_piece(self, piece: Piece, square: Square) -> None:
        """
        Đặt quân cờ lên ô chỉ định.
        
        Args:
            piece: Quân cờ cần đặt
            square: Ô đích
        """
        if square.is_occupied():
            raise ValueError(f"Square {square} is already occupied")
        
        square.place_piece(piece)
        self._pieces[piece.color].append(piece)
        
        if piece.piece_type == PieceType.KING:
            self._kings[piece.color] = piece

    def remove_piece(self, square: Square) -> Optional[Piece]:
        """
        Lấy quân cờ ra khỏi ô.
        
        Args:
            square: Ô cần lấy quân
            
        Returns:
            Optional[Piece]: Quân cờ đã lấy ra
        """
        piece = square.remove_piece()
        if piece:
            self._pieces[piece.color].remove(piece)
            if piece.piece_type == PieceType.KING:
                del self._kings[piece.color]
        return piece

    # Xử lý nước đi
    def make_move(self, move: Move) -> None:
        """
        Thực hiện nước đi trên bàn cờ.
        
        Args:
            move: Nước đi cần thực hiện
        """
        # Cập nhật trạng thái
        self._update_game_state(move)
        
        # Xử lý các loại nước đi đặc biệt
        if move.move_type == MoveType.CASTLE:
            self._handle_castling(move)
        elif move.move_type == MoveType.EN_PASSANT:
            self._handle_en_passant(move)
        elif move.move_type == MoveType.PROMOTION:
            self._handle_promotion(move)
        else:
            self._handle_normal_move(move)
        
        # Lưu lịch sử
        self._move_history.append(move)
        self._position_history.add(self._get_position_key())

    def undo_move(self) -> Optional[Move]:
        """
        Hoàn tác nước đi cuối cùng.
        
        Returns:
            Optional[Move]: Nước đi đã hoàn tác
        """
        if not self._move_history:
            return None
            
        move = self._move_history.pop()
        self._restore_position(move)
        return move

    # Kiểm tra trạng thái
    def is_check(self, color: PieceColor) -> bool:
        """
        Kiểm tra vua có đang bị chiếu không.
        
        Args:
            color: Màu cần kiểm tra
            
        Returns:
            bool: True nếu vua đang bị chiếu
        """
        king = self._kings.get(color)
        if not king:
            return False
            
        opponent_color = (PieceColor.BLACK 
                         if color == PieceColor.WHITE 
                         else PieceColor.WHITE)
        
        for piece in self._pieces[opponent_color]:
            if king.position in piece.get_attack_squares(self):
                return True
        return False

    def is_checkmate(self, color: PieceColor) -> bool:
        """
        Kiểm tra có phải chiếu hết không.
        
        Args:
            color: Màu cần kiểm tra
            
        Returns:
            bool: True nếu là chiếu hết
        """
        if not self.is_check(color):
            return False
            
        return not self._has_legal_moves(color)

    def is_stalemate(self, color: PieceColor) -> bool:
        """
        Kiểm tra có phải hết cờ không.
        
        Args:
            color: Màu cần kiểm tra
            
        Returns:
            bool: True nếu là hết cờ
        """
        if self.is_check(color):
            return False
            
        return not self._has_legal_moves(color)

    # Tiện ích
    def get_fen(self) -> str:
        """
        Tạo chuỗi FEN từ trạng thái bàn cờ hiện tại.
        
        Returns:
            str: Chuỗi FEN
        """
        # Implementation
        pass

    def clone(self) -> 'Board':
        """
        Tạo bản sao của bàn cờ.
        
        Returns:
            Board: Bản sao của bàn cờ
        """
        # Implementation
        pass

    # Private helper methods
    def _update_game_state(self, move: Move) -> None:
        """Cập nhật trạng thái game sau mỗi nước đi"""
        pass

    def _handle_castling(self, move: Move) -> None:
        """Xử lý nước nhập thành"""
        pass

    def _handle_en_passant(self, move: Move) -> None:
        """Xử lý nước bắt tốt qua đường"""
        pass

    def _handle_promotion(self, move: Move) -> None:
        """Xử lý nước phong cấp"""
        pass

    def _handle_normal_move(self, move: Move) -> None:
        """Xử lý nước đi thông thường"""
        pass

    def _get_position_key(self) -> str:
        """Tạo khóa duy nhất cho trạng thái bàn cờ"""
        pass

    def _has_legal_moves(self, color: PieceColor) -> bool:
        """Kiểm tra còn nước đi hợp lệ không"""
        pass