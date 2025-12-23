# Phase 2 实现规划 - 功能与产品力增强

## 📋 概述

基于 Phase 1 (Redis + Celery + 监控系统) 的基础，Phase 2 将实现企业级的功能完整性和性能优化。

**预期投入：** 4-6 周  
**目标完成度：** 95%+  
**优先级分层：** P0 → P1 → P2

---

## 🎯 分阶段实现规划

### **第一阶段：核心业务流程（1-2 周）**

#### P0-1: 工单状态机与流转 ⭐⭐⭐⭐⭐
**价值：** 核心业务，直接支撑巡查闭环

**功能分解：**
- [ ] 工单状态定义 (5 个状态：新建→派单→处理→复核→归档)
- [ ] 工单超时提醒 (Celery 定时任务)
- [ ] 驳回与重新派单流程
- [ ] 批量操作接口 (批量派单、批量审核)
- [ ] SLA 配置与统计
- [ ] 工单操作审计日志

**数据库设计：**
```sql
-- 工单表 (基于 inspectionrecord)
ALTER TABLE inspectionrecord ADD COLUMN order_status ENUM('new','assigned','processing','reviewed','archived');
ALTER TABLE inspectionrecord ADD COLUMN assigned_user_id INT;
ALTER TABLE inspectionrecord ADD COLUMN assigned_time DATETIME;
ALTER TABLE inspectionrecord ADD COLUMN handler_id INT;
ALTER TABLE inspectionrecord ADD COLUMN handler_time DATETIME;
ALTER TABLE inspectionrecord ADD COLUMN reviewer_id INT;
ALTER TABLE inspectionrecord ADD COLUMN review_time DATETIME;

-- 工单流转日志
CREATE TABLE order_flow_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    operator_id INT,
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT
);

-- SLA 配置
CREATE TABLE sla_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    problem_type_id INT,
    dispatch_sla_hours INT,      -- 派单 SLA (小时)
    process_sla_hours INT,        -- 处理 SLA (小时)
    review_sla_hours INT,         -- 复核 SLA (小时)
    enabled TINYINT DEFAULT 1
);
```

**API 端点：**
```
POST   /api/orders/{id}/assign      -- 派单
POST   /api/orders/{id}/process     -- 标记处理中
POST   /api/orders/{id}/review      -- 审核
POST   /api/orders/{id}/reject      -- 驳回
POST   /api/orders/batch/assign     -- 批量派单
GET    /api/orders/{id}/flow        -- 获取流转历史
GET    /api/orders/sla-report       -- SLA 统计报告
```

**Celery 任务：**
```python
# 每小时检查逾期工单
@celery_app.task
def check_overdue_orders():
    ...

# 发送超时提醒
@celery_app.task
def send_sla_reminder(order_id):
    ...
```

---

#### P0-2: 多角色与权限细分 ⭐⭐⭐⭐
**价值：** 支撑组织协作，解决权限管理需求

**功能分解：**
- [ ] 5 个角色定义 (巡查员、派单人、审核人、复核人、管理员)
- [ ] 权限细分 (表级、数据级、操作级)
- [ ] 部门与路段隔离
- [ ] 权限检查中间件

**数据库设计：**
```sql
-- 扩展 user 表
ALTER TABLE user ADD COLUMN role_id INT;
ALTER TABLE user ADD COLUMN department_id INT;
ALTER TABLE user ADD COLUMN can_view_segments TEXT;  -- JSON: 可见路段列表

-- 权限表
CREATE TABLE role (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE,       -- inspector, dispatcher, reviewer, admin
    description TEXT
);

CREATE TABLE role_permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT,
    resource VARCHAR(100),         -- 'order', 'photo', 'report'
    action VARCHAR(50),            -- 'create', 'read', 'update', 'delete'
    data_scope VARCHAR(50)         -- 'own', 'department', 'all'
);

-- 用户权限覆盖表
CREATE TABLE user_permission_override (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    resource VARCHAR(100),
    action VARCHAR(50),
    allowed TINYINT,
    created_by INT,
    created_at DATETIME
);
```

