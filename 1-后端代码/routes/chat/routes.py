# routes/chat.py
# AI 聊天接口 - 集成 Ollama API（本地开源模型 + 千问）

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# ========================
# 配置（支持环境变量）
# ========================
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "127.0.0.1")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:7b")  # 千问 7B 模型

logger.info(f"Ollama API URL: {OLLAMA_API_URL}")
logger.info(f"Ollama Model: {OLLAMA_MODEL}")

# ========================
# 数据模型
# ========================
class ChatMessage(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]  # 对话历史
    query: str  # 用户最新问题
    system_prompt: Optional[str] = None  # 自定义系统提示

class ChatResponse(BaseModel):
    success: bool
    reply: Optional[str] = None
    error: Optional[str] = None

# ========================
# 聊天接口
# ========================
@router.post("/chat", response_model=ChatResponse, summary="AI 助手聊天")
async def chat(req: ChatRequest):
    """
    通用 AI 聊天接口，使用本地 Ollama + 千问模型
    
    - **messages**: 对话历史（格式: [{"role": "user/assistant", "content": "..."}]）
    - **query**: 用户最新问题
    - **system_prompt**: 可选的系统提示词（默认为通用 Q&A 助手）
    """
    
    try:
        # 构建消息列表
        system_prompt = req.system_prompt or """你是一个友好、专业的 AI 助手。
- 提供清晰、准确的回答
- 对于不知道的问题，诚实地说"我不太清楚"
- 支持中文和英文
- 回答简洁易懂，避免冗长的技术术语"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加对话历史
        for msg in req.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        # 添加用户最新问题
        messages.append({"role": "user", "content": req.query})
        
        # 调用 Ollama API
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Ollama API 错误 ({response.status_code}): {error_text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"AI 服务返回错误: {response.status_code}"
                )
            
            data = response.json()
            reply = data.get('message', {}).get('content', '')
            
            if not reply:
                return ChatResponse(
                    success=False,
                    error="AI 没有生成回复，请重试"
                )
            
            return ChatResponse(success=True, reply=reply)
        
    except httpx.ConnectError:
        logger.error("无法连接 Ollama 服务（http://127.0.0.1:11434）")
        return ChatResponse(
            success=False,
            error="AI 服务未启动。请确保 Ollama 正在运行"
        )
    except httpx.TimeoutException:
        logger.error("Ollama API 请求超时")
        return ChatResponse(
            success=False,
            error="请求超时，请重试"
        )
    except Exception as e:
        logger.error(f"聊天失败: {e}", exc_info=True)
        return ChatResponse(
            success=False,
            error=f"服务错误: {str(e)}"
        )


# ========================
# 健康检查（测试 Ollama 连接）
# ========================
@router.get("/chat/health", summary="检查 AI 服务连接")
async def chat_health():
    """检查 Ollama 服务连接状态"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://127.0.0.1:11434/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name') for m in data.get('models', [])]
                
                if OLLAMA_MODEL in models:
                    return {
                        "status": "ok",
                        "message": f"AI 服务已就绪（模型: {OLLAMA_MODEL}）",
                        "models": models
                    }
                else:
                    return {
                        "status": "warning",
                        "message": f"Ollama 在运行，但缺少模型 {OLLAMA_MODEL}",
                        "available_models": models
                    }
            else:
                return {
                    "status": "error",
                    "message": "Ollama 服务异常"
                }
    except httpx.ConnectError:
        return {
            "status": "error",
            "message": "Ollama 服务未启动 (http://127.0.0.1:11434)"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"连接失败: {str(e)}"
        }
