from typing import List
from piece import Piece
from move import Move
from board import Board
from core.pieces.piece import PieceType, PieceColor
from square import Square

class Knight(Piece):
    """
    Class Knight kế thừa từ Piece, đại diện cho quân mã trong cờ vua
    Quân mã di chuyển theo hình chữ L: 2 ô theo một hướng và 1 ô theo hướng vuông góc
    """
    def __init__(self, color: PieceColor, square: Square):
        """
        Khởi tạo quân mã
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân mã đang đứng
        """
        super().__init__(color, square)
        self._piece_type = PieceType.KNIGHT
        # Các hướng di chuyển hình chữ L của mã
        self._moves = [
            (-2, -1), (-2, 1),  # Lên 2 trái/phải 1
            (2, -1), (2, 1),    # Xuống 2 trái/phải 1
            (-1, -2), (1, -2),  # Trái 2 lên/xuống 1
            (-1, 2), (1, 2)     # Phải 2 lên/xuống 1
        ]

    @property
    def piece_type(self) -> PieceType:
        """Lấy loại quân cờ"""
        return self._piece_type

    def get_legal_moves(self, board: Board) -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân mã
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Kiểm tra từng nước đi theo hình chữ L
        for move_row, move_col in self._moves:
            next_row = row + move_row
            next_col = col + move_col
            
            # Kiểm tra vị trí mới có hợp lệ không
            if board.is_valid_position(next_row, next_col):
                target_square = board.get_square(next_row, next_col)
                target_piece = target_square.piece

                # Nếu ô trống hoặc có quân địch
                if target_piece is None:
                    legal_moves.append(Move(current_square, target_square))
                elif target_piece.color != self.color:
                    legal_moves.append(Move(current_square, target_square, target_piece))

        return legal_moves

    def is_l_shape_move(self, move: Move) -> bool:
        """
        Kiểm tra xem một nước đi có phải là nước đi hình chữ L hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu là nước đi hình chữ L hợp lệ, False nếu không
        """
        row_diff = abs(move.end_square.row - move.start_square.row)
        col_diff = abs(move.end_square.col - move.start_square.col)
        
        # Kiểm tra di chuyển hình chữ L (2-1 hoặc 1-2)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def clone(self) -> 'Knight':
        """
        Tạo bản sao của quân mã
        Returns:
            Bản sao của quân mã hiện tại
        """
        return Knight(self.color, self.square)

    def get_piece_value(self) -> int:
        """
        Lấy giá trị của quân mã cho việc tính điểm
        Returns:
            Giá trị quân mã
        """
        return 3

    def __str__(self) -> str:
        """String representation của quân mã"""
        color_name = "White" if self.color == PieceColor.WHITE else "Black"
        return f"{color_name} Knight at {self.square}"

    def get_symbol(self) -> str:
        """
        Lấy ký hiệu của quân mã để hiển thị
        Returns:
            'N' cho mã trắng, 'n' cho mã đen
        """
        return 'N' if self.color == PieceColor.WHITE else 'n'

    def can_reach_square(self, target_square: Square, board: Board) -> bool:
        """
        Kiểm tra xem quân mã có thể đi đến ô đích không
        Args:
            target_square: Ô đích cần kiểm tra
            board: Bàn cờ hiện tại
        Returns:
            True nếu có thể đi đến, False nếu không
        """
        move = Move(self.square, target_square)
        return self.is_l_shape_move(move)