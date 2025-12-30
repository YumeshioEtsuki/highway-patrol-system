"""执行数据库Schema更新：添加region字段"""
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='road_patrol_db'
    )
    cursor = conn.cursor()
    
    print("🔄 正在添加region字段...")
    
    # 为RoadSegment添加region字段
    try:
        cursor.execute("""
            ALTER TABLE RoadSegment 
            ADD COLUMN region VARCHAR(50) DEFAULT NULL 
            COMMENT '所属大洲：North America, South America, Europe, Africa, Asia, Oceania, Antarctica'
        """)
        print("✅ RoadSegment.region字段添加成功")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("⏭️  RoadSegment.region字段已存在，跳过")
        else:
            raise
    
    # 为InspectionRecord添加region字段
    try:
        cursor.execute("""
            ALTER TABLE InspectionRecord 
            ADD COLUMN region VARCHAR(50) DEFAULT NULL 
            COMMENT '所属大洲（冗余字段，从RoadSegment继承）'
        """)
        print("✅ InspectionRecord.region字段添加成功")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("⏭️  InspectionRecord.region字段已存在，跳过")
        else:
            raise
    
    # 创建索引
    try:
        cursor.execute("CREATE INDEX idx_region_rs ON RoadSegment(region)")
        print("✅ RoadSegment索引创建成功")
    except mysql.connector.Error as e:
        if "Duplicate key name" in str(e):
            print("⏭️  RoadSegment索引已存在，跳过")
        else:
            print(f"⚠️  索引创建警告: {e}")
    
    try:
        cursor.execute("CREATE INDEX idx_region_ir ON InspectionRecord(region)")
        print("✅ InspectionRecord索引创建成功")
    except mysql.connector.Error as e:
        if "Duplicate key name" in str(e):
            print("⏭️  InspectionRecord索引已存在，跳过")
        else:
            print(f"⚠️  索引创建警告: {e}")
    
    # 为现有路段数据分配默认区域
    cursor.execute("UPDATE RoadSegment SET region = 'Asia' WHERE region IS NULL")
    updated_segments = cursor.rowcount
    print(f"✅ 已为 {updated_segments} 个路段设置默认区域：Asia")
    
    # 同步巡查记录的region字段
    cursor.execute("""
        UPDATE InspectionRecord ir
        INNER JOIN RoadSegment rs ON ir.segment_id = rs.segment_id
        SET ir.region = rs.region
        WHERE ir.region IS NULL
    """)
    updated_records = cursor.rowcount
    print(f"✅ 已同步 {updated_records} 条巡查记录的区域信息")
    
    conn.commit()
    print("\n🎉 数据库Schema更新完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    if conn:
        conn.rollback()
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
