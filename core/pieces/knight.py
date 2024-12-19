from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any

class Knight(Piece):
    def get_legal_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân mã.
        
        """
        moves = []
        row, col = self.position.row, self.position.col
        jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in jumps:  # Lặp qua các nước đi hình chữ L
            new_row, new_col = row + dr, col + dc

            if self._is_within_board(new_row, new_col):
                target_square = board.get_square(new_row, new_col)
                if target_square and (not target_square.is_occupied() or target_square.has_enemy_piece(self.color)):
                    moves.append((new_row, new_col))

        return moves

    def _is_within_board(self, row: int, col: int) -> bool:
        """
        Kiểm tra xem tọa độ có nằm trong giới hạn bàn cờ không.
        
    
        """
        return 0 <= row < 8 and 0 <= col < 8
