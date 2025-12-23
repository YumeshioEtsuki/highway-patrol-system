# ⚡ Celery 任务队列 - 5 分钟快速上手

## 🎯 最快启动流程

### 1️⃣ 启动 Redis（2 分钟）

```bash
# Windows - Docker 方式（推荐）
docker run -d --name redis-celery -p 6379:6379 redis:7-alpine

# 验证 Redis 运行
redis-cli ping
# 应返回: PONG
```

### 2️⃣ 启动 Celery Worker（1 分钟）

```bash
# 方式 A: 使用 PowerShell 脚本（全自动）
cd 1-后端代码
.\start_celery.ps1

# 方式 B: 手动启动（只启动 Worker）
celery -A celery_app worker --loglevel=info --pool=solo -Q photo,ai,report,maintenance
```

### 3️⃣ 测试任务提交（2 分钟）

```bash
# 运行测试脚本
python test_celery_tasks.py

# 或者访问 Swagger UI
# 打开浏览器: http://127.0.0.1:5000/docs
# 测试端点: POST /api/tasks/photo/compress
```

---

## 📝 快速 API 使用示例

### 提交照片压缩任务

```bash
# 使用 curl
curl -X POST "http://127.0.0.1:5000/api/tasks/photo/compress" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"photo_path": "photos/test.jpg", "quality": 85}'

# 响应示例
{
  "task_id": "c1234567-89ab-cdef-0123-456789abcdef",
  "status": "PENDING"
}
```

### 查询任务状态

```bash
curl -X GET "http://127.0.0.1:5000/api/tasks/status/c1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 响应示例（进行中）
{
  "task_id": "c1234567-89ab-cdef-0123-456789abcdef",
  "status": "PROCESSING",
  "progress": 50,
  "message": "Compressing image..."
}

# 响应示例（完成）
{
  "task_id": "c1234567-89ab-cdef-0123-456789abcdef",
  "status": "SUCCESS",
  "result": {
    "success": true,
    "original_size": 2048000,
    "compressed_size": 512000,
    "reduction_percent": 75.0,
    "output_path": "photos/compressed/test.jpg"
  }
}
```

---

## 🎨 前端集成示例

### JavaScript (小程序/Web)

```javascript
// 1. 提交任务
async function compressPhoto(photoPath) {
  const response = await fetch('http://127.0.0.1:5000/api/tasks/photo/compress', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      photo_path: photoPath,
      quality: 85
    })
  });
  
  const data = await response.json();
  return data.task_id;
}

// 2. 轮询任务状态
async function pollTaskStatus(taskId) {
  const maxAttempts = 60;  // 最多等待 60 秒
  
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`http://127.0.0.1:5000/api/tasks/status/${taskId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.status === 'SUCCESS') {
      console.log('任务完成:', data.result);
      return data.result;
    } else if (data.status === 'FAILURE') {
      throw new Error(`任务失败: ${data.error}`);
    }
    
    // 等待 1 秒后重试
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('任务超时');
}

// 3. 完整流程
async function main() {
  try {
    const taskId = await compressPhoto('photos/large_image.jpg');
    console.log('任务已提交:', taskId);
    
    const result = await pollTaskStatus(taskId);
    console.log('压缩成功:', result);
  } catch (error) {
    console.error('错误:', error);
  }
}
```

---

## 🔍 监控界面快速查看

### Flower 监控（Web UI）

```bash
# 启动 Flower
celery -A celery_app flower --port=5555

# 访问地址
http://127.0.0.1:5555
```

**Flower 功能**:
- 📊 实时查看活跃任务
- 📈 任务执行统计图表
- 🔍 搜索历史任务
- ⚙️ 控制 Worker（暂停/恢复）
- 📝 查看任务详细日志

---

## 🛠️ 常用命令速查

### Worker 管理

```bash
# 启动 Worker（所有队列）
celery -A celery_app worker --loglevel=info --pool=solo

# 启动 Worker（指定队列）
celery -A celery_app worker -Q photo,ai --loglevel=info

# 查看活跃任务
celery -A celery_app inspect active

# 查看注册的任务
celery -A celery_app inspect registered

# 查看队列统计
celery -A celery_app inspect stats

# 清空队列
celery -A celery_app purge
```

### Beat 调度器

```bash
# 启动 Beat（定时任务）
celery -A celery_app beat --loglevel=info

