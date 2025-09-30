#!/bin/bash

echo "========================================="
echo "AdSketch 서버 설치 스크립트"
echo "========================================="

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# OS 확인
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
else
    echo -e "${RED}지원하지 않는 OS입니다.${NC}"
    exit 1
fi

echo -e "${GREEN}OS 감지: $OS${NC}"

# 1. 시스템 업데이트
echo -e "\n${YELLOW}1. 시스템 패키지 업데이트${NC}"
if [ "$OS" == "linux" ]; then
    sudo apt-get update
    sudo apt-get upgrade -y
else
    brew update
fi

# 2. Python 설치 확인
echo -e "\n${YELLOW}2. Python 설치 확인${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 설치 중..."
    if [ "$OS" == "linux" ]; then
        sudo apt-get install python3 python3-pip python3-venv -y
    else
        brew install python3
    fi
else
    echo -e "${GREEN}Python 이미 설치됨: $(python3 --version)${NC}"
fi

# 3. Chrome 및 ChromeDriver 설치
echo -e "\n${YELLOW}3. Chrome 및 ChromeDriver 설치${NC}"
if [ "$OS" == "linux" ]; then
    # Chrome 설치
    if ! command -v google-chrome &> /dev/null; then
        echo "Chrome 설치 중..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install google-chrome-stable -y
    else
        echo -e "${GREEN}Chrome 이미 설치됨${NC}"
    fi

    # ChromeDriver 설치
    echo "ChromeDriver 설치 중..."
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)

    # ChromeDriver 다운로드 URL 찾기
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

    if [ -z "$CHROMEDRIVER_VERSION" ]; then
        # 새로운 ChromeDriver 엔드포인트 사용
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION")
    fi

    wget -N "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -P /tmp
    unzip -o /tmp/chromedriver_linux64.zip -d /tmp
    sudo mv -f /tmp/chromedriver /usr/local/bin/chromedriver
    sudo chmod +x /usr/local/bin/chromedriver

    echo -e "${GREEN}ChromeDriver 설치 완료${NC}"
else
    # Mac용
    if ! command -v chromedriver &> /dev/null; then
        brew install --cask chromedriver
    fi
fi

# 4. 필요한 시스템 패키지 설치
echo -e "\n${YELLOW}4. 추가 시스템 패키지 설치${NC}"
if [ "$OS" == "linux" ]; then
    sudo apt-get install -y \
        xvfb \
        libxi6 \
        libgconf-2-4 \
        libnss3 \
        libxss1 \
        libxcomposite1 \
        libasound2 \
        libxtst6 \
        fonts-liberation \
        libappindicator3-1 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libgbm1
fi

# 5. Git 저장소 클론
echo -e "\n${YELLOW}5. 소스코드 다운로드${NC}"
if [ ! -d "adsk" ]; then
    git clone https://github.com/wlstn9756-hub/adsk.git
    cd adsk
else
    cd adsk
    git pull
fi

# 6. Python 가상환경 생성
echo -e "\n${YELLOW}6. Python 가상환경 생성${NC}"
python3 -m venv venv
source venv/bin/activate

# 7. Python 패키지 설치
echo -e "\n${YELLOW}7. Python 패키지 설치${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install selenium webdriver-manager

# 8. 환경 변수 설정 파일 생성
echo -e "\n${YELLOW}8. 환경 변수 설정${NC}"
cat > .env << EOL
# 서버 환경 설정
SERVER_ENV=production
CHROME_DRIVER_PATH=/usr/local/bin/chromedriver

# 데이터베이스
DATABASE_URL=sqlite:///final_complete_system.db

# 관리자 계정
ADMIN_USERNAME=adsketch
ADMIN_PASSWORD=doem1!

# 서버 설정
HOST=0.0.0.0
PORT=8000
EOL

echo -e "${GREEN}.env 파일 생성 완료${NC}"

# 9. systemd 서비스 파일 생성 (Linux만)
if [ "$OS" == "linux" ]; then
    echo -e "\n${YELLOW}9. 서비스 자동 시작 설정${NC}"

    sudo tee /etc/systemd/system/adsketch.service > /dev/null << EOL
[Unit]
Description=AdSketch Review Automation Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="SERVER_ENV=production"
ExecStart=$(pwd)/venv/bin/python naver_review_automation/final_complete_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl enable adsketch
    echo -e "${GREEN}서비스 등록 완료${NC}"
fi

# 10. 데이터베이스 초기화
echo -e "\n${YELLOW}10. 데이터베이스 초기화${NC}"
cd naver_review_automation
python create_admin.py

# 11. 테스트 실행
echo -e "\n${YELLOW}11. 서버 테스트 실행${NC}"
echo "서버를 테스트 모드로 실행합니다..."
timeout 10 python final_complete_system.py || true

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}설치 완료!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "서비스 시작 방법:"
if [ "$OS" == "linux" ]; then
    echo "  sudo systemctl start adsketch"
    echo ""
    echo "서비스 상태 확인:"
    echo "  sudo systemctl status adsketch"
    echo ""
    echo "로그 확인:"
    echo "  sudo journalctl -u adsketch -f"
else
    echo "  cd $(pwd)"
    echo "  source venv/bin/activate"
    echo "  cd naver_review_automation"
    echo "  python final_complete_system.py"
fi
echo ""
echo "접속 주소: http://서버IP:8000"
echo "관리자 계정: adsketch / doem1!"
echo ""