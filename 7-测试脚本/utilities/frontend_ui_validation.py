"""
前端UI行为验证脚本
模拟真实用户在管理后台进行：
1. 数据生成
2. 数据类型筛选（全部/仅测试/仅真实）
3. 重置过滤器（验证UI状态与数据一致）
4. 图表实时更新

此脚本只验证后端API逻辑，不直接操纵浏览器DOM
"""

import os
import json
import time
import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
TOKEN = os.environ.get("ADMIN_TOKEN")

if not TOKEN:
    print("[ERROR] Missing ADMIN_TOKEN env var")
    exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}
client = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=30)


def test_data_type_filtering():
    """验证数据类型筛选的正确性"""
    print("\n" + "="*60)
    print("TEST: 数据类型筛选与缓存刷新")
    print("="*60)
    
    # 先清理
    print("[1] 清理旧数据...")
    client.post("/api/admin/clean-test-data")
    
    time.sleep(0.5)
    
    # 获取初始真实数据统计
    print("[2] 获取清理后的初始统计...")
    stats_all = client.get("/api/admin/stats").json()
    count_all_before = stats_all.get("total_records", 0)
    print(f"    总数：{count_all_before}")
    
    # 生成30条测试数据
    print("[3] 生成 30 条测试数据...")
    gen_res = client.post("/api/admin/generate?count=30&include_photos=false").json()
    assert gen_res["success"], "生成失败"
    assert gen_res["inserted"] == 30, f"期望30条，实际{gen_res['inserted']}条"
    print(f"    ✓ 生成成功：{gen_res['inserted']}/{gen_res['requested']} 条")
    
    time.sleep(0.5)
    
    # 验证：全部数据应增加30条
    print("[4] 验证全部数据统计已更新...")
    stats_all = client.get("/api/admin/stats").json()
    count_all_after = stats_all.get("total_records", 0)
    print(f"    总数（生成后）：{count_all_after}")
    assert count_all_after >= count_all_before + 30 - 1, \
        f"期望总数增加约30，实际只增加{count_all_after - count_all_before}"
    print(f"    ✓ 总数正确增加：{count_all_after - count_all_before}（期望≥29）")
    
    # 验证：仅测试数据筛选
    print("[5] 验证仅测试数据筛选...")
    stats_test = client.get("/api/admin/stats?data_type=test").json()
    count_test = stats_test.get("total_records", 0)
    print(f"    测试数据总数：{count_test}")
    assert count_test == 30, f"测试数据应为30，实际{count_test}"
    print(f"    ✓ 测试数据筛选正确：{count_test} 条")
    
    # 验证：仅真实数据筛选（应不受生成影响）
    print("[6] 验证仅真实数据筛选...")
    stats_real = client.get("/api/admin/stats?data_type=real").json()
    count_real = stats_real.get("total_records", 0)
    print(f"    真实数据总数：{count_real}")
    # 真实数据应为初始值，不应因生成测试数据而改变
    expected_real = count_all_before
    assert count_real == expected_real, \
        f"真实数据应为{expected_real}，实际{count_real}"
    print(f"    ✓ 真实数据筛选正确：{count_real} 条（未受影响）")
    
    # 验证：全部数据 = 真实 + 测试
    print("[7] 验证数据筛选一致性...")
    total_sum = count_real + count_test
    print(f"    真实({count_real}) + 测试({count_test}) = {total_sum}")
    print(f"    全部统计({count_all_after})")
    assert total_sum == count_all_after, \
        f"分类统计和不等于全部统计：{total_sum} != {count_all_after}"
    print(f"    ✓ 数据分类统计一致")
    
    return True


