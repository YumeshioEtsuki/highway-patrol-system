#!/usr/bin/env python3
"""
第2层诊断：测试后端 API 响应
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("第2层：后端 API 响应检查")
print("=" * 60)

# 检查服务器是否运行
print("\n[2.0] 检查服务器连接...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/profile", timeout=5)
    # 任何响应都表示服务器在运行
    print("✓ 服务器运行中")
except Exception as e:
    print(f"✗ 无法连接服务器: {e}")
    print("  请确保在端口 5000 运行了 FastAPI 服务器")
    sys.exit(1)

# 模拟登录（注意：实际应该使用真实的登录流程）
print("\n[2.1] 获取认证令牌...")
login_data = {
    "username": "admin",
    "password": "admin123"  # 这是测试密码
}
try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get("data", {}).get("access_token")
        if token:
            print(f"✓ 登录成功，令牌已获取")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"✗ 无法获取令牌: {response.json()}")
            sys.exit(1)
    else:
        print(f"✗ 登录失败: {response.status_code}")
        print(f"  响应: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"✗ 登录请求失败: {e}")
    sys.exit(1)

# 测试照片接口
print("\n[2.2] 测试 /api/photos/user 接口...")
try:
    response = requests.get(
        f"{BASE_URL}/api/photos/user",
        headers=headers,
        timeout=10
    )
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get("success"):
            photos = data.get("data", [])
            print(f"\n  ✓ 返回 {len(photos)} 张照片")
            
            if photos:
                # 检查数据格式
                first_photo = photos[0]
                print(f"\n  第一张照片数据结构:")
                for key, val in first_photo.items():
                    print(f"    - {key}: {val} ({type(val).__name__})")
                    
                # 验证必要字段
                required_fields = ['id', 'filename']
                missing = [f for f in required_fields if f not in first_photo]
                if missing:
                    print(f"\n  ✗ 缺少必要字段: {missing}")
                else:
                    print(f"\n  ✓ 包含所有必要字段: {required_fields}")
        else:
            print(f"  ✗ 响应标记为失败")
            
    else:
        print(f"  ✗ API 请求失败")
        print(f"  响应: {response.text}")
        
except Exception as e:
    print(f"✗ API 请求出错: {e}")
    sys.exit(1)

# 测试监控接口
print("\n[2.3] 测试 /api/admin/monitor/metrics/current 接口...")
try:
    response = requests.get(
        f"{BASE_URL}/api/admin/monitor/metrics/current",
        headers=headers,
        timeout=10
    )
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  响应:")
        
        # 只显示关键部分
        if "data" in data:
            if data["data"] is None:
                print(f"    ✗ data 字段为 null")
            else:
                print(f"    ✓ data 字段有值:")
                metrics = data["data"]
                for key, val in list(metrics.items())[:5]:  # 只显示前5个指标
                    print(f"      - {key}: {val}")
                remaining = len(metrics) - 5
                if remaining > 0:
                    print(f"      ... 还有 {remaining} 个指标")
        else:
            print(f"    响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
    else:
        print(f"  ✗ API 请求失败")
        print(f"  响应: {response.text}")
        
except Exception as e:
    print(f"✗ API 请求出错: {e}")

print("\n" + "=" * 60)
print("第2层诊断完成")
print("=" * 60)

print("\n[后续步骤]")
print("1. 如果照片接口返回数据但 ID 格式错误 → 需要修改前端验证")
print("2. 如果照片接口没有返回任何数据 → 检查数据库关联")
print("3. 如果监控接口仍返回 null → 检查后端 collect_current_metrics() 函数")
