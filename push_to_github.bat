@echo off
echo GitHub Personal Access Token을 사용한 푸시
echo.
set /p TOKEN=GitHub Personal Access Token을 입력하세요:

echo.
echo 저장소 URL 설정 중...
git remote set-url origin https://wlstn9756-hub:%TOKEN%@github.com/wlstn9756-hub/adsk.git

echo.
echo GitHub에 푸시 중...
git push -u origin master

echo.
echo 보안을 위해 토큰 정보 제거 중...
git remote set-url origin https://github.com/wlstn9756-hub/adsk.git

echo.
echo 완료되었습니다!
pause