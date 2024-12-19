from core.square import Square
from core.pieces.pawn import Pawn
from core.pieces.rook import Rook
from core.pieces.knight import Knight
from core.pieces.bishop import Bishop
from core.pieces.queen import Queen
from core.pieces.king import King
from core.pieces.piece import Piece
from core.game_rule import GameRule

class Board:
    """
    Lớp đại diện cho bàn cờ cờ vua.
    """
    def __init__(self):
        """
        Khởi tạo bàn cờ 8x8 với các ô (Square) và sắp xếp các quân cờ vào vị trí ban đầu.
        """
        self.grid = [[Square(row, col, 'black' if (row + col) % 2 else 'white') for col in range(8)] for row in range(8)]
        self.setup_pieces()

    def setup_pieces(self):
        """
        Sắp xếp các quân cờ vào vị trí ban đầu.
        """
        # Sắp xếp quân tốt (Pawn)
        for col in range(8):
            self.grid[1][col].place_piece(Pawn('black', self.grid[1][col], 'path/to/black_pawn.png'))
            self.grid[6][col].place_piece(Pawn('white', self.grid[6][col], 'path/to/white_pawn.png'))

        # Sắp xếp quân xe (Rook)
        self.grid[0][0].place_piece(Rook('black', self.grid[0][0], 'path/to/black_rook.png'))
        self.grid[0][7].place_piece(Rook('black', self.grid[0][7], 'path/to/black_rook.png'))
        self.grid[7][0].place_piece(Rook('white', self.grid[7][0], 'path/to/white_rook.png'))
        self.grid[7][7].place_piece(Rook('white', self.grid[7][7], 'path/to/white_rook.png'))

        # Sắp xếp quân mã (Knight)
        self.grid[0][1].place_piece(Knight('black', self.grid[0][1], 'path/to/black_knight.png'))
        self.grid[0][6].place_piece(Knight('black', self.grid[0][6], 'path/to/black_knight.png'))
        self.grid[7][1].place_piece(Knight('white', self.grid[7][1], 'path/to/white_knight.png'))
        self.grid[7][6].place_piece(Knight('white', self.grid[7][6], 'path/to/white_knight.png'))

        # Sắp xếp quân tượng (Bishop)
        self.grid[0][2].place_piece(Bishop('black', self.grid[0][2], 'path/to/black_bishop.png'))
        self.grid[0][5].place_piece(Bishop('black', self.grid[0][5], 'path/to/black_bishop.png'))
        self.grid[7][2].place_piece(Bishop('white', self.grid[7][2], 'path/to/white_bishop.png'))
        self.grid[7][5].place_piece(Bishop('white', self.grid[7][5], 'path/to/white_bishop.png'))

        # Sắp xếp quân hậu (Queen)
        self.grid[0][3].place_piece(Queen('black', self.grid[0][3], 'path/to/black_queen.png'))
        self.grid[7][3].place_piece(Queen('white', self.grid[7][3], 'path/to/white_queen.png'))

        # Sắp xếp quân vua (King)
        self.grid[0][4].place_piece(King('black', self.grid[0][4], 'path/to/black_king.png'))
        self.grid[7][4].place_piece(King('white', self.grid[7][4], 'path/to/white_king.png'))

    def draw(self) -> list[list[dict]]:
        """
        Trả về dữ liệu đại diện cho bàn cờ.
        
        Returns:
            list[list[dict]]: Bàn cờ 8x8 với thông tin về ô và quân cờ.
        """
        board_representation = []
        for row in range(8):
            row_representation = []
            for col in range(8):
                square = self.grid[row][col]
                square_info = {
                    'row': row,
                    'col': col,
                    'color': square.color,
                    'piece': str(square.piece) if square.is_occupied() else None
                }
                row_representation.append(square_info)
            board_representation.append(row_representation)
        return board_representation

    def get_square(self, row: int, col: int) -> Square:
        """
        Lấy đối tượng ô vuông tại vị trí cụ thể.
        
        """
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def move_piece(self, start_square: Square, end_square: Square):
        """
        Thực hiện di chuyển quân cờ từ ô bắt đầu đến ô kết thúc.
        
        Args:
            start_square (Square): Ô xuất phát.
            end_square (Square): Ô đích.
        """
        piece = start_square.remove_piece()
        end_square.place_piece(piece)
        piece.move(end_square)

    def get_all_pieces(self) -> list:
        """
        Lấy danh sách tất cả các quân cờ hiện tại trên bàn cờ.
        
        Returns:
            list: Danh sách các quân cờ.
        """
        pieces = []
        for row in self.grid:
            for square in row:
                if square.is_occupied():
                    pieces.append(square.piece)
        return pieces

    def reset_board(self):
        """
        Đặt lại bàn cờ về trạng thái ban đầu.
        """
        self.grid = [[Square(row, col, 'black' if (row + col) % 2 else 'white') for col in range(8)] for row in range(8)]
        self.setup_pieces()

    def print_board(self):
        """
        In bàn cờ dưới dạng bảng.
        """
        for row in self.grid:
            print([str(square.piece) if square.is_occupied() else 'Empty' for square in row])

    def is_promotion(self, piece, end_square) -> bool:
        """
        Kiểm tra xem quân tốt có đạt đến hàng phong cấp không.
        
        Args:
            piece (Piece): Quân cờ hiện tại.
            end_square (Square): Ô đích nơi quân cờ sẽ di chuyển tới.
        
        Returns:
            bool: True nếu quân tốt có thể phong cấp, ngược lại False.
        """
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and end_square.row == 0) or (piece.color == 'black' and end_square.row == 7):
                return True
        return False
    
    def promote_pawn(self, pawn, position: 'Square', promotion_choice: str = 'queen') -> 'Piece':
        """
        Phong cấp quân tốt thành quân Hậu, Xe, Tượng hoặc Mã.
        
        Args:
            pawn (Pawn): Quân tốt cần được phong cấp.
            position (Square): Ô nơi quân tốt đã đạt đến hàng phong cấp.
            promotion_choice (str): Lựa chọn quân cờ (queen, rook, bishop, knight). Mặc định là "queen".
        
        Returns:
            Piece: Quân cờ mới (Queen, Rook, Knight, Bishop).
        """
        from core.pieces.queen import Queen
        from core.pieces.rook import Rook
        from core.pieces.knight import Knight
        from core.pieces.bishop import Bishop
        
        promotion_choice = promotion_choice.lower()
        
        if promotion_choice == 'queen':
            return Queen(pawn.color, position, f'path/to/{pawn.color}_queen.png')
        elif promotion_choice == 'rook':
            return Rook(pawn.color, position, f'path/to/{pawn.color}_rook.png')
        elif promotion_choice == 'knight':
            return Knight(pawn.color, position, f'path/to/{pawn.color}_knight.png')
        elif promotion_choice == 'bishop':
            return Bishop(pawn.color, position, f'path/to/{pawn.color}_bishop.png')
        else:
            # Mặc định là Hậu nếu lựa chọn không hợp lệ
            return Queen(pawn.color, position, f'path/to/{pawn.color}_queen.png')

    def filter_moves(self, piece: 'Piece', moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Lọc các nước đi không làm vua bị chiếu.
        """
        valid_moves = []
        for move in moves:
            start_square = self.get_square(piece.position.row, piece.position.col)
            end_square = self.get_square(move[0], move[1])
        
            # Tạo đối tượng Move
            move_object = Move(start_square, end_square, piece)
        
            # Kiểm tra xem nước đi có khiến vua bị chiếu không
            game_rule = GameRule(self)
            if not game_rule.will_king_be_in_check(move_object):
                valid_moves.append(move)
        return valid_moves



