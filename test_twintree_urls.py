"""트윈트리 업체 5개 URL 테스트"""
import sys
sys.path.append('naver_review_automation')

from real_review_extractor import get_extractor
import time

# 사용자가 제공한 트윈트리 URL 5개
test_urls = [
    "https://naver.me/FCr3P5OD",
    "https://naver.me/F8ueciYr",
    "https://naver.me/xafv11ex",
    "https://naver.me/5tfDytwM",
    "https://naver.me/5f5UuKuK"
]

shop_name = "트윈트리"

print("=" * 100)
print(f"트윈트리 업체 URL 테스트 (총 {len(test_urls)}개)")
print("=" * 100)

extractor = get_extractor()

# 셀레니움 초기화
if not extractor.driver:
    extractor.setup_selenium()

results = []

for idx, url in enumerate(test_urls, 1):
    print(f"\n{'=' * 100}")
    print(f"[테스트 {idx}/5]")
    print(f"{'=' * 100}")
    print(f"원본 URL: {url}")

    # 리디렉션 확인
    print("\n[1단계] 리디렉션 확인 중...")
    extractor.driver.get(url)
    time.sleep(3)
    redirected_url = extractor.driver.current_url
    print(f"리디렉션된 URL: {redirected_url}")

    # 페이지에서 모든 업체명 확인
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(extractor.driver.page_source, 'html.parser')
    review_blocks = soup.find_all('div', class_='hahVh2')

    print(f"\n[2단계] 페이지 분석 (리뷰 블록 {len(review_blocks)}개)")
    all_shops = []
    for block in review_blocks:
        shop_elem = block.find('span', class_='pui__pv1E2a')
        if shop_elem:
            shop_text = shop_elem.get_text(strip=True)
            all_shops.append(shop_text)

    print(f"발견된 업체명들: {all_shops[:5]}{'...' if len(all_shops) > 5 else ''}")
    print(f"'{shop_name}' 존재 여부: {shop_name in all_shops}")

    # 실제 추출 시도
    print(f"\n[3단계] 리뷰 추출 시도...")
    review_text, receipt_date, metadata = extractor.extract_review(url, shop_name)

    # 결과 저장
    result = {
        'url': url,
        'redirected_url': redirected_url,
        'shop_found': shop_name in all_shops,
        'all_shops': all_shops,
        'review_text': review_text[:100] if review_text else None,
        'receipt_date': receipt_date,
        'success': metadata.get('success', False)
    }
    results.append(result)

    # 결과 출력
    print(f"\n[결과]")
    print(f"  업체명 발견: {result['shop_found']}")
    print(f"  리뷰 내용: {review_text[:80]}..." if review_text else "  리뷰 내용 없음")
    print(f"  영수증 날짜: {receipt_date}")
    print(f"  추출 성공: {result['success']}")

    # 오류 메시지 확인
    error_keywords = ['찾을 수 없습니다', '내용 없음', '에러', 'error', '불일치']
    has_error = any(keyword in review_text.lower() for keyword in error_keywords) if review_text else True

    if has_error or not receipt_date or '날짜 정보 없음' in receipt_date:
        print(f"  [경고] 이 URL은 삭제될 것입니다!")

print(f"\n{'=' * 100}")
print("최종 요약")
print(f"{'=' * 100}")

success_count = sum(1 for r in results if r['success'] and r['shop_found'])
fail_count = len(results) - success_count

print(f"\n총 {len(results)}개 URL 테스트 결과:")
print(f"  성공: {success_count}개")
print(f"  실패: {fail_count}개")

print(f"\n실패한 URL 상세:")
for idx, result in enumerate(results, 1):
    if not result['success'] or not result['shop_found']:
        print(f"\n[실패 URL #{idx}]")
        print(f"  URL: {result['url']}")
        print(f"  리디렉션: {result['redirected_url']}")
        print(f"  '{shop_name}' 발견: {result['shop_found']}")
        print(f"  페이지의 업체명: {result['all_shops'][:3]}...")
        print(f"  리뷰 내용: {result['review_text']}")
        print(f"  영수증 날짜: {result['receipt_date']}")

print(f"\n{'=' * 100}")
