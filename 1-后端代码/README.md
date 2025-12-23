# 公路巡查系统 - 后端 FastAPI 应用

> 完整的 RESTful API 后端，支持巡查记录管理、照片上传、实时推送、AI 聊天、地理数据统计。

## 快速开始

### 前置条件
- Python 3.9+
- MySQL 8.0+
- Ollama（可选，仅 AI 聊天功能需要）

### 安装与启动

1. **克隆项目并进入目录**
   ```bash
   cd highway-patrol-system
   ```

2. **创建虚拟环境（已有可跳过）**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # 或 source .venv/bin/activate  # Linux/Mac
   ```

3. **安装依赖**
   ```bash
   pip install -r 1-后端代码/requirements.txt
   ```

4. **配置环境**
   ```bash
   cp 1-后端代码/.env.example 1-后端代码/.env
   # 编辑 .env 填写 MySQL 信息
   ```

5. **启动后端**
   ```bash
   # 推荐：快速启动（自动初始化数据库）
   $env:SKIP_DB_INIT=0
   python quick_start.py
   
   # 或：跳过初始化（日常开发）
   $env:SKIP_DB_INIT=1
   python quick_start.py
   
   # 或：完整启动含索引优化
   cd 1-后端代码
   $env:SKIP_DB_INIT=1
   python start_server.py --apply-indexes
   ```

6. **验证运行**
   - 访问 http://127.0.0.1:5000 查看首页
   - 访问 http://127.0.0.1:5000/docs 查看 Swagger API 文档
   - 访问 http://127.0.0.1:5000/health 检查服务健康

## 项目结构

详见 [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)

核心模块：
- **models/** - 数据模型与数据库操作
- **routes/** - 六大 API 路由（user, patrol, admin, photo, SSE, chat）
- **utils/** - 工具层：配置、认证、算法、数据库
- **templates/** - HTML 模板（调试页面）
- **assets/** - 静态资源（GeoJSON）
- **photos/** - 照片存储（运行时创建）
- **logs/** - 日志文件（运行时创建）

## 核心功能

### 1. 用户认证
- **路由**：`routes/user.py`
- **功能**：注册、登录、JWT 认证
- **验证**：密码 Argon2 加密，JWT 24h 过期

**示例**
```bash
# 登录
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# 返回
{"access_token": "eyJ...", "token_type": "bearer"}

# 使用 Token 访问受保护端点
curl -X GET http://127.0.0.1:5000/api/patrol \
  -H "Authorization: Bearer eyJ..."
```

### 2. 巡查记录管理
- **路由**：`routes/patrol.py`
- **功能**：新增、查询、更新巡查记录 + 照片上传
- **数据库**：InspectionRecord（巡查）+ Photo（照片）表

**示例**
```bash
# 新增巡查记录（含照片）
curl -X POST http://127.0.0.1:5000/api/patrol \
  -H "Authorization: Bearer <token>" \
  -F "data={...}" \
  -F "photos=@photo1.jpg" \
  -F "photos=@photo2.jpg"

# 查询巡查记录
curl -X GET "http://127.0.0.1:5000/api/patrol?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

### 3. 管理后台
- **路由**：`routes/admin.py`
- **功能**：审核巡查记录、统计汇总、数据导出
- **权限**：仅 admin 角色可访问（通过 Depends(get_current_user) 验证）

**示例**
```bash
# 审核巡查记录
curl -X PUT http://127.0.0.1:5000/api/patrol/<id>/review \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "processing", "note": "已分派处理"}'

# 获取统计数据
curl -X GET "http://127.0.0.1:5000/api/statistics?scope=province&value=浙江省" \
  -H "Authorization: Bearer <token>"
```

### 4. 实时推送
- **路由**：`routes/patrol_sse.py`
- **功能**：Server-Sent Events 实时推送新上传的照片
- **应用**：前端可订阅 `/api/sse/photos` 获得实时更新

**示例**
```javascript
// 前端 JavaScript
const eventSource = new EventSource('/api/sse/photos', {
  headers: { 'Authorization': 'Bearer <token>' }
});
eventSource.onmessage = (event) => {
  console.log('新照片：', event.data);
};
```

