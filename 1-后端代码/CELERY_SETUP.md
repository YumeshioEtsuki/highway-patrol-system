# Celery 任务队列安装配置指南

## 📋 概述

本系统使用 **Celery 5.6.0** + **Redis** 实现异步任务处理，支持：

- **照片处理**：压缩、生成缩略图、批量处理
- **AI 质量检查**：使用 Ollama Qwen 7b 分析照片质量
- **报告导出**：大型 Excel 导出、月度报告生成
- **系统维护**：缓存清理、健康检查、旧文件删除

---

## 🔧 环境要求

### 1. Python 依赖
```bash
# 已在 requirements.txt 中包含
celery==5.6.0
flower==2.0.1
prometheus-client==0.23.1
redis==5.0.1
aioredis==2.0.1
pillow>=12.0.0
pandas>=2.3.0
openpyxl>=3.1.0
requests>=2.31.0
```

### 2. 外部服务
- **Redis**: 作为 Celery 的 broker 和 result backend
- **Ollama**: 运行 Qwen 7b 模型（用于 AI 任务）
- **MySQL**: 数据库（已配置）

---

## 📦 安装步骤

### Step 1: 安装 Redis

#### Windows 方式 1：使用 Docker
```bash
# 拉取 Redis 镜像
docker pull redis:7-alpine

# 启动 Redis 容器
docker run -d --name redis-celery -p 6379:6379 redis:7-alpine

# 验证运行状态
docker ps | findstr redis
```

#### Windows 方式 2：使用 Memurai（Redis for Windows）
```bash
# 下载地址: https://www.memurai.com/get-memurai
# 安装后作为服务自动启动
# 默认监听 127.0.0.1:6379
```

#### Linux/MacOS
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# MacOS (Homebrew)
brew install redis
brew services start redis
```

### Step 2: 安装 Ollama（可选，仅 AI 任务需要）

```bash
# Windows/Linux: 访问 https://ollama.ai/download
# 安装后启动服务
ollama serve

# 拉取 Qwen 7b 模型
ollama pull qwen:7b

# 验证模型
ollama list
```

### Step 3: 安装 Python 依赖

```bash
cd 1-后端代码
pip install -r requirements.txt
```

---

## ⚙️ 配置说明

### 1. Celery 配置文件：`celery_app.py`

```python
# Broker 配置（任务队列）
broker_url = "redis://localhost:6379/1"  # 使用 DB 1

# Backend 配置（结果存储）
result_backend = "redis://localhost:6379/2"  # 使用 DB 2

# 任务路由（4 个队列）
task_routes = {
    'tasks.photo_tasks.*': {'queue': 'photo'},
    'tasks.ai_tasks.*': {'queue': 'ai'},
    'tasks.report_tasks.*': {'queue': 'report'},
    'tasks.maintenance_tasks.*': {'queue': 'maintenance'},
}
```

### 2. 环境变量（`.env` 文件）

```bash
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0  # 缓存使用 DB 0
REDIS_PASSWORD=  # 如有密码请填写

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Ollama 配置
OLLAMA_API_URL=http://127.0.0.1:11434/api/chat
OLLAMA_MODEL=qwen:7b

