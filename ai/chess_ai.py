# ai/chess_ai.py

from typing import Optional, List, Dict, Tuple
from ..core.move import Move
from ..core.game_rule import GameState
from ..core.pieces.piece import Piece, PieceColor, PieceType
from ..core.board import Board
from .strategies import AIStrategy

class ChessAI:
    """
    Class cơ sở cho AI cờ vua
    Cung cấp các chức năng cơ bản và interface cho các chiến thuật AI
    """
    def __init__(self, strategy: AIStrategy):
        """
        Khởi tạo AI với chiến thuật cụ thể
        Args:
            strategy: Chiến thuật AI được sử dụng
        """
        self._strategy = strategy
        self._depth = 3  # Độ sâu tìm kiếm mặc định
        
        # Giá trị cơ bản của các quân cờ
        self._piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }

        # Bảng giá trị vị trí cho từng loại quân
        self._position_values = self._init_position_tables()

    def get_best_move(self, game_state: GameState, thinking_time: float) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất trong thời gian cho phép
        Args:
            game_state: Trạng thái hiện tại của game
            thinking_time: Thời gian suy nghĩ tối đa (giây)
        Returns:
            Nước đi tốt nhất tìm được
        """
        return self._strategy.find_best_move(game_state, thinking_time, self._depth)

    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí hiện tại
        Args:
            game_state: Trạng thái game cần đánh giá
        Returns:
            Điểm số đánh giá vị trí (dương = có lợi cho trắng, âm = có lợi cho đen)
        """
        board = game_state.board
        evaluation = 0.0

        # Đánh giá material (quân cờ)
        material_score = self._evaluate_material(board)
        
        # Đánh giá vị trí các quân
        position_score = self._evaluate_piece_positions(board)
        
        # Đánh giá cấu trúc tốt
        pawn_structure_score = self._evaluate_pawn_structure(board)
        
        # Đánh giá kiểm soát trung tâm
        center_control_score = self._evaluate_center_control(board)
        
        # Tổng hợp điểm với các trọng số
        evaluation = (
            material_score * 1.0 +
            position_score * 0.3 +
            pawn_structure_score * 0.2 +
            center_control_score * 0.1
        )

        # Đảo dấu nếu đang là lượt đen
        if game_state.current_player == PieceColor.BLACK:
            evaluation = -evaluation

        return evaluation

    def set_depth(self, depth: int) -> None:
        """Thiết lập độ sâu tìm kiếm"""
        if depth >= 1:
            self._depth = depth

    def set_strategy(self, strategy: AIStrategy) -> None:
        """Thay đổi chiến thuật AI"""
        self._strategy = strategy

    # === PRIVATE EVALUATION METHODS ===

    def _evaluate_material(self, board: Board) -> float:
        """Đánh giá giá trị quân cờ trên bàn"""
        score = 0.0
        for piece in board.get_all_pieces():
            value = self._piece_values[piece.piece_type]
            if piece.color == PieceColor.WHITE:
                score += value
            else:
                score -= value
        return score

    def _evaluate_piece_positions(self, board: Board) -> float:
        """Đánh giá vị trí các quân cờ"""
        score = 0.0
        for piece in board.get_all_pieces():
            position_value = self._get_position_value(piece)
            if piece.color == PieceColor.WHITE:
                score += position_value
            else:
                score -= position_value
        return score

    def _evaluate_pawn_structure(self, board: Board) -> float:
        """Đánh giá cấu trúc tốt"""
        score = 0.0
        
        # Kiểm tra tốt cô lập
        for color in [PieceColor.WHITE, PieceColor.BLACK]:
            isolated_pawns = self._count_isolated_pawns(board, color)
            doubled_pawns = self._count_doubled_pawns(board, color)
            
            multiplier = 1 if color == PieceColor.WHITE else -1
            score += multiplier * (-20 * isolated_pawns - 10 * doubled_pawns)
            
        return score

    def _evaluate_center_control(self, board: Board) -> float:
        """Đánh giá kiểm soát trung tâm"""
        score = 0.0
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        
        for row, col in center_squares:
            square = board.get_square(row, col)
            if square.piece:
                value = 10  # Giá trị cho việc chiếm giữ trung tâm
                if square.piece.color == PieceColor.WHITE:
                    score += value
                else:
                    score -= value
        return score

    def _get_position_value(self, piece: Piece) -> float:
        """Lấy giá trị vị trí của một quân cờ"""
        if piece.piece_type not in self._position_values:
            return 0.0
            
        position_table = self._position_values[piece.piece_type]
        row, col = piece.position.row, piece.position.col
        
        # Đảo bảng cho quân đen
        if piece.color == PieceColor.BLACK:
            row = 7 - row
            
        return position_table[row][col]

    def _init_position_tables(self) -> Dict[PieceType, List[List[float]]]:
        """Khởi tạo bảng giá trị vị trí cho các quân cờ"""
        tables = {}
        
        # Bảng giá trị vị trí cho tốt
        tables[PieceType.PAWN] = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        # Thêm các bảng giá trị cho các quân khác...
        # (Có thể thêm bảng giá trị chi tiết cho từng loại quân)
        
        return tables

    def _count_isolated_pawns(self, board: Board, color: PieceColor) -> int:
        """Đếm số tốt cô lập"""
        pawns = [p for p in board.get_pieces(color) if p.piece_type == PieceType.PAWN]
        isolated = 0
        
        for pawn in pawns:
            col = pawn.position.col
            has_neighbors = False
            
            # Kiểm tra các cột bên cạnh
            for adj_col in [col-1, col+1]:
                if 0 <= adj_col < 8:
                    for row in range(8):
                        square = board.get_square(row, adj_col)
                        if (square.piece and 
                            square.piece.piece_type == PieceType.PAWN and
                            square.piece.color == color):
                            has_neighbors = True
                            break
            
            if not has_neighbors:
                isolated += 1
                
        return isolated

    def _count_doubled_pawns(self, board: Board, color: PieceColor) -> int:
        """Đếm số tốt chồng"""
        doubled = 0
        for col in range(8):
            pawns_in_col = 0
            for row in range(8):
                square = board.get_square(row, col)
                if (square.piece and 
                    square.piece.piece_type == PieceType.PAWN and
                    square.piece.color == color):
                    pawns_in_col += 1
            if pawns_in_col > 1:
                doubled += pawns_in_col - 1
        return doubled