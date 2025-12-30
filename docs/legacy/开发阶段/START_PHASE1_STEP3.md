# 🚀 Phase 1 Step 3: 数据库监控 - 快速开始

## 📊 任务概览

| 任务 | 工作量 | 优先级 | 状态 |
|-----|--------|--------|------|
| 数据模型创建 | 1h | 🔴 高 | ⏳ 待开始 |
| 监控工具开发 | 2h | 🔴 高 | ⏳ 待开始 |
| API 路由实现 | 1.5h | 🔴 高 | ⏳ 待开始 |
| 前端仪表板 | 2h | 🟡 中 | ⏳ 待开始 |
| 测试和文档 | 1h | 🟢 低 | ⏳ 待开始 |

**总工作量**: 7-8 小时  
**预计完成**: 1-2 天

---

## 🎯 核心功能清单

### Phase 1 Step 3 将实现以下功能：

#### ✅ 核心功能（必须）

- [ ] **慢查询检测**
  - 自动记录 >1000ms 的 SQL 查询
  - 按耗时排序
  - 列表查看和管理

- [ ] **索引健康检查**
  - 检测缺失索引
  - 检测未使用索引
  - 一键应用建议

- [ ] **性能监控仪表板**
  - 实时展示关键指标
  - 历史趋势图表
  - 性能告警

#### 🟡 扩展功能（可选）

- [ ] **自动优化建议**
  - 基于查询模式推荐索引
  - 基于性能数据推荐配置
  - 一键应用优化

- [ ] **性能告警系统**
  - 自定义告警阈值
  - 邮件/系统通知
  - 告警历史记录

---

## 📁 新增文件结构

```
1-后端代码/
├── models/
│   ├── slow_query.py           # ← NEW (20 行)
│   └── performance_metrics.py  # ← NEW (30 行)
├── utils/
│   ├── slow_query_monitor.py   # ← NEW (80 行)
│   ├── index_analyzer.py       # ← NEW (120 行)
│   ├── metrics_collector.py    # ← NEW (100 行)
│   └── optimization_advisor.py # ← NEW (150 行)
├── routes/
│   └── monitor.py              # ← NEW (200 行)
├── static/js/
│   └── monitor-dashboard.js    # ← NEW (300 行)
├── templates/
│   └── monitor.html            # ← NEW (150 行)
└── 3-数据库/
    └── monitor_schema.sql      # ← NEW (50 行)
```

---

## 🛠️ 实施步骤

### Step 1: 创建数据模型（20 分钟）

```python
# 文件: models/slow_query.py
from datetime import datetime
from pydantic import BaseModel

class SlowQueryLog(BaseModel):
    """慢查询日志模型"""
    id: int = None
    query: str
    duration_ms: float
    rows_examined: int = 0
    timestamp: datetime = None
    user_id: int = None
    endpoint: str = None

class SlowQueryStats(BaseModel):
    """慢查询统计"""
    total: int
    avg_duration: float
    max_duration: float
    min_duration: float
    trend: list  # 最近 24 小时趋势
```

### Step 2: 创建监控工具（1 小时）

```python
# 文件: utils/slow_query_monitor.py
from datetime import datetime
from utils.config import SLOW_QUERY_THRESHOLD

class SlowQueryMonitor:
    """慢查询监控器"""
    
    @staticmethod
    def log_query(query: str, duration: float, rows_examined: int):
        """记录查询（如果超过阈值）"""
        if duration > SLOW_QUERY_THRESHOLD:
            # 异步存储到数据库
            # 同时写入 Redis 用于实时展示
            pass
    
    @staticmethod
    def get_recent_slow_queries(limit: int = 50):
        """获取最近的慢查询"""
        pass
    
    @staticmethod
    def get_slow_query_stats():
        """获取慢查询统计"""
        pass
```

### Step 3: 创建 API 路由（1 小时）

```python
# 文件: routes/monitor.py
from fastapi import APIRouter, Depends
from utils.deps import get_current_user

router = APIRouter(prefix="/api/admin/monitor", tags=["monitor"])

@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """获取慢查询列表"""
    pass

@router.get("/metrics")
async def get_performance_metrics(
    period: str = "1h",
    current_user = Depends(get_current_user)
):
    """获取性能指标"""
    pass

@router.get("/recommendations")
async def get_recommendations(
    status: str = "pending",
    current_user = Depends(get_current_user)
):
    """获取优化建议"""
    pass
```

### Step 4: 创建前端仪表板（1.5 小时）

```html
<!-- 文件: templates/monitor.html -->
<!DOCTYPE html>
<html>
<head>
    <title>数据库性能监控</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <!-- 关键指标卡片 -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>查询速率</h3>
                <div class="value" id="queries-per-sec">0</div>
                <p>/sec</p>
            </div>
            <div class="metric-card warning" id="slow-queries-card">
                <h3>慢查询</h3>
                <div class="value" id="slow-queries-count">0</div>
                <p>/min</p>
            </div>
            <div class="metric-card">
                <h3>缓存命中率</h3>
                <div class="value" id="cache-hit-ratio">0%</div>
            </div>
        </div>
        
        <!-- 性能趋势图 -->
        <div class="chart-container">
            <canvas id="performance-chart"></canvas>
        </div>
        
        <!-- 慢查询表格 -->
        <div class="slow-queries-table">
            <h3>最近的慢查询</h3>
            <table id="slow-queries-list">
                <thead>
                    <tr>
                        <th>SQL 语句</th>
                        <th>耗时 (ms)</th>
                        <th>扫描行数</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    
    <script src="/static/js/monitor-dashboard.js"></script>
</body>
</html>
```

