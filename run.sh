#!/bin/bash
echo "=============================================="
echo "[Lambda Visualizer] Initializing on Linux..."
echo "=============================================="

set -e

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt --quiet

if [ ! -f "file.lam" ]; then
    echo "(\x. x x) (\y. y) z" > file.lam
    echo "Created default file.lam"
fi

echo "Starting engine..."
python3 main.py

