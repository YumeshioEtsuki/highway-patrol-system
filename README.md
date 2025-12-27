# 公路巡查数据采集系统

> **Highway Patrol Data Collection System**  
> 基于 FastAPI + 微信小程序 + MySQL 的完整解决方案

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Node.js (微信开发者工具)
- Redis 5.0+ (推荐，用于缓存和异步任务)
  - **推荐使用 Docker**：`.\bin\start_redis.bat`
  - 或下载 Windows 版本

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
cd 1-后端代码
python bin\start_server.py
```

**停止所有服务**
```bash
bin\stop_all.bat
```

### 📖 详细说明

- [完整启动指南](bin/STARTUP_GUIDE.md) - Redis安装、手动启动、监控
- [Redis与Celery说明](4-文档/功能说明/REDIS_CELERY说明.md) - 异步架构详解

### 🔗 访问地址

服务器启动后访问：
- 管理后台：http://localhost:5000
- API 文档：http://localhost:5000/docs
- ReDoc：http://localhost:5000/redoc
- Celery监控：http://localhost:5555 (需先安装 `pip install flower` 并启动)

### 数据库初始化

```bash
cd 3-数据库
# 按顺序执行SQL文件
mysql -u root -p < 00_init_schema.sql
mysql -u root -p < 01_migration_schema.sql
mysql -u root -p < 02_create_indexes.sql
mysql -u root -p < 03_seed_test_data.sql
```

## 📂 项目结构

```
highway-patrol-system/
├── 00-项目管理/           # 项目结构与更新日志
├── bin/                   # 启动脚本
├── 1-后端代码/           # FastAPI 后端
├── 2-小程序代码/         # 微信小程序
├── 3-数据库/             # SQL 脚本
├── 4-文档/               # 项目文档
│   ├── 核心文档/        # API、AI配置、总结等
│   ├── 功能说明/        # 各功能模块说明
│   ├── 开发阶段/        # 阶段性文档
│   └── 过时存档/        # 历史存档
├── 5-演示材料/           # 演示资料
├── 6-开发日志/           # 开发记录（4类）
└── 7-测试脚本/           # 测试工具
```

**详细结构：** 查看 [PROJECT_STRUCTURE.md](00-项目管理/PROJECT_STRUCTURE.md)

## 📚 文档导航

### 🔧 项目管理
- [项目结构说明](00-项目管理/PROJECT_STRUCTURE.md) - 完整目录树
- [第二轮更新日志](00-项目管理/PROJECT_UPDATE_LOG.md) - 第二轮整理记录
- [第三轮整理总结](00-项目管理/第三轮整理总结.md) - 🆕 最新优化成果

### 📖 核心文档
- [API 接口文档](4-文档/核心文档/API接口文档.md)
- [项目交付文档](4-文档/核心文档/项目交付文档.md)
- [快速启动指南](4-文档/核心文档/QUICK_START.md)

### ⚙️ 功能说明
- [Redis与Celery说明](4-文档/功能说明/REDIS_CELERY说明.md) - 异步任务与缓存架构
- [GPS过滤说明](4-文档/功能说明/GPS_FILTERING_README.md)
- [Celery任务队列](4-文档/功能说明/CELERY_README.md)

详细结构请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📖 核心文档

| 文档 | 说明 |
|-----|------|
| [API接口文档](4-文档/核心文档/API接口文档.md) | 完整的 API 接口规范 |
| [项目总结报告](4-文档/核心文档/项目总结报告-核心要点.md) | 核心技术要点总结 |
| [AI_SETUP](4-文档/核心文档/AI_SETUP.md) | AI 助手配置指南 |
| [快速启动指南](4-文档/核心文档/QUICK_START.md) | 快速上手教程 |
| [一键修复指南](4-文档/核心文档/ONE_CLICK_FIX.md) | 常见问题修复 |

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
cd 7-测试脚本/backend-tests
python test_admin_api.py

# 生成测试数据
cd 7-测试脚本/utilities
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
- 新增脚本放入 `7-测试脚本/utilities/`
- 新增文档放入 `4-文档/` 对应子目录
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

- 项目文档：[4-文档/核心文档](4-文档/核心文档/)
- 问题反馈：GitHub Issues
- 开发日志：[6-开发日志](6-开发日志/)

---

**最后更新：** 2025-12-26  
**项目状态：** ✅ 生产就绪
