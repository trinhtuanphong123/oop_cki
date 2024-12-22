from typing import List
from piece import Piece
from move import Move
from board import Board
from core.pieces.piece import PieceType, PieceColor
from square import Square

class Bishop(Piece):
    """
    Class Bishop kế thừa từ Piece, đại diện cho quân tượng trong cờ vua
    Quân tượng di chuyển theo đường chéo, không giới hạn số ô
    """
    def __init__(self, color: PieceColor, square: Square):
        """
        Khởi tạo quân tượng
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân tượng đang đứng
        """
        super().__init__(color, square)
        self._piece_type = PieceType.BISHOP
        # Các hướng di chuyển chéo
        self._directions = [
            (-1, -1),  # Chéo trên trái
            (-1, 1),   # Chéo trên phải
            (1, -1),   # Chéo dưới trái
            (1, 1)     # Chéo dưới phải
        ]

    @property
    def piece_type(self) -> PieceType:
        """Lấy loại quân cờ"""
        return self._piece_type

    def get_legal_moves(self, board: Board) -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân tượng
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Kiểm tra từng hướng chéo
        for dir_row, dir_col in self._directions:
            next_row, next_col = row + dir_row, col + dir_col
            
            # Tiếp tục di chuyển theo hướng cho đến khi gặp chướng ngại
            while board.is_valid_position(next_row, next_col):
                target_square = board.get_square(next_row, next_col)
                target_piece = target_square.piece

                # Nếu ô trống
                if target_piece is None:
                    legal_moves.append(Move(current_square, target_square))
                
                # Nếu gặp quân địch
                elif target_piece.color != self.color:
                    legal_moves.append(Move(current_square, target_square, target_piece))
                    break
                
                # Nếu gặp quân cùng màu
                else:
                    break

                next_row += dir_row
                next_col += dir_col

        return legal_moves

    def clone(self) -> 'Bishop':
        """
        Tạo bản sao của quân tượng
        Returns:
            Bản sao của quân tượng hiện tại
        """
        return Bishop(self.color, self.square)

    def get_piece_value(self) -> int:
        """
        Lấy giá trị của quân tượng cho việc tính điểm
        Returns:
            Giá trị quân tượng
        """
        return 3

    def __str__(self) -> str:
        """String representation của quân tượng"""
        color_name = "White" if self.color == PieceColor.WHITE else "Black"
        return f"{color_name} Bishop at {self.square}"

    def get_symbol(self) -> str:
        """
        Lấy ký hiệu của quân tượng để hiển thị
        Returns:
            'B' cho tượng trắng, 'b' cho tượng đen
        """
        return 'B' if self.color == PieceColor.WHITE else 'b'