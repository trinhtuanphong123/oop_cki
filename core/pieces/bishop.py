from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any

class Bishop(Piece):
    def get_legal_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân tượng.
        
        """
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Các hướng di chuyển chéo
        row, col = self.position.row, self.position.col

        for dr, dc in directions:  # Duyệt qua 4 hướng chéo
            for i in range(1, 8):  # Tượng có thể di chuyển tối đa 7 ô trên bàn cờ
                new_row, new_col = row + dr * i, col + dc * i

                if not self._is_within_board(new_row, new_col):
                    break  # Vượt quá giới hạn bàn cờ, dừng lại

                target_square = board.get_square(new_row, new_col)
                if target_square.is_occupied():
                    if target_square.has_enemy_piece(self.color):
                        moves.append((new_row, new_col))  # Bắt quân đối phương
                    break  # Dừng lại khi gặp vật cản
                else:
                    moves.append((new_row, new_col))  # Thêm nước đi hợp lệ

        return moves

    def _is_within_board(self, row: int, col: int) -> bool:
        """
        Kiểm tra xem tọa độ có nằm trong giới hạn bàn cờ không.
        
        """
        return 0 <= row < 8 and 0 <= col < 8
