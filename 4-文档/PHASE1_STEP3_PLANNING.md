# 📊 Phase 1 Step 3: 数据库监控集成 - 详细规划

## 🎯 概述

在完成 Redis 缓存和 Celery 任务队列后，现在实施**数据库性能监控系统**，通过以下功能优化数据库运行效率：

- 慢查询检测和优化
- 索引健康检查
- 实时性能监控
- 自动优化建议

---

## 📋 功能详解

### 1. 慢查询日志系统

**目标**: 自动记录和分析执行时间超过阈值的 SQL 查询

#### 实现方案

```python
# 创建 models/slow_query.py
class SlowQueryLog:
    """慢查询日志模型"""
    id: int
    query: str              # 完整 SQL 语句
    duration_ms: float      # 执行耗时（毫秒）
    rows_examined: int      # 扫描行数
    timestamp: datetime
    
# 创建 utils/slow_query_monitor.py
def log_slow_query(query: str, duration: float, rows: int):
    """
    记录慢查询
    阈值: 默认 1000ms
    """
    if duration > SLOW_QUERY_THRESHOLD:
        # 存入 Redis (快速)
        # 写入 MySQL (异步任务)
        pass
```

**数据存储**:
```sql
CREATE TABLE slow_query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query TEXT NOT NULL,
    duration_ms FLOAT NOT NULL,
    rows_examined INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_duration (duration_ms)
);
```

**API 端点**:
```
GET /api/admin/monitor/slow-queries     # 获取慢查询列表
GET /api/admin/monitor/slow-queries/stats # 慢查询统计
DELETE /api/admin/monitor/slow-queries/{id} # 删除日志
```

---

### 2. 索引健康检查

**目标**: 检测缺失索引、未使用索引、冗余索引

#### 实现方案

```python
# 创建 utils/index_analyzer.py
def analyze_table_indexes(table_name: str):
    """
    分析表索引
    返回：
    - 缺失索引（基于查询模式推荐）
    - 未使用索引
    - 冗余索引
    """
    
def get_missing_indexes():
    """
    分析所有查询，推荐缺失索引
    示例：
    {
        "table": "inspection_records",
        "recommended_index": "INDEX idx_status_user (status, user_id)",
        "estimated_benefit": "45%"
    }
    """
    pass

def get_unused_indexes():
    """
    查找未使用的索引（根据 information_schema）
    """
    pass
```

**API 端点**:
```
GET /api/admin/monitor/indexes/health    # 索引健康状态
GET /api/admin/monitor/indexes/missing   # 推荐添加的索引
GET /api/admin/monitor/indexes/unused    # 可删除的索引
POST /api/admin/monitor/indexes/apply    # 应用优化建议
```

---

### 3. 实时性能监控仪表板

**目标**: 可视化数据库性能指标

#### 监控指标

| 指标 | 说明 | 正常范围 | 告警阈值 |
|-----|------|---------|---------|
| **Query/sec** | 每秒查询数 | 100-1000 | >2000 |
| **Slow Queries/min** | 每分钟慢查询数 | <5 | >20 |
| **Connection Count** | 活跃连接数 | 5-50 | >100 |
| **Avg Query Time** | 平均查询耗时 | <50ms | >200ms |
| **Cache Hit Ratio** | Redis 缓存命中率 | >80% | <50% |
| **Lock Wait Time** | 平均锁等待时间 | <10ms | >100ms |

#### 实现方案

```python
# 创建 models/performance_metrics.py
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime
    queries_per_sec: float
    slow_queries_per_min: int
    active_connections: int
    avg_query_time_ms: float
    cache_hit_ratio: float
    lock_wait_time_ms: float

# 创建 routes/monitor.py
@router.get("/api/admin/monitor/metrics")
async def get_performance_metrics(
    period: str = "1h"  # 1h, 6h, 24h
):
    """
    获取性能指标
    返回时序数据用于绘制图表
    """
    pass

@router.websocket("/ws/monitor/live")
async def monitor_websocket():
    """
    实时推送监控数据
    前端可实时更新仪表板
    """
    pass
```

**前端仪表板（HTML5）**:
```
┌─────────────────────────────────────────┐
│ 📊 数据库性能监控仪表板                 │
├─────────────────────────────────────────┤
│                                         │
│  查询速率      慢查询      连接数       │
│  ████ 520    [!] 8/min    [!] 45      │
│  /sec        告警          活跃         │
│                                         │
│  ───────────────────────────────────   │
│  性能趋势 (过去 24 小时)                │
│  ┌─────────────────────────────────┐  │
│  │   ╱╲   ╱╲        查询耗时        │  │
│  │  ╱  ╲ ╱  ╲  ────────────────    │  │
│  │ ╱    ╱    ╲  缓存命中率          │  │
│  │─────────────────────────────────│  │
│  │ 0:00  6:00  12:00  18:00  24:00 │  │
│  └─────────────────────────────────┘  │
│                                         │
│  索引健康: ✓ 98%  | 缓存命中率: ✓ 87% │
│                                         │
└─────────────────────────────────────────┘
```

