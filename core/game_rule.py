# game_rule.py
from typing import List, Optional, Set, TYPE_CHECKING
from .pieces.piece import Piece, PieceColor
from .pieces.king import King
from .pieces.pawn import Pawn

if TYPE_CHECKING:
    from .board import Board
    from .move import Move
    from .square import Square

class GameRule:
    """
    Class quản lý luật chơi cờ vua.
    Sử dụng static methods để kiểm tra và xác thực các nước đi.
    """

    @staticmethod
    def is_valid_move(board: 'Board', move: 'Move', current_player: PieceColor) -> bool:
        """
        Kiểm tra nước đi có hợp lệ không
        Args:
            board: Bàn cờ hiện tại
            move: Nước đi cần kiểm tra
            current_player: Người chơi hiện tại
        Returns:
            bool: True nếu nước đi hợp lệ
        """
        piece = move.piece

        # Kiểm tra cơ bản
        if not piece or piece.color != current_player:
            return False

        # Kiểm tra quân có thể đi đến ô đích không
        if not piece.can_move_to(move.end_square, board):
            return False

        # Tạo bản sao bàn cờ để thử nước đi
        temp_board = board.clone()
        temp_piece = temp_board.get_piece_at(piece.position.row, piece.position.col)
        temp_end = temp_board.get_square(move.end_square.row, move.end_square.col)

        # Thử nước đi
        temp_board.make_move(move.__class__(
            temp_piece.position,
            temp_end,
            temp_piece,
            move_type=move._move_type
        ))

        # Kiểm tra có để vua bị chiếu không
        return not GameRule.is_check(temp_board, current_player)

    @staticmethod
    def get_legal_moves(board: 'Board', piece: Piece) -> List['Move']:
        """
        Lấy tất cả nước đi hợp lệ của một quân
        Args:
            board: Bàn cờ hiện tại
            piece: Quân cờ cần lấy nước đi
        Returns:
            Danh sách các nước đi hợp lệ
        """
        legal_moves = []
        possible_moves = piece.get_possible_moves(board)

        for move in possible_moves:
            if GameRule.is_valid_move(board, move, piece.color):
                legal_moves.append(move)

        return legal_moves

    @staticmethod
    def is_check(board: 'Board', color: PieceColor) -> bool:
        """
        Kiểm tra vua có đang bị chiếu không
        Args:
            board: Bàn cờ hiện tại
            color: Màu của vua cần kiểm tra
        Returns:
            True nếu vua đang bị chiếu
        """
        king = board.get_king(color)
        if not king:
            return False

        return board.is_square_attacked(king.position, color.opposite)

    @staticmethod
    def is_checkmate(board: 'Board', color: PieceColor) -> bool:
        """
        Kiểm tra có phải chiếu hết không
        Args:
            board: Bàn cờ hiện tại
            color: Màu cần kiểm tra
        Returns:
            True nếu là chiếu hết
        """
        # Nếu không bị chiếu thì không thể chiếu hết
        if not GameRule.is_check(board, color):
            return False

        # Kiểm tra có nước đi nào thoát được không
        return not GameRule._has_legal_moves(board, color)

    @staticmethod
    def is_stalemate(board: 'Board', color: PieceColor) -> bool:
        """
        Kiểm tra có phải hết cờ không
        Args:
            board: Bàn cờ hiện tại
            color: Màu cần kiểm tra
        Returns:
            True nếu là hết cờ
        """
        # Nếu đang bị chiếu thì không phải hết cờ
        if GameRule.is_check(board, color):
            return False

        # Hết cờ khi không còn nước đi hợp lệ
        return not GameRule._has_legal_moves(board, color)

    @staticmethod
    def _has_legal_moves(board: 'Board', color: PieceColor) -> bool:
        """
        Kiểm tra có còn nước đi hợp lệ không
        Args:
            board: Bàn cờ hiện tại
            color: Màu cần kiểm tra
        Returns:
            True nếu còn nước đi hợp lệ
        """
        for piece in board.get_pieces(color):
            if GameRule.get_legal_moves(board, piece):
                return True
        return False

    @staticmethod
    def is_insufficient_material(board: 'Board') -> bool:
        """
        Kiểm tra có đủ quân để chiếu hết không
        Args:
            board: Bàn cờ hiện tại
        Returns:
            True nếu không đủ quân để chiếu hết
        """
        white_pieces = board.get_pieces(PieceColor.WHITE)
        black_pieces = board.get_pieces(PieceColor.BLACK)

        # Chỉ còn 2 vua
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True

        # Vua + tượng/mã vs vua
        if (len(white_pieces) == 1 and len(black_pieces) == 2) or \
           (len(white_pieces) == 2 and len(black_pieces) == 1):
            for pieces in [white_pieces, black_pieces]:
                if len(pieces) == 2:
                    non_king = next(p for p in pieces if not isinstance(p, King))
                    if not GameRule._is_major_piece(non_king):
                        return True

        return False

    @staticmethod
    def _is_major_piece(piece: Piece) -> bool:
        """
        Kiểm tra có phải quân lớn không (xe, hậu)
        Args:
            piece: Quân cờ cần kiểm tra
        Returns:
            True nếu là quân lớn
        """
        from .pieces.rook import Rook
        from .pieces.queen import Queen
        return isinstance(piece, (Rook, Queen))

    @staticmethod
    def validate_castle_move(board: 'Board', king: King, rook_square: 'Square') -> bool:
        """
        Kiểm tra nước nhập thành có hợp lệ không
        Args:
            board: Bàn cờ hiện tại
            king: Quân vua
            rook_square: Ô của xe
        Returns:
            True nếu có thể nhập thành
        """
        if king.has_moved:
            return False

        rook = rook_square.piece
        if not rook or rook.has_moved:
            return False

        # Kiểm tra đường đi có trống không
        direction = 1 if rook_square.col > king.position.col else -1
        col = king.position.col + direction

        while col != rook_square.col:
            if board.get_piece_at(king.position.row, col):
                return False
            col += direction

        # Kiểm tra vua không đi qua ô bị chiếu
        color = king.color
        if GameRule.is_check(board, color):
            return False

        col = king.position.col
        end_col = king.position.col + (2 * direction)
        while col != end_col:
            square = board.get_square(king.position.row, col)
            if board.is_square_attacked(square, color.opposite):
                return False
            col += direction

        return True

    @staticmethod
    def validate_en_passant(board: 'Board', move: 'Move') -> bool:
        """
        Kiểm tra nước bắt tốt qua đường có hợp lệ không
        Args:
            board: Bàn cờ hiện tại
            move: Nước đi cần kiểm tra
        Returns:
            True nếu có thể bắt tốt qua đường
        """
        if not isinstance(move.piece, Pawn):
            return False

        last_move = board.last_move
        if not last_move or not isinstance(last_move.piece, Pawn):
            return False

        # Kiểm tra điều kiện bắt tốt qua đường
        if abs(last_move.start_square.row - last_move.end_square.row) != 2:
            return False

        if move.piece.position.row != last_move.end_square.row:
            return False

        if abs(move.piece.position.col - last_move.end_square.col) != 1:
            return False

        return True