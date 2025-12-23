# 📚 Redis 缓存系统文档索引

## 🎯 快速导航

### 我想...

#### 快速启动 Redis？
→ [5分钟快速开始](./REDIS_QUICK_START.md)
```bash
docker run -d -p 6379:6379 redis:latest
python start_server.py
python test_redis_cache.py
```

#### 完整了解 Redis 部署？
→ [完整部署指南](./REDIS_SETUP.md)
- Windows 4 种安装方法
- Docker 部署
- 连接验证
- 故障排查

#### 在生产环境部署？
→ [生产部署指南](./PRODUCTION_DEPLOYMENT.md)
- Docker Compose 完整配置
- 云平台（AWS/Azure/Aliyun）
- 高可用配置（Sentinel/Cluster）
- 监控告警

#### 理解技术细节？
→ [完整技术报告](../PHASE_1_STEP_1_REPORT.md)
- 架构设计
- 性能数据
- 文件清单

#### 看完成情况总结？
→ [完成总结](./COMPLETION_SUMMARY.md)
- 交付成果
- 性能改进
- 下一步计划

#### 测试缓存功能？
→ [测试脚本使用](./test_redis_cache.py)
```bash
python test_redis_cache.py
```

#### 为项目添加缓存？
→ [API 使用示例](#api-使用示例)

---

## 📖 文档清单

| 文档 | 目的 | 难度 | 所需时间 |
|------|------|------|---------|
| [REDIS_QUICK_START.md](./REDIS_QUICK_START.md) | 快速上手 | ⭐ | 5分钟 |
| [REDIS_SETUP.md](./REDIS_SETUP.md) | 完整部署 | ⭐⭐ | 15分钟 |
| [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) | 生产级部署 | ⭐⭐⭐ | 30分钟 |
| [PHASE_1_STEP_1_REPORT.md](../PHASE_1_STEP_1_REPORT.md) | 技术细节 | ⭐⭐⭐ | 20分钟 |
| [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md) | 项目总结 | ⭐⭐ | 10分钟 |

---

## 🚀 常用命令速查

### Redis 连接验证
```bash
# 检查 Redis 服务是否运行
redis-cli ping
# 输出: PONG

# 查看 Redis 信息
redis-cli INFO server

# 监控实时命令
redis-cli MONITOR
```

### 查看缓存数据
```bash
# 查看所有缓存键
redis-cli KEYS "*"

# 查看特定前缀的缓存
redis-cli KEYS "admin:*"
redis-cli KEYS "patrol:*"

# 查看缓存内容
redis-cli GET admin:stats:abc123

# 查看缓存过期时间
redis-cli TTL admin:stats:abc123

# 查看总缓存数量
redis-cli DBSIZE
```

### 缓存管理
```bash
# 清除单个缓存
redis-cli DEL admin:stats:abc123

# 清除所有匹配的缓存
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "admin:*"

# 清除所有缓存
redis-cli FLUSHDB

# 查看内存使用
redis-cli INFO memory
```

---

## 🔧 API 使用示例

### 为路由添加缓存

#### 步骤 1：导入缓存装饰器
```python
from utils.cache import cache_response, invalidate_cache
```

#### 步骤 2：添加装饰器
```python
@router.get("/api/my-endpoint")
@cache_response(ttl=600, key_prefix="my:endpoint")
async def my_endpoint(param1: str, param2: int):
    # 业务逻辑
    return {"data": "result"}
```

#### 步骤 3：在修改操作中清除缓存
```python
@router.post("/api/my-data")
async def create_data(data: MySchema):
    # 创建数据
    record = save_data(data)
    
    # 清除相关缓存
    await invalidate_cache("my:endpoint:*")
    
    return record
```

### 自定义缓存策略
```python
# 不同 TTL
@cache_response(ttl=300, key_prefix="quick")      # 5分钟
@cache_response(ttl=3600, key_prefix="normal")    # 1小时
@cache_response(ttl=86400, key_prefix="long")     # 1天

# 禁用缓存
@cache_response(ttl=0)  # 不缓存

# 不使用装饰器（无缓存）
@router.get("/api/realtime")
async def realtime_data():
    return data
```

---

## 📊 性能参考

### 缓存效果对比

| 端点 | 响应时间（无缓存） | 响应时间（有缓存） | 性能提升 |
|------|-----------------|-------------------|---------|
| `/api/admin/stats` | ~500ms | ~20ms | **25x** ⚡ |
| `/api/admin/patrol/list` | ~800ms | ~30ms | **26x** ⚡ |
| `/api/patrol` | ~300ms | ~10ms | **30x** ⚡ |

### 缓存命中率目标
- **统计数据**：75-90%（数据变化不频繁）
- **列表数据**：70-80%（分页查询）
- **导出数据**：80-95%（重复下载）

### 数据库负载减少
```
假设日均 10,000 次 API 请求
缓存命中率 75%：
  - 无缓存：10,000 次 DB 查询
  - 有缓存：2,500 次 DB 查询
  - 减少：75% ✓
```

---

## ⚠️ 常见问题 (FAQ)

### Q: Redis 连接失败怎么办？
**A:** 请参考 [REDIS_SETUP.md - 故障排查](./REDIS_SETUP.md#故障排查) 部分

**快速检查**：
```bash
redis-cli ping
# PONG 表示正常
# 连接拒绝表示 Redis 未运行
```

### Q: 缓存没有生效怎么办？
**A:** 检查以下几点：
1. Redis 是否正在运行：`redis-cli ping`
2. 缓存装饰器是否正确应用：查看源代码
3. 缓存键是否存在：`redis-cli KEYS admin:*`

### Q: 缓存占用内存太多怎么办？
**A:** 参考 [PRODUCTION_DEPLOYMENT.md - 内存优化](./PRODUCTION_DEPLOYMENT.md#61-内存优化)

**快速解决**：
```bash
# 设置最大内存
redis-cli CONFIG SET maxmemory 512mb

# 设置淘汰策略
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Q: 修改数据后列表为什么还是旧的？
**A:** 这是正常的 - 缓存未过期

**解决**：
```bash
# 方法 1：等待 TTL 过期（5-10分钟）
# 方法 2：手动清除缓存
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "admin:*"
# 方法 3：重启后端（全部清除）
```

### Q: 如何监控缓存性能？
**A:** 使用 `redis-cli INFO` 命令
```bash
redis-cli INFO stats | grep "hits\|misses"
# keyspace_hits: 缓存命中次数
# keyspace_misses: 缓存未命中次数
```

---

## 🛠️ 故障排查流程

### 症状：缓存无效

```
1. 验证 Redis 运行
   └─ redis-cli ping
      ├─ 输出 PONG ✓
      └─ 连接失败 → 启动 Redis

2. 检查缓存装饰器
   └─ 查看源代码
      ├─ 已应用 ✓
      └─ 未应用 → 添加 @cache_response

3. 验证缓存数据存在
   └─ redis-cli KEYS pattern
      ├─ 有结果 ✓
      └─ 无结果 → 检查路由逻辑

4. 查看应用日志
   └─ 查看是否有异常
      ├─ 无异常 ✓
      └─ 有异常 → 修复异常
```

### 症状：内存占用过高

```
1. 检查内存使用
   └─ redis-cli INFO memory

2. 查看大键
   └─ redis-cli --bigkeys

3. 调整策略
   ├─ 降低 TTL 值
   ├─ 减少缓存的数据大小
   └─ 设置最大内存限制
```

---

## 📞 支持资源

### 官方文档
- [Redis 官方网站](https://redis.io)
- [Redis 命令参考](https://redis.io/commands)
- [Redis 模块生态](https://redis.io/modules)

### 社区支持
- [Stack Overflow - Redis 标签](https://stackoverflow.com/questions/tagged/redis)
- [Redis 中文网](http://www.redis.cn)
- [Redis 官方论坛](https://github.com/antirez/redis)

### 本项目文档
- 项目总体：[README.md](./README.md)
- 后端指南：[1-后端代码/README.md](./README.md)
- 数据库：[3-数据库/README.md](../3-数据库/README.md)

---

## 🎓 学习路径

### 初学者（想快速启动）
1. 阅读 [REDIS_QUICK_START.md](./REDIS_QUICK_START.md)
2. 运行测试脚本：`python test_redis_cache.py`
3. 在 Swagger 中测试 API

### 中级用户（想深入理解）
1. 阅读 [REDIS_SETUP.md](./REDIS_SETUP.md)
2. 研究源代码：`utils/redis_client.py` 和 `utils/cache.py`
3. 自己为新端点添加缓存

### 高级用户（想生产部署）
1. 研究 [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)
2. 实施高可用配置（Sentinel/Cluster）
3. 部署监控告警系统

---

## 📈 下一步

### 已完成 ✅
- [x] Redis 缓存集成
- [x] 高频端点缓存
- [x] 缓存失效机制
- [x] 完整文档

### 待完成 ⏳
- [ ] Celery 任务队列（Phase 1 Step 2）
- [ ] 数据库监控（Phase 1 Step 3）
- [ ] 审计日志系统（Phase 2）
- [ ] 多角色 RBAC（Phase 2）
- [ ] 实时通知系统（Phase 3）

---

## 🎉 使用建议

1. **开发环境**：使用本地 Redis（Docker）
2. **测试环境**：使用 Docker Compose
3. **生产环境**：使用托管服务（AWS/Azure）或 Sentinel 高可用

---

**最后更新：2025-12-24**  
**版本：v1.0 Production Ready**

