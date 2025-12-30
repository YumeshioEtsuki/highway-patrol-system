#!/usr/bin/env python3
import httpx
import json

BASE_URL = "http://127.0.0.1:5000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2NTE3ODg2fQ.CG8Y_dv3rjwXJKr655DFJBZX3dzLlWFkvZ-GYhpYB8Y"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

client = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=180)

print("[1] 清理旧数据...")
client.post("/api/admin/clean-test-data")

print("[2] 生成1000条数据...")
r = client.post("/api/admin/generate?count=1000").json()
print(json.dumps(r, ensure_ascii=False, indent=2))

print("\n[3] 验证统计...")
s = client.get("/api/admin/stats").json()
total = s.get("total_records", 0)
inserted = r.get("inserted", 0)
requested = r.get("requested", 0)
failed = r.get("failed", 0)
success_rate = (100 * inserted / requested) if requested > 0 else 0

print(f"\n📊 结果摘要：")
print(f"  请求数：{requested}")
print(f"  插入数：{inserted}")
print(f"  失败数：{failed}")
print(f"  成功率：{success_rate:.1f}%")
print(f"  统计总数：{total}")
