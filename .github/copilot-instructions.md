# AI 编程助手指南 - 公路巡查系统

## 项目概述
这是一个完整的公路巡查数据采集系统，由 **FastAPI 后端** + **微信小程序前端** + **MySQL 数据库** 组成。

### 目录结构
```
highway-patrol-system/
├── 1-后端代码/         # FastAPI 应用（主要开发区域）
├── 2-小程序代码/       # 微信小程序 (TypeScript/WXSS)
├── 3-数据库/           # SQL 初始化脚本
├── 4-文档/             # API、架构文档
└── 6-开发日志/         # 变更日志
```

---

## 核心架构

### 后端：FastAPI 应用 (`1-后端代码/app.py`)
**关键特性：**
- **生命周期管理**：启动时自动初始化数据库（通过 `SKIP_DB_INIT=1` 可跳过）
- **CORS 中间件**：已配置支持跨域请求（需改进：仅用于开发）
- **全局异常处理**：统一返回 JSON 错误响应
- **认证体系**：JWT token + 角色检查 (`get_current_user()`)

**数据库表关系：**
```
Department ← RoadSegment ← InspectionRecord ← Photo
         ↓                     ↓
       User        ProblemType
```

### 关键模块

#### 1. `routes/` - API 路由层
- **patrol.py**：巡查记录的增删查改（支持照片上传）
- **patrol_sse.py**：Server-Sent Events 实时推送新照片
- **user.py**：用户登录/注册 (JWT 验证)
- **admin.py**：管理员审核、报告统计
- **photo.py**：静态文件服务（`/photos/<filename>`）

#### 2. `models/` - 数据模型
- **schema.py**：SQL 建表语句（按外键顺序）
- **schemas.py**：Pydantic 验证模型（API 请求/响应）
- **tasks.py**：数据库操作（SQL 执行、事务管理）
- **china_regions.py**：34 省 GPS 坐标范围（用于地理过滤）

#### 3. `utils/` - 工具层
- **config.py**：环境变量配置（数据库、JWT、文件上传）
- **utils.py**：数据库连接、SQL 执行、初始化逻辑
- **auth.py**：密码加密/验证 (Argon2)
- **deps.py**：依赖注入（当前用户）
- **sse.py**：SSE 连接管理
- **algorithm.py**：算法（GPS 过滤、距离计算）

---

## 重要开发工作流

### 1. 启动后端
```bash
# 自动处理端口冲突（Windows）
python 1-后端代码/start_server.py

# 或手动启动（跳过 DB 初始化）
cd 1-后端代码
set SKIP_DB_INIT=1
uvicorn app:app --host 0.0.0.0 --port 5000
```

**调试访问：**
- 前端页面：`http://127.0.0.1:5000`
- Swagger 文档：`http://127.0.0.1:5000/docs`
- ReDoc 文档：`http://127.0.0.1:5000/redoc`

### 2. 数据库初始化
```bash
# 首次运行自动执行（见 app.py 启动事件）
python 1-后端代码/utils/utils.py  # 包含 initialize_database()

# 重置数据库
python 1-后端代码/reset_db.py

# 生成测试数据
python 1-后端代码/add_hangzhou_data.py
```

### 3. 添加新的 API 端点
**步骤：**
1. 在 `models/schemas.py` 定义 Pydantic 验证类
2. 在 `models/tasks.py` 编写 SQL 逻辑
3. 在 `routes/` 中创建 Router 函数，添加 `@router.post/get/put/delete`
4. 在 `app.py` 中 `include_router()`
5. **重要**：使用 `@Depends(get_current_user)` 进行身份验证

**示例：**
```python
# routes/my_route.py
@router.post("/my-endpoint")
async def my_endpoint(
    data: MySchema = ...,
    current_user: CurrentUser = Depends(get_current_user)
):
    # current_user.user_id, current_user.role 已自动验证
    pass
```

---

## 项目特定模式和约定

