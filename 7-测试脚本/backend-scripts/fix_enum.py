#!/usr/bin/env python3
"""
快速修复脚本：修改 InspectionRecord 表的 status 枚举定义
添加缺失的 'completed' 值
"""
import mysql.connector
from utils.config import db_config

def fix_enum():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("📋 开始修改表枚举...")
        
        # 执行 ALTER TABLE 修改 status 枚举
        sql = """
        ALTER TABLE InspectionRecord 
        MODIFY status ENUM('pending', 'processing', 'completed', 'resolved') DEFAULT 'pending'
        """
        cursor.execute(sql)
        conn.commit()
        
        print("✅ 成功！status 枚举已更新为: pending, processing, completed, resolved")
        
        # 验证修改
        cursor.execute("DESCRIBE InspectionRecord status")
        result = cursor.fetchone()
        print(f"📊 当前字段定义: {result}")
        
    except Exception as e:
        print(f"❌ 修改失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True

if __name__ == '__main__':
    success = fix_enum()
    if success:
        print("\n✨ 表结构已修复，请重启 FastAPI 后重试完成操作")
    else:
        print("\n⚠️ 修改失败，请手动在数据库执行:")
        print("ALTER TABLE InspectionRecord MODIFY status ENUM('pending','processing','completed','resolved') DEFAULT 'pending';")
