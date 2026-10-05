"""
main.py: Application orchestrator running the primary loop.
"""

import sys
import os
import pygame
from expr import parse_lambda, EvalNode, build_eval_tree
import window
import layout
import render

WIDTH, HEIGHT = 800, 600
FPS = 60
TARGET_FILE = "file.lam"

THEME = {
    "bg": (12, 12, 20),
    "node_bg": (30, 35, 50),
    "border": (0, 255, 200),
    "path": (70, 70, 90),
    "active": (255, 0, 150),
    "text": (240, 240, 255),
    "ui_bg": (25, 25, 35),
    "ast_node": (255, 255, 50),
    "ast_edge": (100, 100, 130),
}


def load_expression_from_file():
    if os.path.exists(TARGET_FILE):
        try:
            with open(TARGET_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception:
            pass
    return "(\\x. x x) (\\y. y) z"


def save_expression_to_file(expr_str):
    try:
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(expr_str)
    except Exception:
        pass


def build_ast_tree(node):
    if not node:
        return None
    if node.tag == "var":
        return window.ASTVisualNode(str(node.name))
    if node.tag == "abs":
        ch = window.ASTVisualNode(f"λ{node.name}")
        ch.children.append(build_ast_tree(node.right))
        return ch
    ch = window.ASTVisualNode("App")
    ch.children.append(build_ast_tree(node.left))
    ch.children.append(build_ast_tree(node.right))
    return ch


def main():
    pygame.init()
    canvas = window.Canvas(WIDTH, HEIGHT)
    clock = pygame.time.Clock()

    input_expression = load_expression_from_file()
    view_mode = "timeline"
    discovered_depth = 0
    max_tree_depth = 4

    def recompile_graph(expr_str):
        nonlocal discovered_depth
        save_expression_to_file(expr_str)
        t_init = parse_lambda(expr_str)
        root = EvalNode(t_init)
        build_eval_tree(root)
        layout.layout_eval_tree(root, 50, WIDTH - 50)
        
        all_collected = layout.get_all_nodes(root)
        for n in all_collected:
            if n != root:
                n.x, n.y = root.x, root.y
                
        discovered_depth = 0
        return root, root, all_collected

    root_node, focused_node, all_nodes = recompile_graph(input_expression)
    ast_root = None

    while True:
        clock.tick(FPS)
        canvas.screen.fill(THEME["bg"])
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if view_mode == "editor":
                    if event.key == pygame.K_RETURN:
                        root_node, focused_node, all_nodes = recompile_graph(input_expression)
                        view_mode = "timeline"
                    elif event.key == pygame.K_BACKSPACE:
                        input_expression = input_expression[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_expression = load_expression_from_file()
                        view_mode = "timeline"
                    else:
                        if event.unicode and event.unicode.isprintable():
                            input_expression += event.unicode
                else:
                    if event.key == pygame.K_e:
                        input_expression = load_expression_from_file()
                        view_mode = "editor"
                    elif event.key == pygame.K_SPACE and view_mode == "timeline":
                        if discovered_depth < max_tree_depth:
                            discovered_depth += 1
                    elif event.key == pygame.K_i and view_mode == "ast":
                        view_mode = "timeline"
                    elif event.key == pygame.K_TAB and view_mode == "ast":
                        same_generation = [
                            n for n in all_nodes
                            if n.depth == focused_node.depth and n.depth <= discovered_depth
                        ]
                        if same_generation:
                            idx = same_generation.index(focused_node)
                            focused_node = same_generation[(idx + 1) % len(same_generation)]
                            ast_root = build_ast_tree(focused_node.term)
                            window.calculate_ast_layout(ast_root, 50, WIDTH - 50)
            elif event.type == pygame.MOUSEBUTTONDOWN and view_mode == "timeline":
                for n in all_nodes:
                    rect = pygame.Rect(n.x - n.w / 2, n.y - n.h / 2, n.w, n.h)
                    if n.depth <= discovered_depth and rect.collidepoint(event.pos):
                        focused_node = n
                        ast_root = build_ast_tree(focused_node.term)
                        window.calculate_ast_layout(ast_root, 50, WIDTH - 50)
                        view_mode = "ast"

        if view_mode == "timeline":
            layout.animate_eval_tree(root_node)
            render.draw_eval_tree(canvas, root_node, discovered_depth, focused_node, THEME)
        elif view_mode == "ast":
            window.animate_ast_nodes(ast_root)
            window.draw_ast_graph(canvas.screen, canvas.font, ast_root, THEME)
        elif view_mode == "editor":
            pygame.draw.rect(canvas.screen, THEME["ui_bg"], pygame.Rect(50, 200, WIDTH - 100, 150), 0, 8)
            pygame.draw.rect(canvas.screen, THEME["border"], pygame.Rect(50, 200, WIDTH - 100, 150), 3, 8)
            canvas.screen.blit(canvas.font.render("EDIT EXPRESSION (Use \\ or l for lambda):", True, THEME["border"]), (70, 220))
            canvas.screen.blit(canvas.font.render(input_expression + "|", True, THEME["text"]), (70, 270))
            canvas.screen.blit(canvas.hud_font.render("Press ENTER to confirm | ESC to cancel", True, THEME["path"]), (70, 320))

        if view_mode != "editor":
            panel_rect = pygame.Rect(10, HEIGHT - 75, WIDTH - 20, 65)
            pygame.draw.rect(canvas.screen, THEME["ui_bg"], panel_rect, 0, 6)
            if view_mode == "timeline":
                hud_text = f"TIMELINE | SPACE: Next Gen ({discovered_depth}/{max_tree_depth}) | Press 'E' to Edit Term"
            else:
                hud_text = "AST TREE MODE | TAB: Next alternative branch | 'I': Back | 'E': Edit"
            
            canvas.screen.blit(canvas.hud_font.render(hud_text, True, THEME["border"]), (20, HEIGHT - 65))
            canvas.screen.blit(canvas.hud_font.render(f"Term: {str(focused_node.term)}", True, THEME["text"]), (20, HEIGHT - 40))

        pygame.display.flip()


if __name__ == "__main__":
    main()
