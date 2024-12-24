# ai/strategies/mcts.py

import math
import time
import random
from typing import Optional, List, Dict
from strategies import AIStrategy
from ...core.move import Move
from ...core.game_rule import GameRule
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor

class MCTSNode:
    """
    Node trong cây MCTS
    Lưu trữ thông tin về trạng thái game và thống kê
    """
    def __init__(self, game_state: GameState, parent=None, move: Optional[Move] = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move  # Nước đi dẫn đến node này
        self.children: List[MCTSNode] = []
        self.wins = 0  # Số ván thắng
        self.visits = 0  # Số lần thăm
        self.untried_moves = self._get_legal_moves()  # Các nước đi chưa thử

    def _get_legal_moves(self) -> List[Move]:
        """Lấy danh sách các nước đi hợp lệ"""
        return self._get_all_legal_moves(self.game_state)

    def _get_all_legal_moves(self, game_state: GameState) -> List[Move]:
        """Lấy tất cả nước đi hợp lệ cho trạng thái hiện tại"""
        legal_moves = []
        for piece in game_state.board.get_pieces(game_state.current_player):
            legal_moves.extend(game_state.get_legal_moves(piece))
        return legal_moves

    def get_ucb_score(self, exploration_constant: float) -> float:
        """
        Tính điểm UCB (Upper Confidence Bound) cho node
        Args:
            exploration_constant: Hệ số thăm dò (thường là √2)
        Returns:
            Điểm UCB của node
        """
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

class MCTSStrategy(AIStrategy):
    """
    Chiến thuật sử dụng Monte Carlo Tree Search
    MCTS kết hợp tìm kiếm cây với mô phỏng ngẫu nhiên
    """
    def __init__(self, exploration_constant: float = math.sqrt(2)):
        self.exploration_constant = exploration_constant
        self.root = None
        self.nodes_explored = 0

    def find_best_move(self, game_state: GameState, time_limit: float, depth: int) -> Optional[Move]:
        """
        Tìm nước đi tốt nhất sử dụng MCTS
        Args:
            game_state: Trạng thái hiện tại của game
            time_limit: Thời gian tối đa cho phép suy nghĩ
            depth: Độ sâu tối đa cho mô phỏng (không bắt buộc với MCTS)
        Returns:
            Nước đi tốt nhất tìm được
        """
        self.nodes_explored = 0
        start_time = time.time()
        self.root = MCTSNode(game_state)

        # Thực hiện MCTS cho đến khi hết thời gian
        while time.time() - start_time < time_limit:
            node = self._select(self.root)
            simulation_result = self._simulate(node.game_state)
            self._backpropagate(node, simulation_result)
            self.nodes_explored += 1

        # Chọn node con có số lần thăm nhiều nhất
        if not self.root.children:
            return None

        best_child = max(self.root.children, key=lambda c: c.visits)
        return best_child.move

    def _select(self, node: MCTSNode) -> MCTSNode:
        """
        Chọn node để mở rộng theo UCB
        Args:
            node: Node bắt đầu
        Returns:
            Node được chọn để mở rộng
        """
        while not node.game_state.is_game_over:
            if node.untried_moves:
                return self._expand(node)
            
            if not node.children:
                return node
                
            node = self._select_ucb(node)
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """
        Mở rộng node bằng cách thêm một node con mới
        Args:
            node: Node cần mở rộng
        Returns:
            Node con mới được tạo
        """
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)
        
        new_state = node.game_state.clone()
        new_state.make_move(move)
        
        child_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def _simulate(self, game_state: GameState) -> float:
        """
        Thực hiện mô phỏng từ trạng thái game
        Args:
            game_state: Trạng thái bắt đầu mô phỏng
        Returns:
            1.0 nếu thắng, 0.0 nếu thua, 0.5 nếu hòa
        """
        temp_state = game_state.clone()
        max_moves = 100  # Giới hạn số nước để tránh vòng lặp vô hạn
        
        while not temp_state.is_game_over and max_moves > 0:
            moves = self._get_legal_moves(temp_state)
            if not moves:
                break
            move = random.choice(moves)
            temp_state.make_move(move)
            max_moves -= 1

        # Đánh giá kết quả
        if temp_state.is_checkmate():
            return 1.0 if temp_state.current_player != game_state.current_player else 0.0
        return 0.5  # Hòa

    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        """
        Lan truyền kết quả ngược lên cây
        Args:
            node: Node bắt đầu lan truyền
            result: Kết quả mô phỏng
        """
        while node is not None:
            node.visits += 1
            node.wins += result
            result = 1 - result  # Đảo kết quả cho người chơi đối phương
            node = node.parent

    def _select_ucb(self, node: MCTSNode) -> MCTSNode:
        """
        Chọn node con tốt nhất theo công thức UCB
        Args:
            node: Node cha
        Returns:
            Node con được chọn
        """
        return max(node.children, key=lambda c: c.get_ucb_score(self.exploration_constant))

    def evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí dựa trên số liệu thống kê MCTS
        Args:
            game_state: Trạng thái cần đánh giá
        Returns:
            Điểm đánh giá vị trí
        """
        if self.root is None:
            return 0.0
            
        for child in self.root.children:
            if child.game_state == game_state:
                return child.wins / child.visits if child.visits > 0 else 0.0
                
        return 0.0

    def __str__(self) -> str:
        return f"MCTS Strategy (explored {self.nodes_explored} nodes)"

    def __repr__(self) -> str:
        return f"MCTSStrategy(exploration_constant={self.exploration_constant})"