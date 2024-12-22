# game_rule.py

from typing import List, Optional
from enum import Enum
from core.pieces.piece import Piece, PieceColor, PieceType
from .board import Board
from .move import Move
from .square import Square
from .pieces.king import King
from .pieces.pawn import Pawn
from .pieces.bishop import Bishop
from .pieces.knight import Knight
from .pieces.rook import Rook

class GameState:
    """Quản lý trạng thái game cờ"""
    
    class Status(Enum):
        """Trạng thái của ván cờ"""
        ACTIVE = "active"         # Đang chơi
        CHECK = "check"          # Chiếu
        CHECKMATE = "checkmate"  # Chiếu hết
        STALEMATE = "stalemate"  # Hòa do hết nước đi
        DRAW = "draw"            # Hòa do các lý do khác

    def __init__(self, board: Board):
        # Khởi tạo trạng thái game
        self._board = board
        self._current_player = PieceColor.WHITE
        self._status = self.Status.ACTIVE
        self._last_move = None
        
        # Quản lý lịch sử
        self._move_count = 0
        self._fifty_move_counter = 0
        self._move_history = []
        self._position_history = []

    @property
    def board(self) -> Board:
        return self._board

    @property
    def current_player(self) -> PieceColor:
        return self._current_player

    @property
    def status(self) -> Status:
        return self._status

    @property
    def last_move(self) -> Optional[Move]:
        return self._last_move

    @property
    def is_game_over(self) -> bool:
        """Kiểm tra game kết thúc"""
        return self._status in (
            self.Status.CHECKMATE,
            self.Status.STALEMATE,
            self.Status.DRAW
        )

    def update_after_move(self, move: Move) -> None:
        """Cập nhật trạng thái sau nước đi"""
        # Cập nhật lịch sử
        self._move_count += 1
        self._move_history.append(move)
        self._last_move = move
        self._position_history.append(str(self._board))
        
        # Cập nhật fifty-move rule
        if isinstance(move.moving_piece, Pawn) or move.is_capture:
            self._fifty_move_counter = 0
        else:
            self._fifty_move_counter += 1

        # Chuyển lượt chơi
        self._current_player = self._current_player.opposite
        
        # Cập nhật trạng thái game
        self._update_status()

    def undo_last_move(self) -> Optional[Move]:
        """Hoàn tác nước đi cuối"""
        if not self._move_history:
            return None

        # Lấy và xóa nước đi cuối
        last_move = self._move_history.pop()
        self._position_history.pop()
        
        # Cập nhật trạng thái
        self._move_count -= 1
        self._last_move = self._move_history[-1] if self._move_history else None
        self._current_player = self._current_player.opposite
        self._update_status()
        
        return last_move

    def _update_status(self) -> None:
        """Cập nhật trạng thái game"""
        if GameRule.is_checkmate(self._board, self._current_player):
            self._status = self.Status.CHECKMATE
        elif GameRule.is_stalemate(self._board, self._current_player):
            self._status = self.Status.STALEMATE
        elif self._is_draw():
            self._status = self.Status.DRAW
        elif GameRule.is_check(self._board, self._current_player):
            self._status = self.Status.CHECK
        else:
            self._status = self.Status.ACTIVE

    def _is_draw(self) -> bool:
        """Kiểm tra điều kiện hòa"""
        return (
            self._fifty_move_counter >= 50 or
            GameRule.is_insufficient_material(self._board) or
            self._is_threefold_repetition()
        )

    def _is_threefold_repetition(self) -> bool:
        """Kiểm tra lặp vị trí 3 lần"""
        for position in self._position_history:
            if self._position_history.count(position) >= 3:
                return True
        return False

    def __str__(self) -> str:
        return (
            f"Game Status: {self._status.value}\n"
            f"Current Player: {self._current_player.value}\n"
            f"Move Count: {self._move_count}"
        )

