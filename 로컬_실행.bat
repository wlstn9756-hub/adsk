@echo off
echo =======================================
echo 로컬 테스트 서버 실행 중...
echo =======================================
echo.
echo 접속 주소: http://localhost:8001
echo 종료: Ctrl + C
echo.
echo =======================================
echo.

cd /d "%~dp0"
python -m uvicorn naver_review_automation.final_complete_system:app --reload --port 8001 --host 0.0.0.0

pause
