# AdSketch 배포 가이드

## 서버 요구사항
- Ubuntu 18.04 이상
- Python 3.8 이상
- 최소 2GB RAM
- 최소 10GB 디스크 공간

## 자동 설치 스크립트 사용

### 1. 서버에 연결
```bash
ssh root@your-server-ip
```

### 2. 저장소 클론
```bash
cd /var/www
git clone https://github.com/wlstn9756-hub/adsk.git adsketch
cd adsketch
```

### 3. 자동 설치 실행
```bash
chmod +x server_setup.sh
./server_setup.sh
```

## 수동 설치

### 1. 시스템 업데이트
```bash
apt update && apt upgrade -y
```

### 2. Python 설치
```bash
apt install python3 python3-pip python3-venv -y
```

### 3. Chrome 설치
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update
apt install google-chrome-stable -y
```

### 4. ChromeDriver 설치
```bash
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

### 5. 프로젝트 설정
```bash
cd /var/www/adsketch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Systemd 서비스 설정

### 1. 서비스 파일 복사
```bash
sudo cp adsketch.service /etc/systemd/system/
```

### 2. 서비스 활성화 및 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable adsketch
sudo systemctl start adsketch
```

### 3. 서비스 상태 확인
```bash
sudo systemctl status adsketch
```

### 4. 로그 확인
```bash
sudo journalctl -u adsketch -f
```

## 서비스 관리 명령어
```bash
# 서비스 시작
sudo systemctl start adsketch

# 서비스 중지
sudo systemctl stop adsketch

# 서비스 재시작
sudo systemctl restart adsketch

# 부팅시 자동 시작 활성화
sudo systemctl enable adsketch

# 부팅시 자동 시작 비활성화
sudo systemctl disable adsketch
```

## 수동 실행 (테스트용)
```bash
cd /var/www/adsketch/naver_review_automation
source /var/www/adsketch/venv/bin/activate
python final_complete_system.py
```

## 도메인 설정 (선택사항)

### Nginx 설정
```bash
# Nginx 설치
sudo apt install nginx -y

# 설정 파일 생성
sudo nano /etc/nginx/sites-available/adsketch

# 설정 내용
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/adsketch /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### SSL 인증서 설정 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 접속 정보
- URL: http://your-server-ip:8000 (또는 도메인)
- 관리자 계정: adsketch / doem1!

## 보안 설정
- 방화벽 규칙 설정
- fail2ban 설치
- 정기 백업 스크립트
- 환경 변수로 민감 정보 관리

## 모니터링
- Uptime 모니터링 서비스
- 에러 로깅 설정
- 트래픽 분석