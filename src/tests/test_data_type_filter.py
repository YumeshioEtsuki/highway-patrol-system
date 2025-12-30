"""
测试数据类型过滤问题
"""
import requests
import json
from utils.config import settings

BASE_URL = "http://127.0.0.1:5000"

# 测试数据
TEST_CASES = [
    {
        "name": "全部数据（不发送data_type参数）",
        "params": {
            "page": 1,
            "page_size": 10
        }
    },
    {
        "name": "仅真实数据（data_type=real）",
        "params": {
            "data_type": "real",
            "page": 1,
            "page_size": 10
        }
    },
    {
        "name": "仅测试数据（data_type=test）",
        "params": {
            "data_type": "test",
            "page": 1,
            "page_size": 10
        }
    }
]

def test_api():
    """测试 API"""
    # 首先获取 token（使用默认管理员账号）
    login_resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "REDACTED"}
    )
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.text}")
        return
    
    token = login_resp.json().get("data", {}).get("access_token")
    if not token:
        print(f"❌ 无法获取 token")
        return
    
    print(f"✅ 成功登录，token: {token[:30]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for test_case in TEST_CASES:
        print(f"{'='*60}")
        print(f"📋 测试: {test_case['name']}")
        print(f"{'='*60}")
        
        url = f"{BASE_URL}/api/admin/patrol/list"
        params = test_case["params"]
        
        print(f"🌐 URL: {url}")
        print(f"📝 参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.get(url, params=params, headers=headers)
            
            print(f"📊 状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                total = data.get("total", 0)
                
                print(f"✅ 成功!")
                print(f"   总记录数: {total}")
                print(f"   当前页记录数: {len(records)}")
                
                if records:
                    print(f"   首条记录:")
                    first = records[0]
                    print(f"      ID: {first.get('record_id')}")
                    print(f"      data_type: {first.get('data_type')}")
                    print(f"      上报人: {first.get('reporter')}")
            else:
                print(f"❌ 错误: {resp.text}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_api()
