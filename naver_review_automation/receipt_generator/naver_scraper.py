import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import subprocess
import os

def get_chrome_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 백그라운드 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

    # Google API 관련 오류 방지 (QUOTA_EXCEEDED 오류 해결)
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--safebrowsing-disable-auto-update")
    chrome_options.add_argument("--disable-features=MediaRouter")
    chrome_options.add_argument("--disable-features=OptimizationHints")

    # 로그 레벨 설정 (불필요한 로그 최소화)
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        # ChromeDriver 자동 설치 및 사용
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 최신 ChromeDriver 강제 다운로드
        service = ChromeService(ChromeDriverManager(driver_cache_valid_range=1).install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 자동화 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"ChromeDriver 설정 실패: {e}")
        
        # 백업: 시스템 ChromeDriver 사용 시도
        try:
            print("시스템 ChromeDriver 사용 시도...")
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e2:
            print(f"시스템 ChromeDriver도 실패: {e2}")
            return None

def extract_place_info_from_url(url):
    """URL에서 플레이스 정보 추출"""
    try:
        # m.place.naver.com/restaurant/1207475613 형태
        if 'm.place.naver.com' in url:
            parts = url.split('/')
            if len(parts) >= 5:
                business_type = parts[3]  # restaurant, hospital, place 등
                place_id = parts[4].split('?')[0]
                return business_type, place_id
        
        # place.naver.com/place/1234567890 형태
        elif 'place.naver.com' in url:
            place_id = url.split('/')[-1].split('?')[0]
            return 'place', place_id
        
        # map.naver.com에서 place ID 추출
        elif 'map.naver.com' in url:
            if 'place/' in url:
                place_id = url.split('place/')[-1].split('/')[0].split('?')[0]
                return 'place', place_id
        
        return None, None
    except:
        return None, None

