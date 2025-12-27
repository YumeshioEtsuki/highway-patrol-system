"""
异步任务管理路由

功能：
- 触发各类 Celery 异步任务
- 查询任务状态和结果
- 任务列表管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from celery.result import AsyncResult
from celery_app import celery_app
from core.deps import get_current_user, get_current_admin, CurrentUser
from core.logger import setup_logger

# 导入各类任务
from workers.photo.tasks import compress_photo, generate_thumbnail, process_batch_photos
from workers.ai.tasks import check_photo_quality, analyze_patrol_record
from workers.report.tasks import export_large_excel, generate_monthly_report
from workers.maintenance.tasks import cleanup_expired_cache, health_check, collect_performance_metrics

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ============ 请求模型 ============

class CompressPhotoRequest(BaseModel):
    photo_id: str = Field(..., description="照片ID")
    quality: int = Field(85, ge=1, le=100, description="压缩质量")


class GenerateThumbnailRequest(BaseModel):
    photo_id: str = Field(..., description="照片ID")
    width: int = Field(200, description="缩略图宽度")
    height: int = Field(200, description="缩略图高度")


class BatchPhotosRequest(BaseModel):
    photo_ids: List[str] = Field(..., description="照片ID列表")
    quality: int = Field(85, ge=1, le=100, description="压缩质量")


class CheckPhotoQualityRequest(BaseModel):
    photo_id: str = Field(..., description="照片ID")
    threshold: Optional[float] = Field(0.7, description="质量阈值 0-1")


class AnalyzeRecordRequest(BaseModel):
    record_id: int = Field(..., description="巡查记录ID")
    analysis_type: Optional[str] = Field("comprehensive", description="分析类型: comprehensive/risk/quality")


class ExportReportRequest(BaseModel):
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    status_filter: Optional[str] = Field(None, description="状态筛选")


class GenerateMonthlyReportRequest(BaseModel):
    year: int = Field(..., description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")


# ============ 照片处理任务 ============

@router.post("/photo/compress", summary="压缩照片")
async def compress_photo_task(
    req: CompressPhotoRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """触发照片压缩任务（使用安全的 photo_id）"""
    try:
        # 安全验证：确保使用 photo_id 而非 photo_path
        if not req.photo_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少 photo_id 参数"
            )
        
        task = compress_photo.delay(req.photo_id, req.quality)
        logger.info(f"用户 {current_user.username} 触发照片压缩任务: {task.id}, photo_id: {req.photo_id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "照片压缩任务已提交"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发照片压缩任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/photo/thumbnail", summary="生成缩略图")
async def generate_thumbnail_task(
    req: GenerateThumbnailRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """触发生成缩略图任务（使用安全的 photo_id）"""
    try:
        if not req.photo_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少 photo_id 参数"
            )
        
        task = generate_thumbnail.delay(req.photo_id, (req.width, req.height))
        logger.info(f"用户 {current_user.username} 触发缩略图生成任务: {task.id}, photo_id: {req.photo_id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "缩略图生成任务已提交"
        }
    except Exception as e:
        logger.error(f"触发缩略图任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/photo/batch", summary="批量处理照片")
async def batch_process_photos_task(
    req: BatchPhotosRequest,
    current_user: CurrentUser = Depends(get_current_admin)
):
    """批量处理照片任务（管理员）"""
    try:
        if not req.photo_ids or len(req.photo_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少 photo_ids 参数"
            )
        
        task = process_batch_photos.delay(req.photo_ids, req.quality)
        logger.info(f"管理员 {current_user.username} 触发批量照片处理任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": f"批量处理任务已提交，共 {len(req.photo_ids)} 张照片"
        }
    except Exception as e:
        logger.error(f"触发批量照片任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


# ============ AI 分析任务 ============

@router.post("/ai/check-quality", summary="AI质量检测")
async def check_quality_task(
    req: CheckPhotoQualityRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """触发照片AI质量检测任务（使用安全的 photo_id）"""
    try:
        if not req.photo_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少 photo_id 参数"
            )
        
        task = check_photo_quality.delay(req.photo_id)
        logger.info(f"用户 {current_user.username} 触发AI质检任务: {task.id}, photo_id: {req.photo_id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "AI质量检测任务已提交"
        }
    except Exception as e:
        logger.error(f"触发AI质检任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/ai/analyze-record", summary="分析巡查记录")
async def analyze_record_task(
    req: AnalyzeRecordRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """触发巡查记录AI分析任务"""
    try:
        from utils.utils import get_db_connection
        
        logger.info(f"🔍 用户 {current_user.username} 请求分析记录 ID: {req.record_id}")
        
        # 从数据库获取记录详情
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询记录基本信息
        sql = """
            SELECT description, severity 
            FROM InspectionRecord 
            WHERE record_id = %s
        """
        logger.info(f"📊 执行SQL: {sql}, 参数: {req.record_id}")
        cursor.execute(sql, (req.record_id,))
        
        record = cursor.fetchone()
        logger.info(f"📝 查询结果: {record}")
        
        if not record:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"记录 {req.record_id} 不存在"
            )
        
        description = record[0] or "无描述"
        
        # 注意：巡查照片直接保存在文件系统，无需从 patrol_photos 查询
        # 当前简化实现：AI 分析仅基于文本描述，不处理照片
        photos = []
        
        cursor.close()
        conn.close()
        
        # 调用异步任务
        task = analyze_patrol_record.delay(req.record_id, description, photos)
        logger.info(f"用户 {current_user.username} 触发记录分析任务: {task.id}, 记录ID: {req.record_id}")
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"记录分析任务已提交，共 {len(photos)} 张照片"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发记录分析任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


# ============ 报表任务 ============

@router.post("/report/export", summary="导出报表")
async def export_report_task(
    req: ExportReportRequest,
    current_user: CurrentUser = Depends(get_current_admin)
):
    """触发报表导出任务（管理员）"""
    try:
        task = export_large_excel.delay(
            req.start_date,
            req.end_date,
            req.status_filter
        )
        logger.info(f"管理员 {current_user.username} 触发报表导出任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "报表导出任务已提交，完成后可下载"
        }
    except Exception as e:
        logger.error(f"触发报表导出任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/report/monthly", summary="生成月报")
async def generate_monthly_task(
    req: GenerateMonthlyReportRequest,
    current_user: CurrentUser = Depends(get_current_admin)
):
    """触发月报生成任务（管理员）"""
    try:
        logger.info(f"📊 收到月报请求: year={req.year}, month={req.month}, user={current_user.username}")
        task = generate_monthly_report.delay(req.year, req.month)
        logger.info(f"管理员 {current_user.username} 触发月报生成任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": f"{req.year}年{req.month}月报告生成任务已提交"
        }
    except Exception as e:
        logger.error(f"触发月报任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


# ============ 维护任务 ============

@router.post("/maintenance/cleanup-cache", summary="清理缓存")
async def cleanup_cache_task(
    current_user: CurrentUser = Depends(get_current_admin)
):
    """触发缓存清理任务（管理员）"""
    try:
        task = cleanup_expired_cache.delay()
        logger.info(f"管理员 {current_user.username} 触发缓存清理任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "缓存清理任务已提交"
        }
    except Exception as e:
        logger.error(f"触发缓存清理任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/maintenance/health-check", summary="健康检查")
async def health_check_task(
    current_user: CurrentUser = Depends(get_current_admin)
):
    """触发系统健康检查任务（管理员）"""
    try:
        task = health_check.delay()
        logger.info(f"管理员 {current_user.username} 触发健康检查任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "健康检查任务已提交"
        }
    except Exception as e:
        logger.error(f"触发健康检查任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/maintenance/collect-metrics", summary="收集性能指标")
async def collect_metrics_task(
    current_user: CurrentUser = Depends(get_current_admin)
):
    """触发性能指标收集任务（管理员）"""
    try:
        task = collect_performance_metrics.delay()
        logger.info(f"管理员 {current_user.username} 触发性能指标收集任务: {task.id}")
        return {
            "success": True,
            "task_id": task.id,
            "message": "性能指标收集任务已提交"
        }
    except Exception as e:
        logger.error(f"触发性能指标任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


# ============ 任务状态查询 ============

@router.get("/status/{task_id}", summary="查询任务状态")
async def get_task_status(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """查询任务执行状态和结果"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "state": result.state,
            "status": result.status,
        }
        
        if result.ready():
            if result.successful():
                response["result"] = result.result
                response["message"] = "任务执行成功"
            else:
                response["error"] = str(result.info)
                response["message"] = "任务执行失败"
        else:
            response["message"] = "任务执行中..."
        
        return response
    except Exception as e:
        logger.error(f"查询任务状态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get("/list", summary="任务列表")
async def list_tasks(
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取最近任务列表（从 Redis 获取任务状态）"""
    try:
        from utils.redis_client import get_redis_client
        
        all_tasks = []
        
        # 尝试从 Celery inspect 获取活跃任务
        try:
            inspect = celery_app.control.inspect(timeout=1.0)
            if inspect:
                active_tasks = inspect.active() or {}
                scheduled_tasks = inspect.scheduled() or {}
                
                # 合并活跃任务
                for worker, tasks in active_tasks.items():
                    for task in tasks[:limit]:
                        all_tasks.append({
                            "task_id": task.get("id"),
                            "name": task.get("name", "未知任务").split(".")[-1],
                            "state": "RUNNING",
                            "worker": worker,
                        })
                
                # 合并计划任务
                for worker, tasks in scheduled_tasks.items():
                    for task in tasks[:limit]:
                        all_tasks.append({
                            "task_id": task.get("id"),
                            "name": task.get("name", "未知任务").split(".")[-1],
                            "state": "SCHEDULED",
                            "worker": worker,
                        })
        except Exception as inspect_error:
            logger.warning(f"Celery inspect 失败: {inspect_error}")
        
        # 从 Redis 查询最近完成的任务
        redis_client = get_redis_client()
        if redis_client:
            try:
                # 查询 Celery 结果键（celery-taREDACTEDmeta-*）
                result_keys = redis_client.keys("celery-taREDACTEDmeta-*")
                for key in result_keys[:limit]:
                    task_id = key.decode() if isinstance(key, bytes) else key
                    task_id = task_id.replace("celery-taREDACTEDmeta-", "")
                    
                    result = redis_client.get(key)
                    if result:
                        import json
                        task_data = json.loads(result)
                        all_tasks.append({
                            "task_id": task_id,
                            "name": task_data.get("task_name", "未知任务").split(".")[-1] if task_data.get("task_name") else "未知任务",
                            "state": task_data.get("status", "PENDING"),
                            "result": task_data.get("result"),
                        })
            except Exception as redis_error:
                logger.warning(f"从 Redis 查询任务失败: {redis_error}")
        
        # 按时间排序并限制数量
        all_tasks = all_tasks[:limit]
        
        return {
            "success": True,
            "tasks": all_tasks,
            "total": len(all_tasks)
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}", exc_info=True)
        return {
            "success": False,
            "tasks": [],
            "error": str(e)
        }
