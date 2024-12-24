from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict
from core.pieces.piece import Piece
from core.move import Move
from core.game_rule import GameRule
from core.game_state import GameState
from core.board import Board

class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"

class Player(ABC):
    """
    Class cơ sở cho người chơi cờ vua
    Attributes:
        _name: Tên người chơi
        _color: Màu quân của người chơi (trắng/đen)
        _is_human: True nếu là người thật, False nếu là AI
        _captured_pieces: Danh sách quân đã bắt được
        _score: Điểm số của người chơi
        _is_in_check: Trạng thái có đang bị chiếu không
        _moves_made: Lịch sử các nước đã đi
    """
    def __init__(self, name: str, color: PieceColor, is_human: bool = True):
        # Thuộc tính cơ bản
        self._name = name
        self._color = color
        self._is_human = is_human
        
        # Thống kê và trạng thái
        self._captured_pieces: List[Piece] = []
        self._moves_made: List[Move] = []
        self._score = 0
        self._is_in_check = False

        # Giá trị điểm của từng loại quân
        self._piece_values = {
            'PAWN': 1,
            'KNIGHT': 3,
            'BISHOP': 3,
            'ROOK': 5,
            'QUEEN': 9,
            'KING': 0
        }

    # === PROPERTIES ===
    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> PieceColor:
        return self._color

    @property
    def is_human(self) -> bool:
        return self._is_human

    @property
    def score(self) -> int:
        return self._score

    @property
    def is_in_check(self) -> bool:
        return self._is_in_check

    @property
    def captured_pieces(self) -> List[Piece]:
        return self._captured_pieces.copy()

    @property
    def moves_made(self) -> List[Move]:
        return self._moves_made.copy()

    # === ABSTRACT METHODS ===
    @abstractmethod
    def get_move(self, game_state: GameState) -> Optional[Move]:
        """
        Lấy nước đi từ người chơi
        Args:
            game_state: Trạng thái hiện tại của game
        Returns:
            Nước đi được chọn hoặc None nếu không có nước đi hợp lệ
        """
        pass

    # === PUBLIC METHODS ===
    def add_move(self, move: Move) -> None:
        """Thêm nước đi vào lịch sử"""
        self._moves_made.append(move)
        self.handle_move_result(move)

    def handle_move_result(self, move: Move) -> None:
        """Xử lý kết quả sau một nước đi"""
        if move.is_capture:
            self.add_captured_piece(move.captured_piece)

    def add_captured_piece(self, piece: Piece) -> None:
        """Thêm quân cờ bị bắt và cập nhật điểm"""
        if piece:
            self._captured_pieces.append(piece)
            self._update_score(piece)

    def get_pieces(self, board: Board) -> List[Piece]:
        """Lấy danh sách quân cờ của người chơi"""
        return board.get_pieces(self._color)

    def can_move(self, game_state: GameState) -> bool:
        """Kiểm tra còn nước đi hợp lệ không"""
        for piece in self.get_pieces(game_state.board):
            if game_state.get_legal_moves(piece):
                return True
        return False

    def get_captured_pieces_count(self) -> Dict[str, int]:
        """Đếm số lượng từng loại quân đã bắt"""
        counts = {}
        for piece in self._captured_pieces:
            piece_type = piece.piece_type
            counts[piece_type] = counts.get(piece_type, 0) + 1
        return counts

    def set_in_check(self, value: bool) -> None:
        """Cập nhật trạng thái bị chiếu"""
        self._is_in_check = value

    def reset(self) -> None:
        """Reset trạng thái người chơi"""
        self._captured_pieces.clear()
        self._moves_made.clear()
        self._score = 0
        self._is_in_check = False

    # === PRIVATE METHODS ===
    def _update_score(self, captured_piece: Piece) -> None:
        """Cập nhật điểm dựa trên quân cờ bắt được"""
        piece_type = captured_piece.piece_type.upper()
        self._score += self._piece_values.get(piece_type, 0)

    # === MAGIC METHODS ===
    def __str__(self) -> str:
        player_type = "Human" if self._is_human else "AI"
        return f"{self._name} - {player_type} ({self._color.value}), Score: {self._score}"

    def __repr__(self) -> str:
        return f"Player(name='{self._name}', color={self._color}, is_human={self._is_human})"