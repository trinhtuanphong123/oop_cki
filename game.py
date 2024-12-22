import pygame
from typing import Tuple, Optional, List
from enum import Enum
from core.board import Board
from player import Player, PieceColor
from core.pieces.piece import Piece
from core.move import Move
from core.game_rule import GameRule
from chessBot import ChessAI, Difficulty



class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"

class GameManager:
    """
    Class quản lý game cờ vua
    Điều khiển luồng game và tương tác giữa các thành phần
    """
    def __init__(self, screen_size: Tuple[int, int] = (800, 800)):
        # Khởi tạo pygame
        pygame.init()
        
        # Thuộc tính màn hình
        self._screen_size = screen_size
        self._screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Chess Game")
        
        # Khởi tạo các thành phần game
        self._board = Board()
        self._game_rule = GameRule(self._board)
        
        # Khởi tạo người chơi
        self._white_player = Player(PieceColor.WHITE, True)  # Human
        self._black_player = Player(PieceColor.BLACK, False)  # AI
        self._current_player = self._white_player
        
        # Khởi tạo AI
        self._ai = ChessAI(PieceColor.BLACK, Difficulty.MEDIUM)
        
        # Trạng thái game
        self._game_state = GameState.PLAYING
        self._selected_piece = None
        self._valid_moves = []
        
        # Tính toán kích thước ô cờ
        self._square_size = min(screen_size[0], screen_size[1]) // 8
        
        # Load hình ảnh
        self._load_images()

    def _load_images(self) -> None:
        """Load hình ảnh quân cờ"""
        self._piece_images = {}
        for color in ['white', 'black']:
            for piece_type in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
                image = pygame.image.load(f'assets/{color}_{piece_type}.png')
                image = pygame.transform.scale(image, (self._square_size, self._square_size))
                self._piece_images[f'{color}_{piece_type}'] = image

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """
        Xử lý sự kiện click chuột
        Args:
            pos: Tọa độ click (x, y)
        """
        # Chuyển đổi tọa độ pixel sang tọa độ bàn cờ
        row = pos[1] // self._square_size
        col = pos[0] // self._square_size
        clicked_square = self._board.get_square(row, col)

        # Nếu chưa chọn quân cờ
        if self._selected_piece is None:
            if (clicked_square.piece and 
                clicked_square.piece.color == self._current_player.color):
                self._selected_piece = clicked_square.piece
                self._valid_moves = self._game_rule.get_legal_moves(self._selected_piece)
        
        # Nếu đã chọn quân cờ
        else:
            move = Move(self._selected_piece.position, clicked_square)
            if move in self._valid_moves:
                self._make_move(move)
                # Sau khi người chơi đi, cho AI đi
                if self._game_state == GameState.PLAYING:
                    self._make_ai_move()
            
            self._selected_piece = None
            self._valid_moves = []

    def _make_move(self, move: Move) -> None:
        """
        Thực hiện nước đi
        Args:
            move: Nước đi cần thực hiện
        """
        # Thực hiện nước đi trên bàn cờ
        self._board.make_move(move)
        
        # Cập nhật thông tin người chơi
        if move.is_capture:
            self._current_player.add_captured_piece(move.captured_piece)
        
        # Kiểm tra và cập nhật trạng thái game
        self._update_game_state()
        
        # Chuyển lượt nếu game chưa kết thúc
        if self._game_state == GameState.PLAYING:
            self._switch_player()

    def _make_ai_move(self) -> None:
        """Thực hiện nước đi của AI"""
        if self._current_player == self._black_player:
            valid_moves = self._game_rule.get_all_legal_moves(PieceColor.BLACK)
            ai_move = self._ai.get_best_move(self._board, valid_moves)
            if ai_move:
                self._make_move(ai_move)

    def _update_game_state(self) -> None:
        """Cập nhật trạng thái game"""
        if self._game_rule.is_checkmate(self._current_player.color):
            self._game_state = GameState.CHECKMATE
        elif self._game_rule.is_stalemate(self._current_player.color):
            self._game_state = GameState.STALEMATE
        elif self._game_rule.is_draw():
            self._game_state = GameState.DRAW

    def _switch_player(self) -> None:
        """Chuyển lượt chơi"""
        self._current_player = (
            self._black_player if self._current_player == self._white_player 
            else self._white_player
        )

    def draw(self) -> None:
        """Vẽ game lên màn hình"""
        self._draw_board()
        self._draw_pieces()
        if self._selected_piece:
            self._highlight_selected_square()
            self._highlight_valid_moves()
        pygame.display.flip()

    def _draw_board(self) -> None:
        """Vẽ bàn cờ"""
        for row in range(8):
            for col in range(8):
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(
                    self._screen, 
                    color, 
                    (col * self._square_size, row * self._square_size, 
                     self._square_size, self._square_size)
                )

    def _draw_pieces(self) -> None:
        """Vẽ quân cờ"""
        for row in range(8):
            for col in range(8):
                piece = self._board.get_square(row, col).piece
                if piece:
                    image = self._piece_images[f'{piece.color.value}_{piece.piece_type.lower()}']
                    self._screen.blit(
                        image, 
                        (col * self._square_size, row * self._square_size)
                    )

    def _highlight_selected_square(self) -> None:
        """Highlight ô đang chọn"""
        row, col = self._selected_piece.position
        surface = pygame.Surface((self._square_size, self._square_size))
        surface.set_alpha(128)
        surface.fill((255, 255, 0))
        self._screen.blit(surface, (col * self._square_size, row * self._square_size))

    def _highlight_valid_moves(self) -> None:
        """Highlight các nước đi hợp lệ"""
        for move in self._valid_moves:
            row, col = move.end_square.position
            surface = pygame.Surface((self._square_size, self._square_size))
            surface.set_alpha(128)
            surface.fill((0, 255, 0))
            self._screen.blit(surface, (col * self._square_size, row * self._square_size))

    def run(self) -> None:
        """Chạy game loop chính"""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)

            self.draw()
            clock.tick(60)

        pygame.quit()

    @property
    def game_state(self) -> GameState:
        """Lấy trạng thái game hiện tại"""
        return self._game_state

    def reset_game(self) -> None:
        """Reset game về trạng thái ban đầu"""
        self._board.reset()
        self._game_state = GameState.PLAYING
        self._current_player = self._white_player
        self._selected_piece = None
        self._valid_moves = []
        self._white_player.reset_stats()
        self._black_player.reset_stats()


def main():
    # Khởi tạo game manager
    game_manager = GameManager()
    
    # Chạy game
    game_manager.run()

if __name__ == "__main__":
    main()