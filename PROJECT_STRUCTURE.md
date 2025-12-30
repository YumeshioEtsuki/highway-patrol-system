# 项目结构说明

> **标准化改造完成日期**: 2025-12-30

## 📁 目录结构

```
highway-patrol-system/
├── src/                        # 后端源代码（原"1-后端代码"）
│   ├── app.py                  # FastAPI主应用
│   ├── celery_app.py          # Celery异步任务
│   ├── settings.py            # 配置管理
│   ├── routes/                # API路由
│   ├── models/                # 数据模型
│   ├── utils/                 # 工具函数
│   ├── core/                  # 核心功能
│   ├── workers/               # Celery Worker
│   └── .env                   # 后端环境配置
│
├── miniprogram/               # 微信小程序代码（原"2-小程序代码"）
│   ├── pages/
│   ├── components/
│   └── app.json
│
├── database/                  # 数据库文件（原"3-数据库"）
│   ├── 01_create_tables.sql
│   ├── 02_create_indexes.sql
│   └── migrations/
│
├── docs/                      # 文档集中管理
│   ├── legacy/                # 原"4-文档"内容
│   │   ├── 核心文档/
│   │   ├── 功能说明/
│   │   └── 开发阶段/
│   ├── project-management/    # 原"00-项目管理"内容
│   ├── changelog/             # 原"6-开发日志"内容
│   ├── ops/                   # 运维文档
│   ├── diagnostics/           # 诊断文档
│   ├── CHANGELOG.md
│   ├── QUICK_STATUS.md
│   └── ...
│
├── tests/                     # 测试文件集中管理
│   ├── legacy/                # 原"7-测试脚本"内容
│   │   ├── backend-tests/
│   │   ├── diagnostics/
│   │   └── utilities/
│   ├── test_dashboard_reports_integration.py
│   └── verify-dashboard-reports.py
│
├── scripts/                   # 运维和管理脚本
│   ├── admin/                 # 管理员工具
│   │   ├── check_admin_password.py
│   │   └── update_admin_password.py
│   ├── database/              # 数据库相关脚本
│   │   ├── check_db.py
│   │   └── batch_update_skip_db_init.py
│   ├── maintenance/           # 日常维护脚本
│   │   ├── check_env.py
│   │   ├── fix_env_encoding.py
│   │   ├── check_routes.py
│   │   ├── startup_test.py
│   │   └── test_*.py
│   └── start_server.py        # 服务器启动脚本
│
├── assets/                    # 静态资源
│   ├── presentations/         # 原"5-演示材料"内容
│   │   ├── ER图.png
│   │   ├── 项目启动流程图.png
│   │   └── 答辩PPT内容大纲.md
│   └── images/
│
├── bin/                       # 用户入口脚本（保持不变）
│   ├── menu.bat               # 主菜单
│   ├── startup.bat            # 快速启动
│   ├── startup_full.bat       # 完整启动
│   ├── setup_password.bat     # 配置向导
│   ├── env-manager-web.bat    # Web工具
│   ├── docs/                  # 工具文档
│   ├── admin-tools/           # 管理员工具
│   ├── redis-tools/           # Redis工具
│   └── linux-macos/           # 跨平台脚本
│
├── tooling/                   # 开发工具（保持不变）
│   ├── scripts/
│   │   ├── web/               # Web环境变量管理工具
│   │   ├── lib/               # 核心库
│   │   └── cli/
│   └── ops/
│
├── logs/                      # 日志文件集中管理
│   ├── startup.log
│   └── startup_test.log
│
├── photos/                    # 照片存储（保持不变）
├── .github/                   # GitHub配置
├── .venv/                     # Python虚拟环境
├── .vscode/                   # VS Code配置
├── .idea/                     # IntelliJ IDEA配置
│
└── 根目录核心文件（仅保留8个）:
    ├── README.md              # 项目说明
    ├── .env                   # 根目录环境配置
    ├── .env.example           # 配置模板
    ├── .gitignore             # Git忽略规则
    ├── .dockerignore          # Docker忽略规则
    ├── .editorconfig          # 编辑器配置
    ├── Dockerfile             # Docker镜像
    └── VERSION                # 版本号
```

## 🔄 改动对照表

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `1-后端代码/` | `src/` | 符合行业规范（如Django/Spring Boot） |
| `2-小程序代码/` | `miniprogram/` | 更直观的命名 |
| `3-数据库/` | `database/` | 标准化命名 |
| `4-文档/` | `docs/legacy/` | 整合到docs目录 |
| `5-演示材料/` | `assets/presentations/` | 资源统一管理 |
| `6-开发日志/` | `docs/changelog/` | 归档到文档 |
| `7-测试脚本/` | `tests/legacy/` | 整合到tests目录 |
| `00-项目管理/` | `docs/project-management/` | 整合到文档 |
| `根目录*.py` | `scripts/*/` | 按功能分类到子目录 |
| `根目录*.md` | `docs/` | 文档集中管理 |
| `根目录*.log` | `logs/` | 日志隔离 |

## 🎯 设计原则

### 1. **行业标准化**
- 参考 Django、Spring Boot、Node.js 等主流项目结构
- 使用英文目录名，避免数字前缀
- 清晰的功能分层

### 2. **根目录简洁**
- 仅保留 **8个核心配置文件**
- 移除所有脚本和文档
- 提升项目专业度

### 3. **逻辑分组**
- 源代码: `src/`
- 测试代码: `tests/`
- 文档: `docs/`
- 脚本: `scripts/`
- 资源: `assets/`

### 4. **易于维护**
- 相同类型文件集中管理
- 清晰的命名规范
- 完整的文档说明

## 📝 更新内容

### 已更新的文件

1. **启动脚本**
   - `bin/startup.bat` - 更新为 `src/.env`
   - `bin/startup_full.bat` - 更新工作目录为 `src/`
   - `bin/setup_password.bat` - 更新后端目录为 `src`

2. **配置文件**
   - `.gitignore` - 更新所有路径引用
   - `PROJECT_STRUCTURE.md` - 新增此结构说明文档

3. **工具脚本**
   - `tooling/scripts/lib/__init__.py` - 修复 `get_help_text` 导入错误

### 兼容性说明

所有功能保持完全兼容，只是文件位置改变：
- ✅ 后端API正常运行
- ✅ 数据库连接正常
- ✅ 环境变量配置生效
- ✅ Celery任务正常
- ✅ Redis缓存正常
- ✅ bin/工具脚本正常

## 🚀 快速启动

结构调整后，启动方式不变：

```bash
# 快速启动（开发模式）
bin\startup.bat

# 完整启动（Redis + Celery + FastAPI）
bin\startup_full.bat

# 环境变量Web管理工具
bin\env-manager-web.bat
```

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [docs/legacy/核心文档/](docs/legacy/核心文档/) - 核心技术文档
- [docs/ops/STARTUP_GUIDE.md](docs/ops/STARTUP_GUIDE.md) - 启动指南
- [bin/docs/TOOLS_GUIDE.md](bin/docs/TOOLS_GUIDE.md) - 工具使用指南

---

**最后更新**: 2025-12-30  
**改造版本**: v2.0.0  
**改造类型**: 目录结构标准化
