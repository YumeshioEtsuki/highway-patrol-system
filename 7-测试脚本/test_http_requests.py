#!/usr/bin/env python3
"""
模拟完整的 HTTP 请求测试
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("HTTP 请求测试 - 压缩照片与月报")
print("=" * 70)

# 获取 token
print("\n[1] 获取认证令牌...")
login_resp = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "admin123"}
)
print(f"  状态: {login_resp.status_code}")

if login_resp.status_code == 200:
    token = login_resp.json().get("data", {}).get("access_token")
    if token:
        print(f"  ✓ 令牌获取成功")
    else:
        print(f"  ✗ 响应格式错误: {login_resp.json()}")
        exit(1)
else:
    print(f"  ✗ 登录失败: {login_resp.text}")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 测试 2: 压缩照片
print("\n[2] 压缩照片请求")
payload = {
    "photo_id": "1",
    "quality": 85
}
print(f"  请求体: {json.dumps(payload)}")

compress_resp = requests.post(
    f"{BASE_URL}/api/tasks/photo/compress",
    json=payload,
    headers=headers
)
print(f"  状态码: {compress_resp.status_code}")
print(f"  响应: {json.dumps(compress_resp.json(), indent=2, ensure_ascii=False)}")

# 测试 3: 生成月报
print("\n[3] 生成月报请求")
payload = {
    "year": 2025,
    "month": 12
}
print(f"  请求体: {json.dumps(payload)}")

monthly_resp = requests.post(
    f"{BASE_URL}/api/tasks/report/monthly",
    json=payload,
    headers=headers
)
print(f"  状态码: {monthly_resp.status_code}")
print(f"  响应: {json.dumps(monthly_resp.json(), indent=2, ensure_ascii=False)}")

print("\n" + "=" * 70)
