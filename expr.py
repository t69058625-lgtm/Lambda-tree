"""
expr.py: Lambda Calculus AST, Parser, and Normal-Order Engine.
"""


class Term:
    """Represents a Lambda Calculus term (Variable, Abstraction, or Application)."""

    def __init__(self, tag, name=None, left=None, right=None):
        self.tag = tag  # 'var', 'abs', or 'app'
        self.name = name  # Bound variable name (for 'var' and 'abs')
        self.left = left  # Left child tree (for 'app')
        self.right = right  # Right child tree (for 'app' body / 'abs' body)

    def __str__(self):
        if self.tag == "var":
            return self.name
        if self.tag == "abs":
            return f"(λ{self.name}.{self.right})"
        return f"({self.left} {self.right})"


def substitute(node, var_name, expression):
    """Safely substitutes occurrences of var_name with expression."""
    if not node:
        return None
    if node.tag == "var":
        if node.name == var_name:
            return copy_term(expression)
        return Term("var", name=node.name)
    if node.tag == "abs":
        if node.name == var_name:
            return node
        return Term(
            "abs",
            name=node.name,
            right=substitute(node.right, var_name, expression),
        )
    return Term(
        "app",
        left=substitute(node.left, var_name, expression),
        right=substitute(node.right, var_name, expression),
    )


def copy_term(node):
    """Deep copies a lambda term structure."""
    if not node:
        return None
    return Term(
        node.tag,
        name=node.name,
        left=copy_term(node.left),
        right=copy_term(node.right),
    )


def parse_lambda(source_string):
    """Compiles a string using \\ or l into a structured AST term."""
    source_string = source_string.replace("\\", "λ").replace("l", "λ").strip()

    def tokenize(s):
        tokens, i = [], 0
        while i < len(s):
            if s[i] in "()λ.":
                tokens.append(s[i])
                i += 1
            elif s[i].isspace():
                i += 1
            else:
                word = ""
                while (
                    i < len(s)
                    and not s[i].isspace()
                    and s[i] not in "()λ."
                ):
                    word += s[i]
                    i += 1
                tokens.append(word)
        return tokens

    def parse_expr(tokens):
        if not tokens:
            return None
        res = parse_single(tokens)
        while tokens and tokens != ")":
            right = parse_single(tokens)
            if right:
                res = Term("app", left=res, right=right)
        return res

    def parse_single(tokens):
        if not tokens:
            return None
        t = tokens.pop(0)
        if t == "(":
            res = parse_expr(tokens)
            if tokens and tokens == ")":
                tokens.pop(0)
            return res
        if t == "λ":
            variables = []
            while tokens and tokens != ".":
                v = tokens.pop(0)
                if v != "λ":
                    variables.append(v)
            if tokens and tokens == ".":
                tokens.pop(0)
            body = parse_expr(tokens)
            for v in reversed(variables):
                body = Term("abs", name=v, right=body)
            return body
        return Term("var", name=t)

    try:
        return parse_expr(tokenize(source_string))
    except Exception:
        return Term("var", name="parse_error")


class EvalNode:
    """A configuration node inside the evaluation network."""

    def __init__(self, term, depth=0):
        self.term = term
        self.depth = depth
        self.children = []
        self.x, self.y = 400.0, 300.0
        self.target_x, self.target_y = 400.0, 300.0
        self.w, self.h = 220, 55


def find_redexes(node, path=None):
    """Scans structural positions looking for valid reduction points."""
    if path is None:
        path = []
    redexes = []
    if node.tag == "app":
        if node.left.tag == "abs":
            redexes.append(path)
        redexes.extend(find_redexes(node.left, path + ["l"]))
        redexes.extend(find_redexes(node.right, path + ["r"]))
    elif node.tag == "abs":
        redexes.extend(find_redexes(node.right, path + ["r"]))
    return redexes


def reduce_at(node, path):
    """Executes a beta-reduction calculation at the specified branch path."""
    if not path:
        if node.tag == "app" and node.left.tag == "abs":
            return substitute(node.left.right, node.left.name, node.right)
        return node
    if path[0] == "l":
        return Term(
            "app",
            left=reduce_at(node.left, path[1:]),
            right=copy_term(node.right),
        )
    if path[0] == "r":
        if node.tag == "app":
            return Term(
                "app",
                left=copy_term(node.left),
                right=reduce_at(node.right, path[1:]),
            )
        return Term(
            "abs",
            name=node.name,
            right=reduce_at(node.right, path[1:]),
        )
    return node


def build_eval_tree(current_node, visited=None, depth=0, max_depth=5):
    """Recursively unfolds all evaluation paths safely."""
    if depth >= max_depth:
        return
    if visited is None:
        visited = {}

    term_signature = str(current_node.term)
    if term_signature in visited:
        return
    visited[term_signature] = current_node

    redexes = find_redexes(current_node.term)
    for path in redexes:
        next_term = reduce_at(current_node.term, path)
        next_signature = str(next_term)

        if next_signature in visited:
            if visited[next_signature] not in current_node.children:
                current_node.children.append(visited[next_signature])
        else:
            child_node = EvalNode(next_term, depth + 1)
            current_node.children.append(child_node)
            build_eval_tree(child_node, visited, depth + 1, max_depth)

