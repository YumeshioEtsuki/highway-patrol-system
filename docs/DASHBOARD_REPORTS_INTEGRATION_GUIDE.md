# 仪表盘与报表系统 - 集成部署指南

## 目录
1. [系统架构](#系统架构)
2. [核心功能](#核心功能)
3. [部署步骤](#部署步骤)
4. [API 文档](#api-文档)
5. [前端集成](#前端集成)
6. [测试与验证](#测试与验证)
7. [故障排除](#故障排除)

---

## 系统架构

### 整体设计
本系统采用**配置驱动架构**，将 HTML 与 JSON 配置分离，实现：
- 🎯 **动态表单渲染**：通过 JSON 配置动态生成任务表单
- 🔄 **任务队列整合**：Celery 异步任务与前端轮询机制结合
- 📊 **实时 KPI 展示**：后端数据源驱动仪表盘实时更新
- 🔐 **统一请求处理**：CSRF、鉴权、错误处理集中在 APIClient

### 技术栈
- **后端**：FastAPI + Celery + Redis
- **前端**：Vanilla JavaScript（无框架依赖）
- **数据库**：PostgreSQL/MySQL
- **消息队列**：Redis Celery Broker

### 文件结构
```
1-后端代码/
├── app.py                           # FastAPI 主应用（含报表/KPI 路由）
├── celery_app.py                    # Celery 应用配置
├── workers/
│   └── report/
│       └── tasks.py                 # 报表异步任务定义
├── templates/
│   ├── dashboard.html               # 仪表盘页面
│   ├── reports.html                 # 报表中心页面
│   └── tasks.html                   # 任务中心页面
├── static/js/
│   ├── common.js                    # 通用工具库（APIClient, 通知等）
│   ├── tasks.js                     # 任务管理器（TaskManager）
│   ├── reports.js                   # 报表配置与表单渲染
│   └── dashboard.js                 # 仪表盘配置与 KPI 渲染
└── requirements.txt                 # 依赖清单
```

---

## 核心功能

### 1. 报表导出（异步）
**功能**：导出 Excel/PDF 报表，支持日期范围和照片包含选项
- Excel 导出：大型数据集分页处理
- PDF 导出：基于 Excel 导出转换
- 月报生成：按年月生成统计月报

### 2. 仪表盘 KPI
**功能**：实时显示运营关键指标
- 今日任务数：基于当日数据统计
- 任务成功率：已完成 / 总数比例
- 平均耗时：完成时间 - 创建时间
- 活跃用户：当日操作用户数

### 3. 任务轮询
**功能**：前端定时查询任务状态，支持多队列任务
- Celery 任务状态同步
- 实时 UI 更新
- 自动失败重试退避

---

## 部署步骤

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Redis（如未启动）
redis-server

# 启动 Celery Worker（报表任务队列）
celery -A celery_app worker -l info -Q report

# 可选：启动 Celery Beat（定时任务）
celery -A celery_app beat -l info
```

### 2. 后端启动
```bash
# 开发模式（自动重载）
python -m uvicorn app:app --reload --host 127.0.0.1 --port 5000

# 或使用现有启动脚本
python app.py
```

访问：http://127.0.0.1:5000

### 3. 验证静态资源
确保以下文件存在：
```bash
ls -la static/js/
# 输出应包括：
# - common.js
# - tasks.js
# - reports.js
# - dashboard.js
```

### 4. 数据库初始化（如需要）
```bash
# 初始化数据库（自动执行）
python -c "from utils.utils import initialize_database; initialize_database()"

# 或跳过初始化
export SKIP_DB_INIT=1
python app.py
```

---

## API 文档

### 报表 API

#### 1. 导出 Excel
```http
POST /api/reports/export/excel
Content-Type: application/json
Authorization: Bearer <token>

{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "include_photos": "yes"
}

响应 (200):
{
    "task_id": "abc123def456",
    "status": "queued",
    "include_photos": "yes"
}
```

#### 2. 导出 PDF
```http
POST /api/reports/export/pdf
Content-Type: application/json

{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "title": "2024 年度报告"
}

响应 (200):
{
    "task_id": "xyz789abc123",
    "status": "queued",
    "title": "2024 年度报告"
}
```

#### 3. 生成月报
```http
POST /api/reports/monthly/generate
Content-Type: application/json

{
    "year": 2024,
    "month": 12
}

响应 (200):
{
    "task_id": "taREDACTED2024-12",
    "status": "queued",
    "year": 2024,
    "month": 12
}
```

#### 4. 查询任务状态
```http
GET /api/reports/task/{task_id}

响应 (200):
{
    "task_id": "abc123def456",
    "state": "SUCCESS",
    "result": {
        "file_path": "exports/patrol_report_20241226_143022.xlsx",
        "records_count": 1523,
        "file_size": 2457600
    },
    "error": null
}

可能的 state 值：
- PENDING：等待中
- STARTED：已启动
- RUNNING：执行中
- SUCCESS：已完成
- FAILURE：失败
- RETRY：重试中
```

#### 5. 下载报表文件
```http
GET /api/reports/download?file_path=exports/patrol_report_20241226_143022.xlsx

响应：二进制文件流
```

### KPI API

#### 1. 今日任务数
```http
GET /api/dashboard/kpi/today_tasks

响应 (200):
{
    "label": "今日任务",
    "value": 18
}
```

#### 2. 任务成功率
```http
GET /api/dashboard/kpi/success_rate

响应 (200):
{
    "label": "成功率",
    "value": "97%"
}
```

#### 3. 平均耗时
```http
GET /api/dashboard/kpi/avg_latency

响应 (200):
{
    "label": "平均耗时",
    "value": "1.4s"
}
```

#### 4. 活跃用户
```http
GET /api/dashboard/kpi/active_users

响应 (200):
{
    "label": "活跃用户",
    "value": 12
}
```

#### 5. 最近任务列表
```http
GET /api/dashboard/recent-tasks?limit=10

响应 (200):
{
    "recent_tasks": [
        {
            "task_id": "abc123",
            "name": "导出 Excel",
            "state": "SUCCESS"
        },
        ...
    ]
}
```

---

## 前端集成

### 1. 页面访问
```
仪表盘：http://127.0.0.1:5000/dashboard.html
报表中心：http://127.0.0.1:5000/reports.html
任务中心：http://127.0.0.1:5000/tasks.html
```

### 2. JavaScript 依赖树
```
HTML 页面
    ├── common.js（通用工具）
    │   ├── APIClient（HTTP 请求 + CSRF）
    │   ├── showNotification（通知提示）
    │   └── 其他工具函数
    ├── tasks.js（任务管理器）
    │   ├── TaskManager（任务存储 + 轮询）
    │   └── FormRenderer（动态表单渲染）
    └── 页面专有脚本
        ├── reports.js（报表页面）
        ├── dashboard.js（仪表盘页面）
        └── 其他
```

### 3. 表单提交流程
```
用户填表并点击提交
    ↓
validateFields（客户端验证）
    ↓
APIClient.post(endpoint, payload)（发送请求 + CSRF）
    ↓
后端处理并返回 { task_id, status, ... }
    ↓
TaskManager.submit()（添加任务到本地存储）
    ↓
TaskManager.startPolling(task_id)（启动轮询）
    ↓
renderTasksList()（UI 实时更新）
```

### 4. 配置扩展示例

添加新的报表任务（在 `reports.js` 中）：
```javascript
const REPORT_TASK_CONFIG = {
    new_category: {
        icon: '📋',
        name: '新分类',
        tasks: {
            new_task: {
                label: '新任务',
                endpoint: '/api/new/endpoint',
                fields: [
                    {
                        name: 'param1',
                        type: 'text',
                        label: '参数 1',
                        required: true
                    }
                ]
            }
        }
    }
};
```

相应后端接口（在 `app.py` 中）：
```python
@app.post("/api/new/endpoint")
async def new_endpoint(request: Request):
    data = await request.json()
    # 提交 Celery 任务或直接处理
    task = some_celery_task.apply_async(args=[...])
    return {"task_id": task.id, "status": "queued"}
```

---

## 测试与验证

### 1. 单元测试
```bash
# 运行集成测试
pytest tests/test_dashboard_reports_integration.py -v

# 测试特定功能
pytest tests/test_dashboard_reports_integration.py::TestReportAPIs::test_export_excel_success -v
```

### 2. 手动测试清单
- [ ] 访问 `/dashboard.html` 验证 KPI 加载
- [ ] 点击报表中心按钮验证表单渲染
- [ ] 填表并提交验证 API 响应与 task_id
- [ ] 检查任务中心中新任务出现
- [ ] 观察任务状态从 PENDING → SUCCESS/FAILURE 转换
- [ ] 验证报表文件下载链接可用

### 3. 性能验证
```bash
# 检查任务轮询延迟（应 < 100ms）
# 检查 KPI API 响应时间（应 < 200ms）
# 检查内存占用（TaskManager 存储有界）
```

---

## 故障排除

### 问题 1：报表 API 返回 404
**原因**：后端路由未注册或静态资源未挂载

**解决**：
```bash
# 检查 app.py 是否包含以下路由
grep -n "def export_excel_report\|def kpi_today_tasks" app.py

# 检查静态资源是否已挂载
curl http://127.0.0.1:5000/static/js/common.js -I
```

### 问题 2：任务状态未更新
**原因**：Celery Worker 未启动或任务轮询停止

**解决**：
```bash
# 启动 Celery Worker
celery -A celery_app worker -l info -Q report

# 检查浏览器控制台是否有 JavaScript 错误
# 验证网络面板中 /api/reports/task/{task_id} 请求

# 查看 Celery 日志
tail -f celery.log
```

### 问题 3：CSRF 验证失败
**原因**：META 标签缺失或 APIClient CSRF 处理错误

**解决**：
```html
<!-- 检查 HTML 页面头部是否包含 CSRF META -->
<meta name="csrf-token" content="...">

<!-- 在浏览器控制台验证 -->
<script>
  console.log(document.querySelector('meta[name="csrf-token"]')?.content);
</script>
```

### 问题 4：KPI 显示默认值而非真实数据
**原因**：数据库连接失败或查询语句错误

**解决**：
```bash
# 检查数据库连接
python -c "from utils.utils import initialize_database; initialize_database()"

# 查看应用日志
# 修改 app.py 中的 KPI 函数添加真实数据库查询

# 验证 KPI 端点
curl http://127.0.0.1:5000/api/dashboard/kpi/today_tasks | jq .
```

---

## 最佳实践

### 1. 性能优化
- 使用内存缓存减少数据库查询（KPI）
- 批量导出时分页处理（报表）
- 轮询间隔不低于 2 秒（减少服务器压力）

### 2. 安全性
- 始终验证 CSRF token（自动在 APIClient 中处理）
- 输入验证（客户端 + 服务端双重验证）
- 文件下载时防止目录遍历攻击（已在 app.py 中实现）

### 3. 可维护性
- 配置与代码分离（TASK_CONFIG, DASHBOARD_CONFIG）
- 统一错误处理（APIClient, showNotification）
- 日志记录（app_logger, Celery logs）

### 4. 可扩展性
- 新任务：添加配置 + 实现 Celery Task
- 新 KPI：添加 GET 端点 + 配置引用
- 新队列：在 celery_app.py 中配置 task_routes

---

## 联系与支持

- 📧 反馈问题：查看 logs/ 目录中的应用日志
- 🐛 调试：浏览器 DevTools → Network/Console → 查看请求响应
- 📚 更多资料：见 docs/ 目录中的完整 API 文档

---

**最后更新**：2024-12-26
**版本**：2.0.0
