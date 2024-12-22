import random
from typing import List, Tuple, Optional
from enum import Enum
from copy import deepcopy
import math
from core.board import Board
from core.move import Move
from core.pieces.piece import Piece, PieceColor

class Difficulty(Enum):
    EASY = 1    # Random
    MEDIUM = 2  # Negamax
    HARD = 3    # MCTS

class ChessAI:
    """
    Class đại diện cho AI trong game cờ vua
    Attributes:
        _color: Màu quân của AI
        _difficulty: Độ khó của AI
        _piece_values: Giá trị của từng loại quân
    """
    def __init__(self, color: PieceColor, difficulty: Difficulty = Difficulty.MEDIUM):
        self._color = color
        self._difficulty = difficulty
        self._piece_values = {
            'PAWN': 100,
            'KNIGHT': 320,
            'BISHOP': 330,
            'ROOK': 500,
            'QUEEN': 900,
            'KING': 20000
        }

    # Mức độ 1: Random Move
    def _get_random_move(self, board: Board, valid_moves: List[Move]) -> Optional[Move]:
        """
        Chọn ngẫu nhiên một nước đi từ danh sách nước đi hợp lệ
        """
        if valid_moves:
            return random.choice(valid_moves)
        return None

    # Mức độ 2: Negamax Algorithm
    def _negamax(self, board: Board, depth: int, alpha: float, beta: float, color: int) -> Tuple[float, Optional[Move]]:
        """
        Thuật toán Negamax với alpha-beta pruning
        Args:
            board: Trạng thái bàn cờ
            depth: Độ sâu tìm kiếm
            alpha: Alpha value cho pruning
            beta: Beta value cho pruning
            color: 1 cho AI, -1 cho đối thủ
        Returns:
            Tuple(giá trị đánh giá, nước đi tốt nhất)
        """
        if depth == 0:
            return self._evaluate_position(board) * color, None

        best_value = float('-inf')
        best_move = None
        valid_moves = self._get_valid_moves(board)

        for move in valid_moves:
            new_board = deepcopy(board)
            new_board.make_move(move)
            
            value, _ = self._negamax(new_board, depth - 1, -beta, -alpha, -color)
            value = -value

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best_value, best_move

    # Mức độ 3: Monte Carlo Tree Search
    class MCTSNode:
        """Node cho MCTS"""
        def __init__(self, board: Board, move: Optional[Move] = None, parent=None):
            self.board = board
            self.move = move
            self.parent = parent
            self.children = []
            self.wins = 0
            self.visits = 0
            self.untried_moves = self._get_valid_moves(board)

        def uct_value(self, c_param=1.414):
            if self.visits == 0:
                return float('inf')
            return (self.wins / self.visits) + c_param * math.sqrt(math.log(self.parent.visits) / self.visits)

    def _mcts(self, board: Board, iterations: int = 1000) -> Move:
        """
        Monte Carlo Tree Search algorithm
        Args:
            board: Trạng thái bàn cờ
            iterations: Số lần lặp MCTS
        Returns:
            Nước đi tốt nhất
        """
        root = self.MCTSNode(board)

        for _ in range(iterations):
            node = root
            temp_board = deepcopy(board)

            # Selection
            while node.untried_moves == [] and node.children != []:
                node = self._select_uct(node)
                temp_board.make_move(node.move)

            # Expansion
            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                temp_board.make_move(move)
                node = self._add_child(node, move, temp_board)

            # Simulation
            result = self._simulate(temp_board)

            # Backpropagation
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent

        # Chọn nước đi tốt nhất
        return max(root.children, key=lambda c: c.visits).move

    def _evaluate_position(self, board: Board) -> float:
        """
        Đánh giá vị trí hiện tại của bàn cờ
        Returns:
            Giá trị đánh giá (càng cao càng tốt cho AI)
        """
        score = 0
        for piece in board.get_all_pieces():
            value = self._piece_values.get(piece.piece_type, 0)
            if piece.color == self._color:
                score += value
            else:
                score -= value
        return score

    def get_best_move(self, board: Board, valid_moves: List[Move]) -> Optional[Move]:
        """
        Lấy nước đi tốt nhất dựa trên độ khó
        """
        if not valid_moves:
            return None

        if self._difficulty == Difficulty.EASY:
            return self._get_random_move(board, valid_moves)
        
        elif self._difficulty == Difficulty.MEDIUM:
            depth = 3  # Độ sâu tìm kiếm cho Negamax
            _, best_move = self._negamax(board, depth, float('-inf'), float('inf'), 1)
            return best_move
        
        else:  # HARD
            return self._mcts(board)

    def set_difficulty(self, difficulty: Difficulty) -> None:
        """Thay đổi độ khó của AI"""
        self._difficulty = difficulty

    @property
    def color(self) -> PieceColor:
        """Lấy màu quân của AI"""
        return self._color

    @property
    def difficulty(self) -> Difficulty:
        """Lấy độ khó hiện tại của AI"""
        return self._difficulty