# Phase 2 Stage 2: 智能报表与导出系统

## 📋 实施计划

**目标：** 为管理层提供完整的统计分析与报表导出能力  
**周期：** 3-4 天  
**优先级：** P0（核心业务功能）

---

## 🎯 功能清单

### 1. 报表模板系统
- [x] 数据库表设计
- [ ] 日报模板（每日巡查统计、待处理工单、超期预警）
- [ ] 周报模板（趋势对比、部门排名、问题类型分布）
- [ ] 月报模板（综合分析、KPI 达成、复发率统计）
- [ ] 自定义报表（灵活配置维度与指标）

### 2. 异步导出引擎
- [ ] Excel 导出（支持百万级数据分页导出）
- [ ] PDF 导出（带图表、样式、水印）
- [ ] 导出任务队列（Celery 异步处理）
- [ ] 下载链接生成与过期管理

### 3. 报表订阅与推送
- [ ] 定时任务（每日/每周/每月自动生成）
- [ ] 邮件推送（SMTP 集成）
- [ ] 企业微信/钉钉推送（Webhook）
- [ ] 订阅管理（用户自定义接收时间与内容）

### 4. 数据可视化
- [ ] 统计指标聚合（按部门/路段/问题类型/时间窗）
- [ ] 图表数据接口（折线图、柱状图、饼图）
- [ ] 趋势分析（同比、环比）
- [ ] 实时刷新（WebSocket 推送最新数据）

---

## 🚀 本次落地（2025-12-24）
- 增加 reports 路由：模板创建/查询/更新、异步生成队列、历史与统计、订阅管理、下载出口（exports 目录）。
- Celery Beat 增补 send_scheduled_reports（每 60 秒扫描订阅）与 cleanup_expired_reports（每小时清理过期记录）。
- 生成接口返回 record_id + Celery task_id；下载接口校验文件名并提供认证访问。
- 报表引擎支持 PDF（基于 reportlab，缺失依赖时自动降级 CSV），保留 CSV/XLSX。

---

## 🗄️ 数据库设计

### 核心表结构

```sql
-- 报表模板
CREATE TABLE report_template (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    type ENUM('daily','weekly','monthly','custom') COMMENT '报表类型',
    config JSON COMMENT '字段配置 {dimensions:[],metrics:[],filters:{}}',
    sql_template TEXT COMMENT 'SQL 查询模板（支持变量替换）',
    chart_config JSON COMMENT '图表配置',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    enabled TINYINT DEFAULT 1,
    INDEX idx_type (type),
    INDEX idx_creator (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表模板';

-- 报表订阅
CREATE TABLE report_subscription (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL,
    subscriber_id INT NOT NULL COMMENT '订阅用户 ID',
    frequency ENUM('daily','weekly','monthly') COMMENT '发送频率',
    send_time TIME COMMENT '发送时间（如 09:00:00）',
    send_day VARCHAR(20) COMMENT '发送日期（如 monday, 1-31）',
    delivery_method ENUM('email','wechat','dingtalk') DEFAULT 'email',
    delivery_target VARCHAR(255) COMMENT '接收地址',
    enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES report_template(id) ON DELETE CASCADE,
    FOREIGN KEY (subscriber_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_schedule (frequency, send_time, enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表订阅';

-- 报表生成历史
CREATE TABLE report_generation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL,
    generated_by INT COMMENT '生成人（NULL 表示定时任务）',
    generation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_range_start DATE,
    time_range_end DATE,
    file_path VARCHAR(500) COMMENT '文件存储路径',
    file_type ENUM('pdf','xlsx','csv'),
    file_size INT COMMENT '文件大小（字节）',
    download_url VARCHAR(500),
    expires_at DATETIME COMMENT '下载链接过期时间',
    status ENUM('pending','generating','completed','failed') DEFAULT 'pending',
    error_msg TEXT,
    FOREIGN KEY (template_id) REFERENCES report_template(id) ON DELETE CASCADE,
    INDEX idx_status (status, generation_time),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表生成历史';

-- 报表发送日志
CREATE TABLE report_send_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL COMMENT 'report_generation_history ID',
    subscription_id INT COMMENT '订阅 ID（手动发送则为 NULL）',
    sent_to VARCHAR(255) NOT NULL COMMENT '接收人邮箱/ID',
    send_method ENUM('email','wechat','dingtalk'),
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending','sent','failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    error_msg TEXT,
    FOREIGN KEY (report_id) REFERENCES report_generation_history(id) ON DELETE CASCADE,
    INDEX idx_status (status, sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表发送日志';

-- 自定义统计指标（用于灵活报表）
CREATE TABLE report_metric (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '指标名称',
    display_name VARCHAR(100) COMMENT '显示名称',
    sql_expression TEXT COMMENT 'SQL 聚合表达式',
    dimension VARCHAR(50) COMMENT '维度（department/segment/problem_type）',
    unit VARCHAR(20) COMMENT '单位（次/小时/条）',
    sort_order INT DEFAULT 0,
    enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自定义统计指标';
```