### 5. 文件服务
- **路由**：`routes/photo.py`
- **功能**：静态文件服务，提供 `/photos/<filename>` 访问
- **存储**：`UPLOAD_FOLDER` 配置目录

**示例**
```bash
# 访问已上传的照片
curl http://127.0.0.1:5000/photos/inspectionrecord_12345_0.jpg
```

### 6. AI 聊天
- **路由**：`routes/chat.py`
- **功能**：集成 Ollama + 千问，支持巡查数据上下文聊天
- **依赖**：Ollama 服务运行（http://localhost:11434）

**示例**
```bash
# AI 聊天
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "上周统计的问题类型有哪些？"}'
```

## 数据库管理

### 初始化
- **自动执行**：启动时若表不存在，自动执行 `models/schema.py` 中的 SQL
- **跳过初始化**：设置 `SKIP_DB_INIT=1` 环境变量

### 表结构
```sql
-- 关键表
Department         -- 部门
User               -- 用户（认证）
RoadSegment        -- 路段
InspectionRecord   -- 巡查记录
Photo              -- 照片
ProblemType        -- 问题类型
```

详见 `models/schema.py`

### 索引优化
```bash
# 应用索引脚本以提升查询性能
python 1-后端代码/start_server.py --apply-indexes
```

脚本位置：`1-后端代码/indexes.sql`

## 配置详解

### `.env` 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_HOST` | MySQL 主机 | `localhost` |
| `DATABASE_PORT` | MySQL 端口 | `3306` |
| `DATABASE_USER` | MySQL 用户 | `root` |
| `DATABASE_PASSWORD` | MySQL 密码 | `REDACTED` |
| `DATABASE_NAME` | 数据库名 | `road_patrol_db` |
| `SECRET_KEY` | JWT 签名密钥 | `your-secret-key-min-32-chars` |
| `JWT_EXPIRE_HOURS` | JWT 过期时间（小时） | `24` |
| `DEBUG` | 调试模式 | `False` （生产）/ `True` （开发） |
| `ALLOW_ORIGINS` | CORS 允许源 | `["http://localhost:5000"]` |
| `UPLOAD_FOLDER` | 照片存储路径 | `1-后端代码/photos` |
| `MAX_UPLOAD_SIZE` | 最大上传大小（字节） | `10485760` （10MB） |
| `SKIP_DB_INIT` | 跳过数据库初始化 | `0` （执行） / `1` （跳过） |

### 开发 vs 生产配置

**开发环境**
```
DEBUG=True
ALLOW_ORIGINS=["*"]
SKIP_DB_INIT=0
```

**生产环境**
```
DEBUG=False
ALLOW_ORIGINS=["https://your-frontend.com"]
SECRET_KEY=<use-strong-random-key>
SKIP_DB_INIT=1
```

## API 文档

### 自动生成
- **Swagger UI**：http://127.0.0.1:5000/docs
- **ReDoc**：http://127.0.0.1:5000/redoc

### 健康检查
```bash
curl http://127.0.0.1:5000/health
```

返回
```json
{
  "status": "ok",
  "version": "1.0.0",
  "debug": false,
  "allow_origins": ["*"],
  "skip_db_init": "1"
}
```

## 开发指南

### 添加新的 API 端点

1. **定义 Pydantic 模型**（`models/schemas.py`）
   ```python
   class MyRequest(BaseModel):
       field1: str
       field2: int = 100
   ```

2. **编写数据库逻辑**（`models/tasks.py`）
   ```python
   def get_my_data(db_conn, filter_field):
       cursor = db_conn.cursor(dictionary=True)
       cursor.execute("SELECT * FROM MyTable WHERE field = %s", (filter_field,))
       return cursor.fetchall()
   ```

3. **创建路由**（`routes/my_route.py`）
   ```python
   from fastapi import APIRouter, Depends
   from utils.deps import get_current_user, CurrentUser
   
   router = APIRouter(prefix="/api/my", tags=["my_module"])
   
   @router.get("/endpoint")
   async def my_endpoint(
       current_user: CurrentUser = Depends(get_current_user)
   ):
       return {"message": "success"}
   ```

