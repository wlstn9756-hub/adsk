import sqlite3

conn = sqlite3.connect('final_complete_system.db')
cursor = conn.cursor()

# 전체 리뷰 통계
cursor.execute('''
    SELECT COUNT(*) as total,
           SUM(CASE WHEN content IS NULL OR content = "" OR content = "내용 추출 대기중"
                    THEN 1 ELSE 0 END) as need_extract
    FROM reviews
''')
result = cursor.fetchone()
print(f'전체 리뷰: {result[0]}개')
print(f'추출 필요: {result[1] if result[1] else 0}개')

# 샘플 리뷰 확인
cursor.execute('SELECT id, content, review_url FROM reviews LIMIT 10')
rows = cursor.fetchall()
print('\n샘플 리뷰:')
for row in rows:
    content = row[1][:50] if row[1] else "None"
    url = row[2][:50] if row[2] else "None"
    print(f'ID: {row[0]}, Content: {content}..., URL: {url}')

# content 상태별 카운트
cursor.execute('''
    SELECT content, COUNT(*) as cnt
    FROM reviews
    GROUP BY content
    ORDER BY cnt DESC
    LIMIT 5
''')
print('\nContent 상태별 카운트 (상위 5개):')
for row in cursor.fetchall():
    content = row[0][:30] if row[0] else "NULL/EMPTY"
    print(f'{content}: {row[1]}개')

conn.close()