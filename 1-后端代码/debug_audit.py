import mysql.connector
from utils.config import db_config

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

print("=== 审计记录 ===")
cursor.execute('SELECT * FROM AuditLog ORDER BY timestamp DESC LIMIT 5')
for r in cursor.fetchall():
    print(f"  ID={r['id']}, action={r['action']}, resource={r['resource']}, timestamp={r['timestamp']}")

print("\n=== 数据类型 ===")
cursor.execute('SELECT DISTINCT data_type FROM InspectionRecord')
types = [r['data_type'] for r in cursor.fetchall()]
print(f"  现有类型: {types}")

cursor.execute('SELECT COUNT(*) as cnt FROM InspectionRecord WHERE data_type="test"')
test_count = cursor.fetchone()['cnt']
print(f"  test类型记录数: {test_count}")

cursor.execute('SELECT COUNT(*) as cnt FROM InspectionRecord')
total_count = cursor.fetchone()['cnt']
print(f"  总记录数: {total_count}")

conn.close()
