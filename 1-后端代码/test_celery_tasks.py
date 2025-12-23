#!/usr/bin/env python3
"""
Celery 任务队列测试脚本

测试内容：
1. Celery 连接验证
2. 照片压缩任务
3. AI 质量检查任务
4. 报告导出任务
5. 任务状态查询
"""

import time
import os
from celery_app import celery_app
from tasks import compress_photo, check_photo_quality, export_large_excel


def test_celery_connection():
    """测试 Celery 连接"""
    print("\n" + "="*60)
    print("部分 1: Celery 连接测试")
    print("="*60)
    
    try:
        # 检查 Celery 配置
        print(f"[→] Broker: {celery_app.conf.broker_url}")
        print(f"[→] Backend: {celery_app.conf.result_backend}")
        
        # 检查 Worker 是否在线
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            print(f"[✓] 发现 {len(active_workers)} 个活跃 Worker:")
            for worker_name in active_workers.keys():
                print(f"   - {worker_name}")
            return True
        else:
            print("[✗] 没有发现活跃 Worker")
            print("   请先启动 Celery Worker:")
            print("   celery -A celery_app worker --loglevel=info --pool=solo")
            return False
    
    except Exception as e:
        print(f"[✗] 连接测试失败: {e}")
        return False


def test_photo_compression():
    """测试照片压缩任务"""
    print("\n" + "="*60)
    print("部分 2: 照片压缩任务测试")
    print("="*60)
    
    try:
        # 创建测试照片
        test_photo_dir = "photos"
        os.makedirs(test_photo_dir, exist_ok=True)
        test_photo_path = os.path.join(test_photo_dir, "test_image.jpg")
        
        # 如果测试照片不存在，跳过测试
        if not os.path.exists(test_photo_path):
            print("[!] 测试照片不存在，跳过压缩测试")
            print(f"   请在 {test_photo_path} 放置一张测试照片")
            return False
        
        print(f"[→] 提交照片压缩任务: {test_photo_path}")
        
        # 提交异步任务
        task = compress_photo.delay(test_photo_path, quality=85)
        print(f"[✓] 任务已提交，ID: {task.id}")
        
        # 等待任务完成
        print("[→] 等待任务完成...")
        result = task.get(timeout=60)
        
        if result.get("success"):
            print(f"[✓] 压缩成功:")
            print(f"   原始大小: {result['original_size']} 字节")
            print(f"   压缩大小: {result['compressed_size']} 字节")
            print(f"   减少: {result['reduction_percent']}%")
            print(f"   输出: {result['output_path']}")
            return True
        else:
            print(f"[✗] 压缩失败: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"[✗] 压缩测试失败: {e}")
        return False


def test_quality_check():
    """测试 AI 质量检查任务"""
    print("\n" + "="*60)
    print("部分 3: AI 质量检查任务测试")
    print("="*60)
    
    try:
        test_photo_path = os.path.join("photos", "test_image.jpg")
        
        if not os.path.exists(test_photo_path):
            print("[!] 测试照片不存在，跳过 AI 测试")
            return False
        
        print(f"[→] 提交 AI 质量检查任务: {test_photo_path}")
        
        # 提交任务
        task = check_photo_quality.delay(test_photo_path)
        print(f"[✓] 任务已提交，ID: {task.id}")
        
        # 等待任务完成（AI 任务可能较慢）
        print("[→] 等待 AI 分析...")
        result = task.get(timeout=120)
        
        if result.get("success"):
            print(f"[✓] AI 分析成功:")
            print(f"   质量评分: {result.get('quality_score', 'N/A')}/10")
            print(f"   清晰度: {'清晰' if result.get('is_clear') else '模糊'}")
            issues = result.get("issues", [])
            if issues:
                print(f"   问题: {', '.join(issues)}")
            suggestions = result.get("suggestions", "无")
            print(f"   建议: {suggestions}")
            return True
        else:
            print(f"[!] AI 分析失败: {result.get('error')}")
            print("   这可能是因为 Ollama 未运行或模型未加载")
            return False
    
    except Exception as e:
        print(f"[✗] AI 测试失败: {e}")
        return False


def test_report_export():
    """测试报告导出任务"""
    print("\n" + "="*60)
    print("部分 4: 报告导出任务测试")
    print("="*60)
    
    try:
        print("[→] 提交 Excel 导出任务")
        
        # 提交任务（导出最近 7 天的数据）
        task = export_large_excel.delay(
            start_date=None,
            end_date=None,
            status_filter=None
        )
        print(f"[✓] 任务已提交，ID: {task.id}")
        
        # 等待任务完成
        print("[→] 等待导出完成...")
        result = task.get(timeout=180)
        
        if result.get("success"):
            print(f"[✓] 导出成功:")
            print(f"   文件路径: {result['file_path']}")
            print(f"   记录数: {result['records_count']}")
            print(f"   文件大小: {result['file_size']} 字节")
            return True
        else:
            print(f"[✗] 导出失败: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"[✗] 导出测试失败: {e}")
        return False


def test_task_status_query():
    """测试任务状态查询"""
    print("\n" + "="*60)
    print("部分 5: 任务状态查询测试")
    print("="*60)
    
    try:
        # 提交一个简单任务
        from tasks.maintenance_tasks import health_check
        
        print("[→] 提交健康检查任务")
        task = health_check.delay()
        print(f"[✓] 任务已提交，ID: {task.id}")
        
        # 查询任务状态
        print("[→] 查询任务状态...")
        
        for i in range(5):
            status = task.state
            print(f"   [{i+1}/5] 状态: {status}")
            
            if status == "SUCCESS":
                result = task.result
                print(f"[✓] 任务完成:")
                print(f"   结果: {result}")
                return True
            elif status == "FAILURE":
                print(f"[✗] 任务失败: {task.info}")
                return False
            
            time.sleep(1)
        
        print("[!] 任务仍在执行中")
        return True
    
    except Exception as e:
        print(f"[✗] 状态查询测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "█"*60)
    print("  Celery 任务队列测试")
    print("█"*60)
    
    results = {
        "Celery 连接": test_celery_connection(),
    }
    
    # 只有连接成功才继续测试
    if results["Celery 连接"]:
        results["照片压缩"] = test_photo_compression()
        results["AI 质量检查"] = test_quality_check()
        results["报告导出"] = test_report_export()
        results["任务状态查询"] = test_task_status_query()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:.<30} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ 所有测试通过！Celery 任务队列正常工作")
    else:
        print("✗ 部分测试未通过")
        print("\n故障排查建议:")
        
        if not results.get("Celery 连接"):
            print("  1. 启动 Redis: docker run -d -p 6379:6379 redis:latest")
            print("  2. 启动 Celery Worker:")
            print("     celery -A celery_app worker --loglevel=info --pool=solo")
        
        if not results.get("AI 质量检查"):
            print("  3. 启动 Ollama 服务:")
            print("     ollama serve")
            print("  4. 拉取模型:")
            print("     ollama pull qwen:7b")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
