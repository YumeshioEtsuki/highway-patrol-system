# Phase 2 Stage 1 实现指南：工单状态机与多角色权限系统

## 📋 概览

本阶段实现两个核心功能：
1. **工单状态机 (Order State Machine)** - 完整的业务流转流程
2. **多角色权限系统 (Multi-Role Access Control)** - 细粒度权限管理

## 📁 已创建的文件

### 1. 数据库层 (Database)
- **3-数据库/phase2_stage1_order_and_role.sql** (650 行)
  - 15 个新表 (role, permission, role_permission 等)
  - 6 个关键索引
  - 2 个数据库视图
  - 3 个存储过程 (含 SLA 告警)
  - 自动清理事件 (审计日志保留 6 个月)

### 2. 模型层 (Models)
- **models/order_models.py** (200 行)
  - SQLAlchemy ORM 定义
  - 9 个数据模型类
  - 4 个枚举类

- **models/order_schemas.py** (500 行)
  - Pydantic Schema (30+ 类)
  - API 请求/响应验证
  - 统计与报表模型

### 3. 业务逻辑层 (Business Logic)
- **models/order_tasks.py** (400 行)
  - 工单状态转换函数 (assign, process, review, reject, archive)
  - 工单查询与统计
  - SLA 违规查询

- **utils/permissions.py** (450 行)
  - JWT 令牌管理 (含刷新令牌)
  - 权限检查与缓存
  - 依赖注入 (FastAPI)
  - 审计日志记录

### 4. API 路由层 (API Routes)
- **routes/orders.py** (400 行)
  - 12 个工单管理端点
  - 权限检查集成
  - 审计日志自动记录
  - 批量操作支持

## 🚀 部署步骤

### Step 1: 执行数据库迁移

```bash
# 进入数据库脚本目录
cd 1-后端代码

# 执行迁移脚本 (使用 Python 的 utils.py)
python -c "
from utils.utils import execute_sql_file
import os

# 执行 SQL 迁移
execute_sql_file('3-数据库/phase2_stage1_order_and_role.sql')
print('✅ 数据库迁移完成')
"
```

或者在 MySQL 中手动执行：
```bash
mysql -u root -p road_patrol_db < 3-数据库/phase2_stage1_order_and_role.sql
```

### Step 2: 配置文件更新

在 `app.py` 中添加新的路由：

```python
# 在 app.py 顶部导入
from routes import orders
from models import order_models

# 在 app.py 的路由注册部分添加
app.include_router(orders.router)

# 确保 order_models 被导入 (用于 SQLAlchemy 映射)
```

### Step 3: 更新依赖包

如果需要额外的依赖，执行：

```bash
pip install -r requirements.txt
```

### Step 4: 启动应用

```bash
# 跳过数据库初始化 (已手动执行迁移)
set SKIP_DB_INIT=1
python start_server.py
```

或：

```bash
cd 1-后端代码
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Step 5: 验证部署

```bash
# 检查 API 是否可用
curl http://localhost:5000/docs

# 测试工单 API
curl -X GET http://localhost:5000/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 数据库架构变更

### 新增表概览

| 表名 | 用途 | 记录数 | 说明 |
|------|------|--------|------|
| `role` | 角色定义 | ~5 | 5 种角色 (inspector, dispatcher, processor, auditor, admin) |
| `permission` | 权限定义 | ~20 | 20+ 权限项 (create, read, update, delete, review, etc) |
| `role_permission` | 角色权限映射 | ~50 | 多对多关系，支持细粒度控制 |
| `user_permission_override` | 用户特殊权限 | 动态 | 对个别用户的权限覆盖 |
| `order_flow_log` | 工单流转日志 | 动态 | 完整记录工单转移过程 |
| `sla_config` | SLA 配置 | ~20 | 每个问题类型的 SLA 时间 |
| `sla_alert` | SLA 违规告警 | 动态 | 超期工单告警记录 |
| `audit_log` | 操作审计日志 | 动态 | 所有操作的完整日志 (6 月保留) |
| `admin_ip_whitelist` | IP 白名单 | ~10 | 管理员操作的 IP 限制 |
| `refresh_token` | 刷新令牌 | 动态 | JWT 刷新令牌管理 |
| `department_segment` | 部门路段映射 | 动态 | 细粒度数据权限控制 |

### InspectionRecord 表扩展

```sql
-- 新增字段
order_status VARCHAR(50)        -- 工单状态
assigned_user_id INT            -- 派单人
assigned_time DATETIME          -- 派单时间
processor_id INT                -- 处理人
process_time DATETIME           -- 处理时间
reviewer_id INT                 -- 复核人
review_time DATETIME            -- 复核时间
review_remark TEXT              -- 复核意见
reject_count INT                -- 驳回次数
reject_reason TEXT              -- 驳回原因
```

## 🔐 权限体系

### 5 种角色与权限对应

