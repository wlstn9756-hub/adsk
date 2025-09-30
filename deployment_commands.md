# AdSketch 배포 명령어 모음

## 빠른 배포 (Ubuntu 서버)

### 1. 서버 접속
```bash
ssh root@165.22.101.45
# 또는 사용자 도메인 서버
ssh root@your-server-ip
```

### 2. 원클릭 배포
```bash
cd /var/www
git clone https://github.com/wlstn9756-hub/adsk.git adsketch
cd adsketch
chmod +x ubuntu_deploy.sh
./ubuntu_deploy.sh
```

## 서비스 관리 명령어

### 서비스 상태 확인
```bash
systemctl status adsketch
```

### 서비스 시작/중지/재시작
```bash
systemctl start adsketch
systemctl stop adsketch
systemctl restart adsketch
```

### 실시간 로그 보기
```bash
journalctl -u adsketch -f
```

### 부팅시 자동 시작 설정
```bash
systemctl enable adsketch
systemctl disable adsketch  # 비활성화
```

## 도메인 연결 (sketchreview.co.kr)

### 1. DNS 설정 (가비아)
- A 레코드: @ → 서버 IP 주소
- CNAME 레코드: www → 메인 도메인

### 2. Nginx 설정 수정
```bash
nano /etc/nginx/sites-available/adsketch
```

```nginx
server {
    listen 80;
    server_name sketchreview.co.kr www.sketchreview.co.kr;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Nginx 재시작
```bash
nginx -t
systemctl restart nginx
```

### 4. SSL 인증서 설치 (선택사항)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d sketchreview.co.kr -d www.sketchreview.co.kr
```

## 문제 해결

### 서비스 실행 실패시
```bash
# 로그 확인
journalctl -u adsketch -n 50

# 수동 실행으로 에러 확인
cd /var/www/adsketch
source venv/bin/activate
cd naver_review_automation
python final_complete_system.py
```

### 포트 충돌시
```bash
# 포트 사용 확인
netstat -tulpn | grep :8000

# 프로세스 종료
pkill -f final_complete_system.py
```

### Chrome/ChromeDriver 문제시
```bash
# Chrome 버전 확인
google-chrome --version

# ChromeDriver 재설치
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(google-chrome --version | grep -oP '\d+' | head -1)/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

## 업데이트 방법

### 1. 코드 업데이트
```bash
cd /var/www/adsketch
git pull
```

### 2. 의존성 업데이트 (필요시)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 서비스 재시작
```bash
systemctl restart adsketch
```

## 백업 및 복원

### 데이터베이스 백업
```bash
cp /var/www/adsketch/data/final_complete_system.db /var/www/adsketch/backup_$(date +%Y%m%d).db
```

### 전체 프로젝트 백업
```bash
tar -czf adsketch_backup_$(date +%Y%m%d).tar.gz /var/www/adsketch
```

## 모니터링

### 서버 리소스 확인
```bash
top
htop  # 설치 필요: apt install htop
```

### 디스크 사용량
```bash
df -h
du -sh /var/www/adsketch
```

### 메모리 사용량
```bash
free -h
```

## 방화벽 설정

### 포트 허용
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # AdSketch 직접 접속
```

### 방화벽 상태 확인
```bash
ufw status
```

## 접속 정보
- **직접 접속**: http://서버IP:8000
- **도메인 접속**: http://sketchreview.co.kr (DNS 설정 후)
- **관리자 계정**: adsketch / doem1!