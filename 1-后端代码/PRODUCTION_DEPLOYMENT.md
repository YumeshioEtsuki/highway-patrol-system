# 生产环境 Redis 部署指南

## 概述
本指南面向在生产环境中部署公路巡查系统的运维人员。

---

## 📦 部署方案对比

| 方案 | 难度 | 性能 | 可维护性 | 推荐场景 |
|------|------|------|---------|---------|
| **Docker Compose** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **推荐** |
| **Kubernetes** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 大规模部署 |
| **AWS ElastiCache** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 云环境 |
| **Azure Cache for Redis** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Azure 用户 |
| **Aliyun Redis** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 国内部署 |

---

## 🐳 方案 1: Docker Compose（推荐）

### 1.1 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: highway-patrol-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    restart: unless-stopped
    networks:
      - patrol-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./1-后端代码
      dockerfile: Dockerfile
    container_name: highway-patrol-backend
    ports:
      - "5000:5000"
    environment:
      DATABASE_HOST: db
      REDIS_HOST: redis
      REDIS_PORT: 6379
      SKIP_DB_INIT: "0"
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - patrol-network
    volumes:
      - ./1-后端代码/photos:/app/photos
      - ./1-后端代码/logs:/app/logs

volumes:
  redis_data:
    driver: local

networks:
  patrol-network:
    driver: bridge
```

### 1.2 创建 redis.conf

```ini
# Redis 生产配置

# 网络
bind 0.0.0.0
port 6379
timeout 0
tcp-backlog 511
tcp-keepalive 300

# 内存管理
maxmemory 512mb
maxmemory-policy allkeys-lru

# 数据持久化
save 900 1          # 15分钟内至少1个key变化
save 300 10         # 5分钟内至少10个key变化
save 60 10000       # 1分钟内至少10000个key变化

dbfilename dump.rdb
dir /data

# 安全
requirepass REDACTED  # 必须修改！

# 日志
loglevel notice
logfile /data/redis.log

# 性能
databases 16
slowlog-log-slower-than 10000
slowlog-max-len 128

# Lua 脚本
lua-time-limit 5000

# 客户端输出缓冲限制
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# HZ
hz 10
dynamic-hz yes
```

### 1.3 启动服务

```bash
# 启动 Redis
docker-compose up -d redis

# 验证 Redis 运行
docker-compose exec redis redis-cli ping
# 输出: PONG

# 查看日志
docker-compose logs -f redis

# 启动完整堆栈
docker-compose up -d
```

### 1.4 备份和恢复

```bash
# 备份数据
docker-compose exec redis redis-cli BGSAVE

# 查看备份位置
docker-compose exec redis ls -la /data/dump.rdb

# 恢复数据
# 1. 停止 Redis
docker-compose stop redis

# 2. 恢复 dump.rdb 文件到 redis_data 卷

# 3. 启动 Redis
docker-compose start redis
```

---

## ☁️ 方案 2: 云托管服务

### 2.1 AWS ElastiCache

```bash
# 1. 创建 Redis 集群（AWS CLI）
aws elasticache create-cache-cluster \
  --cache-cluster-id highway-patrol-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --port 6379

# 2. 获取端点
aws elasticache describe-cache-clusters \
  --cache-cluster-id highway-patrol-cache \
  --show-cache-node-info

# 3. 更新 .env
REDIS_HOST=highway-patrol-cache.xxx.ng.0001.aps1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=your_auth_token
```

### 2.2 Azure Cache for Redis

```bash
# 1. 创建资源（Azure CLI）
az redis create \
  --resource-group myResourceGroup \
  --name highway-patrol-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0

# 2. 获取连接字符串
az redis list-keys \
  --resource-group myResourceGroup \
  --name highway-patrol-cache

# 3. 更新 .env
REDIS_HOST=highway-patrol-cache.redis.cache.windows.net
REDIS_PORT=6379
REDIS_PASSWORD=<primary_key>
```

### 2.3 Aliyun Redis

```bash
# 1. 在控制台创建实例
# 选择: 内存型 (Memory) → 1GB

# 2. 获取端点和密码
# r-xxxx.redis.aliyuncs.com:6379

# 3. 更新 .env
REDIS_HOST=r-xxxx.redis.aliyuncs.com
REDIS_PORT=6379
REDIS_PASSWORD=your_password
```

---

## 🔒 安全配置

### 3.1 密码保护

```ini
# redis.conf
requirepass very_strong_password_123456!@#
```

### 3.2 网络隔离

```yaml
# docker-compose.yml
networks:
  patrol-network:
    driver: bridge
    
services:
  redis:
    networks:
      - patrol-network
    # 不暴露端口到外网
```

### 3.3 防火墙规则

```bash
# 仅允许应用服务器访问 Redis
sudo ufw allow from 192.168.1.100 to any port 6379