**权限检查示例：**
```python
# 装饰器: @require_permission("order", "read", "department")
async def get_orders(current_user):
    orders = await fetch_user_orders(current_user)  # 自动过滤
    return orders
```

---

### **第二阶段：智能能力 + 报表（2-3 周）**

#### P0-3: 多维报表与导出 ⭐⭐⭐⭐⭐
**价值：** 管理层决策工具，高频使用场景

**功能分解：**
- [ ] 日报模板 (每日统计、待处理、超期)
- [ ] 周报模板 (周对比、效率趋势)
- [ ] 月报模板 (完整分析、KPI)
- [ ] 自定义报表 (拖拽式字段选择)
- [ ] 一键导出 PDF/Excel
- [ ] 报表定时发送 (邮件)
- [ ] 报表权限控制

**数据库设计：**
```sql
-- 报表模板
CREATE TABLE report_template (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    type VARCHAR(50),              -- 'daily', 'weekly', 'monthly', 'custom'
    config JSON,                   -- 字段配置
    sql_query TEXT,                -- 自定义 SQL
    created_by INT,
    created_at DATETIME
);

-- 报表订阅
CREATE TABLE report_subscription (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT,
    subscriber_id INT,
    frequency VARCHAR(50),         -- 'daily', 'weekly', 'monthly'
    send_time TIME,
    enabled TINYINT DEFAULT 1
);

-- 报表发送历史
CREATE TABLE report_send_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT,
    sent_to VARCHAR(255),
    status VARCHAR(50),            -- 'pending', 'sent', 'failed'
    sent_at DATETIME,
    error_msg TEXT
);
```

**Celery 任务：**
```python
@celery_app.task
def generate_daily_report():
    # 计算日报数据
    # 生成 PDF
    # 发送邮件
    pass

@celery_app.task
def export_to_excel(report_config):
    # 异步导出大量数据
    # 返回下载链接
    pass
```

**API 端点：**
```
GET    /api/reports/templates      -- 获取报表模板列表
POST   /api/reports/generate       -- 生成报表
GET    /api/reports/{id}/preview   -- 预览报表
GET    /api/reports/{id}/export    -- 导出报表
POST   /api/reports/subscribe      -- 订阅报表
```

---

#### P0-4: 地图智能能力 ⭐⭐⭐
**价值：** 核心产品差异化，高维度分析

**功能分解：**
- [ ] 地理围栏定义 (多边形)
- [ ] 热区分析 (高频问题区域热力图)
- [ ] 时间窗叠加分析 (特定时段的热区)
- [ ] 问题类型叠加 (某类问题的空间分布)
- [ ] 重复问题聚类与去重
- [ ] 路段级统计

**地理围栏数据结构：**
```sql
CREATE TABLE geo_fence (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    road_segment_id INT,
    polygon_points JSON,           -- [[lat, lng], ...]
    created_at DATETIME
);

-- 热区计算结果缓存
CREATE TABLE heatmap_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fence_id INT,
    time_window VARCHAR(50),       -- '2024-01-01', 'week', 'month'
    problem_type_id INT,           -- NULL 表示所有类型
    heatmap_data JSON,             -- 热力值矩阵
    calculated_at DATETIME,
    expires_at DATETIME
);
```

**热区聚类算法：**
```python
# 使用 scikit-learn DBSCAN 做空间聚类
from sklearn.cluster import DBSCAN

def cluster_problem_locations(lat_lngs, eps=0.01):  # ~1km
    clustering = DBSCAN(eps=eps, min_samples=3).fit(lat_lngs)
    clusters = group_by_label(lat_lngs, clustering.labels_)
    return [{
        'center': calc_centroid(cluster),
        'count': len(cluster),
        'problems': extract_problem_ids(cluster)
    } for cluster in clusters]
```