def extract_operating_hours(driver):
    """영업시간 정보 추출"""
    try:
        print("영업시간 정보 추출 시작...")
        
        # 1단계: 영업시간 펼쳐보기 버튼 클릭
        try:
            print("영업시간 펼쳐보기 버튼 찾기...")
            
            # 모든 클릭 가능한 요소들 확인
            all_buttons = driver.find_elements(By.CSS_SELECTOR, "a, button, [role='button']")
            print(f"전체 클릭 가능 요소 {len(all_buttons)}개 발견")
            
            # 정확한 펼쳐보기 버튼 찾기
            expand_buttons = driver.find_elements(By.CSS_SELECTOR, "a.gKP9i.RMgN0")
            print(f"a.gKP9i.RMgN0 버튼 {len(expand_buttons)}개 발견")
            
            # 대안 선택자들도 시도
            alt_selectors = [
                "a.gKP9i",
                ".gKP9i.RMgN0", 
                "[role='button']",
                "a[aria-expanded]"
            ]
            
            for selector in alt_selectors:
                alt_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{selector} 버튼 {len(alt_buttons)}개 발견")
                if alt_buttons:
                    expand_buttons.extend(alt_buttons)
            
            for i, button in enumerate(expand_buttons):
                try:
                    # 영업시간 관련 버튼인지 확인 (주변 텍스트로 판단)
                    parent_text = button.text.strip()
                    print(f"버튼 {i+1} 텍스트: '{parent_text}'")
                    
                    # 영업시간 키워드가 있거나, time 태그가 있으면 클릭
                    time_elements = button.find_elements(By.CSS_SELECTOR, "time")
                    has_time = len(time_elements) > 0
                    print(f"  time 태그 {len(time_elements)}개 포함")
                    
                    if ('영업' in parent_text or '시작' in parent_text or has_time):
                        print(f"영업시간 관련 버튼 발견! 클릭 시도")
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(3)  # 로딩 대기
                        print("펼쳐보기 버튼 클릭 완료")
                        break
                except Exception as e:
                    print(f"버튼 {i+1} 클릭 시도 중 오류: {e}")
                    continue
        except Exception as e:
            print(f"펼쳐보기 버튼 처리 중 오류: {e}")
        
        # 2단계: 영업시간 정보 추출
        operating_hours = None
        
        print("영업시간 텍스트 추출 시작...")
        
        # H3ua4 클래스에서 영업시간 찾기 (가장 정확한 방법)
        try:
            # 더 넓은 범위의 요소들 확인
            all_selectors = [
                ".H3ua4",
                "[class*='H3ua4']", 
                "div[class*='time']",
                "div[class*='hour']",
                "div[class*='biz']",
                ".A_cdD",
                ".y6tNq"
            ]
            
            for selector in all_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{selector} 요소 {len(elements)}개 발견")
                
                for i, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        if text and len(text) > 0:
                            print(f"{selector}[{i}] 텍스트: '{text[:100]}...'")
                            
                            # 시간 패턴이 있는지 확인
                            time_patterns = [
                                r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})',  # 11:00 - 23:00
                                r'(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})',  # 11:00~23:00
                                r'(\d{1,2})시\s*-\s*(\d{1,2})시'  # 11시-23시
                            ]
                            
                            for pattern in time_patterns:
                                match = re.search(pattern, text)
                                if match:
                                    start_hour = int(match.group(1))
                                    start_min = int(match.group(2)) if ':' in pattern else 0
                                    end_hour = int(match.group(3))
                                    end_min = int(match.group(4)) if ':' in pattern else 0
                                    
                                    operating_hours = {
                                        'start_hour': start_hour,
                                        'start_minute': start_min,
                                        'end_hour': end_hour,
                                        'end_minute': end_min,
                                        'raw_text': f"{start_hour}:{start_min:02d} - {end_hour}:{end_min:02d}"
                                    }
                                    
                                    print(f"영업시간 추출 성공: {operating_hours['raw_text']}")
                                    return operating_hours
                            
                    except Exception as e:
                        print(f"{selector}[{i}] 처리 중 오류: {e}")
                        continue
                        
        except Exception as e:
            print(f"요소 탐색 중 오류: {e}")
        
        # 3단계: time 태그에서 시작시간만 추출 (백업)
        if not operating_hours:
            try:
                time_elements = driver.find_elements(By.CSS_SELECTOR, "time[aria-hidden='true']")
                print(f"time 태그 {len(time_elements)}개 발견")
                
                for i, element in enumerate(time_elements):
                    try:
                        text = element.text.strip()
                        print(f"time[{i}] 텍스트: '{text}'")
                        
                        # "11:00에 영업 시작" 패턴
                        start_pattern = r'(\d{1,2}):(\d{2})에\s*영업\s*시작'
                        match = re.search(start_pattern, text)
                        
                        if match:
                            start_hour = int(match.group(1))
                            start_min = int(match.group(2))
                            # 기본 종료시간 설정 (시작 + 10시간, 최대 23시)
                            end_hour = min(start_hour + 10, 23)
                            end_min = 0
                            
                            operating_hours = {
                                'start_hour': start_hour,
                                'start_minute': start_min,
                                'end_hour': end_hour,
                                'end_minute': end_min,
                                'raw_text': f"{start_hour}:{start_min:02d}에 영업 시작 (종료: {end_hour}:{end_min:02d})"
                            }
                            
                            print(f"시작시간만 추출: {operating_hours['raw_text']}")
                            return operating_hours
                            
                    except Exception as e:
                        print(f"time[{i}] 처리 중 오류: {e}")
                        continue
                        
            except Exception as e:
                print(f"time 태그 처리 중 오류: {e}")
        
        # 4단계: 페이지 소스에서 직접 추출 (최후의 수단)
        if not operating_hours:
            print("페이지 소스에서 영업시간 패턴 직접 찾기...")
            try:
                page_source = driver.page_source
                print(f"페이지 소스 길이: {len(page_source)}자")
                
                # 모든 가능한 시간 패턴들을 찾기
                all_time_patterns = [
                    r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})',  # 11:00 - 23:00
                    r'(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})',  # 11:00~23:00
                    r'(\d{1,2})시\s*-\s*(\d{1,2})시',  # 11시-23시
                    r'(\d{1,2})시\s*~\s*(\d{1,2})시'   # 11시~23시
                ]
                
                print("모든 시간 패턴 검색 중...")
                for i, pattern in enumerate(all_time_patterns):
                    matches = re.findall(pattern, page_source)
                    print(f"패턴 {i+1} ({pattern}): {len(matches)}개 매칭")
                    
                    for j, match in enumerate(matches[:5]):  # 최대 5개까지만 확인
                        try:
                            start_hour = int(match[0])
                            start_min = int(match[1]) if len(match) > 1 and match[1] else 0
                            end_hour = int(match[2]) if len(match) > 2 else int(match[1])
                            end_min = int(match[3]) if len(match) > 3 and match[3] else 0
                            
                            # 유효한 시간인지 확인
                            if 0 <= start_hour <= 23 and 0 <= end_hour <= 24 and start_hour < end_hour:
                                operating_hours = {
                                    'start_hour': start_hour,
                                    'start_minute': start_min,
                                    'end_hour': end_hour,
                                    'end_minute': end_min,
                                    'raw_text': f"{start_hour}:{start_min:02d} - {end_hour}:{end_min:02d}"
                                }
                                
                                print(f"소스에서 영업시간 추출 성공: {operating_hours['raw_text']}")
                                return operating_hours
                                
                        except (ValueError, IndexError) as e:
                            print(f"매칭 결과 파싱 오류: {e}")
                            continue
                
                # H3ua4 관련 텍스트도 더 넓게 검색
                h3ua4_contexts = re.findall(r'H3ua4[^>]*>([^<]+)', page_source, re.IGNORECASE)
                print(f"H3ua4 컨텍스트 {len(h3ua4_contexts)}개 발견")
                
                for i, context in enumerate(h3ua4_contexts):
                    print(f"H3ua4 컨텍스트 {i}: '{context[:50]}...'")
                        
            except Exception as e:
                print(f"페이지 소스 분석 중 오류: {e}")
        
        # 5단계: 기본값 반환 (테스트용)
        if not operating_hours:
            print("영업시간 추출 실패, 기본값 사용")
            operating_hours = {
                'start_hour': 11,
                'start_minute': 0,
                'end_hour': 21,
                'end_minute': 0,
                'raw_text': "11:00 - 21:00 (기본값)"
            }
            return operating_hours
        
        print("영업시간 정보를 찾을 수 없습니다.")
        return None
        
    except Exception as e:
        print(f"영업시간 추출 중 오류: {e}")
        return None

