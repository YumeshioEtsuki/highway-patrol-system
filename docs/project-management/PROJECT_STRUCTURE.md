# 公路巡查系统 - 项目目录结构

> 最后整理时间：2025-12-26  
> 整理内容：完整的项目目录结构规范化（第二次深度整理）

## 📂 根目录结构

```
highway-patrol-system/
├── README.md                 # 项目主文档（快速开始、特性介绍）
├── PROJECT_STRUCTURE.md      # 本文件（目录结构说明）
│
├── bin/                      # 启动脚本
│   ├── startup.bat          # 系统启动脚本（Windows）
│   └── check_password.py     # 密码检查工具
│
├── 1-后端代码/              # FastAPI 后端应用
│   ├── bin/                  # 启动脚本
│   │   ├── start_server.py   # 启动服务器
│   │   ├── start_celery.ps1  # 启动 Celery
│   │   └── start_redis.ps1   # 启动 Redis
│   │
│   ├── tests/                # 测试脚本
│   │   ├── test_*.py         # 各类测试
│   │   ├── verify_seed.py    # 种子数据验证
│   │   └── update_status.py  # 状态更新工具
│   │
│   ├── docs/                 # 后端文档
│   │   ├── BACKEND_README.md
│   │   ├── IMPORT_FIXES.md
│   │   └── REFACTOR_SUMMARY.md
│   │
│   ├── api/                  # API 路由
│   ├── services/             # 业务逻辑服务
│   ├── models/               # 数据模型
│   ├── schemas/              # 数据验证模型
│   ├── utils/                # 工具函数
│   ├── core/                 # 核心模块
│   ├── templates/            # HTML 模板
│   ├── static/               # 静态文件
│   ├── app.py                # FastAPI 主应用
│   └── settings.py           # 配置文件
│
├── 2-小程序代码/            # 微信小程序前端
│   ├── docs/                 # 小程序文档
│   │   ├── MINIPROGRAM_README.md
│   │   ├── TEST_GUIDE.md         # 测试指南
│   │   ├── TEST_CHECKLIST.md     # 测试清单
│   │   ├── COMPLETION_REPORT.md  # 完成报告
│   │   ├── DELIVERY_DOCUMENT.md  # 交付文档
│   │   └── DEVICE_TEST_GUIDE.md  # 真机测试指南
│   │
│   ├── pages/                # 页面文件
│   ├── images/               # 图片资源
│   ├── utils/                # 工具函数
│   ├── app.js/.json/.wxss    # 小程序配置
│   └── project.config.json   # 项目配置
│
├── 3-数据库/                # 数据库脚本（规范编号）
│   ├── 00_init_schema.sql           # 初始化数据库架构
│   ├── 01_migration_schema.sql      # 数据迁移脚本
│   ├── 02_create_indexes.sql        # 创建索引优化
│   ├── 03_seed_test_data.sql        # 种子测试数据
│   ├── 07_extend_order_role.sql     # 扩展：工单与角色
│   ├── 08_extend_reports.sql        # 扩展：报告功能
│   ├── 09_extend_reports_fixed.sql  # 扩展：报告修复版
│   ├── 10_monitor_schema.sql        # 监控模式架构
│   │
│   └── docs/                 # 数据库文档
│       ├── DATABASE_README.md
│       └── DB_DESIGN.pdf     # 数据库设计文档
│
├── 4-文档/                  # 项目文档（分类整理）
│   ├── 核心文档/            # 核心技术文档（17个文件）
│   │   ├── API接口文档.md
│   │   ├── 项目总结报告-核心要点.md
│   │   ├── AI_SETUP.md
│   │   ├── ER图.jpg
│   │   ├── COURSE_TASK.docx        # 课程任务书
│   │   ├── PROJECT_README.md       # 项目主说明
│   │   ├── QUICK_START.md          # 快速启动
│   │   ├── ONE_CLICK_FIX.md        # 一键修复
│   │   ├── PROJECT_STATUS.md       # 项目状态
│   │   ├── DELIVERY.md             # 交付报告
│   │   ├── PHASE1_STEP1.md
│   │   └── PHASE1_STEP3.md
│   │
│   ├── 功能说明/            # 功能模块说明（8个文件）
│   │   ├── GPS地理过滤功能.md
│   │   ├── 优化原理简明指南.md
│   │   ├── MONITOR_GUIDE.md
│   │   ├── Ollama远程访问配置.md
│   │   ├── HOW_TO_START_CELERY.md
│   │   ├── CELERY_COMPLETION_SUMMARY.md
│   │   ├── CELERY_INDEX.md
│   │   └── CELERY_TEST_RESULTS.md
│   │
│   ├── 开发阶段/            # 阶段性开发文档（15个文件）
│   │   ├── PHASE1_STEP3_*.md
│   │   ├── PHASE2_*.md
│   │   ├── README_PHASE2_STAGE1.md
│   │   ├── START_PHASE1_STEP3.md
│   │   ├── READY_FOR_PHASE1_STEP3.md
│   │   ├── PROJECT_DASHBOARD.md
│   │   └── PROJECT_STATUS_PHASE1_STEP2.md
│   │
│   └── 过时存档/            # 历史文档存档（14个文件）
│       ├── 后端按钮修复/    # 过时修复说明
│       ├── OLD_README.md
│       ├── VERSIONING.md
│       └── doc_content.txt
│
├── 5-演示材料/              # 演示材料（保持原样）
│
├── 6-开发日志/              # 开发日志与报告（规范命名）
│   ├── CHANGELOG.md          # 变更日志
│   ├── FINAL_REPORT.md       # 最终实现报告
│   ├── FIX_SUMMARY.md        # 修复总结
│   ├── DIAGNOSTIC_REPORT.md  # 全面诊断报告
│   ├── DIAGNOSTIC_SUMMARY.md # 诊断执行摘要
│   ├── DIAGNOSTIC_SUMMARY.txt
│   ├── DIAGNOSTIC_REFERENCE.txt
│   ├── HEALTH_CHECK.md       # 项目体检报告
│   ├── VERSION_HISTORY.md    # 版本历史
│   ├── 诊断报告_*.md         # 日期诊断报告
│   ├── backend-logs/         # 后端日志
│   └── reports/              # 报告存档
│
└── 7-测试脚本/              # 测试脚本与工具（分类整理）
    ├── backend-scripts/      # 后端脚本（9个文件）
    ├── backend-tests/        # 后端测试用例（14个文件）
    │   ├── test_*.py
    │   ├── admin_integration_test.py
    │   └── test_login.ps1
    │
    ├── utilities/            # 实用工具脚本（28个文件）
    │   ├── reset_database.py
    │   ├── add_*.py
    │   ├── generate_*.py
    │   ├── diagnostic*.py
    │   ├── comprehensive_*.py
    │   ├── quick_*.py
    │   ├── import_baseline.ps1
    │   └── 等其他工具
    │
    └── docs/                 # 脚本文档（9个文件）
        ├── *.md 文档文件
        ├── test.html
        └── SCRIPTS_README.md
```

