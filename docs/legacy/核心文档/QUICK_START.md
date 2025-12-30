# 🚀 公路巡查系统 - 项目快速启动指南

> 适合非开发者：一键启动完整系统，无需深入技术细节

---

## 📦 一、环境准备（首次运行）

### 必需软件
1. **Python 3.10+**（已安装：`python --version` 查看）
2. **MySQL 数据库**（推荐版本：8.0+）
3. **微信开发者工具**（仅用于小程序开发测试）

### 安装依赖
```bash
# 进入后端目录
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"

# 安装 Python 依赖
pip install -r requirements.txt
```

---

## 🎯 二、一键启动（推荐方式）

### Windows 用户
```powershell
# 方式1：使用启动脚本（自动处理端口冲突）
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
python start_server.py

# 方式2：直接启动 FastAPI
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
$env:SKIP_DB_INIT=1  # 跳过数据库初始化（已有数据时）
uvicorn app:app --host 0.0.0.0 --port 5000
```

**启动成功标志：**
```
==================================================
[OK] Application started successfully!
[INFO] Visit http://127.0.0.1:5000
[INFO] API docs http://127.0.0.1:5000/docs
==================================================
```

---

## 🌐 三、访问系统

| 入口 | 地址 | 说明 |
|------|------|------|
| **前端管理页面** | http://127.0.0.1:5000 | 浏览器直接访问（自动登录） |
| **API 交互文档** | http://127.0.0.1:5000/docs | Swagger UI，可测试所有接口 |
| **API 文档** | http://127.0.0.1:5000/redoc | ReDoc 格式文档 |
| **小程序预览** | 微信开发者工具 | 打开 `2-小程序代码` 目录 |

**默认账户：**
- 管理员：`admin` / `REDACTED`
- 巡查员：`inspector` / `inspector`

---

## 🔄 四、项目运行流程

### 系统启动顺序
```
1. MySQL 数据库运行
   ↓
2. FastAPI 后端启动 (端口 5000)
   ├── 自动连接数据库
   ├── 初始化表结构（首次）
   ├── 插入种子数据（用户、路段、问题类型）
   └── 启动 API 服务
   ↓
3. 前端页面可访问
   ↓
4. 小程序连接后端 API
```

### 关键组件

#### 1. 后端 FastAPI (`app.py`)
- **职责**：API 接口、数据库操作、文件上传、JWT 认证
- **启动命令**：`python start_server.py` 或 `uvicorn app:app`
- **配置文件**：`.env`（数据库、JWT、Redis 配置）
- **日志位置**：控制台输出 + `logs/` 目录

#### 2. 数据库 MySQL
- **表结构**：见 `3-数据库/create_database.sql`
- **种子数据**：`services/patrol_service.py` 中的 `_ensure_seed_data()`
- **测试数据**：运行 `7-测试脚本/add_hangzhou_data.py` 生成

#### 3. 前端页面
- **位置**：`1-后端代码/templates/` 和 `static/`
- **路由**：
  - `/` → 登录页
  - `/patrol` → 巡查员页面
  - `/admin` → 管理员页面

#### 4. 微信小程序
- **位置**：`2-小程序代码/`
- **配置**：`utils/config.js` 中设置后端 API 地址
- **测试**：微信开发者工具 → 打开目录 → 编译

---

## 🛠️ 五、常用维护操作

### 重置数据库
```bash
# 方式1：完全重置（删除所有数据）
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
python -c "import mysql.connector; from utils.config import db_config; conn = mysql.connector.connect(**db_config); cursor = conn.cursor(); cursor.execute('DROP DATABASE IF EXISTS road_patrol_db'); cursor.execute('CREATE DATABASE road_patrol_db'); conn.commit(); print('✅ 数据库已清空'); conn.close()"

# 然后初始化表结构和种子数据
python -c "import sys; sys.path.insert(0, '.'); from utils.utils import initialize_database; initialize_database()"
python -c "import sys; sys.path.insert(0, '.'); from services.patrol_service import _ensure_seed_data; from utils.utils import get_db_connection; conn = get_db_connection(); cursor = conn.cursor(); _ensure_seed_data(conn, cursor); cursor.close(); conn.close(); print('✅ 种子数据插入完成')"

# 方式2：仅清理测试数据（通过前端）
# 管理员登录 → 数据管理 → 点击"🗑️ 清理测试数据"
```

### 生成测试数据
```bash
cd "d:\MySQL Project\highway-patrol-system\7-测试脚本"
$env:PYTHONPATH="d:\MySQL Project\highway-patrol-system\1-后端代码"
python add_hangzhou_data.py
```