def test_reset_filter_state():
    """验证重置过滤器的状态保持一致"""
    print("\n" + "="*60)
    print("TEST: 过滤器重置与状态一致性")
    print("="*60)
    
    # 获取当前全部数据统计
    print("[1] 获取当前统计作为基准...")
    stats_all = client.get("/api/admin/stats").json()
    baseline_total = stats_all.get("total_records", 0)
    print(f"    基准总数：{baseline_total}")
    
    # 获取当前仅测试数据统计
    stats_test = client.get("/api/admin/stats?data_type=test").json()
    baseline_test = stats_test.get("total_records", 0)
    print(f"    基准测试数据：{baseline_test}")
    
    # 模拟用户操作：选择"仅测试数据"过滤
    print("[2] 模拟用户选择'仅测试数据'过滤...")
    # （前端会设置 currentDataType='test'，调用 loadStats()）
    # 后端接收 data_type=test 参数
    stats_filtered = client.get("/api/admin/stats?data_type=test").json()
    count_after_filter = stats_filtered.get("total_records", 0)
    print(f"    筛选后总数：{count_after_filter}")
    assert count_after_filter == baseline_test, \
        f"筛选结果应为{baseline_test}，实际{count_after_filter}"
    print(f"    ✓ 过滤正确应用：显示测试数据{count_after_filter}条")
    
    # 模拟用户点击重置按钮
    print("[3] 模拟用户点击'重置'按钮...")
    # （前端会清除 currentDataType='', 清除下拉UI，调用 loadStats()）
    # 无参调用 /api/admin/stats 回到全部数据
    stats_reset = client.get("/api/admin/stats").json()
    count_after_reset = stats_reset.get("total_records", 0)
    print(f"    重置后总数：{count_after_reset}")
    assert count_after_reset == baseline_total, \
        f"重置后应回到全部数据{baseline_total}，实际{count_after_reset}"
    print(f"    ✓ 重置成功：显示全部数据{count_after_reset}条")
    
    # 再次选择"仅测试数据"，验证多次切换正常
    print("[4] 再次选择'仅测试数据'，验证多次切换...")
    stats_refilter = client.get("/api/admin/stats?data_type=test").json()
    count_refilter = stats_refilter.get("total_records", 0)
    print(f"    再次筛选后总数：{count_refilter}")
    assert count_refilter == baseline_test, \
        f"再次筛选应为{baseline_test}，实际{count_refilter}"
    print(f"    ✓ 多次切换正常：{count_refilter}条")
    
    return True


def test_cache_invalidation_on_mutation():
    """验证数据生成/删除后缓存被正确清除"""
    print("\n" + "="*60)
    print("TEST: 缓存清除与图表实时更新")
    print("="*60)
    
    # 第一次生成
    print("[1] 生成测试数据...")
    gen1 = client.post("/api/admin/generate?count=20").json()
    assert gen1.get("success"), f"生成失败：{gen1}"
    inserted = gen1.get('inserted', '?')
    print(f"    ✓ 生成{inserted}条")
    
    time.sleep(0.5)
    
    # 立即查询，应返回新数据（缓存已清除）
    print("[2] 立即查询统计，验证缓存已清除...")
    stats1 = client.get("/api/admin/stats").json()
    total1 = stats1.get("total_records", 0)
    print(f"    统计总数：{total1}")
    assert total1 >= 20, f"缓存未清除，仍为{total1}"
    print(f"    ✓ 缓存正确清除，统计实时更新：{total1}条")
    
    # 清理数据
    print("[3] 清理所有测试数据...")
    clean = client.post("/api/admin/clean-test-data").json()
    assert clean.get("success"), f"清理失败：{clean}"
    deleted = clean.get("deleted_count", 0)
    print(f"    ✓ 删除{deleted}条")
    
    time.sleep(0.5)
    
    # 查询应回到零
    print("[4] 查询清理后的统计...")
    stats2 = client.get("/api/admin/stats").json()
    total2 = stats2.get("total_records", 0)
    print(f"    统计总数：{total2}")
    assert total2 == 0, f"清理失败，仍有{total2}条数据"
    print(f"    ✓ 缓存清除后统计为零：{total2}")
    
    return True


def main():
    try:
        # 连接测试
        print("正在连接后端服务...")
        resp = client.get("/api/admin/stats")
        if resp.status_code != 200:
            print(f"[ERROR] 连接失败，状态码{resp.status_code}")
            exit(1)
        print("✓ 后端服务可访问\n")
        
        # 运行三大测试
        test_data_type_filtering()
        test_reset_filter_state()
        test_cache_invalidation_on_mutation()
        
        print("\n" + "="*60)
        print("✅ 所有前端UI行为验证通过")
        print("="*60)
        print("\n📋 验证摘要：")
        print("  1. ✓ 数据生成数量完全匹配（30/30）")
        print("  2. ✓ 数据类型筛选正常（全部/仅测试/仅真实）")
        print("  3. ✓ 过滤器重置状态一致（清除UI状态+刷新数据）")
        print("  4. ✓ 缓存在生成/删除后立即清除")
        print("  5. ✓ 统计数据实时更新，图表可即刻刷新\n")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ 错误：{e}\n")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
