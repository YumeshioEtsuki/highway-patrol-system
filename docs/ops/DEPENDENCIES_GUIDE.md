# 🔧 系统依赖项与可选功能

本文档说明高速公路巡查系统的外部依赖项、可选功能及其影响。

## 📋 依赖项分类

### 🔴 关键依赖（必需）

| 依赖项 | 用途 | 安装方式 | 缺失影响 |
|--------|------|--------|--------|
| **MySQL 8.0+** | 核心数据库 | 手动安装或 Docker | ❌ 应用无法启动 |
| **Python 3.10+** | 运行时环境 | 安装官方版本 | ❌ 应用无法启动 |

### 🟡 强烈推荐（实际生产需要）

| 依赖项 | 用途 | 安装方式 | 缺失影响 |
|--------|------|--------|--------|
| **Docker Desktop** | 容器化部署、Redis 运行 | [安装链接](https://www.docker.com/products/docker-desktop/) | ⚠️ Redis 缓存功能不可用，降级内存缓存 |
| **Redis 7+** | 缓存、Celery Broker | Docker 或本地安装 | ⚠️ 缓存功能降级，异步任务队列失效 |

### 🟢 可选依赖（附加功能）

| 依赖项 | 用途 | 安装方式 | 缺失影响 |
|--------|------|--------|--------|
| **Ollama** | AI 聊天、照片分析 | [ollama.ai](https://ollama.ai) | ⚠️ AI 功能不可用，其他功能正常 |
| **Qwen 模型** | 千问 AI 模型 | `ollama pull qwen:7b` | ⚠️ AI 聊天功能失效 |

---

## 🚀 快速启动指南

### 方案 A: 最小化部署（仅数据库）

```bash
# 1. 安装 Python 3.10+ 并设置 .env 文件
cp 1-后端代码/.env.example 1-后端代码/.env
# 编辑 .env，设置 DATABASE_PASSWORD

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 3. 安装依赖
pip install -r 1-后端代码/requirements.txt

# 4. 手动启动应用
cd 1-后端代码
python bin/start_server.py
```

**功能限制：**
- ❌ 无异步任务（Celery）
- ❌ 无缓存优化
- ❌ 无 AI 功能
- ✅ 基础 CRUD 操作和报表功能正常

---

### 方案 B: 完整部署（推荐，需要 Docker）

```bash
# 自动启动 Redis + Celery + FastAPI
.\bin\startup_full.bat
```

**功能：**
- ✅ 异步任务队列（Celery）
- ✅ Redis 缓存
- ✅ 基础 CRUD 操作和报表

**Ollama 是可选的** — 如果需要 AI 功能，额外启动：

```bash
# 在另一个终端启动 Ollama（需先安装）
ollama serve
# 在另一个终端拉取模型（首次需要）
ollama pull qwen:7b
```

---

### 方案 C: 完整 Docker 部署（未来）

目前项目有 `Dockerfile`，但完整的 `docker-compose.yml` 还在规划中。

---

## 📊 功能对应的依赖关系

```
核心功能（CRUD、报表、仪表盘）
├── 必需: MySQL
├── 可选: Redis（缓存性能优化）
└── 可选: Docker（简化部署）

异步任务（报表导出、后台处理）
├── 必需: MySQL
├── 必需: Redis（Celery Broker）
├── 必需: Celery Worker（启动脚本自动处理）
└── 推荐: Docker（Redis 容器化）

AI 功能（聊天、照片分析）
├── 必需: MySQL
└── 必需: Ollama + Qwen 模型
```

---

## ⚙️ 启动检查说明

### 自动检查（在 `.\bin\startup_full.bat` 中）

脚本会在启动时自动检查：

| 检查项 | 结果 | 处理 |
|--------|------|------|
| **[1/6] Docker** | ✅ 可用 | 使用 Docker Redis |
|  | ❌ 不可用 | 尝试本地 Redis，失败则内存缓存 |
| **[2/6] Redis** | ✅ 运行 | 继续 |
|  | ❌ 不运行 | 如果 Docker 可用则启动容器 |
| **[4/6] Python** | ✅ 已安装 | 继续 |
|  | ❌ 未安装 | 停止并提示安装 |
| **[4.5/6] Ollama** | ✅ 运行 | 继续（AI 功能可用） |
|  | ⚠️ 未运行 | 警告但继续（AI 功能不可用） |
| **[5/6] Celery** | - | 自动启动新窗口 |
| **[6/6] FastAPI** | - | 启动应用 |

### 运行时检查（应用启动时）

在 `app.py` 中，应用启动时会检查：

```
[INFO] 检查外部依赖...
  [✓] database: 数据库已连接
  [✓] redis: Redis 已连接
  [⚠] ollama: Ollama 服务未运行 (缓存降级到内存)
```

---

## 🔧 故障排查

### 问题 1: "Redis 连接失败" 错误

**原因：** Docker 不运行或 Redis 容器未启动

**解决方案：**
```bash
# 启动 Docker Desktop
# 然后运行
docker start highway-redis
# 或完整启动
.\bin\startup_full.bat
```

### 问题 2: "AI 聊天返回错误"

**原因：** Ollama 未启动或 Qwen 模型未拉取

**解决方案：**
```bash
# 方案 1: 安装 Ollama
# 下载并安装 https://ollama.ai

# 方案 2: 启动 Ollama（已安装）
ollama serve

# 方案 3: 拉取 Qwen 模型（在另一个终端）
ollama pull qwen:7b
```

### 问题 3: "数据库连接失败"

**原因：** MySQL 未启动或密码错误

**解决方案：**
```bash
# 检查 .env 中的数据库配置
cat 1-后端代码\.env | findstr DATABASE_

# 确认 MySQL 正在运行（在 Windows 服务或终端中）
# 重新设置密码
.\bin\setup_password.bat
```

---

## 📝 环境变量配置

在 `1-后端代码/.env` 中配置：

```dotenv
# 数据库（必需）
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password_here

# Redis（可选，不设置则使用本地或内存缓存）
REDIS_HOST=localhost
REDIS_PORT=6379

# Ollama（可选，不设置则默认 127.0.0.1:11434）
OLLAMA_HOST=127.0.0.1
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen:7b
```

---

## 📚 进一步了解

- **Redis 安装指南**: [docs/ops/REDIS_DOCKER_GUIDE.md](./REDIS_DOCKER_GUIDE.md)
- **Ollama 集成**: [1-后端代码/routes/chat/routes.py](../1-后端代码/routes/chat/routes.py)
- **Celery 任务**: [1-后端代码/workers/](../1-后端代码/workers/)
- **启动脚本**: [bin/startup_full.bat](../bin/startup_full.bat)

---

## 🎯 推荐配置

### 开发环境
```
✅ 需要：Python 3.10+、MySQL、虚拟环境
⭐ 强烈推荐：Docker Desktop、Redis
📌 可选：Ollama（测试 AI 功能）
```

### 生产环境
```
✅ 需要：Python、MySQL、Redis
🔧 推荐：Docker 容器化、Kubernetes 编排
📌 按需：Ollama（如需 AI 功能）
```

---

**最后更新**：2025年12月29日
