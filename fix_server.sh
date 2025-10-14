#!/bin/bash
# 서버 자동 수정 스크립트

set -e

echo "🔧 서버 수정 시작..."

# 1. DB 백업
echo "📦 데이터베이스 백업 중..."
cd /var/www/adsketch
cp final_complete_system.db final_complete_system.db.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ 백업 완료"

# 2. DB 컬럼 추가 (에러 무시)
echo "🗄️ 데이터베이스 스키마 업데이트 중..."
sqlite3 final_complete_system.db "ALTER TABLE receipt_work_orders ADD COLUMN attachment_images TEXT;" 2>/dev/null || echo "  - attachment_images 컬럼 이미 존재하거나 추가됨"
sqlite3 final_complete_system.db "ALTER TABLE receipt_work_orders ADD COLUMN review_excel_path TEXT;" 2>/dev/null || echo "  - review_excel_path 컬럼 이미 존재하거나 추가됨"
sqlite3 final_complete_system.db "ALTER TABLE receipt_work_orders ADD COLUMN review_photos_path TEXT;" 2>/dev/null || echo "  - review_photos_path 컬럼 이미 존재하거나 추가됨"

# 3. 컬럼 확인
echo "✅ 추가된 컬럼 확인:"
sqlite3 final_complete_system.db "PRAGMA table_info(receipt_work_orders);" | grep -E "attachment_images|review_excel_path|review_photos_path" || echo "  컬럼 조회 실패 - 수동 확인 필요"

# 4. 필요한 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p naver_review_automation/uploads/orders
mkdir -p naver_review_automation/uploads/review_assets
mkdir -p naver_review_automation/static
echo "✅ 디렉토리 생성 완료"

# 5. 템플릿 파일 확인
echo "📄 템플릿 파일 확인:"
ls -la naver_review_automation/static/ 2>/dev/null || echo "  static 디렉토리가 비어있거나 없음"

# 6. 권한 설정
echo "🔐 권한 설정 중..."
chmod -R 755 naver_review_automation/uploads 2>/dev/null || true
chmod -R 755 naver_review_automation/static 2>/dev/null || true
chown -R root:root naver_review_automation/uploads 2>/dev/null || true
chown -R root:root naver_review_automation/static 2>/dev/null || true
echo "✅ 권한 설정 완료"

# 7. 기존 Python 프로세스 종료
echo "🛑 기존 프로세스 종료 중..."
pkill -9 -f 'python.*final_complete_system' 2>/dev/null || echo "  종료할 프로세스 없음"
pkill -9 -f gunicorn 2>/dev/null || echo "  종료할 gunicorn 없음"
sleep 2

# 8. 서비스 재시작
echo "🔄 서비스 재시작 중..."
systemctl restart adsketch
sleep 5

# 9. 서비스 상태 확인
echo "📊 서비스 상태:"
systemctl status adsketch --no-pager || true

# 10. 포트 확인
echo ""
echo "🌐 포트 8000 사용 확인:"
netstat -tulpn | grep :8000 || echo "  포트 8000이 사용되지 않음"

# 11. 최근 로그 확인
echo ""
echo "📋 최근 서비스 로그 (마지막 20줄):"
journalctl -u adsketch -n 20 --no-pager

echo ""
echo "✅ 서버 수정 완료!"
echo ""
echo "🔍 확인 사항:"
echo "1. 서비스가 active (running) 상태인지 확인"
echo "2. 포트 8000이 정상적으로 열렸는지 확인"
echo "3. 웹사이트 접속 테스트: http://165.22.101.45"
echo ""
