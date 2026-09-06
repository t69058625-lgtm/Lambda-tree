#!/data/data/com.termux/files/usr/bin/bash
echo "=============================================="
echo "[Lambda Visualizer] Initializing on Termux..."
echo "=============================================="

echo "Verifying environment requirements..."
pip install -r requirements.txt --quiet

if [ ! -f "file.lam" ]; then
    echo "(\x. x x) (\y. y) z" > file.lam
    echo "Created default file.lam"
fi

if [ -z "$DISPLAY" ]; then
    export DISPLAY=:1
    echo "Warning: DISPLAY was unset. Forcing fallback to :1"
fi

echo "Launching engine inside Termux X11..."
python main.py

