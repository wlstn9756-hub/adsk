"""리뷰 추출 테스트"""
import sys
sys.path.append('naver_review_automation')

from real_review_extractor import get_extractor

# 테스트 URL (사용자가 제공한 URL 패턴)
test_url = "https://m.place.naver.com/my/67986ad873736e3dcfcef1c9/reviewfeed?reviewId=68e537d462a04728a376c77e"
shop_name = "티프 동대문"

print("=" * 60)
print("리뷰 추출 테스트")
print("=" * 60)
print(f"URL: {test_url}")
print(f"업체명: {shop_name}")
print("=" * 60)

extractor = get_extractor()
review_text, receipt_date, metadata = extractor.extract_review(test_url, shop_name)

print("\n결과:")
print(f"리뷰 내용: {review_text[:100] if review_text else 'None'}...")
print(f"영수증 날짜: {receipt_date}")
print(f"메타데이터: {metadata}")
print("=" * 60)
