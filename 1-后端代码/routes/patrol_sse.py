# routes/patrol_sse.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from utils.sse import sse_message
from utils.deps import get_current_admin_qs, CurrentUser
import asyncio

router = APIRouter(prefix="/api", tags=["sse"])

# 限流队列，避免过载积压
patrol_event_queue: asyncio.Queue = asyncio.Queue(maxsize=200)


async def patrol_event_stream():
    """
    SSE 事件流生成器（异步且非阻塞）
    - 使用 asyncio.wait_for 等待队列事件，避免阻塞整个事件循环。
    - 定时发送心跳，保持连接并防止代理缓冲。
    """
    while True:
        try:
            event = await asyncio.wait_for(patrol_event_queue.get(), timeout=5)
            if isinstance(event, str):
                yield event.encode("utf-8")
            else:
                yield event
        except asyncio.TimeoutError:
            # 心跳包，告知客户端连接仍然存活
            yield b": ping\n\n"
        # 立即让出控制权，不占用事件循环
        await asyncio.sleep(0)


@router.get("/sse/patrol-photo", summary="巡查照片实时推送（SSE）")
async def patrol_photo_stream(admin: CurrentUser = Depends(get_current_admin_qs)):
    """
    SSE 实时推送新上传的巡查照片（需要管理员权限）
    
    客户端连接后，每当有新照片上传时会收到实时推送。
    
    事件格式：
    ```
    data: {"event": "new_photo", "data": {"record_id": 1, "photo_id": 2, "photo_url": "..."}}
    ```
    """
    return StreamingResponse(
        patrol_event_stream(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


def push_new_photo_event(record_id: int, photo_id: int, photo_url: str):
    """
    推送新照片事件到 SSE 流（非阻塞）
    
    Args:
        record_id: 巡查记录ID
        photo_id: 照片ID
        photo_url: 照片HTTP URL路径（如 /photos/auto_123.jpg）
    """
    import asyncio
    message = sse_message(
        event="new_photo",
        data={
            "record_id": record_id,
            "photo_id": photo_id,
            "photo_url": photo_url
        }
    )
    # 尽量使用非阻塞入队，避免在不同线程/上下文中卡住事件循环
    try:
        patrol_event_queue.put_nowait(message)
        print(f"[SSE] 已推送照片事件: record_id={record_id}, photo_id={photo_id}, url={photo_url}")
    except asyncio.QueueFull:
        print(f"[SSE] 队列已满，丢弃照片事件: {photo_id}")
        pass  # 队列满则丢弃
        pass