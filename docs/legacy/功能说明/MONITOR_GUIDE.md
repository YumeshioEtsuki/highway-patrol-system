# Phase 1 Step 3 - 数据库监控系统使用指南

## 📍 快速开始

### 1. 启动所有服务

```bash
# 在 1-后端代码 目录下

# 方式 1: 使用 PowerShell 脚本（推荐）
.\start_celery.ps1    # 启动 Celery Worker + Beat

# 在另一个终端启动后端
python app.py

# 方式 2: 手动启动（Windows）
# 终端 1 - 后端
set SKIP_DB_INIT=1
uvicorn app:app --host 0.0.0.0 --port 5000

# 终端 2 - Celery Worker
celery -A celery_app worker -l info

# 终端 3 - Celery Beat (定时任务)
celery -A celery_app beat -l info
```

### 2. 访问仪表板

打开浏览器访问：
```
http://127.0.0.1:5000/monitor
```

## 🎯 核心功能

### A. 实时性能指标

**访问地址：** `http://127.0.0.1:5000/monitor`

仪表板显示 6 个关键指标：
- 📊 **查询速率** - 每秒查询数 (QPS)
- 🔴 **慢查询** - 每分钟慢查询数
- 🔗 **活跃连接** - 当前数据库连接数
- ⏱️ **查询延迟** - 平均查询时间 (毫秒)
- 💾 **缓存命中率** - Redis 缓存效率
- 🔒 **锁等待时间** - 并发冲突指标

### B. 性能趋势图表

4 个实时更新的图表：
1. **查询速率趋势** - 显示 QPS 变化
2. **查询延迟趋势** - 显示平均响应时间
3. **缓存命中率趋势** - 显示缓存效率
4. **活跃连接趋势** - 显示并发情况

数据自动每 30 秒刷新一次。

### C. 慢查询分析

**Top 5 最耗时查询**
- 显示具体 SQL 语句
- 执行耗时（毫秒）
- 扫描行数和返回行数
- 执行时间

点击查询可以看到完整的 SQL 文本。

### D. 索引健康评估

**索引健康评分**
- 总索引数
- 健康索引数
- 整体健康分数 (0-100)

**未使用的索引列表**
- 可以安全删除
- 释放存储空间

### E. 自动优化建议

**优化建议类型：**

| 优先级 | 类型 | 描述 |
|------|------|------|
| 🔴 HIGH | 索引 | 为高频查询添加缺失索引 |
| 🔴 HIGH | 索引 | 删除未使用的索引 |
| 🟡 MEDIUM | 缓存 | 为高频查询启用缓存 |
| 🟡 MEDIUM | 连接 | 调整连接池大小 |
| 🟢 LOW | 其他 | 其他优化建议 |

**操作：**
- 🔄 **应用建议** - 执行优化
- 🚫 **忽略** - 暂时跳过此建议

## 🔌 API 接口

### 身份验证

所有监控 API 都需要：
1. 有效的 JWT token
2. Admin 角色权限

```bash
# 请求头
Authorization: Bearer <your_jwt_token>

# 从登录响应获取 token
POST /api/users/login
{
  "username": "admin",
  "password": "admin_password"
}
```

### API 端点详细说明

#### 1. 获取当前性能指标
```bash
GET /api/admin/monitor/metrics/current

Response:
{
  "status": "success",
  "data": {
    "timestamp": "2024-01-15T10:30:00",
    "queries_per_sec": 45.2,
    "slow_queries_per_min": 3,
    "active_connections": 25,
    "avg_query_time_ms": 125.5,
    "cache_hit_ratio": 0.87,
    "lock_wait_time_ms": 0.5
  }
}
```

#### 2. 获取指标历史
```bash
GET /api/admin/monitor/metrics/history?hours=24

Response:
{
  "status": "success",
  "data": {
    "timestamps": ["2024-01-15T10:00:00", ...],
    "queries_per_sec": [45.2, 46.1, ...],
    "slow_queries_per_min": [3, 5, ...],
    "active_connections": [25, 28, ...],
    ...
  },
  "hours": 24
}
```

