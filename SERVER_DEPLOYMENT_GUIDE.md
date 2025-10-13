# 서버 배포 가이드

## 수정 사항 요약

### 변경된 파일
- `naver_review_automation/real_review_extractor.py`

### 주요 개선 사항
1. **상세한 로깅 추가**: 각 단계에서 상세한 로그 출력으로 디버깅 용이성 향상
2. **페이지 로딩 대기 시간 증가**: 3초 → 4초로 증가하여 안정성 향상
3. **에러 핸들링 강화**: 예외 타입 및 상세 정보 로깅
4. **리뷰 블록 검증**: 페이지 구조 변경 감지 기능 추가
5. **업체명 디버깅**: 발견된 모든 업체명 로깅으로 매칭 문제 진단 지원
6. **대체 선택자**: 추출 실패 시 대체 선택자로 재시도

---

## 서버 배포 방법

### 방법 1: Git Pull (권장)

```bash
# 서버에 SSH 접속
ssh user@your-server-ip

# 프로젝트 디렉토리로 이동
cd /path/to/adsketch

# 최신 코드 가져오기
git pull origin main

# 서비스 재시작
sudo systemctl restart naver-review-automation
```

### 방법 2: 직접 파일 복사

서버에서 Git을 사용하지 않는 경우:

```bash
# 로컬에서 수정된 파일을 서버로 복사
scp naver_review_automation/real_review_extractor.py user@your-server-ip:/path/to/adsketch/naver_review_automation/

# 서버에 SSH 접속하여 서비스 재시작
ssh user@your-server-ip
sudo systemctl restart naver-review-automation
```

---

## 배포 후 확인 사항

### 1. 서비스 상태 확인
```bash
sudo systemctl status naver-review-automation
```

예상 출력: `Active: active (running)`

### 2. 로그 확인
```bash
# 실시간 로그 모니터링
sudo journalctl -u naver-review-automation -f

# 최근 100줄 로그 확인
sudo journalctl -u naver-review-automation -n 100
```

### 3. 추출 기능 테스트

관리자 대시보드에서:
1. 리뷰 목록 페이지 접속
2. "추출" 버튼 클릭
3. 로그에서 다음 메시지 확인:
   - `페이지 로딩 시작: ...`
   - `리뷰 블록 X개 발견`
   - `발견된 업체명들: [...]`
   - `리뷰 본문 추출 성공: ...`
   - `영수증 날짜 추출: ...`

### 4. 에러 발생 시 확인할 로그

이제 더 상세한 에러 정보가 로깅됩니다:

```bash
# 에러 로그만 필터링
sudo journalctl -u naver-review-automation | grep ERROR
```

주요 에러 메시지:
- `Selenium 설정 실패, HTTP 방식으로 전환`: Chrome 드라이버 문제
- `리뷰 블록을 찾을 수 없습니다`: 페이지 구조 변경 또는 로딩 문제
- `업체명 'XXX'과 일치하는 리뷰를 찾을 수 없습니다`: 업체명 불일치

---

## 문제 해결

### Chrome 드라이버 설치 확인

서버에서 Chrome과 ChromeDriver가 설치되어 있는지 확인:

```bash
# Chrome 설치 확인
google-chrome --version

# ChromeDriver 설치 확인
chromedriver --version
```

설치되지 않은 경우:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver

# 또는 Chrome 직접 설치
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# ChromeDriver 설치
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
LATEST=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 추출 실패 시 체크리스트

1. **Chrome 드라이버 상태**
   - Chrome과 ChromeDriver 버전 호환성 확인
   - `chromedriver --version` 실행 가능 여부

2. **네트워크 연결**
   - 서버에서 네이버 접속 가능 여부: `curl https://m.place.naver.com`

3. **메모리 및 리소스**
   - Chrome은 메모리를 많이 사용: `free -h`로 메모리 확인

4. **로그 분석**
   - `발견된 업체명들` 로그에서 실제 업체명 확인
   - DB의 업체명과 정확히 일치하는지 확인 (공백, 특수문자 주의)

5. **페이지 로딩 시간**
   - 서버 네트워크가 느린 경우 `time.sleep(4)`를 더 늘릴 수 있음
   - `real_review_extractor.py`의 107번째 줄과 63번째 줄

---

## 성능 최적화 (선택사항)

### Chrome 메모리 사용량 줄이기

`real_review_extractor.py`의 `setup_selenium()` 함수에 추가 옵션:

```python
options.add_argument('--disable-extensions')
options.add_argument('--disable-images')  # 이미지 로딩 비활성화
options.add_argument('--single-process')  # 단일 프로세스 모드
```

### 추출 타임아웃 조정

페이지 로딩이 너무 느린 경우:

```python
# real_review_extractor.py 107번째 줄
time.sleep(5)  # 4초 → 5초로 증가
```

---

## 롤백 방법

문제 발생 시 이전 버전으로 복구:

```bash
cd /path/to/adsketch
git log --oneline -5  # 최근 5개 커밋 확인
git revert 06582b8    # 최신 커밋 되돌리기
sudo systemctl restart naver-review-automation
```

---

## 지원

문제가 계속되면 다음 정보를 포함하여 문의:

1. 서버 로그 (최근 100줄):
   ```bash
   sudo journalctl -u naver-review-automation -n 100 > logs.txt
   ```

2. Chrome/ChromeDriver 버전:
   ```bash
   google-chrome --version
   chromedriver --version
   ```

3. 서버 환경:
   ```bash
   uname -a
   cat /etc/os-release
   ```

4. 추출 시도한 리뷰 URL 및 업체명
