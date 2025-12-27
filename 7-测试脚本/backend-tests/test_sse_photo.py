#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SSE照片推送功能
运行此脚本后，访问 http://127.0.0.1:5000/admin.html，
然后点击"生成测试数据"并勾选"同时生成照片"，
观察"实时新照片"区域是否有新照片显示。
"""

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(env_path)

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:5000")
ADMIN_USER = os.getenv("TEST_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    raise ValueError("❌ TEST_ADMIN_PASSWORD 未配置！请在环境变量或 .env 中设置测试账号密码")

def test_sse_photos():
    print("=" * 60)
    print("SSE 照片推送功能测试")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n[步骤1] 登录获取访问令牌...")
    login_resp = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD}
    )
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(login_resp.text)
        return
    
    token = login_resp.json()["access_token"]
    print(f"✅ 登录成功，获取到token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 启动SSE监听（在另一个线程中）
    print("\n[步骤2] 启动SSE照片流监听...")
    import threading
    received_photos = []
    
    def listen_sse():
        try:
            resp = requests.get(
                f"{BASE_URL}/api/patrol/photos/stream",
                headers=headers,
                stream=True,
                timeout=30
            )
            print("✅ SSE连接已建立")
            
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data:'):
                        data_str = decoded[5:].strip()
                        if data_str and data_str != ': ping':
                            print(f"📸 收到照片事件: {data_str}")
                            received_photos.append(data_str)
        except Exception as e:
            print(f"⚠️ SSE监听异常: {e}")
    
    sse_thread = threading.Thread(target=listen_sse, daemon=True)
    sse_thread.start()
    time.sleep(2)  # 等待连接建立
    
    # 3. 生成带照片的测试数据
    print("\n[步骤3] 生成5条带照片的测试数据...")
    gen_resp = requests.post(
        f"{BASE_URL}/api/admin/generate?count=5&include_photos=true",
        headers=headers
    )
    
    if gen_resp.status_code != 200:
        print(f"❌ 生成失败: {gen_resp.status_code}")
        print(gen_resp.text)
        return
    
    result = gen_resp.json()
    print(f"✅ 生成成功: {result}")
    
    # 4. 等待SSE推送
    print("\n[步骤4] 等待SSE推送（最多10秒）...")
    for i in range(10):
        time.sleep(1)
        print(f"  等待中... {i+1}/10秒，已收到 {len(received_photos)} 条照片事件")
        if len(received_photos) >= 5:
            break
    
    # 5. 结果验证
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"生成记录数: {result.get('inserted', 0)}")
    print(f"收到照片事件数: {len(received_photos)}")
    
    if len(received_photos) > 0:
        print("\n✅ SSE照片推送功能正常！")
        print("收到的照片事件:")
        for i, photo in enumerate(received_photos[:5], 1):
            print(f"  {i}. {photo}")
    else:
        print("\n❌ 未收到任何照片事件，可能的原因：")
        print("  1. SSE推送代码未正确调用")
        print("  2. 队列已满或推送失败")
        print("  3. 网络连接问题")
    
    print("\n💡 提示：在浏览器中访问 http://127.0.0.1:5000/admin.html")
    print("   刷新页面后，查看'实时新照片'区域是否显示照片")
    print("=" * 60)


if __name__ == "__main__":
    test_sse_photos()
