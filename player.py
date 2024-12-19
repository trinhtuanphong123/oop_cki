from core.board import Board
from core.square import Square
from core.pieces.piece import Piece
from core.game_rule import GameRule

class Player:
    """
    Lớp đại diện cho người chơi trong trò chơi cờ vua.
    """
    def __init__(self, username: str, color: str):
        """
        Khởi tạo một người chơi với tên và màu của quân cờ mà họ điều khiển.
        
        Args:
            username (str): Tên của người chơi.
            color (str): Màu của quân cờ ('white' hoặc 'black').
        """
        self.username = username  # Tên của người chơi
        self.color = color  # Màu của quân cờ ('white' hoặc 'black')
        self.captured_pieces = []  # Danh sách các quân cờ đã bị bắt bởi người chơi

    def make_move(self, board: 'Board', start_square: 'Square', end_square: 'Square') -> bool:
        """
        Thực hiện một nước đi từ ô bắt đầu đến ô kết thúc.
        
        Args:
            board (Board): Bàn cờ hiện tại.
            start_square (Square): Ô bắt đầu của nước đi.
            end_square (Square): Ô kết thúc của nước đi.
        
        Returns:
            bool: True nếu nước đi thành công, False nếu nước đi không hợp lệ.
        """
        piece = start_square.piece
        if piece and piece.color == self.color:
            # Lấy danh sách các nước đi hợp lệ của quân cờ
            legal_moves = board.filter_moves(piece)
            
            # Kiểm tra xem ô kết thúc có nằm trong danh sách nước đi hợp lệ hay không
            if (end_square.row, end_square.col) in legal_moves:
                captured_piece = board.move_piece(start_square, end_square)
                if captured_piece:
                    self.capture_piece(captured_piece)
                return True
        return False

    def capture_piece(self, piece: 'Piece'):
        """
        Lưu trữ quân cờ đã bị người chơi bắt.
        
        Args:
            piece (Piece): Quân cờ bị bắt.
        """
        self.captured_pieces.append(piece)

    def get_captured_pieces(self) -> list:
        """
        Lấy danh sách các quân cờ mà người chơi đã bắt.
        
        Returns:
            list: Danh sách các quân cờ bị bắt.
        """
        return self.captured_pieces

    def has_legal_moves(self, board: 'Board') -> bool:
        """
        Kiểm tra xem người chơi có bất kỳ nước đi hợp lệ nào hay không.
        
        Args:
            board (Board): Bàn cờ hiện tại.
        
        Returns:
            bool: True nếu người chơi có ít nhất một nước đi hợp lệ, False nếu không.
        """
        for piece in board.get_all_pieces():
            if piece.color == self.color:
                legal_moves = board.filter_moves(piece)
                if legal_moves:
                    return True
        return False

    def is_king_in_check(self, board: 'Board') -> bool:
        """
        Kiểm tra xem vua của người chơi có đang bị chiếu hay không.
        
        """
        game_rule = GameRule(board)
        return game_rule.is_check(self.color)

    def possible_moves(self, board: 'Board') -> dict:
        """
        Lấy danh sách tất cả các nước đi hợp lệ của tất cả các quân cờ của người chơi.
        
        Args:
            board (Board): Bàn cờ hiện tại.
        
        Returns:
            dict: Từ điển chứa tất cả các nước đi hợp lệ của các quân cờ của người chơi.
                  Định dạng: {piece: [(row1, col1), (row2, col2), ...]}
        """
        moves = {}
        for piece in board.get_all_pieces():
            if piece.color == self.color:
                legal_moves = board.filter_moves(piece)
                if legal_moves:
                    moves[piece] = legal_moves
        return moves

    def __str__(self):
        """
        Trả về chuỗi đại diện của người chơi.
        
        Returns:
            str: Thông tin của người chơi (ví dụ: 'Player(JohnDoe, white)')
        """
        return f"Player({self.username}, {self.color})"

    def __repr__(self):
        """
        Trả về chuỗi đại diện của người chơi.
        
        Returns:
            str: Thông tin của người chơi (ví dụ: 'Player(JohnDoe, white)')
        """
        return self.__str__()
