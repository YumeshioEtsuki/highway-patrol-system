# routes/patrol_sse.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from core.sse import sse_message
from core.deps import get_current_admin_qs, CurrentUser
import asyncio

router = APIRouter(prefix="/api", tags=["sse"])

# 限流队列，避免过载积压（增大队列容量以应对批量数据生成）
patrol_event_queue: asyncio.Queue = asyncio.Queue(maxsize=500)


async def patrol_event_stream():
    """
    SSE 事件流生成器（异步且非阻塞，增强稳定性）
    - 使用 asyncio.wait_for 等待队列事件，避免阻塞整个事件循环。
    - 每2秒发送心跳，保持连接并防止代理/浏览器超时断开。
    - 增加异常恢复机制，避免单个错误导致整个流断开。
    """
    import time
    last_heartbeat = time.time()
    
    while True:
        try:
            # 缩短超时到2秒，更频繁地发送心跳
            event = await asyncio.wait_for(patrol_event_queue.get(), timeout=2.0)
            if isinstance(event, str):
                yield event.encode("utf-8")
            else:
                yield event
            last_heartbeat = time.time()
        except asyncio.TimeoutError:
            # 心跳包：发送真实事件（更强的连接保持）
            current_time = time.time()
            if current_time - last_heartbeat >= 2.0:
                heartbeat_msg = sse_message(
                    event="heartbeat",
                    data={"timestamp": int(current_time)}
                )
                if isinstance(heartbeat_msg, str):
                    yield heartbeat_msg.encode("utf-8")
                else:
                    yield heartbeat_msg
                last_heartbeat = current_time
        except asyncio.CancelledError:
            # 客户端断开连接，正常退出
            print("[SSE] 客户端断开连接")
            break
        except Exception as e:
            # 其他异常：记录日志但不中断流
            print(f"[SSE] 事件流异常（已恢复）: {e}")
            yield b": error-recovered\n\n"
            last_heartbeat = time.time()
        
        # 让出控制权，避免阻塞事件循环
        await asyncio.sleep(0.01)


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
    推送新照片事件到 SSE 流（非阻塞，支持同步调用）
    
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
    # 安全入队：支持从同步代码调用（修正逻辑）
    try:
        # 首先尝试获取运行中的事件循环
        try:
            loop = asyncio.get_running_loop()
            # 在异步上下文中，直接入队
            patrol_event_queue.put_nowait(message)
            print(f"[SSE] 已推送照片事件（异步）: record_id={record_id}, photo_id={photo_id}")
        except RuntimeError:
            # 不在异步上下文中（如生成数据的同步函数）
            # 查找主事件循环并使用 call_soon_threadsafe
            try:
                loop = asyncio.get_event_loop()
                # 跨线程安全入队
                loop.call_soon_threadsafe(patrol_event_queue.put_nowait, message)
                print(f"[SSE] 已推送照片事件（跨线程）: record_id={record_id}, photo_id={photo_id}")
            except Exception as inner_e:
                # 无法获取事件循环（可能服务器未启动），静默忽略
                print(f"[SSE] 无法推送照片事件（无事件循环）: {inner_e}")
    except asyncio.QueueFull:
        print(f"[SSE] 队列已满，丢弃照片事件: record_id={record_id}, photo_id={photo_id}")
    except Exception as e:
        # 任何其他错误都不应该阻塞主流程
        print(f"[SSE] 推送照片事件失败（已忽略）: {e}")