#!/usr/bin/env python3
"""
测试前端发送的请求是否符合后端 Pydantic 模型
"""
import sys
sys.path.insert(0, r'd:\MySQL Project\highway-patrol-system\1-后端代码')

from pydantic import ValidationError
from routes.tasks.routes import CompressPhotoRequest, GenerateMonthlyReportRequest

print("=" * 60)
print("Pydantic 模型验证测试")
print("=" * 60)

# 测试 1: 压缩照片请求
print("\n[1] CompressPhotoRequest 验证")
print("模型定义: photo_id: str, quality: int (ge=1, le=100)")

test_cases = [
    {"photo_id": "1", "quality": 85},
    {"photo_id": 1, "quality": 85},
    {"photo_id": "1", "quality": "85"},
    {"photo_id": "auto_1.jpg", "quality": 85},
]

for i, data in enumerate(test_cases):
    try:
        req = CompressPhotoRequest(**data)
        print(f"  ✓ 测试 {i+1}: {data} → 验证通过")
        print(f"    photo_id={req.photo_id} (type: {type(req.photo_id).__name__})")
        print(f"    quality={req.quality} (type: {type(req.quality).__name__})")
    except ValidationError as e:
        print(f"  ✗ 测试 {i+1}: {data}")
        for err in e.errors():
            print(f"    字段: {err['loc']}, 错误: {err['msg']}")

# 测试 2: 月报请求
print("\n[2] GenerateMonthlyReportRequest 验证")
print("模型定义: year: int, month: int (ge=1, le=12)")

test_cases_2 = [
    {"year": 2025, "month": 12},
    {"year": "2025", "month": "12"},
    {"year": 2025, "month": 12.0},
    {"year": 2030, "month": 1},
]

for i, data in enumerate(test_cases_2):
    try:
        req = GenerateMonthlyReportRequest(**data)
        print(f"  ✓ 测试 {i+1}: {data} → 验证通过")
        print(f"    year={req.year} (type: {type(req.year).__name__})")
        print(f"    month={req.month} (type: {type(req.month).__name__})")
    except ValidationError as e:
        print(f"  ✗ 测试 {i+1}: {data}")
        for err in e.errors():
            print(f"    字段: {err['loc']}, 错误: {err['msg']}")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)