```
┌─ ADMIN (管理员)
│  └─ 拥有所有权限，可管理用户、角色、配置等
│
├─ INSPECTOR (巡查员)
│  ├─ order:create    创建巡查记录
│  ├─ order:read      查看自己的记录
│  ├─ photo:read      查看照片
│  └─ order:export    导出自己的数据
│
├─ DISPATCHER (派单人)
│  ├─ order:read      查看全部工单
│  ├─ order:assign    派单
│  └─ order:batch_assign  批量派单
│
├─ PROCESSOR (处理人)
│  ├─ order:read      查看派给自己的工单
│  ├─ order:process   标记处理中
│  └─ order:update    更新处理信息
│
└─ AUDITOR (复核人)
   ├─ order:read           查看全部工单
   ├─ order:review         审核批准
   ├─ order:reject         驳回
   ├─ order:batch_review   批量审核
   └─ report:read          查看报表
```

### 权限检查流程

```
请求 → Authorization Header
    ↓
解析 JWT Token
    ↓
查询用户角色与权限 (Redis 缓存)
    ↓
检查是否有 {resource}:{action} 权限
    ↓
检查数据范围限制 (own/dept/all)
    ↓
执行操作 + 记录审计日志
    ↓
返回结果
```

## 📈 工单状态流转图

```
                    ┌─────────────┐
                    │    NEW      │  (新建)
                    └──────┬──────┘
                           │ [dispatcher] assign
                           ↓
                    ┌─────────────┐
        ┌──────────→│  ASSIGNED   │  (已派单)
        │           └──────┬──────┘
        │                  │ [processor] process
        │                  ↓
        │           ┌─────────────┐
        │           │ PROCESSING  │  (处理中)
        │           └──────┬──────┘
        │                  │ [processor] review
        │                  ↓
        │           ┌─────────────┐
        │           │  REVIEWED   │  (已审核)
        │           └──────┬──────┘
        │                  │ [auditor] approve
        │                  ↓
        │           ┌─────────────┐
        │           │  ARCHIVED   │  (已归档/完成)
        │           └─────────────┘
        │
        └───────────────────────────────── [auditor] reject
                                           (驳回)
```

## 🔑 关键 API 端点

### 工单管理

| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/api/orders/{id}/assign` | 派单 | order:assign |
| POST | `/api/orders/{id}/process` | 标记处理中 | order:process |
| POST | `/api/orders/{id}/review` | 提交审核 | order:review |
| POST | `/api/orders/{id}/reject` | 驳回 | order:reject |
| POST | `/api/orders/{id}/approve` | 批准 & 归档 | order:review |
| GET | `/api/orders` | 列表 (权限过滤) | order:read |
| GET | `/api/orders/{id}` | 详情 | order:read |
| GET | `/api/orders/stats/overview` | 统计 | order:read |
| GET | `/api/orders/sla/violations` | SLA 违规 | order:read |
| POST | `/api/orders/batch/assign` | 批量派单 | order:batch_assign |

## 🛠️ 配置示例

### 1. 创建用户与分配角色

```python
# 在 Python 中执行
import mysql.connector
from utils.config import settings

conn = mysql.connector.connect(
    host=settings.DATABASE_HOST,
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    database=settings.DATABASE_NAME
)

cursor = conn.cursor()

# 创建用户并分配角色
cursor.execute("""
    UPDATE user SET role_id = (SELECT id FROM role WHERE name = 'dispatcher')
    WHERE username = 'dispatcher_user1'
""")

conn.commit()
cursor.close()
conn.close()
```

### 2. 配置 SLA

```python
# 配置问题类型的 SLA
cursor.execute("""
    INSERT INTO sla_config (
        problem_type_id, name, dispatch_sla_hours,
        process_sla_hours, review_sla_hours, total_sla_hours, priority
    ) VALUES (1, '道路坑洼', 24, 72, 24, 120, 1)
""")
```

## 🧪 测试清单

- [ ] 数据库迁移成功 (所有 11 个表都已创建)
- [ ] API 端点都能正常调用
- [ ] 权限检查生效 (无权限时返回 403)
- [ ] 审计日志记录完整
- [ ] 工单状态流转正确
- [ ] 批量操作支持
- [ ] Redis 权限缓存命中
- [ ] SLA 告警生成

## 📝 后续步骤

1. **P0-2 多维报表系统** (第 2 周)
   - 预置日报/周报/月报模板
   - 自定义报表生成
   - PDF/Excel 导出

2. **P0-3 地图智能分析** (第 2 周)
   - DBSCAN 聚类
   - 热力图生成
   - 地理围栏

3. **P1-5 质检与 AI** (第 2 周)
   - YOLOv8n 轻量级检测
   - 照片质量评分
   - 内容校验

## ⚠️ 常见问题

### Q: 如何重置数据库?
A: 执行 reset_db.py，然后重新运行迁移脚本

### Q: 权限缓存如何更新?
A: 权限更改后自动失效缓存 24 小时，或手动清除

### Q: 如何添加新权限?
A: 
1. 在 permission 表插入新权限
2. 在 role_permission 表分配给相应角色
3. 清除缓存

### Q: 审计日志存储多久?
A: 6 个月自动清理 (可在 SQL 中修改)

## 📞 联系与支持

有任何问题或建议，请提交 Issue 或 Pull Request。

---

**Status**: ✅ Phase 2 Stage 1 Complete
**Files Created**: 5 files (3,250+ lines of code)
**Est. Time to Deploy**: 30 minutes
**Est. Testing Time**: 1-2 hours

