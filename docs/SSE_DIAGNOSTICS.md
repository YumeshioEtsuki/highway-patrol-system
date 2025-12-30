# SSE照片推送断开问题诊断报告

## 问题现象
生成数据几秒后，SSE照片实时显示连接断开，显示"实时推送已断开，系统将自动重连..."

## 已实施的优化（第一轮）

### 1. 后端心跳优化
- ✅ 心跳间隔从5秒缩短到2秒
- ✅ 异常恢复机制（捕获Exception不中断流）
- ✅ 队列容量从200增加到500

### 2. 前端重连优化
- ✅ 检测EventSource.readyState避免重复重连
- ✅ CONNECTING状态由浏览器自动重连
- ✅ CLOSED状态手动5秒后重连

### 3. 服务器配置优化
- ✅ Uvicorn timeout_keep_alive设置为75秒
- ✅ SSE响应头添加X-Accel-Buffering: no

### 4. 推送限流
- ✅ 只推送前10张照片 + 每10%进度
- ✅ 200条记录仅推送约20次

## 发现的新问题

### 问题1：跨线程入队逻辑错误 ⚠️
**位置**：`routes/patrol/sse_routes.py` - `push_new_photo_event()`

**原始代码**（第105行）：
```python
except RuntimeError:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon_threadsafe(patrol_event_queue.put_nowait, message)
        else:
            patrol_event_queue.put_nowait(message)  # ❌ 错误：在非异步上下文调用
```

**问题**：当事件循环未运行时，直接调用 `put_nowait()` 会失败，因为队列操作需要异步上下文。

**已修复**：移除 `else` 分支，统一使用 `call_soon_threadsafe`

---

### 问题2：前端未明确处理心跳事件
**位置**：`templates/admin.html` - `photoSource.onmessage`

**现状**：
- 后端发送心跳格式：`: heartbeat\n\n` (SSE注释)
- 前端 `onmessage` 只处理 `new_photo` 事件
- 心跳包被浏览器静默忽略（这是正常的）

**分析**：
- SSE注释格式的心跳包 **不会触发** `onmessage` 事件
- 浏览器会自动保持连接活跃
- **这不是问题**，设计是正确的

---

### 问题3：可能的网络/代理超时
**可能原因**：
1. **浏览器限制**：某些浏览器对SSE连接有时间或数量限制
2. **反向代理**：Nginx/Apache默认超时可能小于75秒
3. **防火墙**：网络防火墙可能限制长连接
4. **操作系统**：Windows TCP KeepAlive默认2小时（太长）

---

## 诊断步骤

### 第一步：运行测试脚本
```bash
cd "d:\MySQL Project\highway-patrol-system"
pip install sseclient-py
python test_sse_stability.py
```

**观察项**：
- [ ] SSE连接是否能保持60秒不断开
- [ ] 心跳包是否每2秒出现一次
- [ ] 生成数据时照片事件是否正常推送
- [ ] 是否有长时间（>10秒）无任何事件

### 第二步：查看后端日志
重启服务器后生成数据，观察日志：

```
[SSE] 已推送照片事件（异步）: record_id=1, photo_id=2
[SSE] 已推送照片事件（跨线程）: record_id=2, photo_id=3
[SSE] 客户端断开连接  ← 如果出现这行，说明客户端主动断开
```

### 第三步：浏览器开发者工具
1. 打开浏览器控制台 (F12)
2. 切换到 **Network** 标签
3. 筛选 `patrol-photo` 请求
4. 查看：
   - **Status**: 应该是 `200` 或 `pending`
   - **Type**: `text/event-stream`
   - **EventStream** 标签：查看实时事件

**关键信息**：
- 如果显示 `ERR_INCOMPLETE_CHUNKED_ENCODING`：代理超时
- 如果显示 `net::ERR_CONNECTION_RESET`：服务器主动断开
- 如果显示 `(failed) net::ERR_HTTP2_PROTOCOL_ERROR`：HTTP/2协议问题

### 第四步：检查Nginx/代理配置
如果使用了反向代理，需要配置：

```nginx
location /api/sse/ {
    proxy_pass http://localhost:5000;
    
    # SSE关键配置
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 3600s;  # 1小时超时
    proxy_send_timeout 3600s;
    
    # 心跳支持
    tcp_nodelay on;
}
```

---

## 进一步优化方案

### 方案A：改进心跳机制（推荐）
**目的**：更强的心跳，确保连接不被中间代理断开

**实施**：
1. 将心跳从SSE注释改为真实事件
2. 前端接收心跳后更新UI提示

**代码变更**：
```python
# sse_routes.py - patrol_event_stream()
yield sse_message(event="heartbeat", data={"timestamp": int(time.time())})
```

```javascript
// admin.html - photoSource.onmessage
if (payload.event === "heartbeat") {
    console.log('[SSE] 💓 收到心跳');
    return;
}
```

### 方案B：TCP KeepAlive配置
**目的**：操作系统层面保持TCP连接

**实施**（需要修改 `start_server.py`）：
```python
import socket

# 在uvicorn.Config之前
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)    # 30秒后开始KeepAlive
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)   # 每10秒探测
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)      # 5次失败后断开
```

### 方案C：前端主动ping（备选）
**目的**：前端定期发送请求保持会话活跃

**实施**：
```javascript
// admin.html - startPhotoStream() 内
let pingTimer = setInterval(() => {
    if (photoSource && photoSource.readyState === EventSource.OPEN) {
        // 发送一个轻量级请求保持会话（如获取当前时间）
        fetch('/api/ping', { 
            headers: { 'Authorization': `Bearer ${getAccessToken()}` }
        }).catch(() => {});
    }
}, 10000);  // 每10秒ping一次
```

---

## 测试检查清单

运行以下测试验证修复：

- [ ] **短期测试**（1分钟）
  - [ ] 生成10条带照片数据
  - [ ] SSE连接保持稳定60秒
  - [ ] 照片事件正常推送

- [ ] **中期测试**（5分钟）
  - [ ] 不生成数据，仅保持SSE连接5分钟
  - [ ] 观察是否断开
  - [ ] 心跳包是否持续发送

- [ ] **长期测试**（30分钟）
  - [ ] 保持页面打开30分钟
  - [ ] 期间生成3-5批数据
  - [ ] SSE是否需要重连

- [ ] **压力测试**
  - [ ] 生成200条带照片数据
  - [ ] 观察队列是否溢出
  - [ ] 推送是否限流正常（约20次）

---

## 结论

当前最可能的原因：
1. ✅ **已修复**：跨线程入队逻辑错误导致部分事件丢失
2. 🔍 **待验证**：中间代理或浏览器超时设置
3. 🔍 **待验证**：TCP连接被操作系统回收

**下一步行动**：
1. 重启服务器（应用代码修复）
2. 运行 `test_sse_stability.py` 测试
3. 如果仍断开，实施 **方案A**（改进心跳）
4. 检查浏览器Network标签错误信息
