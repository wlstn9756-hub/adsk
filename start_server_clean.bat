@echo off
chcp 65001 >nul
echo ====================================
echo 서버 깨끗하게 재시작
echo ====================================

echo.
echo [1단계] 모든 Python 프로세스 종료 중...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2단계] 프로세스 확인...
tasklist | findstr python.exe
if %ERRORLEVEL% EQU 0 (
    echo 아직 Python 프로세스가 실행 중입니다. 다시 종료 시도...
    taskkill /F /IM python.exe /T 2>nul
    timeout /t 2 /nobreak >nul
)

echo.
echo [3단계] 포트 8000 확인...
netstat -ano | findstr :8000
if %ERRORLEVEL% EQU 0 (
    echo 포트 8000이 사용 중입니다. 프로세스 종료...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul
    timeout /t 2 /nobreak >nul
)

echo.
echo [4단계] 서버 시작...
cd naver_review_automation
python -m uvicorn final_complete_system:app --host 0.0.0.0 --port 8000 --reload

pause
