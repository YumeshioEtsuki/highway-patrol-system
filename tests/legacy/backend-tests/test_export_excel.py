"""
测试导出Excel接口
"""
import requests

# 测试配置
BASE_URL = "http://127.0.0.1:5000"

# 1. 登录获取token
print("=" * 60)
print("步骤1: 登录获取token...")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

if login_response.status_code == 200:
    login_data = login_response.json()
    if login_data.get("success"):
        token = login_data["data"]["access_token"]
        print(f"✅ 登录成功! Token: {token[:50]}...")
    else:
        print(f"❌ 登录失败: {login_data.get('message')}")
        exit(1)
else:
    print(f"❌ 登录请求失败: {login_response.status_code}")
    print(f"响应: {login_response.text}")
    exit(1)

# 2. 测试导出Excel接口
print("\n" + "=" * 60)
print("步骤2: 测试导出Excel接口...")
print("=" * 60)

export_url = f"{BASE_URL}/api/export/excel"
headers = {
    "Authorization": f"Bearer {token}"
}

print(f"请求URL: {export_url}")
print(f"请求头: {headers}")

try:
    export_response = requests.get(
        export_url,
        headers=headers,
        timeout=30
    )
    
    print(f"\n响应状态码: {export_response.status_code}")
    print(f"响应头: {dict(export_response.headers)}")
    
    if export_response.status_code == 200:
        # 保存文件
        filename = "test_export.xlsx"
        with open(filename, 'wb') as f:
            f.write(export_response.content)
        print(f"✅ 导出成功! 文件已保存为: {filename}")
        print(f"文件大小: {len(export_response.content)} 字节")
    else:
        print(f"❌ 导出失败!")
        print(f"错误响应: {export_response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时（30秒）")
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