#### 3. 获取慢查询列表
```bash
GET /api/admin/monitor/slow-queries?limit=10&offset=0

Response:
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "query": "SELECT * FROM users WHERE ...",
      "duration_ms": 2500,
      "rows_examined": 50000,
      "rows_returned": 100,
      "timestamp": "2024-01-15T10:30:00"
    },
    ...
  ],
  "pagination": {
    "limit": 10,
    "offset": 0
  }
}
```

#### 4. 获取最耗时的查询
```bash
GET /api/admin/monitor/slow-queries/top?limit=5

Response:
{
  "status": "success",
  "data": [
    {
      "query": "...",
      "total_duration": 15000,
      "execution_count": 10,
      "avg_duration": 1500
    },
    ...
  ]
}
```

#### 5. 获取索引健康状态
```bash
GET /api/admin/monitor/indexes/health

Response:
{
  "status": "success",
  "health_summary": {
    "total_indexes": 45,
    "healthy_indexes": 42,
    "health_score": 93.3
  },
  "unused_indexes": [
    {
      "table_name": "users",
      "index_name": "idx_old_field",
      "columns": "old_field"
    },
    ...
  ]
}
```

#### 6. 获取待处理的优化建议
```bash
GET /api/admin/monitor/recommendations

Response:
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "type": "index",
      "priority": "HIGH",
      "description": "考虑为字段 user_id 添加索引",
      "suggested_action": "CREATE INDEX idx_user_id ON users(user_id)",
      "estimated_improvement": 35.0,
      "affected_table": "users"
    },
    ...
  ],
  "count": 5
}
```

#### 7. 生成新的优化建议
```bash
POST /api/admin/monitor/recommendations/generate

Response:
{
  "status": "success",
  "generated": 8,
  "saved": 7
}
```

#### 8. 应用优化建议
```bash
POST /api/admin/monitor/recommendations/{id}/apply

Response:
{
  "status": "success",
  "message": "Recommendation applied"
}
```

#### 9. 忽略优化建议
```bash
POST /api/admin/monitor/recommendations/{id}/dismiss

Response:
{
  "status": "success",
  "message": "Recommendation dismissed"
}
```

#### 10. 系统健康检查
```bash
GET /api/admin/monitor/health-check

Response:
{
  "status": "success",
  "health": {
    "status": "healthy",  // or "warning" / "error"
    "issues": ["High number of slow queries"],
    "metrics": {...},
    "slow_query_stats": {...},
    "index_health": {...}
  }
}
```

## 🛠️ 数据库表结构

### 主要表

#### slow_query_logs - 慢查询日志
```sql
CREATE TABLE slow_query_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    query_hash VARCHAR(64) UNIQUE,        -- 查询哈希值（去重）
    query LONGTEXT,                        -- SQL 语句
    duration_ms FLOAT,                     -- 耗时（毫秒）
    rows_examined INT,                     -- 扫描行数
    rows_returned INT,                     -- 返回行数
    lock_time_ms FLOAT,                    -- 锁等待时间
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,                           -- 执行用户
    endpoint VARCHAR(255),                 -- API 端点
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_duration (duration_ms)
);
```

#### performance_metrics - 性能指标
```sql
CREATE TABLE performance_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    queries_per_sec FLOAT,                 -- 查询速率
    slow_queries_per_min INT,              -- 慢查询数
    active_connections INT,                -- 活跃连接
    avg_query_time_ms FLOAT,               -- 平均查询时间
    cache_hit_ratio FLOAT,                 -- 缓存命中率
    lock_wait_time_ms FLOAT,               -- 锁等待时间
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io_reads INT,
    disk_io_writes INT,
    
    INDEX idx_timestamp (timestamp)
);
```

