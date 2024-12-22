from typing import List, Optional, Tuple, TYPE_CHECKING
from .piece import Piece, PieceColor, PieceType, Move

if TYPE_CHECKING:
    from ..board import Board
    from ..square import Square

class King(Piece):
    """
    Class đại diện cho quân Vua trong cờ vua.
    Quân Vua di chuyển một ô theo mọi hướng và có thể nhập thành.
    """
    __slots__ = ['_can_castle']

    def __init__(self, color: PieceColor, position: 'Square'):
        """
        Khởi tạo quân Vua.

        Args:
            color: Màu của quân Vua
            position: Vị trí ban đầu
        """
        super().__init__(color, position, PieceType.KING)
        self._can_castle = True  # Khả năng nhập thành

    @property
    def can_castle(self) -> bool:
        """Kiểm tra còn khả năng nhập thành không"""
        return self._can_castle and not self.has_moved

    def get_legal_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy tất cả các nước đi hợp lệ của quân Vua.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        moves = []
        current_row = self.position.row
        current_col = self.position.col

        # Các hướng di chuyển có thể của Vua
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Hướng trên
            (0, -1),           (0, 1),    # Hướng ngang
            (1, -1),  (1, 0),  (1, 1)     # Hướng dưới
        ]

        # Kiểm tra các nước đi thông thường
        for d_row, d_col in directions:
            new_row = current_row + d_row
            new_col = current_col + d_col

            # Kiểm tra nước đi có nằm trong bàn cờ không
            if not (0 <= new_row < 8 and 0 <= new_col < 8):
                continue

            target_square = board.get_square(new_row, new_col)
            
            # Không thể đi vào ô có quân cùng màu
            if target_square.has_friendly_piece(self.color):
                continue

            # Kiểm tra ô đích có an toàn không
            if self._is_square_safe(new_row, new_col, board):
                moves.append(Move(
                    start=(current_row, current_col),
                    end=(new_row, new_col),
                    is_capture=target_square.has_enemy_piece(self.color)
                ))

        # Thêm các nước nhập thành nếu có thể
        castling_moves = self._get_castling_moves(board)
        moves.extend(castling_moves)

        return moves

    def _is_square_safe(self, row: int, col: int, board: 'Board') -> bool:
        """
        Kiểm tra một ô có an toàn cho Vua không.
        
        Args:
            row: Hàng của ô cần kiểm tra
            col: Cột của ô cần kiểm tra
            board: Bàn cờ hiện tại
            
        Returns:
            bool: True nếu ô an toàn, False nếu không
        """
        # Kiểm tra tất cả quân địch
        for r in range(8):
            for c in range(8):
                square = board.get_square(r, c)
                if (square.is_occupied() and 
                    square.piece.color != self.color):
                    piece = square.piece
                    # Nếu là Vua đối phương, kiểm tra khoảng cách
                    if piece.piece_type == PieceType.KING:
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return False
                    # Với các quân khác, kiểm tra nước đi
                    else:
                        attacks = piece.get_pseudo_legal_moves(board)
                        if any(move.end == (row, col) for move in attacks):
                            return False
        return True

    def _get_castling_moves(self, board: 'Board') -> List[Move]:
        """
        Lấy các nước nhập thành có thể.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            List[Move]: Danh sách các nước nhập thành hợp lệ
        """
        moves = []
        if not self.can_castle:
            return moves

        # Vị trí ban đầu của Vua
        row = 7 if self.color == PieceColor.WHITE else 0
        
        # Kiểm tra nhập thành ngắn (bên phải)
        if self._can_castle_kingside(board, row):
            moves.append(Move(
                start=(row, 4),
                end=(row, 6),
                is_castle=True
            ))

        # Kiểm tra nhập thành dài (bên trái)
        if self._can_castle_queenside(board, row):
            moves.append(Move(
                start=(row, 4),
                end=(row, 2),
                is_castle=True
            ))

        return moves

    def _can_castle_kingside(self, board: 'Board', row: int) -> bool:
        """
        Kiểm tra có thể nhập thành ngắn không.
        
        Args:
            board: Bàn cờ hiện tại
            row: Hàng của Vua
            
        Returns:
            bool: True nếu có thể nhập thành ngắn
        """
        # Kiểm tra các ô giữa Vua và Xe có trống không
        if not (board.is_empty(row, 5) and board.is_empty(row, 6)):
            return False

        # Kiểm tra Xe có tại vị trí ban đầu không
        rook_square = board.get_square(row, 7)
        if not (rook_square.is_occupied() and 
                rook_square.piece.piece_type == PieceType.ROOK and
                not rook_square.piece.has_moved):
            return False

        # Kiểm tra các ô Vua đi qua có an toàn không
        return (self._is_square_safe(row, 4, board) and
                self._is_square_safe(row, 5, board) and
                self._is_square_safe(row, 6, board))

    def _can_castle_queenside(self, board: 'Board', row: int) -> bool:
        """
        Kiểm tra có thể nhập thành dài không.
        
        Args:
            board: Bàn cờ hiện tại
            row: Hàng của Vua
            
        Returns:
            bool: True nếu có thể nhập thành dài
        """
        # Kiểm tra các ô giữa Vua và Xe có trống không
        if not (board.is_empty(row, 3) and 
                board.is_empty(row, 2) and 
                board.is_empty(row, 1)):
            return False

        # Kiểm tra Xe có tại vị trí ban đầu không
        rook_square = board.get_square(row, 0)
        if not (rook_square.is_occupied() and 
                rook_square.piece.piece_type == PieceType.ROOK and
                not rook_square.piece.has_moved):
            return False

        # Kiểm tra các ô Vua đi qua có an toàn không
        return (self._is_square_safe(row, 4, board) and
                self._is_square_safe(row, 3, board) and
                self._is_square_safe(row, 2, board))

    def move_to(self, new_square: 'Square', board: 'Board') -> None:
        """
        Di chuyển Vua đến ô mới và xử lý nhập thành.
        
        Args:
            new_square: Ô đích
            board: Bàn cờ hiện tại
        """
        old_col = self.position.col
        new_col = new_square.col
        
        # Xử lý nhập thành
        if abs(new_col - old_col) == 2:
            row = self.position.row
            if new_col > old_col:  # Nhập thành ngắn
                rook_old = board.get_square(row, 7)
                rook_new = board.get_square(row, 5)
            else:  # Nhập thành dài
                rook_old = board.get_square(row, 0)
                rook_new = board.get_square(row, 3)
                
            # Di chuyển Xe
            rook = rook_old.piece
            rook.move_to(rook_new, board)

        super().move_to(new_square, board)
        self._can_castle = False

    def is_in_check(self, board: 'Board') -> bool:
        """
        Kiểm tra Vua có đang bị chiếu không.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            bool: True nếu đang bị chiếu
        """
        return not self._is_square_safe(self.position.row, 
                                      self.position.col, 
                                      board)

    def clone(self) -> 'King':
        """
        Tạo bản sao của quân Vua.
        
        Returns:
            King: Bản sao của quân Vua
        """
        clone = super().clone()
        clone._can_castle = self._can_castle
        return clone