---

### 4. 自动优化建议系统

**目标**: 基于性能数据智能生成优化建议

#### 优化建议类型

| 类型 | 示例 | 优先级 |
|-----|------|--------|
| **索引优化** | 为 `status` 列添加索引 | 高 |
| **查询优化** | 使用 JOIN 代替子查询 | 高 |
| **缓存策略** | 缓存高频查询结果 | 中 |
| **连接池** | 增加连接池大小 | 低 |
| **表分区** | 对大表进行分区 | 低 |

#### 实现方案

```python
# 创建 utils/optimization_advisor.py
def analyze_and_recommend():
    """
    分析性能数据并生成优化建议
    """
    recommendations = []
    
    # 检查慢查询
    slow_queries = get_slow_queries(limit=100)
    for query in slow_queries:
        # 分析 EXPLAIN 结果
        explain = analyze_explain_plan(query)
        
        if explain["full_index_scan"]:
            recommendations.append({
                "type": "index_optimization",
                "priority": "HIGH",
                "description": f"为表 {explain['table']} 添加索引",
                "suggested_index": generate_index_sql(explain),
                "estimated_improvement": "45%"
            })
    
    return sorted(recommendations, key=lambda x: priority_score(x["priority"]))
```

**API 端点**:
```
GET /api/admin/monitor/recommendations    # 获取优化建议
POST /api/admin/monitor/recommendations/{id}/apply # 应用建议
POST /api/admin/monitor/recommendations/{id}/dismiss # 忽略建议
```

---

## 🏗️ 代码结构

```
新增文件/文件夹:

1-后端代码/
├── models/
│   ├── slow_query.py           # 慢查询模型（20 行）
│   └── performance_metrics.py  # 性能指标模型（30 行）
├── utils/
│   ├── slow_query_monitor.py   # 慢查询监控工具（80 行）
│   ├── index_analyzer.py       # 索引分析工具（120 行）
│   ├── metrics_collector.py    # 指标收集工具（100 行）
│   └── optimization_advisor.py # 优化建议工具（150 行）
├── routes/
│   └── monitor.py              # 监控 API 路由（200 行）
├── static/
│   └── js/monitor-dashboard.js # 前端仪表板脚本（300 行）
├── templates/
│   └── monitor.html            # 监控仪表板模板（150 行）
└── 3-数据库/
    └── monitor_schema.sql      # 监控表结构（50 行）

总计: ~1,200 行新代码
```

---

## 📅 实施时间表

### Day 1: 基础设施建设 (3-4 小时)

```
10:00 - 创建数据模型 (models/)
  ├── slow_query.py
  └── performance_metrics.py
  
11:00 - 创建工具类 (utils/)
  ├── slow_query_monitor.py
  ├── index_analyzer.py
  └── metrics_collector.py

14:00 - 创建数据库表
  └── monitor_schema.sql

15:00 - 创建 API 路由 (routes/monitor.py)
```

### Day 2: 前端和集成 (3-4 小时)

```
10:00 - 创建前端仪表板
  ├── templates/monitor.html
  └── static/js/monitor-dashboard.js

13:00 - 集成到主应用
  ├── app.py (引入 monitor 路由)
  ├── 添加 WebSocket 连接
  └── 处理实时数据推送

15:00 - 测试和优化
  ├── 单元测试
  ├── 集成测试
  └── 性能测试
```

### Day 3: 文档和部署 (2-3 小时)

```
10:00 - 编写文档
  ├── 监控系统使用指南
  ├── API 文档
  └── 部署指南

13:00 - 创建测试脚本
  └── test_monitor_system.py

14:00 - 部署到生产环境
  ├── 数据库初始化
  ├── 服务启动测试
  └── 监控 24 小时运行
```

---

## 💾 数据库表设计

### 1. 慢查询日志表

