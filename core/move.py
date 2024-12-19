from core.pieces.piece import Piece
from .square import Square
class Move:
    """
    Lớp đại diện cho một nước đi trong trò chơi cờ vua.
    """
    def __init__(self, start_square: 'Square', end_square: 'Square', piece: 'Piece'):
        """
        Khởi tạo nước đi với ô xuất phát, ô kết thúc và quân cờ thực hiện nước đi.
        
        Args:
            start_square (Square): Ô xuất phát.
            end_square (Square): Ô kết thúc.
            piece (Piece): Quân cờ thực hiện nước đi.
        """
        self.start_square = start_square
        self.end_square = end_square
        self.piece = piece

    def execute(self):
        """
        Thực hiện nước đi từ ô bắt đầu đến ô kết thúc.
        """
        self.start_square.remove_piece()
        self.end_square.place_piece(self.piece)
        self.piece.move(self.end_square)

    def __str__(self):
        """
        Trả về chuỗi đại diện của nước đi.
        
        Returns:
            str: Thông tin của nước đi (ví dụ: 'Move(Pawn, (1, 0) -> (3, 0))').
        """
        return f"Move({self.piece}, ({self.start_square.row}, {self.start_square.col}) -> ({self.end_square.row}, {self.end_square.col}))"

    def __repr__(self):
        """
        Trả về chuỗi đại diện của nước đi.
        
        Returns:
            str: Thông tin của nước đi (ví dụ: 'Move(Pawn, (1, 0) -> (3, 0))').
        """
        return self.__str__()
