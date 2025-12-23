import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.config import db_config
import mysql.connector

conn = mysql.connector.connect(**db_config)
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM InspectionRecord LIKE 'data_type'")
print('col:', cur.fetchone())
cur.execute("SHOW INDEX FROM InspectionRecord WHERE Key_name='idx_data_type'")
print('idx:', cur.fetchone())
cur.execute("SHOW CREATE TABLE InspectionRecord")
row = cur.fetchone()
print('create table snippet:\n', '\n'.join(row[1].split('\n')[:10]))
cur.close(); conn.close()