# 任务配置
CELERY_MAX_RETRIES=3
CELERY_RETRY_DELAY=60
TASK_TIME_LIMIT=600  # 10 分钟超时
```

---

## 🚀 启动服务

### 方式 1：使用 PowerShell 脚本（推荐）

```powershell
cd 1-后端代码
.\start_celery.ps1
```

该脚本会自动打开 3 个终端窗口：
1. **Celery Worker**: 处理异步任务
2. **Celery Beat**: 定时任务调度器
3. **Flower**: Web 监控界面

### 方式 2：手动启动

#### 终端 1: 启动 Celery Worker
```bash
cd 1-后端代码
celery -A celery_app worker --loglevel=info --pool=solo -Q photo,ai,report,maintenance
```

#### 终端 2: 启动 Celery Beat（定时任务）
```bash
cd 1-后端代码
celery -A celery_app beat --loglevel=info
```

#### 终端 3: 启动 Flower（监控界面）
```bash
cd 1-后端代码
celery -A celery_app flower --port=5555
```

---

## 🧪 验证安装

### 1. 检查 Redis 连接
```bash
redis-cli ping
# 应返回: PONG
```

### 2. 检查 Celery Worker
```bash
celery -A celery_app inspect active
# 应显示活跃 Worker 列表
```

### 3. 运行测试脚本
```bash
python test_celery_tasks.py
```

### 4. 访问 Flower 监控
打开浏览器访问: http://127.0.0.1:5555

---

## 📊 任务队列说明

| 队列名称 | 用途 | 优先级 | 并发数 |
|---------|------|--------|--------|
| `photo` | 照片处理（压缩、缩略图） | 高 | 4 |
| `ai` | AI 质量检查 | 中 | 2 |
| `report` | 报告导出 | 低 | 2 |
| `maintenance` | 系统维护（定时任务） | 低 | 1 |

---

## 🔄 定时任务配置

在 `celery_app.py` 中配置了 2 个定时任务：

```python
beat_schedule = {
    # 每天凌晨 2 点清理过期缓存
    'cleanup-expired-cache': {
        'task': 'tasks.maintenance_tasks.cleanup_expired_cache',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # 每小时健康检查
    'health-check': {
        'task': 'tasks.maintenance_tasks.health_check',
        'schedule': crontab(minute=0),
    },
}
```

---

## 🛠️ 开发调试

### 查看 Worker 日志
```bash
# Worker 日志级别
celery -A celery_app worker --loglevel=debug

# 只显示特定队列
celery -A celery_app worker -Q photo --loglevel=info
```

### 查看任务详情
```bash
# 查看活跃任务
celery -A celery_app inspect active

# 查看注册的任务
celery -A celery_app inspect registered

# 查看队列状态
celery -A celery_app inspect stats
```

### 手动执行任务
```python
from tasks import compress_photo

# 异步执行
result = compress_photo.delay('photos/test.jpg', quality=85)

# 同步执行（阻塞等待）
result = compress_photo.apply(args=['photos/test.jpg'], kwargs={'quality': 85})
```

---

## 🐛 常见问题

### 1. Worker 无法连接到 Redis
**问题**: `[ERROR] Consumer: Cannot connect to redis://localhost:6379/1`

**解决**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查端口占用
netstat -ano | findstr :6379

# 重启 Redis
docker restart redis-celery
```

### 2. AI 任务失败
**问题**: `[ERROR] Ollama API connection failed`

**解决**:
```bash
# 检查 Ollama 服务
curl http://127.0.0.1:11434/api/tags

# 启动 Ollama
ollama serve

# 验证模型
ollama list | findstr qwen
```

### 3. 任务一直 PENDING
**问题**: 任务提交后状态一直是 `PENDING`

**解决**:
- 检查 Worker 是否运行
- 确认队列名称正确
- 查看 Worker 日志是否有错误

### 4. 内存占用过高
**问题**: Worker 内存持续增长

**解决**:
```python
# 在 celery_app.py 中设置
worker_max_tasks_per_child = 1000  # Worker 处理 1000 个任务后重启
```

---

## 📈 性能优化

### 1. 调整 Worker 并发数
```bash
# 基于 CPU 核心数
celery -A celery_app worker --concurrency=8

# 使用 eventlet/gevent（IO 密集型）
pip install eventlet
celery -A celery_app worker --pool=eventlet --concurrency=100
```

### 2. 启用结果压缩
```python
# celery_app.py
result_compression = 'gzip'
```

### 3. 设置任务过期时间
```python
# celery_app.py
result_expires = 3600  # 结果保留 1 小时
```

---

## 🔒 生产环境建议

### 1. 使用 Supervisor 管理进程
```ini
; /etc/supervisor/conf.d/celery.conf
[program:celery-worker]
command=/path/to/venv/bin/celery -A celery_app worker --loglevel=info
directory=/path/to/project
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery-beat]
command=/path/to/venv/bin/celery -A celery_app beat --loglevel=info
directory=/path/to/project
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

### 2. 使用 Redis Sentinel（高可用）
```python
# celery_app.py
broker_url = "sentinel://localhost:26379;sentinel://localhost:26380"
broker_transport_options = {
    'master_name': 'mymaster',
}
```

### 3. 启用任务监控
```bash
# 启动 Prometheus 监控
celery -A celery_app worker --loglevel=info -O fair
```

---

## 📚 参考资料

- [Celery 官方文档](https://docs.celeryq.dev/)
- [Redis 官方文档](https://redis.io/documentation)
- [Flower 监控指南](https://flower.readthedocs.io/)
- [Ollama API 文档](https://github.com/ollama/ollama/blob/main/docs/api.md)

---

## 📞 技术支持

遇到问题？请查看：
- `logs/celery_worker.log` - Worker 日志
- `logs/celery_beat.log` - Beat 调度器日志
- Flower 监控界面: http://127.0.0.1:5555

---

**文档版本**: 1.0  
**最后更新**: 2025-01-21  
**适用版本**: Celery 5.6.0 + Redis 7.x
