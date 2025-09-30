FROM python:3.9-slim

# Chrome 설치를 위한 필수 패키지
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1) \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# 작업 디렉토리 설정
WORKDIR /app

# requirements 먼저 복사 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install selenium webdriver-manager

# 소스코드 복사
COPY . .

# 환경변수 설정
ENV SERVER_ENV=production
ENV CHROME_DRIVER_PATH=/usr/local/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# 데이터 디렉토리 생성
RUN mkdir -p /app/data /app/logs

# 헬스체크 엔드포인트
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["python", "naver_review_automation/final_complete_system.py"]