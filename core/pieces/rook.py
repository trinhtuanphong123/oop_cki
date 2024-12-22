from typing import List, Tuple, Optional
from piece import Piece
from move import Move
from board import Board
from core.pieces.piece import PieceType, PieceColor
from square import Square

class Rook(Piece):
    """
    Class Rook kế thừa từ Piece, đại diện cho quân xe trong cờ vua
    Quân xe di chuyển theo chiều ngang hoặc dọc, không giới hạn số ô
    """
    def __init__(self, color: PieceColor, square: Square):
        """
        Khởi tạo quân xe
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân xe đang đứng
        """
        super().__init__(color, square)
        self._piece_type = PieceType.ROOK
        self._has_moved = False

    @property
    def piece_type(self) -> PieceType:
        """Lấy loại quân cờ"""
        return self._piece_type

    @property
    def has_moved(self) -> bool:
        """Kiểm tra quân xe đã di chuyển chưa (cho nhập thành)"""
        return self._has_moved

    def get_legal_moves(self, board: Board) -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân xe
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Các hướng di chuyển của xe: ngang và dọc
        directions = [
            (-1, 0),  # Lên
            (1, 0),   # Xuống
            (0, -1),  # Trái
            (0, 1)    # Phải
        ]

        for dir_row, dir_col in directions:
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

    def move_to(self, target_square: Square) -> None:
        """
        Di chuyển quân xe đến ô mới
        Args:
            target_square: Ô đích
        """
        super().move_to(target_square)
        self._has_moved = True

    def can_castle(self) -> bool:
        """
        Kiểm tra quân xe có thể thực hiện nhập thành không
        Returns:
            True nếu có thể nhập thành, False nếu không
        """
        return not self._has_moved

    def clone(self) -> 'Rook':
        """
        Tạo bản sao của quân xe
        Returns:
            Bản sao của quân xe hiện tại
        """
        new_rook = Rook(self.color, self.square)
        new_rook._has_moved = self._has_moved
        return new_rook

    def get_piece_value(self) -> int:
        """
        Lấy giá trị của quân xe cho việc tính điểm
        Returns:
            Giá trị quân xe
        """
        return 5

    def __str__(self) -> str:
        """String representation của quân xe"""
        color_name = "White" if self.color == PieceColor.WHITE else "Black"
        return f"{color_name} Rook at {self.square}"

    def get_symbol(self) -> str:
        """
        Lấy ký hiệu của quân xe để hiển thị
        Returns:
            'R' cho xe trắng, 'r' cho xe đen
        """
        return 'R' if self.color == PieceColor.WHITE else 'r'