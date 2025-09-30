@echo off
chcp 65001 >nul
echo ========================================
echo  Naver Review Management System
echo ========================================
echo.

cd naver_review_system

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing required packages...
pip install -r requirements_extended.txt

echo.
echo [4/4] Starting server...
echo.
echo ========================================
echo  Server is running!
echo  Open browser: http://localhost:8000
echo  Press Ctrl+C to stop
echo ========================================
echo.

python main_integrated.py

pause