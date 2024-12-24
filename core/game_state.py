# game_state.py
from typing import List, Optional, Dict, Set, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
import logging

from .board import Board
from .pieces.piece import Piece, PieceColor, PieceType
from .move import Move, MoveType
from .square import Square

logger = logging.getLogger(__name__)

class GameStatus(Enum):
    """Enum định nghĩa trạng thái game"""
    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"
    TIMEOUT = "timeout"

@dataclass
class GameStateMemento:
    """Lưu trữ trạng thái game (Memento pattern)"""
    board_state: Board
    current_player: PieceColor
    move_history: List[Move]
    captured_pieces: Dict[PieceColor, List[Piece]]
    status: GameStatus
    half_move_clock: int
    full_move_number: int

class GameState:
    """Quản lý trạng thái và luồng game cờ vua"""
    
    def __init__(self):
        self._board = Board()
        self._current_player = PieceColor.WHITE
        self._status = GameStatus.ACTIVE
        self._move_history: List[Move] = []
        self._state_history: List[GameStateMemento] = []
        self._captured_pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }
        self._half_move_clock = 0  # Đếm nước đi không bắt quân/không di chuyển tốt
        self._full_move_number = 1  # Số nước đi đầy đủ
        self._selected_piece: Optional[Piece] = None
        self._legal_moves: List[Move] = []
        self._initialize_game()

    def _initialize_game(self) -> None:
        """Khởi tạo game mới"""
        try:
            self._board.setup_initial_position()
            self._update_game_status()
            logger.info("Game initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing game: {e}")
            raise

    def make_move(self, start_square: 'Square', end_square: 'Square') -> bool:
        """Thực hiện nước đi"""
        try:
            # Validate basic conditions
            piece = start_square.piece
            if not self._validate_move_conditions(piece, start_square, end_square):
                return False

            # Create and validate move
            move = Move(start_square, end_square, piece)
            if not self._is_valid_move(move):
                return False

            # Save current state
            self._save_state()

            # Execute move
            self._execute_move(move)

            # Update game state
            self._update_after_move(move)
            
            logger.info(f"Move executed: {move}")
            return True

        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False

    def _validate_move_conditions(self, piece: Optional[Piece], 
                                start_square: 'Square', 
                                end_square: 'Square') -> bool:
        """Kiểm tra điều kiện cơ bản của nước đi"""
        if not piece:
            return False
        if piece.color != self._current_player:
            return False
        if self.is_game_over():
            return False
        if start_square == end_square:
            return False
        return True

    def _execute_move(self, move: Move) -> None:
        """Thực hiện nước đi trên bàn cờ"""
        # Handle capture
        if move.is_capture:
            captured_piece = move.end_square.piece
            if captured_piece:
                self._captured_pieces[self._current_player].append(captured_piece)

        # Handle castling
        if move.is_castle:
            self._handle_castling(move)
        
        # Handle en passant
        elif move.is_en_passant:
            self._handle_en_passant(move)
        
        # Handle promotion
        elif move.is_promotion:
            self._handle_promotion(move)
        
        # Standard move
        else:
            self._board.make_move(move)

    def _update_after_move(self, move: Move) -> None:
        """Cập nhật trạng thái sau nước đi"""
        # Update clocks
        self._update_move_clocks(move)
        
        # Add to history
        self._move_history.append(move)
        
        # Switch player
        self._switch_player()
        
        # Update game status
        self._update_game_status()
        
        # Clear selection
        self._selected_piece = None
        self._legal_moves.clear()

    def _update_move_clocks(self, move: Move) -> None:
        """Cập nhật đồng hồ nước đi"""
        # Reset half move clock if capture or pawn move
        if move.is_capture or move.piece.piece_type == PieceType.PAWN:
            self._half_move_clock = 0
        else:
            self._half_move_clock += 1

        # Increment full move number after black's move
        if self._current_player == PieceColor.BLACK:
            self._full_move_number += 1

    def get_legal_moves_for_piece(self, piece: Piece) -> List[Move]:
        """Lấy danh sách nước đi hợp lệ cho quân cờ"""
        if piece.color != self._current_player:
            return []
            
        possible_moves = piece.get_possible_moves(self._board)
        legal_moves = []
        
        for move in possible_moves:
            if self._is_legal_move(move):
                legal_moves.append(move)
                
        return legal_moves

    def _is_legal_move(self, move: Move) -> bool:
        """Kiểm tra nước đi có hợp pháp không (không để vua bị chiếu)"""
        # Make move temporarily
        self._board.make_move(move)
        
        # Check if king is in check
        is_legal = not self._is_king_in_check(self._current_player)
        
        # Undo move
        self._board.undo_move(move)
        
        return is_legal

    def _is_king_in_check(self, color: PieceColor) -> bool:
        """Kiểm tra vua có đang bị chiếu không"""
        king = self._board.get_king(color)
        if not king:
            return False
            
        opponent_color = (PieceColor.BLACK 
                         if color == PieceColor.WHITE 
                         else PieceColor.WHITE)
        
        for piece in self._board.get_pieces_by_color(opponent_color):
            if king.position in [move.end_square 
                               for move in piece.get_possible_moves(self._board)]:
                return True
        return False

    def get_game_result(self) -> Dict:
        """Lấy kết quả game"""
        return {
            'status': self._status,
            'winner': self._get_winner(),
            'move_count': len(self._move_history),
            'captured_pieces': self._captured_pieces
        }

    def _get_winner(self) -> Optional[PieceColor]:
        """Xác định người thắng"""
        if self._status == GameStatus.CHECKMATE:
            return (PieceColor.BLACK 
                   if self._current_player == PieceColor.WHITE 
                   else PieceColor.WHITE)
        return None

    def to_fen(self) -> str:
        """Chuyển trạng thái game sang notation FEN"""
        # Implementation of FEN notation conversion
        pass

    @classmethod
    def from_fen(cls, fen: str) -> 'GameState':
        """Tạo trạng thái game từ notation FEN"""
        # Implementation of FEN notation parsing
        pass