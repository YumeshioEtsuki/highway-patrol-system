#!/usr/bin/env python
"""
Phase 1 Step 3 监控系统测试脚本
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
ADMIN_TOKEN = "your_admin_token_here"  # 需要替换为有效的 admin token

def print_section(title):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_monitor_health_check():
    """测试健康检查"""
    print_section("测试 1: 系统健康检查")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/health-check",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功")
            print(f"   状态: {data.get('health', {}).get('status', 'unknown')}")
            print(f"   问题: {data.get('health', {}).get('issues', [])}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_metrics():
    """测试获取性能指标"""
    print_section("测试 2: 获取性能指标")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/metrics/current",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('data', {})
            print(f"✅ 性能指标获取成功")
            print(f"   查询速率: {metrics.get('queries_per_sec', 0):.2f} QPS")
            print(f"   慢查询: {metrics.get('slow_queries_per_min', 0)} /分钟")
            print(f"   活跃连接: {metrics.get('active_connections', 0)} 个")
            print(f"   平均查询时间: {metrics.get('avg_query_time_ms', 0):.1f} ms")
            print(f"   缓存命中率: {metrics.get('cache_hit_ratio', 0)*100:.1f}%")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_slow_queries():
    """测试获取慢查询"""
    print_section("测试 3: 获取慢查询")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/slow-queries?limit=5",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            queries = data.get('data', [])
            print(f"✅ 慢查询获取成功")
            print(f"   总数: {len(queries)} 条")
            if queries:
                for i, q in enumerate(queries[:3], 1):
                    print(f"   {i}. 耗时 {q.get('duration_ms', 0)} ms")
                    print(f"      扫描行: {q.get('rows_examined', 0)}")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_index_health():
    """测试获取索引健康状态"""
    print_section("测试 4: 获取索引健康状态")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/indexes/health",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            health = data.get('health_summary', {})
            print(f"✅ 索引健康状态获取成功")
            print(f"   总索引数: {health.get('total_indexes', 0)}")
            print(f"   健康索引: {health.get('healthy_indexes', 0)}")
            print(f"   健康评分: {health.get('health_score', 0):.1f}/100")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_recommendations():
    """测试获取优化建议"""
    print_section("测试 5: 获取优化建议")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/recommendations",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            recs = data.get('data', [])
            print(f"✅ 优化建议获取成功")
            print(f"   待处理建议: {len(recs)} 条")
            if recs:
                for i, r in enumerate(recs[:3], 1):
                    print(f"   {i}. [{r.get('priority', 'MEDIUM')}] {r.get('description', '无描述')[:50]}")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_generate_recommendations():
    """测试生成优化建议"""
    print_section("测试 6: 生成优化建议")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/monitor/recommendations/generate",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 生成成功")
            print(f"   生成建议数: {data.get('generated', 0)}")
            print(f"   已保存: {data.get('saved', 0)}")
            return True
        else:
            print(f"❌ 生成失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_metrics_history():
    """测试获取指标历史"""
    print_section("测试 7: 获取指标历史")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/monitor/metrics/history?hours=24",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('data', {})
            print(f"✅ 指标历史获取成功")
            print(f"   数据点数: {len(history.get('timestamps', []))}")
            if history.get('timestamps'):
                print(f"   时间范围: {history['timestamps'][0]} 到 {history['timestamps'][-1]}")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_dashboard_page():
    """测试仪表板页面"""
    print_section("测试 8: 访问仪表板页面")
    
    try:
        response = requests.get(
            f"{BASE_URL}/monitor",
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ 仪表板页面访问成功")
            print(f"   页面大小: {len(response.content)} 字节")
            return True
        else:
            print(f"❌ 访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  Phase 1 Step 3 - 监控系统集成测试")
    print("  开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 检查服务器连通性
    print("\n检查服务器连通性...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 服务器已连接 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print(f"   确保服务器运行在 {BASE_URL}")
        return
    
    # 运行测试
    results = {
        "健康检查": test_monitor_health_check(),
        "获取指标": test_get_metrics(),
        "获取慢查询": test_get_slow_queries(),
        "索引健康": test_get_index_health(),
        "获取建议": test_get_recommendations(),
        "生成建议": test_generate_recommendations(),
        "指标历史": test_metrics_history(),
        "仪表板页面": test_dashboard_page(),
    }
    
    # 总结
    print_section("测试总结")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！监控系统已完全就绪。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查日志。")
    
    print("\n完成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    run_all_tests()
