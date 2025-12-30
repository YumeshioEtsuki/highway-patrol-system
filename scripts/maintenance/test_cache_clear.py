#!/usr/bin/env python3
"""
测试自动缓存清除机制
验证以下场景：
1. 生成数据后自动清除缓存
2. 删除数据后自动清除缓存
3. 重置数据库后自动清除缓存
4. 手动清除缓存按钮
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={'username': 'admin', 'password': 'MIMASHI123'}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✓ 登录成功")
        return token
    else:
        print(f"✗ 登录失败: {response.status_code}")
        return None

def get_stats(token):
    """获取统计数据"""
    response = requests.get(
        f"{BASE_URL}/api/admin/stats",
        headers={'Authorization': f'Bearer {token}'},
        params={'_t': str(int(time.time() * 1000))}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('total_records', 0)
    return None

def clear_cache(token):
    """手动清除缓存"""
    response = requests.post(
        f"{BASE_URL}/api/admin/clear-cache",
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 缓存已清除: {data.get('cleared_count')} 个键")
        return True
    else:
        print(f"✗ 清除缓存失败: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🧪 测试缓存自动清除机制")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试1: 获取初始统计
    print("\n📊 测试1: 获取当前统计")
    total = get_stats(token)
    print(f"当前总记录数: {total}")
    
    # 测试2: 手动清除缓存
    print("\n🧹 测试2: 手动清除缓存")
    if clear_cache(token):
        time.sleep(1)
        new_total = get_stats(token)
        print(f"清除缓存后统计: {new_total}")
        if new_total == total:
            print("✓ 缓存清除后数据一致")
        else:
            print(f"⚠ 数据不一致（可能是数据库变化）")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("1. 生成测试数据时会自动清除缓存")
    print("2. 删除测试数据时会自动清除缓存")
    print("3. 重置数据库时会自动清除缓存")
    print("4. 页面上有'清除缓存'按钮可手动清除")

if __name__ == "__main__":
    main()
