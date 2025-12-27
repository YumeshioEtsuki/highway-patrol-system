# routes/admin.py

from fastapi import APIRouter, HTTPException, Depends, Query, status, Request
from fastapi.responses import StreamingResponse
from typing import Optional
import io
from core.logger import setup_logger
from utils.cache import cache_response, invalidate_cache
from utils.redis_client import cache_delete_pattern

logger = setup_logger(__name__)

from services.patrol_service import (
    mark_record_as_processing,
    mark_record_as_completed,
    get_patrol_list_admin,
    get_admin_stats,
    export_patrol_records_to_excel,
    stream_verify_database,
    stream_get_database_status,
    stream_reinit_database_with_step,
    generate_fake_records,
    clean_test_data,
    insert_audit_log,
    get_audit_logs
)
from models.base import AdminCompleteRequest, ApiResponse
from utils.utils import reinit_database, verify_database, get_database_status
from core.deps import get_current_admin, get_current_admin_qs, CurrentUser
from core.exceptions import BusinessException
from core.rate_limit import limiter
from fastapi import Depends

router = APIRouter(prefix="/api", tags=["admin"])
@router.get("/admin/audit", summary="审计日志列表")
async def audit_list(
    action: Optional[str] = Query(None, description="操作类型"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键字（resource/details）"),
    page: Optional[int] = Query(1, ge=1, description="页码"),
    page_size: Optional[int] = Query(50, ge=1, le=200, description="单页条数"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """审计日志分页查询（管理员权限）"""
    try:
        return get_audit_logs(action=action, user_id=user_id, start_date=start_date, end_date=end_date,
                              keyword=keyword, page=page or 1, page_size=page_size or 50)
    except Exception as e:
        # 若数据库未初始化或审计表不存在，友好返回空数据而非 500
        msg = str(e).lower()
        if "doesn't exist" in msg and "audit" in msg:
            logger.warning("审计表不存在，返回空数据。请初始化数据库或取消 SKIP_DB_INIT 后重启。")
            return {"records": [], "total": 0, "page": page or 1, "page_size": page_size or 50}
        logger.error(f"审计日志查询失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="查询失败")


@router.get("/admin/audit/export", summary="审计日志导出（CSV）")
async def audit_export(
    action: Optional[str] = Query(None, description="操作类型"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键字（resource/details）"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """导出审计日志为 CSV（管理员权限）"""
    import csv
    from datetime import datetime
    
    try:
        # 获取所有符合条件的审计记录（不分页，最多 10000 条）
        result = get_audit_logs(
            action=action, user_id=user_id, start_date=start_date, end_date=end_date,
            keyword=keyword, page=1, page_size=10000
        )
        records = result.get('records', [])
        
        # 生成 CSV 内容
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '用户ID', '操作', '资源', '详情', '时间'])
        
        for rec in records:
            writer.writerow([
                rec.get('id', ''),
                rec.get('user_id', ''),
                rec.get('action', ''),
                rec.get('resource', ''),
                rec.get('details', ''),
                rec.get('timestamp', '')
            ])
        
        # 返回 CSV 文件
        csv_bytes = output.getvalue().encode('utf-8-sig')  # UTF-8 with BOM，支持 Excel 正确识别中文
        return StreamingResponse(
            iter([csv_bytes]),
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
    except Exception as e:
        msg = str(e).lower()
        if "doesn't exist" in msg and "audit" in msg:
            # 表不存在时导出仅含表头的空 CSV
            import csv
            from datetime import datetime
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', '用户ID', '操作', '资源', '详情', '时间'])
            csv_bytes = output.getvalue().encode('utf-8-sig')
            logger.warning("审计表不存在，导出空CSV。请初始化数据库或取消 SKIP_DB_INIT 后重启。")
            return StreamingResponse(
                iter([csv_bytes]),
                media_type='text/csv; charset=utf-8',
                headers={'Content-Disposition': f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
        logger.error(f"审计日志导出失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="导出失败")


# ========================
# 管理员业务接口
# ========================

@router.post("/patrol/{record_id}/process", response_model=ApiResponse, summary="标记记录为处理中")
async def api_mark_as_processing(
    record_id: int,
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    管理员标记巡查记录为"处理中"状态（需要管理员权限）
    
    - **record_id**: 记录ID
    """
    try:
        success = mark_record_as_processing(record_id)
        if not success:
            raise BusinessException(detail="记录不存在或状态不可变")
        insert_audit_log(admin.user_id, "mark_processing", f"record:{record_id}")
        # 清除相关缓存
        cache_delete_pattern("admin:patrol:list:*")
        cache_delete_pattern("admin:stats:*")
        return ApiResponse(success=True, message="已标记为处理中")
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败"
        )


@router.post("/patrol/{record_id}/complete", response_model=ApiResponse, summary="标记记录为已完成")
async def api_mark_as_completed(
    record_id: int,
    req: AdminCompleteRequest,
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    管理员标记巡查记录为"已完成"状态（需要管理员权限）
    
    - **record_id**: 记录ID
    - **remark**: 处理备注（必填）
    """
    try:
        success = mark_record_as_completed(record_id, process_note=req.remark)
        if not success:
            raise BusinessException(detail="记录未处于\"处理中\"状态")
        insert_audit_log(admin.user_id, "mark_completed", f"record:{record_id}")
        # 清除相关缓存
        cache_delete_pattern("admin:patrol:list:*")
        cache_delete_pattern("admin:stats:*")
        return ApiResponse(success=True, message="已标记为已完成")
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"完成失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败"
        )


@router.get("/admin/patrol/list", summary="管理员查询所有巡查记录")
# 注意：该接口包含复杂的筛选与分页，启用缓存可能导致“全部时间/无筛选”场景返回旧结果。
# 为避免前端看到过期数据，这里禁用装饰器级缓存。
async def api_patrol_list_admin(
    status_filter: Optional[str] = Query(None, description="状态筛选（pending/processing/completed）"),
    problem_type_id: Optional[int] = Query(None, description="问题类型ID"),
    severity: Optional[int] = Query(None, description="严重度"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词（描述/路段/问题类型）"),
    data_type: Optional[str] = Query(None, description="数据类型（real/test），不传则查询全部"),
    page: Optional[int] = Query(1, ge=1, description="页码，从1开始"),
    page_size: Optional[int] = Query(100, ge=1, le=200, description="每页条数，最大200"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    管理员查询所有巡查记录（需要管理员权限）
    
    - **status_filter**: 可选，按状态筛选（pending/processing/completed）
    - **problem_type_id**: 可选，按问题类型筛选
    - **severity**: 可选，按严重度筛选
    - **start_date/end_date**: 可选，按时间范围筛选
    - **keyword**: 可选，按描述/路段/问题类型模糊匹配
    """
    # 🔍 调试日志：打印接收到的所有参数
    logger.info(f"📥 [api_patrol_list_admin] 接收参数: status={status_filter}, problem_type={problem_type_id}, "
                f"severity={severity}, start_date={start_date}, end_date={end_date}, keyword={keyword}, "
                f"data_type={data_type}, page={page}, page_size={page_size}")
    
    try:
        records = get_patrol_list_admin(
            status_filter=status_filter,
            problem_type_id=problem_type_id,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
            keyword=keyword,
            data_type=data_type,
            page=page or 1,
            page_size=page_size or 100
        )
        logger.info(f"📤 [api_patrol_list_admin] 返回记录数: {len(records.get('records', []))}")
        return records
    except Exception as e:
        # 增加详细日志，便于排查 500 错误
        logger.error(f"/api/admin/patrol/list 查询失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询失败"
        )


@router.get("/admin/stats", summary="管理员统计看板")
@cache_response(ttl=600, key_prefix="admin_stats")
async def admin_stats(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    data_type: Optional[str] = Query(None, description="数据类型（real/test），不传则统计全部"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    try:
        return get_admin_stats(start_date=start_date, end_date=end_date, data_type=data_type)
    except Exception as e:
        logger.error(f"Admin stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="统计失败"
        )


@router.get("/export/excel", summary="导出巡查记录为 Excel")
@cache_response(ttl=600, key_prefix="admin:export:excel")
async def export_excel(
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    segment_id: Optional[int] = Query(None, description="路段ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    导出巡查记录为 Excel 文件（需要管理员权限）
    
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    - **segment_id**: 路段ID（可选）
    - **status**: 状态筛选（可选）
    """
    try:
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if segment_id:
            filters['segment_id'] = segment_id
        if status_filter:
            filters['status'] = status_filter
        
        excel_data = export_patrol_records_to_excel(filters)
        
        # 使用URL编码的文件名，避免中文编码问题
        from urllib.parse import quote
        filename = quote("公路巡查记录.xlsx")
        
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename*=UTF-8\'\'{filename}'
            }
        )
    except Exception as e:
        logger.error(f"导出失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {e}"
        )


# ========================
# 数据库管理接口
# ========================

@router.get("/reinit", summary="数据库重新初始化")
@limiter.limit("1/minute")
async def reinit(
    request: Request,
    step: str = Query('all', description="初始化步骤（1 或 all）"),
    admin: CurrentUser = Depends(get_current_admin)
):
    """
    数据库重新初始化（需要管理员权限）
    
    **警告：此操作会清空数据！**
    """
    if step == '1':
        step_value = 1
    else:
        step_value = 'all'
    
    result = reinit_database(step=step_value, skip_read_only_queries=True)
    insert_audit_log(admin.user_id, "reinit_database", f"step:{step_value}")
    return result


@router.post("/admin/generate", summary="生成随机测试数据")
@limiter.limit("3/minute")
async def generate_data(
    request: Request,
    count: int = Query(50, ge=1, le=5000, description="生成数量"),
    include_photos: bool = Query(False, description="是否生成照片"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """生成随机巡查记录数据（需要管理员权限）- 同步版本"""
    from services.patrol_service import _cache_clear
    
    result = generate_fake_records(count=count, with_photos=include_photos)
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', '生成失败'))
    
    # 生成数据后立即清除统计缓存，让下次查询从 DB 读取新数据
    _cache_clear("admin_stats")
    
    insert_audit_log(admin.user_id, "generate_data", f"count:{count}，inserted:{result.get('inserted', 0)}")
    return result


@router.get("/admin/generate/stream", summary="生成随机测试数据（流式）")
async def generate_data_stream(
    request: Request,
    count: int = Query(50, ge=1, le=5000, description="生成数量"),
    include_photos: bool = Query(False, description="是否生成照片"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """生成随机巡查记录数据（SSE流式，实时显示进度）"""
    from services.patrol_service import stream_generate_fake_records
    
    # 在开始生成之前记录审计日志
    insert_audit_log(
        admin.user_id,
        "generate_data",
        f"开始生成: count={count}, photos={include_photos}"
    )
    
    generator = stream_generate_fake_records(count=count, with_photos=include_photos)
    return StreamingResponse(
        generator(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@router.post("/admin/seed-road-segments", summary="补充全国路段基础库")
@limiter.limit("2/minute")
async def seed_road_segments_endpoint(
    request: Request,
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """当路段库数量过少时，补充全国干线高速/国道基础库。"""
    from services.patrol_service import seed_extended_road_segments
    from services.patrol_service import _cache_clear
    try:
        added = seed_extended_road_segments(min_threshold=20)
        _cache_clear("patrol:list")
        return {"success": True, "added": added}
    except Exception as e:
        logger.error(f"seed-road-segments 失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="补充路段失败")


@router.post("/admin/clean-test-data", summary="清理所有测试数据")
@limiter.limit("2/minute")
async def clean_test_data_endpoint(
    request: Request,
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    删除所有测试数据（data_type='test'的记录及关联照片）
    需要管理员权限
    
    Returns:
        dict: {
            'success': bool,
            'deleted_count': int,  # 删除的记录数
            'photos_deleted': int  # 删除的照片文件数
        }
    """
    try:
        result = clean_test_data()
        
        # 清理数据后清除所有统计和列表缓存（使用 Redis 模式匹配确保完全清掉）
        cache_delete_pattern("admin_stats:*")  # 统计数据
        cache_delete_pattern("admin:stats:*")  # 统计数据（其他格式）
        cache_delete_pattern("admin:patrol:list:*")  # 管理员巡查列表
        cache_delete_pattern("patrol:list:*")  # 巡查员列表
        logger.info("已清理所有相关缓存")
        
        insert_audit_log(admin.user_id, "clean_test_data", f"deleted:{result.get('deleted_count', 0)}")
        return result
    except Exception as e:
        logger.error(f"清理测试数据失败: {e}")
        raise HTTPException(status_code=500, detail=f'清理测试数据失败: {str(e)}')


@router.get("/verify", summary="验证数据库状态")
async def verify(admin: CurrentUser = Depends(get_current_admin)):
    """验证数据库状态（需要管理员权限）"""
    result = verify_database()
    return result


@router.get("/status", summary="获取数据库状态")
async def get_status(admin: CurrentUser = Depends(get_current_admin)):
    """获取数据库状态（需要管理员权限）"""
    try:
        result = get_database_status()
        return result
    except Exception as e:
        logger.error(f"/api/status出错: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': '服务器内部错误',
            'details': str(e),
            'execution_time': 0
        }


# ========================
# SSE 流式接口
# ========================

@router.get("/reinit/stream", summary="数据库重新初始化（流式）")
async def reinit_stream(
    step: str = Query('all', description="初始化步骤（1 或 all）"),
    admin: CurrentUser = Depends(get_current_admin_qs)
):
    """
    数据库重新初始化（SSE 流式返回）
    
    返回实时初始化进度
    """
    return stream_reinit_database_with_step(step)


@router.get("/verify/stream", summary="验证数据库（流式）")
async def verify_stream(admin: CurrentUser = Depends(get_current_admin_qs)):
    """验证数据库状态（SSE 流式返回）"""
    return stream_verify_database()


@router.get("/status/stream", summary="获取数据库状态（流式）")
async def status_stream(admin: CurrentUser = Depends(get_current_admin_qs)):
    """获取数据库状态（SSE 流式返回）"""
    return stream_get_database_status()


# ========================
# 公共统计接口（无需登录）
# ========================

@router.get("/public/stats", summary="公共统计（无需认证）")
async def public_stats(
    region: str = Query(None, description="大洲过滤[已过时]"),
    scope: str = Query('world', description="数据范围：world|china|province|city"),
    province: str = Query(None, description="省份名称（如'浙江省'）"),
    city: str = Query(None, description="城市名称"),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    lat_min: float = Query(None, description="自定义纬度下界"),
    lat_max: float = Query(None, description="自定义纬度上界"),
    lon_min: float = Query(None, description="自定义经度下界"),
    lon_max: float = Query(None, description="自定义经度上界"),
    data_type: str = Query(None, description="数据类型（real/test），不传则统计全部")
):
    """
    获取统计数据
    
    示例：
    - /api/public/stats?scope=world → 全球统计
    - /api/public/stats?scope=china → 中国统计
    - /api/public/stats?scope=province&province=浙江省 → 浙江省统计
    - /api/public/stats?scope=city&province=浙江省&city=杭州 → 杭州市统计
    """
    try:
        return get_admin_stats(
            region=region,
            scope=scope,
            province=province,
            city=city,
            start_date=start_date,
            end_date=end_date,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            data_type=data_type
        )
    except Exception as e:
        logger.error(f"Public stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="统计失败")
