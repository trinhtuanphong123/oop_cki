# src/gui/game_manager.py

from typing import Optional, List, Tuple
from enum import Enum
from .core.board import Board
from .core.game_rule import GameState
from .core.move import Move
from .core.game_rule import GameRule
from .core.pieces.piece import Piece, PieceColor
from .player.player import Player
from .player.ai_player import AIPlayer
from .ai.chess_ai import ChessAI
from .ai.strategies.strategies import AIStrategy
from .ai.strategies.radom import RandomStrategy
from .ai.strategies.negamax import NegamaxStrategy
from .ai.strategies.mcts import MCTSStrategy

class GameStatus(Enum):
    """Trạng thái của ván cờ"""
    ACTIVE = "active"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"

class GameMode(Enum):
    """Chế độ chơi"""
    PLAYER_VS_PLAYER = "pvp"
    PLAYER_VS_AI = "pve"
    AI_VS_AI = "eve"

class GameDifficulty(Enum):
    """Độ khó của AI"""
    EASY = 1    # Random Strategy
    MEDIUM = 2  # Negamax depth 3
    HARD = 3    # Negamax depth 5
    EXPERT = 4  # MCTS with more time

class GameManager:
    """
    Quản lý luồng game và giao diện người dùng
    Kết nối giữa GUI và logic game
    """
    
    def __init__(self):
        """Khởi tạo game manager"""
        self._game_state = GameState()
        self._mode = GameMode.PLAYER_VS_PLAYER
        self._players: List[Player] = []
        self._move_history: List[Move] = []
        self._status = GameStatus.ACTIVE
        self._current_player_index = 0
        self._selected_piece: Optional[Piece] = None
        self._highlighted_moves: List[Move] = []
        self._game_rules = GameRule()
        
        # AI settings
        self._ai_difficulty = GameDifficulty.MEDIUM
        self._ai_thinking_time = {
            GameDifficulty.EASY: 1.0,
            GameDifficulty.MEDIUM: 2.0,
            GameDifficulty.HARD: 3.0,
            GameDifficulty.EXPERT: 5.0
        }

    def new_game(self, mode: GameMode, difficulty: GameDifficulty = GameDifficulty.MEDIUM) -> None:
        """
        Bắt đầu ván cờ mới
        Args:
            mode: Chế độ chơi (PvP, PvE, EvE)
            difficulty: Độ khó cho AI
        """
        self._mode = mode
        self._ai_difficulty = difficulty
        self._setup_players()
        self._game_state = GameState()
        self._move_history.clear()
        self._status = GameStatus.ACTIVE
        self._current_player_index = 0
        self._selected_piece = None
        self._highlighted_moves.clear()

    def _setup_players(self) -> None:
        """Thiết lập người chơi dựa trên mode và độ khó"""
        ai_strategy = self._get_ai_strategy()
        
        if self._mode == GameMode.PLAYER_VS_PLAYER:
            self._players = [
                Player("Player 1", PieceColor.WHITE),
                Player("Player 2", PieceColor.BLACK)
            ]
        elif self._mode == GameMode.PLAYER_VS_AI:
            self._players = [
                Player("Player", PieceColor.WHITE),
                AIPlayer("AI", PieceColor.BLACK, ai_strategy)
            ]
        else:  # AI_VS_AI
            self._players = [
                AIPlayer("AI White", PieceColor.WHITE, NegamaxStrategy()),
                AIPlayer("AI Black", PieceColor.BLACK, MCTSStrategy())
            ]

    def _get_ai_strategy(self) -> AIStrategy:
        """Chọn chiến thuật AI dựa trên độ khó"""
        if self._ai_difficulty == GameDifficulty.EASY:
            return RandomStrategy()
        elif self._ai_difficulty == GameDifficulty.MEDIUM:
            strategy = NegamaxStrategy()
            strategy.set_depth(3)
            return strategy
        elif self._ai_difficulty == GameDifficulty.HARD:
            strategy = NegamaxStrategy()
            strategy.set_depth(5)
            return strategy
        else:  # EXPERT
            return MCTSStrategy()

    def handle_square_click(self, row: int, col: int) -> None:
        """
        Xử lý sự kiện click vào ô cờ
        Args:
            row: Hàng của ô được click
            col: Cột của ô được click
        """
        if self._status != GameStatus.ACTIVE:
            return

        clicked_square = self._game_state.board.get_square(row, col)
        
        # Nếu đã chọn quân cờ trước đó
        if self._selected_piece:
            # Tìm nước đi đến ô được click
            move = self._find_move_to_square(clicked_square)
            if move in self._highlighted_moves:
                self.make_move(move)
                self._clear_selection()
            else:
                # Click vào ô khác -> chọn quân mới nếu hợp lệ
                self._try_select_piece(clicked_square)
        else:
            # Chưa chọn quân nào -> thử chọn quân mới
            self._try_select_piece(clicked_square)

    def _try_select_piece(self, square) -> None:
        """
        Thử chọn quân cờ trên ô
        Args:
            square: Ô cần kiểm tra
        """
        piece = square.piece
        if piece and piece.color == self.current_player.color:
            self._selected_piece = piece
            self._highlighted_moves = self._game_state.get_legal_moves(piece)

    def _clear_selection(self) -> None:
        """Xóa lựa chọn hiện tại"""
        self._selected_piece = None
        self._highlighted_moves.clear()

    def _find_move_to_square(self, target_square) -> Optional[Move]:
        """
        Tìm nước đi đến ô đích trong các nước đi được highlight
        Args:
            target_square: Ô đích
        Returns:
            Nước đi tìm thấy hoặc None
        """
        for move in self._highlighted_moves:
            if move.end_square == target_square:
                return move
        return None

    def make_move(self, move: Move) -> bool:
        """
        Thực hiện nước đi
        Args:
            move: Nước đi cần thực hiện
        Returns:
            True nếu thành công, False nếu thất bại
        """
        if self._game_state.make_move(move):
            self._move_history.append(move)
            self.current_player.add_move(move)
            self._update_game_status()
            self._switch_player()
            return True
        return False

    def get_square_highlights(self) -> List[Tuple[int, int]]:
        """
        Lấy danh sách các ô cần highlight
        Returns:
            List các tọa độ (row, col) cần highlight
        """
        highlights = []
        
        # Highlight ô quân được chọn
        if self._selected_piece:
            pos = self._selected_piece.position
            highlights.append((pos.row, pos.col))
            
        # Highlight các nước đi hợp lệ
        for move in self._highlighted_moves:
            highlights.append((move.end_square.row, move.end_square.col))
            
        return highlights

    def handle_promotion(self, piece_type: str) -> None:
        """
        Xử lý việc phong cấp tốt
        Args:
            piece_type: Loại quân muốn phong cấp
        """
        if self._game_state.pending_promotion:
            self._game_state.complete_promotion(piece_type)
            self._switch_player()

    def get_ai_move(self) -> Optional[Move]:
        """
        Lấy nước đi từ AI
        Returns:
            Nước đi được AI chọn
        """
        if isinstance(self.current_player, AIPlayer):
            thinking_time = self._ai_thinking_time[self._ai_difficulty]
            return self.current_player.get_move(self._game_state, thinking_time)
        return None

    @property
    def current_player(self) -> Player:
        """Lấy người chơi hiện tại"""
        return self._players[self._current_player_index]

    @property
    def game_state(self) -> GameState:
        """Lấy trạng thái game"""
        return self._game_state

    @property
    def status(self) -> GameStatus:
        """Lấy trạng thái ván cờ"""
        return self._status

    def _update_game_status(self) -> None:
        """Cập nhật trạng thái game"""
        if self._game_state.is_checkmate():
            self._status = GameStatus.CHECKMATE
            winner_index = (self._current_player_index + 1) % 2
            self._players[winner_index].update_score(1)
        elif self._game_state.is_stalemate():
            self._status = GameStatus.STALEMATE
        elif self._game_state.is_draw():
            self._status = GameStatus.DRAW

    def _switch_player(self) -> None:
        """Chuyển lượt chơi"""
        self._current_player_index = (self._current_player_index + 1) % 2

    def get_game_result(self) -> dict:
        """
        Lấy kết quả ván cờ
        Returns:
            Dict chứa thông tin kết quả
        """
        return {
            'status': self._status,
            'winner': self._get_winner(),
            'moves_count': len(self._move_history),
            'player1_score': self._players[0].score,
            'player2_score': self._players[1].score
        }

    def _get_winner(self) -> Optional[Player]:
        """
        Xác định người thắng
        Returns:
            Người thắng hoặc None nếu hòa
        """
        if self._status in [GameStatus.STALEMATE, GameStatus.DRAW]:
            return None
        return self._players[(self._current_player_index + 1) % 2]

    def save_game(self, filename: str) -> bool:
        """
        Lưu ván cờ
        Args:
            filename: Tên file lưu
        Returns:
            True nếu lưu thành công
        """
        # TODO: Implement save game logic
        pass

    def load_game(self, filename: str) -> bool:
        """
        Tải ván cờ
        Args:
            filename: Tên file cần tải
        Returns:
            True nếu tải thành công
        """
        # TODO: Implement load game logic
        pass