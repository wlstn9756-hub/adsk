"""
스마트 자동 배정 시스템
- 리뷰에서 업체명 추출
- 추출된 업체명으로 주문 매칭
- 자동 배정
"""

from typing import Optional, Tuple
import re

def extract_shop_name_from_content(content: str) -> Optional[str]:
    """리뷰 내용에서 업체명 추출"""
    # 패턴 1: "XXX에 갔는데", "XXX에서"
    patterns = [
        r'([가-힣\s]+?)(?:에서|에|을|를|의)',
        r'^([가-힣\s]+?)\s',
        r'([가-힣]+본점|[가-힣]+지점)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            shop = match.group(1).strip()
            if len(shop) > 2:  # 최소 3글자 이상
                return shop

    return None

def find_matching_order(shop_name: str, receipt_date: str, db_session):
    """업체명과 날짜로 적절한 주문 찾기"""
    from sqlalchemy import func
    from final_complete_system import ReceiptWorkOrder

    # 1차: 정확히 일치하는 업체명 + 미완료 주문
    order = db_session.query(ReceiptWorkOrder).filter(
        ReceiptWorkOrder.business_name == shop_name,
        ReceiptWorkOrder.status == 'approved',
        ReceiptWorkOrder.completed_count < ReceiptWorkOrder.total_count
    ).order_by(
        ReceiptWorkOrder.created_at.desc()  # 최신 주문 우선
    ).first()

    if order:
        return order, "exact_match"

    # 2차: 부분 일치하는 업체명 + 미완료 주문
    order = db_session.query(ReceiptWorkOrder).filter(
        ReceiptWorkOrder.business_name.contains(shop_name),
        ReceiptWorkOrder.status == 'approved',
        ReceiptWorkOrder.completed_count < ReceiptWorkOrder.total_count
    ).order_by(
        ReceiptWorkOrder.created_at.desc()
    ).first()

    if order:
        return order, "partial_match"

    # 3차: 업체명의 일부가 포함된 경우
    keywords = shop_name.split()
    for keyword in keywords:
        if len(keyword) >= 2:  # 최소 2글자 이상
            order = db_session.query(ReceiptWorkOrder).filter(
                ReceiptWorkOrder.business_name.contains(keyword),
                ReceiptWorkOrder.status == 'approved',
                ReceiptWorkOrder.completed_count < ReceiptWorkOrder.total_count
            ).order_by(
                ReceiptWorkOrder.created_at.desc()
            ).first()

            if order:
                return order, f"keyword_match:{keyword}"

    return None, "no_match"

def smart_assign_review(review_url: str, review_content: str, receipt_date: str, db_session) -> Tuple[Optional[int], str]:
    """
    리뷰를 스마트하게 주문에 배정
    Returns: (order_id, match_type)
    """
    # 리뷰 내용에서 업체명 추출
    shop_name = extract_shop_name_from_content(review_content)

    if not shop_name:
        return None, "no_shop_name"

    # 업체명으로 주문 찾기
    order, match_type = find_matching_order(shop_name, receipt_date, db_session)

    if order:
        return order.id, f"{match_type}:{shop_name}"

    return None, f"no_order:{shop_name}"