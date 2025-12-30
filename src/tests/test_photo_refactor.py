"""
任务中心照片安全重构测试脚本

测试新增的照片管理API和任务提交功能
"""

import requests
import json
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # 替换为实际token

headers = {
    "Authorization": f"Bearer {TOKEN}"
}


def test_photo_upload():
    """测试照片上传"""
    print("\n=== 测试照片上传 ===")
    
    # 创建测试照片文件（如果不存在）
    test_photo = Path("test_photo.jpg")
    if not test_photo.exists():
        print("⚠️  请准备一个测试照片文件: test_photo.jpg")
        return None
    
    with open(test_photo, "rb") as f:
        files = {"file": ("test_photo.jpg", f, "image/jpeg")}
        response = requests.post(
            f"{BASE_URL}/api/photos/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 上传成功: photo_id={data['photo_id']}")
        print(f"   文件名: {data['filename']}")
        print(f"   大小: {data['size_bytes']} bytes")
        return data['photo_id']
    else:
        print(f"❌ 上传失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None


def test_get_user_photos():
    """测试获取用户照片列表"""
    print("\n=== 测试获取照片列表 ===")
    
    response = requests.get(
        f"{BASE_URL}/api/photos/user",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取成功: 共 {data['total']} 张照片")
        for i, photo in enumerate(data['data'][:5], 1):
            print(f"   {i}. {photo['filename']} (ID: {photo['id']})")
        return data['data']
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return []


def test_compress_photo(photo_id):
    """测试压缩照片任务"""
    print("\n=== 测试压缩照片任务 ===")
    
    payload = {
        "photo_id": photo_id,
        "quality": 85
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tasks/photo/compress",
        headers={**headers, "Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 任务提交成功: task_id={data['task_id']}")
        print(f"   消息: {data['message']}")
        return data['task_id']
    else:
        print(f"❌ 任务提交失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None


def test_generate_thumbnail(photo_id):
    """测试生成缩略图任务"""
    print("\n=== 测试生成缩略图任务 ===")
    
    payload = {
        "photo_id": photo_id,
        "width": 200,
        "height": 200
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tasks/photo/thumbnail",
        headers={**headers, "Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 任务提交成功: task_id={data['task_id']}")
        return data['task_id']
    else:
        print(f"❌ 任务提交失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None


def test_ai_quality_check(photo_id):
    """测试AI质量检测任务"""
    print("\n=== 测试AI质量检测任务 ===")
    
    payload = {
        "photo_id": photo_id,
        "threshold": 0.7
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tasks/ai/check-quality",
        headers={**headers, "Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 任务提交成功: task_id={data['task_id']}")
        return data['task_id']
    else:
        print(f"❌ 任务提交失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return None


def test_old_api_rejection():
    """测试旧API（使用photo_path）是否被拒绝"""
    print("\n=== 测试旧API拒绝机制 ===")
    
    # 尝试使用旧的 photo_path 参数
    payload = {
        "photo_path": "/path/to/photo.jpg",
        "quality": 85
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tasks/photo/compress",
        headers={**headers, "Content-Type": "application/json"},
        json=payload
    )
    
    # 应该返回 422 (Validation Error)
    if response.status_code == 422:
        print("✅ 正确拒绝了包含 photo_path 的请求")
        print(f"   错误信息: {response.json()['detail']}")
    else:
        print(f"⚠️  未按预期拒绝: status={response.status_code}")


def test_task_list():
    """测试任务列表查询"""
    print("\n=== 测试任务列表查询 ===")
    
    response = requests.get(
        f"{BASE_URL}/api/tasks/list?limit=10",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取成功: 共 {len(data.get('tasks', []))} 个任务")
        for task in data.get('tasks', [])[:3]:
            print(f"   - {task.get('task_id')}: {task.get('state')}")
    else:
        print(f"❌ 获取失败: {response.status_code}")


def main():
    """主测试流程"""
    print("=" * 60)
    print("任务中心照片安全重构 - 功能测试")
    print("=" * 60)
    
    # 检查token
    if TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("\n❌ 请先设置有效的 ACCESS_TOKEN")
        print("   1. 登录系统获取 token")
        print("   2. 修改脚本中的 TOKEN 变量")
        return
    
    # 1. 测试照片列表
    photos = test_get_user_photos()
    
    # 2. 测试照片上传
    photo_id = test_photo_upload()
    
    # 如果上传失败，尝试使用已有照片
    if not photo_id and photos:
        photo_id = photos[0]['id']
        print(f"\n使用已有照片进行测试: {photo_id}")
    
    if not photo_id:
        print("\n❌ 无可用照片，测试终止")
        return
    
    # 3. 测试各类任务
    test_compress_photo(photo_id)
    test_generate_thumbnail(photo_id)
    test_ai_quality_check(photo_id)
    
    # 4. 测试安全机制
    test_old_api_rejection()
    
    # 5. 查看任务列表
    test_task_list()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 检查 Celery Worker 日志确认任务执行")
    print("2. 访问 http://localhost:8000/tasks.html 查看UI")
    print("3. 查看任务列表中的任务状态")


if __name__ == "__main__":
    main()
