## 🎯 开发工具和启动方式总览

### 📊 工具对比表

| 工具 | 适用场景 | 易用度 | 功能完整度 | 启动方式 |
|------|---------|--------|-----------|---------|
| **🌐 Web 工具** | 配置修改（推荐）| ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | `env-manager-web.bat` |
| **📟 CLI 工具** | 命令行爱好者 | ⭐⭐⭐ | ⭐⭐⭐⭐ | `python manage_env.py` |
| **🎯 菜单系统** | 新手友好 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | `menu.bat` |
| **🚀 快速启动** | 快速开发 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | `startup.bat` |
| **🚀 完整启动** | 完整开发环境 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | `startup_full.bat` |

---

## 🚀 启动方式详解

### 1️⃣ Web 环境变量管理工具（最推荐）

**目的**：可视化修改环境变量配置

**启动**：
```bash
# Windows
.\bin\env-manager-web.bat

# Linux/macOS
bash bin/env-manager-web.sh

# PowerShell
.\bin\env-manager-web.ps1
```

**访问**：http://127.0.0.1:5051

**功能**：
- 📝 输入键名查看当前值
- 🔍 查看推荐值
- ✅ 一键应用推荐值到选定环境
- 🎯 输入自定义值应用
- 📋 查看所有环境的完整配置

**适用人群**：
- ✅ 新手（界面友好）
- ✅ 团队成员（无需命令行知识）
- ✅ 运维人员（可视化操作）

---

### 2️⃣ 菜单工具（快速选择）

**目的**：一个入口，快速访问所有开发工具

**启动**：
```bash
# Windows
.\bin\menu.bat

# Linux/macOS
bash bin/menu.sh
```

**菜单选项**：
```
1. 🌐 Web 环境变量管理工具    (推荐)
2. 📟 CLI 环境变量管理工具
3. 🚀 项目启动（快速开发）
4. 🚀 项目启动（完整）
5. 📊 数据库检查
0. 退出
```

**适用人群**：
- ✅ 新手
- ✅ 快速工作流
- ✅ 不想记命令

---

### 3️⃣ CLI 环境变量管理工具

**目的**：命令行方式修改配置（脚本集成友好）

**启动**：
```bash
cd tooling/scripts
python manage_env.py
```

**功能菜单**：
1. 查看配置文件
2. 添加新配置
3. 编辑环境变量
4. 编辑单个文件
5. 分组建议与批量应用

**适用人群**：
- ✅ 命令行爱好者
- ✅ 脚本集成（CI/CD）
- ✅ 高级用户

---

### 4️⃣ 快速启动（快速开发）

**目的**：快速启动 FastAPI 后端（dev 环境）

**启动**：
```bash
.\bin\startup.bat
```

