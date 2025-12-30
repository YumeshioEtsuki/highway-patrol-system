## 🚀 快速开始

### 前置条件
- **Python 3.9+**
- **MySQL 8.0+** 运行中
- **Redis 5.0+**（可选，仅需要异步任务队列时）

### 一键启动

**仅启动后端 API：**
```bash
python quick_start.py
```

**启动后端 + Celery 任务队列：**
```bash
python quick_start.py --with-celery
```

**首次初始化数据库：**
```bash
python quick_start.py --reset
```

### 访问地址

- **API 文档**：http://127.0.0.1:5000/docs（Swagger UI）
- **应用首页**：http://127.0.0.1:5000
- **Celery Flower 监控**（仅启用 Celery 时）：http://127.0.0.1:5555

---

## 📁 项目目录结构（重构后）

```
1-后端代码/
├── app.py                          # FastAPI 应用入口
├── celery_app.py                   # Celery 任务队列配置
├── settings.py                     # 应用设置（从 utils/config.py 复制）
├── requirements.txt                # Python 依赖列表
├── README.md                       # 本文件
│
├── api/                            # API 路由（按域分组）
│   ├── auth/                       # 认证相关路由
│   │   └── routes.py               # 登录、注册、令牌管理
│   ├── patrol/                     # 巡查业务路由
│   │   ├── patrol_routes.py        # 巡查记录 CRUD
│   │   ├── photo_routes.py         # 照片管理
│   │   └── sse_routes.py           # 实时推送（SSE）
│   ├── admin/                      # 管理员路由
│   │   ├── admin_routes.py         # 管理功能
│   │   ├── reports_routes.py       # 报表导出
│   │   ├── monitor_routes.py       # 数据库监控
│   │   └── tasks_routes.py         # 任务队列管理
│   └── chat/                       # 聊天路由
│       └── routes.py               # 聊天接口
│
├── core/                           # 核心基础设施
│   ├── deps.py                     # JWT 认证、依赖注入
│   ├── auth.py                     # 密码加密、验证
│   ├── logger.py                   # 日志配置
│   ├── exceptions.py               # 自定义异常
│   ├── rate_limit.py               # 限流配置
│   ├── permissions.py              # 权限检查
│   └── sse.py                      # Server-Sent Events 管理
│
├── services/                       # 业务服务层
│   ├── patrol_service.py           # 巡查业务逻辑（原 models/tasks.py）
│   ├── report_service.py           # 报表业务逻辑（原 models/report_tasks.py）
│   ├── report_generator.py         # 报表生成引擎（CSV/Excel/PDF）
│   ├── china_regions.py            # 地区数据（GPS 坐标）
│   └── ...其他服务
│
├── workers/                        # Celery 异步任务（按队列分组）
│   ├── photo/                      # 照片处理队列
│   │   └── tasks.py                # 压缩、缩略图、批处理
│   ├── ai/                         # AI 质检队列
│   │   └── tasks.py                # 照片质量检查、场景识别
│   ├── report/                     # 报表生成队列
│   │   └── tasks.py                # 异步生成、定时推送、清理
│   └── maintenance/                # 系统维护队列
│       └── tasks.py                # 缓存清理、健康检查、指标收集
│
├── schemas/                        # Pydantic 数据模型
│   ├── base.py                     # 基础请求/响应（原 models/schemas.py）
│   ├── report.py                   # 报表相关（原 models/report_schemas.py）
│   └── order.py                    # 工单相关（原 models/order_schemas.py）
│
├── db/                             # 数据库相关
│   ├── schema.py                   # 建表 SQL（原 models/schema.py）
│   ├── report_models.py            # 报表 ORM（原 models/report_models.py）
│   └── order_models.py             # 工单 ORM（原 models/order_models.py）
│
├── scripts/                        # 工具脚本
│   ├── reset_db.py                 # 重建数据库
│   ├── add_hangzhou_data.py        # 导入杭州测试数据
│   └── update_imports.py           # 批量更新导入路径（重构工具）
│
├── utils/                          # 通用工具（仅保留无法迁移部分）
│   ├── config.py                   # 配置（已复制到 settings.py）
│   ├── utils.py                    # 数据库连接、SQL 执行
│   ├── redis_client.py             # Redis 连接
│   ├── algorithm.py                # 地理位置算法、距离计算
│   ├── index_analyzer.py           # 数据库索引分析
│   ├── slow_query_monitor.py       # 慢查询监控
│   ├── metrics_collector.py        # 性能指标收集
│   └── optimization_advisor.py     # 优化建议生成
│
├── static/                         # 静态文件
├── templates/                      # HTML 模板
├── uploads/                        # 文件上传目录（原 photos/）
├── exports/                        # 报表导出目录
└── logs/                           # 应用日志（app.log）
```

