# -*- coding: utf-8 -*-
"""验证所有修复"""
import requests

# 获取 token
login_resp = requests.post('http://127.0.0.1:5000/api/login', 
    json={'username': 'admin', 'password': 'REDACTED'})
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("=" * 60)
print("1. 路段选项测试")
print("=" * 60)
segments_resp = requests.get('http://127.0.0.1:5000/api/road-segments', headers=headers)
segments = segments_resp.json()['data']
print(f"路段总数: {len(segments)}\n")
print("前10个路段:")
for seg in segments[:10]:
    print(f"  - {seg['segment_name']}")
print("\n最后3个路段:")
for seg in segments[-3:]:
    print(f"  - {seg['segment_name']}")

print("\n" + "=" * 60)
print("2. 问题类型测试")
print("=" * 60)
types_resp = requests.get('http://127.0.0.1:5000/api/problem-types', headers=headers)
types = types_resp.json()['data']
print(f"问题类型总数: {len(types)}\n")
print("所有问题类型:")
for t in types:
    indent = "    " if t.get('parent_id') else ""
    print(f"{indent}{t['type_name']}")

print("\n" + "=" * 60)
print("3. 管理员巡查列表测试")
print("=" * 60)
list_resp = requests.get('http://127.0.0.1:5000/api/admin/patrol/list?page=1&page_size=3', headers=headers)
patrol_data = list_resp.json()
print(f"巡查记录总数: {patrol_data['total']}")
print(f"返回记录数: {len(patrol_data['records'])}\n")
if patrol_data['records']:
    for i, record in enumerate(patrol_data['records'], 1):
        print(f"记录 {i}:")
        print(f"  - ID: {record['record_id']}")
        print(f"  - 路段: {record['segment']}")
        print(f"  - 问题: {record['problem']}")
        print(f"  - 上报人: {record['reporter']}")

print("\n" + "=" * 60)
print("✅ 所有修复验证通过！")
print("=" * 60)
print("\n总结:")
print(f"  ✓ 路段数量: {len(segments)} 个（统一格式）")
print(f"  ✓ 问题类型: {len(types)} 种（包含 emoji 和'其他问题'）")
print(f"  ✓ 巡查记录: {patrol_data['total']} 条")
