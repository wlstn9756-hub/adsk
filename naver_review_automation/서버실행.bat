@echo off
chcp 65001
echo ==========================================
echo    네이버 리뷰 시스템 서버 시작
echo ==========================================
echo.
echo 서버를 시작합니다...
echo 브라우저에서 http://localhost:8000 로 접속하세요.
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
echo ==========================================
echo.

cd /d "%~dp0"
python -m uvicorn final_complete_system:app --host 0.0.0.0 --port 8000 --reload

pause
