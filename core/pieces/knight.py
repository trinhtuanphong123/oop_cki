from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any, List, Tuple

class Knight(Piece):
    """
    Lớp đại diện cho quân mã trong cờ vua.
    Quân mã di chuyển theo hình chữ L.
    """
    def __init__(self, color: str, position: 'Square'):
        """
        Khởi tạo quân mã.
        
        Args:
            color: Màu của quân mã ('white' hoặc 'black')
            position: Vị trí ban đầu
        """
        super().__init__(color, position, 'knight')

    def get_legal_moves(self, board: Any) -> List[Tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân mã.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Tuple[int, int]]: Danh sách các vị trí (row, col) hợp lệ
        """
        moves = []
        current_pos = (self.position.row, self.position.col)
        possible_moves = self._get_knight_moves(current_pos)

        for new_pos in possible_moves:
            if self._is_valid_move(board, new_pos):
                moves.append(new_pos)

        return moves

    def _get_knight_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Tạo danh sách tất cả các nước đi có thể của quân mã từ vị trí hiện tại.
        
        Args:
            position: Vị trí hiện tại (row, col)
            
        Returns:
            List[Tuple[int, int]]: Danh sách các vị trí có thể đi
        """
        row, col = position
        knight_moves = []
        
        # Các hướng di chuyển hình chữ L của quân mã
        jumps = [
            (-2, -1), (-2, 1),   # Lên 2 trái/phải 1
            (-1, -2), (-1, 2),   # Lên 1 trái/phải 2
            (1, -2), (1, 2),     # Xuống 1 trái/phải 2
            (2, -1), (2, 1)      # Xuống 2 trái/phải 1
        ]

        for dr, dc in jumps:
            new_row, new_col = row + dr, col + dc
            if self._is_within_board(new_row, new_col):
                knight_moves.append((new_row, new_col))

        return knight_moves

    def _is_valid_move(self, board: Any, position: Tuple[int, int]) -> bool:
        """
        Kiểm tra một nước đi có hợp lệ không.
        
        Args:
            board: Bàn cờ hiện tại
            position: Vị trí cần kiểm tra (row, col)
            
        Returns:
            bool: True nếu nước đi hợp lệ
        """
        row, col = position
        target_square = board.get_square(row, col)
        
        if not target_square:
            return False

        # Hợp lệ nếu ô trống hoặc có quân địch
        return (not target_square.is_occupied() or 
                target_square.has_enemy_piece(self.color))

    def _is_within_board(self, row: int, col: int) -> bool:
        """
        Kiểm tra tọa độ có nằm trong bàn cờ không.
        
        Args:
            row: Số hàng (0-7)
            col: Số cột (0-7)
            
        Returns:
            bool: True nếu tọa độ hợp lệ
        """
        return 0 <= row < 8 and 0 <= col < 8

    def get_value(self) -> float:
        """
        Tính giá trị của quân mã dựa trên vị trí.
        
        Returns:
            float: Giá trị của quân mã
        """
        base_value = 3.0  # Giá trị cơ bản của quân mã
        position_bonus = self._calculate_position_bonus()
        
        return base_value + position_bonus

    def _calculate_position_bonus(self) -> float:
        """
        Tính điểm cộng thêm dựa trên vị trí của mã.
        
        Returns:
            float: Điểm cộng thêm cho vị trí
        """
        row, col = self.position.row, self.position.col
        bonus = 0.0
        
        # Mã ở rìa bàn cờ yếu hơn
        if row in (0, 7) or col in (0, 7):
            bonus -= 0.2
            
        # Mã ở trung tâm mạnh hơn
        if 2 <= row <= 5 and 2 <= col <= 5:
            bonus += 0.3
            
        # Mã ở vị trí kiểm soát nhiều ô hơn
        control_squares = len(self.get_legal_moves(None))  # None là temporary
        bonus += control_squares * 0.05
        
        return bonus

    def __str__(self) -> str:
        """Chuỗi đại diện của quân mã"""
        return f"{self.color} Knight at ({self.position.row}, {self.position.col})"