"""문제 URL 테스트"""
import sys
sys.path.append('naver_review_automation')

from real_review_extractor import get_extractor

# 문제가 된 URL
problem_url = "https://naver.me/5tfDytwM"
shop_name = "티프 동대문"

print("=" * 80)
print("문제 URL 상세 테스트")
print("=" * 80)
print(f"URL: {problem_url}")
print(f"업체명: {shop_name}")
print("=" * 80)

extractor = get_extractor()

# 먼저 리디렉션된 URL 확인
if not extractor.driver:
    extractor.setup_selenium()

print("\n[1단계] 리디렉션 확인 중...")
extractor.driver.get(problem_url)
import time
time.sleep(3)
redirected_url = extractor.driver.current_url
print(f"리디렉션된 URL: {redirected_url}")

# 페이지 HTML 확인
from bs4 import BeautifulSoup
soup = BeautifulSoup(extractor.driver.page_source, 'html.parser')

# 모든 업체명 찾기
print("\n[2단계] 페이지의 모든 업체명 확인...")
review_blocks = soup.find_all('div', class_='hahVh2')
print(f"리뷰 블록 개수: {len(review_blocks)}")

all_shops = []
for idx, block in enumerate(review_blocks, 1):
    shop_elem = block.find('span', class_='pui__pv1E2a')
    if shop_elem:
        shop_text = shop_elem.get_text(strip=True)
        all_shops.append(shop_text)
        print(f"  {idx}. '{shop_text}' (길이: {len(shop_text)} 바이트: {repr(shop_text)})")

print(f"\n찾는 업체명: '{shop_name}' (길이: {len(shop_name)} 바이트: {repr(shop_name)})")
print(f"\n업체명 '{shop_name}'이 리스트에 있는가? {shop_name in all_shops}")

# 실제 추출 시도
print("\n[3단계] 실제 추출 시도...")
review_text, receipt_date, metadata = extractor.extract_review(problem_url, shop_name)

print(f"\n결과:")
print(f"  리뷰 내용: {review_text[:100] if len(review_text) < 100 else review_text[:100] + '...'}...")
print(f"  영수증 날짜: {receipt_date}")
print(f"  성공 여부: {metadata.get('success', False)}")
print("=" * 80)
