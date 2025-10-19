"""단축 URL 테스트"""
import sys
sys.path.append('naver_review_automation')

from real_review_extractor import get_extractor

# 사용자가 제공한 단축 URL들
test_urls = [
    "https://naver.me/FUQfT4Jf",
    "https://naver.me/x4GY9gLz",
    "https://naver.me/GypZ5Boj",
    "https://naver.me/GuD6v2aB",
    "https://naver.me/Gplwssxz"
]

shop_name = "티프 동대문"

extractor = get_extractor()

for idx, url in enumerate(test_urls, 1):
    print("=" * 80)
    print(f"테스트 {idx}/5")
    print("=" * 80)
    print(f"원본 URL: {url}")

    review_text, receipt_date, metadata = extractor.extract_review(url, shop_name)

    print(f"\n리뷰 내용 (앞 100자):")
    print(f"  {review_text[:100] if review_text else 'None'}...")
    print(f"\n영수증 날짜: {receipt_date}")
    print(f"메타데이터: {metadata}")
    print()
