# routes/patrol.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status, Query
from fastapi.responses import FileResponse
from typing import Optional, List, Union
import os
import uuid
from datetime import datetime
from utils.config import settings
from utils.deps import get_current_user, CurrentUser
from utils.exceptions import BusinessException, NotFoundException
from utils.logger import setup_logger
from utils.cache import cache_response, invalidate_cache

logger = setup_logger(__name__)
from models.schemas import (
    PatrolCreate, PatrolQuery, PatrolListResponse,
    PatrolDetailResponse, PhotoUploadResponse, UserStatsResponse,
    RoadSegmentsListResponse, ProblemTypesListResponse, RoadSegmentResponse,
    ProblemTypeResponse
)
from models.tasks import (
    create_patrol_record, get_patrol_list, get_patrol_detail,
    save_photo_to_db, get_user_stats, get_all_road_segments, get_all_problem_types,
    get_admin_stats
)

try:
    from routes.patrol_sse import push_new_photo_event
except ImportError:
    push_new_photo_event = None  # 容错处理

router = APIRouter(prefix="/api", tags=["patrol"])

# 配置上传目录
UPLOAD_FOLDER = settings.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in settings.ALLOWED_EXTENSIONS


@router.post("/patrol", summary="创建巡查记录")
async def create_patrol(
    segment_id: int = Form(...),
    issue_type_id: int = Form(...),
    description: str = Form(...),
    severity: Optional[int] = Form(1),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[Union[List[UploadFile], UploadFile]] = File(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建巡查记录（支持FormData和照片上传）
    """
    from datetime import datetime
    try:
        print(f"[DEBUG] 收到提交: segment_id={segment_id}, issue_type_id={issue_type_id}, desc={description}")
        print(f"[DEBUG] GPS: latitude={latitude}, longitude={longitude} (types: {type(latitude).__name__}, {type(longitude).__name__})")
        print(f"[DEBUG] Photo参数: {photo} (type: {type(photo).__name__})")
        
        # 构建巡查记录数据（上传时间使用标准 datetime 以避免 MySQL 解析失败）
        patrol_data = {
            'user_id': current_user.user_id,
            'patrol_time': datetime.now(),
            'segment_id': int(segment_id),
            'problem_type_id': int(issue_type_id),
            'description': description.strip(),
            'severity': int(severity) if severity else 1,
            'latitude': float(latitude) if latitude else None,
            'longitude': float(longitude) if longitude else None
        }
        
        print(f"[DEBUG] 处理后数据: {patrol_data}")
        record_id = create_patrol_record(patrol_data)
        print(f"[DEBUG] 记录创建成功: {record_id}")
        
        # 处理照片上传
        uploaded_photos = 0
        if photo:
            files = photo if isinstance(photo, list) else [photo]
            print(f"[DEBUG] 处理 {len(files)} 个文件")
            for idx, file in enumerate(files):
                print(f"[DEBUG] 文件 {idx}: {file}, filename={getattr(file, 'filename', 'N/A')}")
                if file and file.filename:
                    try:
                        photo_data = await file.read()
                        print(f"[DEBUG] 文件 {idx} 已读取，大小: {len(photo_data)} 字节")
                        photo_result = await upload_photo_for_record(record_id, file, photo_data)
                        if photo_result:
                            uploaded_photos += 1
                            print(f"[DEBUG] 文件 {idx} 上传成功，photo_id: {photo_result}")
                    except Exception as e:
                        logger.error(f"照片上传失败: {e}")
                        print(f"[DEBUG] 文件 {idx} 上传异常: {e}")
        print(f"[DEBUG] 共上传 {uploaded_photos} 张照片")
        
        # 清除相关缓存
        await invalidate_cache("patrol:list:*")
        await invalidate_cache("admin:*")
        
        return {
            "success": True,
            "record_id": record_id,
            "photos_uploaded": uploaded_photos,
            "message": "巡查记录提交成功"
        }
    except ValueError as e:
        logger.error(f"值错误: {e}")
        raise BusinessException(detail=f"数据格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"Create patrol error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建记录失败: {str(e)}"
        )


@router.get("/patrol", response_model=PatrolListResponse, summary="查询巡查记录列表")
@cache_response(ttl=300, key_prefix="patrol:list")
async def list_patrol(
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    查询巡查记录列表（分页）
    
    - **user_id**: 用户ID
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    """
    try:
        # 默认查询当前用户，非管理员不可查看他人
        target_user_id = user_id if user_id is not None else current_user.user_id
        if target_user_id != current_user.user_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看其他用户记录"
            )
        
        result = get_patrol_list(user_id=target_user_id, page=page, page_size=page_size)
        return result
    except Exception as e:
        logger.error(f"List patrol error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询列表失败"
        )


@router.get("/patrol/{record_id}", response_model=PatrolDetailResponse, summary="查询巡查记录详情")
async def patrol_detail(
    record_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    查询巡查记录详情（包含照片列表）
    
    - **record_id**: 记录ID
    """
    try:
        record = get_patrol_detail(record_id)
        if record is None:
            raise NotFoundException(detail="记录不存在")
        
        # 验证权限
        if record['user_id'] != current_user.user_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该记录"
            )
        
        return record
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Detail error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询详情失败"
        )


@router.post("/photo", response_model=PhotoUploadResponse, summary="上传巡查照片")
async def upload_photo(
    file: UploadFile = File(..., description="照片文件"),
    record_id: int = Form(..., description="记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    上传巡查照片
    
    - **file**: 照片文件（支持 png/jpg/jpeg/gif）
    - **record_id**: 关联的巡查记录ID
    
    支持的文件格式：png, jpg, jpeg, gif
    最大文件大小：10MB
    """
    # 验证文件
    if not file.filename:
        raise BusinessException(detail="文件名为空")
    
    if not allowed_file(file.filename):
        raise BusinessException(detail="不支持的文件类型，仅支持 png/jpg/jpeg/gif")
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    today = datetime.now().strftime("%Y/%m")
    save_dir = os.path.join(UPLOAD_FOLDER, today)
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, unique_filename)
    
    try:
        # 保存文件
        contents = await file.read()
        
        # 检查文件大小
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise BusinessException(detail=f"文件大小超过限制（最大{settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB）")
        
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        # 保存到数据库
        photo_id = save_photo_to_db(
            record_id=record_id,
            file_path=filepath,
            file_name=unique_filename
        )
        
        photo_url = f"/photos/{today}/{unique_filename}"
        
        # 推送 SSE 事件
        if push_new_photo_event is not None:
            try:
                push_new_photo_event(record_id, photo_id, photo_url)
            except Exception as e:
                logger.warning(f"SSE 推送失败: {e}")
        
        return PhotoUploadResponse(
            photo_id=photo_id,
            photo_url=photo_url
        )
    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Photo upload error: {e}", exc_info=True)
        # 清理已保存的文件
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传失败"
        )


