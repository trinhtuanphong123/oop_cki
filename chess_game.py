import pygame as pg
import sys
from chess_gui import ChessGUI
from game_manager import GameManager, GameMode
from player.human_player import HumanPlayer
from player.ai_player import AIPlayer, AILevel

class ChessGame:
    def __init__(self):
        # Initialize Pygame
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption('Chess Game')
        self.clock = pg.time.Clock()
        
        # Initialize components
        self.gui = ChessGUI(self.screen)
        self.game_manager = GameManager()
        
        # Initial state
        self.running = True
        self.current_state = "MENU"  # MENU, GAME, PAUSE

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        """Handle all pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                
            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.current_state == "MENU":
                    self.handle_menu_click(event.pos)
                elif self.current_state == "GAME":
                    self.handle_game_click(event.pos)

    def handle_menu_click(self, pos):
        """Handle clicks in menu"""
        # Temporary simple menu - just start a game
        self.start_new_game(GameMode.HUMAN_VS_HUMAN)

    def handle_game_click(self, pos):
        """Handle clicks during game"""
        square = self.gui.get_square_at_pos(pos)
        if square:
            result = self.game_manager.handle_square_selection(square)
            if result['selected']:
                self.gui.selected_square = square
                self.gui.legal_moves = result['legal_moves']
            if result['move_made']:
                self.gui.animate_move(result['move_made'])
                self.gui.last_move = result['move_made']

    def start_new_game(self, mode: GameMode):
        """Start a new game"""
        config = {
            'mode': mode,
            'white_player': {'name': 'Player 1'},
            'black_player': {'name': 'Player 2'},
        }
        if self.game_manager.create_game(config):
            self.current_state = "GAME"

    def update(self):
        """Update game state"""
        if self.current_state == "GAME":
            # Handle AI moves if needed
            if self.game_manager.is_ai_turn():
                move = self.game_manager.get_ai_move()
                if move:
                    self.gui.animate_move(move)
                    self.gui.last_move = move

    def draw(self):
        """Draw current frame"""
        if self.current_state == "MENU":
            self.draw_menu()
        elif self.current_state == "GAME":
            self.draw_game()
        
        pg.display.flip()

    def draw_menu(self):
        """Draw menu screen"""
        self.screen.fill((255, 255, 255))
        # Add menu drawing code here

    def draw_game(self):
        """Draw game screen"""
        game_state = self.game_manager.get_game_state()
        self.gui.update(game_state)

def main():
    game = ChessGame()
    game.run()
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()