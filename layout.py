"""
layout.py: Graph positioning physics and animation handlers.
"""

def get_all_nodes(node, seen=None):
    if not node:
        return []
    if seen is None:
        seen = set()
    if node in seen:
        return []
    seen.add(node)
    
    nodes = [node]
    for child in node.children:
        nodes.extend(get_all_nodes(child, seen))
    return nodes


def layout_eval_tree(node, x_min, x_max, y_start=80, y_spacing=100, seen=None):
    if not node:
        return
    if seen is None:
        seen = set()
    if node in seen:
        return
    seen.add(node)

    node.target_y = y_start + node.depth * y_spacing
    node.target_x = (x_min + x_max) / 2.0

    if node.children:
        width = (x_max - x_min) / len(node.children)
        for i, child in enumerate(node.children):
            c_min = x_min + i * width
            c_max = c_min + width
            layout_eval_tree(child, c_min, c_max, y_start, y_spacing, seen)


def animate_eval_tree(node, seen=None):
    if not node:
        return
    if seen is None:
        seen = set()
    if node in seen:
        return
    seen.add(node)

    node.x += (node.target_x - node.x) * 0.15
    node.y += (node.target_y - node.y) * 0.15

    for child in node.children:
        animate_eval_tree(child, seen)