### 1. 文件上传处理
- **存储位置**：由 `settings.UPLOAD_FOLDER` 定义（默认 `1-后端代码/photos`）
- **访问方式**：静态挂载在 `/photos/<filename>`
- **验证**：使用 `allowed_file()` 检查扩展名（仅 png/jpg/jpeg/gif）
- **限制**：最大 10MB，详见 `config.py`

### 2. 数据库操作约定
- **连接**：每次请求通过 `get_db_connection()` 获取新连接
- **事务**：`autocommit=False`，需手动 `commit()` 或 `rollback()`
- **事务关键函数**：`create_patrol_record()` 中涉及多表插入
- **SQL 清理**：注释通过 `remove_comments_from_statement()` 移除

### 3. GPS 地理过滤
- **实现**：`utils/algorithm.py` 提供坐标计算函数
- **数据**：`models/china_regions.py` 包含 34 省份的 GPS 范围
- **用法**：
  ```python
  # 按省份过滤
  /api/statistics?scope=province&value=浙江省
  
  # 按市过滤（Haversine 距离）
  /api/statistics?scope=city&value=杭州市
  ```

### 4. 认证和授权
- **JWT 密钥**：`settings.SECRET_KEY`（开发环境；生产环境需改）
- **token 过期**：默认 24 小时（`JWT_EXPIRE_HOURS`）
- **角色检查**：User.role 为 `'inspector'` 或 `'admin'`
- **依赖注入**：
  ```python
  async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser
  ```

---

## 常见任务清单

### ✅ 修改数据库表
1. 编辑 `models/schema.py` 中的 SQL 语句
2. 或编写新的 `.sql` 文件放在 `3-数据库/`
3. 调用 `utils.py` 的 `execute_sql_file()` 执行

### ✅ 修改 API 响应格式
1. 更新 `models/schemas.py` 中的 Pydantic 类
2. 更新 `models/tasks.py` 的 SQL 查询结果映射
3. **注意**：保持向后兼容（小程序依赖当前格式）

### ✅ 添加新权限检查
1. 修改 `utils/deps.py` 中的 `get_current_user()` 或创建新的依赖
2. 在 routes 中使用 `Depends(your_check_func)`

### ✅ 测试 API
1. 打开 `/docs` Swagger 界面，直接测试
2. 或使用 `test.html`（前端页面）
3. 或参考 `test_gps_filtering.py` 编写测试脚本

---

## 部署和配置

### 环境变量（`.env` 文件）
```
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=REDACTED
DATABASE_NAME=road_patrol_db
DEBUG=True
SKIP_DB_INIT=1  # 仅在日常开发中使用
```

### 生产环境建议
- ❌ 关闭 `DEBUG=False`
- ❌ 使用复杂的 `SECRET_KEY`
- ❌ 限制 `ALLOW_ORIGINS` 只允许前端域名
- ✅ 启用 HTTPS 和 HSTS

---

## 性能优化建议

1. **数据库索引**：`indexes.sql` 已定义，通过 `EXPLAIN` 验证查询性能
2. **照片优化**：使用 Pillow 库压缩上传的图片
3. **缓存**：考虑使用 Redis 缓存高频查询（如统计数据）
4. **分页**：所有列表接口支持 `limit` 和 `offset` 参数

---

## 问题排查

| 问题 | 解决方案 |
|------|--------|
| 端口 5000 被占用 | `start_server.py` 自动清理；或手动 `taskkill /F /PID <pid>` |
| 数据库连接失败 | 检查 MySQL 运行、`.env` 配置、密码正确性 |
| JWT token 无效 | 确保 request header 格式：`Authorization: Bearer <token>` |
| 照片上传失败 | 检查 `/photos` 目录权限、文件大小、扩展名 |
| 小程序无法连接 | 检查服务器 IP、防火墙规则、CORS 配置 |

---

## 参考资源

- **FastAPI 官方文档**：https://fastapi.tiangolo.com
- **JWT 认证**：`routes/user.py` 中的 `login()` 函数示例
- **项目文档索引**：`4-文档/项目总结报告-核心要点.md`
- **API 规范**：待完善（见 `4-文档/API接口文档.md`）
