# board.py

from typing import List, Optional, Dict, Tuple
from core.pieces.piece import Piece, PieceColor, PieceType 
from .square import Square
from .move import Move
from .pieces.king import King
from .pieces.pawn import Pawn

class Board:
    """
    Class đại diện cho bàn cờ.
    Quản lý:
    - Các ô trên bàn cờ
    - Vị trí các quân cờ
    - Xử lý các nước đi
    - Lưu trữ lịch sử
    """

    def __init__(self):
        """Khởi tạo bàn cờ mới"""
        # Khởi tạo ma trận ô cờ
        self._squares: List[List[Square]] = [
            [Square(row, col) for col in range(8)]
            for row in range(8)
        ]

        # Quản lý quân cờ theo màu
        self._pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }

        # Lịch sử và trạng thái
        self._move_history: List[Move] = []
        self._captured_pieces: List[Piece] = []

    # Phương thức truy cập
    def get_square(self, row: int, col: int) -> Square:
        """Lấy ô tại vị trí chỉ định"""
        if not self._is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return self._squares[row][col]

    def get_pieces(self, color: PieceColor) -> List[Piece]:
        """Lấy danh sách quân cờ theo màu"""
        return self._pieces[color].copy()

    def get_king(self, color: PieceColor) -> Optional[King]:
        """Lấy vua của một bên"""
        for piece in self._pieces[color]:
            if isinstance(piece, King):
                return piece
        return None

    # Phương thức thao tác với quân cờ
    def add_piece(self, piece: Piece, square: Square) -> None:
        """
        Thêm quân cờ vào bàn cờ
        Args:
            piece: Quân cờ cần thêm
            square: Ô cần đặt quân
        """
        if square.is_occupied():
            raise ValueError(f"Square {square} is already occupied")

        # Cập nhật vị trí
        square.piece = piece
        piece.position = square
        
        # Thêm vào danh sách
        self._pieces[piece.color].append(piece)

    def remove_piece(self, piece: Piece) -> None:
        """
        Xóa quân cờ khỏi bàn cờ
        Args:
            piece: Quân cờ cần xóa
        """
        if piece in self._pieces[piece.color]:
            self._pieces[piece.color].remove(piece)
            piece.position.piece = None

    # Phương thức xử lý nước đi
    def make_move(self, move: Move) -> bool:
        """
        Thực hiện nước đi
        Args:
            move: Nước đi cần thực hiện
        Returns:
            True nếu thực hiện thành công
        """
        if not self._validate_move(move):
            return False

        # Xử lý bắt quân
        if move.is_capture:
            captured = move.end_square.piece
            self.remove_piece(captured)
            self._captured_pieces.append(captured)

        # Di chuyển quân
        piece = move.start_square.piece
        self.remove_piece(piece)
        self.add_piece(piece, move.end_square)

        # Xử lý các trường hợp đặc biệt
        if move.is_castle:
            self._handle_castling(move)
        elif move.is_en_passant:
            self._handle_en_passant(move)
        elif move.is_promotion:
            self._handle_promotion(move)

        # Lưu lịch sử
        self._move_history.append(move)
        return True

    def undo_move(self) -> Optional[Move]:
        """
        Hoàn tác nước đi cuối cùng
        Returns:
            Nước đi đã hoàn tác hoặc None
        """
        if not self._move_history:
            return None

        last_move = self._move_history.pop()
        piece = last_move.end_square.piece

        # Hoàn tác di chuyển
        self.remove_piece(piece)
        self.add_piece(piece, last_move.start_square)

        # Hoàn tác bắt quân
        if last_move.is_capture:
            captured = self._captured_pieces.pop()
            self.add_piece(captured, last_move.end_square)

        # Hoàn tác trường hợp đặc biệt
        if last_move.is_castle:
            self._undo_castling(last_move)
        elif last_move.is_en_passant:
            self._undo_en_passant(last_move)

        return last_move

    # Phương thức hỗ trợ
    def _validate_move(self, move: Move) -> bool:
        """Kiểm tra nước đi có hợp lệ"""
        if not move.start_square.is_occupied():
            return False
        
        piece = move.start_square.piece
        if not piece.can_move_to(move.end_square, self):
            return False

        return True

    def _is_valid_position(self, row: int, col: int) -> bool:
        """Kiểm tra vị trí có hợp lệ"""
        return 0 <= row < 8 and 0 <= col < 8

    def _handle_castling(self, move: Move) -> None:
        """Xử lý nhập thành"""
        row = move.start_square.row
        old_rook_col = 7 if move.end_square.col > move.start_square.col else 0
        new_rook_col = 5 if move.end_square.col > move.start_square.col else 3

        # Di chuyển xe
        rook = self.get_square(row, old_rook_col).piece
        self.remove_piece(rook)
        self.add_piece(rook, self.get_square(row, new_rook_col))

    def _handle_en_passant(self, move: Move) -> None:
        """Xử lý bắt tốt qua đường"""
        captured_row = move.start_square.row
        captured_col = move.end_square.col
        captured = self.get_square(captured_row, captured_col).piece
        
        self.remove_piece(captured)
        self._captured_pieces.append(captured)

    def _handle_promotion(self, move: Move) -> None:
        """Xử lý phong cấp"""
        if move.promotion_piece_type:
            # Tạo quân mới và thay thế
            new_piece = move.promotion_piece_type(
                move.moving_piece.color,
                move.end_square
            )
            self.remove_piece(move.moving_piece)
            self.add_piece(new_piece, move.end_square)

    def __str__(self) -> str:
        """Hiển thị bàn cờ dạng text"""
        board_str = ""
        for row in range(8):
            for col in range(8):
                square = self._squares[row][col]
                piece = square.piece
                board_str += f"{piece if piece else '.'} "
            board_str += "\n"
        return board_str