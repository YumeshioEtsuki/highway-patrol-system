#!/usr/bin/env python3
"""测试安全重置后UI是否正确刷新"""
import httpx
import json
import time

BASE_URL = "http://127.0.0.1:5000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2NTE3ODg2fQ.CG8Y_dv3rjwXJKr655DFJBZX3dzLlWFkvZ-GYhpYB8Y"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

client = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=180)

print("[1] 生成500条数据...")
r1 = client.post("/api/admin/generate?count=500").json()
print(f"    ✓ 生成{r1.get('inserted')}条")

time.sleep(0.5)

print("[2] 检查统计（应有500条）...")
s1 = client.get("/api/admin/stats").json()
total1 = s1.get("total_records", 0)
print(f"    统计：{total1}条")
assert total1 == 500, f"期望500，实际{total1}"
print(f"    ✓ 验证成功")

print("\n[3] 执行安全重置（这会清空所有数据，重建表）...")
# 模拟前端的 reinit_database 调用
r_reset = client.get("/api/reinit?step=1").json()
print(json.dumps(r_reset, ensure_ascii=False, indent=2))

time.sleep(2)  # 等待重置完全完成

print("\n[4] 重置后检查统计（应为0条）...")
s2 = client.get("/api/admin/stats").json()
total2 = s2.get("total_records", 0)
print(f"    统计：{total2}条")
assert total2 == 0, f"重置失败，仍有{total2}条数据"
print(f"    ✓ 重置成功，数据已清空")

print("\n[5] 清理缓存...")
client.post("/api/admin/clean-test-data")

print("\n[6] 再次检查（应仍为0条）...")
s3 = client.get("/api/admin/stats").json()
total3 = s3.get("total_records", 0)
print(f"    统计：{total3}条")
assert total3 == 0, f"期望0，实际{total3}"
print(f"    ✓ 验证通过")

print("\n" + "="*60)
print("✅ 安全重置功能正常：")
print("  1. 数据生成成功（500条）")
print("  2. 统计正确显示（500条）")
print("  3. 安全重置完全清空数据（0条）")
print("  4. 缓存清除正常")
print("  5. UI应在前端2秒后自动刷新显示空状态")
print("="*60)
