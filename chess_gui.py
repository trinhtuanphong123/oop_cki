# gui/chess_gui.py
import pygame as pg
import os
from typing import Optional, List, Tuple, Dict
from core.move import Move
from core.pieces.piece import Piece, PieceColor

class Colors:
    """Màu sắc cho GUI"""
    LIGHT_SQUARE = (240, 217, 181)  # Màu ô sáng
    DARK_SQUARE = (181, 136, 99)    # Màu ô tối
    SELECTED = (186, 202, 43)       # Màu ô được chọn
    LEGAL_MOVE = (130, 151, 105)    # Màu nước đi hợp lệ
    LAST_MOVE = (205, 210, 106)     # Màu nước đi cuối
    CHECK = (220, 100, 100)         # Màu khi bị chiếu
    BACKGROUND = (49, 46, 43)       # Màu nền
    TEXT = (255, 255, 255)          # Màu chữ

class ChessGUI:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Board dimensions
        self.board_size = min(self.width - 200, self.height - 100)
        self.square_size = self.board_size // 8
        self.board_offset_x = (self.width - self.board_size) // 2
        self.board_offset_y = (self.height - self.board_size) // 2
        
        # Load images
        self.pieces_images = {}
        self.load_pieces()
        
        # UI state
        self.selected_square: Optional[Tuple[int, int]] = None
        self.legal_moves: List[Move] = []
        self.last_move: Optional[Move] = None
        self.flipped = False
        
        # Font initialization
        self.font = pg.font.SysFont('Arial', 20)
        self.large_font = pg.font.SysFont('Arial', 24, bold=True)

    def draw_board(self):
        """Vẽ bàn cờ"""
        for row in range(8):
            for col in range(8):
                x = self.board_offset_x + col * self.square_size
                y = self.board_offset_y + row * self.square_size
                color = Colors.LIGHT_SQUARE if (row + col) % 2 == 0 else Colors.DARK_SQUARE
                pg.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))

    def draw_pieces(self, board_state: Dict):
        """Vẽ quân cờ"""
        for row in range(8):
            for col in range(8):
                piece = board_state[row][col]
                if piece != '--':
                    x = self.board_offset_x + col * self.square_size
                    y = self.board_offset_y + row * self.square_size
                    self.screen.blit(self.pieces_images[piece], (x, y))

    def draw_highlights(self):
        """Vẽ các ô được highlight"""
        if self.selected_square:
            x = self.board_offset_x + self.selected_square[1] * self.square_size
            y = self.board_offset_y + self.selected_square[0] * self.square_size
            s = pg.Surface((self.square_size, self.square_size))
            s.set_alpha(128)
            s.fill(Colors.SELECTED)
            self.screen.blit(s, (x, y))
            
            for move in self.legal_moves:
                x = self.board_offset_x + move.end_square[1] * self.square_size
                y = self.board_offset_y + move.end_square[0] * self.square_size
                s = pg.Surface((self.square_size, self.square_size))
                s.set_alpha(100)
                s.fill(Colors.LEGAL_MOVE)
                self.screen.blit(s, (x, y))

    def draw_last_move(self):
        """Vẽ nước đi cuối cùng"""
        if self.last_move:
            for square in [self.last_move.start_square, self.last_move.end_square]:
                x = self.board_offset_x + square[1] * self.square_size
                y = self.board_offset_y + square[0] * self.square_size
                s = pg.Surface((self.square_size, self.square_size))
                s.set_alpha(100)
                s.fill(Colors.LAST_MOVE)
                self.screen.blit(s, (x, y))

    def load_pieces(self):
        """Load ảnh quân cờ"""
        piece_filenames = {
            'wP': 'white-pawn.png',
            'wR': 'white-rook.png',
            'wN': 'white-knight.png',
            'wB': 'white-bishop.png',
            'wQ': 'white-queen.png',
            'wK': 'white-king.png',
            'bP': 'black-pawn.png',
            'bR': 'black-rook.png',
            'bN': 'black-knight.png',
            'bB': 'black-bishop.png',
            'bQ': 'black-queen.png',
            'bK': 'black-king.png'
        }
        
        assets_dir = "assets/images/imgs-80"
        
        for piece_symbol, filename in piece_filenames.items():
            image_path = os.path.join(assets_dir, filename)
            try:
                if not os.path.exists(image_path):
                    print(f"Warning: Image not found at {image_path}")
                    surface = pg.Surface((self.square_size, self.square_size))
                    surface.fill((255, 255, 255))
                    font = pg.font.SysFont('Arial', 36)
                    text = font.render(piece_symbol, True, (0, 0, 0))
                    text_rect = text.get_rect(center=(self.square_size/2, self.square_size/2))
                    surface.blit(text, text_rect)
                    self.pieces_images[piece_symbol] = surface
                else:
                    image = pg.image.load(image_path)
                    self.pieces_images[piece_symbol] = pg.transform.scale(
                        image, 
                        (self.square_size, self.square_size)
                    )
            except pg.error as e:
                print(f"Error loading image {image_path}: {e}")
                surface = pg.Surface((self.square_size, self.square_size))
                surface.fill((255, 255, 255))
                font = pg.font.SysFont('Arial', 36)
                text = font.render(piece_symbol, True, (0, 0, 0))
                text_rect = text.get_rect(center=(self.square_size/2, self.square_size/2))
                surface.blit(text, text_rect)
                self.pieces_images[piece_symbol] = surface

    def draw_captured_pieces(self, white_captured: List[Piece], black_captured: List[Piece]):
        """Vẽ quân cờ bị bắt"""
        piece_size = self.square_size // 2
        start_x = self.board_offset_x + self.board_size + 20
        white_y = self.board_offset_y
        black_y = self.board_offset_y + self.board_size - piece_size
        
        for i, piece in enumerate(black_captured):
            x = start_x + (i % 8) * piece_size
            y = black_y - (i // 8) * piece_size
            scaled_image = pg.transform.scale(self.pieces_images[piece.symbol], (piece_size, piece_size))
            self.screen.blit(scaled_image, (x, y))
        
        for i, piece in enumerate(white_captured):
            x = start_x + (i % 8) * piece_size
            y = white_y + (i // 8) * piece_size
            scaled_image = pg.transform.scale(self.pieces_images[piece.symbol], (piece_size, piece_size))
            self.screen.blit(scaled_image, (x, y))

    def draw_current_player(self, current_player: PieceColor):
        """Hiển thị lượt đi hiện tại"""
        x = 10
        y = self.height // 2
        indicator_rect = pg.Rect(x, y - 30, 150, 60)
        pg.draw.rect(self.screen, Colors.BACKGROUND, indicator_rect)
        color_text = "White" if current_player == PieceColor.WHITE else "Black"
        text = self.large_font.render(f"{color_text}'s Turn", True, Colors.TEXT)
        self.screen.blit(text, (x + 10, y))

    def draw_move_history(self, moves: List[Move]):
        """Hiển thị lịch sử nước đi"""
        start_x = 10
        start_y = self.board_offset_y
        history_rect = pg.Rect(start_x, start_y, 150, self.board_size)
        pg.draw.rect(self.screen, Colors.BACKGROUND, history_rect)
        title = self.large_font.render("Move History", True, Colors.TEXT)
        self.screen.blit(title, (start_x + 10, start_y + 10))
        
        y = start_y + 50
        for i, move in enumerate(moves[-10:]):
            move_text = f"{i+1}. {move}"
            text = self.font.render(move_text, True, Colors.TEXT)
            self.screen.blit(text, (start_x + 10, y))
            y += 25

    def draw_check_indicator(self, is_check: bool):
        """Hiển thị trạng thái chiếu"""
        if is_check:
            text = self.large_font.render("CHECK!", True, Colors.CHECK)
            x = self.width - 150
            y = 10
            self.screen.blit(text, (x, y))

    def draw_game_end(self, winner: Optional[PieceColor], reason: str):
        """Hiển thị kết thúc game"""
        overlay = pg.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if winner:
            winner_text = "White" if winner == PieceColor.WHITE else "Black"
            message = f"{winner_text} wins by {reason}!"
        else:
            message = f"Game Over - {reason}"
        text = self.large_font.render(message, True, Colors.TEXT)
        text_rect = text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(text, text_rect)

    def update(self, game_state: Dict):
        """Cập nhật toàn bộ giao diện"""
        self.screen.fill(Colors.BACKGROUND)
        self.draw_board()
        self.draw_last_move()
        self.draw_highlights()
        self.draw_pieces(game_state['board'])
        self.draw_captured_pieces(
            game_state.get('white_captured', []),
            game_state.get('black_captured', [])
        )
        self.draw_current_player(game_state['current_player'])
        self.draw_move_history(game_state.get('move_history', []))
        
        if game_state.get('is_check', False):
            self.draw_check_indicator(True)
        if game_state.get('is_game_over', False):
            self.draw_game_end(
                game_state.get('winner'),
                game_state.get('end_reason', '')
            )
        pg.display.flip()