@router.get("/stats", response_model=UserStatsResponse, summary="获取用户统计信息")
async def stats(
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取用户巡查统计信息
    
    - **user_id**: 用户ID
    
    返回：总记录数、待处理数、处理中数、已完成数
    """
    try:
        # 验证权限
        if user_id != current_user.user_id and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看其他用户统计"
            )
        
        result = get_user_stats(user_id=user_id)
        status = result.get('status_breakdown', {}) if isinstance(result, dict) else {}
        return {
            "total_records": result.get('total_records', 0),
            "pending_count": status.get('pending', 0),
            "processing_count": status.get('processing', 0),
            "completed_count": status.get('completed', 0)
        }
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计失败"
        )


@router.get("/road-segments", response_model=RoadSegmentsListResponse, summary="获取所有路段")
async def get_road_segments(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有路段信息
    
    返回：路段ID、路段名称、起始号、结束号等信息
    """
    try:
        segments = get_all_road_segments()
        return RoadSegmentsListResponse(data=segments)
    except Exception as e:
        logger.error(f"Road segments error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取路段列表失败"
        )


@router.get("/issue-types", response_model=ProblemTypesListResponse, summary="获取所有问题类型")
async def get_problem_types(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有问题类型
    
    返回：问题类型ID、类型名称等信息
    """
    try:
        types = get_all_problem_types()
        return ProblemTypesListResponse(data=types)
    except Exception as e:
        logger.error(f"Problem types error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取问题类型列表失败"
        )


@router.get("/public/stats", summary="公开统计数据（供地图页使用）")
async def public_stats(
    region: Optional[str] = None,
    scope: str = Query('world', description="数据范围：world|china|province|city"),
    province: Optional[str] = Query(None, description="省份名称（如'浙江省'）"),
    city: Optional[str] = Query(None, description="城市名称"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    lat_min: Optional[float] = Query(None, description="自定义纬度下界"),
    lat_max: Optional[float] = Query(None, description="自定义纬度上界"),
    lon_min: Optional[float] = Query(None, description="自定义经度下界"),
    lon_max: Optional[float] = Query(None, description="自定义经度上界")
):
    """
    公开统计接口，不需认证
    - 支持大洲(region)兼容参数
    - scope/province/city 与管理员接口保持一致，供前端地图按地理范围过滤
    """
    try:
        from models.tasks import get_admin_stats
        stats = get_admin_stats(
            region=region,
            scope=scope,
            province=province,
            city=city,
            start_date=start_date,
            end_date=end_date,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max
        )
        return stats
    except Exception as e:
        logger.error(f"Public stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="统计失败"
        )


# ========================
# 辅助函数
# ========================

async def upload_photo_for_record(record_id: int, file: UploadFile, photo_data: bytes):
    """
    为巡查记录上传照片
    
    Args:
        record_id: 巡查记录ID
        file: 上传文件
        photo_data: 文件数据
    
    Returns:
        照片保存信息或None
    """
    try:
        from models.tasks import save_photo_to_record
        
        # 生成文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{record_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        # 保存照片文件
        photos_dir = settings.UPLOAD_FOLDER
        os.makedirs(photos_dir, exist_ok=True)
        
        filepath = os.path.join(photos_dir, unique_filename)
        with open(filepath, 'wb') as f:
            f.write(photo_data)
        
        # 保存到数据库
        file_size = os.path.getsize(filepath)
        result = save_photo_to_record(
            record_id=record_id,
            photo_type='test_pictures',
            file_path=filepath,
            file_name=unique_filename,
            file_size=file_size
        )
        
        # 推送 SSE 事件
        if result and push_new_photo_event:
            try:
                photo_url = f"/photos/{unique_filename}"
                push_new_photo_event(record_id, result, photo_url)
                print(f"[DEBUG] SSE 事件已推送: record_id={record_id}, photo_id={result}")
            except Exception as e:
                logger.error(f"SSE 推送失败: {e}")
        
        return result
    except Exception as e:
        logger.error(f"保存照片失败: {e}")
        return None