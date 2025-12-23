"""
Celery 任务模块

包含：
- photo_tasks: 照片处理任务
- ai_tasks: AI 质量检查任务
- report_tasks: 报告导出任务
- maintenance_tasks: 系统维护任务
"""

from .photo_tasks import compress_photo, process_batch_photos
from .ai_tasks import check_photo_quality, analyze_patrol_record
from .report_tasks import export_large_excel, generate_monthly_report
from .maintenance_tasks import cleanup_expired_cache, health_check

__all__ = [
    "compress_photo",
    "process_batch_photos",
    "check_photo_quality",
    "analyze_patrol_record",
    "export_large_excel",
    "generate_monthly_report",
    "cleanup_expired_cache",
    "health_check",
]