# 查看定时任务列表
celery -A celery_app inspect scheduled
```

---

## 📦 可用任务列表

### 1. 照片处理任务（队列: photo）

| 任务名称 | API 端点 | 描述 |
|---------|---------|------|
| compress_photo | `POST /api/tasks/photo/compress` | 压缩照片（减小文件大小） |
| generate_thumbnail | `POST /api/tasks/photo/thumbnail` | 生成缩略图 |
| process_batch_photos | `POST /api/tasks/photo/batch` | 批量处理照片 |

### 2. AI 任务（队列: ai）

| 任务名称 | API 端点 | 描述 |
|---------|---------|------|
| check_photo_quality | `POST /api/tasks/photo/quality-check` | AI 质量检查（模糊检测） |
| analyze_patrol_record | `POST /api/tasks/ai/analyze` | AI 分析巡查记录 |

**注意**: AI 任务需要 Ollama 服务运行

```bash
# 启动 Ollama
ollama serve

# 拉取模型
ollama pull qwen:7b
```

### 3. 报告任务（队列: report）

| 任务名称 | API 端点 | 描述 |
|---------|---------|------|
| export_large_excel | `POST /api/tasks/report/export-excel` | 导出大型 Excel 报告 |
| generate_monthly_report | `POST /api/tasks/report/monthly` | 生成月度报告 |

### 4. 维护任务（队列: maintenance）

| 任务名称 | API 端点 | 描述 |
|---------|---------|------|
| cleanup_expired_cache | `POST /api/tasks/maintenance/cleanup-cache` | 清理过期缓存 |
| health_check | 自动（每小时） | 系统健康检查 |
| cleanup_old_photos | 自动（每天凌晨） | 删除 90 天前的照片 |

---

## 🐛 快速故障排查

### ❌ 问题：Worker 无法启动

```bash
# 检查 Redis
redis-cli ping

# 检查端口占用
netstat -ano | findstr :6379

# 重启 Redis
docker restart redis-celery
```

### ❌ 问题：任务一直 PENDING

```bash
# 1. 确认 Worker 正在运行
celery -A celery_app inspect active

# 2. 检查队列名称是否正确
# 照片任务必须使用 photo 队列
# AI 任务必须使用 ai 队列

# 3. 查看 Worker 日志
celery -A celery_app worker --loglevel=debug
```

### ❌ 问题：AI 任务失败

```bash
# 1. 检查 Ollama 服务
curl http://127.0.0.1:11434/api/tags

# 2. 启动 Ollama
ollama serve

# 3. 验证模型
ollama list | findstr qwen
```

---

## 📊 任务性能建议

### 照片压缩任务
- **推荐并发**: 4-8 个 Worker
- **平均耗时**: 1-3 秒/张
- **适用场景**: 用户上传后自动压缩

### AI 质量检查
- **推荐并发**: 1-2 个 Worker（Ollama 资源限制）
- **平均耗时**: 5-15 秒/张
- **适用场景**: 管理员审核时触发

### Excel 导出
- **推荐并发**: 2-4 个 Worker
- **平均耗时**: 10-60 秒（取决于数据量）
- **适用场景**: 大批量数据导出

---

## 🚀 生产环境快速部署

### 使用 Supervisor 管理（Linux）

```bash
# 1. 安装 Supervisor
sudo apt install supervisor

# 2. 创建配置文件
sudo nano /etc/supervisor/conf.d/celery.conf

# 3. 添加以下内容
[program:celery-worker]
command=/path/to/venv/bin/celery -A celery_app worker --loglevel=info
directory=/path/to/highway-patrol-system/1-后端代码
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery-beat]
command=/path/to/venv/bin/celery -A celery_app beat --loglevel=info
directory=/path/to/highway-patrol-system/1-后端代码
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log

# 4. 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 5. 启动服务
sudo supervisorctl start celery-worker
sudo supervisorctl start celery-beat
```

### 使用 Docker Compose（跨平台）

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
  
  celery-worker:
    build: .
    command: celery -A celery_app worker --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
  
  celery-beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
  
  flower:
    build: .
    command: celery -A celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

volumes:
  redis-data:
```

---

## 📚 更多资源

- 📖 **完整文档**: 参见 `CELERY_SETUP.md`
- 🧪 **测试脚本**: `python test_celery_tasks.py`
- 📊 **监控界面**: http://127.0.0.1:5555
- 📝 **API 文档**: http://127.0.0.1:5000/docs

---

## 💡 小贴士

1. **开发环境**: 使用 `--pool=solo` 参数（Windows 兼容）
2. **生产环境**: 使用 `--pool=prefork` 或 `--pool=gevent`
3. **调试模式**: 添加 `--loglevel=debug` 查看详细日志
4. **任务重试**: 所有任务默认最多重试 3 次
5. **结果保留**: 任务结果默认保留 1 小时

---

**快速上手指南版本**: 1.0  
**最后更新**: 2025-01-21  
**预计上手时间**: 5 分钟
