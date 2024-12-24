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

class ChessGUI:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Board dimensions
        self.board_size = min(self.width - 200, self.height - 100)  # Leave space for UI
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
        self.flipped = False  # For board flipping

    def load_pieces(self):
        """Load piece images from assets folder"""
        pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK',
                 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK']
                 
        # Get the absolute path to the assets directory
        current_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(current_dir, '..', 'assets', 'pieces')
        
        for piece in pieces:
            image_path = os.path.join(assets_dir, f"{piece}.png")
            try:
                image = pg.image.load(image_path)
                # Scale image to fit square
                self.pieces_images[piece] = pg.transform.scale(
                    image, 
                    (self.square_size, self.square_size)
                )
            except pg.error as e:
                print(f"Error loading image {image_path}: {e}")

    def draw_board(self):
        """Draw the chess board"""
        for row in range(8):
            for col in range(8):
                # Calculate screen position
                x = self.board_offset_x + col * self.square_size
                y = self.board_offset_y + row * self.square_size
                
                # Determine square color
                color = Colors.LIGHT_SQUARE if (row + col) % 2 == 0 else Colors.DARK_SQUARE
                
                # Draw square
                pg.draw.rect(
                    self.screen,
                    color,
                    (x, y, self.square_size, self.square_size)
                )

    def draw_pieces(self, board_state: Dict):
        """Draw pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = board_state[row][col]
                if piece != '--':
                    # Calculate screen position
                    x = self.board_offset_x + col * self.square_size
                    y = self.board_offset_y + row * self.square_size
                    
                    # Draw piece
                    self.screen.blit(self.pieces_images[piece], (x, y))

    def draw_highlights(self):
        """Draw highlights for selected square and legal moves"""
        if self.selected_square:
            # Highlight selected square
            x = self.board_offset_x + self.selected_square[1] * self.square_size
            y = self.board_offset_y + self.selected_square[0] * self.square_size
            
            s = pg.Surface((self.square_size, self.square_size))
            s.set_alpha(128)
            s.fill(Colors.SELECTED)
            self.screen.blit(s, (x, y))
            
            # Highlight legal moves
            for move in self.legal_moves:
                x = self.board_offset_x + move.end_square[1] * self.square_size
                y = self.board_offset_y + move.end_square[0] * self.square_size
                
                s = pg.Surface((self.square_size, self.square_size))
                s.set_alpha(100)
                s.fill(Colors.LEGAL_MOVE)
                self.screen.blit(s, (x, y))

    def draw_last_move(self):
        """Highlight the last move made"""
        if self.last_move:
            for square in [self.last_move.start_square, self.last_move.end_square]:
                x = self.board_offset_x + square[1] * self.square_size
                y = self.board_offset_y + square[0] * self.square_size
                
                s = pg.Surface((self.square_size, self.square_size))
                s.set_alpha(100)
                s.fill(Colors.LAST_MOVE)
                self.screen.blit(s, (x, y))

    def animate_move(self, move: Move):
        """Animate piece movement"""
        start_x = self.board_offset_x + move.start_square[1] * self.square_size
        start_y = self.board_offset_y + move.start_square[0] * self.square_size
        end_x = self.board_offset_x + move.end_square[1] * self.square_size
        end_y = self.board_offset_y + move.end_square[0] * self.square_size
        
        piece_image = self.pieces_images[move.piece.symbol]
        frames = 10
        
        for i in range(frames + 1):
            # Clear previous frame
            self.draw_board()
            
            # Calculate current position
            current_x = start_x + (end_x - start_x) * i / frames
            current_y = start_y + (end_y - start_y) * i / frames
            
            # Draw piece at current position
            self.screen.blit(piece_image, (current_x, current_y))
            
            pg.display.flip()
            pg.time.wait(20)  # 20ms delay between frames

    def get_square_at_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to board coordinates"""
        x, y = pos
        
        # Check if click is within board bounds
        if (x < self.board_offset_x or 
            x >= self.board_offset_x + self.board_size or
            y < self.board_offset_y or 
            y >= self.board_offset_y + self.board_size):
            return None
            
        # Convert to board coordinates
        col = (x - self.board_offset_x) // self.square_size
        row = (y - self.board_offset_y) // self.square_size
        
        # Flip coordinates if board is flipped
        if self.flipped:
            row = 7 - row
            col = 7 - col
            
        return (row, col)

    def draw_game_info(self, game_state: Dict):
        """Draw game information (captured pieces, current player, etc)"""
        # Draw captured pieces
        self.draw_captured_pieces(
            game_state['white_captured'],
            game_state['black_captured']
        )
        
        # Draw current player indicator
        self.draw_current_player(game_state['current_player'])
        
        # Draw move history
        self.draw_move_history(game_state['move_history'])

    def draw_captured_pieces(self, white_captured: List[Piece], black_captured: List[Piece]):
        """Draw captured pieces on the side of the board"""
        # Implementation for drawing captured pieces

    def draw_current_player(self, current_player: PieceColor):
        """Draw indicator for current player's turn"""
        # Implementation for drawing current player

    def draw_move_history(self, moves: List[Move]):
        """Draw move history on the side"""
        # Implementation for drawing move history

    def flip_board(self):
        """Flip the board view"""
        self.flipped = not self.flipped

    def update(self, game_state: Dict):
        """Update the complete display"""
        # Clear screen
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw components
        self.draw_board()
        self.draw_last_move()
        self.draw_highlights()
        self.draw_pieces(game_state['board'])
        self.draw_game_info(game_state)
        
        # Update display
        pg.display.flip()