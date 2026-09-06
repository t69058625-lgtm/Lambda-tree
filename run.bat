@echo off
echo ==============================================
echo [Lambda Visualizer] Initializing on Windows...
echo ==============================================

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate
echo Installing requirements...
pip install -r requirements.txt --quiet

if not exist file.lam (
    echo (\x. x x) (\y. y) z > file.lam
    echo Created default file.lam
)

echo Starting engine...
python main.py
pause

