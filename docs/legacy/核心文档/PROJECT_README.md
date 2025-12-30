# 公路巡查系统 (Highway Patrol System)

**完整的公路巡查数据采集系统** — 后端 API + 微信小程序 + MySQL 数据库

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-blue.svg)](https://fastapi.tiangolo.com/)  
[![MySQL](https://img.shields.io/badge/mysql-8.0+-blue.svg)](https://www.mysql.com/)

---

## 🎯 项目概览

| 组件 | 技术栈 | 说明 |
|------|--------|------|
| **后端** | FastAPI + Python 3.12 | RESTful API、实时推送、数据管理 |
| **前端** | 微信小程序 (TypeScript) | 巡查工作台、地图分析、实时通知 |
| **数据库** | MySQL 8.0 | 数据存储、自动初始化、性能优化 |

---

## 🚀 快速开始

### 前置要求
- Python 3.12+
- MySQL 8.0+
- 虚拟环境（推荐 `.venv`）

### 环境配置与启动

完整的新手指南请查阅 **[环境配置与启动指南](./docs/SETUP.md)**

快速启动（假设环境已配置）：

```bash
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate   # macOS/Linux

# 2. 进入后端目录
cd 1-后端代码

# 3. 启动开发服务器
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# 4. 访问
# 前端: http://localhost:5000
# API 文档: http://localhost:5000/docs
```

---

## 📁 项目结构

```
highway-patrol-system/
├── docs/                     📚 项目文档中心（重要！新手必读）
│   ├── README.md            文档导航
│   ├── SETUP.md             环境配置指南
│   └── DEVELOPMENT.md       本地开发规范
│
├── scripts/                  🛠️  实用脚本与工具
│   └── README.md            脚本使用指南
│
├── 1-后端代码/              🔧 FastAPI 后端应用
│   ├── app.py              主应用
│   ├── .env                开发配置（本地，不提交）
│   ├── .env.example        配置模板
│   ├── requirements.txt    Python 依赖
│   ├── routes/             API 路由
│   ├── models/             数据模型
│   ├── utils/              工具函数
│   ├── templates/          前端页面
│   └── photos/             上传照片（自动生成）
│
├── 2-小程序代码/            📱 微信小程序前端
│   ├── app.js              小程序逻辑
│   ├── pages/              页面组件
│   └── README.md           小程序文档
│
├── 3-数据库/                💾 数据库脚本
│   ├── create_database.sql 建表脚本
│   ├── test_data.sql       测试数据
│   └── README.md           数据库文档
│
├── 4-文档/                  📖 详细功能文档
│   ├── API接口文档.md       API 规范
│   ├── GPS地理过滤功能.md   地理定位功能
│   └── 项目总结报告-核心要点.md 核心说明
│
├── 5-演示材料/              🎬 答辩与演示
│   └── 答辩PPT内容大纲.md
│
├── 6-开发日志/              📝 开发过程记录
│   └── (各类诊断报告与变更日志)
│
├── 7-测试脚本/              ✅ 测试与诊断脚本
│   ├── diagnose_data.py    数据库诊断
│   ├── test_admin_api.py   API 测试
│   └── (更多测试脚本)
│
├── .env                     环境配置（根目录，仅用于兼容，见 1-后端代码/.env）
├── .env.example             配置模板示例
├── .gitignore              Git 忽略规则
├── .editorconfig           编码规范（支持多个 IDE）
├── .vscode/                VS Code 配置
└── README.md               此文件
```

---

## 📚 重要文档

**新成员必读：**
1. **[docs/README.md](./docs/README.md)** — 文档导航与核心概念
2. **[docs/SETUP.md](./docs/SETUP.md)** — 环境配置与启动（详细步骤）
3. **[docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)** — 本地开发规范

**其他文档：**
- [API 接口文档](./4-文档/API接口文档.md) — RESTful API 规范
- [GPS 功能说明](./4-文档/GPS地理过滤功能.md) — 地理定位实现
- [项目架构](./4-文档/项目总结报告-核心要点.md) — 系统设计
- [脚本使用指南](./scripts/README.md) — 开发脚本使用

---

## 🔑 核心功能

### 后端 API
- ✅ **巡查记录管理** — 增删查改、照片上传、GPS 定位
- ✅ **实时推送** — SSE 实时通知、新照片提醒
- ✅ **用户认证** — JWT Token、角色控制（巡查员/管理员）
- ✅ **统计分析** — 多维度报表、数据导出
- ✅ **运维后台** — 数据库管理、审计日志、限流控制
- ✅ **安全加固** — 速率限制、敏感数据加密、操作审计

### 前端小程序
- 📍 **工作台** — 上报问题、选择类型、上传照片
- 🗺️ **地图分析** — 热力分布、按省市过滤、问题统计
- 🔔 **实时推送** — 新照片通知、记录更新提醒
- 📊 **统计看板** — 数据概览、趋势分析

---

## 🛠️ 常用命令

```bash
# 环境激活
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r 1-后端代码/requirements.txt

# 启动后端
cd 1-后端代码 && uvicorn app:app --reload

# 生成测试数据（1000 条）
python 7-测试脚本/add_hangzhou_data.py

# 数据库诊断
python 7-测试脚本/diagnose_data.py

# 清理测试数据
python 7-测试脚本/cleanup.py

# 重置数据库
python 1-后端代码/reset_db.py

# 运行管理后台（进入后端，访问 /admin）
# http://localhost:5000/admin
```

---

## 📊 配置速查

### 数据库连接 (1-后端代码/.env)
```dotenv
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=REDACTED
DATABASE_NAME=road_patrol_db
```

### JWT & 应用
```dotenv
SECRET_KEY=road_patrol_dev_secret_2025_do_not_use_in_production
JWT_EXPIRE_HOURS=24
DEBUG=True
```

### 文件上传
```dotenv
UPLOAD_FOLDER=photos
MAX_UPLOAD_SIZE=10485760  # 10MB
```

详见 [1-后端代码/.env.example](./1-后端代码/.env.example)

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|--------|
| 无法解析导入 `utils.*` | 确保从 `1-后端代码` 目录启动或运行脚本 |
| 数据库连接失败 | 检查 MySQL 运行，确认 `.env` 中的主机/用户/密码正确 |
| 端口 5000 被占用 | 运行 `python 1-后端代码/start_server.py` 或指定其他端口 |
| 导入解析提示 | 检查 `.vscode/settings.json` 中 `python.analysis.extraPaths` 配置 |

更多问题见 [故障排查](./docs/TROUBLESHOOTING.md)

---

## 🤝 贡献指南

1. 新文档或更新放在 `docs/` 目录
2. 脚本放在 `7-测试脚本/` 或 `scripts/`
3. 编码遵循 `.editorconfig` 规范
4. 提交前确认 `.env` 和 `.venv` 未被提交（`.gitignore` 已覆盖）

---

## 📞 获取帮助

- **API 文档**: http://localhost:5000/docs (启动后)
- **项目文档**: 见 `docs/` 目录
- **开发日志**: `6-开发日志/`
- **诊断脚本**: `python 7-测试脚本/diagnose_data.py`

---

## 📋 版本与更新

**当前版本**: v1.0 (2025-12-23)

**最近更新**:
- ✅ 环境配置体系优化（.env/.gitignore/.editorconfig）
- ✅ 项目结构规范化（docs/, scripts/ 文件夹）
- ✅ 文档中心建立（README.md、SETUP.md）
- ✅ 数据生成与刷新问题修复
- ✅ Pylance 导入解析优化

详见 [开发日志](./6-开发日志/README.md)

---

## 📄 许可证

MIT License — 见 [LICENSE](./LICENSE) 文件

---

**维护者**: 开发团队  
**最后更新**: 2025-12-23  
**文档版本**: v1.0
│   ├── photos/             # 照片存储
│   └── logs/               # 日志文件
│
├── 2-小程序代码/
│   ├── app.json            # 小程序配置
│   ├── pages/              # 页面（首页、巡查、地图等）
│   ├── utils/              # 工具函数
│   └── images/             # 资源图片
│
├── 3-数据库/
│   ├── create_database.sql # 建表脚本
│   ├── test_data.sql       # 测试数据
│   ├── add_indexes.sql     # 性能优化索引
│   └── add_*.sql           # 字段/功能扩展
│
├── 4-文档/
│   ├── 项目总结报告-核心要点.md
│   ├── API接口文档.md
│   ├── AI_SETUP.md
│   └── 后端按钮修复/       # 修复文档存档
│
├── 5-演示材料/            # 演示、部署资源
├── 6-开发日志/            # 变更记录
└── README.md              # 本文件
```

---

## 🚀 快速开始

### 启动后端

```bash
cd 1-后端代码

# 配置环境变量（第一次）
copy .env.example .env
# 编辑 .env，设置数据库连接信息

# 安装依赖
pip install -r requirements.txt

# 启动服务（自动处理端口冲突）
python start_server.py

# 或手动启动
set SKIP_DB_INIT=1
uvicorn app:app --host 0.0.0.0 --port 5000
```

### 验证运行

- 前端页面：http://127.0.0.1:5000
- Swagger 文档：http://127.0.0.1:5000/docs
- ReDoc 文档：http://127.0.0.1:5000/redoc

### 小程序开发

```bash
cd 2-小程序代码

# 使用微信开发者工具打开此目录
# 编辑 project.config.json 配置 AppID 与项目名

# 开发：使用热重载
# 构建：打包上传至微信审核
```

---

## ✨ 最新优化亮点（v1.2.0）

### 🎨 用户体验
- **骨架屏加载**：统计卡片、图表、表格在加载时显示流畅的占位动画
- **实时推送**：SSE 照片流自动断线重连，零感知体验
- **导出功能**：审计日志与巡查记录支持导出为 CSV/Excel

### ⚡ 性能优化
- **数据库连接池**：复用连接，减少握手延迟（可选 MySQLConnectionPool）
- **关键字段索引**：自动创建或手动应用 `add_indexes.sql`（用户ID、状态+时间、上传时间等）
- **统计数据缓存**：支持 Redis 或内存缓存，TTL 可配置（默认 600s）
- **请求耗时日志**：自动记录所有 HTTP 的响应时间，便于性能分析

### 🔐 安全加固
- **速率限制**：
  - 登录：5 次/分钟
  - 数据库操作：1-3 次/分钟
- **审计日志**：所有管理员敏感操作被记录，支持按操作、用户、时间、关键词筛选
- **环境变量规范**：`.env.example` 详尽注释，生产环境配置清晰

### 🛠️ 开发友好
- **启动脚本增强**：`start_server.py` 可选应用数据库脚本、清理占用端口
- **常数集中管理**：`constants.py` 集中配置数据类型、状态值等
- **模块化架构**：路由、模型、工具分层清晰，便于扩展

---

## 📖 文档导航

| 文档 | 用途 |
|------|------|
| `1-后端代码/README.md` | 后端应用详细说明、API 文档、部署指南 |
| `4-文档/项目总结报告-核心要点.md` | 项目架构概览、核心模块说明 |
| `4-文档/API接口文档.md` | API 端点详细说明 |
| `2-小程序代码/README.md` | 小程序开发与测试指南 |
| `2-小程序代码/开发完成报告.md` | 小程序功能完成度与测试结果 |

---

## 🔗 照片存储与访问

- **存储位置**：`1-后端代码/photos/`
- **访问方式**：`http://<IP>:5000/photos/<filename>`
- **生成方式**：
  - 巡查员通过小程序上传
  - 管理员生成虚拟数据时自动创建
- **配置**：`utils/config.py` 中的 `settings.UPLOAD_FOLDER`

---

## 🛠️ 环境变量示例

```bash
# 数据库连接
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=road_patrol_db

# 认证
SECRET_KEY=your-secret-key-here
JWT_EXPIRE_HOURS=24

# 性能优化
DB_POOL_SIZE=10
MAX_PAGE_SIZE=200
REDIS_URL=redis://localhost:6379
STATS_CACHE_TTL=600

# 启动选项
SKIP_DB_INIT=1  # 日常开发跳过数据库初始化
APPLY_INDEXES_ON_START=1  # 启动时应用数据库索引

# 调试
DEBUG=False
ALLOW_ORIGINS=["https://yourdomain.com"]
```

详见 `1-后端代码/.env.example`

---

## 📞 常见问题

**Q: 数据库连接失败？**
- 检查 MySQL 是否运行
- 验证 `.env` 中的连接信息
- 查看 `logs/app_YYYY-MM-DD.log` 获取具体错误

**Q: 端口 5000 被占用？**
- 使用 `start_server.py` 会自动清理
- 或手动指定其他端口：`uvicorn app:app --port 8000`

**Q: 小程序无法连接后端？**
- 确保后端已启动（`http://<IP>:5000/docs` 可访问）
- 检查防火墙是否放行 5000 端口
- 在小程序中设置正确的 API 基础 URL

**Q: 如何导出数据？**
- 巡查记录：点击后台"📤 导出Excel"
- 审计日志：点击"📥 导出CSV"

---

## 🎯 后续规划

- [ ] 单元测试与集成测试（pytest）
- [ ] 前端单页应用改进（分离前端工程）
- [ ] 多语言支持（i18n）
- [ ] 移动端优化
- [ ] 云部署方案（Docker、K8s）

---

## 📄 许可证

Internal Project - All Rights Reserved

---

**项目维护**：公路巡查系统开发团队  
**最后更新**：2025-12-23  
**版本**：v1.2.0
