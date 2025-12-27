"""为不同区域创建测试路段和巡查记录"""
import mysql.connector
from datetime import datetime, timedelta
import random

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='REDACTED',
        database='road_patrol_db'
    )
    cursor = conn.cursor(dictionary=True)
    
    print("正在为不同区域创建测试数据...")
    
    # 定义大洲和对应的路段
    regions = [
        ('Asia', 'G318川藏线', 3000, 3100),
        ('Europe', 'E40欧洲高速', 100, 200),
        ('North America', 'I-95美国东海岸', 500, 600),
        ('South America', 'Pan-American Highway', 700, 800),
        ('Africa', 'Trans-African Highway', 200, 300),
        ('Oceania', 'Pacific Highway', 400, 500)
    ]
    
    # 获取部门ID
    cursor.execute("SELECT department_id FROM Department LIMIT 1")
    dept = cursor.fetchone()
    dept_id = dept['department_id'] if dept else 1
    
    # 获取用户ID
    cursor.execute("SELECT user_id FROM User WHERE role='inspector' LIMIT 1")
    user = cursor.fetchone()
    user_id = user['user_id'] if user else 1
    
    # 获取问题类型ID列表
    cursor.execute("SELECT type_id FROM ProblemType")
    type_ids = [row['type_id'] for row in cursor.fetchall()]
    if not type_ids:
        type_ids = [1]
    
    segment_ids = {}
    
    # 为每个区域创建路段
    for region, segment_name, start_num, end_num in regions:
        # 检查路段是否已存在
        cursor.execute("SELECT segment_id FROM RoadSegment WHERE segment_name = %s", (segment_name,))
        existing = cursor.fetchone()
        
        if existing:
            segment_id = existing['segment_id']
            # 更新区域信息
            cursor.execute("UPDATE RoadSegment SET region = %s WHERE segment_id = %s", (region, segment_id))
            print(f"更新现有路段: {segment_name} ({region})")
        else:
            # 创建新路段
            cursor.execute("""
                INSERT INTO RoadSegment (segment_name, start_number, end_number, department_id, region)
                VALUES (%s, %s, %s, %s, %s)
            """, (segment_name, start_num, end_num, dept_id, region))
            segment_id = cursor.lastrowid
            print(f"创建新路段: {segment_name} ({region})")
        
        segment_ids[region] = segment_id
        
        # 为每个路段创建2-5条巡查记录
        num_records = random.randint(2, 5)
        for i in range(num_records):
            days_ago = random.randint(1, 30)
            upload_time = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT INTO InspectionRecord 
                (user_id, upload_time, latitude, longitude, segment_id, problem_type_id, 
                 description, severity, status, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                upload_time,
                random.uniform(-85, 85),  # 纬度
                random.uniform(-180, 180),  # 经度
                segment_id,
                random.choice(type_ids),
                f"{region}地区路段问题{i+1}",
                random.randint(1, 5),
                random.choice(['pending', 'processing', 'resolved']),
                region
            ))
        
        print(f"  - 为 {segment_name} 创建了 {num_records} 条巡查记录")
    
    conn.commit()
    print(f"\n成功！已为 {len(regions)} 个区域创建测试数据")
    
    # 显示每个区域的统计
    print("\n各区域记录统计:")
    cursor.execute("""
        SELECT region, COUNT(*) as count 
        FROM InspectionRecord 
        WHERE region IS NOT NULL 
        GROUP BY region 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['region']}: {row['count']} 条记录")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
