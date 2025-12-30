"""
AI 质量检查异步任务

功能：
- 使用 Ollama 检查照片质量
- 智能分析巡查记录
- 自动标注问题类型
"""

import os
import glob
import base64
import requests
from typing import Dict, Any
from celery_app import celery_app
from core.logger import setup_logger

logger = setup_logger(__name__)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen:7b"


def get_photo_path_from_id(photo_id: str) -> str:
    """
    安全的 photo_id 到文件路径映射
    
    从数据库查询照片文件路径而不是文件系统查找
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


@celery_app.task(bind=True, name="tasks.ai_tasks.check_photo_quality", max_retries=2)
def check_photo_quality(self, photo_id: str) -> Dict[str, Any]:
    """
    使用 AI 检查照片质量（使用安全的 photo_id）
    
    参数：
        photo_id: 照片ID（安全标识符）
    
    返回：
        {
            "success": bool,
            "quality_score": float,  # 0-10
            "is_clear": bool,
            "issues": list,
            "suggestions": str
        }
    """
    try:
        logger.info(f"开始 AI 质量检查: photo_id={photo_id}")
        
        # 安全路径映射
        photo_path = get_photo_path_from_id(photo_id)
        
        # 验证文件存在
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"照片不存在: {photo_id}")
        
        # 读取照片并转换为 base64
        with open(photo_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 构建 AI 提示
        prompt = """请分析这张公路巡查照片的质量，评估以下方面：
1. 清晰度（是否模糊）
2. 光线（是否过暗或过曝）
3. 构图（是否包含关键信息）
4. 问题是否明显可见

请用 JSON 格式返回：
{
    "quality_score": 0-10分,
    "is_clear": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": "改进建议"
}"""
        
        # 调用 Ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_data]
                    }
                ],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API 返回错误: {response.status_code}")
        
        # 解析响应
        ai_response = response.json()
        content = ai_response.get("message", {}).get("content", "{}")
        
        # 尝试解析 JSON
        import json
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # 如果不是 JSON，使用默认值
            result = {
                "quality_score": 7.0,
                "is_clear": True,
                "issues": [],
                "suggestions": content
            }
        
        logger.info(f"AI 质量检查完成: {photo_path}, 评分: {result.get('quality_score')}")
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        logger.error(f"AI 质量检查失败 photo_id={photo_id}: {e}", exc_info=True)
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=120)
        
        return {
            "success": False,
            "error": str(e),
            "quality_score": 5.0,
            "is_clear": False,
            "issues": ["AI 检查失败"],
            "suggestions": "无法进行 AI 分析"
        }


@celery_app.task(bind=True, name="tasks.ai_tasks.analyze_patrol_record")
def analyze_patrol_record(self, record_id: int, description: str, photos: list) -> Dict[str, Any]:
    """
    智能分析巡查记录
    
    参数：
        record_id: 巡查记录 ID
        description: 问题描述
        photos: 照片路径列表
    
    返回：
        {
            "success": bool,
            "severity_level": int,  # 1-5
            "problem_category": str,
            "ai_analysis": str,
            "recommended_action": str
        }
    """
    try:
        logger.info(f"开始 AI 分析巡查记录: {record_id}")
        
        # 构建分析提示
        prompt = f"""请分析这条公路巡查记录：

问题描述：{description}
照片数量：{len(photos)}

请评估：
1. 严重程度（1-5级，5 最严重）
2. 问题类别（路面、桥梁、标识、排水等）
3. 风险分析
4. 建议处理方案

请用 JSON 格式返回：
{{
    "severity_level": 1-5,
    "problem_category": "类别",
    "ai_analysis": "详细分析",
    "recommended_action": "处理建议"
}}"""
        
        # 调用 Ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API 返回错误: {response.status_code}")
        
        # 解析响应
        ai_response = response.json()
        content = ai_response.get("message", {}).get("content", "{}")
        
        import json
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {
                "severity_level": 3,
                "problem_category": "未分类",
                "ai_analysis": content,
                "recommended_action": "需要人工审核"
            }
        
        logger.info(f"AI 分析完成: 记录 {record_id}, 严重度 {result.get('severity_level')}")
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        logger.error(f"AI 分析失败 记录 {record_id}: {e}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=120)
        
        return {
            "success": False,
            "error": str(e),
            "severity_level": 3,
            "problem_category": "未知",
            "ai_analysis": "AI 分析失败",
            "recommended_action": "需要人工审核"
        }
