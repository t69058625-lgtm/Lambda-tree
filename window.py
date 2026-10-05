"""
window.py: UI abstractions, layout configurations, fonts, and Qt-like layout blocks.
"""
import pygame
from typing import Any

class Canvas:
    def __init__(self, width: int, height: int):
        self.screen: pygame.Surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.font: pygame.font.Font = pygame.font.SysFont("Courier", 20, bold=True)
        self.hud_font: pygame.font.Font = pygame.font.SysFont("Courier", 16)

    def draw_box(self, text, x, y, min_w, h, is_active, is_hovered, theme):
        text_surf = self.font.render(text, True, theme["text"])
        w = max(min_w, text_surf.get_width() + 30)
        rect = pygame.Rect(int(x - w / 2), int(y - h / 2), w, h)
        
        bg_color = theme["active"] if is_active else theme["node_bg"]
        border_color = theme["border"] if is_hovered else theme["path"]
        
        pygame.draw.rect(self.screen, bg_color, rect, 0, 6)
        pygame.draw.rect(self.screen, border_color, rect, 2, 6)
        self.screen.blit(text_surf, (int(x - text_surf.get_width() / 2), int(y - text_surf.get_height() / 2)))
        return w

class ASTVisualNode:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.x, self.y = 0.0, 0.0
        self.target_x, self.target_y = 0.0, 0.0

def calculate_ast_layout(node, x_min, x_max, y_start=80, y_spacing=80):
    if not node: return
    node.target_y = y_start
    node.target_x = (x_min + x_max) / 2.0
    if node.children:
        w = (x_max - x_min) / len(node.children)
        for i, ch in enumerate(node.children):
            calculate_ast_layout(ch, x_min + i * w, x_min + (i + 1) * w, y_start + y_spacing, y_spacing)

def animate_ast_nodes(node):
    if not node: return
    node.x += (node.target_x - node.x) * 0.15
    node.y += (node.target_y - node.y) * 0.15
    for ch in node.children: animate_ast_nodes(ch)

def draw_ast_graph(screen, font, node: ASTVisualNode | None, theme,  offset_x: int | Any = 0, offset_y: int | Any = 0):
    if not node: return
    screen_x = int(node.x + offset_x)
    screen_y = int(node.y + offset_y)
    for ch in node.children:
        ch_screen_x = int(ch.x + offset_x)
        ch_screen_y = int(ch.y + offset_y)
        pygame.draw.line(screen, theme["ast_edge"], (screen_x, screen_y), (ch_screen_x, ch_screen_y), 2)
        draw_ast_graph(screen, font, ch, theme, offset_x, offset_y)
    txt = font.render(node.name, True, theme["text"])
    rect = pygame.Rect(screen_x - 30, screen_y - 15, 60, 30)
    pygame.draw.rect(screen, theme["ui_bg"], rect, 0, 4)
    pygame.draw.rect(screen, theme["ast_node"], rect, 1, 4)
    screen.blit(txt, (screen_x - txt.get_width() // 2, screen_y - txt.get_height() // 2))
# --- QT-LIKE STACKING BLOCKS SYSTEM ---
class UIBlock:
    """Базовый абстрактный блок интерфейса (аналог QWidget)."""
    def __init__(self, width_policy="expand", height_policy="wrap"):
        self.width_policy = width_policy
        self.height_policy = height_policy
        self.rect = pygame.Rect(0, 0, 0, 0)

class VBoxLayout:
    """Контейнер вертикальной сборки элементов (аналог QVBoxLayout)."""
    def __init__(self, margin=15, spacing=10):
        self.margin = margin
        self.spacing = spacing
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def arrange(self, x, y, available_w, available_h):
        curr_y = y + self.margin
        for block in self.blocks:
            b_w = available_w - (self.margin * 2)
            b_h = block.rect.height if block.height_policy == "wrap" else 40
            block.rect = pygame.Rect(x + self.margin, curr_y, b_w, b_h)
            curr_y += b_h + self.spacing

# Модульные оверлеи рендеринга
def draw_settings_menu(
                screen: pygame.surface.Surface, 
                font: pygame.font.Font, 
                hud_font: pygame.font.Font, 
                w: int, h: int, 
                theme, selected_row: int, modes, mode_idx, theme_name):
    # Make a vertical layout manager with big enough margins
    layout = VBoxLayout(margin=30, spacing=25)

    # Register EVERY element as separate blocks, including the header
    header_row = UIBlock(); header_row.rect.height = 40
    row0 = UIBlock(); row0.rect.height = 35
    row1 = UIBlock(); row1.rect.height = 35

    layout.add_block(header_row)
    layout.add_block(row0)
    layout.add_block(row1)

    # Automatically calculate coordinates for every  block inside the settings window
    layout.arrange(100, 100, w - 200, h - 200)
    
    # Draw the border and background of the menu
    pygame.draw.rect(screen, theme["ui_bg"], pygame.Rect(100, 100, w - 200, h - 200), 0, 12)
    pygame.draw.rect(screen, theme["border"], pygame.Rect(100, 100, w - 200, h - 200), 3, 12)

    # Draw the header using beautifull, dynamicly calculated coordinates of a block
    screen.blit(font.render("ENGINE ARCHITECTURE SETTINGS", True, theme["border"]), (header_row.rect.x, header_row.rect.y))

    # Themes (calcuolated for the header including spacing)
    c0 = theme["active"] if selected_row == 0 else theme["text"]
    screen.blit(font.render(f"  Color Theme: < {theme_name} >", True, c0), (row0.rect.x, row0.rect.y))

    # Engine modes (calculated even lower)
    c1 = theme["active"] if selected_row == 1 else theme["text"]
    screen.blit(font.render(f"  Visual Engine: < {modes[mode_idx]} >", True, c1), (row1.rect.x, row1.rect.y))

    # Hints in the bottom
    screen.blit(hud_font.render("Use UP / DOWN to navigate | LEFT / RIGHT to toggle choices", True, theme["path"]), (140, h - 160))
    screen.blit(hud_font.render("Press 'S' or ESC to exit back to operational runtime", True, theme["path"]), (140, h - 135))

def draw_expression_editor(screen, font, hud_font, w, h, theme, current_input):
    pygame.draw.rect(screen, theme["ui_bg"], pygame.Rect(50, 200, w - 100, 150), 0, 8)
    pygame.draw.rect(screen, theme["border"], pygame.Rect(50, 200, w - 100, 150), 3, 8)
    screen.blit(font.render("EDIT EXPRESSION (Use \\ or l for lambda):", True, theme["border"]), (70, 220))
    screen.blit(font.render(current_input + "|", True, theme["text"]), (70, 270))
    screen.blit(hud_font.render("Press ENTER to confirm | ESC to cancel", True, theme["path"]), (70, 320))
