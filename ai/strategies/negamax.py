# ai/strategies/negamax.py

import time
from typing import Optional, Tuple, List
from strategies import AIStrategy
from ...core.move import Move
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor, Piece

class NegamaxStrategy(AIStrategy):
    """
    Chiến thuật sử dụng thuật toán Negamax với cắt tỉa Alpha-Beta
    Negamax là một biến thể của Minimax, tận dụng tính đối xứng của việc đánh giá vị trí
    """

    def __init__(self):
        """Khởi tạo chiến thuật Negamax"""
        # Điểm số cho các trạng thái đặc biệt
        self.CHECKMATE_SCORE = 100000
        self.STALEMATE_SCORE = 0
        self.start_time = 0
        self.nodes_searched = 0

    def find_best_move(self, game_state: GameState, time_limit: float, depth: int) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất sử dụng thuật toán Negamax
        Args:
            game_state: Trạng thái hiện tại của game
            time_limit: Thời gian tối đa cho phép suy nghĩ (giây)
            depth: Độ sâu tìm kiếm tối đa
        Returns:
            Nước đi tốt nhất tìm được
        """
        self.start_time = time.time()
        self.nodes_searched = 0
        
        # Khởi tạo các giá trị
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Lấy tất cả nước đi hợp lệ và sắp xếp theo độ ưu tiên
        legal_moves = self._sort_moves(self._get_legal_moves(game_state), game_state)
        
        # Iterative deepening: tăng dần độ sâu tìm kiếm
        for current_depth in range(1, depth + 1):
            if time.time() - self.start_time >= time_limit:
                break
                
            current_best_move = None
            current_best_score = float('-inf')
            
            # Thử từng nước đi
            for move in legal_moves:
                if time.time() - self.start_time >= time_limit:
                    break
                    
                # Thực hiện nước đi
                game_state.make_move(move)
                
                # Tìm kiếm đệ quy với độ sâu giảm dần
                score = -self._negamax(game_state, current_depth - 1, -beta, -alpha)
                
                # Hoàn tác nước đi
                game_state.undo_last_move()
                
                # Cập nhật nước đi tốt nhất
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
                    
                alpha = max(alpha, score)
                
            # Cập nhật kết quả tốt nhất tổng thể
            if current_best_score > best_score:
                best_score = current_best_score
                best_move = current_best_move
                
        return best_move

    def _negamax(self, game_state: GameState, depth: int, alpha: float, beta: float) -> float:
        """
        Thuật toán Negamax với cắt tỉa Alpha-Beta
        Args:
            game_state: Trạng thái game hiện tại
            depth: Độ sâu còn lại cần tìm kiếm
            alpha: Giá trị alpha cho cắt tỉa
            beta: Giá trị beta cho cắt tỉa
        Returns:
            Điểm đánh giá tốt nhất cho vị trí
        """
        self.nodes_searched += 1
        
        # Kiểm tra thời gian
        if time.time() - self.start_time >= self.time_limit:
            return 0
            
        # Đạt độ sâu 0 hoặc kết thúc game -> đánh giá vị trí
        if depth == 0 or game_state.is_game_over:
            return self._evaluate_position_with_conditions(game_state)
            
        legal_moves = self._sort_moves(self._get_legal_moves(game_state), game_state)
        
        # Nếu không có nước đi hợp lệ
        if not legal_moves:
            if game_state.is_check():
                return -self.CHECKMATE_SCORE
            return self.STALEMATE_SCORE
            
        max_score = float('-inf')
        
        # Thử từng nước đi
        for move in legal_moves:
            game_state.make_move(move)
            score = -self._negamax(game_state, depth - 1, -beta, -alpha)
            game_state.undo_last_move()
            
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            
            # Cắt tỉa Alpha-Beta
            if alpha >= beta:
                break
                
        return max_score

    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí hiện tại
        Args:
            game_state: Trạng thái cần đánh giá
        Returns:
            Điểm đánh giá vị trí
        """
        # Kiểm tra các trường hợp đặc biệt
        if game_state.is_checkmate():
            return -self.CHECKMATE_SCORE if game_state.current_player else self.CHECKMATE_SCORE
            
        if game_state.is_stalemate():
            return self.STALEMATE_SCORE
            
        # Đánh giá vị trí thông thường
        evaluation = 0
        is_endgame = self._is_endgame(game_state)
        
        # Đánh giá material
        evaluation += self._evaluate_material(game_state)
        
        # Đánh giá vị trí quân cờ
        evaluation += self._evaluate_piece_positions(game_state)
        
        # Đánh giá khả năng di chuyển
        evaluation += self._evaluate_piece_mobility(game_state)
        
        # Đánh giá bảo vệ vua trong giai đoạn đầu/giữa
        if not is_endgame:
            evaluation += self._evaluate_king_safety(game_state)
            
        # Đánh giá cấu trúc tốt
        evaluation += self._evaluate_pawn_structure(game_state)
        
        # Đổi dấu nếu đến lượt đen
        return evaluation if game_state.current_player == PieceColor.WHITE else -evaluation

    def _evaluate_king_safety(self, game_state: GameState) -> float:
        """
        Đánh giá độ an toàn của vua
        Args:
            game_state: Trạng thái game
        Returns:
            Điểm đánh giá độ an toàn của vua
        """
        score = 0
        
        for color in [PieceColor.WHITE, PieceColor.BLACK]:
            king = game_state.board.get_king(color)
            if not king:
                continue
                
            # Kiểm tra nhập thành
            if game_state.has_castled(color):
                score += 60 if color == PieceColor.WHITE else -60
                
            # Kiểm tra bảo vệ vua
            king_protectors = self._count_king_protectors(game_state, king)
            score += king_protectors * 10 if color == PieceColor.WHITE else -king_protectors * 10
            
        return score

    def _count_king_protectors(self, game_state: GameState, king: 'Piece') -> int:
        """
        Đếm số quân bảo vệ xung quanh vua
        Args:
            game_state: Trạng thái game
            king: Quân vua cần kiểm tra
        Returns:
            Số quân bảo vệ
        """
        protectors = 0
        king_row, king_col = king.position.row, king.position.col
        
        # Kiểm tra 8 ô xung quanh vua
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue
                    
                target_row = king_row + row_offset
                target_col = king_col + col_offset
                
                if game_state.board.is_valid_position(target_row, target_col):
                    piece = game_state.board.get_piece_at(target_row, target_col)
                    if piece and piece.color == king.color:
                        protectors += 1
                        
        return protectors

    def __str__(self) -> str:
        return "Negamax Strategy"

    def __repr__(self) -> str:
        return f"NegamaxStrategy(nodes_searched={self.nodes_searched})"