class GameRule:
    """Quản lý luật chơi"""
    @staticmethod
    def is_valid_move(board: Board, move: Move, current_player: PieceColor) -> bool:
        """Kiểm tra nước đi hợp lệ"""
        if not move.moving_piece or move.moving_piece.color != current_player:
            return False

        # Kiểm tra nước đi cơ bản
        if not move.moving_piece.can_move_to(move.end_square, board):
            return False

        # Kiểm tra các nước đặc biệt
        if move.is_en_passant and not GameRule._is_valid_en_passant(move, board):
            return False

        if move.is_castle and not GameRule._is_valid_castle(move, board):
            return False

        # Kiểm tra chiếu
        if GameRule._causes_self_check(board, move):
            return False

        return True

    @staticmethod
    def get_legal_moves(board: Board, piece: Piece) -> List[Move]:
        """Lấy danh sách nước đi hợp lệ"""
        legal_moves = []
        for move in piece.get_possible_moves(board):
            if GameRule.is_valid_move(board, move, piece.color):
                legal_moves.append(move)
        return legal_moves

    @staticmethod
    def is_check(board: Board, player: PieceColor) -> bool:
        """Kiểm tra vua có đang bị chiếu"""
        king = board.get_king(player)
        return king and GameRule._is_square_attacked(board, king.position, player.opposite)

    @staticmethod
    def is_checkmate(board: Board, player: PieceColor) -> bool:
        """Kiểm tra chiếu hết"""
        return (GameRule.is_check(board, player) and 
                GameRule._has_no_legal_moves(board, player))

    @staticmethod
    def is_stalemate(board: Board, player: PieceColor) -> bool:
        """Kiểm tra hết nước đi"""
        return (not GameRule.is_check(board, player) and 
                GameRule._has_no_legal_moves(board, player))

    @staticmethod
    def is_insufficient_material(board: Board) -> bool:
        """Kiểm tra không đủ quân chiếu hết"""
        white_pieces = board.get_pieces(PieceColor.WHITE)
        black_pieces = board.get_pieces(PieceColor.BLACK)

        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True  # Vua đối vua

        if (len(white_pieces) == 2 and len(black_pieces) == 1 or
            len(white_pieces) == 1 and len(black_pieces) == 2):
            # Vua + (tượng/mã) đối vua
            for piece in white_pieces + black_pieces:
                if isinstance(piece, (Bishop, Knight)):
                    return True

        return False

    @staticmethod
    def _is_valid_en_passant(move: Move, board: Board) -> bool:
        """Kiểm tra nước bắt tốt qua đường"""
        if not isinstance(move.moving_piece, Pawn):
            return False
        # Thêm logic kiểm tra en passant
        return True

    @staticmethod
    def _is_valid_castle(move: Move, board: Board) -> bool:
        """Kiểm tra nước nhập thành"""
        if not isinstance(move.moving_piece, King):
            return False
        # Thêm logic kiểm tra castle
        return True

    @staticmethod
    def _is_square_attacked(board: Board, square: Square, attacker_color: PieceColor) -> bool:
        """Kiểm tra ô có bị tấn công"""
        for piece in board.get_pieces(attacker_color):
            if piece.can_attack_square(square, board):
                return True
        return False

    @staticmethod
    def _has_no_legal_moves(board: Board, player: PieceColor) -> bool:
        """Kiểm tra không còn nước đi hợp lệ"""
        for piece in board.get_pieces(player):
            if GameRule.get_legal_moves(board, piece):
                return False
        return True

    @staticmethod
    def _causes_self_check(board: Board, move: Move) -> bool:
        """Kiểm tra nước đi có để vua bị chiếu"""
        # Tạo bàn cờ tạm để thử nước đi
        temp_board = board.clone()
        temp_board.make_move(move)
        
        # Kiểm tra vua có bị chiếu
        king = temp_board.get_king(move.moving_piece.color)
        return king and GameRule._is_square_attacked(
            temp_board,
            king.position,
            move.moving_piece.color.opposite
        )