# ai/evaluation/evaluator.py

from typing import Dict, List
from ...core.board import Board
from ...core.pieces.piece import Piece, PieceColor, PieceType
from ...core.game_state import GameState

class PositionEvaluator:
    """
    Class đánh giá vị trí trên bàn cờ.
    Cung cấp các phương thức đánh giá khác nhau cho AI.
    """
    
    def evaluate_material(self, board: Board, piece_values: Dict[PieceType, int]) -> float:
        """
        Đánh giá dựa trên giá trị quân cờ
        Args:
            board: Bàn cờ hiện tại
            piece_values: Giá trị của từng loại quân
        Returns:
            Điểm đánh giá (dương = lợi thế trắng, âm = lợi thế đen)
        """
        score = 0.0
        for piece in board.get_all_pieces():
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == PieceColor.WHITE:
                score += value
            else:
                score -= value
        return score

    def evaluate_positions(self, board: Board, position_tables: Dict[PieceType, List[List[int]]]) -> float:
        """
        Đánh giá vị trí các quân cờ
        Args:
            board: Bàn cờ hiện tại
            position_tables: Bảng giá trị vị trí cho từng loại quân
        Returns:
            Điểm đánh giá vị trí
        """
        score = 0.0
        for piece in board.get_all_pieces():
            if piece.piece_type in position_tables:
                table = position_tables[piece.piece_type]
                row = piece.position.row
                col = piece.position.col
                
                # Đảo bảng cho quân đen
                if piece.color == PieceColor.BLACK:
                    row = 7 - row
                    
                value = table[row][col]
                if piece.color == PieceColor.WHITE:
                    score += value
                else:
                    score -= value
        return score

    def evaluate_pawn_structure(self, board: Board) -> float:
        """
        Đánh giá cấu trúc tốt
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Điểm đánh giá cấu trúc tốt
        """
        score = 0.0
        
        # Đánh giá tốt đôi và tốt cô lập
        for color in [PieceColor.WHITE, PieceColor.BLACK]:
            multiplier = 1 if color == PieceColor.WHITE else -1
            
            # Đếm tốt đôi và tốt cô lập
            doubled = self._count_doubled_pawns(board, color)
            isolated = self._count_isolated_pawns(board, color)
            
            score += multiplier * (-20 * isolated - 10 * doubled)
            
        return score

    def evaluate_center_control(self, board: Board) -> float:
        """
        Đánh giá kiểm soát trung tâm
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Điểm đánh giá kiểm soát trung tâm
        """
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        score = 0.0
        
        for row, col in center_squares:
            piece = board.get_piece_at(row, col)
            if piece:
                value = 10
                if piece.color == PieceColor.WHITE:
                    score += value
                else:
                    score -= value
                    
        return score

    def evaluate_king_safety(self, board: Board) -> float:
        """
        Đánh giá an toàn của vua
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Điểm đánh giá an toàn của vua
        """
        score = 0.0
        for color in [PieceColor.WHITE, PieceColor.BLACK]:
            king = board.get_king(color)
            if king:
                # Đánh giá dựa trên vị trí của vua
                is_endgame = len(board.get_all_pieces()) <= 12
                if not is_endgame:
                    # Trong tàn cuộc, vua nên tích cực hơn
                    if color == PieceColor.WHITE:
                        score -= self._evaluate_king_position(king)
                    else:
                        score += self._evaluate_king_position(king)
        return score

    def evaluate_mobility(self, game_state: GameState) -> float:
        """
        Đánh giá khả năng di chuyển
        Args:
            game_state: Trạng thái game hiện tại
        Returns:
            Điểm đánh giá khả năng di chuyển
        """
        white_moves = len(game_state.get_legal_moves(PieceColor.WHITE))
        black_moves = len(game_state.get_legal_moves(PieceColor.BLACK))
        return (white_moves - black_moves) * 0.1

    def _count_doubled_pawns(self, board: Board, color: PieceColor) -> int:
        """Đếm số tốt đôi"""
        doubled = 0
        for col in range(8):
            pawns_in_col = 0
            for row in range(8):
                piece = board.get_piece_at(row, col)
                if piece and piece.piece_type == PieceType.PAWN and piece.color == color:
                    pawns_in_col += 1
            if pawns_in_col > 1:
                doubled += pawns_in_col - 1
        return doubled

    def _count_isolated_pawns(self, board: Board, color: PieceColor) -> int:
        """Đếm số tốt cô lập"""
        isolated = 0
        for col in range(8):
            has_pawns = False
            has_neighbors = False
            
            # Kiểm tra cột hiện tại
            for row in range(8):
                piece = board.get_piece_at(row, col)
                if piece and piece.piece_type == PieceType.PAWN and piece.color == color:
                    has_pawns = True
                    break
                    
            # Kiểm tra cột bên cạnh
            if has_pawns:
                for adj_col in [col-1, col+1]:
                    if 0 <= adj_col < 8:
                        for row in range(8):
                            piece = board.get_piece_at(row, adj_col)
                            if piece and piece.piece_type == PieceType.PAWN and piece.color == color:
                                has_neighbors = True
                                break
                if not has_neighbors:
                    isolated += 1
                    
        return isolated

    def _evaluate_king_position(self, king: Piece) -> float:
        """Đánh giá vị trí của vua"""
        row, col = king.position.row, king.position.col
        
        # Khuyến khích vua ở gần góc trong giai đoạn đầu
        corner_distance = min(
            abs(row - 0) + abs(col - 0),
            abs(row - 0) + abs(col - 7),
            abs(row - 7) + abs(col - 0),
            abs(row - 7) + abs(col - 7)
        )
        
        return corner_distance * 2