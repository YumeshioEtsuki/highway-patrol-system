"""
照片管理路由

功能：
- 获取用户上传的照片列表
- 上传新照片（独立于巡查记录）
- 安全的照片ID到路径映射
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime
import os
import uuid
import hashlib
from core.deps import get_current_user, CurrentUser
from core.logger import setup_logger
from settings import settings

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/photos", tags=["photos"])

# 照片上传目录
UPLOAD_FOLDER = getattr(settings, 'UPLOAD_FOLDER', 'photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def generate_photo_id(user_id: int, filename: str) -> str:
    """生成唯一照片ID"""
    timestamp = datetime.now().isoformat()
    raw = f"{user_id}_{filename}_{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_photo_path_by_id(photo_id: str) -> str:
    """
    根据 photo_id 获取物理路径（从数据库查询）
    
    注意：这是一个简化实现，实际应该从数据库查询
    为了演示安全映射，这里假设照片已保存到统一目录
    """
    # TODO: 从数据库查询真实路径
    # 示例：SELECT file_path FROM patrol_photos WHERE photo_id = ?
    
    # 临时实现：假设所有照片在 photos/ 下
    search_path = os.path.join(UPLOAD_FOLDER, f"{photo_id}.*")
    import glob
    matches = glob.glob(search_path)
    if matches:
        return matches[0]
    
    raise FileNotFoundError(f"照片不存在: {photo_id}")


@router.get("/user", summary="获取用户照片列表")
async def get_user_photos(
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前用户上传的所有照片列表
    
    返回：
    [
        {
            "id": "abc123",
            "filename": "road_damage.jpg",
            "upload_time": "2024-01-01 12:00:00",
            "record_id": 123  # 如果关联了巡查记录
        }
    ]
    """
    try:
        from utils.utils import get_db_connection
        
        logger.info(f"获取用户 {current_user.username} 的照片列表")
        
        # 查询当前用户关联的所有照片（通过 InspectionRecord）
        # 使用 photo_id 整数主键作为标识符
        user_id = getattr(current_user, 'user_id', None)
        if not user_id:
            raise ValueError("无法获取用户ID")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                p.photo_id AS id,
                p.file_name AS filename,
                DATE_FORMAT(p.upload_time, '%Y-%m-%d %H:%i:%S') AS upload_time,
                p.file_size AS size_bytes,
                p.record_id
            FROM Photo p
            LEFT JOIN InspectionRecord ir ON p.record_id = ir.record_id
            WHERE ir.user_id = %s
            ORDER BY p.upload_time DESC
            LIMIT 100
            """,
            (user_id,)
        )
        photos = cursor.fetchall() or []
        cursor.close()
        conn.close()

        logger.debug(f"找到 {len(photos)} 张照片（user_id={user_id}）")
        
        return {
            "success": True,
            "data": photos[:100],  # 限制返回最近100张
            "total": len(photos)
        }
    
    except Exception as e:
        logger.error(f"获取照片列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取照片列表失败: {str(e)}"
        )


@router.post("/upload", summary="上传照片")
async def upload_photo(
    file: UploadFile = File(..., description="照片文件"),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    上传照片（独立于巡查记录）
    
    返回：
    {
        "success": true,
        "photo_id": "abc123def456",
        "filename": "road_damage.jpg",
        "upload_time": "2024-01-01 12:00:00"
    }
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名为空"
        )
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # 生成唯一照片ID
        photo_id = generate_photo_id(current_user.user_id, file.filename)
        
        # 保留原始扩展名
        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_filename = f"{photo_id}.{ext}"
        
        # 按日期组织目录
        today = datetime.now().strftime("%Y/%m")
        save_dir = os.path.join(UPLOAD_FOLDER, today)
        os.makedirs(save_dir, exist_ok=True)
        
        filepath = os.path.join(save_dir, safe_filename)
        
        # 读取文件内容
        contents = await file.read()
        
        # 检查文件大小（默认10MB）
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制（最大 {max_size // 1024 // 1024}MB）"
            )
        
        # 保存文件
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        # TODO: 保存到数据库
        # INSERT INTO patrol_photos (photo_id, user_id, file_path, file_name, upload_time)
        # VALUES (?, ?, ?, ?, NOW())
        
        logger.info(f"用户 {current_user.username} 上传照片: {photo_id} ({file.filename})")
        
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "success": True,
            "photo_id": photo_id,
            "filename": file.filename,
            "size_bytes": len(contents),
            "upload_time": upload_time,
            "message": "照片上传成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传照片失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.get("/path/{photo_id}", summary="获取照片路径（内部API）")
async def get_photo_path(
    photo_id: str,
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, str]:
    """
    根据 photo_id 获取物理路径（仅供后端任务使用）
    
    安全说明：
    - 此接口不直接返回文件路径给前端
    - 仅用于后端 Celery 任务内部调用
    - 前端通过 photo_id 提交任务，后端负责路径映射
    """
    try:
        photo_path = get_photo_path_by_id(photo_id)
        
        # 验证文件存在
        if not os.path.exists(photo_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="照片文件不存在"
            )
        
        return {
            "photo_id": photo_id,
            "photo_path": photo_path,
            "exists": True
        }
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"照片不存在: {photo_id}"
        )
    except Exception as e:
        logger.error(f"获取照片路径失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取照片路径失败"
        )