---

#### P1-5: 智能质检与识别 ⭐⭐⭐
**价值：** 保证数据质量，减少人工审核

**功能分解：**
- [ ] 照片内容校验 (是否道路场景)
- [ ] 关键对象检测 (护栏、坑洼、标线等)
- [ ] 质量指标评分 (模糊度、曝光、角度)
- [ ] 上传时实时提示
- [ ] AI 建议的可信度标记
- [ ] 审核反馈学习循环

**轻量级模型选择：**
```python
# 方案 A: YOLO 检测 + 端侧推理 (推荐)
# - YOLOv8n/s (轻量级)
# - 推理时间 < 1 秒
# - 模型大小 < 50MB

# 方案 B: 调用现有大模型 API
# - 阿里云 CV API
# - 腾讯云 CI
# - 百度 EasyDL
```

**API 端点：**
```
POST   /api/photos/validate        -- 上传时校验
GET    /api/photos/{id}/quality    -- 获取质量评分
POST   /api/ai/suggestions/{id}    -- 获取 AI 建议 (带可信度)
POST   /api/feedback/mark          -- 用户反馈标记
```

---

### **第三阶段：性能优化（2-3 周，与前两阶段并行）**

#### P1-6: 缓存与热点治理 ⭐⭐⭐⭐⭐
**价值：** 性能翻倍提升，支撑高并发

**功能分解：**
- [ ] 高频统计接口缓存 (Redis)
- [ ] 缓存预热与更新策略
- [ ] 照片元数据列表缓存
- [ ] 导出任务异步化
- [ ] 缓存一致性保证

**缓存策略：**
```python
# 统计接口：Cache-Aside + 版本号
@app.get("/api/statistics/daily")
@cached(ttl=3600, version="stats_v1")  # 1 小时
async def get_daily_statistics():
    return db.fetch_stats()

# 照片列表：短期缓存 + 过期自动更新
@app.get("/api/photos")
@cached(ttl=300, tag="photo_list")  # 5 分钟
async def list_photos(skip, limit):
    return db.fetch_photos(skip, limit)

# 导出：异步任务 + 结果轮询
@app.post("/api/reports/export-async")
async def export_async(config):
    task_id = export_task.delay(config)
    return {"task_id": task_id}

@app.get("/api/tasks/{task_id}/status")
async def check_export_status(task_id):
    task = celery_app.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "url": task.result}
    return {"status": "processing"}
```

---

#### P1-7: 数据库索引治理 ⭐⭐⭐⭐
**价值：** 查询性能稳定性

**功能分解：**
- [ ] 自动化 EXPLAIN 分析
- [ ] 缺失索引报警
- [ ] 冗余索引识别
- [ ] 定期索引碎片整理
- [ ] 大表分区方案

**Nightly Job：**
```python
@celery_app.task
def analyze_query_performance():
    # 1. 获取慢查询日志
    slow_queries = get_slow_queries(last_24h)
    
    # 2. 运行 EXPLAIN
    for query in slow_queries:
        plan = run_explain(query)
        if no_index_used(plan):
            suggest_index(query)
    
    # 3. 检查冗余索引
    redundant = find_redundant_indexes()
    alert_on_redundancy(redundant)
    
    # 4. 碎片整理
    optimize_tables(['inspectionrecord', 'photo'])

# 分区示例：inspectionrecord 按月分区
ALTER TABLE inspectionrecord PARTITION BY RANGE (YEAR_MONTH(upload_time)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    ...
);
```

---

#### P1-8: 分页与游标优化 ⭐⭐⭐
**价值：** 大列表查询性能

**功能分解：**
- [ ] Keyset 分页实现
- [ ] 游标生成与验证
- [ ] 深度分页优化

