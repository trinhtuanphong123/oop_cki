import pygame
from const import SQUARE_SIZE

class Dragger:
    """
    Lớp Dragger chịu trách nhiệm quản lý việc kéo và thả các quân cờ.
    """
    def __init__(self):
        self._mouse_pos = (0, 0)  # Lưu vị trí chuột (x, y)
        self._initial_pos = (0, 0)  # Lưu vị trí ban đầu (row, col)
        self._piece = None  # Quân cờ đang được kéo
        self._dragging = False  # Trạng thái kéo

    # Property cho vị trí chuột
    @property
    def mouse_pos(self):
        return self._mouse_pos

    @mouse_pos.setter
    def mouse_pos(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            raise ValueError("mouse_pos must be a tuple/list with two elements (x, y)")
        self._mouse_pos = pos

    # Property cho vị trí ban đầu
    @property
    def initial_position(self):
        return self._initial_pos

    @initial_position.setter
    def initial_position(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            raise ValueError("initial_position must be a tuple/list with two elements (x, y)")
        row = pos[1] // SQUARE_SIZE
        col = pos[0] // SQUARE_SIZE
        self._initial_pos = (row, col)

    # Property cho quân cờ
    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, value):
        self._piece = value

    # Property cho trạng thái kéo
    @property
    def dragging(self):
        return self._dragging

    @dragging.setter
    def dragging(self, value):
        if not isinstance(value, bool):
            raise ValueError("Dragging must be a boolean value")
        self._dragging = value

    # Phương thức cập nhật và vẽ quân cờ
    def update_blit(self, surface, size=SQUARE_SIZE):
        """
        Vẽ quân cờ đang được kéo trên màn hình.
        
        Args:
            surface (pygame.Surface): Bề mặt màn hình để vẽ quân cờ.
            size (int): Kích thước của quân cờ.
        """
        if self.piece:
            # Cập nhật hình ảnh của quân cờ
            self.piece.set_texture(size=size)
            img = pygame.image.load(self.piece.texture)
            img_center = self.mouse_pos
            self.piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, self.piece.texture_rect)

    # Bắt đầu kéo quân cờ
    def start_drag(self, piece, pos):
        """
        Bắt đầu quá trình kéo quân cờ.
        
        Args:
            piece (Piece): Quân cờ được kéo.
            pos (tuple): Vị trí chuột (x, y) tại thời điểm kéo.
        """
        self.piece = piece
        self.initial_position = pos
        self.dragging = True

    # Cập nhật vị trí chuột
    def update_mouse_position(self, pos):
        """
        Cập nhật vị trí chuột khi người chơi kéo quân cờ.
        
        Args:
            pos (tuple): Tọa độ (x, y) hiện tại của chuột.
        """
        self.mouse_pos = pos

    # Kết thúc kéo quân cờ
    def stop_drag(self):
        """
        Kết thúc quá trình kéo quân cờ.
        """
        self.piece = None
        self.dragging = False

    def get_target_square(self) -> tuple[int, int]:
        """
        Trả về tọa độ của ô (row, col) mà quân cờ đang được thả vào.
        
        Returns:
            tuple[int, int]: Tọa độ (row, col) của ô đích.
        """
        if self.mouse_pos:
            row = self.mouse_pos[1] // SQUARE_SIZE
            col = self.mouse_pos[0] // SQUARE_SIZE
            return (row, col)
        return (-1, -1)

    def highlight_target_square(self, surface):
        """
        Tô sáng ô vuông mà quân cờ đang được kéo thả.
        
        Args:
            surface (pygame.Surface): Bề mặt để vẽ.
        """
        if self.dragging:
            row, col = self.get_target_square()
            if 0 <= row < 8 and 0 <= col < 8:
                rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, (0, 255, 0), rect, 3)  # Vẽ viền màu xanh

    def is_dragging(self) -> bool:
        """
        Kiểm tra xem quân cờ có đang được kéo hay không.
        
        Returns:
            bool: True nếu đang kéo, False nếu không.
        """
        return self.dragging
