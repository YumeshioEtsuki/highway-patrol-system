import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.config import db_config
import mysql.connector

conn = mysql.connector.connect(**db_config)
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM InspectionRecord LIKE 'data_type'")
if not cur.fetchone():
    print('Adding data_type column...')
    cur.execute("""
        ALTER TABLE InspectionRecord 
        ADD COLUMN data_type ENUM('real','test') DEFAULT 'real' COMMENT '数据类型：real=真实数据，test=测试数据'
    """)
else:
    print('data_type already exists')
cur.execute("SHOW INDEX FROM InspectionRecord WHERE Key_name='idx_data_type'")
if not cur.fetchone():
    print('Creating index idx_data_type...')
    cur.execute("CREATE INDEX idx_data_type ON InspectionRecord(data_type)")
else:
    print('idx_data_type already exists')
conn.commit()
print('Done')
cur.close(); conn.close()