**Keyset 分页示例：**
```python
# 旧方式：OFFSET + LIMIT (深度分页慢)
SELECT * FROM inspectionrecord ORDER BY id LIMIT 1000000, 20;

# 新方式：Keyset 分页 (常数时间)
# 第 1 页：
SELECT * FROM inspectionrecord WHERE id > 0 ORDER BY id LIMIT 20;

# 第 2 页：基于最后一条记录的 id（假设为 1000）
SELECT * FROM inspectionrecord WHERE id > 1000 ORDER BY id LIMIT 20;

# 前端无感知：
@app.get("/api/orders")
async def list_orders(cursor: str = None):
    if cursor:
        last_id = decrypt_cursor(cursor)
        orders = db.query("SELECT * FROM ... WHERE id > ? LIMIT 20", last_id)
    else:
        orders = db.query("SELECT * FROM ... LIMIT 20")
    
    return {
        "data": orders,
        "next_cursor": encrypt_cursor(orders[-1].id)
    }
```

---

#### P2-9: 读写分离 ⭐⭐⭐
**价值：** 支持高写入并发

**功能分解：**
- [ ] MySQL 主从配置
- [ ] 连接池区分
- [ ] 写入走主库，查询走从库
- [ ] 复制延迟监控

**实现方式：**
```python
# 配置两个连接池
primary_pool = create_connection_pool("master.db:3306")   # 写入
replica_pool = create_connection_pool("slave.db:3306")    # 查询

# 在依赖注入中区分
async def get_write_db():
    return primary_pool.get_connection()

async def get_read_db():
    return replica_pool.get_connection()

# 在 API 中使用
@app.post("/api/orders")
async def create_order(db_write = Depends(get_write_db)):
    # 写入到主库
    return db_write.insert(order)

@app.get("/api/orders")
async def list_orders(db_read = Depends(get_read_db)):
    # 从从库读取
    return db_read.query("SELECT * FROM orders")
```

---

#### P2-10: 通知与订阅系统 ⭐⭐⭐
**价值：** 用户体验，及时通知

**功能分解：**
- [ ] WebSocket/SSE 实时推送
- [ ] 邮件通知
- [ ] 企业微信集成
- [ ] 短信通知
- [ ] 条件订阅

**实现方式：**
```python
# WebSocket 实时推送
from fastapi import WebSocket

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    # 订阅用户通知频道
    channel = f"user:{user_id}:notifications"
    async for message in redis_client.subscribe(channel):
        await websocket.send_json(message)

# 邮件通知
from celery_app import celery_app

@celery_app.task
def send_email_notification(user_id, subject, body):
    user = get_user(user_id)
    send_email(user.email, subject, body)

# 企业微信集成
def send_wechat_notification(user_id, message):
    user = get_user(user_id)
    if user.wechat_userid:
        # 调用企业微信 API
        post_wechat_message(user.wechat_userid, message)

# 条件订阅
@app.post("/api/subscriptions/create")
async def create_subscription(current_user, config):
    # config = {
    #   "road_segments": [1, 2, 3],
    #   "problem_types": [101, 102],
    #   "channels": ["email", "wechat"],
    #   "conditions": {"severity": "high"}
    # }
    db.insert_subscription(current_user.id, config)
```

---

### **第四阶段：安全与测试（1-2 周，与其他阶段并行）**

#### P1-11: 审计日志与安全 ⭐⭐⭐⭐
**价值：** 合规要求，问题追溯

**功能分解：**
- [ ] 操作审计日志 (谁、什么时候、做了什么、改了什么)
- [ ] 数据变更追踪
- [ ] IP 白名单
- [ ] 二次校验 (敏感操作)
- [ ] JWT 刷新机制
- [ ] HTTPS + HSTS

**数据库设计：**
```sql
CREATE TABLE audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id INT,
    resource_type VARCHAR(50),     -- 'order', 'photo', 'user'
    resource_id INT,
    action VARCHAR(50),            -- 'create', 'update', 'delete', 'export'
    old_value JSON,
    new_value JSON,
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50)             -- 'success', 'failed'
);

-- IP 白名单
CREATE TABLE admin_ip_whitelist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ip_address VARCHAR(45),
    description VARCHAR(255),
    added_by INT,
    added_at DATETIME
);
```

