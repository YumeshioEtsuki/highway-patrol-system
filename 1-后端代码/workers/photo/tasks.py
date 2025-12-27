"""
照片处理异步任务

功能：
- 照片压缩（减小文件大小）
- 生成缩略图
- 格式转换
- 批量处理
"""

import os
import glob
from typing import Dict, Any
from PIL import Image
from celery_app import celery_app
from core.logger import setup_logger
from settings import settings

logger = setup_logger(__name__)


def get_photo_path_from_id(photo_id: str) -> str:
    """
    安全的 photo_id 到文件路径映射
    
    参数：
        photo_id: 照片唯一标识符
    
    返回：
        str: 照片文件的完整路径
    
    抛出：
        FileNotFoundError: 照片不存在
    """
    from utils.utils import get_db_connection
    
    # 从数据库查询文件路径
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM Photo WHERE photo_id = %s", (photo_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result[0]
        else:
            raise FileNotFoundError(f"照片不存在: photo_id={photo_id}")
    
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"查询照片路径失败: photo_id={photo_id}, error={e}")
        raise FileNotFoundError(f"照片不存在: photo_id={photo_id}")



@celery_app.task(bind=True, name="tasks.photo_tasks.compress_photo", max_retries=3)
def compress_photo(self, photo_id: str, quality: int = 85) -> Dict[str, Any]:
    """
    压缩照片文件（使用安全的 photo_id）
    
    参数：
        photo_id: 照片ID（安全标识）
        quality: 压缩质量（1-100，默认 85）
    
    返回：
        {
            "success": bool,
            "original_size": int,
            "compressed_size": int,
            "reduction_percent": float,
            "output_path": str
        }
    """
    try:
        logger.info(f"开始压缩照片: photo_id={photo_id}")
        
        # 安全路径映射：根据 photo_id 获取真实路径
        photo_path = get_photo_path_from_id(photo_id)
        
        # 验证文件存在
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"照片不存在: {photo_id}")
        
        # 获取原始文件大小
        original_size = os.path.getsize(photo_path)
        
        # 准备输出目录，避免与原始样本混放
        output_dir = settings.PHOTO_OUTPUT_FOLDER
        os.makedirs(output_dir, exist_ok=True)

        # 打开图片
        with Image.open(photo_path) as img:
            # 转换为 RGB（移除 Alpha 通道）
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            
            # 生成输出路径（与原始样本分目录存放）
            base_name, ext = os.path.splitext(os.path.basename(photo_path))
            output_path = os.path.join(output_dir, f"{base_name}_compressed{ext}")
            
            # 压缩保存
            img.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True
            )
        
        # 获取压缩后文件大小
        compressed_size = os.path.getsize(output_path)
        reduction_percent = ((original_size - compressed_size) / original_size) * 100
        
        logger.info(f"压缩完成: {photo_path} -> {output_path}")
        logger.info(f"大小减少: {original_size} -> {compressed_size} ({reduction_percent:.1f}%)")
        
        return {
            "success": True,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction_percent": round(reduction_percent, 2),
            "output_path": output_path
        }
    
    except Exception as e:
        # 使用 photo_id 而不是 photo_path（因为异常可能在获取 photo_path 时发生）
        logger.error(f"照片压缩失败 photo_id={photo_id}: {e}", exc_info=True)
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(bind=True, name="tasks.photo_tasks.generate_thumbnail")
def generate_thumbnail(self, photo_id: str, size: tuple = (200, 200)) -> Dict[str, Any]:
    """
    生成照片缩略图（使用安全的 photo_id）
    
    参数：
        photo_id: 照片ID
        size: 缩略图尺寸 (width, height)
    
    返回：
        {
            "success": bool,
            "thumbnail_path": str,
            "size": tuple
        }
    """
    try:
        logger.info(f"开始生成缩略图: photo_id={photo_id}, size={size}")

        # 安全路径映射
        photo_path = get_photo_path_from_id(photo_id)

        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"照片不存在: {photo_path}")

        with Image.open(photo_path) as img:
            # 保持宽高比
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # 生成输出目录与路径（与原始样本分离）
            output_dir = settings.PHOTO_OUTPUT_FOLDER
            os.makedirs(output_dir, exist_ok=True)

            base_name, ext = os.path.splitext(os.path.basename(photo_path))
            thumbnail_path = os.path.join(output_dir, f"{base_name}_thumb{ext}")

            # 保存
            img.save(thumbnail_path, format="JPEG", quality=85)

        logger.info(f"缩略图生成成功: {thumbnail_path}")

        return {
            "success": True,
            "thumbnail_path": thumbnail_path,
            "size": size
        }

    except Exception as e:
        # 使用 photo_id 而不是 photo_path（因为异常可能在获取 photo_path 时发生）
        logger.error(f"缩略图生成失败 photo_id={photo_id}: {e}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)

        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="tasks.photo_tasks.process_batch_photos")
def process_batch_photos(photo_paths: list, quality: int = 85) -> Dict[str, Any]:
    """
    批量处理照片（异步）
    
    参数：
        photo_paths: 照片路径/ID 列表
        quality: 压缩质量
    
    返回：
        {
            "total": int,
            "task_ids": list - 所有子任务 ID，用于追踪进度
        }
    
    注意：
        - 不在此函数内等待子任务完成
        - 通过返回的 task_ids 可以单独查询每个任务的状态
    """
    logger.info(f"开始提交批量处理任务，共 {len(photo_paths)} 张照片")
    
    task_ids = []
    
    for photo_path in photo_paths:
        try:
            # 异步调用压缩任务（不等待结果）
            result = compress_photo.apply_async(args=[photo_path, quality])
            task_ids.append(result.id)
            logger.info(f"提交照片处理任务: {photo_path} (task_id={result.id})")
        
        except Exception as e:
            logger.error(f"提交照片处理失败 {photo_path}: {e}")
    
    logger.info(f"批量处理任务提交完成: 总数 {len(photo_paths)}, 成功提交 {len(task_ids)}")
    
    return {
        "total": len(photo_paths),
        "task_ids": task_ids
    }