### 重启服务器
```powershell
# 方式1：Ctrl+C 停止后重新运行
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
python start_server.py

# 方式2：清理端口后启动
$port = 5000
netstat -ano | Select-String ":$port " | ForEach-Object { 
    if ($_ -match '\s+(\d+)\s*$') { 
        Stop-Process -Id $Matches[1] -Force -ErrorAction SilentlyContinue
    } 
}
Start-Sleep -Seconds 2
python start_server.py
```

---

## ⚙️ 六、配置文件说明

### `.env` 文件（需自行创建）
```env
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=REDACTED
DATABASE_NAME=road_patrol_db

# 应用配置
DEBUG=True
SECRET_KEY=road_patrol_dev_secret_2025_do_not_use_in_production

# Redis 缓存（可选，未安装会自动使用内存缓存）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 跳过初始化（日常开发）
SKIP_DB_INIT=1
```

---

## 🚨 七、常见问题排查

| 问题 | 解决方案 |
|------|--------|
| **端口 5000 被占用** | 运行 `python start_server.py`（自动清理）或手动 `netstat -ano | findstr :5000` 查找进程并结束 |
| **数据库连接失败** | 检查 MySQL 是否运行、`.env` 配置是否正确、密码是否匹配 |
| **JWT token 无效** | 前端清除 localStorage、重新登录获取新 token |
| **小程序无法连接** | 检查 `utils/config.js` 中的 `BASE_URL`、确保后端已启动、关闭防火墙 |
| **照片上传失败** | 检查 `1-后端代码/photos/` 目录是否存在、权限是否正确、文件大小是否超过 10MB |
| **重置后列表未清空** | 已修复：清理缓存现在会同时清除统计和列表缓存 |
| **路段选项不匹配** | 已修复：统一为"G1 京哈高速"格式，共 33 个路段 |
| **问题类型无 emoji** | 已修复：所有顶层类型都包含 emoji（🛣️🚧🚥💧❓） |

---

## 📊 八、系统数据流

```
用户操作
  ↓
前端页面/小程序
  ↓
FastAPI API (/api/*)
  ↓
services/patrol_service.py (业务逻辑)
  ↓
MySQL 数据库
  ↓
返回 JSON 响应
```

**关键文件路径：**
- **路由定义**：`api/*/routes.py`
- **业务逻辑**：`services/patrol_service.py`
- **数据模型**：`db/schema.py`（SQL）、`models/schemas.py`（Pydantic）
- **认证逻辑**：`utils/deps.py`（JWT 验证）
- **配置管理**：`settings.py`、`.env`

---

## 🎓 九、开发建议

### 如果你想修改功能：
1. **修改 API 逻辑**：编辑 `services/patrol_service.py`
2. **添加新接口**：在 `api/` 目录对应模块添加路由
3. **修改数据库表**：编辑 `db/schema.py`，然后重置数据库
4. **修改前端页面**：编辑 `templates/*.html`
5. **修改小程序**：编辑 `2-小程序代码/pages/`

### 如果遇到错误：
1. 查看控制台日志（运行服务器的终端）
2. 访问 `/docs` 测试 API 是否正常
3. 检查浏览器开发者工具的 Network 标签
4. 查看 `logs/` 目录下的日志文件

---

## 📚 十、扩展资源

- **项目总结**：`4-文档/项目总结报告-核心要点.md`
- **API 文档**：`4-文档/API接口文档.md`
- **开发日志**：`6-开发日志/`
- **FastAPI 官方文档**：https://fastapi.tiangolo.com
- **MySQL 教程**：https://www.runoob.com/mysql/mysql-tutorial.html

---

## ✅ 十一、版本特性说明

### v2.0 新增功能（当前版本）
- ✅ **Redis 缓存**：统计数据和列表缓存（10分钟/5分钟 TTL）
- ✅ **问题类型 Emoji**：🛣️路面破损、🚧护栏损坏、🚥标线模糊、💧排水系统、❓其他问题
- ✅ **扩展路段库**：33 个路段（国道 + 省道 + 高速），统一命名格式
- ✅ **缓存清理优化**：重置数据时同时清空统计和列表缓存
- ✅ **自动端口清理**：`start_server.py` 自动处理端口冲突

### 与 v1.0 的主要区别
- **缓存系统**：新增 Redis 支持，但未安装时自动降级到内存缓存
- **数据呈现**：路段和问题类型格式更规范，增强用户体验
- **性能优化**：高频查询接口使用缓存，减少数据库压力

---

## 🎉 十二、快速验证

运行以下命令验证系统状态：
```bash
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
python verify_seed.py
```

**预期输出：**
```
路段数量: 33

前8个路段:
  - G1 京哈高速
  - G2 京沪高速
  ...

问题类型数量: 9

顶层问题类型 (应该包含 emoji):
  - 🛣️ 路面破损
  - 🚧 护栏损坏
  - 🚥 标线模糊
  - 💧 排水系统
  - ❓ 其他问题
```

---

**祝使用愉快！如有问题请查看日志或联系开发者。** 🚗💨
