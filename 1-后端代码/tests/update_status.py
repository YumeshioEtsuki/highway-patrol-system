from utils.utils import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
cur.execute("UPDATE InspectionRecord SET status='completed' WHERE status='resolved'")
print('更新行', cur.rowcount)
conn.commit()
cur.close()
conn.close()
