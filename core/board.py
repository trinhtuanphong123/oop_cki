# core/board.py

from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from .pieces.piece import Piece, PieceColor, PieceType

if TYPE_CHECKING:
    from .square import Square
    from .move import Move, MoveType
    from .pieces.king import King

class Board:
    """
    Class đại diện cho bàn cờ và quản lý trạng thái game.
    - Quản lý vị trí các quân cờ
    - Xử lý các nước đi đặc biệt
    - Lưu trữ lịch sử nước đi
    """

    def __init__(self):
        """Khởi tạo bàn cờ trống"""
        self._initialize_board()
        self._move_history: List['Move'] = []
        self._captured_pieces: List[Piece] = []

    def _initialize_board(self) -> None:
        """Khởi tạo bàn cờ và danh sách quân"""
        from .square import Square
        
        # Khởi tạo bàn cờ
        self._squares: List[List['Square']] = [
            [Square(row, col) for col in range(8)]
            for row in range(8)
        ]

        # Khởi tạo danh sách quân
        self._pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }

    def is_valid_position(self, row: int, col: int) -> bool:
        """Kiểm tra vị trí có nằm trong bàn cờ"""
        return 0 <= row < 8 and 0 <= col < 8

    def get_square(self, row: int, col: int) -> 'Square':
        """Lấy ô tại vị trí cụ thể"""
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return self._squares[row][col]

    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        """Lấy quân cờ tại vị trí"""
        return self.get_square(row, col).piece

    def get_pieces(self, color: PieceColor) -> List[Piece]:
        """Lấy danh sách quân cờ theo màu"""
        return self._pieces[color].copy()

    def place_piece(self, piece: Piece, square: 'Square') -> None:
        """Đặt quân cờ lên ô"""
        if square.piece:
            self.remove_piece(square.piece)
        
        square.piece = piece
        piece.position = square
        
        if piece not in self._pieces[piece.color]:
            self._pieces[piece.color].append(piece)

    def remove_piece(self, piece: Piece) -> None:
        """Lấy quân cờ ra khỏi bàn cờ"""
        if piece in self._pieces[piece.color]:
            self._pieces[piece.color].remove(piece)
        if piece.position:
            piece.position.piece = None

    def execute_move(self, move: 'Move') -> bool:
        """
        Thực hiện một nước đi
        Args:
            move: Nước đi cần thực hiện
        Returns:
            bool: True nếu thực hiện thành công
        """
        # Xử lý quân bị bắt
        if move.move_type.is_capture:
            captured_piece = move.captured_piece
            if captured_piece:
                self.remove_piece(captured_piece)
                self._captured_pieces.append(captured_piece)

        # Di chuyển quân cờ
        piece = move.moving_piece
        self.remove_piece(piece)
        self.place_piece(piece, move.end_square)

        # Xử lý các trường hợp đặc biệt
        if move.move_type.is_castle:
            self._handle_castling(move)
        elif move.move_type.is_en_passant:
            self._handle_en_passant(move)
        elif move.move_type.is_promotion:
            self._handle_promotion(move)

        # Lưu lịch sử
        self._move_history.append(move)
        return True

    def undo_last_move(self) -> Optional['Move']:
        """
        Hoàn tác nước đi cuối cùng
        Returns:
            Move hoặc None nếu không có nước đi nào
        """
        if not self._move_history:
            return None

        move = self._move_history.pop()
        piece = move.moving_piece

        # Hoàn tác di chuyển chính
        self.remove_piece(piece)
        self.place_piece(piece, move.start_square)

        # Hoàn tác bắt quân
        if move.move_type.is_capture and self._captured_pieces:
            captured_piece = self._captured_pieces.pop()
            if move.move_type.is_en_passant:
                # Với bắt tốt qua đường, đặt lại tốt bị bắt
                capture_square = self.get_square(
                    move.start_square.row,
                    move.end_square.col
                )
                self.place_piece(captured_piece, capture_square)
            else:
                self.place_piece(captured_piece, move.end_square)

        # Hoàn tác nhập thành
        if move.move_type.is_castle:
            self._undo_castling(move)

        return move

    def _handle_castling(self, move: 'Move') -> None:
        """
        Xử lý nhập thành
        - Nhập thành ngắn: Vua đi sang phải 2 ô, xe đi sang trái 2 ô
        - Nhập thành dài: Vua đi sang trái 2 ô, xe đi sang phải 3 ô
        """
        row = move.start_square.row
        is_kingside = move.end_square.col > move.start_square.col
        
        # Xác định vị trí cũ và mới của xe
        old_rook_col = 7 if is_kingside else 0
        new_rook_col = 5 if is_kingside else 3
        
        # Di chuyển xe
        rook = self.get_piece_at(row, old_rook_col)
        if rook:
            self.remove_piece(rook)
            self.place_piece(rook, self.get_square(row, new_rook_col))

    def _handle_en_passant(self, move: 'Move') -> None:
        """
        Xử lý bắt tốt qua đường
        - Tốt bị bắt nằm cùng hàng với tốt bắt
        - Tốt bắt di chuyển chéo sang ô trống
        """
        captured_square = self.get_square(
            move.start_square.row,
            move.end_square.col
        )
        captured_pawn = captured_square.piece
        if captured_pawn:
            self.remove_piece(captured_pawn)
            self._captured_pieces.append(captured_pawn)

    def _handle_promotion(self, move: 'Move') -> None:
        """
        Xử lý phong cấp
        - Tạo quân mới theo loại được chọn
        - Thay thế tốt bằng quân mới
        """
        if not move.move_type.promotion_piece_type:
            return

        # Import các class quân cờ cần thiết
        from .pieces.queen import Queen
        from .pieces.rook import Rook
        from .pieces.bishop import Bishop
        from .pieces.knight import Knight

        # Dictionary ánh xạ loại quân với class
        piece_classes = {
            PieceType.QUEEN: Queen,
            PieceType.ROOK: Rook,
            PieceType.BISHOP: Bishop,
            PieceType.KNIGHT: Knight
        }

        piece_class = piece_classes.get(move.move_type.promotion_piece_type)
        if piece_class:
            new_piece = piece_class(move.moving_piece.color, move.end_square)
            self.remove_piece(move.moving_piece)
            self.place_piece(new_piece, move.end_square)

    def __str__(self) -> str:
        """Hiển thị bàn cờ dạng text"""
        board_str = "  a b c d e f g h\n"
        for row in range(8):
            board_str += f"{8-row} "
            for col in range(8):
                piece = self.get_piece_at(row, col)
                board_str += f"{piece.symbol if piece else '.'} "
            board_str += f"{8-row}\n"
        board_str += "  a b c d e f g h"
        return board_str