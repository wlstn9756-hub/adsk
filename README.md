# 📋 네이버 리뷰 관리 시스템 v2.0

## 🚀 새로운 기능

### 1. **리뷰 주문 접수 시스템**
- 고객이 직접 리뷰 작성을 주문할 수 있는 폼
- 플레이스 URL로 업체 정보 자동 추출
- 리뷰 개수, 작성 기간, 별점 분포 설정
- 필수 키워드 및 금지어 설정

### 2. **URL 중복 체크**
- 리뷰 URL 등록 시 자동 중복 검사
- URL 정규화를 통한 정확한 중복 감지
- 이미 등록된 리뷰 정보 표시

### 3. **모던 대시보드**
- 실시간 통계 (오늘 완료, 진행중, 대기중, 월 매출)
- 주문 상태별 필터링
- 진행률 시각화

## 📁 프로젝트 구조

```
adsketch/
├── naver_review_system/       # 메인 시스템
│   ├── main_integrated.py     # 통합 애플리케이션
│   ├── api_routes.py         # API 엔드포인트
│   ├── models_extended.py    # 추가 데이터베이스 모델
│   ├── templates/            # HTML 템플릿
│   │   ├── dashboard.html   # 대시보드
│   │   └── order_form.html  # 주문 접수 폼
│   └── requirements_extended.txt
├── run_local.bat             # 로컬 실행 스크립트
└── README.md

```

## 🛠️ 설치 및 실행

### 방법 1: 배치 파일 실행 (Windows)
```bash
# adsketch 폴더에서
run_local.bat
```

### 방법 2: 수동 실행
```bash
# 1. 프로젝트 폴더로 이동
cd C:\Users\wlstn\Desktop\adsketch\naver_review_system

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements_extended.txt

# 4. 서버 실행
python main_integrated.py
```

## 🌐 접속 정보

- **URL**: http://localhost:8000
- **대시보드**: http://localhost:8000/dashboard
- **주문 접수**: http://localhost:8000/order-form

### 초기 로그인 정보
- **ID**: admin
- **Password**: doemtmzpcl1!

## 📊 주요 API 엔드포인트

### 주문 관리
- `POST /api/v1/orders/create` - 주문 생성
- `GET /api/v1/orders` - 주문 목록
- `GET /api/v1/orders/{order_no}` - 주문 상세
- `PUT /api/v1/orders/{order_no}/status` - 상태 변경

### 리뷰 관리
- `POST /api/v1/reviews/check-duplicate` - URL 중복 체크
- `POST /add-review` - 리뷰 추가 (중복 체크 포함)
- `GET /reviews` - 리뷰 목록

### 대시보드
- `GET /api/v1/dashboard/stats` - 통계 정보

## 💡 주요 개선사항

1. **URL 중복 방지**
   - 동일한 리뷰 URL 재등록 차단
   - URL 정규화를 통한 정확한 중복 감지

2. **사용자 경험 개선**
   - Tailwind CSS를 활용한 모던한 UI
   - 실시간 진행률 표시
   - 반응형 디자인

3. **비즈니스 프로세스**
   - 주문 → 할당 → 작성 → 검수 → 완료
   - 자동 리뷰어 할당 (구현 예정)
   - 결제 시스템 연동 준비

## 🔒 보안

- JWT 기반 인증
- 비밀번호 bcrypt 해싱
- 역할 기반 접근 제어 (Admin/Client/Reviewer)

## 📝 테스트 시나리오

1. **주문 접수 테스트**
   - 주문 폼에서 플레이스 URL 입력
   - 리뷰 개수 선택 및 금액 확인
   - 주문 제출

2. **중복 체크 테스트**
   - 동일한 리뷰 URL 두 번 등록 시도
   - 중복 경고 메시지 확인

3. **대시보드 테스트**
   - 통계 정보 확인
   - 주문 목록 필터링
   - 상태별 조회

## 🚧 추후 개발 예정

- [ ] 리뷰어 자동 할당 시스템
- [ ] 결제 모듈 연동 (토스페이먼츠/아임포트)
- [ ] 이메일/SMS 알림
- [ ] 리뷰 품질 검수 시스템
- [ ] 통계 리포트 자동 생성

## 📞 문의

문제가 발생하면 다음을 확인하세요:
1. Python 3.8 이상 설치 확인
2. Chrome WebDriver 설치
3. 포트 8000번 사용 가능 확인

---
© 2024 네이버 리뷰 관리 시스템 v2.0