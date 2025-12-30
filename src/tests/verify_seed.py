# -*- coding: utf-8 -*-
"""验证种子数据"""
from utils.utils import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# 路段
cursor.execute('SELECT COUNT(*) FROM RoadSegment')
print(f'路段数量: {cursor.fetchone()[0]}')

cursor.execute('SELECT segment_name FROM RoadSegment ORDER BY segment_id LIMIT 8')
print('\n前8个路段:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

# 问题类型
cursor.execute('SELECT COUNT(*) FROM ProblemType')
print(f'\n问题类型数量: {cursor.fetchone()[0]}')

cursor.execute('SELECT type_name FROM ProblemType WHERE parent_id IS NULL ORDER BY type_id')
print('\n顶层问题类型 (应该包含 emoji):')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

cursor.close()
conn.close()
