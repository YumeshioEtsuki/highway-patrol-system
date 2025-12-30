#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试照片压缩任务，验证修复是否有效
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from celery_app import celery_app
from workers.photo.tasks import compress_photo

def test_compress_photo_task():
    """测试压缩照片任务"""
    
    print("=" * 60)
    print("测试照片压缩任务")
    print("=" * 60)
    
    # 提交任务
    print("\n1. 提交压缩照片任务 (photo_id=1, quality=85)...")
    task = compress_photo.apply_async(args=["1", 85])
    task_id = task.id
    print(f"   [OK] 任务已提交，task_id: {task_id}")
    
    # 等待任务执行
    print("\n2. 等待任务执行 (最多 30 秒)...")
    try:
        # 使用轮询检查任务状态
        for i in range(30):
            task_state = celery_app.AsyncResult(task_id)
            print(f"   [{i+1}s] 任务状态: {task_state.state}")
            
            if task_state.ready():
                print(f"\n3. 任务执行完成 (状态: {task_state.state})")
                
                if task_state.state == "SUCCESS":
                    result = task_state.result
                    print(f"   [OK] 成功!")
                    print(f"   返回值: {result}")
                    return True
                else:
                    print(f"   [ERROR] 任务失败")
                    print(f"   错误: {task_state.info}")
                    return False
            
            time.sleep(1)
        
        print(f"\n[ERROR] 任务超时（30秒）")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_compress_photo_task()
    sys.exit(0 if success else 1)
