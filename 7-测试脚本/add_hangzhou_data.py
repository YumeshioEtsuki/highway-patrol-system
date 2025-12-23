#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为杭州市生成专用测试数据
"""
import sys
sys.path.insert(0, '.')

from utils.utils import get_db_connection
from datetime import datetime, timedelta
import random

def generate_hangzhou_records(count=20):
    """为杭州市生成精准的测试数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取用户、路段、问题类型
        cursor.execute("SELECT user_id FROM User ORDER BY user_id LIMIT 1")
        user_row = cursor.fetchone()
        if not user_row:
            raise ValueError("无可用用户")
        user_id = user_row[0]

        cursor.execute("SELECT segment_id FROM RoadSegment")
        segments = [r[0] for r in cursor.fetchall()] or [None]

        cursor.execute("SELECT type_id FROM ProblemType")
        types = [r[0] for r in cursor.fetchall()] or [None]

        now = datetime.now()
        statuses = ['pending', 'processing', 'resolved']
        
        # 杭州市GPS范围：30.3°N±1.5度, 120.2°E±1.2度 (更大范围以增加概率)
        lat_min, lat_max = 28.8, 31.8
        lon_min, lon_max = 118.7, 121.7

        for i in range(count):
            dt = now - timedelta(days=random.randint(0, 30), seconds=random.randint(0, 86400))
            lat = round(random.uniform(lat_min, lat_max), 6)
            lon = round(random.uniform(lon_min, lon_max), 6)
            sev = random.randint(1, 5)
            status = random.choices(statuses, weights=[6, 3, 1])[0]
            seg = random.choice(segments)
            typ = random.choice(types)
            desc = f"[杭州市] 测试记录 #{i+1}"

            cursor.execute(
                """
                INSERT INTO InspectionRecord (
                    user_id, upload_time, latitude, longitude,
                    segment_id, problem_type_id, description, severity, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, dt.strftime('%Y-%m-%d %H:%M:%S'), lat, lon, seg, typ, desc, sev, status)
            )
        
        conn.commit()
        print(f"✅ 已生成 {count} 条杭州市测试数据")
        print(f"   GPS范围: {lat_min}°-{lat_max}°N, {lon_min}°-{lon_max}°E")
        
        # 显示样本
        cursor.execute("""
            SELECT latitude, longitude, description 
            FROM InspectionRecord 
            WHERE latitude BETWEEN 28.8 AND 31.8 
              AND longitude BETWEEN 118.7 AND 121.7
            LIMIT 5
        """)
        samples = cursor.fetchall()
        print(f"\n   📍 样本数据:")
        for sample in samples:
            print(f"      - {sample[2]}: ({sample[0]}, {sample[1]})")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🏙️  为杭州市生成专用测试数据")
    print("=" * 60)
    success = generate_hangzhou_records(count=20)
    sys.exit(0 if success else 1)
