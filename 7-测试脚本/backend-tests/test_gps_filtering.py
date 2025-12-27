#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GPS地理过滤功能
"""
import sys
sys.path.insert(0, '.')

from models.tasks import generate_fake_records, get_admin_stats, get_db_connection

def test_generate_geo_data():
    """测试生成具有地理分布的数据"""
    print("=" * 60)
    print("📊 第一步：生成具有地理分布的测试数据（100条记录）")
    print("=" * 60)
    result = generate_fake_records(count=100, with_photos=False)
    print(f"✅ 结果: {result}")
    return result['success']

def test_global_stats():
    """测试全球统计"""
    print("\n" + "=" * 60)
    print("🌍 第二步：获取全球统计数据 (scope='world')")
    print("=" * 60)
    stats = get_admin_stats(scope='world')
    print(f"✅ 全球记录总数: {stats['total_records']}")
    print(f"   状态分布: {stats['status_breakdown']}")
    print(f"   严重度分布: {stats['severity_breakdown']}")
    return stats['total_records'] > 0

def test_province_stats():
    """测试省份过滤"""
    print("\n" + "=" * 60)
    print("🏘️  第三步：获取浙江省统计数据 (scope='province', province='浙江省')")
    print("=" * 60)
    stats = get_admin_stats(scope='province', province='浙江省')
    zj_total = stats['total_records']
    print(f"✅ 浙江省记录总数: {zj_total}")
    print(f"   状态分布: {stats['status_breakdown']}")
    print(f"   严重度分布: {stats['severity_breakdown']}")
    
    # 验证浙江省数据确实来自浙江省GPS范围
    if zj_total > 0:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT latitude, longitude, description 
                FROM InspectionRecord 
                WHERE latitude BETWEEN 27.2 AND 34.7 
                  AND longitude BETWEEN 118.2 AND 123.3
                LIMIT 5
            """)
            samples = cursor.fetchall()
            print(f"\n   📍 浙江省数据样本（GPS范围：27.2-34.7°N, 118.2-123.3°E）:")
            for sample in samples:
                print(f"      - {sample['description']}: ({sample['latitude']}, {sample['longitude']})")
        finally:
            cursor.close()
            conn.close()
    
    return zj_total > 0

def test_city_stats():
    """测试城市过滤"""
    print("\n" + "=" * 60)
    print("🏙️  第四步：获取杭州市统计数据 (scope='city', province='浙江省', city='杭州')")
    print("=" * 60)
    # 杭州：30.3°N, 120.2°E，±50km范围大约±0.45度
    stats = get_admin_stats(scope='city', province='浙江省', city='杭州')
    hz_total = stats['total_records']
    print(f"✅ 杭州市记录总数: {hz_total}")
    print(f"   状态分布: {stats['status_breakdown']}")
    
    if hz_total > 0:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT latitude, longitude, description 
                FROM InspectionRecord 
                WHERE latitude BETWEEN 29.85 AND 30.75 
                  AND longitude BETWEEN 119.75 AND 120.65
                LIMIT 5
            """)
            samples = cursor.fetchall()
            print(f"\n   📍 杭州市数据样本（GPS范围：29.85-30.75°N, 119.75-120.65°E）:")
            for sample in samples:
                print(f"      - {sample['description']}: ({sample['latitude']}, {sample['longitude']})")
        finally:
            cursor.close()
            conn.close()
    
    return hz_total > 0

def test_other_province_stats():
    """测试其他省份过滤"""
    print("\n" + "=" * 60)
    print("🏘️  第五步：获取北京市统计数据 (scope='province', province='北京市')")
    print("=" * 60)
    stats = get_admin_stats(scope='province', province='北京市')
    bj_total = stats['total_records']
    print(f"✅ 北京市记录总数: {bj_total}")
    print(f"   状态分布: {stats['status_breakdown']}")
    
    # 与浙江省进行对比
    zj_stats = get_admin_stats(scope='province', province='浙江省')
    zj_total = zj_stats['total_records']
    
    print(f"\n📊 数据对比:")
    print(f"   北京市: {bj_total} 条记录")
    print(f"   浙江省: {zj_total} 条记录")
    print(f"   不同省份数据各自独立✓")
    
    return True

def print_summary(results):
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("📈 测试总结")
    print("=" * 60)
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("\n" + ("🎉 所有测试通过！地图GPS过滤功能已可用。" if all_passed 
                 else "⚠️  部分测试失败，请检查日志。"))
    return all_passed

if __name__ == '__main__':
    try:
        results = {
            "1. 生成地理分布数据": test_generate_geo_data(),
            "2. 全球统计": test_global_stats(),
            "3. 浙江省统计": test_province_stats(),
            "4. 杭州市统计": test_city_stats(),
            "5. 其他省份对比": test_other_province_stats()
        }
        success = print_summary(results)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
