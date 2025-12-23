"""
Celery 应用配置和初始化

用于异步任务处理：
- 照片压缩和处理
- AI 质量检查（Ollama）
- 大型报告导出
- 定期清理任务
"""

from celery import Celery
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# 创建 Celery 应用实例
celery_app = Celery(
    "highway_patrol",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.photo_tasks",      # 照片处理任务
        "tasks.ai_tasks",         # AI 质量检查任务
        "tasks.report_tasks",     # 报告导出任务
        "tasks.maintenance_tasks" # 维护任务
    ]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],
    
    # 时区
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    
    # 任务结果
    result_expires=3600,  # 结果保留 1 小时
    result_persistent=True,
    
    # 任务执行
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    
    # 重试策略
    task_default_max_retries=3,
    task_default_retry_delay=60,  # 60 秒后重试
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    worker_disable_rate_limits=False,
    
    # 任务路由（不同队列）
    task_routes={
        "tasks.photo_tasks.*": {"queue": "photo"},
        "tasks.ai_tasks.*": {"queue": "ai"},
        "tasks.report_tasks.*": {"queue": "report"},
        "tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },
    
    # 任务优先级
    task_queue_max_priority=10,
    task_default_priority=5,
)

# 定期任务配置（Celery Beat）
celery_app.conf.beat_schedule = {
    # 每天凌晨 3 点清理过期缓存
    "cleanup-expired-cache": {
        "task": "tasks.maintenance_tasks.cleanup_expired_cache",
        "schedule": 3600.0 * 24,  # 24 小时
        "options": {"queue": "maintenance"}
    },
    
    # 每小时检查任务健康状态
    "health-check": {
        "task": "tasks.maintenance_tasks.health_check",
        "schedule": 3600.0,  # 1 小时
        "options": {"queue": "maintenance"}
    },
    
    # 每分钟收集一次性能指标
    "collect-performance-metrics": {
        "task": "tasks.maintenance_tasks.collect_performance_metrics",
        "schedule": 60.0,  # 1 分钟
        "options": {"queue": "maintenance"}
    },
    
    # 每 6 小时生成一次优化建议
    "generate-optimization-recommendations": {
        "task": "tasks.maintenance_tasks.generate_optimization_recommendations",
        "schedule": 3600.0 * 6,  # 6 小时
        "options": {"queue": "maintenance"}
    },
}

logger.info("Celery 应用初始化成功")
logger.info(f"Broker: {settings.CELERY_BROKER_URL}")
logger.info(f"Backend: {settings.CELERY_RESULT_BACKEND}")
