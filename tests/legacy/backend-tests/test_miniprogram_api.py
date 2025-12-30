"""
小程序API测试脚本
测试后端接口是否正常工作
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def print_result(title, response):
    """打印测试结果"""
    print(f"\n{'='*60}")
    print(f"测试: {title}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")
    print('='*60)

def test_login():
    """测试登录接口"""
    # 微信登录通常需要 code，这里模拟
    payload = {
        "username": "test_user",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print_result("用户登录", response)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    return None

def test_register():
    """测试注册接口"""
    payload = {
        "username": "mini_program_user",
        "password": "Test123456",
        "real_name": "小程序测试用户",
        "phone": "13800138000"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=payload)
    print_result("用户注册", response)

def test_patrol_list(token):
    """测试巡查记录列表"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/patrol", headers=headers)
    print_result("巡查记录列表", response)
    
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        if records:
            return records[0]['id']
    return None

def test_patrol_detail(token, record_id):
    """测试巡查记录详情"""
    if not record_id:
        print("\n⚠️  没有记录ID，跳过详情测试")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/patrol/{record_id}", headers=headers)
    print_result(f"巡查记录详情 (ID: {record_id})", response)

def test_stats(token):
    """测试统计接口"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/stats", headers=headers)
    print_result("用户统计信息", response)

def test_admin_patrol_list(token):
    """测试管理员巡查列表"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试不同筛选条件
    params_list = [
        {},
        {"status_filter": "pending"},
        {"status_filter": "processing"},
        {"status_filter": "completed"}
    ]
    
    for params in params_list:
        response = requests.get(f"{BASE_URL}/admin/patrol/list", 
                              headers=headers, 
                              params=params)
        filter_text = params.get('status_filter', '全部')
        print_result(f"管理员记录列表 (筛选: {filter_text})", response)

def test_admin_stats(token):
    """测试管理员统计"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    print_result("管理员统计信息", response)

def test_road_segments():
    """测试路段列表"""
    response = requests.get(f"{BASE_URL}/road-segments")
    print_result("路段列表", response)

def test_issue_types():
    """测试问题类型列表"""
    response = requests.get(f"{BASE_URL}/issue-types")
    print_result("问题类型列表", response)

def main():
    """主测试流程"""
    print("\n" + "🧪 " * 30)
    print("小程序后端API测试")
    print("🧪 " * 30)
    
    # 1. 测试公开接口
    print("\n\n📋 第1阶段: 公开接口测试")
    test_road_segments()
    test_issue_types()
    
    # 2. 测试登录
    print("\n\n🔐 第2阶段: 认证测试")
    token = test_login()
    
    if not token:
        print("\n❌ 登录失败，尝试注册新用户...")
        test_register()
        time.sleep(1)
        token = test_login()
    
    if not token:
        print("\n❌ 无法获取Token，后续测试终止")
        return
    
    print(f"\n✅ 获取到Token: {token[:20]}...")
    
    # 3. 测试巡查员接口
    print("\n\n👷 第3阶段: 巡查员接口测试")
    record_id = test_patrol_list(token)
    test_patrol_detail(token, record_id)
    test_stats(token)
    
    # 4. 测试管理员接口
    print("\n\n👨‍💼 第4阶段: 管理员接口测试")
    test_admin_patrol_list(token)
    test_admin_stats(token)
    
    # 总结
    print("\n\n" + "✅ " * 30)
    print("测试完成！")
    print("✅ " * 30)
    print("\n📝 测试总结:")
    print("1. 如果看到大量401错误，说明Token认证有问题")
    print("2. 如果看到404错误，说明路由不存在")
    print("3. 如果看到422错误，说明请求参数格式不正确")
    print("4. 如果看到500错误，检查后端日志查看详细错误")
    print("\n💡 下一步:")
    print("1. 在微信开发者工具中导入小程序代码")
    print("2. 配置baseUrl为 http://127.0.0.1:5000")
    print("3. 关闭域名校验")
    print("4. 测试登录、创建、审核流程")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
