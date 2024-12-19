from const import ROWS, COLS, SQUARE_SIZE, WIDTH, HEIGHT
import pygame
from core.board import Board
from player import Player
from interface.dragger import Dragger
from core.pieces.pawn import Pawn
from core.pieces.king import King
from core.game_rule import GameRule
from chessBot import AI  # Giả sử lớp AI đã có
from core.move import Move

pygame.init()

class Game:
    """
    Lớp chính đại diện cho trò chơi cờ vua, quản lý trạng thái và logic của trò chơi.
    """
    def __init__(self, player_username: str):
        """
        Khởi tạo trò chơi với người chơi và AI.
        
        Args:
            player_username (str): Tên của người chơi.
        """
        self.board = Board()  # Tạo bàn cờ
        self.player = Player(player_username, 'white')  # Người chơi điều khiển quân trắng
        self.ai = AI('black', 'medium')  # AI điều khiển quân đen
        self.dragger = Dragger()  # Quản lý kéo và thả quân cờ
        self.current_player = self.player  # Người chơi đi trước
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))  # Cửa sổ trò chơi
        pygame.display.set_caption("Chess Game")

    def draw(self):
        """
        Vẽ bàn cờ và các quân cờ trên màn hình.
        """
        self.board.draw(self.window)
        if self.dragger.dragging and self.dragger.piece:
            x, y = self.dragger.mouse_x - SQUARE_SIZE // 2, self.dragger.mouse_y - SQUARE_SIZE // 2
            self.window.blit(self.dragger.piece.image, (x, y))
        pygame.display.update()

    def switch_turn(self):
        """
        Chuyển lượt chơi từ người chơi sang AI và ngược lại.
        """
        self.current_player = self.player if self.current_player == self.ai else self.ai

    def handle_player_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        """
        Xử lý nước đi của người chơi.
        """
        start_square = self.board.get_square(*start_pos)
        end_square = self.board.get_square(*end_pos)
    
        if start_square and end_square and start_square.is_occupied():
            piece = start_square.piece
        
            if piece.color == self.player.color:
                move = Move(start_square, end_square, piece)
                game_rule = GameRule(self.board)
            
                # Kiểm tra nếu đây là nước đi nhập thành
                if game_rule.is_castling_move(move):
                    game_rule.execute_castling(move)
                    return True
            
                # Xử lý nước đi thông thường
                move_successful = self.board.move_piece(start_square, end_square)
            
                # Đánh dấu rằng vua đã di chuyển
                if isinstance(piece, King):
                    piece.has_moved = True
            
                # Phong cấp tốt nếu cần
                if move_successful and isinstance(piece, Pawn) and self.board.is_promotion(piece, end_square):
                    promoted_piece = self.board.promote_pawn(piece, end_square)
                    end_square.place_piece(promoted_piece)
            
                return move_successful
        return False

    def handle_ai_move(self):
        """
        AI tính toán và thực hiện nước đi của mình.
        """
        best_move = self.ai.calculate_best_move(self.board)
        if best_move:
            game_rule = GameRule(self.board)
            # Kiểm tra nếu AI thực hiện nước đi nhập thành
            if game_rule.is_castling_move(best_move):
                game_rule.execute_castling(best_move)
            else:
                self.board.move_piece(best_move.start_square, best_move.end_square)

    def check_game_state(self):
        """
        Kiểm tra xem trò chơi có kết thúc không (chiếu hết, hòa).
        """
        game_rule = GameRule(self.board)
        
        if game_rule.is_checkmate(self.player.color):
            print("Checkmate! AI wins!")
            return "checkmate"
        elif game_rule.is_checkmate(self.ai.color):
            print("Checkmate! Player wins!")
            return "checkmate"
        elif game_rule.is_stalemate(self.player.color) or game_rule.is_stalemate(self.ai.color):
            print("Stalemate! The game is a draw.")
            return "stalemate"
        return "continue"

    def reset_game(self):
        """
        Đặt lại trò chơi về trạng thái ban đầu.
        """
        self.board.reset_board()
        self.current_player = self.player

    def highlight_legal_moves(self, pos: tuple):
        """
        Tô sáng các nước đi hợp lệ của quân cờ được chọn.
        
        Args:
            pos (tuple): Vị trí ô được chọn (row, col).
        """
        square = self.board.get_square(*pos)
        if square and square.is_occupied():
            piece = square.piece
            if piece.color == self.current_player.color:
                legal_moves = self.board.filter_moves(piece)
                for move in legal_moves:
                    row, col = move
                    square = self.board.get_square(row, col)
                    if square:
                        pygame.draw.rect(self.window, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.display.update()

    def run(self):
        """
        Chạy vòng lặp trò chơi chính.
        """
        clock = pygame.time.Clock()
        running = True
        highlighted_moves = []

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = event.pos[1] // SQUARE_SIZE, event.pos[0] // SQUARE_SIZE
                    square = self.board.get_square(row, col)
                    if square and square.is_occupied():
                        self.dragger.start_drag(square.piece)
                        self.highlight_legal_moves((row, col))

                elif event.type == pygame.MOUSEBUTTONUP:
                    row, col = event.pos[1] // SQUARE_SIZE, event.pos[0] // SQUARE_SIZE
                    if self.dragger.dragging:
                        self.handle_player_move((self.dragger.piece.position.row, self.dragger.piece.position.col), (row, col))
                        self.dragger.stop_drag()
                        self.switch_turn()
                        self.handle_ai_move()

                elif event.type == pygame.MOUSEMOTION:
                    self.dragger.update_mouse_position(event.pos)

            self.draw()
            clock.tick(60)

        pygame.quit()
