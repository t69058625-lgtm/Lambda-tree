# Lambda Calculus Evaluation Tree Visualizer

An interactive Python application designed to parse lambda calculus expressions, map out their alternative reduction pathways in a modular evaluation timeline graph, and unroll their Abstract Syntax Trees (AST).

## Features
- **Visual Evaluation Mapping:** Interactive nodes displaying full calculus expressions.
- **Incremental Step Tracing:** Unfold execution pathways branch by branch using `SPACE`.
- **AST Explorer:** Click any reduction node to visualize its underlying Abstract Syntax Tree graph.
- **Dynamic Expression Editing:** Modify definitions cleanly on-the-fly inside the client by pressing `E`.
- **Multi-Platform Bootstrapper:** Built-in scripts for seamless execution across Windows, Linux, and Android (Termux).

## Installation & Running

Ensure you have your environment variables set up, then execute the script matching your current ecosystem:

### Windows
```cmd
run.bat
```

### Linux
```bash
chmod +x run.sh
./run.sh
```

### Android (Termux + X11 environment)
```bash
chmod +x run_android.sh
./run_android.sh
```

## Control Layout
- **`SPACE` (Timeline):** Advance generation / discover next available steps.
- **`MOUSE CLICK` (Timeline):** Jump inside a term block node to open its AST layout mapping.
- **`TAB` (AST Mode):** Shift view to alternative reduction branch inside the same generation level.
- **`I` (AST Mode):** Escape tree focus and return back out to the main evaluation timeline map.
- **`E` (Any Mode):** Open text prompt console screen overlay to change the evaluated term expression.

