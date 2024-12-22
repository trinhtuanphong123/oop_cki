# game_rule.py

from typing import List, Optional, Dict, Tuple
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

class GameState(Enum):
    """Trạng thái của ván cờ"""
    ACTIVE = "active"         # Đang chơi
    CHECK = "check"          # Chiếu
    CHECKMATE = "checkmate"  # Chiếu hết
    STALEMATE = "stalemate"  # Hòa do hết nước đi
    DRAW = "draw"            # Hòa do các lý do khác

class GameRule:
    def __init__(self, board: Board):
        # Khởi tạo các thuộc tính cơ bản
        self._board = board
        self._current_player = PieceColor.WHITE
        self._state = GameState.ACTIVE
        self._last_move: Optional[Move] = None
        
        # Quản lý nước đi
        self._fifty_move_counter = 0
        self._move_count = 0
        self._move_history: List[Move] = []
        self._position_history: List[str] = []
        
        # Quản lý en passant
        self._en_passant_target: Optional[Square] = None
        self._en_passant_pawn: Optional[Piece] = None
        
        # Điểm cơ bản của quân cờ
        self._piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0
        }

    # === PHẦN 1: QUẢN LÝ TRẠNG THÁI ===
    @property 
    def current_player(self) -> PieceColor:
        return self._current_player

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def is_game_over(self) -> bool:
        return self._state in (GameState.CHECKMATE, GameState.STALEMATE, GameState.DRAW)

    def _update_game_state(self) -> None:
        """Cập nhật trạng thái game sau mỗi nước đi"""
        if self._is_checkmate():
            self._state = GameState.CHECKMATE
        elif self._is_stalemate():
            self._state = GameState.STALEMATE
        elif self._is_draw():
            self._state = GameState.DRAW
        elif self._is_check():
            self._state = GameState.CHECK
        else:
            self._state = GameState.ACTIVE

    # === PHẦN 2: XỬ LÝ NƯỚC ĐI ===
    def make_move(self, move: Move) -> bool:
        """Thực hiện nước đi"""
        if not self.is_valid_move(move):
            return False

        # Cập nhật bộ đếm
        self._move_count += 1
        if isinstance(move.moving_piece, Pawn) or move.is_capture:
            self._fifty_move_counter = 0
        else:
            self._fifty_move_counter += 1

        # Lưu trạng thái trước khi di chuyển
        self._position_history.append(self._get_board_state())
        
        # Cập nhật en passant
        self.update_en_passant(move)

        # Thực hiện nước đi
        if self._board.make_move(move):
            self._last_move = move
            self._move_history.append(move)
            self._current_player = self._current_player.opposite
            self._update_game_state()
            return True

        return False

    def undo_move(self) -> Optional[Move]:
        """Hoàn tác nước đi cuối cùng"""
        if not self._move_history:
            return None

        last_move = self._move_history.pop()
        self._position_history.pop()
        
        if self._board.undo_move():
            self._current_player = self._current_player.opposite
            self._move_count -= 1
            self._last_move = self._move_history[-1] if self._move_history else None
            self._update_game_state()
            return last_move

        return None

    # === PHẦN 3: KIỂM TRA LUẬT ===
    def is_valid_move(self, move: Move) -> bool:
        """Kiểm tra nước đi có hợp lệ"""
        if not move.moving_piece or move.moving_piece.color != self._current_player:
            return False

        # Kiểm tra en passant
        if move.is_en_passant and not self.can_en_passant(
            move.moving_piece, 
            move.end_square
        ):
            return False

        # Kiểm tra nhập thành
        if move.is_castle and not self._is_castle_legal(move):
            return False

        # Kiểm tra nước đi cơ bản
        if not move.moving_piece.can_move_to(move.end_square, self._board):
            return False

        # Kiểm tra chiếu
        if self._causes_self_check(move):
            return False

        return True

    def get_legal_moves(self, piece: Piece) -> List[Move]:
        """Lấy tất cả nước đi hợp lệ của một quân"""
        legal_moves = []
        possible_moves = piece.get_possible_moves(self._board)

        for move in possible_moves:
            if self.is_valid_move(move):
                legal_moves.append(move)

        return legal_moves

    # === PHẦN 4: XỬ LÝ EN PASSANT ===
    def update_en_passant(self, move: Move) -> None:
        """Cập nhật trạng thái en passant"""
        self._en_passant_target = None
        self._en_passant_pawn = None

        if isinstance(move.moving_piece, Pawn):
            if abs(move.end_square.row - move.start_square.row) == 2:
                self._en_passant_pawn = move.moving_piece
                mid_row = (move.start_square.row + move.end_square.row) // 2
                self._en_passant_target = self._board.get_square(
                    mid_row,
                    move.end_square.col
                )

    def can_en_passant(self, pawn: Piece, target: Square) -> bool:
        """Kiểm tra khả năng bắt tốt qua đường"""
        return (self._en_passant_target == target and
                self._en_passant_pawn is not None and
                self._en_passant_pawn.color != pawn.color)

    # === PHẦN 5: TÍNH ĐIỂM VỊ TRÍ ===
    def get_position_value(self, piece: Piece) -> float:
        """Tính điểm vị trí của quân cờ"""
        base_value = self._piece_values[piece.piece_type]
        position_bonus = self._calculate_position_bonus(piece)
        mobility_bonus = self._calculate_mobility_bonus(piece)
        return base_value + position_bonus + mobility_bonus

    def _calculate_position_bonus(self, piece: Piece) -> float:
        """Tính điểm thưởng vị trí"""
        methods = {
            PieceType.PAWN: self._get_pawn_bonus,
            PieceType.KNIGHT: self._get_knight_bonus,
            PieceType.BISHOP: self._get_bishop_bonus,
            PieceType.ROOK: self._get_rook_bonus,
            PieceType.KING: self._get_king_bonus
        }
        return methods.get(piece.piece_type, lambda x: 0.0)(piece)

    # === PHẦN 6: KIỂM TRA TRẠNG THÁI ===
    def _is_check(self) -> bool:
        """Kiểm tra vua có đang bị chiếu"""
        king = self._board.get_king(self._current_player)
        return king and self._is_square_attacked(king.position, self._current_player.opposite)

    def _is_checkmate(self) -> bool:
        """Kiểm tra chiếu hết"""
        return self._is_check() and self._has_no_legal_moves()

    def _is_stalemate(self) -> bool:
        """Kiểm tra hết nước đi"""
        return not self._is_check() and self._has_no_legal_moves()

    def _is_draw(self) -> bool:
        """Kiểm tra điều kiện hòa"""
        return (self._fifty_move_counter >= 50 or
                self._is_insufficient_material() or
                self._is_threefold_repetition())

    def _is_insufficient_material(self) -> bool:
        """Kiểm tra không đủ quân chiếu hết"""
        white_pieces = self._board.get_pieces(PieceColor.WHITE)
        black_pieces = self._board.get_pieces(PieceColor.BLACK)

        # Kiểm tra các trường hợp hòa cơ bản
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True  # Vua đối vua

        if (len(white_pieces) == 2 and len(black_pieces) == 1 or
            len(white_pieces) == 1 and len(black_pieces) == 2):
            # Vua + (tượng/mã) đối vua
            for piece in white_pieces + black_pieces:
                if isinstance(piece, (Bishop, Knight)):
                    return True

        return False

    def __str__(self) -> str:
        return (f"Game State: {self._state.value}\n"
                f"Current Player: {self._current_player.value}\n"
                f"Move Count: {self._move_count}")