## 📋 文件命名规范

### 数据库脚本 (3-数据库/)
- **格式**: `NN_description.sql`
- **编号说明**:
  - `00-03` - 核心架构（初始化、迁移、索引、测试数据）
  - `07-09` - 功能扩展（工单、报告等）
  - `10+` - 监控与其他扩展

**现有脚本清单：**
```
00_init_schema.sql           # 初始化数据库架构
01_migration_schema.sql      # 数据迁移
02_create_indexes.sql        # 创建索引
03_seed_test_data.sql        # 测试数据
07_extend_order_role.sql     # 扩展：工单与角色管理
08_extend_reports.sql        # 扩展：报告功能
09_extend_reports_fixed.sql  # 扩展：报告修复版
10_monitor_schema.sql        # 监控模式
```

### 文档文件 (各目录 docs/)
- **英文大写下划线**: `KEYWORD_DESCRIPTION.md`
- **示例**: `BACKEND_README.md`, `TEST_GUIDE.md`
- **PDF 文档**: `KEYWORD.pdf` 或 `KEYWORD_DESC.pdf`

### 测试脚本 (7-测试脚本/)
- **后端测试**: `backend-tests/` - API、集成测试
- **实用工具**: `utilities/` - 数据生成、诊断、清理
- **脚本文档**: `docs/` - 使用说明、参考卡片

### 启动脚本 (各目录 bin/)
- **格式**: `start_*.py` 或 `startup.*`
- **示例**: `start_server.py`, `startup.bat`

## 🗂️ 目录整理原则

1. **根目录保持简洁** - 只保留必要的配置和启动脚本
2. **分类明确** - 同类文件归入相同目录
3. **层级清晰** - 避免过深的嵌套（最多 3 级）
4. **命名一致** - 同类文件遵循统一的命名规范
5. **易于维护** - 新增文件应按现有规则分类

## 📍 快速导航

