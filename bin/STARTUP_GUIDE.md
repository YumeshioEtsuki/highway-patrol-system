# 高速公路巡查系统 - 一键启动指南

## 🚀 一键启动方式

### 方式1：完整启动（推荐）

**启动 Redis + Celery + FastAPI 三件套**

```bash
# Windows
.\bin\startup_full.bat

# 功能包括：
# ✅ Redis 缓存服务（端口 6379）
# ✅ Celery 异步任务队列
# ✅ FastAPI 后端服务（端口 5000）
```

### 方式2：仅启动 FastAPI

**适合只需要基础功能的场景**

```bash
# Windows
.\bin\startup.bat

# 功能包括：
# ✅ FastAPI 后端服务（端口 5000）
# ⚠️ Redis 和 Celery 不启动（异步功能降级）
```

### 安全模式（SECURE_MODE）

**在生产/CI环境，建议启用安全模式：不读取任何 `.env` 文件，仅使用系统环境变量。**

```bash
# 启用安全模式并设置数据库密码（两者其一即可）
set SECURE_MODE=1
set DB_PASSWORD=your_password
rem 或：set DATABASE_PASSWORD=your_password

# 启动（任选其一）
.\bin\startup_full.bat
.\bin\startup.bat
```

关闭安全模式回到 `.env` 模式：

```bash
set SECURE_MODE=0
.\bin\startup_full.bat
```

### 停止所有服务

```bash
# Windows
.\bin\stop_all.bat

# 将停止：
# - FastAPI 服务器
# - Celery Worker
# - Redis Server
```

---

## 📦 环境依赖

### 1. Redis 安装（必需 - 用于缓存和消息队列）

#### 🐳 方式A：Docker（强烈推荐）✨

**优势：** 一键安装、自动更新、数据持久化、跨平台

```bash
# 1. 安装 Docker Desktop
# 下载: https://www.docker.com/products/docker-desktop/
# 详细教程: .\bin\DOCKER_INSTALL_GUIDE.md

# 2. 启动 Redis（自动创建容器）
.\bin\start_redis.bat

# 或使用 PowerShell
.\bin\start_redis.ps1

# 3. 验证
docker exec -it highway-redis redis-cli ping
# 预期输出: PONG
```

**Docker Redis 特点：**
- ✅ 自动持久化数据（AOF）
- ✅ 开机自动启动
- ✅ 资源隔离，不影响系统
- ✅ 一键启动/停止/重启
- ✅ 完整文档：[REDIS_DOCKER_GUIDE.md](REDIS_DOCKER_GUIDE.md)

#### Windows 安装方式

**方式A：使用预编译版本（推荐）**
```bash
# 1. 下载 Redis for Windows
# https://github.com/microsoftarchive/redis/releases
# 下载 Redis-x64-5.0.14.1.zip

# 2. 解压到 C:\Redis

# 3. 添加到系统环境变量 PATH
C:\Redis

# 4. 测试安装
redis-server --version
```

**方式B：使用 WSL2 + Ubuntu**
```bash
# 在 WSL2 Ubuntu 中安装
sudo apt update
sudo apt install redis-server

# 启动 Redis
redis-server --daemonize yes

# 测试连接
redis-cli ping
```

**方式C：使用 Docker**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

#### 验证 Redis 安装
```bash
# 检查 Redis 是否在运行
redis-cli ping
# 预期输出: PONG
```

### 2. Python 依赖

```bash
# 已在 requirements.txt 中包含
pip install redis celery
```

---

## ⚙️ 手动启动（适合调试）

### 步骤1：启动 Redis

```bash
# Windows（前台运行）
redis-server --port 6379

# Windows（后台运行）
start /MIN redis-server --port 6379

# WSL2/Linux
redis-server --daemonize yes
```

### 步骤2：启动 Celery Worker

```bash
# Windows（必须使用 --pool=solo）
celery -A celery_app worker --loglevel=info --pool=solo

# Linux/Mac
celery -A celery_app worker --loglevel=info
```

**可选：启动 Celery Beat（定时任务）**
```bash
celery -A celery_app beat --loglevel=info
```

### 步骤3：启动 FastAPI

```bash
# 开发模式（自动重载）
uvicorn app:app --reload --host 0.0.0.0 --port 5000

# 生产模式
uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4
```

---

## 🔍 服务检查

### 检查 Redis 连接

```bash
# 命令行检查
redis-cli
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> exit

# Python 检查
python -c "import redis; r=redis.Redis(host='localhost', port=6379); print(r.ping())"
```

### 检查 Celery Worker

```bash
# 查看 Worker 状态
celery -A celery_app inspect active

# 查看已注册的任务
celery -A celery_app inspect registered
```

### 检查 FastAPI

```bash
# 浏览器访问
http://localhost:5000/docs        # Swagger UI
http://localhost:5000/redoc       # ReDoc

# 命令行检查
curl http://localhost:5000/health
```

---

## 📊 监控工具

### Celery 监控（Flower）

```bash
# 安装 Flower
pip install flower

# 启动监控面板
celery -A celery_app flower --port=5555

# 访问
http://localhost:5555
```

### Redis 监控

```bash
# 实时监控命令
redis-cli monitor

# 查看内存使用
redis-cli INFO memory

# 查看所有键
redis-cli KEYS "*"
```

---

## ❗ 常见问题

### 问题1：Redis 连接失败

**错误信息：**
```
[WARN] Redis 连接失败: ConnectionRefusedError
```

**解决方案：**
```bash
# 1. 检查 Redis 是否运行
tasklist | findstr redis-server

# 2. 手动启动 Redis
redis-server --port 6379

# 3. 检查防火墙是否阻止 6379 端口
```

### 问题2：Celery Worker 启动失败

**错误信息（Windows）：**
```
ValueError: not enough values to unpack
```

**解决方案：**
```bash
# Windows 必须使用 --pool=solo
celery -A celery_app worker --loglevel=info --pool=solo
```

### 问题3：端口 5000 被占用

**解决方案：**
```bash
# Windows 查找占用进程
netstat -ano | findstr :5000

# 停止进程（替换 PID）
taskkill /PID <PID> /F

# 或使用其他端口
uvicorn app:app --port 5001
```

### 问题4：Celery 找不到 celery_app

**错误信息：**
```
ModuleNotFoundError: No module named 'celery_app'
```

**解决方案：**
```bash
# 确保在 1-后端代码 目录下运行
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"

# 检查 celery_app.py 是否存在
dir celery_app.py
```

---

## 🎯 推荐启动顺序

### 开发环境
```
1. Redis Server（后台）
2. Celery Worker（独立窗口）
3. Celery Beat（可选，独立窗口）
4. FastAPI（当前窗口，带热重载）
```

### 生产环境
```
1. Redis Server（systemd/守护进程）
2. Celery Worker（supervisor/守护进程，多Worker）
3. Celery Beat（supervisor/守护进程）
4. FastAPI（gunicorn + uvicorn workers）
```

---

## 📚 相关文档

- [Redis与Celery功能说明](../4-文档/功能说明/REDIS_CELERY说明.md)
- [后端部署指南](../4-文档/核心文档/DEPLOYMENT.md)
- [API接口文档](../4-文档/核心文档/API接口文档.md)

---

**最后更新：** 2025-12-26  
**脚本位置：** `bin/startup_full.bat` `bin/stop_all.bat`
