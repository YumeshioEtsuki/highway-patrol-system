# Redis 缓存系统设置指南

## 概述
本项目已集成 Redis 缓存以提高性能。Redis 用于：
1. **请求缓存**：缓存频繁查询的统计数据、列表数据（TTL: 5-10分钟）
2. **Celery 任务队列代理**：异步任务调度和结果存储
3. **会话存储**（可选）：JWT token 黑名单

## Windows 上启动 Redis

### 方法 1: 使用 Docker（推荐）
```bash
# 拉取官方 Redis 镜像
docker pull redis:latest

# 启动 Redis 容器（默认端口 6379，无密码）
docker run -d --name redis-server -p 6379:6379 redis:latest

# 验证连接
docker exec redis-server redis-cli ping
# 应输出: PONG

# 停止 Redis
docker stop redis-server
docker rm redis-server
```

### 方法 2: 使用 WSL 2 (Windows Subsystem for Linux)
```bash
# 1. 确保已安装 WSL 2
# 在 PowerShell 中：
wsl --install

# 2. 在 WSL 终端中安装 Redis
sudo apt update
sudo apt install redis-server -y

# 3. 启动 Redis
redis-server

# 4. 在另一个 WSL 终端验证
redis-cli ping
```

### 方法 3: 使用 Memurai (Windows 原生 Redis)
```bash
# 访问: https://github.com/microsoftarchive/memurai-releases/releases
# 下载最新版本，安装后自动作为 Windows 服务运行

# 验证服务
redis-cli ping
```

### 方法 4: 使用 chocolatey
```powershell
# 安装 Chocolatey（管理员 PowerShell）
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装 Redis
choco install redis-64 -y

# 启动 Redis 服务
redis-server

# 验证
redis-cli ping
```

## 验证 Redis 运行

### 使用 redis-cli
```bash
redis-cli
> PING
PONG
> CONFIG GET port
> exit
```

### 使用 Python
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # 应输出: True
```

## 配置文件 (.env)

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=          # 留空表示无密码

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## 缓存策略

### 当前缓存的端点
| 端点 | TTL | 前缀 | 说明 |
|------|-----|------|------|
| `/api/admin/stats` | 600s (10分钟) | `admin:stats` | 管理员统计看板 |
| `/api/admin/patrol/list` | 300s (5分钟) | `admin:patrol:list` | 管理员巡查列表 |
| `/api/export/excel` | 600s (10分钟) | `admin:export:excel` | Excel 导出 |
| `/api/patrol` | 300s (5分钟) | `patrol:list` | 巡查员列表 |

### 缓存失效
数据修改时自动清除相关缓存：
- 创建新巡查记录 → 清除 `patrol:list:*` 和 `admin:*`
- 标记为处理中 → 清除 `admin:patrol:list:*` 和 `admin:stats:*`
- 标记为完成 → 清除 `admin:patrol:list:*` 和 `admin:stats:*`

## 故障排查

### 连接拒绝错误
```
redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379
```
**解决**：确保 Redis 服务正在运行
```bash
# 启动 Redis 服务
redis-server

# 或使用 Docker
docker run -d --name redis-server -p 6379:6379 redis:latest
```

### 密码认证失败
如果 Redis 配置了密码，更新 `.env`：
```env
REDIS_PASSWORD=your_password
```

### 缓存未生效
1. 检查 Redis 是否正在运行
2. 查看日志中的 Redis 连接消息
3. 验证 `utils/redis_client.py` 中的连接配置

## 监控 Redis

### 实时监控
```bash
redis-cli
> MONITOR    # 监控所有命令
> KEYS *     # 查看所有 key
> DBSIZE     # 查看 key 数量
> FLUSHDB    # 清空当前数据库
```

### 性能统计
```bash
redis-cli INFO stats
```

## 与 Celery 的集成

Celery 使用 Redis 作为消息代理和结果后端：
- **Broker DB**: `redis://localhost:6379/1` - 任务队列
- **Result Backend**: `redis://localhost:6379/2` - 任务结果存储
- **Main Cache DB**: `redis://localhost:6379/0` - 请求缓存

每个组件使用不同的数据库编号避免冲突。

## 下一步
1. 启动 Redis 服务
2. 运行后端：`python start_server.py`
3. 访问 `/docs` 测试缓存端点
4. 查看日志验证缓存命中情况

