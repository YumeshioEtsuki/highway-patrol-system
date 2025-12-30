"""
报表 API 路由（Phase 2 Stage 2）
- 模板管理
- 报表异步生成
- 下载与订阅
"""
import os
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from core.deps import get_current_user, get_current_admin, CurrentUser
import services.report_service as report_service
from models.report import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportGenerateRequest,
    SubscriptionCreate,
)
from workers.report.tasks import generate_report_async
from services.report_generator import EXPORT_DIR

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ============ 模板管理 ============


@router.get("/templates", summary="报表模板列表")
async def list_templates(
    type: Optional[str] = Query(None, description="模板类型"),
    enabled: Optional[bool] = Query(True, description="是否启用"),
    admin: CurrentUser = Depends(get_current_admin)
):
    templates = await report_service.list_templates(type=type, enabled=enabled)
    return {"success": True, "items": templates}


@router.get("/templates/{template_id}", summary="获取报表模板")
async def get_template_detail(
    template_id: int,
    admin: CurrentUser = Depends(get_current_admin)
):
    tpl = await report_service.get_template(template_id)
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    return {"success": True, "data": tpl}


@router.post("/templates", status_code=status.HTTP_201_CREATED, summary="创建报表模板")
async def create_template(
    payload: ReportTemplateCreate,
    admin: CurrentUser = Depends(get_current_admin)
):
    template_id = await report_service.create_template(
        name=payload.name,
        type=payload.type.value,
        config=payload.config or {},
        chart_config=payload.chart_config or {},
        created_by=admin.user_id
    )
    return {"success": True, "id": template_id}


@router.patch("/templates/{template_id}", summary="更新报表模板")
async def update_template(
    template_id: int,
    payload: ReportTemplateUpdate,
    admin: CurrentUser = Depends(get_current_admin)
):
    updated = await report_service.update_template(
        template_id=template_id,
        name=payload.name,
        config=payload.config,
        sql_template=payload.sql_template,
        chart_config=payload.chart_config,
        enabled=payload.enabled,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到或无更新字段")
    return {"success": True, "id": template_id}


# ============ 报表生成与历史 ============


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED, summary="提交报表生成任务")
async def generate_report(
    payload: ReportGenerateRequest,
    admin: CurrentUser = Depends(get_current_admin)
):
    try:
        record_id = await report_service.create_generation_record(
            template_id=payload.template_id,
            generated_by=admin.user_id,
            time_range_start=payload.time_range_start,
            time_range_end=payload.time_range_end,
            file_type=payload.file_type.value
        )
        await report_service.update_generation_status(record_id, status="generating")
        task = generate_report_async.apply_async(
            args=[
                record_id,
                payload.template_id,
                str(payload.time_range_start),
                str(payload.time_range_end),
                payload.file_type.value,
                payload.filters or {},
            ]
        )
        return {"success": True, "record_id": record_id, "task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"生成任务提交失败: {e}")


@router.get("/history", summary="报表生成历史")
async def list_report_history(
    template_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: CurrentUser = Depends(get_current_admin)
):
    items, total = await report_service.list_reports(
        template_id=template_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return {"success": True, "total": total, "items": items}


@router.get("/stats", summary="报表统计摘要")
async def report_stats(admin: CurrentUser = Depends(get_current_admin)):
    stats = await report_service.get_report_stats()
    return {"success": True, "data": stats}


@router.get("/metrics", summary="可用指标列表")
async def report_metrics(admin: CurrentUser = Depends(get_current_admin)):
    metrics = await report_service.get_metrics()
    return {"success": True, "items": metrics}


# ============ 下载 ============


@router.get("/download", response_class=FileResponse, summary="下载报表文件")
async def download_report(path: str = Query(..., description="文件名"), current_user: CurrentUser = Depends(get_current_user)):
    filename = os.path.basename(path)
    full_path = os.path.abspath(os.path.join(EXPORT_DIR, filename))
    if not full_path.startswith(EXPORT_DIR):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法路径")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return FileResponse(full_path, filename=filename)


# ============ 订阅 ============


@router.post("/subscriptions", status_code=status.HTTP_201_CREATED, summary="创建报表订阅")
async def create_subscription(
    payload: SubscriptionCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    sub_id = await report_service.create_subscription(
        template_id=payload.template_id,
        subscriber_id=current_user.user_id,
        frequency=payload.frequency.value,
        send_time=payload.send_time.strftime("%H:%M:%S"),
        send_day=payload.send_day,
        delivery_method=payload.delivery_method.value,
        delivery_target=payload.delivery_target,
    )
    return {"success": True, "id": sub_id}


@router.get("/subscriptions/me", summary="我的报表订阅")
async def my_subscriptions(current_user: CurrentUser = Depends(get_current_user)):
    items = await report_service.list_user_subscriptions(current_user.user_id)
    return {"success": True, "items": items}


@router.delete("/subscriptions/{subscription_id}", summary="删除订阅")
async def delete_subscription(subscription_id: int, current_user: CurrentUser = Depends(get_current_user)):
    deleted = await report_service.delete_subscription(subscription_id, current_user.user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订阅不存在或无权限")
    return {"success": True}
