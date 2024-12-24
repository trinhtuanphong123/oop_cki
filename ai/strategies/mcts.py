# ai/strategies/mcts.py

import math
import time
import random
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from .strategies import AIStrategy
from ...core.move import Move
from ...core.game_state import GameState
from ...core.pieces.piece import PieceColor

@dataclass
class MCTSStats:
    """Thống kê cho MCTS"""
    nodes_explored: int = 0
    max_depth: int = 0
    execution_time: float = 0
    total_simulations: int = 0

class MCTSNode:
    """Node trong cây MCTS"""
    def __init__(self, 
                 game_state: GameState, 
                 parent: Optional['MCTSNode'] = None,
                 move: Optional[Move] = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children: List['MCTSNode'] = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = self._get_legal_moves()
        self.depth = 0 if parent is None else parent.depth + 1

    def get_ucb_score(self, exploration_constant: float) -> float:
        """Tính điểm UCB"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration

    def _get_legal_moves(self) -> List[Move]:
        """Lấy danh sách nước đi hợp lệ"""
        return self.game_state.get_legal_moves()

class MCTSStrategy(AIStrategy):
    """Monte Carlo Tree Search strategy"""
    def __init__(self, exploration_constant: float = math.sqrt(2)):
        self.exploration_constant = exploration_constant
        self.stats = MCTSStats()
        self.root: Optional[MCTSNode] = None

    def find_best_move(self,
                       game_state: GameState,
                       time_limit: float,
                       depth: int,
                       evaluation_fn: Callable[[GameState], float]) -> Optional[Move]:
        """Tìm nước đi tốt nhất bằng MCTS"""
        # Reset statistics
        self.stats = MCTSStats()
        start_time = time.time()
        
        # Khởi tạo root node
        self.root = MCTSNode(game_state)

        # Chạy MCTS cho đến khi hết thời gian
        while time.time() - start_time < time_limit:
            node = self._select(self.root)
            if not node.game_state.is_game_over():
                node = self._expand(node)
            
            result = self._simulate(node, evaluation_fn)
            self._backpropagate(node, result)
            
            self.stats.nodes_explored += 1
            self.stats.max_depth = max(self.stats.max_depth, node.depth)
            self.stats.total_simulations += 1

        self.stats.execution_time = time.time() - start_time

        # Chọn nước đi tốt nhất
        return self._get_best_move()

    def analyze_position(self,
                        game_state: GameState,
                        depth: int,
                        time_limit: float) -> dict:
        """Phân tích vị trí hiện tại"""
        if self.root is None:
            return {"error": "No analysis available"}

        analysis = {
            "stats": {
                "nodes_explored": self.stats.nodes_explored,
                "max_depth": self.stats.max_depth,
                "execution_time": self.stats.execution_time,
                "total_simulations": self.stats.total_simulations
            },
            "best_moves": [],
            "position_evaluation": {}
        }

        # Thêm top 3 nước đi tốt nhất
        sorted_children = sorted(
            self.root.children,
            key=lambda n: n.visits,
            reverse=True
        )[:3]

        for child in sorted_children:
            analysis["best_moves"].append({
                "move": str(child.move),
                "visits": child.visits,
                "win_rate": child.wins / child.visits if child.visits > 0 else 0
            })

        return analysis

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Chọn node theo UCB"""
        while not node.game_state.is_game_over():
            if node.untried_moves:
                return node
            
            if not node.children:
                return node
                
            node = max(
                node.children,
                key=lambda n: n.get_ucb_score(self.exploration_constant)
            )
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Mở rộng node"""
        if not node.untried_moves:
            return node
            
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)
        
        new_state = node.game_state.clone()
        new_state.make_move(move)
        
        new_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(new_node)
        return new_node

    def _simulate(self,
                 node: MCTSNode,
                 evaluation_fn: Callable[[GameState], float]) -> float:
        """Thực hiện mô phỏng"""
        state = node.game_state.clone()
        
        while not state.is_game_over():
            moves = state.get_legal_moves()
            if not moves:
                break
            state.make_move(random.choice(moves))

        return self._get_simulation_result(state, evaluation_fn)

    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        """Lan truyền kết quả"""
        while node:
            node.visits += 1
            node.wins += result
            result = 1 - result
            node = node.parent

    def _get_best_move(self) -> Optional[Move]:
        """Lấy nước đi tốt nhất"""
        if not self.root or not self.root.children:
            return None

        return max(
            self.root.children,
            key=lambda n: n.visits
        ).move

    def _get_simulation_result(self,
                             state: GameState,
                             evaluation_fn: Callable[[GameState], float]) -> float:
        """Tính kết quả mô phỏng"""
        if state.is_checkmate():
            return 1.0 if state.current_player == self.root.game_state.current_player else 0.0
        elif state.is_draw():
            return 0.5
        
        eval_score = evaluation_fn(state)
        return (eval_score + 1) / 2  # Normalize to [0,1]

    def __str__(self) -> str:
        return f"MCTS Strategy (explored {self.stats.nodes_explored} nodes)"