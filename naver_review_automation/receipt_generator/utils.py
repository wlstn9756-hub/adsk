# 영수증 시스템 공통 유틸리티 함수들

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# 셀렉터 상수들 (모바일/데스크톱 모두 지원)
NICKNAME_SELECTORS = [
    # 모바일 셀렉터
    ".pui__PlaceDetailHeader--author", ".pui__PlaceDetailReviewItem--author", ".author", ".user",
    # 기존 데스크톱 셀렉터
    "h1._6MtIQ_", "._6MtIQ_", ".review_user_name", ".user_name", ".reviewer_name", ".author_name", ".nickname"
]
DATE_SELECTORS = [
    # 모바일 셀렉터
    ".pui__PlaceDetailReviewItem--date", ".pui__date", ".date", 
    # 기존 데스크톱 셀렉터
    'time[aria-hidden="true"]', 'time', '.pui__X35jYm', '.review-date',
    # 추가 셀렉터
    'span.pui__X35jYm', '[class*="date"]', '[class*="time"]', '.review_date', '.review-time'
]
CONTENT_SELECTORS = [
    # 모바일 셀렉터
    ".pui__PlaceDetailReviewItem--content", ".pui__content", ".content", ".review-text",
    # 기존 데스크톱 셀렉터
    'a[role="button"][data-pui-click-code="otherreviewfeed.rvshowmore"]', '.review-content', '.review_content', '[class*="content"]'
]
BUSINESS_SELECTORS = [
    # 모바일 셀렉터
    ".pui__PlaceDetailHeader--title", ".pui__title", ".place-title",
    # 기존 데스크톱 셀렉터
    'h1', '.place_fixed_maintit', '.GHAhO', '.Fc1rA', '[data-testid="place-name"]', 'span.pui__pv1E2a'
]
REVIEW_CONTAINER_SELECTORS = [
    # 모바일 셀렉터
    ".pui__PlaceDetailReviewItem", ".pui__review-item", ".review-item",
    # 기존 데스크톱 셀렉터
    '[data-reviewid]', '.place_section_content', '.review_item', '.ugc-review-list__item', '[class*="review"]'
]

def create_chrome_driver():
    """ChromeDriver 인스턴스 생성"""
    print("[DEBUG] ChromeDriver 생성 시작...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Windows에서 추가 옵션
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        if os.path.exists('./chromedriver.exe'):
            print("[DEBUG] chromedriver.exe 사용")
            service = Service('./chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("[DEBUG] 시스템 ChromeDriver 사용")
            driver = webdriver.Chrome(options=chrome_options)
        
        print("[DEBUG] ChromeDriver 생성 완료")
        return driver
    except Exception as e:
        print(f"[ERROR] ChromeDriver 생성 실패: {str(e)}")
        raise

def resolve_short_url(url):
    """단축 URL을 실제 URL로 변환"""
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return url

def extract_element_text(container, selectors):
    """여러 셀렉터로 요소에서 텍스트 추출"""
    from selenium.webdriver.common.by import By
    
    for selector in selectors:
        try:
            element = container.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            if text and len(text) > 0:
                return text
        except:
            continue
    return None

def check_deleted_keywords(page_source):
    """페이지에서 삭제 키워드 확인"""
    deleted_keywords = [
        "삭제된", "delete", "removed", "찾을 수 없", "존재하지 않", 
        "더 이상 사용할 수 없", "노출중단", "서비스 종료"
    ]
    
    page_source_lower = page_source.lower()
    for keyword in deleted_keywords:
        if keyword in page_source_lower:
            print(f"[WARNING] 삭제 키워드 감지: {keyword}")
            return True
    return False

def check_normal_keywords(page_source):
    """페이지에서 정상 리뷰 키워드 확인"""
    normal_keywords = [
        "리뷰", "review", "별점", "평점", "맛있", "좋았", "추천", 
        "방문", "먹었", "다녀왔", "가격", "음식", "서비스"
    ]
    
    page_source_lower = page_source.lower()
    for keyword in normal_keywords:
        if keyword in page_source_lower:
            return True
    return False

def validate_file_upload(file, allowed_extensions=None):
    """파일 업로드 유효성 검증"""
    if allowed_extensions is None:
        allowed_extensions = ('.xlsx', '.xls', '.csv')
    
    if not file or file.filename == '':
        return False, '파일이 선택되지 않았습니다.'
    
    if not file.filename.lower().endswith(allowed_extensions):
        return False, f'{", ".join(allowed_extensions)} 파일만 업로드 가능합니다.'
    
    return True, None

def is_date_match(target_date, container_date):
    """두 날짜가 매칭되는지 확인 (다양한 형식 지원)"""
    import re
    
    if not target_date or not container_date:
        print(f"[DEBUG] 날짜 매칭 실패 - 빈 값: target={target_date}, container={container_date}")
        return False
    
    print(f"[DEBUG] 날짜 매칭 시도: '{target_date}' vs '{container_date}'")
    
    # 정확한 매칭
    if target_date == container_date:
        print(f"[DEBUG] 정확한 매칭 성공!")
        return True
    
    # 부분 매칭
    if target_date in container_date or container_date in target_date:
        print(f"[DEBUG] 부분 매칭 성공!")
        return True
    
    # 날짜 형식 변환 매칭
    # 다양한 날짜 패턴 지원
    date_patterns = [
        r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})',  # 2024-07-02, 2024.07.02, 2024/07/02
        r'(\d{1,2})\.(\d{1,2})\.[가-힣]*',      # 7.2.수, 7.2.월
        r'(\d{1,2})\.(\d{1,2})\.?',             # 7.2., 7.2
        r'(\d{1,2})월\s*(\d{1,2})일',            # 7월 2일
        r'(\d{1,2})/(\d{1,2})',                   # 7/2
        r'(\d{1,2})-(\d{1,2})',                   # 7-2
    ]
    
    target_month, target_day = None, None
    container_month, container_day = None, None
    
    # 목표 날짜에서 월/일 추출
    for pattern in date_patterns:
        match = re.search(pattern, target_date)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # 년-월-일
                target_month, target_day = int(groups[1]), int(groups[2])
            elif len(groups) == 2:  # 월-일
                target_month, target_day = int(groups[0]), int(groups[1])
            if target_month and target_day:
                break
    
    # 컨테이너 날짜에서 월/일 추출
    for pattern in date_patterns:
        match = re.search(pattern, container_date)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # 년-월-일
                container_month, container_day = int(groups[1]), int(groups[2])
            elif len(groups) == 2:  # 월-일
                container_month, container_day = int(groups[0]), int(groups[1])
            if container_month and container_day:
                break
    
    # 월/일이 모두 매칭되면 같은 날짜
    if (target_month and target_day and container_month and container_day and
        target_month == container_month and target_day == container_day):
        print(f"[DEBUG] 월/일 매칭 성공: {target_month}/{target_day}")
        return True
    
    # 숫자만 추출해서 비교 (마지막 시도)
    target_numbers = re.findall(r'\d+', target_date)
    container_numbers = re.findall(r'\d+', container_date)
    
    if len(target_numbers) >= 2 and len(container_numbers) >= 2:
        # 월과 일만 비교 (년도 제외)
        if target_numbers[-2:] == container_numbers[-2:]:
            print(f"[DEBUG] 숫자 매칭 성공: {target_numbers[-2:]}")
            return True
    
    print(f"[DEBUG] 모든 매칭 실패: target_month={target_month}, target_day={target_day}, container_month={container_month}, container_day={container_day}")
    return False

