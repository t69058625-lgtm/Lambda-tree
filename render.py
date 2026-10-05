"""
render.py: Custom Pygame canvas rendering wrappers for evaluation nodes.
"""

import pygame
from typing import Any

def draw_eval_tree(canvas, node, max_depth, focused_node, theme, offset_x: float | Any = 0.0, offset_y: float | Any = 0.0, seen=None):
    if not node or node.depth > max_depth:
        return
    if seen is None:
        seen = set()
    if node in seen:
        return
    seen.add(node)

    # Экранные координаты текущего узла таймлайна
    screen_x = node.x + offset_x
    screen_y = node.y + offset_y

    for child in node.children:
        if child.depth <= max_depth:
            child_screen_x = child.x + offset_x
            child_screen_y = child.y + offset_y
            pygame.draw.line(
                canvas.screen,
                theme["path"],
                (int(screen_x), int(screen_y + node.h / 2)),
                (int(child_screen_x), int(child_screen_y - child.h / 2)),
                3,
            )
            draw_eval_tree(canvas, child, max_depth, focused_node, theme, offset_x, offset_y, seen)

    rect = pygame.Rect(int(screen_x - node.w / 2), int(screen_y - node.h / 2), node.w, node.h)
    is_hovered = rect.collidepoint(pygame.mouse.get_pos())
    node.w = canvas.draw_box(
        str(node.term),
        screen_x,
        screen_y,
        160,
        node.h,
        (node == focused_node),
        is_hovered,
        theme,
    )
