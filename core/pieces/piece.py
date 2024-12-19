
from ..board import Board
from ..square import Square


import os

class Piece:
    """
    Lớp cơ sở đại diện cho quân cờ trong trò chơi cờ vua.
    """
    def __init__(self, color: str, position: 'Square', name: str):
        """
        Khởi tạo quân cờ với màu sắc, vị trí và tên của quân cờ.
        
        Args:
            color (str): Màu của quân cờ ('white' hoặc 'black').
            position (Square): Ô vuông mà quân cờ đang đứng.
            name (str): Tên của quân cờ ('pawn', 'rook', 'knight', v.v.).
        """
        self.color = color  # Màu của quân cờ ('white' hoặc 'black')
        self.position = position  # Ô vuông nơi quân cờ đang đứng
        self.name = name  # Tên của quân cờ ('pawn', 'rook', 'knight', etc.)
        self.texture = None  # Đường dẫn đến hình ảnh
        self.set_texture()

    def set_texture(self, size=80):
        """
        Cấu hình đường dẫn đến hình ảnh của quân cờ dựa trên kích thước và tên quân cờ.
        
        Args:
            size (int): Kích thước hình ảnh (mặc định là 80).
        """
        self.texture = os.path.join(
            f'assets/images/imgs-{size}', f'{self.color}-{self.name}.png'
        )

    def get_legal_moves(self, board: 'Board') -> list:
        """
        Trả về danh sách các nước đi hợp lệ cho quân cờ.
        
        """
        raise NotImplementedError("Phương thức này phải được triển khai trong các lớp con.")

    def move(self, new_square: 'Square'):
        """
        Di chuyển quân cờ đến một ô mới.
        
        Args:
            new_square (Square): Ô vuông mới nơi quân cờ sẽ di chuyển đến.
        """
        self.position = new_square

    def can_capture(self, target_square: 'Square') -> bool:
        """
        Kiểm tra xem quân cờ có thể bắt quân cờ của đối thủ trên ô mục tiêu không.
        
        """
        return target_square.is_occupied() and target_square.piece.color != self.color

    def __str__(self):
        """
        Trả về chuỗi đại diện của quân cờ.
        
        Returns:
            str: Thông tin của quân cờ (ví dụ: 'Piece(white, Rook)').
        """
        return f"Piece({self.color}, {self.name})"

    def __repr__(self):
        """
        Trả về chuỗi đại diện của quân cờ.
        
        Returns:
            str: Thông tin của quân cờ (ví dụ: 'Piece(white, Rook)').
        """
        return self.__str__()
