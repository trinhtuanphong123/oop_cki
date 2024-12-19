from .board import Board
from .square import Square
from .move import Move
from core.pieces.pawn import Pawn
from core.pieces.king import King
from core.pieces.rook import Rook
import copy

class GameRule:
    """
    Lớp đại diện cho các quy tắc của trò chơi cờ vua.
    """
    def __init__(self, board: 'Board'):
        """
        Khởi tạo luật chơi với tham chiếu đến bàn cờ hiện tại.
        
        Args:
            board (Board): Đối tượng bàn cờ hiện tại.
        """
        self.board = board

    def is_legal_move(self, move: 'Move') -> bool:
        """
        Kiểm tra xem nước đi có hợp lệ theo luật chơi hay không.
        
        """
        if self.will_king_be_in_check(move):
            return False
        return True

    def will_king_be_in_check(self, move: 'Move') -> bool:
        """
        Giả lập nước đi và kiểm tra xem vua của người chơi có bị chiếu hay không.
        
        """
        # Tạo bản sao của bàn cờ
        board_copy = copy.deepcopy(self.board)

        # Thực hiện nước đi trên bàn cờ sao chép
        start_square = move.start_square
        end_square = move.end_square
        board_copy.move_piece(start_square, end_square)
        
        # Kiểm tra xem vua có bị chiếu không
        is_king_in_check = self.is_check(move.piece.color)
        
        return is_king_in_check
    

    def is_checkmate(self, color: str) -> bool:
        """
        Kiểm tra xem người chơi có bị chiếu hết hay không.
        
        """
        if not self.is_check(color):
            return False

        for piece in self.board.get_all_pieces():
            if piece.color == color:
                legal_moves = piece.get_legal_moves(self.board)
                for move in legal_moves:
                    # Tạo bản sao của bàn cờ trước khi thực hiện nước đi
                    board_copy = copy.deepcopy(self.board)
                    start_square = self.board.get_square(piece.position.row, piece.position.col)
                    end_square = self.board.get_square(move[0], move[1])
                    board_copy.move_piece(start_square, end_square)
                    
                    # Kiểm tra xem vua còn bị chiếu không
                    if not self.is_check(color):
                        return False
        return True

    def is_stalemate(self, color: str) -> bool:
        """
        Kiểm tra xem có phải thế cờ hòa hay không.
        
        """
        if self.is_check(color):
            return False

        for piece in self.board.get_all_pieces():
            if piece.color == color:
                legal_moves = piece.get_legal_moves(self.board)
                if legal_moves:
                    return False
        return True

    def is_check(self, color: str) -> bool:
        """
        Kiểm tra xem vua của người chơi có bị chiếu không.
        
        """
        king_position = self.find_king_position(color)
        if not king_position:
            return False

        for piece in self.board.get_all_pieces():
            if piece.color != color:
                legal_moves = piece.get_legal_moves(self.board)
                if king_position in legal_moves:
                    return True
        return False

    def find_king_position(self, color: str) -> tuple:
        """
        Tìm vị trí của vua trên bàn cờ.
        
        """
        for piece in self.board.get_all_pieces():
            if isinstance(piece, King) and piece.color == color:
                return (piece.position.row, piece.position.col)
        return None

    def is_promotion(self, pawn: 'Pawn', target_square: 'Square') -> bool:
        """
        Kiểm tra xem quân tốt có được phong cấp hay không.
        
        """
        if isinstance(pawn, Pawn) and (target_square.row == 0 or target_square.row == 7):
            return True
        return False

    def is_en_passant(self, pawn: 'Pawn', target_square: 'Square') -> bool:
        """
        Kiểm tra xem có thể thực hiện bắt tốt qua đường (en passant) hay không.
        
        """
        last_move = self.board.get_last_move()
        if last_move and isinstance(last_move.piece, Pawn):
            if abs(last_move.start_square.row - last_move.end_square.row) == 2:
                if pawn.position.row == last_move.end_square.row and pawn.position.col == target_square.col:
                    return True
        return False
    
    def is_castling_move(self, move: 'Move') -> bool:
        piece = move.piece
        if not isinstance(piece, King) or piece.has_moved:
            return False

        if abs(move.start_square.col - move.end_square.col) == 2:
            rook_start_col = 7 if move.end_square.col == 6 else 0
            rook_square = self.board.get_square(move.start_square.row, rook_start_col)
            if isinstance(rook_square.piece, Rook) and not rook_square.piece.has_moved:
                return True
        return False

    def execute_castling(self, move: 'Move'):
        """
    Thực hiện nước đi nhập thành.
    """
        king = move.piece
    
    # Di chuyển vua
        self.board.move_piece(move.start_square, move.end_square)
        king.has_moved = True  # Đánh dấu rằng vua đã di chuyển
    
    # Di chuyển xe (rook)
        if abs(move.start_square.col - move.end_square.col) == 2:
            rook_start_col = 7 if move.end_square.col == 6 else 0
            rook_end_col = 5 if move.end_square.col == 6 else 3

            rook_square = self.board.get_square(move.start_square.row, rook_start_col)
            rook_piece = rook_square.remove_piece()

            new_rook_square = self.board.get_square(move.start_square.row, rook_end_col)
            new_rook_square.place_piece(rook_piece)
            rook_piece.has_moved = True  # Đánh dấu rằng xe đã di chuyển
