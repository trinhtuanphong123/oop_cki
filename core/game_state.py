# game_state.py
from typing import List, Optional, Dict
from enum import Enum
import logging

from .board import Board
from .pieces.piece import Piece, PieceColor, PieceType
from .move import Move
from .square import Square

logger = logging.getLogger(__name__)

class GameStatus(Enum):
    """Trạng thái game"""
    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate" 
    STALEMATE = "stalemate"
    DRAW = "draw"

class GameState:
    """Quản lý trạng thái game cờ vua"""
    
    def __init__(self):
        self._board = Board()
        self._current_player = PieceColor.WHITE
        self._status = GameStatus.ACTIVE
        self._move_history: List[Move] = []
        self._captured_pieces = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: []
        }
        self._initialize_game()

    def _initialize_game(self) -> None:
        """Khởi tạo game mới"""
        try:
            self._board.setup_initial_position()
            self._update_game_status()
        except Exception as e:
            logger.error(f"Error initializing game: {e}")
            raise

    def make_move(self, start_square: Square, end_square: Square) -> bool:
        """Thực hiện nước đi"""
        try:
            piece = start_square.piece
            if not piece or piece.color != self._current_player:
                return False

            move = Move(start_square, end_square, piece)
            if not self._is_legal_move(move):
                return False

            # Xử lý bắt quân
            if end_square.piece:
                self._captured_pieces[self._current_player].append(end_square.piece)

            # Thực hiện nước đi
            self._board.make_move(move)
            self._move_history.append(move)
            
            # Chuyển lượt và cập nhật trạng thái
            self._current_player = (PieceColor.BLACK 
                                  if self._current_player == PieceColor.WHITE 
                                  else PieceColor.WHITE)
            self._update_game_status()
            
            return True

        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False

    def _is_legal_move(self, move: Move) -> bool:
        """Kiểm tra nước đi hợp lệ"""
        # Thử nước đi
        self._board.make_move(move)
        
        # Kiểm tra vua có bị chiếu không
        is_legal = not self._is_king_in_check(self._current_player)
        
        # Hoàn tác nước đi
        self._board.undo_move(move)
        
        return is_legal

    def _is_king_in_check(self, color: PieceColor) -> bool:
        """Kiểm tra vua có bị chiếu"""
        king = self._board.get_king(color)
        if not king:
            return False
            
        opponent_color = (PieceColor.BLACK 
                         if color == PieceColor.WHITE 
                         else PieceColor.WHITE)
        
        for piece in self._board.get_pieces_by_color(opponent_color):
            moves = piece.get_possible_moves(self._board)
            if any(move.end_square == king.position for move in moves):
                return True
        return False

    def _update_game_status(self) -> None:
        """Cập nhật trạng thái game"""
        # Kiểm tra chiếu
        if self._is_king_in_check(self._current_player):
            # Kiểm tra chiếu hết
            if not self._has_legal_moves():
                self._status = GameStatus.CHECKMATE
            else:
                self._status = GameStatus.CHECK
        # Kiểm tra hòa cờ
        elif not self._has_legal_moves():
            self._status = GameStatus.STALEMATE
        else:
            self._status = GameStatus.ACTIVE

    def _has_legal_moves(self) -> bool:
        """Kiểm tra còn nước đi hợp lệ không"""
        for piece in self._board.get_pieces_by_color(self._current_player):
            if any(self._is_legal_move(move) 
                  for move in piece.get_possible_moves(self._board)):
                return True
        return False

    def get_legal_moves(self, square: Square) -> List[Move]:
        """Lấy danh sách nước đi hợp lệ cho một ô"""
        piece = square.piece
        if not piece or piece.color != self._current_player:
            return []
            
        moves = []
        for move in piece.get_possible_moves(self._board):
            if self._is_legal_move(move):
                moves.append(move)
        return moves

    def get_game_state(self) -> Dict:
        """Lấy trạng thái game"""
        return {
            'board': self._board,
            'current_player': self._current_player,
            'status': self._status,
            'move_history': self._move_history,
            'captured_pieces': self._captured_pieces,
        }

    def is_game_over(self) -> bool:
        """Kiểm tra game kết thúc chưa"""
        return self._status in (
            GameStatus.CHECKMATE, 
            GameStatus.STALEMATE,
            GameStatus.DRAW
        )