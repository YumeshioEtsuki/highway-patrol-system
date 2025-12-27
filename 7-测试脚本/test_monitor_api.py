#!/usr/bin/env python3
"""
测试后端 Monitor API
直接从 Python 代码调用，避免 HTTP 请求复杂性
"""
import sys
import os

# 添加后端代码目录到 Python 路径
sys.path.insert(0, r'd:\MySQL Project\highway-patrol-system\1-后端代码')

from utils.metrics_collector import MetricsCollector

print("=" * 60)
print("Monitor API 诊断")
print("=" * 60)

# 测试 1: get_latest_metrics (查询 performance_metrics 表)
print("\n[1] 测试 get_latest_metrics() - 查询表最新记录")
try:
    result = MetricsCollector.get_latest_metrics()
    if result is None:
        print("  ⚠️  表为空或不存在（这会触发 fallback）")
    else:
        print(f"  ✓ 成功获取最新数据:")
        for key, val in result.items():
            print(f"    - {key}: {val}")
except Exception as e:
    print(f"  ✗ 查询失败: {e}")

# 测试 2: collect_current_metrics (实时采集)
print("\n[2] 测试 collect_current_metrics() - 实时采集性能指标")
try:
    result = MetricsCollector.collect_current_metrics()
    if result is None:
        print("  ✗ 收集失败，返回 None")
    else:
        print(f"  ✓ 成功采集数据:")
        for key, val in result.items():
            print(f"    - {key}: {val}")
except Exception as e:
    print(f"  ✗ 采集失败: {e}")

# 测试 3: 模拟 API 响应逻辑
print("\n[3] 模拟 API 响应逻辑 (get_current_metrics 端点)")
try:
    metrics = MetricsCollector.get_latest_metrics()
    
    if metrics is None:
        print("  [step 1] 表为空，触发 fallback")
        metrics = MetricsCollector.collect_current_metrics()
        
        if metrics is None:
            print("  [step 2] collect_current_metrics() 返回 None，使用硬编码默认值")
            from datetime import datetime
            metrics = {
                "queries_per_sec": 1.2,
                "slow_queries_per_min": 0,
                "active_connections": 5,
                "avg_query_time_ms": 50.0,
                "cache_hit_ratio": 0.95,
                "lock_wait_time_ms": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    # API 响应格式
    response = {
        "status": "success",
        "data": metrics
    }
    
    print(f"\n  ✓ 最终 API 响应:")
    print(f"    status: {response['status']}")
    print(f"    data: {response['data']}")
    
except Exception as e:
    print(f"  ✗ 模拟失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