4. **注册路由**（`app.py`）
   ```python
   from routes import my_route
   app.include_router(my_route.router)
   ```

### 使用认证

所有需要用户身份的路由，添加依赖注入：
```python
from utils.deps import get_current_user, CurrentUser

@router.get("/protected")
async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
    print(f"User ID: {current_user.user_id}, Role: {current_user.role}")
    return {"user_id": current_user.user_id}
```

### 地理数据分析

查询时按省份或城市过滤：
```bash
# 按省份
/api/statistics?scope=province&value=浙江省

# 按城市（基于坐标距离计算）
/api/statistics?scope=city&value=杭州市
```

实现位置：`utils/algorithm.py`

### 调试与日志

日志存储在 `logs/` 目录，按日期命名：
```bash
logs/
├── 2025-12-22.log
└── 2025-12-23.log
```

## 性能优化建议

1. **数据库索引**
   ```bash
   python start_server.py --apply-indexes
   ```

2. **查询优化**
   - 使用 LIMIT/OFFSET 分页
   - 按条件索引列过滤
   - 避免 SELECT * 查询

3. **缓存**
   - 考虑使用 Redis 缓存高频查询

4. **压缩上传文件**
   - 使用 Pillow 库压缩照片

## 问题排查

| 问题 | 解决方案 |
|------|--------|
| 端口 5000 被占用 | `taskkill /F /IM python.exe` 或重启系统 |
| 数据库连接失败 | 检查 MySQL 运行、`.env` 配置、密码 |
| JWT token 无效 | 确保 header 格式 `Authorization: Bearer <token>` |
| 照片上传失败 | 检查 `/photos` 目录权限、文件大小（< 10MB）、扩展名（png/jpg/jpeg/gif） |
| 小程序无法连接 | 确保小程序 baseUrl 使用 LAN IP，检查防火墙 |

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com)
- [Pydantic 文档](https://pydantic-ai.jina.ai)
- [MySQL 文档](https://dev.mysql.com/doc/)
- [JWT 认证最佳实践](https://tools.ietf.org/html/rfc8949)
- [项目根目录文档](../4-文档/项目总结报告-核心要点.md)


## 📋 项目概述

这是一个高性能、生产就绪的公路巡查数据采集系统后端，由 **FastAPI** 框架驱动，集成了以下关键功能：

- **实时 SSE 推送**：照片和巡查数据实时推送到前端
- **JWT 认证**：安全的 token 支持的认证体系
- **管理员控制面板**：数据库运维、审计日志、统计分析
- **高性能优化**：连接池、缓存、索引、速率限制
- **可观测性**：请求耗时日志、审计跟踪

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **操作系统**: Windows / Linux / macOS

### 安装与启动

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量** (`.env` 文件)：
   ```bash
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_USER=root
   DATABASE_PASSWORD=REDACTED
   DATABASE_NAME=road_patrol_db
   DEBUG=False
   SECRET_KEY=your-secret-key-here-change-in-production
   JWT_EXPIRE_HOURS=24
   
   # 可选：性能优化配置
   DB_POOL_SIZE=10
   MAX_PAGE_SIZE=200
   APPLY_INDEXES_ON_START=1
   REDIS_URL=redis://localhost:6379
   STATS_CACHE_TTL=600
   
   # 可选：跳过数据库初始化（日常开发使用）
   SKIP_DB_INIT=1
   ```

3. **启动服务器**：
   ```bash
   # 方式 1：自动处理端口冲突（推荐）
   python start_server.py
   
   # 方式 2：直接使用 uvicorn
   uvicorn app:app --host 0.0.0.0 --port 5000
   ```

4. **验证运行**：
   - 访问 `http://127.0.0.1:5000` 查看前端
   - 访问 `http://127.0.0.1:5000/docs` 查看 Swagger API 文档
   - 访问 `http://127.0.0.1:5000/redoc` 查看 ReDoc 文档

---

## 📊 核心功能

### 1. 巡查记录管理 (`/api/patrol/*`)

- **上报记录**：`POST /api/patrol` - 创建新的巡查记录（含照片上传）
- **查询列表**：`GET /api/patrol/list` - 分页查询巡查记录
- **标记处理**：`POST /api/patrol/{id}/process` - 标记为"处理中"
- **标记完成**：`POST /api/patrol/{id}/complete` - 标记为"已完成"
- **导出**：`GET /api/export/excel` - 导出为 Excel

### 2. 实时推送 (`/api/sse/*`)

- **照片推送**：`GET /api/sse/patrol-photo` - Server-Sent Events 推送新照片
- **使用 token 认证**：需在 URL 中传递 `?token=<jwt_token>`

### 3. 用户认证 (`/api/user/*`)

- **登录**：`POST /api/user/login` - 获取 JWT token
- **注册**：`POST /api/user/register` - 创建新用户账户
- **获取用户信息**：`GET /api/me` - 获取当前登录用户信息
- **速率限制**：登录端点限制为 **5 次/分钟**

### 4. 管理员接口 (`/api/admin/*`)

- **审计日志**：
  - `GET /api/admin/audit` - 查询审计日志（分页）
  - `GET /api/admin/audit/export` - 导出审计日志为 CSV
  
- **统计分析**：
  - `GET /api/admin/stats` - 获取统计数据（含缓存）
  - `GET /api/public/stats` - 公开统计（无需认证）
  
- **数据库运维**（SSE 流式）：
  - `GET /api/reinit/stream` - 数据库重新初始化
  - `GET /api/verify/stream` - 数据完整性校验
  - `GET /api/status/stream` - 数据库状态检查
  
- **测试数据管理**：
  - `POST /api/admin/generate` - 生成虚拟巡查记录和照片
  - `POST /api/admin/clean-test-data` - 删除所有测试数据
  
- **敏感操作速率限制**：
  - `/api/reinit/stream`：1 次/分钟
  - `/api/admin/generate`：3 次/分钟
  - `/api/admin/clean-test-data`：2 次/分钟

---

## 🔧 性能优化

### 数据库优化

1. **连接池**（可选）
   - 启用：设置 `DB_POOL_SIZE > 0` 和 `REDIS_URL` (如果使用 Redis)
   - 默认 10 个连接，复用减少握手开销

2. **数据库索引**
   - 脚本位置：`3-数据库/add_indexes.sql`
   - 自动应用：设置 `APPLY_INDEXES_ON_START=1`
   - 索引包括：
     - `idx_user_id`：用户 ID 查询加速
     - `idx_status_time`：状态+时间复合索引
     - `idx_upload_time`：上传时间排序
     - `idx_problem_type`：问题类型统计

3. **统计缓存**
   - 启用：需配置 `REDIS_URL` 或自动使用内存缓存
   - TTL：默认 600 秒，可通过 `STATS_CACHE_TTL` 修改
   - 缓存键格式：`admin_stats:<filters_hash>`

### 应用层优化

1. **请求耗时日志**
   - 自动记录所有 HTTP 请求的处理时间
   - 日志文件：`logs/app_YYYY-MM-DD.log`

2. **分页限制**
   - 统一 `MAX_PAGE_SIZE=200`，防止超大查询
   - 自动在路由层夹紧 `page_size` 参数

3. **速率限制**
   - 关键登录：5 次/分钟
   - 数据库操作：1-3 次/分钟

---

## 🔐 安全性

### 认证与授权

- **JWT Token**：24 小时有效期（可通过 `JWT_EXPIRE_HOURS` 修改）
- **密码加密**：Argon2 算法（防彩虹表）
- **角色控制**：
  - `inspector`：巡查员，可上报和查看自己的记录
  - `admin`：管理员，可访问后台和执行敏感操作

### 审计跟踪

所有敏感操作被记录在 `audit_log` 表中：
- 标记记录状态变更
- 数据库重置
- 测试数据生成/清理
- 导出操作

**查询审计日志**：
```bash
GET /api/admin/audit?action=mark_completed&user_id=1&start_date=2025-01-01
```

### CORS 配置

在 `utils/config.py` 中定义 `ALLOW_ORIGINS`，示例：
```python
ALLOW_ORIGINS = ["http://localhost:5000", "https://example.com"]
```

---

## 📁 项目结构

```
1-后端代码/
├── app.py                 # FastAPI 应用入口
├── start_server.py        # 智能启动脚本
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
│
├── routes/               # API 路由
│   ├── patrol.py         # 巡查记录接口
│   ├── patrol_sse.py     # SSE 推送接口
│   ├── user.py           # 认证接口
│   ├── admin.py          # 管理员接口
│   └── photo.py          # 照片静态服务
│
├── models/               # 数据模型与业务逻辑
│   ├── schema.py         # SQL 建表语句
│   ├── schemas.py        # Pydantic 验证模型
│   ├── tasks.py          # 数据库操作（CRUD）
│   └── china_regions.py  # GPS 地理边界数据
│
├── utils/                # 工具模块
│   ├── config.py         # 配置管理
│   ├── utils.py          # 数据库连接、初始化
│   ├── auth.py           # 密码加密/验证
│   ├── deps.py           # 依赖注入（认证）
│   ├── logger.py         # 日志配置
│   ├── exceptions.py     # 自定义异常
│   ├── rate_limit.py     # 速率限制
│   ├── sse.py            # SSE 连接管理
│   └── algorithm.py      # GPS 过滤等算法
│
├── templates/            # HTML 前端模板
│   ├── index.html        # 巡查工作台
│   ├── admin.html        # 管理后台
│   ├── map.html          # 地图分析
│   └── ai-assistant.html # AI 浮窗
│
├── static/               # CSS / JS 静态资源
├── photos/               # 上传的照片存储
├── logs/                 # 日志文件
└── __pycache__/
```

---

## � 脚本位置说明（2025-12-23 整理）

为了保持后端代码目录的**清洁专注**，我们已将测试脚本和数据工具移动到专门目录。以下是整理后的新位置：

### ✅ 后端核心文件（保留在 1-后端代码）
- `app.py` - FastAPI 应用入口
- `start_server.py` - 启动脚本
- `constants.py` - 常数定义
- `requirements.txt` - Python 依赖
- `.env.example` - 配置模板
- `README.md` - 本文档

### ➡️ 移动到 7-测试脚本 的文件

#### 测试脚本
- **test_gps_filtering.py** - GPS 地理过滤功能测试
  ```bash
  python 7-测试脚本/test_gps_filtering.py
  ```
- **run_add_indexes.py** - 数据库索引初始化脚本
  ```bash
  python 7-测试脚本/run_add_indexes.py
  ```
- **test.html** - API 功能测试页面（手动打开）

#### 数据生成和重置工具
- **add_hangzhou_data.py** - 生成杭州地区测试数据
  ```bash
  python 7-测试脚本/add_hangzhou_data.py
  ```
- **reset_db.py** - 重置数据库（清空所有数据）
  ```bash
  python 7-测试脚本/reset_db.py
  ```

#### 临时调试脚本（隔离到 _deprecated）
- **tmp_check_db.py** - 临时数据库检查脚本
- **tmp_fix_datatype.py** - 临时字段类型修复脚本

### 整理效果
| 指标 | 改进 |
|------|------|
| 后端根目录文件数 | ↓ 60%（从 15 个精简到 6 个） |
| 代码清晰度 | ⭐⭐⭐⭐⭐ (从 ⭐⭐⭐ 提升) |
| 新人上手 | ⭐⭐⭐⭐ (快速识别核心代码) |
| 关注点分离 | ✓ 测试脚本独立，不干扰生产代码 |

### 详细整理说明
查看完整的整理文档：[后端目录整理](../6-开发日志/后端目录整理-2025-12-23.md)

---

## �🛠️ 常见问题

### Q1: 数据库连接失败

**症状**：`[MySQL] Connection failed: Access denied for user 'root'@'localhost'`

**排查步骤**：
1. 检查 MySQL 是否运行：`mysql -u root -p`
2. 验证 `.env` 中的数据库密码是否正确
3. 确认数据库存在：`SHOW DATABASES LIKE 'road_patrol_db';`

### Q2: 端口 5000 被占用

**症状**：`Address already in use`

**解决方案**：
- 使用 `start_server.py` 会自动清理占用的进程
- 或手动指定其他端口：`uvicorn app:app --port 8000`

### Q3: JWT token 无效

**症状**：`401 Unauthorized: Invalid authentication credentials`

**检查清单**：
- 请求头格式：`Authorization: Bearer <token>`（注意空格和 Bearer）
- Token 是否过期（默认 24 小时）
- 重新登录获取新 token

### Q4: 照片上传失败

**症状**：`413 Payload Too Large` 或 `415 Unsupported Media Type`

**可能原因**：
- 文件大小超过 10MB 限制（在 `config.py` 中修改 `MAX_UPLOAD_SIZE`）
- 文件格式不支持（仅允许 png/jpg/jpeg/gif，在 `routes/patrol.py` 中检查）
- `/photos` 目录权限不足

### Q5: 统计数据不更新

**症状**：缓存持久化，数据滞后

**解决方案**：
- 清除缓存：访问 `GET /api/admin/stats?nocache=1`（需要管理员权限）
- 或减小 `STATS_CACHE_TTL`（默认 600 秒）
- 或禁用缓存：删除 `REDIS_URL` 配置

---

## 📈 部署建议

### 开发环境

```bash
SKIP_DB_INIT=1
DEBUG=True
ALLOW_ORIGINS=["http://localhost:5000"]
```

### 生产环境

```bash
SKIP_DB_INIT=0          # 自动初始化数据库
DEBUG=False
ALLOW_ORIGINS=["https://yourdomain.com"]
SECRET_KEY=<random-strong-key>
JWT_EXPIRE_HOURS=12
DB_POOL_SIZE=20
REDIS_URL=redis://prod-redis:6379
STATS_CACHE_TTL=300
APPLY_INDEXES_ON_START=1
```

### 建议的启动脚本（systemd）

```ini
[Unit]
Description=Road Patrol System API
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/road-patrol-system/1-后端代码
Environment="PATH=/opt/road-patrol-system/venv/bin"
ExecStart=/opt/road-patrol-system/venv/bin/python start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔗 API 文档

完整的 API 文档可访问：
- **Swagger UI**：`http://localhost:5000/docs`
- **ReDoc**：`http://localhost:5000/redoc`

---

## 📝 变更日志

### v1.2.0 (2025-01-23)

#### ✨ 新功能
- **骨架屏加载**：统计卡片、图表和表格加载时显示骨架屏，提升用户体验
- **审计日志导出**：支持将管理员操作日志导出为 CSV 格式
- **数据库连接池**：可选的 MySQL 连接池支持，减少连接开销

#### ⚡ 性能优化
- **数据库索引脚本**：添加关键列的复合索引（状态+时间、上传时间等）
- **统计数据缓存**：支持 Redis 或内存缓存，TTL 可配置
- **请求耗时日志**：记录所有 HTTP 请求的处理时间以便性能分析

#### 🔐 安全增强
- **速率限制**：关键端点的请求频率限制（登录 5/分钟、DB 操作 1-3/分钟）
- **审计跟踪**：所有敏感操作被记录并可导出
- **环境变量规范化**：`.env.example` 文档齐全，便于部署

#### 🐛 Bug 修复
- 修复 SSE 连接断线后未自动重连的问题
- 修复大数据导出时内存溢出问题

### v1.1.0 (2025-01-15)
- 初始化项目
- 实现巡查记录管理、用户认证、实时推送
- 管理员后台与数据库运维工具

---

## 📞 技术支持

如有问题，请：
1. 检查本 README 的常见问题部分
2. 查阅项目文档：`4-文档/`
3. 检查日志：`logs/app_YYYY-MM-DD.log`

---

## 📄 许可证

Internal Project - All Rights Reserved

---

**最后更新**：2025-12-23
