#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
네이버 플레이스 메뉴 스크래퍼 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from receipt_generator.naver_scraper import get_naver_place_menu

def test_menu_extraction(url):
    """메뉴 추출 테스트"""
    print("=" * 60)
    print("네이버 플레이스 메뉴 추출 테스트")
    print("=" * 60)
    print(f"\n테스트 URL: {url}\n")

    try:
        menu_items = get_naver_place_menu(url)

        if menu_items:
            print(f"\n✅ 성공! {len(menu_items)}개 메뉴 추출됨:")
            print("-" * 60)
            for i, (name, price) in enumerate(menu_items, 1):
                print(f"{i}. {name}: {price:,}원")
            print("-" * 60)
        else:
            print("\n❌ 실패: 메뉴를 추출할 수 없습니다.")
            print("가능한 원인:")
            print("1. URL이 잘못되었습니다")
            print("2. 네이버 플레이스 페이지 구조가 변경되었습니다")
            print("3. ChromeDriver 설치나 설정에 문제가 있습니다")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 테스트 URL
    test_url = "https://m.place.naver.com/restaurant/1655521895/home"

    if len(sys.argv) > 1:
        test_url = sys.argv[1]

    test_menu_extraction(test_url)
