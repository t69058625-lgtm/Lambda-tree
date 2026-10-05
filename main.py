"""
main.py: Application orchestrator running the primary loop with theme and visual settings.
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

THEMES = {
    "Classic Dark": {
        "bg": (12, 12, 20), "node_bg": (30, 35, 50), "border": (0, 255, 200),
        "path": (70, 70, 90), "active": (255, 0, 150), "text": (240, 240, 255),
        "ui_bg": (25, 25, 35), "ast_node": (255, 255, 50), "ast_edge": (100, 100, 130)
    },
    "Neon Matrix": {
        "bg": (5, 15, 5), "node_bg": (15, 40, 15), "border": (0, 255, 70),
        "path": (30, 80, 30), "active": (255, 255, 255), "text": (180, 255, 180),
        "ui_bg": (10, 25, 10), "ast_node": (0, 255, 255), "ast_edge": (40, 100, 40)
    }
}
VISUAL_MODES = ["Standard AST", "John Tromp Diagram", "Mockingbird Logic"]
current_theme_name = "Classic Dark"
current_visual_mode_idx = 0

def load_expression_from_file():
    if os.path.exists(TARGET_FILE):
        try:
            with open(TARGET_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content: return content
        except Exception: pass
    return "(\\x. x x) (\\y. y) z"

def save_expression_to_file(expr_str):
    try:
        with open(TARGET_FILE, "w", encoding="utf-8") as f: f.write(expr_str)
    except Exception: pass

def build_ast_tree(node):
    if not node: return None
    if node.tag == "var": return window.ASTVisualNode(str(node.name))
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
    global WIDTH, HEIGHT, current_theme_name, current_visual_mode_idx
    canvas = window.Canvas(WIDTH, HEIGHT)
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Modular Lambda Runtime Tracker")

    try:
        icon_surf = pygame.Surface((32, 32))
        icon_surf.fill((30, 35, 50))
        pygame.draw.rect(icon_surf, (0, 255, 200), (0, 0, 32, 32), 3, 4)
        pygame.display.set_icon(icon_surf)
    except Exception: pass

    clock = pygame.time.Clock()
    input_expression = load_expression_from_file()
    view_mode = "timeline"
    discovered_depth = 0
    max_tree_depth = 4
    offset_x, offset_y = 0.0, 0.0
    dragging = False
    selected_setting_row = 0

    def recompile_graph(expr_str):
        nonlocal discovered_depth, offset_x, offset_y
        save_expression_to_file(expr_str)
        t_init = parse_lambda(expr_str)
        root = EvalNode(t_init)
        build_eval_tree(root)
        layout.layout_eval_tree(root, 50, WIDTH - 50)
        all_collected = layout.get_all_nodes(root)
        root.x, root.y = root.target_x, root.target_y
        for n in all_collected:
            if n != root: n.x, n.y = root.x, root.y
        discovered_depth = 0
        offset_x, offset_y = 0.0, 0.0
        return root, root, all_collected

    root_node, focused_node, all_nodes = recompile_graph(input_expression)
    ast_root = None
    theme_keys = list(THEMES.keys())

    while True:
        clock.tick(FPS)
        current_theme = THEMES[current_theme_name]
        canvas.screen.fill(current_theme["bg"])
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                canvas.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                layout.layout_eval_tree(root_node, 50, WIDTH - 50)
                if ast_root: window.calculate_ast_layout(ast_root, 50, WIDTH - 50)
            elif event.type == pygame.KEYDOWN:
                if view_mode == "editor":
                    if event.key == pygame.K_RETURN:
                        root_node, focused_node, all_nodes = recompile_graph(input_expression)
                        view_mode = "timeline"
                    elif event.key == pygame.K_BACKSPACE: input_expression = input_expression[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_expression = load_expression_from_file()
                        view_mode = "timeline"
                    else:
                        if event.unicode and event.unicode.isprintable(): input_expression += event.unicode
                elif view_mode == "settings":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_s: view_mode = "timeline"
                    elif event.key == pygame.K_UP: selected_setting_row = (selected_setting_row - 1) % 2
                    elif event.key == pygame.K_DOWN: selected_setting_row = (selected_setting_row + 1) % 2
                    elif event.key == pygame.K_LEFT:
                        if selected_setting_row == 0: current_theme_name = theme_keys[(theme_keys.index(current_theme_name) - 1) % len(theme_keys)]
                        else: current_visual_mode_idx = (current_visual_mode_idx - 1) % len(VISUAL_MODES)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                        if selected_setting_row == 0: current_theme_name = theme_keys[(theme_keys.index(current_theme_name) + 1) % len(theme_keys)]
                        else: current_visual_mode_idx = (current_visual_mode_idx + 1) % len(VISUAL_MODES)
                else:
                    if event.key == pygame.K_e:
                        input_expression = load_expression_from_file()
                        view_mode = "editor"
                    elif event.key == pygame.K_s: view_mode = "settings"
                    elif event.key == pygame.K_SPACE and view_mode == "timeline":
                        if discovered_depth < max_tree_depth: discovered_depth += 1
                    elif event.key == pygame.K_i and view_mode == "ast": view_mode = "timeline"
                    elif event.key == pygame.K_TAB and view_mode == "ast":
                        sg = [n for n in all_nodes if n.depth == focused_node.depth and n.depth <= discovered_depth]
                        if sg:
                            focused_node = sg[(sg.index(focused_node) + 1) % len(sg)]
                            ast_root = build_ast_tree(focused_node.term)
                            window.calculate_ast_layout(ast_root, 50, WIDTH - 50)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши (Mouse1)
                    ui_hit = False                    
                    if view_mode == "timeline":
                        # Учитываем смещение камеры при клике на узлы таймлайна
                        adj_pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                        for n in all_nodes:
                            rect = pygame.Rect(n.x - n.w / 2, n.y - n.h / 2, n.w, n.h)
                            if n.depth <= discovered_depth and rect.collidepoint(adj_pos):
                                focused_node = n
                                ast_root = build_ast_tree(focused_node.term)
                                window.calculate_ast_layout(ast_root, 50, WIDTH - 50)
                                view_mode = "ast"
                                ui_hit = True
                                break
                    elif view_mode == "ast":
                        ui_hit = False
                    if not ui_hit:
                        dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False                    
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    # Камера двигается свободно, изменяя глобальные офсеты
                    offset_x += event.rel[0]
                    offset_y += event.rel[1]
        if view_mode == "timeline":
            layout.animate_eval_tree(root_node)
            # Передаем offset_x и offset_y прямо в функцию отрисовки
            render.draw_eval_tree(canvas, root_node, discovered_depth, focused_node, current_theme, offset_x, offset_y)
                
        elif view_mode == "ast":
            window.animate_ast_nodes(ast_root)
            # Передаем offset_x и offset_y для чистого сдвига всей сцены дерева AST
            window.draw_ast_graph(canvas.screen, canvas.font, ast_root, current_theme, offset_x, offset_y)
        elif view_mode == "settings":
            window.draw_settings_menu(canvas.screen, canvas.font, canvas.hud_font, WIDTH, HEIGHT, current_theme, selected_setting_row, VISUAL_MODES, current_visual_mode_idx, current_theme_name)
        elif view_mode == "editor":
            window.draw_expression_editor(canvas.screen, canvas.font, canvas.hud_font, WIDTH, HEIGHT, current_theme, input_expression)

        if view_mode not in ["editor", "settings"]:
            pygame.draw.rect(canvas.screen, current_theme["ui_bg"], pygame.Rect(10, HEIGHT - 75, WIDTH - 20, 65), 0, 6)
            hud_text = f"TIMELINE | SPACE: Next Gen ({discovered_depth}/{max_tree_depth}) | Press 'S' for Settings" if view_mode == "timeline" else "AST TREE MODE | TAB: Next branch | 'I': Back"
            canvas.screen.blit(canvas.hud_font.render(hud_text, True, current_theme["border"]), (20, HEIGHT - 65))
            canvas.screen.blit(canvas.hud_font.render(f"Term: {str(focused_node.term)}", True, current_theme["text"]), (20, HEIGHT - 40))
        pygame.display.flip()

if __name__ == "__main__": main()