| 类型 | 位置 | 说明 |
|-----|------|------|
| 🚀 快速启动 | `bin/startup.bat` | 一键启动系统 |
| 📖 主文档 | `README.md` | 项目概述与快速开始 |
| 🔧 启动服务器 | `1-后端代码/bin/start_server.py` | FastAPI 启动脚本 |
| 🧪 后端测试 | `1-后端代码/tests/` | 单元测试、集成测试 |
| 📊 数据库初始化 | `3-数据库/00_init_schema.sql` | 数据库建表 |
| 📚 API 文档 | `4-文档/核心文档/API接口文档.md` | 接口规范 |
| 🎯 核心文档 | `4-文档/核心文档/` | API、AI配置、总结等 |
| 🔍 功能说明 | `4-文档/功能说明/` | GPS、优化、监控等 |
| 🛠️ 测试工具 | `7-测试脚本/utilities/` | 数据生成、诊断工具 |
| 📝 开发日志 | `6-开发日志/CHANGELOG.md` | 变更记录 |
| 🏥 系统诊断 | `6-开发日志/DIAGNOSTIC_REPORT.md` | 诊断报告 |

## ✅ 整理完成清单

### 第一轮整理（2025-12-26 上午）
- [x] 根目录文件清理（移除所有 .py/.md 散文件）
- [x] 1-后端代码目录整理（bin、tests、docs）
- [x] 2-小程序代码目录整理（docs）
- [x] 3-数据库 SQL 文件初步重命名
- [x] 6-开发日志文档统一命名
- [x] 7-测试脚本分门别类

### 第二轮深度整理（2025-12-26 下午）
- [x] 3-数据库 SQL 完整规范化（00-10编号）
- [x] 3-数据库文档子目录（docs/）
- [x] 删除空的 photos 文件夹
- [x] 整合 scripts 文件夹到 7-测试脚本
- [x] 4-文档深度分类（核心文档、功能说明、开发阶段、过时存档）
- [x] 整合根目录 docs/ 到 4-文档/核心文档/
- [x] 创建主 README.md
- [x] 更新 PROJECT_STRUCTURE.md

## 🎯 整理成果统计

| 指标 | 第一轮 | 第二轮（最终） |
|-----|--------|-------------|
| 根目录文件数 | 15+ → 0 | 0（仅1个README.md） |
| 根目录文件夹数 | 15个 | 12个（精简3个） |
| 数据库脚本规范 | 部分 | 完整（00-10编号） |
| 4-文档分类 | 单层 | 4个子类别 |
| 核心文档数量 | N/A | 17个 |
| 功能说明文档 | N/A | 8个 |
| 测试工具脚本 | 58个 | 58个（优化归类） |

## 📂 4-文档目录详细分类

### 核心文档/ （17个文件）
项目的核心技术文档，包括 API、总结、配置等必读文档。

### 功能说明/ （8个文件）
各功能模块的详细说明，如 GPS过滤、Celery任务、监控等。

### 开发阶段/ （15个文件）
阶段性开发文档，记录各阶段的计划、进度、总结。

### 过时存档/ （14个文件）
历史文档和过时的修复说明，保留备查但不影响主目录。

---

## 🔄 维护建议

### 新增文件规则
- **启动脚本** → `bin/` 或 `1-后端代码/bin/`
- **测试脚本** → `7-测试脚本/utilities/`
- **API测试** → `7-测试脚本/backend-tests/`
- **核心文档** → `4-文档/核心文档/`
- **功能说明** → `4-文档/功能说明/`
- **数据库脚本** → `3-数据库/` (按编号NN_*.sql)
- **临时文件** → 使用 `_temp/` 或 `_archive/` 子目录

### 文档更新路径
根据项目结构变化，以下文件需要同步更新：

1. **启动脚本路径**
   - `bin/startup.bat` - 检查调用路径
   - `1-后端代码/bin/start_server.py` - 检查相对路径

2. **数据库脚本引用**
   - 更新任何硬编码的 SQL 文件路径
   - 检查 `1-后端代码/utils/utils.py` 中的初始化逻辑

3. **文档链接**
   - README.md 中的文档链接
   - 各文档中的相互引用

4. **配置文件**
   - `.env.example` 中的路径说明
   - `settings.py` 中的文件路径配置

### 清理规则
- 超过 3 个月未使用的测试脚本 → `7-测试脚本/utilities/_archive/`
- 过时的阶段文档 → `4-文档/过时存档/`
- 临时日志和输出 → 定期清理或添加到 `.gitignore`

---

**最后更新：** 2025-12-26  
**整理状态：** ✅ 第二轮深度整理完成  
**项目状态：** 🚀 生产就绪

