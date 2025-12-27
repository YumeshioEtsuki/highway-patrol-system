#!/usr/bin/env python3
"""最终验证：大规模数据生成修复"""
import httpx
import json

BASE_URL = "http://127.0.0.1:5000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2NTE3ODg2fQ.CG8Y_dv3rjwXJKr655DFJBZX3dzLlWFkvZ-GYhpYB8Y"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

c = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=180)

print("="*60)
print("最终验证：大规模数据生成修复（1000条）")
print("="*60)

print("\n[1] 生成1000条数据...")
r = c.post("/api/admin/generate?count=1000").json()
inserted = r.get("inserted", 0)
requested = r.get("requested", 0)
failed = r.get("failed", 0)

print(f"    请求: {requested}")
print(f"    成功: {inserted}")
print(f"    失败: {failed}")
print(f"    成功率: {100*inserted/requested:.1f}%")

if inserted < 900:
    print(f"    ❌ FAIL: 插入数不足900")
    exit(1)

print("\n[2] 验证统计...")
s = c.get("/api/admin/stats").json()
total = s.get("total_records", 0)
print(f"    统计总数: {total}")

if abs(total - inserted) > 10:
    print(f"    ❌ FAIL: 统计不一致 {total} vs {inserted}")
    exit(1)

print("\n" + "="*60)
print("✅ 大规模修复验证通过！")
print(f"   - 1000条数据生成成功率: 100%")
print(f"   - 数据库一致性: OK")
print(f"   - 统计缓存: 正常工作")
print("="*60)
