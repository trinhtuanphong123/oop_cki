from core.pieces.piece import Piece

class Square:
    """
    Lớp đại diện cho ô vuông (ô cờ) trên bàn cờ.
    """
    def __init__(self, row: int, col: int, color: str):
        """
        Khởi tạo một ô vuông với vị trí hàng, cột và màu sắc.
        
        Args:
            row (int): Hàng của ô (0-7).
            col (int): Cột của ô (0-7).
            color (str): Màu của ô ('black' hoặc 'white').
        """
        self.row = row
        self.col = col
        self.color = color
        self.piece = None  # Quân cờ đang đứng trên ô (None nếu trống)

    def is_occupied(self) -> bool:
        """
        Kiểm tra xem ô có quân cờ hay không.
        
        Returns:
            bool: True nếu có quân cờ trên ô, ngược lại False.
        """
        return self.piece is not None

    def place_piece(self, piece: 'Piece'):
        """
        Đặt quân cờ vào ô vuông.
        
        Args:
            piece (Piece): Quân cờ cần đặt vào ô.
        """
        self.piece = piece

    def remove_piece(self) -> 'Piece':
        """
        Loại bỏ quân cờ khỏi ô và trả về quân cờ đã bị loại bỏ.
        
        Returns:
            Piece: Quân cờ đã bị loại khỏi ô.
        """
        piece = self.piece
        self.piece = None
        return piece

    def has_enemy_piece(self, color: str) -> bool:
        """
        Kiểm tra xem ô có chứa quân cờ của đối phương hay không.
        
        """
        return self.is_occupied() and self.piece.color != color

    def __str__(self):
        """
        Trả về chuỗi đại diện của ô vuông.
        
        Returns:
            str: Thông tin của ô vuông (ví dụ: 'Square(2, 3, black, Pawn)').
        """
        piece_info = str(self.piece) if self.piece else 'Empty'
        return f"Square({self.row}, {self.col}, {self.color}, {piece_info})"

    def __repr__(self):
        """
        Trả về chuỗi đại diện của ô vuông.
        
        Returns:
            str: Thông tin của ô vuông (ví dụ: 'Square(2, 3, black, Pawn)').
        """
        return self.__str__()
