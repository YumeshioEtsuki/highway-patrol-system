#!/usr/bin/env python3
"""测试登录接口"""
import sys
import time
import json
import urllib.request
import urllib.error

time.sleep(1)  # 等待后端启动

url = "http://127.0.0.1:5000/api/login"
data = json.dumps({"username": "admin", "password": "admin"}).encode('utf-8')

try:
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        print(f"状态: {response.status}")
        print("响应:")
        result = json.loads(response.read().decode('utf-8'))
        print(json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"错误状态: {e.code}")
    print("响应:")
    try:
        error_content = json.loads(e.read().decode('utf-8'))
        print(json.dumps(error_content, indent=2, ensure_ascii=False))
    except:
        print(e.read().decode('utf-8', errors='replace'))
except Exception as e:
    print(f"异常: {e}")
    import traceback
    traceback.print_exc()