#### optimization_recommendations - 优化建议
```sql
CREATE TABLE optimization_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50),                      -- 'index', 'query', 'cache'
    priority VARCHAR(20),                  -- 'HIGH', 'MEDIUM', 'LOW'
    description TEXT,                      -- 建议描述
    suggested_action TEXT,                 -- 建议操作
    estimated_improvement FLOAT,           -- 预期提升（%）
    affected_table VARCHAR(255),           -- 受影响的表
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'applied', 'dismissed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    applied_by INT
);
```

## 📊 Celery 定时任务

### 自动执行的任务

```python
# 每分钟收集一次性能指标
"collect-performance-metrics"
  运行频率: 60 秒
  功能: 收集和保存性能指标

# 每 6 小时生成一次优化建议
"generate-optimization-recommendations"
  运行频率: 6 小时
  功能: 分析性能数据并生成优化建议
```

### 查看任务执行

访问 Flower 监控面板：
```
http://127.0.0.1:5555
```

可以看到：
- 所有执行的任务
- 任务执行时间
- 任务成功/失败状态
- Worker 状态

## 🔍 问题诊断

### 常见问题

#### 1. 仪表板页面无法加载

**症状：** 访问 `/monitor` 显示错误

**排查：**
```bash
# 1. 检查服务器是否运行
curl http://127.0.0.1:5000/health

# 2. 检查日志
tail -f logs/app.log

# 3. 确保有有效的 token
# 使用浏览器开发者工具检查 localStorage 中的 token
```

#### 2. API 返回 401 Unauthorized

**症状：** API 请求返回 401

**解决：**
```bash
# 1. 获取新的 token
curl -X POST http://127.0.0.1:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 2. 在请求头中使用 token
Authorization: Bearer <new_token>
```

#### 3. 监控数据为空

**症状：** 仪表板显示 "暂无数据"

**原因：**
- Celery Worker 未运行
- 指标收集任务未执行

**解决：**
```bash
# 1. 检查 Worker 是否运行
celery -A celery_app inspect active

# 2. 手动触发收集任务
python -c "from utils.metrics_collector import MetricsCollector; \
           m = MetricsCollector.collect_current_metrics(); \
           MetricsCollector.save_metrics(m); \
           print('✅ 指标已收集')"
```

#### 4. 性能下降

**症状：** 启用监控后系统变慢

**排查：**
```bash
# 1. 检查 Celery 任务队列
celery -A celery_app inspect reserved

# 2. 检查数据库表大小
SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'road_patrol_db'
ORDER BY size_mb DESC;

# 3. 清理旧数据
python cleanup_monitor_tables.py
```

## 📈 性能优化建议

### 根据不同场景的优化策略

**场景 1: 查询性能差**
- 生成的建议：添加缺失索引
- 预期改进：30-50%
- 实施步骤：
  1. 在优化建议中点击"应用"
  2. 系统自动执行 CREATE INDEX
  3. 验证查询速度改进

**场景 2: 缓存命中率低**
- 生成的建议：启用查询缓存
- 预期改进：20-40%
- 实施步骤：
  1. 识别高频查询
  2. 在应用中添加缓存装饰器
  3. 设置适当的 TTL

**场景 3: 连接数过高**
- 生成的建议：增加连接池或启用连接复用
- 预期改进：15-25%
- 实施步骤：
  1. 调整 `max_connections` 参数
  2. 启用连接复用
  3. 减少长连接

## 🎓 学习资源

- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Celery 文档](https://docs.celeryproject.io)
- [MySQL 性能优化](https://dev.mysql.com/doc/)
- [Chart.js 文档](https://www.chartjs.org/)

## 🚀 下一步

1. **配置告警** - 设置性能告警规则
2. **集成通知** - 邮件/短信预警
3. **高级分析** - 机器学习异常检测
4. **成本优化** - 根据使用量调整资源

---

**上次更新：** 2024 年
**状态：** ✅ 生产就绪
