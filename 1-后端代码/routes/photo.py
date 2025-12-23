# routes/photo.py
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from models.tasks import get_photo_by_id
from utils.exceptions import NotFoundException

router = APIRouter(prefix="/api", tags=["photo"])


@router.get("/photo/{photo_id}", summary="获取照片")
async def serve_photo(photo_id: int):
    """
    获取照片二进制数据
    
    - **photo_id**: 照片ID
    
    返回照片的二进制流，浏览器可直接显示
    """
    photo_bytes = get_photo_by_id(photo_id)
    if not photo_bytes:
        raise NotFoundException(detail="照片不存在")
    
    return Response(
        content=photo_bytes,
        media_type="image/jpeg",  # 可根据实际格式动态判断
        headers={
            "Cache-Control": "public, max-age=31536000",  # 缓存1年
        }
    )