```sql
CREATE TABLE slow_query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE,          -- SQL 哈希值
    query TEXT NOT NULL,                    -- 完整 SQL
    duration_ms FLOAT NOT NULL,             -- 耗时（毫秒）
    rows_examined INT DEFAULT 0,            -- 扫描行数
    rows_returned INT DEFAULT 0,            -- 返回行数
    lock_time_ms FLOAT DEFAULT 0,           -- 锁定时间
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    endpoint VARCHAR(255),
    INDEX idx_timestamp (timestamp),
    INDEX idx_duration (duration_ms),
    INDEX idx_query_hash (query_hash),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2. 性能指标表

```sql
CREATE TABLE performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    queries_per_sec FLOAT,
    slow_queries_per_min INT,
    active_connections INT,
    avg_query_time_ms FLOAT,
    cache_hit_ratio FLOAT,
    lock_wait_time_ms FLOAT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io_reads INT,
    disk_io_writes INT,
    INDEX idx_timestamp (timestamp)
);
```

### 3. 优化建议表

```sql
CREATE TABLE optimization_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,              -- index, query, cache, etc.
    priority VARCHAR(20),                   -- HIGH, MEDIUM, LOW
    description TEXT NOT NULL,
    suggested_sql TEXT,
    estimated_improvement FLOAT,
    status VARCHAR(50) DEFAULT 'pending',   -- pending, applied, dismissed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    applied_by INT,
    INDEX idx_status (status),
    INDEX idx_type (type),
    FOREIGN KEY (applied_by) REFERENCES users(id)
);
```

---

## 🔌 API 端点完整列表

### 慢查询 API

```bash
# 获取慢查询列表
GET /api/admin/monitor/slow-queries
  params: limit=50, offset=0, order_by=duration

# 获取慢查询统计
GET /api/admin/monitor/slow-queries/stats
  返回: 总数, 平均耗时, 最大耗时, 趋势

# 获取单条查询详情
GET /api/admin/monitor/slow-queries/{id}

# 删除慢查询日志
DELETE /api/admin/monitor/slow-queries/{id}

# 清空所有日志
DELETE /api/admin/monitor/slow-queries/all
```

### 索引 API

```bash
# 获取索引健康状态
GET /api/admin/monitor/indexes/health
  返回: 整体健康度, 各表详情

# 获取缺失索引
GET /api/admin/monitor/indexes/missing
  返回: 推荐索引列表

# 获取未使用索引
GET /api/admin/monitor/indexes/unused
  返回: 可删除索引列表

# 应用索引优化
POST /api/admin/monitor/indexes/apply
  body: {index_sql: "CREATE INDEX ..."}
```

### 性能监控 API

```bash
# 获取实时性能指标
GET /api/admin/monitor/metrics
  params: period=1h, resolution=1m

# 获取性能历史数据
GET /api/admin/monitor/metrics/history
  params: start_time, end_time

# WebSocket 实时推送
WS /ws/monitor/live
  推送: 每 5 秒实时数据
```

### 优化建议 API

```bash
# 获取所有建议
GET /api/admin/monitor/recommendations
  params: status=pending, type=index, limit=20

# 获取单条建议
GET /api/admin/monitor/recommendations/{id}

# 应用建议
POST /api/admin/monitor/recommendations/{id}/apply

# 忽略建议
POST /api/admin/monitor/recommendations/{id}/dismiss

# 撤销应用
POST /api/admin/monitor/recommendations/{id}/revert
```

---

## 🎯 关键功能特性

### 1. 实时推送 WebSocket
```javascript
// 前端代码
const socket = new WebSocket('ws://127.0.0.1:5000/ws/monitor/live');

socket.onmessage = (event) => {
    const metrics = JSON.parse(event.data);
    updateDashboard(metrics);
    updateCharts(metrics);
};
```

### 2. 自动告警
```python
# 当指标超过阈值时自动告警
ALERT_RULES = {
    "slow_queries_per_min": {
        "warning": 10,
        "critical": 20,
        "action": "send_notification"
    },
    "cache_hit_ratio": {
        "warning": 0.6,
        "critical": 0.4,
        "action": "suggest_optimization"
    }
}
```

### 3. 智能推荐
```
基于历史数据和查询模式，自动生成优化建议，
显示预期改进效果，让管理员做出决策。
```

---

## 📊 预期收益

| 指标 | 改进 | 方法 |
|-----|------|------|
| 数据库查询速度 | ↑ 30-50% | 添加缺失索引 |
| 缓存命中率 | ↑ 20-40% | 缓存热点查询 |
| 连接数 | ↓ 20-30% | 连接池优化 |
| 磁盘 I/O | ↓ 15-25% | 查询优化 |
| 管理效率 | ↑ 5 倍 | 自动化建议 |

---

## 🧪 测试计划

### 单元测试
```python
test_slow_query_detection()
test_index_analysis()
test_metrics_collection()
test_recommendation_generation()
```

### 集成测试
```python
test_api_endpoints()
test_websocket_connection()
test_alert_triggering()
test_dashboard_rendering()
```

### 性能测试
```python
test_metrics_storage_performance()
test_query_analysis_speed()
test_concurrent_connections()
test_memory_usage()
```

---

## 🚀 开始实施

**准备好开始 Phase 1 Step 3 了吗？**

下一步：
1. 创建数据模型
2. 实现监控工具
3. 构建 API 路由
4. 开发前端仪表板
5. 编写测试和文档

---

**规划完成时间**: 2025-01-21  
**预计实施周期**: 3-5 天  
**工作量**: 1,200+ 行新代码 + 文档  
**优先级**: 高（直接提升系统性能）
