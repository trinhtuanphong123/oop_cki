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

        # Kiểm tra từng hướng đi chéo
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

    def is_diagonal_move(self, move: Move) -> bool:
        """
        Kiểm tra xem một nước đi có phải là nước đi chéo hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu là nước đi chéo hợp lệ, False nếu không
        """
        start_row, start_col = move.start_square.row, move.start_square.col
        end_row, end_col = move.end_square.row, move.end_square.col
        
        # Di chuyển chéo khi độ chênh lệch hàng và cột bằng nhau
        return abs(end_row - start_row) == abs(end_col - start_col)

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

    def can_reach_square(self, target_square: Square, board: Board) -> bool:
        """
        Kiểm tra xem quân tượng có thể đi đến ô đích không (không tính các quân chặn)
        Args:
            target_square: Ô đích cần kiểm tra
            board: Bàn cờ hiện tại
        Returns:
            True nếu có thể đi đến, False nếu không
        """
        move = Move(self.square, target_square)
        return self.is_diagonal_move(move)