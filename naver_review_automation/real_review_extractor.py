import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import os
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class RealNaverReviewExtractor:
    """실제 네이버 리뷰 추출기 - Chrome 있으면 Selenium, 없으면 HTTP"""
    
    def __init__(self):
        self.driver = None
        self.chrome_available = False
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def setup_selenium(self):
        """셀레니움 설정 (로컬에서만 시도)"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 항상 headless 모드로 실행 (창이 안 뜨도록)
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
                
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(5)
            self.chrome_available = True
            
            logger.info("✅ Chrome 드라이버 설정 완료")
            return True
            
        except Exception as e:
            logger.warning(f"Chrome 설정 실패: {e}")
            logger.info("HTTP 방식으로 대체 실행")
            self.chrome_available = False
            return False

    def extract_direct_review_selenium(self, url: str, shop_name: Optional[str] = None) -> Tuple[str, str]:
        """Selenium으로 개별 리뷰 페이지 추출 (reviewId 기반)"""
        try:
            if not self.driver:
                if not self.setup_selenium():
                    logger.error("Selenium 설정 실패, HTTP 방식으로 전환")
                    return self.extract_with_http(url)

            # 이미 해당 URL에 있지 않은 경우에만 로드
            if self.driver.current_url != url:
                logger.info(f"개별 리뷰 페이지 로딩: {url}")
                self.driver.get(url)
                time.sleep(4)  # 로딩 대기 시간 증가
            else:
                logger.info(f"이미 로드된 페이지 사용: {url}")

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # reviewId가 URL에 있는 경우 - 업체명으로 정확히 매칭!
            if "reviewId=" in url and shop_name:
                import re
                from urllib.parse import urlparse, parse_qs

                # URL에서 reviewId 추출
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                review_id = params.get('reviewId', [None])[0]

                logger.info(f"🎯 reviewId: {review_id}, 업체명: '{shop_name}'")

                # 모든 리뷰 블록 찾기
                review_blocks = soup.find_all('div', class_='hahVh2')
                logger.info(f"리뷰 블록 {len(review_blocks)}개 발견")

                target_review = None

                # 1순위: 업체명으로 정확히 매칭 (가장 중요!)
                for block in review_blocks:
                    shop_elem = block.find('span', class_='pui__pv1E2a')
                    if shop_elem:
                        found_shop_name = shop_elem.get_text(strip=True)
                        logger.info(f"  검사 중 - 업체명: '{found_shop_name}'")

                        if found_shop_name == shop_name:
                            logger.info(f"✅ 업체명 일치! '{shop_name}'")
                            target_review = block
                            break

                # 2순위: reviewId로 찾기 (업체명으로 못 찾은 경우)
                if not target_review and review_id:
                    logger.info(f"업체명 매칭 실패, reviewId로 재시도: {review_id}")
                    for block in review_blocks:
                        block_html = str(block)
                        if review_id in block_html:
                            logger.info(f"✅ reviewId 일치하는 블록 발견!")
                            target_review = block
                            break

                if target_review:
                    # 리뷰 본문 추출
                    review_text = ""
                    review_div = target_review.find('div', class_='pui__vn15t2')
                    if not review_div:
                        review_elem = target_review.find('a', {'data-pui-click-code': 'reviewend.text'})
                        if review_elem:
                            review_text = review_elem.get_text(strip=True)
                    else:
                        review_text = review_div.get_text(strip=True)

                    # 영수증 날짜 추출
                    receipt_date = ""
                    time_elem = target_review.find('time', {'aria-hidden': 'true'})
                    if time_elem:
                        receipt_date = time_elem.get_text(strip=True)

                    # 업체명 확인
                    shop_elem = target_review.find('span', class_='pui__pv1E2a')
                    found_shop = shop_elem.get_text(strip=True) if shop_elem else "알 수 없음"
                    logger.info(f"✅ 추출 성공 - 업체: {found_shop}, 리뷰: {review_text[:30]}..., 날짜: {receipt_date}")

                    return (
                        review_text or "리뷰 본문을 찾을 수 없습니다",
                        receipt_date or "영수증 날짜를 찾을 수 없습니다"
                    )
                else:
                    # 못 찾은 경우
                    all_shops = [block.find('span', class_='pui__pv1E2a').get_text(strip=True)
                                for block in review_blocks
                                if block.find('span', class_='pui__pv1E2a')]
                    logger.error(f"❌ 업체명 '{shop_name}'과 일치하는 리뷰 없음. 발견된 업체: {all_shops}")
                    return f"업체명 '{shop_name}'과 일치하는 리뷰를 찾을 수 없습니다", "날짜 정보 없음"

            # 일반 개별 리뷰 페이지 처리
            # 리뷰 본문 추출 - data-pui-click-code="reviewend.text"
            review_text = ""
            review_elem = soup.find('a', {'data-pui-click-code': 'reviewend.text'})
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                logger.info(f"리뷰 본문 추출 성공: {review_text[:50]}...")
            else:
                # 대체 선택자 시도
                review_div = soup.find('div', class_='pui__vn15t2')
                if review_div:
                    review_text = review_div.get_text(strip=True)
                    logger.info(f"대체 선택자로 리뷰 본문 추출: {review_text[:50]}...")
                else:
                    logger.warning("리뷰 본문을 찾을 수 없습니다")

            # 영수증 날짜 추출 - time 태그
            receipt_date = ""
            time_elem = soup.find('time', {'aria-hidden': 'true'})
            if time_elem:
                receipt_date = time_elem.get_text(strip=True)
                logger.info(f"영수증 날짜 추출: {receipt_date}")
            else:
                logger.warning("영수증 날짜 time 태그를 찾을 수 없습니다")

            return (
                review_text or "리뷰 본문을 찾을 수 없습니다",
                receipt_date or "영수증 날짜를 찾을 수 없습니다"
            )

        except Exception as e:
            logger.error(f"Selenium 추출 오류 상세: {type(e).__name__} - {str(e)}", exc_info=True)
            return f"Selenium 추출 실패: {type(e).__name__}", "날짜 추출 실패"

    def extract_list_review_selenium(self, url: str, shop_name: str) -> Tuple[str, str]:
        """Selenium으로 리뷰 목록에서 특정 업체 리뷰 추출"""
        try:
            if not self.driver:
                if not self.setup_selenium():
                    logger.error("Selenium 설정 실패, HTTP 방식으로 전환")
                    return self.extract_with_http(url)

            logger.info(f"페이지 로딩 시작: {url}")
            self.driver.get(url)

            # 단축 URL 리디렉션 대기
            if "naver.me" in url:
                try:
                    WebDriverWait(self.driver, 10).until(lambda d: d.current_url != url)
                    logger.info(f"리디렉션 완료: {self.driver.current_url}")
                except Exception as e:
                    logger.error(f"리디렉션 대기 실패: {e}")

            time.sleep(4)  # 페이지 로딩 대기 시간 증가

            # 업체명으로 리뷰 찾기
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            target_review = None

            review_blocks = soup.find_all('div', class_='hahVh2')
            logger.info(f"리뷰 블록 {len(review_blocks)}개 발견")

            if len(review_blocks) == 0:
                logger.error("리뷰 블록을 찾을 수 없습니다. 페이지 구조가 변경되었을 수 있습니다.")
                return "리뷰 블록을 찾을 수 없습니다", "날짜 추출 불가"

            # 먼저 모든 업체명 로깅
            all_shop_names = []
            for block in review_blocks:
                shop_elem = block.find('span', class_='pui__pv1E2a')
                if shop_elem:
                    shop_text = shop_elem.text.strip()
                    all_shop_names.append(shop_text)
                    if shop_text == shop_name:
                        target_review = block
                        logger.info(f"업체명 '{shop_name}' 매칭 성공")
                        break

            logger.info(f"발견된 업체명들: {all_shop_names[:5]}")

            # 스크롤해서 더 찾기
            if not target_review:
                logger.info(f"첫 페이지에서 '{shop_name}' 미발견, 스크롤 시작")
                for i in range(5):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    review_blocks = soup.find_all('div', class_='hahVh2')

                    for block in review_blocks:
                        shop_elem = block.find('span', class_='pui__pv1E2a')
                        if shop_elem and shop_elem.text.strip() == shop_name:
                            target_review = block
                            logger.info(f"스크롤 {i+1}회차에서 업체명 발견")
                            break

                    if target_review:
                        break

            # 리뷰 데이터 추출
            if target_review:
                # 더보기 버튼 클릭 시도
                try:
                    more_button = target_review.find('a', {'data-pui-click-code': 'otherreviewfeed.rvshowmore'})
                    if more_button:
                        selenium_blocks = self.driver.find_elements(By.CSS_SELECTOR, "div.hahVh2")
                        for selenium_block in selenium_blocks:
                            if shop_name in selenium_block.text:
                                try:
                                    more_btn = selenium_block.find_element(By.CSS_SELECTOR, "a[data-pui-click-code='otherreviewfeed.rvshowmore']")
                                    self.driver.execute_script("arguments[0].click();", more_btn)
                                    time.sleep(1)
                                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                                    # 다시 타겟 리뷰 찾기
                                    review_blocks = soup.find_all('div', class_='hahVh2')
                                    for block in review_blocks:
                                        shop_elem = block.find('span', class_='pui__pv1E2a')
                                        if shop_elem and shop_elem.text.strip() == shop_name:
                                            target_review = block
                                            break
                                    break
                                except Exception as inner_e:
                                    logger.warning(f"더보기 버튼 클릭 실패: {inner_e}")
                except Exception as e:
                    logger.warning(f"더보기 버튼 처리 실패: {e}")

                # 리뷰 본문 추출
                review_text = ""
                review_div = target_review.find('div', class_='pui__vn15t2')
                if review_div:
                    review_text = review_div.text.strip()
                    logger.info(f"리뷰 본문 추출 성공: {review_text[:50]}...")
                else:
                    logger.warning("리뷰 본문 div를 찾을 수 없습니다")

                # 영수증 날짜 추출
                receipt_date = ""
                time_elem = target_review.find('time', {'aria-hidden': 'true'})
                if time_elem:
                    receipt_date = time_elem.text.strip()
                    logger.info(f"영수증 날짜 추출: {receipt_date}")
                else:
                    logger.warning("영수증 날짜 time 태그를 찾을 수 없습니다")

                return (
                    review_text or "리뷰 본문을 찾을 수 없습니다",
                    receipt_date or "영수증 날짜를 찾을 수 없습니다"
                )
            else:
                logger.error(f"업체명 '{shop_name}'과 일치하는 리뷰를 찾을 수 없습니다. 발견된 업체명: {all_shop_names[:3]}")
                return f"업체명 '{shop_name}'과 일치하는 리뷰를 찾을 수 없습니다", "날짜 정보 없음"

        except Exception as e:
            logger.error(f"리뷰 목록 추출 오류 상세: {type(e).__name__} - {str(e)}", exc_info=True)
            return f"추출 오류 발생: {type(e).__name__}", "날짜 추출 실패"

    def extract_with_http(self, url: str) -> Tuple[str, str]:
        """HTTP 요청으로 기본 정보 추출 (Chrome 없을 때)"""
        try:
            logger.info(f"HTTP 방식으로 페이지 접근: {url}")
            
            # User-Agent를 다양하게 시도
            headers_list = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ]
            
            for user_agent in headers_list:
                try:
                    self.session.headers.update({'User-Agent': user_agent})
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # 페이지 제목에서 업체 정보 추출
                        title = soup.find('title')
                        title_text = title.get_text() if title else ""
                        
                        # 메타 태그에서 설명 추출
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        description = meta_desc.get('content', '') if meta_desc else ""
                        
                        # 기본 정보 조합
                        extracted_info = f"페이지 제목: {title_text}\\n"
                        if description:
                            extracted_info += f"설명: {description[:100]}..."
                        
                        # URL 타입별 정보 추가
                        if "/my/review/" in url:
                            extracted_info += "\\n[개별 리뷰 페이지]"
                            date_info = "개별 리뷰 날짜"
                        else:
                            extracted_info += "\\n[리뷰 피드 페이지]"
                            date_info = "피드 페이지 날짜"
                        
                        return extracted_info, date_info
                        
                except Exception as e:
                    logger.warning(f"User-Agent {user_agent} 실패: {e}")
                    continue
            
            return "HTTP 추출 실패 - 모든 User-Agent 시도 완료", "날짜 추출 불가"
            
        except Exception as e:
            logger.error(f"HTTP 추출 총 실패: {e}")
            return f"HTTP 추출 오류: {str(e)}", "오류 발생"

    def extract_review(self, url: str, shop_name: Optional[str] = None) -> Tuple[str, str, dict]:
        """메인 추출 함수 - 최적의 방법 자동 선택"""
        start_time = time.time()

        try:
            logger.info(f"리뷰 추출 시작: {url}")
            logger.info(f"Chrome 사용 가능: {self.chrome_available}")

            # 단축 URL(naver.me)인 경우 먼저 리디렉션 확인
            if "naver.me" in url and self.chrome_available:
                logger.info("단축 URL 감지 - 리디렉션 확인 중")
                if not self.driver:
                    self.setup_selenium()

                self.driver.get(url)
                time.sleep(2)  # 리디렉션 대기
                redirected_url = self.driver.current_url
                logger.info(f"리디렉션된 URL: {redirected_url}")
                url = redirected_url  # URL을 리디렉션된 URL로 변경

            # URL 패턴 확인 - 네이버 리뷰 URL 형식들
            # reviewId 파라미터가 있으면 특정 리뷰를 가리키는 것
            has_review_id = "reviewId=" in url

            # 진짜 개별 리뷰 페이지는 /place/review/ugc/ 같은 특정 패턴만
            is_ugc_review = "/place/review/ugc/" in url

            # /my/.../reviewfeed 는 리뷰 피드 페이지
            is_my_reviewfeed = "/my/" in url and "reviewfeed" in url

            # 기타 리뷰 목록 패턴
            is_place_feed = "/place/feed/" in url or "/restaurant/" in url

            # reviewId가 있으면 개별 리뷰 페이지처럼 처리 (해당 리뷰만 추출)
            is_direct_review = is_ugc_review or has_review_id

            logger.info(f"🔍 URL 패턴 분석:")
            logger.info(f"  - URL: {url}")
            logger.info(f"  - reviewId 파라미터: {has_review_id}")
            logger.info(f"  - UGC 리뷰: {is_ugc_review}")
            logger.info(f"  - My 리뷰피드: {is_my_reviewfeed}")
            logger.info(f"  - Place 피드: {is_place_feed}")
            logger.info(f"  - 최종 판정: {'개별 리뷰 직접 추출' if is_direct_review else '리뷰 목록에서 업체명 검색'}")

            if is_direct_review:
                # reviewId가 있거나 UGC 리뷰 - 페이지에 표시된 리뷰를 바로 추출
                logger.info("✅ 개별 리뷰 직접 추출 (페이지의 리뷰 내용 가져오기)")
                if self.chrome_available:
                    review_text, receipt_date = self.extract_direct_review_selenium(url, shop_name)
                else:
                    review_text, receipt_date = self.extract_with_http(url)
            else:
                # 리뷰 목록/피드 페이지 - shop_name으로 매칭 필요
                logger.info("📋 리뷰 목록 페이지로 처리 - 업체명으로 리뷰 검색")
                if not shop_name:
                    logger.error("❌ 리뷰 목록 페이지인데 업체명이 없습니다")
                    return "업체명이 필요합니다", "업체명 누락", {}

                if self.chrome_available:
                    review_text, receipt_date = self.extract_list_review_selenium(url, shop_name)
                else:
                    review_text, receipt_date = self.extract_with_http(url)
            
            # 메타데이터 생성
            processing_time = round(time.time() - start_time, 2)
            metadata = {
                "processing_time_seconds": processing_time,
                "extraction_method": "selenium" if self.chrome_available else "http",
                "url_type": "direct" if is_direct_review else "list",
                "shop_name": shop_name,
                "success": "오류" not in review_text and "찾을 수 없습니다" not in review_text
            }
            
            logger.info(f"추출 완료 - 소요시간: {processing_time}초")
            return review_text, receipt_date, metadata
            
        except Exception as e:
            logger.error(f"리뷰 추출 총 오류: {e}")
            return f"추출 중 오류 발생: {str(e)}", "오류 발생", {
                "processing_time_seconds": round(time.time() - start_time, 2),
                "extraction_method": "failed",
                "error": str(e)
            }
    
    def test_extraction_capability(self) -> dict:
        """추출 기능 테스트"""
        try:
            # Chrome 사용 가능 여부 테스트
            chrome_test = self.setup_selenium()
            
            # HTTP 요청 테스트
            try:
                response = self.session.get("https://www.naver.com", timeout=5)
                http_test = response.status_code == 200
            except:
                http_test = False
            
            return {
                "chrome_available": chrome_test,
                "http_available": http_test,
                "recommended_method": "selenium" if chrome_test else "http",
                "capabilities": {
                    "direct_review_extraction": chrome_test,
                    "list_review_extraction": chrome_test,
                    "basic_page_info": http_test
                }
            }
        except Exception as e:
            return {
                "chrome_available": False,
                "http_available": False,
                "error": str(e)
            }
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# 전역 추출기 인스턴스 (성능 최적화)
_global_extractor = None

def get_extractor():
    """전역 추출기 인스턴스 가져오기"""
    global _global_extractor
    if _global_extractor is None:
        _global_extractor = RealNaverReviewExtractor()
        _global_extractor.setup_selenium()  # 미리 설정
    return _global_extractor

def extract_naver_review_real(url: str, shop_name: Optional[str] = None) -> Tuple[str, str, dict]:
    """실제 네이버 리뷰 추출 - 편의 함수"""
    extractor = get_extractor()
    return extractor.extract_review(url, shop_name)

def test_extractor_capability() -> dict:
    """추출기 기능 테스트"""
    extractor = get_extractor()
    return extractor.test_extraction_capability()

# 테스트용 함수
def test_real_extraction():
    """실제 추출 테스트"""
    test_urls = [
        {
            "url": "https://m.place.naver.com/my/review/68affe6981fb5b79934cd611?v=2",
            "type": "direct",
            "shop_name": None
        },
        {
            "url": "https://naver.me/5jBm0HYx",
            "type": "list", 
            "shop_name": "미미한 샌드까츠"
        }
    ]
    
    results = []
    extractor = get_extractor()
    
    print("🧪 실제 추출 기능 테스트 시작")
    print(f"추출기 상태: {extractor.test_extraction_capability()}")
    
    for test in test_urls:
        print(f"\n📍 테스트: {test['type']} - {test['url'][:50]}...")
        
        review_text, receipt_date, metadata = extractor.extract_review(
            test['url'], test.get('shop_name')
        )
        
        result = {
            "url": test['url'],
            "type": test['type'],
            "review_text": review_text[:100] + "..." if len(review_text) > 100 else review_text,
            "receipt_date": receipt_date,
            "metadata": metadata
        }
        
        results.append(result)
        print(f"✅ 결과: {result}")
    
    return results

if __name__ == "__main__":
    # 직접 실행시 테스트
    test_real_extraction()