---

## 📦 实现步骤

### Step 1: 数据库迁移（30 分钟）
1. 创建报表相关表
2. 插入预置模板数据
3. 插入常用统计指标

### Step 2: ORM 模型（1 小时）
- `models/report_models.py`：ReportTemplate, ReportSubscription, ReportGenerationHistory, ReportSendLog
- `models/report_schemas.py`：Pydantic 验证模型

### Step 3: 报表生成引擎（3 小时）
- `utils/report_generator.py`：
  - `generate_daily_report()` - 日报
  - `generate_weekly_report()` - 周报
  - `generate_monthly_report()` - 月报
  - `render_to_pdf()` - PDF 渲染（使用 WeasyPrint/ReportLab）
  - `export_to_excel()` - Excel 导出（使用 openpyxl）

### Step 4: Celery 异步任务（2 小时）
- `tasks/report_tasks.py`：
  - `generate_report_async.delay(template_id, params)`
  - `send_scheduled_reports.delay()` - 定时扫描订阅
  - `cleanup_expired_reports.delay()` - 清理过期文件

### Step 5: API 路由（2 小时）
- `routes/reports.py`：
  - `POST /api/reports/generate` - 手动生成报表
  - `GET /api/reports` - 报表历史列表
  - `GET /api/reports/{id}/download` - 下载报表
  - `POST /api/reports/templates` - 创建模板
  - `GET /api/reports/templates` - 模板列表
  - `POST /api/reports/subscriptions` - 订阅报表
  - `GET /api/reports/metrics` - 统计指标接口

### Step 6: 定时任务配置（30 分钟）
- 更新 `celery_app.py`，添加 Beat 调度：
  ```python
  celery_app.conf.beat_schedule.update({
      'daily-reports': {
          'task': 'tasks.report_tasks.send_scheduled_reports',
          'schedule': crontab(hour=9, minute=0),  # 每天 9:00
      },
      'cleanup-reports': {
          'task': 'tasks.report_tasks.cleanup_expired_reports',
          'schedule': crontab(hour=2, minute=0),  # 每天 2:00
      },
  })
  ```

### Step 7: 测试与验证（1 小时）
- `verify_phase2_stage2.py`：
  - 测试模板创建与查询
  - 测试报表生成（日/周/月）
  - 测试 Excel/PDF 导出
  - 测试订阅与定时发送

---

## 🎨 预置报表模板

### 日报模板
```json
{
  "name": "巡查日报",
  "type": "daily",
  "dimensions": ["department", "segment"],
  "metrics": [
    "total_inspections",      // 总巡查次数
    "pending_orders",         // 待处理工单
    "overdue_orders",         // 超期工单
    "avg_resolution_time"     // 平均处理时长
  ],
  "charts": [
    {"type": "bar", "title": "各部门巡查量", "metric": "total_inspections"},
    {"type": "pie", "title": "问题类型分布", "metric": "problem_distribution"}
  ]
}
```

### 周报模板
```json
{
  "name": "巡查周报",
  "type": "weekly",
  "metrics": [
    "weekly_trend",           // 周趋势对比
    "department_ranking",     // 部门排名
    "problem_type_analysis",  // 问题类型深度分析
    "efficiency_score"        // 效率评分
  ],
  "comparison": {
    "last_week": true,
    "same_period_last_year": false
  }
}
```

### 月报模板
```json
{
  "name": "巡查月报",
  "type": "monthly",
  "metrics": [
    "monthly_summary",        // 月度总览
    "kpi_achievement",        // KPI 达成情况
    "recurrence_rate",        // 问题复发率
    "quality_score",          // 质量评分
    "cost_analysis"           // 成本分析
  ],
  "includes": [
    "executive_summary",      // 管理摘要
    "detailed_breakdown",     // 详细分解
    "recommendations"         // 优化建议
  ]
}
```

---

## 🔒 权限控制

| 角色 | 查看报表 | 生成报表 | 订阅报表 | 管理模板 |
|------|---------|---------|---------|---------|
| inspector | 自己的 | 自己的 | ✓ | ✗ |
| dispatcher | 部门的 | 部门的 | ✓ | ✗ |
| reviewer | 所有 | 所有 | ✓ | ✗ |
| admin | 所有 | 所有 | ✓ | ✓ |

---

## 📊 成功指标

- [ ] 日报生成时间 < 5 秒
- [ ] 周报生成时间 < 15 秒
- [ ] 月报生成时间 < 30 秒
- [ ] Excel 导出支持 100 万行数据
- [ ] PDF 文件大小 < 5MB
- [ ] 邮件发送成功率 > 99%
- [ ] 定时任务准时率 > 99.9%

---

## 🚀 下一步（Stage 3）

完成报表系统后，将开始实施：
- **地图智能与热区分析**
- 地理围栏配置
- 高频问题区域热力图
- 同一地段重复问题聚类