def scrape_naver_place_info_selenium(url):
    """Selenium을 사용한 네이버 플레이스 정보 스크래핑 (메뉴 + 영업시간)"""
    driver = None
    try:
        driver = get_chrome_driver()
        if not driver:
            return {'menu_items': [], 'operating_hours': None}

        # URL이 /home이나 다른 탭으로 끝나면 /menu로 변경
        menu_url = url
        if '/home' in url or '/review' in url or '/photo' in url:
            menu_url = re.sub(r'/(home|review|photo).*', '/menu', url)
            print(f"메뉴 URL로 변경: {menu_url}")
        elif not url.endswith('/menu'):
            # URL 끝에 /menu 추가
            menu_url = url.rstrip('/') + '/menu'
            print(f"메뉴 URL 추가: {menu_url}")

        print(f"페이지 로딩 중: {menu_url}")
        driver.get(menu_url)

        # 페이지 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 추가 대기 시간 (JavaScript 로딩)
        time.sleep(3)

        # 페이지 스크롤 (동적 로딩 트리거)
        print("페이지 스크롤하여 콘텐츠 로딩...")
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 1500);")
        time.sleep(2)

        # 모바일 버전인지 확인
        is_mobile = 'm.place.naver.com' in url
        print(f"모바일 버전: {is_mobile}")
        
        # 메뉴 페이지 로딩 대기 (이미 /menu URL로 이동했음)
        print("메뉴 콘텐츠 로딩 대기...")
        time.sleep(5)

        # 추가 스크롤로 더 많은 콘텐츠 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 메뉴 항목 추출
        menu_items = []

        print("메뉴 추출 시작...")

        # 방법 1: span.lPzHi와 em 태그 직접 찾기 (우선순위)
        print("방법 1: span.lPzHi와 em 태그 직접 찾기...")
        try:
            # 명시적 대기: span.lPzHi 요소가 로드될 때까지 기다림
            try:
                print("span.lPzHi 요소 로딩 대기...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.lPzHi"))
                )
                print("span.lPzHi 요소 로드 완료!")
            except TimeoutException:
                print("span.lPzHi 요소 대기 시간 초과 (요소가 없을 수 있음)")

            menu_name_elements = driver.find_elements(By.CSS_SELECTOR, "span.lPzHi")
            print(f"span.lPzHi 요소 {len(menu_name_elements)}개 발견")
            
            for i, menu_name_elem in enumerate(menu_name_elements):
                try:
                    menu_name = menu_name_elem.text.strip()
                    if not menu_name:
                        continue
                    
                    print(f"메뉴 {i+1}: {menu_name}")
                    
                    # em 태그 찾기 (여러 범위에서 시도)
                    price_found = False
                    search_ranges = [
                        menu_name_elem.find_element(By.XPATH, "./.."),  # 부모
                        menu_name_elem.find_element(By.XPATH, "./../.."),  # 조부모
                        menu_name_elem.find_element(By.XPATH, "./../../..")  # 증조부모
                    ]
                    
                    for j, parent in enumerate(search_ranges):
                        try:
                            em_elements = parent.find_elements(By.CSS_SELECTOR, "em")
                            print(f"  범위 {j+1}에서 em 태그 {len(em_elements)}개 발견")
                            
                            for em_elem in em_elements:
                                em_text = em_elem.text.strip()
                                print(f"    em 텍스트: '{em_text}'")
                                
                                # 가격 패턴 확인
                                price_numbers = re.findall(r'[\d,]+', em_text)
                                if price_numbers:
                                    price = int(price_numbers[0].replace(',', ''))
                                    if price > 1000:  # 유효한 가격 범위
                                        menu_items.append((menu_name, price))
                                        print(f"메뉴 추출 성공: {menu_name} - {price}원")
                                        price_found = True
                                        break
                            
                            if price_found:
                                break
                                
                        except Exception as e:
                            print(f"  범위 {j+1} 처리 중 오류: {e}")
                            continue
                    
                    if not price_found:
                        print(f"  가격을 찾을 수 없음: {menu_name}")
                
                except Exception as e:
                    print(f"메뉴 {i+1} 처리 중 오류: {e}")
                    continue
        
        except Exception as e:
            print(f"span.lPzHi 추출 실패: {e}")
        
        # 방법 2: 기존 메뉴 선택자들 시도 + 새로운 선택자들
        if not menu_items:
            print("방법 2: 다양한 메뉴 선택자들 시도...")

            menu_selectors = [
                # 2024년 업데이트된 네이버 플레이스 구조
                "ul.O8qbU.nbAel li",
                ".O8qbU li",
                "ul[class*='menu'] li",
                "div[class*='menu'] > div",

                # 모바일 버전
                ".place_bluelink_menu .list_menu .item_menu",
                ".place_bluelink_menu .item_menu",
                ".list_menu .item_menu",
                ".item_menu",

                # 데스크톱 버전
                ".place_section_content .list_menu .item_menu",
                ".place_section_content .item_menu",

                # 일반적인 메뉴 구조
                ".menu_list .menu_item",
                "[class*='menu'] [class*='item']",
                ".menu-item",
                ".menu_item",

                # 리스트 구조 (포괄적)
                "ul li",
                ".list li"
            ]
            
            for selector in menu_selectors:
                try:
                    menu_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if menu_elements:
                        print(f"메뉴 요소 {len(menu_elements)}개 발견: {selector}")
                        
                        for element in menu_elements:
                            try:
                                # 메뉴명 추출 (다양한 구조 지원)
                                menu_name = None
                                name_selectors = [
                                    "span.lPzHi",  # 새로운 구조
                                    ".link_menu .name_menu",
                                    ".name_menu",
                                    ".menu_name",
                                    ".item_menu_name",
                                    ".tit",
                                    "strong",
                                    "h3",
                                    "h4",
                                    "span"
                                ]
                                
                                for name_sel in name_selectors:
                                    try:
                                        name_elem = element.find_element(By.CSS_SELECTOR, name_sel)
                                        menu_name = name_elem.text.strip()
                                        if menu_name and len(menu_name) > 1:
                                            break
                                    except:
                                        continue
                                
                                # 요소 텍스트 전체에서 메뉴명 추출 시도
                                if not menu_name:
                                    menu_name = element.text.strip().split('\n')[0]
                                
                                # 가격 추출
                                menu_price = None
                                price_selectors = [
                                    "em",  # 새로운 구조
                                    ".price_menu",
                                    ".price",
                                    ".menu_price",
                                    ".item_menu_price",
                                    ".cost",
                                    "[class*='price']",
                                    "span"
                                ]
                                
                                for price_sel in price_selectors:
                                    try:
                                        price_elem = element.find_element(By.CSS_SELECTOR, price_sel)
                                        price_text = price_elem.text.strip()
                                        # 가격에서 숫자 추출
                                        price_numbers = re.findall(r'[\d,]+', price_text)
                                        if price_numbers:
                                            menu_price = int(price_numbers[0].replace(',', ''))
                                            if menu_price > 0:
                                                break
                                    except:
                                        continue
                                
                                # 요소 텍스트 전체에서 가격 추출 시도
                                if not menu_price:
                                    element_text = element.text.strip()
                                    price_numbers = re.findall(r'[\d,]+', element_text)
                                    for price_str in price_numbers:
                                        try:
                                            price = int(price_str.replace(',', ''))
                                            if price > 1000:  # 1000원 이상만 유효한 가격으로 간주
                                                menu_price = price
                                                break
                                        except:
                                            continue
                                
                                # 메뉴명과 가격이 모두 있으면 추가
                                if menu_name and menu_price and menu_price > 0:
                                    # 메뉴명에서 가격 제거
                                    menu_name = re.sub(r'[\d,]+원?', '', menu_name).strip()
                                    if len(menu_name) > 1:
                                        menu_items.append((menu_name, menu_price))
                                        print(f"메뉴 추출: {menu_name} - {menu_price}원")
                            
                            except Exception as e:
                                continue
                        
                        if menu_items:
                            break
                            
                except Exception as e:
                    continue
        
        # 방법 3: 페이지 HTML 전체 분석 (디버깅용)
        if not menu_items:
            print("방법 3: 페이지 HTML 전체 분석...")
            try:
                # 현재 페이지 URL 확인
                current_url = driver.current_url
                print(f"현재 페이지 URL: {current_url}")
                
                # 메뉴 관련 요소들 전체 찾기
                all_spans = driver.find_elements(By.CSS_SELECTOR, "span")
                all_ems = driver.find_elements(By.CSS_SELECTOR, "em")
                
                print(f"페이지 내 span 요소 총 개수: {len(all_spans)}")
                print(f"페이지 내 em 요소 총 개수: {len(all_ems)}")
                
                # lPzHi 클래스 확인
                lpzhi_elements = driver.find_elements(By.CSS_SELECTOR, "span.lPzHi")
                print(f"span.lPzHi 요소 개수: {len(lpzhi_elements)}")
                
                # 모든 lPzHi 요소의 텍스트 출력
                for i, elem in enumerate(lpzhi_elements[:10]):  # 최대 10개만
                    try:
                        text = elem.text.strip()
                        print(f"  lPzHi {i+1}: '{text}'")
                    except:
                        print(f"  lPzHi {i+1}: 텍스트 읽기 실패")
                
                # 모든 em 요소의 텍스트 출력
                print("em 요소들:")
                for i, elem in enumerate(all_ems[:10]):  # 최대 10개만
                    try:
                        text = elem.text.strip()
                        if text and len(text) > 0:
                            print(f"  em {i+1}: '{text}'")
                    except:
                        print(f"  em {i+1}: 텍스트 읽기 실패")
                
                # 페이지 소스에서 lPzHi 패턴 찾기
                page_source = driver.page_source
                lpzhi_pattern = r'<span class="lPzHi">([^<]+)</span>'
                em_pattern = r'<em[^>]*>([^<]+)</em>'
                
                lpzhi_matches = re.findall(lpzhi_pattern, page_source)
                em_matches = re.findall(em_pattern, page_source)
                
                print(f"소스에서 lPzHi 패턴 매칭: {len(lpzhi_matches)}개")
                print(f"소스에서 em 패턴 매칭: {len(em_matches)}개")
                
                # 매칭 결과 출력
                for i, match in enumerate(lpzhi_matches[:5]):
                    print(f"  lPzHi 매칭 {i+1}: '{match}'")
                
                for i, match in enumerate(em_matches[:5]):
                    print(f"  em 매칭 {i+1}: '{match}'")
                
            except Exception as e:
                print(f"페이지 분석 중 오류: {e}")
        
        # 방법 3: 페이지 소스에서 정규식으로 추출
        if not menu_items:
            print("페이지 소스에서 정규식으로 추출 시도...")
            page_source = driver.page_source
            
            # 네이버 플레이스 특정 패턴들
            patterns = [
                r'<span class="lPzHi">([^<]+)</span>.*?<em[^>]*>([^<]+)</em>',
                r'<span[^>]*class="[^"]*lPzHi[^"]*"[^>]*>([^<]+)</span>.*?<em[^>]*>([\d,]+)</em>',
                r'"name":"([^"]+)".*?"price":"?(\d+)',
                r'([가-힣\w\s\(\)\+\-\.]+).*?<em[^>]*>([\d,]+)</em>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source, re.DOTALL)
                print(f"패턴 매칭: {len(matches)}개 발견")
                
                for match in matches:
                    try:
                        name = match[0].strip()
                        price_text = match[1].strip()
                        
                        # 가격에서 숫자만 추출
                        price_numbers = re.findall(r'[\d,]+', price_text)
                        if price_numbers:
                            price = int(price_numbers[0].replace(',', ''))
                            if len(name) > 1 and price > 1000:
                                menu_items.append((name, price))
                                print(f"패턴 추출: {name} - {price}원")
                    except:
                        continue
                
                if menu_items:
                    break
        
        # 영업시간 정보 추출
        operating_hours = extract_operating_hours(driver)
        
        # 중복 제거
        unique_items = []
        seen = set()
        for name, price in menu_items:
            if name not in seen:
                seen.add(name)
                unique_items.append((name, price))
        
        return {
            'menu_items': unique_items[:20],  # 최대 20개
            'operating_hours': operating_hours
        }
        
    except Exception as e:
        print(f"Selenium 스크래핑 오류: {e}")
        return {
            'menu_items': [],
            'operating_hours': None
        }
    
    finally:
        if driver:
            driver.quit()

def scrape_naver_place_menu_requests(url):
    """requests를 사용한 기본 스크래핑 (백업용)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 메뉴 정보 추출 시도
        menu_items = []
        
        # 기본 텍스트 패턴 매칭
        text_content = soup.get_text()
        menu_patterns = re.findall(r'([가-힣\w\s\(\)\+\-\.]+)\s*[\s\-:]\s*([\d,]+원?)', text_content)
        
        for name, price_text in menu_patterns:
            try:
                name = name.strip()
                price_numbers = re.findall(r'[\d,]+', price_text)
                if price_numbers:
                    price = int(price_numbers[0].replace(',', ''))
                    if len(name) > 1 and price > 1000:
                        menu_items.append((name, price))
            except:
                continue
        
        # 중복 제거
        unique_items = []
        seen = set()
        for name, price in menu_items:
            if name not in seen:
                seen.add(name)
                unique_items.append((name, price))
        
        return unique_items[:20]
        
    except Exception as e:
        print(f"requests 스크래핑 오류: {e}")
        return []

def get_naver_place_info(url):
    """네이버 플레이스 정보 가져오기 (메뉴 + 영업시간)"""
    if not url or 'naver.com' not in url:
        return {
            'menu_items': [],
            'operating_hours': None
        }
    
    print(f"네이버 플레이스 정보 추출 시작: {url}")
    
    business_type, place_id = extract_place_info_from_url(url)
    print(f"업체 유형: {business_type}, 플레이스 ID: {place_id}")
    
    # 1. Selenium을 사용한 동적 스크래핑 시도
    place_info = scrape_naver_place_info_selenium(url)
    
    # 2. 실패시 기본 requests 스크래핑 시도 (메뉴만)
    if not place_info['menu_items']:
        print("Selenium 실패, requests 시도...")
        menu_items = scrape_naver_place_menu_requests(url)
        place_info['menu_items'] = menu_items
    
    # 3. 여전히 실패시 샘플 메뉴 반환
    if not place_info['menu_items']:
        print("메뉴 추출 실패, 샘플 메뉴 반환")
        place_info['menu_items'] = [
            ("김치찌개", 8000),
            ("된장찌개", 7000),
            ("불고기", 15000),
            ("갈비탕", 12000),
            ("냉면", 9000),
            ("비빔밥", 8500),
            ("제육볶음", 10000),
            ("순대국", 8000)
        ]
    
    print(f"총 {len(place_info['menu_items'])}개 메뉴 추출 완료")
    if place_info['operating_hours']:
        hours = place_info['operating_hours']
        print(f"영업시간: {hours['start_hour']}:{hours['start_minute']:02d} ~ {hours['end_hour']}:{hours['end_minute']:02d}")
    else:
        print("영업시간 정보 없음")
    
    return place_info

def get_naver_place_menu(url):
    """기존 호환성을 위한 메뉴만 반환하는 함수"""
    place_info = get_naver_place_info(url)
    return place_info['menu_items']

def format_menu_for_textarea(menu_items, apply_filter=False):
    """메뉴 리스트를 textarea 형식으로 변환"""
    if apply_filter:
        # receipt_generator의 smart_filter_menu 함수 재구현
        filtered_items = []
        for name, price in menu_items:
            # 1. 이미 7글자 이하면 그대로 사용
            if len(name) <= 7:
                filtered_items.append((name, price))
            else:
                # 2. 공백 제거해서 7글자 이하가 되면 공백 제거
                no_space = name.replace(" ", "")
                if len(no_space) <= 7:
                    filtered_items.append((no_space, price))
                # 3. 그래도 길면 제외
        return '\n'.join([f"{name} {price}" for name, price in filtered_items])
    else:
        return '\n'.join([f"{name} {price}" for name, price in menu_items])

# 테스트용 함수
if __name__ == "__main__":
    test_url = "https://m.place.naver.com/restaurant/1207475613"
    menu_items = get_naver_place_menu(test_url)
    print("\n=== 추출된 메뉴 ===")
    for name, price in menu_items:
        print(f"{name}: {price}원")