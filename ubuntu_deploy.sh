#!/bin/bash

# AdSketch Ubuntu 서버 배포 스크립트
# Ubuntu 18.04+ 전용 간단 배포 스크립트
# 사용법: chmod +x ubuntu_deploy.sh && ./ubuntu_deploy.sh

set -e

echo "🚀 AdSketch Ubuntu 서버 배포를 시작합니다..."

# 1. 시스템 업데이트
echo "📦 시스템 업데이트 중..."
apt update && apt upgrade -y

# 2. 필수 패키지 설치
echo "🔧 필수 패키지 설치 중..."
apt install -y python3 python3-pip python3-venv curl wget unzip gnupg software-properties-common git nginx ufw

# 3. Chrome 설치
echo "🌐 Google Chrome 설치 중..."
if ! command -v google-chrome &> /dev/null; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt update
    apt install -y google-chrome-stable
else
    echo "✅ Chrome 이미 설치됨"
fi

# 4. ChromeDriver 설치
echo "🚗 ChromeDriver 설치 중..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
LATEST_CHROMEDRIVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# 5. 프로젝트 디렉토리 설정
echo "📁 프로젝트 디렉토리 설정 중..."
mkdir -p /var/www/adsketch
cd /var/www/adsketch

# 6. Git clone 또는 업데이트
if [ ! -d ".git" ]; then
    echo "📥 소스코드 다운로드 중..."
    git clone https://github.com/wlstn9756-hub/adsk.git .
else
    echo "🔄 소스코드 업데이트 중..."
    git pull
fi

# 7. Python 가상환경 설정
echo "🐍 Python 가상환경 설정 중..."
python3 -m venv venv
source venv/bin/activate

# 8. 의존성 설치
echo "📚 Python 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 9. 필요한 디렉토리 생성
echo "📂 필요한 디렉토리 생성 중..."
mkdir -p data logs

# 10. systemd 서비스 파일 복사 및 설정
echo "🔧 시스템 서비스 설정 중..."
if [ -f "adsketch.service" ]; then
    cp adsketch.service /etc/systemd/system/
else
    # 서비스 파일이 없는 경우 생성
    cat > /etc/systemd/system/adsketch.service << EOF
[Unit]
Description=AdSketch Review Management System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/var/www/adsketch
Environment=PATH=/var/www/adsketch/venv/bin
Environment=PYTHONPATH=/var/www/adsketch
Environment=SERVER_ENV=production
Environment=DATABASE_PATH=/var/www/adsketch/data/final_complete_system.db
Environment=CHROME_DRIVER_PATH=/usr/local/bin/chromedriver
ExecStart=/var/www/adsketch/venv/bin/python /var/www/adsketch/naver_review_automation/final_complete_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
fi

# 11. 서비스 활성화 및 시작
echo "✅ 서비스 활성화 중..."
systemctl daemon-reload
systemctl enable adsketch
systemctl start adsketch

# 12. Nginx 설정 (선택사항)
echo "🌐 Nginx 설정 중..."
cat > /etc/nginx/sites-available/adsketch << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Nginx 사이트 활성화
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
fi
ln -sf /etc/nginx/sites-available/adsketch /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# 13. 방화벽 설정
echo "🔥 방화벽 설정 중..."
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # 직접 접속용
ufw --force enable

# 14. 서비스 상태 확인
echo "🔍 서비스 상태 확인 중..."
sleep 5

# 서비스 상태 체크
if systemctl is-active --quiet adsketch; then
    echo "✅ AdSketch 서비스 정상 실행 중"
else
    echo "❌ AdSketch 서비스 실행 실패 - 로그를 확인하세요"
    echo "로그 확인: journalctl -u adsketch -f"
fi

# 15. 최종 정보 출력
echo ""
echo "🎉 AdSketch 배포가 완료되었습니다!"
echo ""
echo "📋 접속 정보:"
echo "- 직접 접속: http://$(curl -s ifconfig.me):8000"
echo "- Nginx 프록시: http://$(curl -s ifconfig.me)"
echo "- 관리자 계정: adsketch / doem1!"
echo ""
echo "🔧 유용한 명령어:"
echo "- 서비스 상태: systemctl status adsketch"
echo "- 로그 실시간: journalctl -u adsketch -f"
echo "- 서비스 재시작: systemctl restart adsketch"
echo "- 서비스 중지: systemctl stop adsketch"
echo ""
echo "🌐 도메인 연결을 원하는 경우:"
echo "1. DNS A 레코드를 $(curl -s ifconfig.me)로 설정"
echo "2. /etc/nginx/sites-available/adsketch 에서 server_name 수정"
echo "3. systemctl restart nginx"
echo "4. SSL 인증서 설치: apt install certbot python3-certbot-nginx -y && certbot --nginx"
echo ""