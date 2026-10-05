"""
render.py: Custom Pygame canvas rendering wrappers for evaluation nodes.
"""

import pygame

def draw_eval_tree(canvas, node, max_depth, focused_node, theme, seen=None):
    if not node or node.depth > max_depth:
        return
    if seen is None:
        seen = set()
    if node in seen:
        return
    seen.add(node)

    for child in node.children:
        if child.depth <= max_depth:
            pygame.draw.line(
                canvas.screen,
                theme["path"],
                (int(node.x), int(node.y + node.h / 2)),
                (int(child.x), int(child.y - child.h / 2)),
                3,
            )
            draw_eval_tree(canvas, child, max_depth, focused_node, theme, seen)

    rect = pygame.Rect(
        int(node.x - node.w / 2), int(node.y - node.h / 2), node.w, node.h
    )
    is_hovered = rect.collidepoint(pygame.mouse.get_pos())
    node.w = canvas.draw_box(
        str(node.term),
        node.x,
        node.y,
        160,
        node.h,
        (node == focused_node),
        is_hovered,
        theme,
    )
