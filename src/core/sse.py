# utils/sse.py
import json
import time
from datetime import datetime, timezone

def sse_message(event, data, step=None):
    """生成一条 SSE 消息
    增强：携带毫秒级时间戳与 ISO8601 时间，便于前端精确计算耗时。
    """
    now = time.time()
    payload = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'ts_epoch_ms': int(now * 1000),
        'ts': datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
        'event': event,
        'data': data
    }
    if step is not None:
        payload['step'] = step
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"