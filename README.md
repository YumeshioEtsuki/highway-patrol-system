# 公路巡查数据采集系统

> **Highway Patrol Data Collection System**  
> 基于 FastAPI + 微信小程序 + MySQL 的完整解决方案

## 🚀 快速开始

### 环境要求

#### 🔴 必需依赖
- **Python 3.10+** — 运行环境
- **MySQL 8.0+** — 核心数据库

#### 🟡 推荐依赖（生产环境必需）
- **Docker Desktop** — 容器化部署、Redis 运行
  - 快速启动：`.\bin\start_redis.bat`
- **Redis 7+** — 缓存和 Celery Broker
  - Docker 方式（推荐）或本地安装

#### 🟢 可选依赖（附加 AI 功能）
- **Ollama** — AI 聊天和照片分析
  - 下载：https://ollama.ai
  - 拉取模型：`ollama pull qwen:7b`

**详细依赖说明**：[docs/ops/DEPENDENCIES_GUIDE.md](./docs/ops/DEPENDENCIES_GUIDE.md)

### 🔐 安全配置（首次必做）

**1. 创建配置文件**
```powershell
# 复制配置模板
Copy-Item .env.example .env
```

**2. 修改数据库密码**
编辑 `.env` 文件，设置真实密码：
```env
DATABASE_PASSWORD=你的MySQL密码
```

⚠️ **重要**: `.env` 文件已被 `.gitignore` 排除，不会被提交到 Git。

详细配置说明：[docs/SECURITY_CONFIG.md](docs/SECURITY_CONFIG.md)

### ⚡ 一键启动

**完整功能（Redis + Celery + FastAPI）** - 推荐
```bash
# Windows
bin\startup_full.bat

# 启动内容：
# ✅ Redis 缓存服务（Docker 或本地，端口 6379）
# ✅ Celery 异步任务队列
# ✅ FastAPI 后端服务（端口 5000）
```

**仅启动 Redis（Docker 方式）** - 首次使用推荐
```bash
# 自动安装并启动 Docker Redis
bin\start_redis.bat

# 或使用 PowerShell
bin\start_redis.ps1
```

**基础功能（仅 FastAPI）**
```bash
# Windows
bin\startup.bat

# 或手动启动
cd src
python bin\start_server.py
```

**停止所有服务**
```bash
bin\stop_all.bat
```

### 📖 详细说明

- [完整启动指南](docs/ops/STARTUP_GUIDE.md) - Redis安装、手动启动、监控
- [Redis与Celery说明](4-文档/功能说明/REDIS_CELERY说明.md) - 异步架构详解

### 🔗 访问地址

服务器启动后访问：
- 管理后台：http://localhost:5000
- API 文档：http://localhost:5000/docs
- ReDoc：http://localhost:5000/redoc
- Celery监控：http://localhost:5555 (需先安装 `pip install flower` 并启动)

### 数据库初始化

```bash
cd database
# 按顺序执行SQL文件
mysql -u root -p < 00_init_schema.sql
mysql -u root -p < 01_migration_schema.sql
mysql -u root -p < 02_create_indexes.sql
mysql -u root -p < 03_seed_test_data.sql
```

## 📂 项目结构

```
highway-patrol-system/
├── src/                   # FastAPI 后端（原"1-后端代码"）
├── miniprogram/           # 微信小程序（原"2-小程序代码"）
├── database/              # SQL 脚本（原"3-数据库"）
├── docs/                  # 项目文档（整合）
│   ├── legacy/           # 原"4-文档"内容
│   ├── project-management/ # 原"00-项目管理"
│   ├── changelog/        # 原"6-开发日志"
│   ├── ops/              # 运维文档
│   └── diagnostics/      # 诊断文档
├── tests/                 # 测试工具（整合"7-测试脚本"）
├── scripts/               # 运维脚本
├── assets/                # 演示资料（原"5-演示材料"）
├── bin/                   # 启动脚本
├── tooling/               # 开发工具
└── logs/                  # 日志文件
```

**详细结构：** 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📚 文档导航

### 🔧 项目管理
- [项目结构说明](PROJECT_STRUCTURE.md) - 完整目录树
- [第三轮整理总结](docs/project-management/第三轮整理总结.md) - 🆕 最新优化成果

### 📖 核心文档
- [API 接口文档](docs/legacy/核心文档/API接口文档.md)
- [快速启动指南](docs/legacy/核心文档/QUICK_START.md)
- [AI 设置指南](docs/legacy/核心文档/AI_SETUP.md)

### ⚙️ 功能说明
- [Redis与Celery说明](docs/legacy/功能说明/REDIS_CELERY说明.md) - 异步任务与缓存架构
- [GPS过滤说明](docs/legacy/功能说明/GPS地理过滤功能.md)

详细结构请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📖 核心文档

| 文档 | 说明 |
|-----|------|
| [API接口文档](docs/legacy/核心文档/API接口文档.md) | 完整的 API 接口规范 |
| [AI_SETUP](docs/legacy/核心文档/AI_SETUP.md) | AI 助手配置指南 |
| [快速启动指南](docs/legacy/核心文档/QUICK_START.md) | 快速上手教程 |

## 🔧 功能特性

### 后端功能
- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 角色权限管理（管理员/巡查员）
- ✅ GPS 地理位置过滤
- ✅ 数据类型标记（真实/测试）
- ✅ Redis 缓存优化
- ✅ Celery 异步任务队列
- ✅ Excel 数据导出
- ✅ AI 智能助手（Ollama集成）
- ✅ Server-Sent Events 实时推送

### 小程序功能
- ✅ 问题上报与拍照
- ✅ GPS 定位
- ✅ 历史记录查询
- ✅ 个人中心
- ✅ 离线数据缓存

### 管理后台
- ✅ 数据概览与统计
- ✅ 世界地图可视化
- ✅ 巡查记录管理
- ✅ 工单流转（待处理→处理中→已完成）
- ✅ 数据筛选与导出
- ✅ 审计日志

## 🧪 测试与工具

```bash
# 运行完整测试
cd tests/legacy/backend-tests
python test_admin_api.py

# 生成测试数据
cd tests/legacy/utilities
python add_hangzhou_data.py

# 重置数据库
python reset_database.py

# 系统诊断
python comprehensive_diagnostic.py
```

## 📊 技术栈

**后端：**
- FastAPI 0.104+
- MySQL 5.7+
- Redis 7.0+
- Celery 5.3+
- Argon2 (密码加密)
- Pillow (图像处理)

**前端：**
- 微信小程序原生框架
- ECharts 5.4+ (数据可视化)
- Leaflet + OpenStreetMap (地图)

**开发工具：**
- Git
- VS Code
- 微信开发者工具
- Postman / Swagger UI

## 📝 开发说明

### 代码规范
- 后端遵循 PEP 8
- 前端遵循微信小程序规范
- 提交信息格式：`<type>: <subject>`
  - `feat`: 新功能
  - `fix`: 修复
  - `docs`: 文档
  - `refactor`: 重构
  - `test`: 测试

### 目录规范
- 新增脚本放入 `tests/legacy/utilities/`
- 新增文档放入 `docs/legacy/` 对应子目录
- 临时文件使用 `_temp/` 或 `_archive/`

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目为课程实践项目，仅供学习交流使用。

## 📞 联系方式

- 项目文档：[docs/legacy/核心文档](docs/legacy/核心文档/)
- 问题反馈：GitHub Issues
- 开发日志：[docs/changelog](docs/changelog/)

---

**最后更新：** 2025-12-30  
**项目状态：** ✅ 生产就绪  
**结构版本：** v2.0.0 (标准化改造)
