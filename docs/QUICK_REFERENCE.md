# 仪表盘与报表系统 - 快速参考卡

## 📌 系统概览

| 项目 | 说明 |
|------|------|
| **系统名称** | 公路巡查系统 - 仪表盘与报表模块 |
| **版本** | 2.0.0 |
| **更新日期** | 2024-12-26 |
| **架构** | FastAPI + Celery + Redis |
| **状态** | 完整集成，就绪部署 |

---

## 🚀 快速启动（5 分钟）

### 前置检查
```bash
# 1. 检查 Redis 运行
redis-cli ping
# 输出：PONG ✅

# 2. 检查 Python 3.9+
python --version
# 输出：Python 3.x.x ✅
```

### 启动服务
```bash
# 终端 1：启动 Celery Worker
cd 1-后端代码
celery -A celery_app worker -l info -Q report

# 终端 2：启动 FastAPI 应用
cd 1-后端代码
python -m uvicorn app:app --reload

# 终端 3：运行验证脚本
cd ..
python bin/verify-dashboard-reports.py
```

### 访问页面
| 页面 | URL |
|------|-----|
| 仪表盘 | http://127.0.0.1:5000/dashboard.html |
| 报表中心 | http://127.0.0.1:5000/reports.html |
| 任务中心 | http://127.0.0.1:5000/tasks.html |
| API 文档 | http://127.0.0.1:5000/docs |

---

## 📊 API 速查表

### 报表 API
```bash
# 导出 Excel
curl -X POST http://127.0.0.1:5000/api/reports/export/excel \
  -H "Content-Type: application/json" \
  -d '{"start_date":"2024-01-01","end_date":"2024-12-31","include_photos":"no"}'

# 导出 PDF
curl -X POST http://127.0.0.1:5000/api/reports/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"start_date":"2024-01-01","end_date":"2024-12-31","title":"2024 报告"}'

# 生成月报
curl -X POST http://127.0.0.1:5000/api/reports/monthly/generate \
  -H "Content-Type: application/json" \
  -d '{"year":2024,"month":12}'

# 查询任务状态（用返回的 task_id）
curl http://127.0.0.1:5000/api/reports/task/{task_id}
```

### KPI API
```bash
# 今日任务
curl http://127.0.0.1:5000/api/dashboard/kpi/today_tasks

# 成功率
curl http://127.0.0.1:5000/api/dashboard/kpi/success_rate

# 平均耗时
curl http://127.0.0.1:5000/api/dashboard/kpi/avg_latency

# 活跃用户
curl http://127.0.0.1:5000/api/dashboard/kpi/active_users

# 最近任务
curl "http://127.0.0.1:5000/api/dashboard/recent-tasks?limit=10"
```

---

## 🎯 用户场景

### 场景 1：导出月度报表
```
1. 打开 http://127.0.0.1:5000/reports.html
2. 点击"导出 Excel"
3. 选择日期范围（例：2024-01-01 ~ 2024-12-31）
4. 点击"提交"
5. 等待任务完成（在任务中心查看状态）
6. 点击下载链接获取 Excel 文件
```

### 场景 2：查看运营概览
```
1. 打开 http://127.0.0.1:5000/dashboard.html
2. 看到 4 个 KPI：
   - 今日任务：18
   - 成功率：97%
   - 平均耗时：1.4s
   - 活跃用户：12
3. 下方显示最近 10 项任务
4. 点击"刷新 KPI"手动更新数据
```

### 场景 3：跟踪异步任务
```
1. 在 /reports.html 或 /tasks.html 提交任务
2. 任务提交后自动显示在"任务中心"
3. 状态自动轮询更新（每 2 秒）
4. 完成后显示"✅ 已完成"，失败显示"❌ 失败"
```

---

## 📂 文件导航

| 文件 | 位置 | 用途 |
|------|------|------|
| **app.py** | 1-后端代码/ | FastAPI 主应用（所有 API 路由） |
| **dashboard.html** | 1-后端代码/templates/ | 仪表盘页面 |
| **reports.html** | 1-后端代码/templates/ | 报表页面 |
| **common.js** | 1-后端代码/static/js/ | HTTP 客户端 + CSRF |
| **tasks.js** | 1-后端代码/static/js/ | 任务管理器与轮询 |
| **dashboard.js** | 1-后端代码/static/js/ | KPI 渲染 |
| **reports.js** | 1-后端代码/static/js/ | 报表表单配置 |
| **GUIDE.md** | docs/ | 完整部署指南 |
| **test_*.py** | tests/ | 单元与集成测试 |
| **verify-*.py** | bin/ | 快速验证脚本 |

---

## ⚙️ 配置修改

