#!/usr/bin/env python3
"""
【快速修复脚本】
根据诊断报告，自动修复项目中的常见问题

使用方法：
    cd 1-后端代码
    python ../7-测试脚本/quick_fix_script.py
"""

import sys
import os
sys.path.insert(0, '.')

def fix_1_clean_test_data():
    """修复1: 清理所有测试数据"""
    print("\n" + "="*60)
    print("【修复1】清理测试数据")
    print("="*60)
    
    from services.patrol_service import clean_test_data
    
    print("\n⚠️  警告: 此操作将删除所有 data_type='test' 的记录")
    confirm = input("确认继续? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ 操作已取消")
        return False
    
    try:
        result = clean_test_data()
        print(f"\n✅ 清理完成:")
        print(f"   • 删除记录: {result['deleted_count']} 条")
        print(f"   • 删除照片: {result['photos_deleted']} 张")
        return True
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False


def fix_2_generate_real_data():
    """修复2: 生成真实模拟数据"""
    print("\n" + "="*60)
    print("【修复2】生成真实模拟数据")
    print("="*60)
    
    from services.patrol_service import generate_fake_records
    
    try:
        count = input("输入要生成的数据条数 (默认100): ").strip()
        count = int(count) if count else 100
        
        print(f"\n正在生成 {count} 条真实模拟数据...")
        result = generate_fake_records(count=count, with_photos=False)
        
        if result['success']:
            print(f"\n✅ 生成完成:")
            print(f"   • 成功: {result['inserted']} 条")
            print(f"   • 失败: {result['failed']} 条")
            print(f"   • GPS分布: 按省份随机分布")
            return True
        else:
            print(f"❌ 生成失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False


def fix_3_create_indexes():
    """修复3: 创建数据库索引"""
    print("\n" + "="*60)
    print("【修复3】创建数据库索引以优化性能")
    print("="*60)
    
    from utils.utils import get_db_connection
    
    indexes = [
        ("idx_data_type", "CREATE INDEX idx_data_type ON InspectionRecord(data_type)"),
        ("idx_upload_time", "CREATE INDEX idx_upload_time ON InspectionRecord(upload_time)"),
        ("idx_status", "CREATE INDEX idx_status ON InspectionRecord(status)"),
        ("idx_user_id", "CREATE INDEX idx_user_id ON InspectionRecord(user_id)"),
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created = 0
    skipped = 0
    
    for idx_name, idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            conn.commit()
            print(f"✅ 索引创建成功: {idx_name}")
            created += 1
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️  索引已存在: {idx_name}")
                skipped += 1
            else:
                print(f"⚠️  索引创建失败 {idx_name}: {e}")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ 索引创建完成:")
    print(f"   • 新建: {created} 个")
    print(f"   • 已存在: {skipped} 个")
    return True


def fix_4_verify_schema():
    """修复4: 验证表结构"""
    print("\n" + "="*60)
    print("【修复4】验证表结构完整性")
    print("="*60)
    
    from utils.utils import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 检查data_type列
    print("\n4.1 检查 data_type 列:")
    cursor.execute("SHOW COLUMNS FROM InspectionRecord LIKE 'data_type'")
    col = cursor.fetchone()
    
    if col:
        print(f"   ✅ 列存在")
        print(f"      • 类型: {col['Type']}")
        print(f"      • Null: {col['Null']}")
        print(f"      • 默认值: {col['Default']}")
    else:
        print(f"   ⚠️  列不存在，尝试添加...")
        try:
            cursor.execute("""
                ALTER TABLE InspectionRecord 
                ADD COLUMN data_type ENUM('real','test') DEFAULT 'real'
                COMMENT '数据类型：real=真实数据，test=测试数据'
            """)
            conn.commit()
            print(f"   ✅ 列已添加")
        except Exception as e:
            print(f"   ❌ 添加失败: {e}")
    
    # 验证数据完整性
    print("\n4.2 数据类型分布:")
    cursor.execute("""
        SELECT 
            data_type,
            COUNT(*) as cnt,
            ROUND(COUNT(*)*100.0/
                (SELECT COUNT(*) FROM InspectionRecord), 1) as pct
        FROM InspectionRecord
        GROUP BY data_type
    """)
    
    for row in cursor.fetchall():
        print(f"   • {row['data_type']}: {row['cnt']} 条 ({row['pct']}%)")
    
    cursor.close()
    conn.close()
    return True


def fix_5_optimize_config():
    """修复5: 优化配置参数"""
    print("\n" + "="*60)
    print("【修复5】配置参数优化建议")
    print("="*60)
    
    print("\n5.1 当前配置检查:")
    
    try:
        from utils.config import settings
        from settings import settings as settings2
        
        configs = {
            'MAX_PAGE_SIZE': settings.MAX_PAGE_SIZE,
            'JWT_EXPIRE_HOURS': settings.JWT_EXPIRE_HOURS,
            'DEBUG': settings.DEBUG,
        }
        
        for key, val in configs.items():
            print(f"   • {key}: {val}")
        
        print("\n5.2 生产环境建议:")
        
        if settings.DEBUG:
            print("   ⚠️  DEBUG=True 应改为 False 以用于生产环境")
        
        if settings.MAX_PAGE_SIZE < 200:
            print(f"   💡 MAX_PAGE_SIZE={settings.MAX_PAGE_SIZE} 可增加至 300-500")
        
        if settings.JWT_EXPIRE_HOURS == 24:
            print(f"   ℹ️  JWT_EXPIRE_HOURS=24 对中等系统合理")
        
        print("\n   修改方法: 编辑 .env 文件或 utils/config.py")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
    
    return True


def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + "  🔧 公路巡查系统 - 快速修复工具 v1.0".ljust(59) + "║")
    print("║" + "".ljust(59) + "║")
    print("║" + "  注: 所有修复都可逆，修复前会提示确认".ljust(59) + "║")
    print("╚" + "="*58 + "╝\n")
    
    while True:
        print("\n" + "="*60)
        print("【可用修复选项】")
        print("="*60)
        print("\n1. 清理所有测试数据 (删除data_type='test'的记录)")
        print("2. 生成真实模拟数据 (按省份分布的GPS坐标)")
        print("3. 创建数据库索引 (优化查询性能)")
        print("4. 验证表结构 (检查data_type列等)")
        print("5. 配置参数优化 (查看建议)")
        print("0. 退出\n")
        
        choice = input("请选择 (0-5): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            fix_1_clean_test_data()
        elif choice == '2':
            fix_2_generate_real_data()
        elif choice == '3':
            fix_3_create_indexes()
        elif choice == '4':
            fix_4_verify_schema()
        elif choice == '5':
            fix_5_optimize_config()
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按Enter继续...")


if __name__ == '__main__':
    main()
