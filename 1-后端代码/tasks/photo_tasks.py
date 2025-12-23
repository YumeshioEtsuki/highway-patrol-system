"""
照片处理异步任务

功能：
- 照片压缩（减小文件大小）
- 生成缩略图
- 格式转换
- 批量处理
"""

import os
from typing import Dict, Any
from PIL import Image
from celery_app import celery_app
from utils.logger import setup_logger
from utils.config import settings

logger = setup_logger(__name__)


@celery_app.task(bind=True, name="tasks.photo_tasks.compress_photo", max_retries=3)
def compress_photo(self, photo_path: str, quality: int = 85) -> Dict[str, Any]:
    """
    压缩照片文件
    
    参数：
        photo_path: 照片文件路径
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
        logger.info(f"开始压缩照片: {photo_path}")
        
        # 验证文件存在
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"照片不存在: {photo_path}")
        
        # 获取原始文件大小
        original_size = os.path.getsize(photo_path)
        
        # 打开图片
        with Image.open(photo_path) as img:
            # 转换为 RGB（移除 Alpha 通道）
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            
            # 生成输出路径
            base, ext = os.path.splitext(photo_path)
            output_path = f"{base}_compressed{ext}"
            
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
        logger.error(f"照片压缩失败 {photo_path}: {e}", exc_info=True)
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(bind=True, name="tasks.photo_tasks.generate_thumbnail")
def generate_thumbnail(self, photo_path: str, size: tuple = (200, 200)) -> Dict[str, Any]:
    """
    生成照片缩略图
    
    参数：
        photo_path: 照片文件路径
        size: 缩略图尺寸（宽, 高）
    
    返回：
        {
            "success": bool,
            "thumbnail_path": str,
            "size": tuple
        }
    """
    try:
        logger.info(f"生成缩略图: {photo_path}")
        
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"照片不存在: {photo_path}")
        
        with Image.open(photo_path) as img:
            # 保持宽高比
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 生成缩略图路径
            base, ext = os.path.splitext(photo_path)
            thumbnail_path = f"{base}_thumb{ext}"
            
            # 保存
            img.save(thumbnail_path, format="JPEG", quality=85)
        
        logger.info(f"缩略图生成成功: {thumbnail_path}")
        
        return {
            "success": True,
            "thumbnail_path": thumbnail_path,
            "size": size
        }
    
    except Exception as e:
        logger.error(f"缩略图生成失败 {photo_path}: {e}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)
        
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="tasks.photo_tasks.process_batch_photos")
def process_batch_photos(photo_paths: list, quality: int = 85) -> Dict[str, Any]:
    """
    批量处理照片
    
    参数：
        photo_paths: 照片路径列表
        quality: 压缩质量
    
    返回：
        {
            "total": int,
            "success": int,
            "failed": int,
            "results": list
        }
    """
    logger.info(f"开始批量处理 {len(photo_paths)} 张照片")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for photo_path in photo_paths:
        try:
            # 调用压缩任务
            result = compress_photo.apply_async(args=[photo_path, quality])
            task_result = result.get(timeout=300)  # 5 分钟超时
            
            if task_result.get("success"):
                success_count += 1
            else:
                failed_count += 1
            
            results.append({
                "path": photo_path,
                "result": task_result
            })
        
        except Exception as e:
            logger.error(f"处理照片失败 {photo_path}: {e}")
            failed_count += 1
            results.append({
                "path": photo_path,
                "result": {"success": False, "error": str(e)}
            })
    
    logger.info(f"批量处理完成: 成功 {success_count}, 失败 {failed_count}")
    
    return {
        "total": len(photo_paths),
        "success": success_count,
        "failed": failed_count,
        "results": results
    }
