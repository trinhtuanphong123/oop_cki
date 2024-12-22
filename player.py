from enum import Enum
from typing import List
from core.pieces.piece import Piece
from core.move import Move

class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"

class Player:
    """
    Class đại diện cho người chơi cờ vua
    Attributes:
        _color: Màu quân của người chơi (trắng/đen)
        _is_human: True nếu là người thật, False nếu là AI
        _captured_pieces: Danh sách quân đã bắt được
        _score: Điểm số của người chơi
        _is_in_check: Trạng thái có đang bị chiếu không
    """
    def __init__(self, color: PieceColor, is_human: bool = True):
        # Thuộc tính private
        self._color = color
        self._is_human = is_human
        self._captured_pieces = []
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

    # Getters
    @property
    def color(self) -> PieceColor:
        """Lấy màu quân của người chơi"""
        return self._color

    @property
    def is_human(self) -> bool:
        """Kiểm tra có phải người thật không"""
        return self._is_human

    @property
    def score(self) -> int:
        """Lấy điểm số hiện tại"""
        return self._score

    @property
    def is_in_check(self) -> bool:
        """Kiểm tra có đang bị chiếu không"""
        return self._is_in_check

    @property
    def captured_pieces(self) -> List[Piece]:
        """Lấy danh sách quân đã bắt được"""
        return self._captured_pieces.copy()  # Trả về bản sao để bảo vệ dữ liệu

    # Setters
    def set_in_check(self, value: bool) -> None:
        """Cập nhật trạng thái bị chiếu"""
        self._is_in_check = value

    # Methods
    def add_captured_piece(self, piece: Piece) -> None:
        """
        Thêm quân cờ bị bắt vào danh sách
        Args:
            piece: Quân cờ bị bắt
        """
        if piece:
            self._captured_pieces.append(piece)
            self._update_score(piece)

    def _update_score(self, captured_piece: Piece) -> None:
        """
        Cập nhật điểm dựa trên quân cờ bắt được
        Args:
            captured_piece: Quân cờ bị bắt
        """
        piece_type = captured_piece.piece_type.upper()
        self._score += self._piece_values.get(piece_type, 0)

    def get_captured_pieces_count(self) -> dict:
        """
        Đếm số lượng từng loại quân đã bắt
        Returns:
            Dict với key là loại quân và value là số lượng
        """
        counts = {}
        for piece in self._captured_pieces:
            piece_type = piece.piece_type
            counts[piece_type] = counts.get(piece_type, 0) + 1
        return counts

    def handle_move_result(self, move: Move) -> None:
        """
        Xử lý kết quả sau một nước đi
        Args:
            move: Nước đi vừa thực hiện
        """
        if move.is_capture:
            self.add_captured_piece(move.captured_piece)

    def reset_stats(self) -> None:
        """Reset thống kê của người chơi khi bắt đầu ván mới"""
        self._captured_pieces.clear()
        self._score = 0
        self._is_in_check = False

    def __str__(self) -> str:
        """Biểu diễn string của người chơi"""
        player_type = "Human" if self._is_human else "AI"
        return f"{player_type} Player ({self._color.value}), Score: {self._score}"