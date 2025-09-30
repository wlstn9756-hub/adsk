@echo off
echo.
echo GitHub Personal Access Token으로 푸시하기
echo =========================================
echo.
echo 토큰 생성 방법:
echo 1. GitHub 로그인
echo 2. Settings - Developer settings
echo 3. Personal access tokens - Generate new token
echo 4. repo 권한 체크 후 생성
echo.
set /p TOKEN=토큰을 입력하세요:

git remote set-url origin https://%TOKEN%@github.com/wlstn9756-hub/adsk.git
git push -u origin main

echo.
echo 푸시 완료! 보안을 위해 토큰 정보 제거중...
git remote set-url origin https://github.com/wlstn9756-hub/adsk.git

echo.
echo 완료되었습니다!
pause