---

## ⚙️ 环境配置

### 1. 复制环境变量
```bash
cp 1-后端代码/.env.example 1-后端代码/.env
```

### 2. 修改 `.env` 文件
```ini
# 数据库
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=你的数据库密码
DATABASE_NAME=road_patrol_db

# Redis（可选，仅 Celery 需要）
REDIS_URL=redis://localhost:6379/0

# 应用
DEBUG=True
SECRET_KEY=你的密钥（任意字符串）
JWT_EXPIRE_HOURS=24

# 开发模式跳过 DB 初始化
SKIP_DB_INIT=0
```

---

## 🔄 工作流

### 首次使用
1. **初始化数据库**
   ```bash
   python quick_start.py --reset
   ```
   
2. **启动后端**
   ```bash
   python quick_start.py
   ```
   
3. **访问 API 文档**  
   打开浏览器访问 http://127.0.0.1:5000/docs

### 启用异步任务（Celery）
需要运行报表导出、照片处理等异步任务时：

```bash
# 确保 Redis 已启动，然后：
python quick_start.py --with-celery
```

此时会启动：
- **FastAPI 后端** (端口 5000)
- **Celery Worker** (处理任务)
- **Celery Beat** (定时任务调度)
- **Flower UI** (任务监控，端口 5555）

---

## 📊 数据库迁移

如需手动应用 SQL 脚本：
```bash
python 1-后端代码/scripts/reset_db.py
```

或在 Python REPL 中：
```python
from utils.utils import execute_sql_file
execute_sql_file('3-数据库/create_database.sql')
```

---

## 🧹 代码清理记录

本次重构执行了：
- ✅ 删除测试脚本：`test_*.py`, `verify_*.py`, `check_db_structure.py`
- ✅ 删除过时文件：`admin_old.py`, `orders.py`（对应的路由/模型）
- ✅ 清理日志：合并多个日志文件为 `logs/app.log`
- ✅ 目录重组：按功能域拆分 routes → api/{auth,patrol,admin,chat}
- ✅ 模块重构：models → schemas + services + db，utils → core + services
- ✅ 任务队列：tasks → workers/{photo,ai,report,maintenance}
- ✅ 配置统一：utils/config.py → settings.py（顶级）
- ✅ 批量修复：所有导入路径已自动更新

---

## 📝 故障排查

### 启动报错：ModuleNotFoundError
**原因**：依赖未安装或导入路径错误  
**解决**：
```bash
pip install -r 1-后端代码/requirements.txt
```

### 启动报错：无法连接数据库
**原因**：MySQL 未启动或配置错误  
**解决**：
```bash
# 检查 MySQL 状态
mysql -u root -p

# 检查 .env 中的数据库配置
cat 1-后端代码/.env
```

### 启动报错：端口 5000 被占用
**自动处理**：quick_start.py 会尝试自动清理占用进程  
**手动处理**：
```bash
# 查看占用端口的进程
netstat -ano | findstr :5000

# 强制关闭（Windows）
taskkill /F /PID <pid>
```

---

## 🔗 相关文档

- **API 接口文档**：见 `/docs`（Swagger）或 `/redoc`（ReDoc）
- **项目规划**：`4-文档/PHASE2_STAGE2_PLAN.md`
- **开发日志**：`6-开发日志/`

---

## 📞 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI | ≥0.104.0 |
| 认证 | JWT (python-jose) | ≥3.3.0 |
| 数据库 | MySQL | ≥8.0 |
| 缓存/队列 | Redis | ≥5.0 |
| 任务队列 | Celery | ≥5.3.0 |
| 数据验证 | Pydantic | ≥2.5.0 |
| 导出 | openpyxl, reportlab | ≥3.1.5 |
| 日志 | logging + custom | - |

---

**最后更新**：2025-12-24  
**重构版本**：v2.0.0 (结构化)
