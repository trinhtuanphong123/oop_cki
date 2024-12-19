from __future__ import annotations
from core.pieces.piece import Piece
from core.square import Square
from typing import Any

class King(Piece):
    """
    Lớp đại diện cho quân vua (King) trong trò chơi cờ vua.
    """
    def __init__(self, color: str, position: Square):
        super().__init__(color, position)
        self.has_moved = False  # Dùng để theo dõi xem vua đã di chuyển hay chưa (phục vụ nhập thành)

    def get_legal_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Trả về danh sách các nước đi hợp lệ của quân vua.
        """
        moves = []
        row, col = self.position.row, self.position.col
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Ngang và dọc
            (1, 1), (1, -1), (-1, 1), (-1, -1) # Chéo
        ]

        # Duyệt qua các hướng di chuyển của vua
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            target_square = board.get_square(new_row, new_col)
            
            if target_square and (not target_square.is_occupied() or target_square.has_enemy_piece(self.color)):
                moves.append((new_row, new_col))

        # Thêm các nước đi nhập thành
        if not self.has_moved:
            moves += self._get_castling_moves(board)

        return moves

    def _get_castling_moves(self, board: Any) -> list[tuple[int, int]]:
        """
        Lấy danh sách các nước đi nhập thành hợp lệ cho vua.
        """
        moves = []
        row, col = self.position.row

        # Danh sách cột của xe cho nhập thành (cánh vua và cánh hậu)
        castling_positions = [(7, 6), (0, 2)]  # (cột xe, cột mà vua sẽ đến)

        for rook_col, king_dest_col in castling_positions:
            rook_square = board.get_square(row, rook_col)
            if rook_square and rook_square.is_occupied():
                rook = rook_square.piece
                if isinstance(rook, Piece) and not rook.has_moved:
                    # Kiểm tra xem ô giữa vua và xe có trống hay không
                    path_clear = all(
                        not board.get_square(row, col).is_occupied()
                        for col in range(min(rook_col, king_dest_col) + 1, max(rook_col, king_dest_col))
                    )

                    # Nếu tất cả các ô giữa vua và xe đều trống
                    if path_clear:
                        moves.append((row, king_dest_col))

        return moves