### 修改轮询间隔
```javascript
// 在 tasks.js 中，约第 430 行
}, 2000);  // 改为需要的毫秒数（默认 2000ms）
```

### 添加新的 KPI
```python
# 在 app.py 中添加新的 GET 端点
@app.get("/api/dashboard/kpi/custom_metric")
async def kpi_custom_metric():
    return {"label": "自定义指标", "value": 123}

# 在 dashboard.js 中添加到配置
const DASHBOARD_CONFIG = {
    kpis: [
        // ...现有 KPI...
        { key: 'custom_metric', label: '自定义指标', fetch: '/api/dashboard/kpi/custom_metric' }
    ]
};
```

### 修改报表表单
```javascript
// 在 reports.js 中修改 REPORT_TASK_CONFIG
const REPORT_TASK_CONFIG = {
    export_category: {
        icon: '📊',
        name: '导出',
        tasks: {
            custom_export: {
                label: '自定义导出',
                endpoint: '/api/custom/export',
                fields: [
                    // 添加表单字段
                    { name: 'param', type: 'text', label: '参数', required: true }
                ]
            }
        }
    }
};
```

---

## 🐛 常见问题排查

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| 静态资源 404 | common.js/tasks.js 加载失败 | 检查 `/static/js/` 文件是否存在 |
| API 连接失败 | 网络请求超时 | 确保后端运行在 127.0.0.1:5000 |
| 任务无法更新 | 任务状态停留在 PENDING | 启动 Celery Worker；检查 Redis 连接 |
| CSRF 验证失败 | 提交报错 "CSRF token required" | 确保 HTML 包含 `<meta name="csrf-token">` |
| KPI 显示默认值 | 数据未从数据库加载 | 修改 app.py 中的 KPI 函数添加数据库查询 |

---

## 📈 性能优化

### 数据库查询优化
```python
# ❌ 坏：每次查询全表
@app.get("/api/dashboard/kpi/today_tasks")
async def kpi_today_tasks():
    result = db.query("SELECT COUNT(*) FROM patrols")
    return {"label": "今日任务", "value": result}

# ✅ 好：使用缓存
from functools import lru_cache
@lru_cache(maxsize=1)
def get_today_tasks():
    return db.query("SELECT COUNT(*) FROM patrols WHERE DATE(created_at)=CURDATE()")

@app.get("/api/dashboard/kpi/today_tasks")
async def kpi_today_tasks():
    return {"label": "今日任务", "value": get_today_tasks()}
```

### 前端优化
```javascript
// ❌ 坏：重复轮询相同任务
for (let i = 0; i < 100; i++) {
    TaskManager.startPolling(taskId);  // 重复 100 次！
}

// ✅ 好：检查是否已轮询
if (!TaskManager.pollers.has(taskId)) {
    TaskManager.startPolling(taskId);
}
```

---

## 🔐 安全检查清单

- [ ] CSRF token 在所有表单中正确配置
- [ ] API 请求必须通过 APIClient（自动注入 token）
- [ ] 文件下载路径验证（已在 app.py 中实现）
- [ ] 日期输入验证（客户端 + 服务端）
- [ ] 数据库查询使用参数化（防 SQL 注入）
- [ ] 错误消息不泄露敏感信息

---

## 📞 支持与反馈

### 日志位置
```bash
# 应用日志
less logs/app.log

# Celery 任务日志
celery -A celery_app worker -l debug

# 浏览器控制台
F12 → Console → 查看 JS 错误
```

### 调试技巧
```javascript
// 在浏览器控制台查看任务状态
console.log(TaskManager.getAllTasks());

// 查看 CSRF token
console.log(document.querySelector('meta[name="csrf-token"]').content);

// 查看 API 请求详情
// F12 → Network → 选择请求 → 查看 Headers/Response
```

### 获取帮助
1. 查看 [DASHBOARD_REPORTS_INTEGRATION_GUIDE.md](../docs/DASHBOARD_REPORTS_INTEGRATION_GUIDE.md)
2. 运行 `python bin/verify-dashboard-reports.py` 检查系统状态
3. 检查 logs/ 中的错误日志
4. 查看 tests/ 中的测试用例了解预期行为

---

## 📋 快速命令

```bash
# 启动所有服务
redis-server &
cd 1-后端代码
celery -A celery_app worker -Q report &
python -m uvicorn app:app --reload &

# 验证系统就绪
python ../bin/verify-dashboard-reports.py

# 运行测试
cd ..
pytest tests/test_dashboard_reports_integration.py -v

# 清空任务队列
celery -A celery_app purge -f

# 查看 API 文档
# 打开 http://127.0.0.1:5000/docs
```

---

**版本**：2.0.0  
**最后更新**：2024-12-26  
**状态**：生产就绪 ✅
