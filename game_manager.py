# game/game_manager.py

from typing import Optional, Dict, List, Tuple
from enum import Enum
from datetime import datetime

from core.game_state import GameState, GameStatus
from core.board import Board
from core.move import Move, MoveType
from core.square import Square
from core.pieces.piece import Piece, PieceColor
from player.player import Player
from player.human_player import HumanPlayer
from player.ai_player import AIPlayer, AILevel
from ai.chess_ai import ChessAi

class GameMode(Enum):
    HUMAN_VS_HUMAN = "human_vs_human"
    HUMAN_VS_AI = "human_vs_ai" 
    AI_VS_AI = "ai_vs_ai"

class GameManager:
    """
    Class điều phối toàn bộ luồng game, kết nối các thành phần và xử lý logic chính
    """
    def __init__(self):
        # Core components
        self._game_state: Optional[GameState] = None
        self._board: Optional[Board] = None
        
        # Players
        self._white_player: Optional[Player] = None 
        self._black_player: Optional[Player] = None
        self._current_player: Optional[Player] = None
        
        # Game state tracking
        self._selected_piece: Optional[Piece] = None
        self._legal_moves: List[Move] = []
        self._move_history: List[Move] = []
        self._game_mode: Optional[GameMode] = None
        self._game_started: Optional[datetime] = None
        self._is_game_over = False

        # Game settings
        self._animation_speed = 1.0
        self._show_legal_moves = True
        self._auto_queen_promotion = True

    def create_game(self, config: Dict) -> bool:
        """
        Tạo game mới với cấu hình được chỉ định
        Args:
            config: {
                'mode': GameMode,
                'white_player': Dict player info,
                'black_player': Dict player info,
                'ai_level': AILevel (optional),
                'time_control': int (minutes, optional)
            }
        """
        try:
            # Reset state
            self._reset_game_state()
            
            # Setup core components
            self._game_state = GameState()
            self._board = self._game_state.board
            self._game_mode = config['mode']
            self._game_started = datetime.now()
            
            # Setup players
            self._setup_players(config)
            
            # Additional settings
            if 'time_control' in config:
                self._setup_time_control(config['time_control'])
                
            return True
        except Exception as e:
            print(f"Error creating game: {e}")
            return False

    def handle_square_selection(self, square_pos: Tuple[int, int]) -> Dict:
        """
        Xử lý khi người chơi click chọn ô
        Args:
            square_pos: (row, col) của ô được chọn
        Returns:
            Dict containing:
                - selected: bool
                - legal_moves: List[Move]
                - move_made: Optional[Move]
                - game_over: bool
                - updates: List[Dict]
        """
        result = {
            'selected': False,
            'legal_moves': [],
            'move_made': None,
            'game_over': False,
            'updates': []
        }

        # Validate current state
        if self._is_game_over or not self._current_player:
            return result

        # Get square and piece
        square = self._board.get_square(*square_pos)
        if not square:
            return result

        # If piece already selected, try to make move
        if self._selected_piece:
            if square in [move.end_square for move in self._legal_moves]:
                move = Move(
                    self._selected_piece.position,
                    square,
                    self._selected_piece
                )
                result.update(self._make_move(move))
            self._clear_selection()
            return result

        # Select new piece
        piece = square.piece
        if piece and piece.color == self._current_player.color:
            self._selected_piece = piece
            self._legal_moves = self._game_state.get_legal_moves(piece)
            result['selected'] = True
            result['legal_moves'] = self._legal_moves

        return result

    def _make_move(self, move: Move) -> Dict:
        """
        Thực hiện nước đi và cập nhật trạng thái
        """
        result = {
            'move_made': move,
            'captured': None,
            'game_over': False,
            'updates': []
        }

        # Save current state for undo
        self._save_state()

        # Execute move
        self._game_state.make_move(move)
        self._move_history.append(move)

        # Update captured pieces
        if move.is_capture:
            result['captured'] = move.captured_piece
            self._current_player.add_captured_piece(move.captured_piece)

        # Check game end conditions
        if self._game_state.is_checkmate():
            result['game_over'] = True
            result['winner'] = self._current_player
            self._handle_game_end(self._current_player)
        elif self._game_state.is_stalemate() or self._game_state.is_draw():
            result['game_over'] = True
            self._handle_game_end(None)

        # Switch player if game not over
        if not result['game_over']:
            self._switch_player()

        return result

    def get_ai_move(self) -> Optional[Move]:
        """Get AI move if it's AI's turn"""
        if isinstance(self._current_player, AIPlayer):
            return self._current_player.get_move(self._game_state)
        return None

    def undo_last_move(self) -> bool:
        """Undo the last move if possible"""
        if not self._move_history:
            return False
            
        self._restore_last_state()
        self._move_history.pop()
        self._switch_player()
        return True

    def _setup_players(self, config: Dict) -> None:
        """Setup players based on game mode"""
        if self._game_mode == GameMode.HUMAN_VS_HUMAN:
            self._white_player = HumanPlayer(config['white_player'])
            self._black_player = HumanPlayer(config['black_player'])
        
        elif self._game_mode == GameMode.HUMAN_VS_AI:
            self._white_player = HumanPlayer(config['white_player'])
            self._black_player = AIPlayer(
                color=PieceColor.BLACK,
                level=config.get('ai_level', AILevel.MEDIUM)
            )
        
        else:  # AI_VS_AI
            self._white_player = AIPlayer(
                color=PieceColor.WHITE,
                level=config.get('white_ai_level', AILevel.MEDIUM)
            )
            self._black_player = AIPlayer(
                color=PieceColor.BLACK,
                level=config.get('black_ai_level', AILevel.MEDIUM)
            )

        self._current_player = self._white_player

    def _switch_player(self) -> None:
        """Switch current player"""
        self._current_player = (
            self._black_player 
            if self._current_player == self._white_player 
            else self._white_player
        )

    def _clear_selection(self) -> None:
        """Clear current piece selection"""
        self._selected_piece = None
        self._legal_moves = []

    def _save_state(self) -> None:
        """Save current game state"""
        self._game_state.create_memento()

    def _restore_last_state(self) -> None:
        """Restore to last saved state"""
        self._game_state.restore_from_memento()

    def get_game_state(self) -> Dict:
        """Get current game state for UI"""
        return {
            'board': self._board.get_position(),
            'current_player': self._current_player,
            'selected_piece': self._selected_piece,
            'legal_moves': self._legal_moves,
            'move_history': self._move_history,
            'is_check': self._game_state.is_check(),
            'is_game_over': self._is_game_over,
            'white_captured': self._white_player.captured_pieces,
            'black_captured': self._black_player.captured_pieces
        }

    def _handle_game_end(self, winner: Optional[Player]) -> None:
        """Handle game end"""
        self._is_game_over = True
        if winner:
            winner.increment_score()
        # Update player stats
        self._update_player_stats()

    def _reset_game_state(self) -> None:
        """Reset all game state variables"""
        self._game_state = None
        self._board = None
        self._selected_piece = None
        self._legal_moves = []
        self._move_history = []
        self._is_game_over = False