# 或在云环境中配置安全组
# AWS: 入站规则 → TCP 6379 → 来源：应用服务器 IP
```

### 3.4 SSL/TLS 支持

```yaml
# docker-compose.yml（Redis 6.0+）
command: redis-server --tls-port 6379 --port 0 --tls-cert-file /certs/redis.crt --tls-key-file /certs/redis.key
```

---

## 📊 监控和告警

### 4.1 Prometheus 监控

```yaml
# docker-compose.yml 新增
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

redis-exporter:
  image: oliver006/redis_exporter
  ports:
    - "9121:9121"
  environment:
    REDIS_ADDR: redis://redis:6379
```

### 4.2 告警规则

```yaml
# prometheus.yml
alert_rules_files:
  - /etc/prometheus/rules.yml

# rules.yml
groups:
  - name: redis
    rules:
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        annotations:
          summary: "Redis 不可用"
      
      - alert: RedisHighMemoryUsage
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        annotations:
          summary: "Redis 内存使用率 > 80%"
      
      - alert: RedisHighKeyEvictions
        expr: increase(redis_evicted_keys_total[5m]) > 1000
        annotations:
          summary: "Redis 驱逐了过多键（5分钟）"
```

### 4.3 ELK 日志分析

```yaml
# docker-compose.yml 新增
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  ports:
    - "9200:9200"
  environment:
    discovery.type: single-node

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  ports:
    - "9600:9600"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

---

## 🔄 高可用配置

### 5.1 Redis Sentinel（主从 + 自动故障转移）

```yaml
version: '3.8'

services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --port 6379 --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_master:/data

  redis-slave:
    image: redis:7-alpine
    command: redis-server --port 6380 --slaveof redis-master 6379
    ports:
      - "6380:6380"
    volumes:
      - redis_slave:/data
    depends_on:
      - redis-master

  sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/sentinel.conf --port 26379
    ports:
      - "26379:26379"
    volumes:
      - ./sentinel.conf:/etc/sentinel.conf
    depends_on:
      - redis-master

volumes:
  redis_master:
  redis_slave:
```

### 5.2 Redis Cluster（分布式）

```bash
# 创建 Redis Cluster（6 个节点）
docker run -d --name redis-cluster redis:7-alpine redis-server --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes

# 初始化集群
redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 127.0.0.1:6382 127.0.0.1:6383 127.0.0.1:6384 --cluster-replicas 1
```

---

## 📈 性能优化

### 6.1 内存优化

```ini
# redis.conf
# 启用内存压缩
activedefrag yes
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100

# 启用节省内存的数据结构
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-compress-depth 0
set-max-intset-entries 512
```

### 6.2 慢查询日志

```bash
# 在 redis-cli 中
CONFIG SET slowlog-log-slower-than 10000  # 10ms
CONFIG SET slowlog-max-len 128

# 查看慢查询
SLOWLOG GET 10
```

### 6.3 持久化策略

```ini
# AOF（快速恢复，更安全）
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no

# RDB（快速备份，较少写入）
save 900 1
save 300 10
save 60 10000
```

---

## ✅ 生产检查清单

- [ ] Redis 版本 ≥ 6.0
- [ ] 配置强密码
- [ ] 启用数据持久化（RDB 或 AOF）
- [ ] 配置防火墙
- [ ] 配置监控告警
- [ ] 定期备份
- [ ] 内存上限和淘汰策略
- [ ] 日志级别设为 notice
- [ ] 禁用危险命令（FLUSHDB, FLUSHALL）
- [ ] 配置高可用（Sentinel 或 Cluster）
- [ ] 负载测试验证
- [ ] 灾难恢复计划

---

## 🚨 故障恢复

### 7.1 Redis 宕机恢复

```bash
# 1. 检查 Redis 状态
docker-compose ps

# 2. 查看错误日志
docker-compose logs redis

# 3. 重启 Redis
docker-compose restart redis

# 4. 验证恢复
docker-compose exec redis redis-cli ping
```

### 7.2 内存溢出处理

```bash
# 1. 检查内存使用
redis-cli INFO memory

# 2. 清理过期键
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "expired:*"

# 3. 重新配置内存上限
redis-cli CONFIG SET maxmemory 1gb
```

### 7.3 数据恢复

```bash
# 1. 从备份恢复
cp /backup/dump.rdb /data/

# 2. 重启 Redis
docker-compose restart redis

# 3. 验证数据
redis-cli DBSIZE
```

---

## 📚 参考资源

- [Redis 官方文档](https://redis.io/documentation)
- [Redis 生产建议](https://redis.io/topics/sentinel)
- [Docker Redis 镜像](https://hub.docker.com/_/redis)

---

**最后更新：2025-12-24**

