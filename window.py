"""
window.py: Pygame Canvas Wrapper and Geometry Solver Core.
"""

import pygame


class Canvas:
    """Manages system displays and text drawing utilities."""

    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Modular Lambda Runtime Tracker")

        self.font = pygame.font.SysFont("monospace", 20, bold=True)
        self.hud_font = pygame.font.SysFont("monospace", 16, bold=True)

    def draw_box(self, text, x, y, w, h, is_focused, is_hovered, colors):
        """Draws a functional UI term cell with text auto-centering."""
        txt_surf = self.font.render(text, True, colors["text"])
        box_width = max(txt_surf.get_width() + 40, w)

        rect = pygame.Rect(
            int(x - box_width / 2), int(y - h / 2), box_width, h
        )
        border_color = (
            colors["active"]
            if is_focused
            else (colors["border"] if is_hovered else colors["path"])
        )

        pygame.draw.rect(self.screen, colors["node_bg"], rect, 0, 6)
        pygame.draw.rect(self.screen, border_color, rect, 3 if is_focused else 2, 6)
        self.screen.blit(
            txt_surf,
            (
                int(x - txt_surf.get_width() / 2),
                int(y - txt_surf.get_height() / 2),
            ),
        )
        return box_width


class ASTVisualNode:
    """Internal structural cell utilized solely for generating layouts."""

    def __init__(self, label):
        self.label = label
        self.children = []
        self.x, self.y = 400.0, 300.0
        self.target_x, self.target_y = 400.0, 300.0


def calculate_ast_layout(node, x_min, x_max, depth=1, y_start=100):
    if not node:
        return
    node.target_x = (x_min + x_max) / 2
    node.target_y = y_start + depth * 85
    if not node.children:
        return
    segment_width = (x_max - x_min) / len(node.children)
    for idx, child in enumerate(node.children):
        calculate_ast_layout(
            child,
            x_min + idx * segment_width,
            x_min + (idx + 1) * segment_width,
            depth + 1,
            y_start,
        )


def animate_ast_nodes(node):
    if not node:
        return
    node.x += (node.target_x - node.x) * 0.15
    node.y += (node.target_y - node.y) * 0.15
    for child in node.children:
        animate_ast_nodes(child)


def draw_ast_graph(screen, font, node, colors):
    if not node:
        return
    for child in node.children:
        pygame.draw.line(
            screen,
            colors["ast_edge"],
            (int(node.x), int(node.y)),
            (int(child.x), int(child.y)),
            3,
        )
        draw_ast_graph(screen, font, child, colors)
    pygame.draw.circle(screen, colors["ast_node"], (int(node.x), int(node.y)), 22)
    screen.blit(
        font.render(node.label, True, colors["bg"]), (node.x - 10, node.y - 10)
    )

