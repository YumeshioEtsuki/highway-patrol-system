"""
系统维护异步任务

功能：
- 清理过期缓存
- 健康检查
- 数据库清理
- 性能指标收集
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from celery_app import celery_app
from core.logger import setup_logger
from utils.redis_client import get_redis_client

logger = setup_logger(__name__)


@celery_app.task(name="tasks.maintenance_tasks.cleanup_expired_cache")
def cleanup_expired_cache() -> Dict[str, Any]:
    """
    清理过期缓存
    
    返回：
        {
            "success": bool,
            "cleaned_keys": int
        }
    """
    try:
        logger.info("开始清理过期缓存")
        
        client = get_redis_client()
        if not client:
            return {
                "success": False,
                "error": "Redis 不可用"
            }
        
        # 获取所有键
        all_keys = client.keys("*")
        cleaned = 0
        
        for key in all_keys:
            ttl = client.ttl(key)
            # TTL < 0 表示已过期或没有过期时间
            if ttl < 0:
                client.delete(key)
                cleaned += 1
        
        logger.info(f"缓存清理完成: 清理了 {cleaned} 个过期键")
        
        return {
            "success": True,
            "cleaned_keys": cleaned
        }
    
    except Exception as e:
        logger.error(f"缓存清理失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="tasks.maintenance_tasks.health_check")
def health_check() -> Dict[str, Any]:
    """
    系统健康检查
    
    返回：
        {
            "success": bool,
            "redis_status": str,
            "celery_status": str,
            "timestamp": str
        }
    """
    try:
        logger.info("开始系统健康检查")
        
        # 检查 Redis
        redis_status = "OK"
        try:
            client = get_redis_client()
            if client:
                client.ping()
            else:
                redis_status = "UNAVAILABLE"
        except Exception as e:
            redis_status = f"ERROR: {e}"
        
        # 检查 Celery（如果能执行这个任务，说明 Celery 正常）
        celery_status = "OK"
        
        logger.info(f"健康检查完成: Redis={redis_status}, Celery={celery_status}")
        
        return {
            "success": True,
            "redis_status": redis_status,
            "celery_status": celery_status,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name="tasks.maintenance_tasks.cleanup_old_photos")
def cleanup_old_photos(days: int = 90) -> Dict[str, Any]:
    """
    清理旧照片文件（超过指定天数）
    
    参数：
        days: 保留天数（默认 90 天）
    
    返回：
        {
            "success": bool,
            "deleted_count": int,
            "freed_space": int
        }
    """
    try:
        import os
        from settings import settings
        
        logger.info(f"开始清理 {days} 天前的旧照片")
        
        photo_dir = settings.UPLOAD_FOLDER
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        freed_space = 0
        
        for filename in os.listdir(photo_dir):
            file_path = os.path.join(photo_dir, filename)
            
            # 检查文件修改时间
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_date:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_count += 1
                    freed_space += file_size
        
        logger.info(f"旧照片清理完成: 删除 {deleted_count} 个文件, 释放 {freed_space} 字节")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "freed_space": freed_space
        }
    
    except Exception as e:
        logger.error(f"旧照片清理失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="tasks.maintenance_tasks.collect_performance_metrics")
def collect_performance_metrics() -> Dict[str, Any]:
    """
    收集性能指标（由 Celery Beat 定时执行）
    
    返回：
        {
            "success": bool,
            "metrics": dict
        }
    """
    try:
        logger.info("开始收集性能指标")
        
        # 收集基础系统指标
        import psutil
        import os
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids()),
        }
        
        # 检查 Redis 状态
        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_info = redis_client.info("stats")
                metrics["redis_connected_clients"] = redis_info.get("connected_clients", 0)
                metrics["redis_used_memory_mb"] = redis_info.get("used_memory", 0) / (1024 * 1024)
            except Exception as e:
                logger.warning(f"无法获取 Redis 指标: {e}")
        
        logger.info(f"性能指标收集成功: {metrics}")
        return {
            "success": True,
            "metrics": metrics
        }
    
    except ImportError:
        logger.warning("psutil 未安装，无法收集系统指标")
        return {
            "success": True,
            "metrics": {
                "timestamp": datetime.now().isoformat(),
                "message": "psutil 未安装，无法收集详细指标"
            }
        }
    except Exception as e:
        logger.error(f"性能指标收集失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="tasks.maintenance_tasks.generate_optimization_recommendations")
def generate_optimization_recommendations() -> Dict[str, Any]:
    """
    生成优化建议（由 Celery Beat 定时执行）
    
    返回：
        {
            "success": bool,
            "recommendations_count": int
        }
    """
    try:
        from utils.optimization_advisor import OptimizationAdvisor
        
        logger.info("开始生成优化建议")
        
        recommendations = OptimizationAdvisor.generate_recommendations()
        
        saved_count = 0
        for rec in recommendations:
            if OptimizationAdvisor.save_recommendation(rec):
                saved_count += 1
        
        logger.info(f"优化建议生成完成: {saved_count} 条已保存")
        
        return {
            "success": True,
            "recommendations_count": saved_count
        }
    
    except Exception as e:
        logger.error(f"优化建议生成失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

