from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any, List, Tuple
from ..square import Square
class Bishop(Piece):
    """
    Lớp đại diện cho quân tượng trong cờ vua.
    Quân tượng di chuyển theo đường chéo.
    """
    def __init__(self, color: str, position: 'Square'):
        """
        Khởi tạo quân tượng.
        
        Args:
            color: Màu của quân tượng ('white' hoặc 'black')
            position: Vị trí ban đầu
        """
        super().__init__(color, position, 'bishop')

    def get_legal_moves(self, board: Any) -> List[Tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân tượng.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Tuple[int, int]]: Danh sách các vị trí (row, col) hợp lệ
        """
        return self._get_diagonal_moves(board)

    def _get_diagonal_moves(self, board: Any) -> List[Tuple[int, int]]:
        """
        Lấy tất cả các nước đi chéo hợp lệ.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Tuple[int, int]]: Danh sách các nước đi chéo hợp lệ
        """
        moves = []
        row, col = self.position.row, self.position.col
        
        # Các hướng di chuyển chéo: phải-xuống, phải-lên, trái-xuống, trái-lên
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            moves.extend(self._get_moves_in_direction(board, row, col, dr, dc))

        return moves

    def _get_moves_in_direction(
        self, 
        board: Any, 
        row: int, 
        col: int, 
        dr: int, 
        dc: int
    ) -> List[Tuple[int, int]]:
        """
        Lấy các nước đi hợp lệ theo một hướng chéo.
        
        Args:
            board: Bàn cờ hiện tại
            row: Hàng hiện tại
            col: Cột hiện tại
            dr: Hướng di chuyển theo hàng
            dc: Hướng di chuyển theo cột
            
        Returns:
            List[Tuple[int, int]]: Các nước đi hợp lệ theo hướng
        """
        moves = []
        
        for distance in range(1, 8):  # Quân tượng đi tối đa 7 ô
            new_row = row + dr * distance
            new_col = col + dc * distance

            if not self._is_within_board(new_row, new_col):
                break

            target_square = board.get_square(new_row, new_col)
            
            if target_square.is_occupied():
                if target_square.has_enemy_piece(self.color):
                    moves.append((new_row, new_col))  # Có thể bắt quân địch
                break  # Dừng khi gặp bất kỳ quân cờ nào
            else:
                moves.append((new_row, new_col))  # Thêm nước đi vào ô trống

        return moves

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
        Tính giá trị của quân tượng dựa trên vị trí.
        
        Returns:
            float: Giá trị của quân tượng
        """
        base_value = 3.0  # Giá trị cơ bản của quân tượng
        
        # Cộng thêm điểm cho vị trí tốt
        position_bonus = self._calculate_position_bonus()
        
        return base_value + position_bonus

    def _calculate_position_bonus(self) -> float:
        """
        Tính điểm cộng thêm dựa trên vị trí của tượng.
        
        Returns:
            float: Điểm cộng thêm cho vị trí
        """
        bonus = 0.0
        
        # Tượng ở trung tâm mạnh hơn
        center_distance = abs(3.5 - self.position.col) + abs(3.5 - self.position.row)
        bonus -= center_distance * 0.05  # Càng xa trung tâm càng yếu
        
        # Tượng cặp mạnh hơn tượng đơn (được xử lý ở Board)
        
        return bonus

    def __str__(self) -> str:
        """Chuỗi đại diện của quân tượng"""
        return f"{self.color} Bishop at {self.position}"