def remove_image_metadata(image_file):
    """이미지 파일의 모든 메타데이터 제거"""
    from PIL import Image
    import piexif
    
    try:
        # 이미지 열기 (파일 객체 또는 경로 모두 지원)
        img = Image.open(image_file)
        
        # 새로운 이미지로 다시 저장 (메타데이터 없이)
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        
        return image_without_exif
    except Exception as e:
        print(f"[ERROR] 메타데이터 제거 실패: {str(e)}")
        return None

def parse_text_to_files(text_content):
    """텍스트 내용을 개별 파일로 분리
    형식: 숫자. 원고 내용
    """
    import re
    
    files = {}
    
    # 줄바꿈으로 분리
    lines = text_content.strip().split('\n')
    current_number = None
    current_content = []
    
    for line in lines:
        # 숫자. 으로 시작하는 라인 찾기
        match = re.match(r'^(\d+)\.\s*(.*)$', line.strip())
        if match:
            # 이전 번호의 내용 저장
            if current_number is not None:
                filename = f"{current_number}.txt"
                files[filename] = '\n'.join(current_content).strip()
            
            # 새로운 번호 시작
            current_number = match.group(1)
            content = match.group(2)
            current_content = [content] if content else []
        else:
            # 현재 번호의 내용에 추가
            if current_number is not None and line.strip():
                current_content.append(line.strip())
    
    # 마지막 번호의 내용 저장
    if current_number is not None:
        filename = f"{current_number}.txt"
        files[filename] = '\n'.join(current_content).strip()
    
    return files

def create_receipt_package_zip(receipt_images, photo_images=None, text_files=None, store_name="", date_str=""):
    """영수증, 사진, 텍스트를 포함한 압축 패키지 생성"""
    import zipfile
    import io
    from datetime import datetime
    
    # 메모리상에 zip 파일 생성
    zip_buffer = io.BytesIO()
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%H%M%S")
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 영수증 추가
        for idx, (img_data, filename) in enumerate(receipt_images):
            if isinstance(img_data, io.BytesIO):
                img_data.seek(0)
                zip_file.writestr(f"receipts/{filename}", img_data.read())
            
        # 사진 추가 (메타데이터 제거됨)
        if photo_images:
            for idx, (img_data, original_name) in enumerate(photo_images):
                if isinstance(img_data, io.BytesIO):
                    img_data.seek(0)
                    # 원본 파일명의 확장자 유지
                    ext = original_name.split('.')[-1] if '.' in original_name else 'jpg'
                    zip_file.writestr(f"photos/{idx+1}.{ext}", img_data.read())
        
        # 텍스트 파일 추가
        if text_files:
            for filename, content in text_files.items():
                zip_file.writestr(f"texts/{filename}", content.encode('utf-8'))
    
    zip_buffer.seek(0)
    
    # 압축 파일명
    zip_filename = f"{store_name}_{date_str}_{timestamp}.zip"
    
    return zip_buffer, zip_filename