### Step 5: 集成到主应用（15 分钟）

```python
# 文件: app.py (修改)
from routes import monitor

# 在 include_router 部分添加
app.include_router(monitor.router)

# 挂载监控仪表板模板
@app.get("/admin/monitor")
async def monitor_dashboard(current_user = Depends(get_current_user)):
    from fastapi.responses import HTMLResponse
    with open("templates/monitor.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
```

### Step 6: 创建数据库表（10 分钟）

```sql
-- 文件: 3-数据库/monitor_schema.sql

CREATE TABLE slow_query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query TEXT NOT NULL,
    duration_ms FLOAT NOT NULL,
    rows_examined INT DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_duration (duration_ms)
);

CREATE TABLE performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    queries_per_sec FLOAT,
    slow_queries_per_min INT,
    active_connections INT,
    avg_query_time_ms FLOAT,
    cache_hit_ratio FLOAT,
    INDEX idx_timestamp (timestamp)
);
```

---

## 📋 立即可做的事

### 1. 创建目录结构
```powershell
# 已有的目录，可直接创建文件
mkdir models    # 已有
mkdir utils     # 已有
mkdir routes    # 已有
mkdir templates # 已有
mkdir static/js # 已有
```

### 2. 从简单开始
建议实施顺序：
1. ✅ 创建数据模型（最简单）
2. ✅ 创建数据库表
3. ✅ 创建监控工具（最核心）
4. ✅ 创建 API 路由
5. ✅ 创建前端仪表板（可视化）

### 3. 测试验证
```bash
# 完成后可以通过以下方式测试
1. 访问: http://127.0.0.1:5000/admin/monitor
2. 在 Swagger UI 测试 API: http://127.0.0.1:5000/docs
3. 提交几个查询看是否记录慢查询
```

---

## 📊 预期成果

完成 Phase 1 Step 3 后，您将获得：

✅ **慢查询自动检测**
- 每个查询自动计时
- 超过 1 秒的查询自动记录
- Web 界面查看历史记录

✅ **性能仪表板**
- 实时展示 6 个关键指标
- 24 小时历史趋势图表
- 性能告警（可视化）

✅ **索引健康检查**
- 检测缺失索引
- 检测冗余索引
- 一键优化建议

✅ **自动化管理**
- 用不到 2 周的工作量
- 管理系统 10 倍效率提升
- 性能问题自动发现

---

## 💡 关键技术点

### 1. 性能数据收集
```python
# 使用 MySQL 的 INFORMATION_SCHEMA
# 定期查询并记录性能指标
SELECT 
    COUNT(*) as queries,
    ROUND(SUM(TIMER_WAIT)/1000000000000, 6) as duration
FROM performance_schema.events_statements_summary_by_event_name
```

### 2. 实时推送
```javascript
// 使用 WebSocket 推送实时数据
const ws = new WebSocket('ws://localhost:5000/ws/monitor/live');
ws.onmessage = (event) => {
    const metrics = JSON.parse(event.data);
    updateCharts(metrics);
};
```

### 3. 智能建议
```python
# 基于查询模式和 EXPLAIN 计划生成建议
EXPLAIN format=json SELECT * FROM inspection_records WHERE status = 'pending';
# 分析输出，如果是全表扫描则推荐添加索引
```

---

## 🎯 Phase 1 总进度

```
Phase 1: 核心性能优化
├── ✅ Step 1: Redis 缓存      ───────── 100%
├── ✅ Step 2: Celery 任务队列 ───────── 100%
└── ⏳ Step 3: 数据库监控      ───────── 0% ← 现在开始
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总进度: ████████████████████░░░░░░░░░░  66%
完成后: ██████████████████████████████  100%
```

---

## ❓ 常见问题

### Q: 监控对性能有影响吗？
**A**: 几乎没有。我们使用异步任务在后台收集数据，主流程不阻塞。

### Q: 如果没有 MySQL 的 performance_schema？
**A**: 可以通过 `slow_query_log` 配置，或自己在应用中记录。

### Q: 可以自定义告警阈值吗？
**A**: 完全可以，在 config.py 中配置，或通过 Web UI 动态设置。

### Q: 数据会占用很多存储空间吗？
**A**: 不会。我们只保留最近 30 天的数据，旧数据自动清理。

---

## 🚀 开始实施

**准备好开始了吗？**

我将按以下顺序实施：

1. **第一阶段**（30 分钟）：创建数据模型和数据库表
2. **第二阶段**（1.5 小时）：实现监控工具和 API 路由  
3. **第三阶段**（1 小时）：构建前端仪表板
4. **第四阶段**（30 分钟）：集成、测试和文档

**总耗时**: 3-4 小时，可以在今天完成！

---

**您准备好了吗？回复"开始"或"let me start"，我们立即开始 Phase 1 Step 3！**

---

*相关文档*:
- 📋 详细规划: [PHASE1_STEP3_PLANNING.md](./PHASE1_STEP3_PLANNING.md)
- 📊 Celery 测试结果: [CELERY_TEST_RESULTS.md](./CELERY_TEST_RESULTS.md)
- 📈 项目进度: [PROJECT_STATUS_PHASE1_STEP2.md](./PROJECT_STATUS_PHASE1_STEP2.md)
