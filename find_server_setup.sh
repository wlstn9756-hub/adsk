#!/bin/bash
# 서버 환경 확인 스크립트

echo "=== 1. 프로젝트 디렉토리 찾기 ==="
find / -name "final_complete_system.py" -type f 2>/dev/null | head -5

echo ""
echo "=== 2. Python 프로세스 확인 ==="
ps aux | grep python | grep -v grep

echo ""
echo "=== 3. 실행 중인 서비스 확인 ==="
systemctl list-units --type=service | grep -i naver

echo ""
echo "=== 4. 포트 사용 확인 (FastAPI 기본 8000번) ==="
netstat -tulpn | grep :8000

echo ""
echo "=== 5. crontab 확인 ==="
crontab -l 2>/dev/null || echo "No crontab"

echo ""
echo "=== 6. Git 저장소 찾기 ==="
find / -name ".git" -type d 2>/dev/null | head -5

echo ""
echo "=== 7. 홈 디렉토리 내용 ==="
ls -la ~/

echo ""
echo "=== 8. /opt 디렉토리 확인 ==="
ls -la /opt/ 2>/dev/null || echo "No /opt directory"

echo ""
echo "=== 9. /var/www 디렉토리 확인 ==="
ls -la /var/www/ 2>/dev/null || echo "No /var/www directory"