**做什么**：
- ✅ 加载 `.env` 配置（dev 环境）
- ✅ 检查数据库
- ✅ 启动 FastAPI 服务器 (http://127.0.0.1:5000)
- ✅ 跳过 Redis 和 Celery（可选）

**特点**：
- 快速（仅启动后端）
- 轻量（不需要 Redis/Celery）
- 开发友好（支持自动重载）

---

### 5️⃣ 完整启动（完整开发环境）

**目的**：启动完整的开发环境（Redis + Celery + FastAPI）

**启动**：
```bash
.\bin\startup_full.bat
```

**启动顺序**：
1. 🔍 检查环境配置
2. 🚀 启动 Redis Server (port 6379)
3. 👷 启动 Celery Worker
4. 🌐 启动 FastAPI 后端 (port 5000)

**特点**：
- 完整的生产级环境
- 支持异步任务（Celery）
- 支持缓存和 SSE

**适用场景**：
- ✅ 功能测试
- ✅ 异步任务开发
- ✅ 生产环境验证

---

## 💡 工作流示例

### 场景 A：快速修改配置后启动

```bash
# 1. 打开 Web 工具
.\bin\env-manager-web.bat
# → 在浏览器中修改配置
# → http://127.0.0.1:5051

# 2. 快速启动后端
.\bin\startup.bat
# → FastAPI 启动，自动加载修改后的 .env
```

### 场景 B：完整开发流程

```bash
# 1. 打开菜单
.\bin\menu.bat

# 选择选项 4：启动完整环境
# → Redis + Celery + FastAPI 全启动

# 2. 在另一个终端修改配置
.\bin\menu.bat
# 选择选项 1：Web 工具修改

# 3. 重启后端加载新配置
# 按 Ctrl+C 停止，再次运行 startup_full.bat
```

### 场景 C：数据库问题排查

```bash
.\bin\menu.bat
选择选项 5：数据库检查
→ 显示当前数据库状态、表结构、索引等
```

---

## 🎯 选择建议

### 我想快速修改配置？
→ **使用 Web 工具** (`env-manager-web.bat`)
- 最直观
- 推荐值建议
- 多环境同步

### 我是新手，什么都不确定？
→ **使用菜单系统** (`menu.bat`)
- 一个入口
- 清晰的选项
- 减少记忆负担

### 我想快速启动项目开发？
→ **使用快速启动** (`startup.bat`)
- 15秒内启动
- 仅启动必要服务
- 自动配置加载

### 我需要完整的开发环境？
→ **使用完整启动** (`startup_full.bat`)
- Redis 缓存
- Celery 异步任务
- 生产级配置

### 我是高级用户，想脚本集成？
→ **使用 CLI 工具** + **lib 库**
```python
from tooling.scripts.lib import EnvManager

manager = EnvManager(Path.cwd())
manager.set_values_batch("LOG_LEVEL", ["prod"], "WARNING")
```

---

## 📂 文件结构说明

```
bin/                             # 用户交互入口
├── env-manager-web.bat         # 一键启动 Web 工具 ✨ 推荐
├── env-manager-web.sh          # Linux/macOS 版本
├── env-manager-web.ps1         # PowerShell 版本
├── menu.bat                    # 工具菜单 ✨ 新手友好
├── menu.sh                     # Linux/macOS 菜单
├── startup.bat                 # 快速启动
├── startup_full.bat            # 完整启动
└── ...其他脚本

tooling/scripts/                 # 核心工具
├── lib/                         # 可复用的业务逻辑库
│   ├── env_manager.py          # Model 层
│   ├── validators.py           # 验证和推荐规则
│   └── __init__.py
├── cli/                         # CLI 界面（使用 lib）
│   ├── manage_env.py           # 交互式 CLI
│   └── ...
├── web/                         # Web 界面（使用 lib）
│   ├── app.py                  # FastAPI + 路由
│   ├── templates/              # HTML 模板
│   └── static/                 # CSS/JS 资源
└── README.md                   # 详细文档 ⭐ 必读
```

---

## 🔧 技术架构

所有工具都基于同一套核心库（`lib/`）：

```
           ┌─────────────────────┐
           │   lib/ (核心库)      │
           │ ┌─────────────────┐  │
           │ │ env_manager.py  │  │ 数据读写
           │ │ validators.py   │  │ 验证/推荐
           │ └─────────────────┘  │
           └──────────┬────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌──────────┐ ┌──────────┐ ┌─────────┐
    │  Web UI  │ │ CLI UI   │ │ REST API│
    │(FastAPI)│ │(Click)   │ │(未来)   │
    └──────────┘ └──────────┘ └─────────┘
```

**优势**：
- ✅ 一处修改，处处生效
- ✅ 易于测试
- ✅ 易于扩展

---

## 📚 更多信息

详细的架构说明、最佳实践、扩展指南，请参考：

👉 **[tooling/scripts/README.md](../tooling/scripts/README.md)**

---

## 🎓 总结

| 需求 | 推荐工具 | 启动命令 |
|------|---------|---------|
| 修改配置 | Web 工具 | `.\bin\env-manager-web.bat` |
| 快速开发 | 快速启动 | `.\bin\startup.bat` |
| 完整环境 | 完整启动 | `.\bin\startup_full.bat` |
| 新手入门 | 菜单系统 | `.\bin\menu.bat` |
| 高级集成 | CLI + lib | `python tooling/scripts/cli/manage_env.py` |

🌟 **最佳实践**：
1. 第一次使用？→ `menu.bat`
2. 日常开发？→ `startup.bat` + `env-manager-web.bat`
3. 完整测试？→ `startup_full.bat`
4. 脚本集成？→ 使用 `lib/env_manager.py`

