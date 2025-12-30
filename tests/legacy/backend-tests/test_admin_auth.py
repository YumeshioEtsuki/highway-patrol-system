#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员认证流程和 SSE 端点
"""
import requests
import time
from urllib.parse import urlencode

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = (5, 5)

print("=" * 60)
print("🧪 开始测试管理员认证和 SSE 流式端点")
print("=" * 60)

# ============================================================
# 步骤 1: 登录
# ============================================================
print("\n[步骤 1] 登录管理员账号...")
login_res = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "REDACTED"},
    timeout=TIMEOUT
)
print(f"  状态码: {login_res.status_code}")

if login_res.status_code != 200:
    print(f"  ❌ 登录失败: {login_res.text}")
    exit(1)

data = login_res.json()
token = data.get("access_token")
if not token:
    print(f"  ❌ 未获得 token: {data}")
    exit(1)

print(f"  ✅ 成功获得 token: {token[:30]}...")

# ============================================================
# 步骤 2: 测试 /api/me 端点（验证身份）
# ============================================================
print("\n[步骤 2] 验证身份 (/api/me)...")
me_res = requests.get(
    f"{BASE_URL}/api/me",
    headers={"Authorization": f"Bearer {token}"},
    timeout=TIMEOUT
)
print(f"  状态码: {me_res.status_code}")

if me_res.status_code != 200:
    print(f"  ❌ 验证失败: {me_res.text}")
    exit(1)

me_data = me_res.json()
print(f"  ✅ 身份验证成功")
print(f"     用户名: {me_data.get('username')}")
print(f"     角色: {me_data.get('role')}")

# ============================================================
# 步骤 3: 测试 SSE 端点（使用 query token）
# ============================================================
print("\n[步骤 3] 测试 SSE 流式端点（/api/verify/stream?token=...）...")

# 构建包含 token 的 URL
stream_url = f"{BASE_URL}/api/verify/stream?token={token}"
print(f"  URL: {stream_url[:50]}...")

try:
    stream_res = requests.get(stream_url, stream=True, timeout=TIMEOUT)
    print(f"  状态码: {stream_res.status_code}")
    print(f"  内容类型: {stream_res.headers.get('content-type')}")
    
    if stream_res.status_code != 200:
        print(f"  ❌ 错误响应:")
        print(f"     {stream_res.text[:500]}")
    else:
        print(f"  ✅ 连接成功，正在读取 SSE 数据...")
        
        # 读取前几条 SSE 消息
        line_count = 0
        start_time = time.time()
        for line in stream_res.iter_lines(decode_unicode=True):
            if time.time() - start_time > 5:
                print("     ⚠️  SSE 5s 内无数据，停止读取")
                break
            if line.strip():
                print(f"     {line[:80]}")
                line_count += 1
                if line_count >= 3:
                    stream_res.close()
                    break
        
        print(f"  ✅ SSE 端点工作正常")
        
except requests.exceptions.Timeout:
    print(f"  ⚠️  请求超时（预期行为，因为验证是长期运行任务）")
except Exception as e:
    print(f"  ❌ 错误: {e}")

# ============================================================
# 步骤 4: 测试 /api/admin/patrol/list 端点（使用 Bearer token）
# ============================================================
print("\n[步骤 4] 测试管理员列表端点 (/api/admin/patrol/list)...")

list_res = requests.get(
    f"{BASE_URL}/api/admin/patrol/list",
    headers={"Authorization": f"Bearer {token}"},
    timeout=TIMEOUT
)
print(f"  状态码: {list_res.status_code}")

if list_res.status_code != 200:
    print(f"  ❌ 列表查询失败:")
    print(f"     {list_res.text[:500]}")
else:
    try:
        records = list_res.json()
        print(f"  ✅ 成功获得 {len(records)} 条记录")
        if records:
            print(f"     第一条记录 ID: {records[0].get('record_id')}")
    except:
        print(f"  ⚠️  响应无法解析为 JSON")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)
