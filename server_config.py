import os

# 서버 설정
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8001))  # 8001번으로 변경

# 다른 서비스와 충돌 방지
DATABASE_PATH = os.environ.get('DATABASE_PATH', './adsketch_data/final_complete_system.db')
LOG_PATH = os.environ.get('LOG_PATH', './adsketch_logs/')

# Chrome 설정
CHROME_MEMORY_LIMIT = "512M"  # 메모리 제한 설정