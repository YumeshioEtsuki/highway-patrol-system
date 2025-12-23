# 后端目录结构说明

## 核心业务模块

```
1-后端代码/
├── app.py                      # FastAPI 主应用入口
│                              # - 生命周期管理（启动/关闭）
│                              # - CORS 中间件配置
│                              # - 路由注册（user, patrol, admin, photo, SSE）
│                              # - 静态文件挂载（/photos）
│                              # - 全局异常处理
│                              # - /health 健康检查端点
│
├── models/                     # 数据模型层
│   ├── schema.py              # SQL 建表语句（CREATE TABLE）
│   ├── schemas.py             # Pydantic 验证模型（API 请求/响应）
│   ├── tasks.py               # 数据库操作与事务管理
│   ├── china_regions.py       # 地理信息：34 省份 GPS 坐标范围
│   └── __init__.py
│
├── routes/                     # API 路由层（按功能模块划分）
│   ├── user.py                # 用户认证：登录/注册/JWT
│   ├── patrol.py              # 巡查记录：增删查改 + 照片上传
│   ├── patrol_sse.py          # Server-Sent Events：实时推送新照片
│   ├── admin.py               # 管理员：审核、统计、导出
│   ├── photo.py               # 照片：静态文件服务（/photos/<filename>）
│   ├── chat.py                # AI 聊天：集成 Ollama + 千问
│   └── __init__.py
│
├── utils/                      # 工具函数层
│   ├── config.py              # 配置管理：Pydantic Settings，.env 加载
│   ├── utils.py               # 数据库工具：连接、执行 SQL、初始化、密码哈希
│   ├── deps.py                # 依赖注入：获取当前用户、认证检查
│   ├── auth.py                # 认证工具：JWT、密码 (Argon2)
│   ├── sse.py                 # SSE 连接管理
│   ├── algorithm.py           # 算法：GPS 地理过滤、距离计算（Haversine）
│   └── __init__.py
│
├── assets/                     # 静态资源
│   └── world.json             # GeoJSON 世界地图（用于前端地图展示）
│
├── photos/                     # 照片存储目录（与前端 UPLOAD_FOLDER 一致）
│   │                          # 运行时动态创建，无需纳入版本控制
│   └── .gitkeep               # 占位符
│
├── logs/                       # 日志文件（运行时生成）
│   │                          # 示例：2025-12-23.log
│   └── .gitkeep               # 占位符
│
├── templates/                  # HTML 模板（前端调试页面）
│   ├── index.html             # 应用首页
│   ├── admin.html             # 管理后台页面（需后端角色检查）
│   ├── patrol.html            # 巡查记录页面
│   ├── map.html               # 地图展示页面（Leaflet + 高德 API）
│   ├── map_simple.html        # 简化地图页面
│   └── ai-assistant.html      # AI 助手聊天界面
│
├── .env.example               # 环境变量模板（开发参考）
├── .env                       # 实际环境变量（生产不提交）
│
├── app.py                     # [同上，核心应用]
├── start_server.py            # 启动脚本：端口清理、可选索引应用
├── constants.py               # 业务常量：数据类型、状态枚举
├── indexes.sql                # 数据库索引脚本（性能优化）
├── requirements.txt           # Python 依赖清单
├── README.md                  # 后端开发指南
│
└── __pycache__/               # Python 编译缓存（.gitignore）
```

## 快速查询

| 功能 | 文件 | 说明 |
|------|------|------|
| 用户登录 | `routes/user.py` | JWT 认证、密码验证 |
| 巡查记录 CRUD | `routes/patrol.py` | 新增、查询、更新巡查记录 |
| 照片上传 | `routes/patrol.py` + `routes/photo.py` | 文件验证、存储、静态服务 |
| 管理后台 | `routes/admin.py` | 审核、统计、导出 |
| 实时推送 | `routes/patrol_sse.py` | Server-Sent Events 新照片通知 |
| AI 聊天 | `routes/chat.py` | Ollama + 千问集成 |
| 地理过滤 | `utils/algorithm.py` | GPS 地理分析、坐标计算 |
| 数据库初始化 | `utils/utils.py` | 建表、插入初始数据、验证 |
| 配置管理 | `utils/config.py` | 环境变量、敏感信息处理 |

## 关键约定

### 1. 数据库初始化流程
- 启动时自动执行（除非设置 `SKIP_DB_INIT=1`）
- SQL 语句位置：`models/schema.py`（CREATE TABLE 语句列表）
- 数据库工具：`utils/utils.py`（execute_sql_file、initialize_database）

### 2. 认证与授权
- **入口**：`utils/deps.py` 的 `get_current_user()`
- **依赖注入**：使用 `Depends(get_current_user)` 保护路由
- **角色检查**：管理员路由需检查 `current_user.role == "admin"`
- **密码加密**：Argon2（`utils/auth.py`）

### 3. 文件上传
- **存储路径**：由 `settings.UPLOAD_FOLDER` 定义（默认 `1-后端代码/photos`）
- **访问 URL**：`/photos/<filename>` 通过静态挂载
- **验证**：`utils.py` 中 `allowed_file()` 检查扩展名
- **限制**：最大 10MB

### 4. GPS 地理过滤
- **数据源**：`models/china_regions.py`（34 省份坐标范围）
- **算法**：`utils/algorithm.py`（Haversine 距离公式）
- **用法**：`/api/statistics?scope=province&value=浙江省`

### 5. API 文档
- **Swagger UI**：`http://127.0.0.1:5000/docs`
- **ReDoc**：`http://127.0.0.1:5000/redoc`
- **健康检查**：`GET /health` 返回状态和配置摘要

## 启动与开发

### 快速启动（开发）
```bash
cd highway-patrol-system
$env:SKIP_DB_INIT=1
python quick_start.py
```

### 完整启动（含索引优化）
```bash
cd highway-patrol-system/1-后端代码
$env:SKIP_DB_INIT=1
python start_server.py --apply-indexes
```

### 环境配置
1. 复制 `.env.example` 为 `.env`
2. 填写 MySQL 连接信息与 JWT 密钥
3. 开发环境建议：`DEBUG=True`, `ALLOW_ORIGINS=["*"]`（需设 allow_credentials=false）
4. 生产环境建议：`DEBUG=False`, `ALLOW_ORIGINS=["your-frontend-domain"]`

## 代码风格约定

- **导入顺序**：标准库 → 第三方 → 本地模块
- **命名**：
  - 函数/变量：snake_case
  - 类：PascalCase
  - 常量：UPPER_SNAKE_CASE
- **类型提示**：新代码应包含类型注解
- **异常处理**：使用全局 exception_handler，不在路由中捕获

## 常见问题

**Q: 如何新增一个 API 端点？**  
A: 在 `routes/` 中创建 `@router.post/get` 装饰函数，在 `app.py` 中 `include_router()`

**Q: 如何修改数据库表结构？**  
A: 编辑 `models/schema.py` 或在 `3-数据库/` 创建 SQL 脚本，调用 `utils.execute_sql_file()` 执行

**Q: 如何保护 API？**  
A: 在路由函数参数添加 `current_user: CurrentUser = Depends(get_current_user)`

**Q: 照片上传到哪里？**  
A: `settings.UPLOAD_FOLDER`（默认 `1-后端代码/photos`），通过 `/photos/<filename>` 访问
