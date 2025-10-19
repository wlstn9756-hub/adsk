"""트윈트리 업체 5개 URL 간단 테스트 (파일 저장)"""
import sys
sys.path.append('naver_review_automation')

from real_review_extractor import get_extractor
import time
import json

# 사용자가 제공한 트윈트리 URL 5개
test_urls = [
    "https://naver.me/FCr3P5OD",
    "https://naver.me/F8ueciYr",
    "https://naver.me/xafv11ex",
    "https://naver.me/5tfDytwM",
    "https://naver.me/5f5UuKuK"
]

shop_name = "트윈트리"

extractor = get_extractor()

if not extractor.driver:
    extractor.setup_selenium()

results = []

for idx, url in enumerate(test_urls, 1):
    print(f"테스트 {idx}/5: {url}")

    # 리디렉션 확인
    extractor.driver.get(url)
    time.sleep(3)
    redirected_url = extractor.driver.current_url

    # 페이지에서 업체명 확인
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(extractor.driver.page_source, 'html.parser')
    review_blocks = soup.find_all('div', class_='hahVh2')

    all_shops = []
    for block in review_blocks:
        shop_elem = block.find('span', class_='pui__pv1E2a')
        if shop_elem:
            shop_text = shop_elem.get_text(strip=True)
            all_shops.append(shop_text)

    shop_found = shop_name in all_shops

    # 실제 추출
    review_text, receipt_date, metadata = extractor.extract_review(url, shop_name)

    # 성공 여부 판단
    error_keywords = ['찾을 수 없습니다', '내용 없음', '에러', 'error', '불일치']
    has_error = any(keyword in review_text.lower() for keyword in error_keywords) if review_text else True
    will_be_deleted = has_error or not receipt_date or '날짜 정보 없음' in receipt_date

    # 결과 저장
    result = {
        'index': idx,
        'url': url,
        'redirected_url': redirected_url,
        'shop_found_on_page': shop_found,
        'all_shops_on_page': all_shops,
        'review_length': len(review_text) if review_text else 0,
        'receipt_date': receipt_date,
        'success': metadata.get('success', False),
        'will_be_deleted': will_be_deleted
    }
    results.append(result)

    status = "성공" if not will_be_deleted else "실패 (삭제 예정)"
    print(f"  - 업체명 페이지에 존재: {shop_found}")
    print(f"  - 리뷰 길이: {len(review_text) if review_text else 0}자")
    print(f"  - 영수증 날짜: {receipt_date}")
    print(f"  - 상태: {status}\n")

# 결과를 파일에 저장
with open('twintree_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("최종 요약")
print("=" * 80)

success_count = sum(1 for r in results if not r['will_be_deleted'])
fail_count = len(results) - success_count

print(f"총 {len(results)}개 URL 테스트 결과:")
print(f"  성공: {success_count}개")
print(f"  실패 (삭제 예정): {fail_count}개\n")

if fail_count > 0:
    print("실패한 URL:")
    for r in results:
        if r['will_be_deleted']:
            print(f"  [{r['index']}] {r['url']}")
            print(f"      - 페이지에 '{shop_name}' 존재: {r['shop_found_on_page']}")
            print(f"      - 페이지의 업체들: {r['all_shops_on_page'][:3]}...")
            print(f"      - 영수증 날짜: {r['receipt_date']}")

print("\n상세 결과는 twintree_test_results.json 파일에 저장되었습니다.")