---

#### P2-12: 压测与基线 ⭐⭐⭐
**价值：** 性能保证，容量规划

**功能分解：**
- [ ] k6/Locust 压测脚本
- [ ] 关键场景基线测试
- [ ] SLO 定义与监控
- [ ] 自动化回归

**压测脚本示例 (k6)：**
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 100,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'],  // p95 < 500ms
    http_req_failed: ['rate<0.1'],     // 错误率 < 10%
  }
};

export default function () {
  // 测试：列表查询
  let res = http.get('http://localhost:5000/api/orders?limit=20');
  check(res, {
    'status 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

---

#### P2-13: 灰度与回滚 ⭐⭐
**价值：** 安全上线，风险控制

**功能分解：**
- [ ] Feature Flag 配置
- [ ] 灰度规则引擎 (按用户、按百分比)
- [ ] 数据库迁移回滚方案
- [ ] 预估影响评估

**Feature Flag 实现：**
```python
# Redis 存储 Feature Flag
# key: "feature:new_report_system" value: { "enabled": true, "rollout_percent": 50 }

@app.get("/api/reports")
async def get_reports(current_user):
    if feature_flag.is_enabled("new_report_system", user_id=current_user.id):
        # 使用新报表系统
        return new_report_service.get_reports()
    else:
        # 使用旧系统
        return legacy_report_service.get_reports()

# 管理员界面可配置
@app.post("/api/admin/feature-flags/{flag_name}/set")
async def set_feature_flag(flag_name, enabled, rollout_percent=100):
    redis_client.set(f"feature:{flag_name}", {
        "enabled": enabled,
        "rollout_percent": rollout_percent,
        "updated_at": datetime.now().isoformat()
    })
```

---

## 📊 实现时间表

```
Week 1:
  Day 1-2: 工单状态机 + 权限细分 (P0-1, P0-2)
  Day 3-4: 多维报表 (P0-3)
  Day 5:   集成测试 + bug fix

Week 2:
  Day 1-2: 地图热区 + 质检 (P0-4, P1-5)
  Day 3-4: 缓存优化 (P1-6)
  Day 5:   性能测试

Week 3:
  Day 1-2: 索引治理 + 分页优化 (P1-7, P1-8)
  Day 3-4: 读写分离 (P2-9)
  Day 5:   压测与基线 (P2-12)

Week 4-5: 
  - 通知系统 + 审计日志 (P2-10, P1-11)
  - 灰度发布准备 (P2-13)
  - 全量回归测试
  - 文档编写

Week 6:
  - 上线前冲刺
  - 灰度验证
  - 正式发布
```

---

## 📈 关键指标与验收

### 功能完成度
- [x] P0 功能 100% 完成
- [x] P1 功能 100% 完成
- [ ] P2 功能 80%+ 完成

### 性能目标 (SLO)
- 列表查询 p95 < 500ms
- 统计接口 p95 < 1000ms
- 报表导出 < 30s
- 错误率 < 0.1%

### 可靠性
- 99.9% 可用性
- 工单 SLA 达成率 > 95%
- 审计日志完整性 = 100%

---

## 📚 文档输出

为每个阶段输出：
- [ ] 功能设计文档
- [ ] API 文档
- [ ] 数据库迁移脚本
- [ ] 测试用例
- [ ] 部署检查清单

---

## 🚀 建议下一步

1. **确认优先级** - 根据业务需求调整顺序
2. **资源分配** - 前后端开发人员协调
3. **开发环境** - 建立测试数据集
4. **代码审查** - 每个阶段的评审流程
5. **用户反馈** - 收集需求优化

---

**准备好开始第一阶段了吗？我们从工单状态机开始！** 🚀
