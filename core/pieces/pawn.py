from __future__ import annotations
from core.pieces.piece import Piece
from typing import Any

class Pawn(Piece):
    def get_legal_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân tốt.
        
        """
        moves = []
        direction = -1 if self.color == 'white' else 1
        row, col = self.position.row, self.position.col

        # Kiểm tra đi thẳng 1 ô
        next_row = row + direction
        if self._is_within_board(next_row, col) and not board.get_square(next_row, col).is_occupied():
            moves.append((next_row, col))

        # Kiểm tra đi thẳng 2 ô (nước đi đầu tiên)
        start_row = 6 if self.color == 'white' else 1
        if row == start_row:
            two_step_row = row + 2 * direction
            if (self._is_within_board(two_step_row, col)
                and not board.get_square(next_row, col).is_occupied()
                and not board.get_square(two_step_row, col).is_occupied()):
                moves.append((two_step_row, col))

        # Kiểm tra bắt chéo
        for dx in [-1, 1]:
            diag_row, diag_col = row + direction, col + dx
            if self._is_within_board(diag_row, diag_col):
                target_square = board.get_square(diag_row, diag_col)
                if target_square and target_square.has_enemy_piece(self.color):
                    moves.append((diag_row, diag_col))

        return moves

    def _is_within_board(self, row: int, col: int) -> bool:
        """
        Kiểm tra xem tọa độ có nằm trong giới hạn bàn cờ không.
        
        """
        return 0 <= row < 8 and 0 <= col < 8
