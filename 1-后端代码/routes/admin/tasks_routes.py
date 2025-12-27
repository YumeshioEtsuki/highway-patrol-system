# routes/tasks.py

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
from celery.result import AsyncResult
from celery_app import celery_app
from core.logger import setup_logger
from core.deps import get_current_user, get_current_admin_qs, CurrentUser
from workers.photo.tasks import compress_photo
from workers.ai.tasks import check_photo_quality
from workers.report.tasks import export_large_excel, generate_monthly_report
from workers.maintenance.tasks import cleanup_expired_cache

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# 请求模型
class CompressPhotoRequest(BaseModel):
    photo_id: str = Field(..., description="照片ID")
    quality: int = Field(85, ge=1, le=100, description="压缩质量")

class QualityCheckRequest(BaseModel):
    photo_id: str = Field(..., description="照片ID")
    threshold: Optional[float] = Field(0.7, description="质量阈值 0-1")


@router.post("/photo/compress", summary="提交照片压缩任务")
async def submit_compress_photo(
    req: CompressPhotoRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    提交照片压缩异步任务
    
    - **photo_id**: 照片ID（整数或UUID）
    - **quality**: 压缩质量（1-100）
    """
    try:
        # 提交任务（Celery worker 会处理 photo_id 到路径的映射）
        task = compress_photo.delay(req.photo_id, req.quality)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "照片压缩任务已提交"
        }
    except Exception as e:
        logger.error(f"提交压缩任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/photo/quality-check", summary="提交照片质量检查任务")
async def submit_quality_check(
    req: QualityCheckRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    提交 AI 照片质量检查异步任务
    
    - **photo_id**: 照片ID（整数或UUID）
    - **threshold**: 质量阈值（0-1）
    """
    try:
        task = check_photo_quality.delay(req.photo_id, req.threshold)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "AI 质量检查任务已提交"
        }
    except Exception as e:
        logger.error(f"提交质量检查任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/report/export-excel", summary="提交大型 Excel 导出任务")
async def submit_export_excel(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    提交大型 Excel 导出异步任务（管理员权限）
    
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **status_filter**: 状态筛选
    """
    try:
        task = export_large_excel.delay(start_date, end_date, status_filter)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "Excel 导出任务已提交"
        }
    except Exception as e:
        logger.error(f"提交导出任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/report/monthly", summary="生成月度报告")
async def submit_monthly_report(
    year: int,
    month: int = Query(..., ge=1, le=12),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    生成月度报告（管理员权限）
    
    - **year**: 年份
    - **month**: 月份（1-12）
    """
    try:
        task = generate_monthly_report.delay(year, month)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": f"{year}年{month}月报告生成任务已提交"
        }
    except Exception as e:
        logger.error(f"提交月报任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.get("/status/{task_id}", summary="查询任务状态")
async def get_task_status(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    查询任务执行状态
    
    - **task_id**: 任务 ID
    """
    try:
        # 获取任务结果
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.state,
        }
        
        # 根据状态返回不同信息
        if task_result.state == "PENDING":
            response["message"] = "任务等待执行"
        elif task_result.state == "STARTED":
            response["message"] = "任务正在执行"
        elif task_result.state == "SUCCESS":
            response["message"] = "任务执行成功"
            response["result"] = task_result.result
        elif task_result.state == "FAILURE":
            response["message"] = "任务执行失败"
            response["error"] = str(task_result.info)
        elif task_result.state == "RETRY":
            response["message"] = "任务正在重试"
        
        return response
    
    except Exception as e:
        logger.error(f"查询任务状态失败 {task_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.post("/maintenance/cleanup-cache", summary="手动清理缓存")
async def trigger_cleanup_cache(
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    手动触发缓存清理任务（管理员权限）
    """
    try:
        task = cleanup_expired_cache.delay()
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "PENDING",
            "message": "缓存清理任务已提交"
        }
    except Exception as e:
        logger.error(f"提交清理任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务提交失败: {str(e)}"
        )


@router.get("/stats", summary="任务队列统计")
async def get_task_stats(
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    获取任务队列统计信息（管理员权限）
    """
    try:
        # 获取 Celery 统计信息
        inspect = celery_app.control.inspect()
        
        # 活跃任务
        active_tasks = inspect.active()
        
        # 保留任务
        reserved_tasks = inspect.reserved()
        
        # 统计
        active_count = sum(len(tasks) for tasks in (active_tasks or {}).values())
        reserved_count = sum(len(tasks) for tasks in (reserved_tasks or {}).values())
        
        return {
            "success": True,
            "active_tasks": active_count,
            "reserved_tasks": reserved_count,
            "workers": list((active_tasks or {}).keys()),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"获取任务统计失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )
