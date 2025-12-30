"""
快速测试：创建测试用户并测试登录
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

# 测试用户信息
TEST_USERS = [
    {
        "username": "patrol_test",
        "password": "Test123456",
        "real_name": "巡查员测试",
        "phone": "13800000001"
    },
    {
        "username": "admin_test",
        "password": "Admin123456",
        "real_name": "管理员测试",
        "phone": "13800000002"
    }
]

def create_test_users():
    """创建测试用户"""
    print("📝 创建测试用户...\n")
    
    for user in TEST_USERS:
        print(f"注册用户: {user['username']}")
        response = requests.post(f"{BASE_URL}/register", json=user)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功: {data}")
        elif response.status_code == 422:
            print("⚠️  用户可能已存在，尝试登录...")
        else:
            print(f"❌ 失败: {response.text}")
        print()

def test_login(username, password):
    """测试登录"""
    print(f"🔐 测试登录: {username}")
    
    payload = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功!")
        # 后端返回 access_token 字段
        token = data.get('access_token') or data.get('token')
        print(f"Token: {token[:30] if token else 'N/A'}...")
        print(f"User ID: {data.get('user', {}).get('user_id')}")
        print(f"Role: {data.get('user', {}).get('role')}")
        return token
    else:
        print(f"❌ 登录失败: {response.json()}")
    
    print()
    return None

def test_create_patrol(token):
    """测试创建巡查记录（FormData方式）"""
    print("📝 测试创建巡查记录...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 使用FormData
    data = {
        "segment_id": 1,
        "issue_type_id": 1,
        "description": "测试记录：路面破损严重",
        "severity": 4,
        "latitude": 39.9042,
        "longitude": 116.4074
    }
    
    response = requests.post(f"{BASE_URL}/patrol", headers=headers, data=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 创建成功!")
        print(f"记录ID: {result.get('record_id')}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result.get('record_id')
    else:
        print(f"❌ 创建失败: {response.text}")
    
    print()
    return None

def main():
    print("=" * 60)
    print("快速测试流程")
    print("=" * 60 + "\n")
    
    # 1. 创建用户
    create_test_users()
    
    # 2. 测试登录
    print("-" * 60)
    token = test_login("patrol_test", "Test123456")
    
    if not token:
        print("\n❌ 无法获取token，测试终止")
        return
    
    # 3. 测试创建记录
    print("-" * 60)
    record_id = test_create_patrol(token)
    
    # 4. 测试查询列表
    if record_id:
        print("-" * 60)
        print("📋 测试查询记录列表...\n")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/patrol", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 查询成功!")
            print(f"总记录数: {data.get('total', 0)}")
            print(f"记录列表: {len(data.get('records', []))} 条")
        else:
            print(f"❌ 查询失败: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
