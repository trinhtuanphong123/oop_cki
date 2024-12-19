from .player import Player
from core.board import Board
from core.move import Move
import random

class AIStrategy:
    """
    Lớp trừu tượng đại diện cho chiến lược AI.
    """
    def calculate_move(self, board: 'Board', color: str) -> 'Move':
        raise NotImplementedError("Phương thức này phải được triển khai trong các lớp con.")

class RandomStrategy(AIStrategy):
    """
    Chiến lược ngẫu nhiên (dành cho AI dễ).
    """
    def calculate_move(self, board: 'Board', color: str) -> 'Move':
        possible_moves = []
        for piece in board.get_all_pieces():
            if piece.color == color:
                for move in piece.get_legal_moves(board):
                    start_square = piece.position
                    end_square = board.get_square(*move)
                    possible_moves.append(Move(start_square, end_square, piece))
        
        if possible_moves:
            return random.choice(possible_moves)
        return None

class NegamaxStrategy(AIStrategy):
    """
    Chiến lược sử dụng thuật toán Negamax Alpha-Beta.
    """
    def __init__(self, depth: int):
        self.depth = depth

    def calculate_move(self, board: 'Board', color: str) -> 'Move':
        _, best_move = self.negamax_alphabeta(board, self.depth, -float('inf'), float('inf'), True, color)
        return best_move

    def negamax_alphabeta(self, board: 'Board', depth: int, alpha: float, beta: float, is_max_player: bool, color: str) -> tuple:
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board, color), None
        
        max_eval = -float('inf')
        best_move = None
        
        possible_moves = []
        for piece in board.get_all_pieces():
            if piece.color == color:
                for move in piece.get_legal_moves(board):
                    start_square = piece.position
                    end_square = board.get_square(*move)
                    possible_moves.append(Move(start_square, end_square, piece))
        
        for move in possible_moves:
            board.move_piece(move.start_square, move.end_square)
            eval, _ = self.negamax_alphabeta(board, depth - 1, -beta, -alpha, not is_max_player, color)
            eval = -eval
            board.undo_move()
            
            if eval > max_eval:
                max_eval = eval
                best_move = move
            
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        
        return max_eval, best_move

    def evaluate_board(self, board: 'Board', color: str) -> int:
        """
        Đánh giá bàn cờ dựa trên giá trị của các quân cờ.
        """
        value = 0
        piece_values = {'Pawn': 1, 'Knight': 3, 'Bishop': 3, 'Rook': 5, 'Queen': 9, 'King': 1000}
        
        for piece in board.get_all_pieces():
            if piece.color == color:
                value += piece_values.get(piece.__class__.__name__, 0)
            else:
                value -= piece_values.get(piece.__class__.__name__, 0)
        
        return value


class AI(Player):
    """
    Lớp đại diện cho AI trong trò chơi cờ vua.
    """
    _instances = {}

    def __new__(cls, color: str, difficulty: str):
        if (color, difficulty) not in cls._instances:
            cls._instances[(color, difficulty)] = super(AI, cls).__new__(cls)
        return cls._instances[(color, difficulty)]

    def __init__(self, color: str, difficulty: str):
        """
        Khởi tạo AI với màu của quân cờ và độ khó của AI.
        
        Args:
            color (str): Màu của quân cờ mà AI điều khiển ('white' hoặc 'black').
            difficulty (str): Độ khó của AI ('easy', 'medium', 'hard').
        """
        super().__init__("AI", color)
        self.difficulty = difficulty
        self.strategy = self.set_strategy(difficulty)

    def set_strategy(self, difficulty: str) -> AIStrategy:
        """
        Chọn chiến lược AI tùy thuộc vào độ khó.
        
        Args:
            difficulty (str): Độ khó của AI.
        
        Returns:
            AIStrategy: Chiến lược AI.
        """
        if difficulty == 'easy':
            return RandomStrategy()
        elif difficulty == 'medium':
            return NegamaxStrategy(depth=3)
        elif difficulty == 'hard':
            return NegamaxStrategy(depth=5)
        else:
            raise ValueError("Độ khó không hợp lệ. Vui lòng chọn 'easy', 'medium' hoặc 'hard'.")

    def calculate_best_move(self, board: 'Board') -> 'Move':
        """
        Tính toán nước đi tốt nhất dựa trên chiến lược AI.
        
        Args:
            board (Board): Bàn cờ hiện tại.
        
        Returns:
            Move: Nước đi tốt nhất mà AI có thể thực hiện.
        """
        return self.strategy.calculate_move(board)

    def __str__(self):
        return f"AI({self.color}, {self.difficulty})"

    def __repr__(self):
        return self.__str__()
