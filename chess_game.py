import pygame as pg
from typing import Optional, Dict, Tuple
from chess_gui import ChessGUI
from core.game_state import GameState, GameStatus 
from core.move import Move, MoveType
from core.pieces.piece import Piece, PieceColor
from player.human_player import HumanPlayer
from player.ai_player import AIPlayer, AILevel

class ChessGame:
    def __init__(self, screen: pg.Surface, game_config: Dict):
        """
        Khởi tạo game cờ vua
        Args:
            screen: Màn hình pygame
            game_config: Cấu hình game từ main (chế độ chơi, độ khó AI...)
        """
        # Pygame components
        self.screen = screen
        self.clock = pg.time.Clock()
        
        # Khởi tạo GUI sử dụng class ChessGUI đã có
        self.gui = ChessGUI(self.screen)
        
        # Khởi tạo game state để quản lý trạng thái game
        self.game_state = GameState()
        
        # Khởi tạo người chơi dựa trên config
        self.current_player_color = PieceColor.WHITE
        self._setup_players(game_config)
        
        # Biến tracking game
        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        self.is_game_over = False
        self.game_result = None

    def _setup_players(self, config: Dict) -> None:
        """Thiết lập người chơi dựa trên config"""
        game_mode = config.get('mode')
        
        # Người chơi quân trắng luôn là người
        self.white_player = HumanPlayer(PieceColor.WHITE)
        
        # Người chơi quân đen có thể là người hoặc AI
        if game_mode == "HUMAN_VS_HUMAN":
            self.black_player = HumanPlayer(PieceColor.BLACK)
        else:
            ai_level = config.get('ai_level', AILevel.MEDIUM)
            self.black_player = AIPlayer(PieceColor.BLACK, ai_level)
            
        self.current_player = self.white_player

    def handle_events(self) -> None:
        """Xử lý các event trong game"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
                
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Chỉ xử lý click khi là lượt người chơi
                if isinstance(self.current_player, HumanPlayer):
                    self._handle_click(event.pos)
                    
        return True

    def _handle_click(self, pos: Tuple[int, int]) -> None:
        """
        Xử lý click chuột trên bàn cờ
        """
        square = self.gui.get_square_at_pos(pos)
        if not square:
            return
            
        if self.selected_square:
            # Nếu đã chọn quân, thử thực hiện nước đi
            move = Move(self.selected_square, square, 
                       self.game_state.board.get_piece(self.selected_square))
                       
            if move in self.legal_moves:
                self._make_move(move)
            self.selected_square = None
            self.legal_moves = []
            
        else:
            # Chọn quân mới
            piece = self.game_state.board.get_piece(square)
            if piece and piece.color == self.current_player_color:
                self.selected_square = square
                self.legal_moves = self.game_state.get_legal_moves(square)
                
        # Cập nhật GUI
        self.gui.selected_square = self.selected_square
        self.gui.legal_moves = self.legal_moves

    def _make_move(self, move: Move) -> None:
        """
        Thực hiện nước đi và cập nhật trạng thái game
        """
        # Thực hiện nước đi
        result = self.game_state.make_move(move)
        if not result:
            return
            
        # Cập nhật GUI
        self.gui.last_move = move
        
        # Kiểm tra kết thúc game
        self._check_game_over()
        
        if not self.is_game_over:
            # Chuyển lượt
            self._switch_player()
            
            # Nếu là lượt AI, lấy và thực hiện nước đi của AI
            if isinstance(self.current_player, AIPlayer):
                self._make_ai_move()

    def _make_ai_move(self) -> None:
        """Xử lý nước đi của AI"""
        ai_move = self.current_player.get_move(self.game_state)
        if ai_move:
            # Thêm animation cho nước đi AI
            self.gui.animate_move(ai_move)
            self._make_move(ai_move)

    def _switch_player(self) -> None:
        """Chuyển lượt chơi"""
        self.current_player_color = (PieceColor.BLACK 
                                   if self.current_player_color == PieceColor.WHITE 
                                   else PieceColor.WHITE)
        self.current_player = (self.black_player 
                            if self.current_player_color == PieceColor.BLACK 
                            else self.white_player)

    def _check_game_over(self) -> None:
        """Kiểm tra điều kiện kết thúc game"""
        # Kiểm tra chiếu hết
        if self.game_state.is_checkmate():
            self.is_game_over = True
            winner = "White" if self.current_player_color == PieceColor.BLACK else "Black"
            self.game_result = f"Checkmate! {winner} wins!"
            return

        # Kiểm tra hòa cờ do bế tắc
        if self.game_state.is_stalemate():
            self.is_game_over = True
            self.game_result = "Stalemate! Game is a draw."
            return

        # Kiểm tra hòa do không đủ quân chiếu hết
        if self.game_state.is_insufficient_material():
            self.is_game_over = True
            self.game_result = "Draw due to insufficient material!"
            return

    def update(self) -> None:
        """Cập nhật trạng thái game mỗi frame"""
        # Cập nhật game state
        game_data = {
            'board': self.game_state.board.get_board_state(),
            'current_player': self.current_player_color,
            'selected_square': self.selected_square,
            'legal_moves': self.legal_moves,
            'last_move': self.last_move,
            'move_history': self.game_state.move_history,
            'captured_pieces': {
                'white': self.game_state.captured_pieces[PieceColor.WHITE],
                'black': self.game_state.captured_pieces[PieceColor.BLACK]
            },
            'is_check': self.game_state.is_in_check(),
            'is_game_over': self.is_game_over,
            'game_result': self.game_result
        }

        # Cập nhật GUI
        self.gui.update(game_data)

    def save_game(self) -> Dict:
        """Lưu trạng thái game hiện tại"""
        return {
            'board_state': self.game_state.board.get_board_state(),
            'current_player': self.current_player_color,
            'move_history': self.game_state.move_history,
            'captured_pieces': self.game_state.captured_pieces,
            'game_mode': 'AI' if isinstance(self.black_player, AIPlayer) else 'HUMAN',
            'ai_level': self.black_player.level if isinstance(self.black_player, AIPlayer) else None
        }

    def load_game(self, saved_state: Dict) -> bool:
        """
        Load trạng thái game đã lưu
        Returns:
            bool: True nếu load thành công, False nếu thất bại
        """
        try:
            # Khôi phục trạng thái bàn cờ
            self.game_state.board.set_board_state(saved_state['board_state'])
            
            # Khôi phục thông tin game
            self.current_player_color = saved_state['current_player']
            self.game_state.move_history = saved_state['move_history']
            self.game_state.captured_pieces = saved_state['captured_pieces']
            
            # Khôi phục người chơi
            if saved_state['game_mode'] == 'AI':
                self.black_player = AIPlayer(PieceColor.BLACK, saved_state['ai_level'])
            else:
                self.black_player = HumanPlayer(PieceColor.BLACK)
                
            self.current_player = (self.black_player 
                                if self.current_player_color == PieceColor.BLACK 
                                else self.white_player)
            
            # Cập nhật GUI
            self.update()
            return True
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def handle_promotion(self, move: Move) -> None:
        """Xử lý phong cấp tốt"""
        if not isinstance(self.current_player, HumanPlayer):
            # AI tự động chọn quân hậu
            move.promotion_piece_type = 'Q'
            return

        # Hiển thị menu chọn quân phong cấp cho người chơi
        promotion_piece = self.gui.show_promotion_dialog(move.color)
        if promotion_piece:
            move.promotion_piece_type = promotion_piece
            self._make_move(move)

    def handle_special_moves(self, move: Move) -> None:
        """Xử lý các nước đi đặc biệt"""
        # Kiểm tra nhập thành
        if move.is_castling:
            rook_move = self.game_state.get_castling_rook_move(move)
            if rook_move:
                self.gui.animate_move(rook_move)
                
        # Kiểm tra bắt tốt qua đường
        elif move.is_en_passant:
            captured_pawn_pos = self.game_state.get_en_passant_capture_square(move)
            if captured_pawn_pos:
                self.gui.show_capture_animation(captured_pawn_pos)

    def display_game_over(self) -> None:
        """Hiển thị màn hình kết thúc game"""
        if self.is_game_over:
            self.gui.show_game_over_screen(self.game_result)

    def reset_game(self) -> None:
        """Reset game về trạng thái ban đầu"""
        # Reset game state
        self.game_state = GameState()
        
        # Reset tracking variables
        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        self.is_game_over = False
        self.game_result = None
        
        # Reset về lượt trắng
        self.current_player_color = PieceColor.WHITE
        self.current_player = self.white_player
        
        # Cập nhật GUI
        self.update()

    def run(self) -> None:
        """Game loop chính"""
        running = True
        while running:
            # Xử lý events
            running = self.handle_events()
            
            # Cập nhật game state
            self.update()
            
            # Hiển thị kết thúc game nếu cần
            if self.is_game_over:
                self.display_game_over()
            
            # Giới hạn FPS
            self.clock.tick(60)

        # Lưu game trước khi thoát
        self.save_game()