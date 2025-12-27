# Redis Docker 安装和启动指南

## 📦 使用 Docker 运行 Redis（推荐方案）

### 前置条件

安装 Docker Desktop for Windows：
- 下载地址：https://www.docker.com/products/docker-desktop/
- 安装后重启电脑

---

## 🚀 快速启动

### 方式1：使用启动脚本（推荐）

```bash
# Windows
.\bin\start_redis.bat

# 或使用 PowerShell 脚本
.\bin\start_redis.ps1
```

### 方式2：手动命令

```bash
# 启动 Redis 容器（持久化数据）
docker run -d \
  --name highway-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  --restart unless-stopped \
  redis:7-alpine redis-server --appendonly yes

# 查看容器状态
docker ps | findstr redis

# 测试连接
docker exec -it highway-redis redis-cli ping
# 预期输出: PONG
```

---

## 🛠️ 常用命令

### 容器管理

```bash
# 启动 Redis 容器
docker start highway-redis

# 停止 Redis 容器
docker stop highway-redis

# 重启 Redis 容器
docker restart highway-redis

# 查看日志
docker logs highway-redis

# 查看实时日志
docker logs -f highway-redis

# 删除容器（数据仍保留在 volume 中）
docker rm highway-redis

# 删除数据卷（慎用！会清空所有数据）
docker volume rm redis-data
```

### Redis 操作

```bash
# 进入 Redis CLI
docker exec -it highway-redis redis-cli

# 查看所有键
docker exec -it highway-redis redis-cli KEYS "*"

# 清空所有数据
docker exec -it highway-redis redis-cli FLUSHALL

# 查看内存使用
docker exec -it highway-redis redis-cli INFO memory

# 监控实时命令
docker exec -it highway-redis redis-cli MONITOR
```

---

## ⚙️ 配置说明

### 容器参数解释

```bash
docker run -d \                          # 后台运行
  --name highway-redis \                 # 容器名称
  -p 6379:6379 \                         # 端口映射 (宿主机:容器)
  -v redis-data:/data \                  # 数据持久化
  --restart unless-stopped \              # 自动重启策略
  redis:7-alpine \                       # Redis 7 Alpine 版本（体积小）
  redis-server --appendonly yes          # 开启 AOF 持久化
```

### 自动重启策略

- `no` - 不自动重启（默认）
- `always` - 总是重启
- `unless-stopped` - 除非手动停止，否则总是重启（推荐）
- `on-failure` - 仅在失败时重启

---

## 🔒 安全加固（生产环境）

### 添加密码保护

```bash
# 启动带密码的 Redis
docker run -d \
  --name highway-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  --restart unless-stopped \
  redis:7-alpine redis-server \
    --appendonly yes \
    --requirepass "REDACTED"

# 连接时需要密码
docker exec -it highway-redis redis-cli -a "REDACTED"
```

### 更新 .env 配置

```env
# Redis 连接配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=REDACTED  # 如果设置了密码

# 或使用 URL 格式
REDIS_URL=redis://:REDACTED@localhost:6379/0
```

---

## 📊 性能优化

### 内存限制

```bash
# 限制 Redis 最大使用内存为 256MB
docker run -d \
  --name highway-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  --memory="256m" \
  --restart unless-stopped \
  redis:7-alpine redis-server \
    --appendonly yes \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru
```

### 常用内存淘汰策略

- `noeviction` - 内存满时返回错误（默认）
- `allkeys-lru` - 淘汰最少使用的键（推荐）
- `volatile-lru` - 仅淘汰设置了过期时间的键
- `allkeys-random` - 随机淘汰键
- `volatile-ttl` - 淘汰即将过期的键

---

## 🔍 故障排查

### 问题1：端口已被占用

```bash
# 查找占用 6379 的进程
netstat -ano | findstr :6379

# 停止冲突的容器
docker stop $(docker ps -q --filter "publish=6379")

# 或使用其他端口
docker run -d --name highway-redis -p 6380:6379 redis:7-alpine
```

### 问题2：容器无法启动

```bash
# 查看容器日志
docker logs highway-redis

# 检查容器状态
docker ps -a | findstr redis

# 强制删除并重建
docker rm -f highway-redis
docker run -d --name highway-redis -p 6379:6379 redis:7-alpine
```

### 问题3：数据丢失

```bash
# 检查数据卷是否存在
docker volume ls | findstr redis

# 检查数据卷详情
docker volume inspect redis-data

# 备份数据卷
docker run --rm -v redis-data:/data -v ${PWD}:/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

---

## 📈 监控

### Docker Stats

```bash
# 查看容器资源使用
docker stats highway-redis

# 输出示例：
# CONTAINER ID   NAME            CPU %   MEM USAGE / LIMIT   NET I/O
# abc123         highway-redis   0.5%    15MB / 256MB        1.2kB / 850B
```

### Redis Info

```bash
# 完整信息
docker exec highway-redis redis-cli INFO

# 仅查看内存
docker exec highway-redis redis-cli INFO memory

# 仅查看统计
docker exec highway-redis redis-cli INFO stats
```

---

## 🔄 数据迁移

### 从现有 Redis 迁移到 Docker

```bash
# 1. 导出现有数据（如果有）
redis-cli --rdb dump.rdb

# 2. 复制到容器
docker cp dump.rdb highway-redis:/data/

# 3. 重启容器加载数据
docker restart highway-redis
```

### 数据备份

```bash
# 触发 RDB 快照
docker exec highway-redis redis-cli BGSAVE

# 导出备份文件
docker cp highway-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

---

## 🌐 Docker Compose（可选）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: highway-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis-data:
    driver: local
```

启动：
```bash
docker-compose up -d
```

---

## ✅ 验证安装

### 1. 容器运行检查

```bash
docker ps | findstr redis
# 应该看到 STATUS 为 "Up X minutes"
```

### 2. 连接测试

```bash
docker exec -it highway-redis redis-cli ping
# 预期输出: PONG
```

### 3. Python 连接测试

```python
# 测试脚本
python -c "import redis; r=redis.Redis(host='localhost', port=6379); print(r.ping())"
# 预期输出: True
```

### 4. 完整功能测试

```python
import redis

# 连接
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 设置值
r.set('test_key', 'Hello Redis in Docker!')

# 获取值
value = r.get('test_key')
print(f"Value: {value}")

# 删除键
r.delete('test_key')

print("✅ Redis 连接测试成功！")
```

---

## 📚 相关资源

- [Docker Hub - Redis](https://hub.docker.com/_/redis)
- [Redis 官方文档](https://redis.io/docs/)
- [Docker Desktop 文档](https://docs.docker.com/desktop/)
- [本项目 Redis 使用说明](../4-文档/功能说明/REDIS_CELERY说明.md)

---

**最后更新：** 2025-12-26  
**推荐镜像：** `redis:7-alpine` (约 30MB)
