from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any

class Rook(Piece):
    def get_legal_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân xe.
        
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Các hướng đi ngang và dọc
        row, col = self.position.row, self.position.col

        for dr, dc in directions:  # Lặp qua 4 hướng
            for i in range(1, 8):  # Quân xe có thể đi tối đa 7 ô trong một hướng
                new_row, new_col = row + dr * i, col + dc * i

                if not self._is_within_board(new_row, new_col):
                    break  # Nếu vượt ngoài bàn cờ, dừng lại
                
                target_square = board.get_square(new_row, new_col)
                if target_square.is_occupied():
                    if target_square.has_enemy_piece(self.color):
                        moves.append((new_row, new_col))  # Bắt quân cờ đối phương
                    break  # Dừng lại khi gặp vật cản (quân cờ)
                else:
                    moves.append((new_row, new_col))  # Thêm nước đi trống vào danh sách

        return moves

    def _is_within_board(self, row: int, col: int) -> bool:
        """
        Kiểm tra xem tọa độ có nằm trong giới hạn bàn cờ không.
        
        """
        return 0 <= row < 8 and 0 <= col < 8
