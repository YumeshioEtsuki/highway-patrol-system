#!/usr/bin/env python3
"""测试管理员API的数据返回"""
import requests
import json
import sys

# 配置
BACKEND_URL = "http://127.0.0.1:5000"

def test_admin_stats():
    """测试 /api/admin/stats 端点"""
    print("=" * 60)
    print("测试 /api/admin/stats")
    print("=" * 60)
    
    # 首先登录获取 token
    login_response = requests.post(
        f"{BACKEND_URL}/api/user/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(login_response.text)
        return False
    
    login_data = login_response.json()
    token = login_data.get('access_token')
    print(f"✓ 登录成功，Token: {token[:20]}...")
    
    # 调用 stats 接口
    headers = {"Authorization": f"Bearer {token}"}
    try:
        stats_response = requests.get(
            f"{BACKEND_URL}/api/admin/stats",
            headers=headers,
            timeout=5
        )
        
        print(f"\n📊 HTTP 状态码: {stats_response.status_code}")
        
        if stats_response.status_code != 200:
            print(f"❌ 请求失败")
            print(stats_response.text)
            return False
        
        data = stats_response.json()
        print(f"\n📦 返回数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查关键字段
        required_fields = [
            'total_records',
            'status_breakdown',
            'type_breakdown',
            'severity_breakdown',
            'recent_7_days',
            'recent_30_days'
        ]
        
        print(f"\n✓ 数据字段检查:")
        for field in required_fields:
            if field in data:
                if isinstance(data[field], list):
                    print(f"  ✓ {field}: {len(data[field])} 项")
                else:
                    print(f"  ✓ {field}: {data[field]}")
            else:
                print(f"  ❌ 缺少字段: {field}")
        
        # 特别检查 type_breakdown
        if 'type_breakdown' in data:
            type_data = data['type_breakdown']
            print(f"\n🎯 问题类型分布详情 ({len(type_data)} 项):")
            for item in type_data[:5]:
                print(f"    - {item.get('label', 'N/A')}: {item.get('count', 0)} 条")
            if len(type_data) > 5:
                print(f"    ... 还有 {len(type_data) - 5} 项")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_admin_stats()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
