# Changelog

所有项目重要更改都将记录在此文件中。

本文件格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.0.0] - 2025-12-28

### 🎉 重大升级

这是一个全面重构的版本，完成了从原型系统到生产就绪系统的转变。

### ✨ 新增功能 (Added)

#### 后端架构
- **模块化路由系统**: 将单文件路由拆分为 `routes/{admin,auth,chat,patrol,photos,tasks}` 子模块
- **服务层抽象**: 新增 `services/` 目录，实现业务逻辑与路由解耦
- **核心工具模块**: 新增 `core/` 目录（database, dependencies, security）
- **工作队列模块**: 新增 `workers/` 目录，支持异步任务处理
- **配置管理**: 统一配置文件 `settings.py`（替代分散的环境变量）

#### 数据库功能
- **审计日志系统**: 新增 `AuditLog` 表，记录所有管理员敏感操作
- **数据类型标记**: InspectionRecord 新增 `data_type` 字段（real/test），支持测试数据筛选
- **索引优化方案**: 新增 `02_create_indexes.sql`，提升查询性能
- **增量迁移支持**: 新增 `07-10` 系列扩展脚本（订单/报告/监控）

#### 管理功能
- **实时进度显示**: 生成数据任务支持 SSE 流式传输进度（0%-100%）
- **数据生成优化**: 支持批量生成测试数据（含照片），带防抖机制
- **数据类型筛选**: 支持按真实/测试数据分类查看
- **数据清理功能**: 一键清理测试数据（保留真实数据）
- **审计日志查询**: 支持按操作类型/用户/时间范围筛选

#### 前端优化
- **实时照片流**: 懒加载展示，支持点击展开/折叠，单击放大
- **防抖优化**: loadStats/loadRecords 防抖（间隔1-2秒），降低 F12 控制台轮询频率
- **进度条展示**: 任务执行时在审计面板上方显示实时进度条
- **Dashboard 面板**: 新增统计报表和任务管理界面
- **Reports 面板**: 新增报告生成和导出功能

#### 启动脚本
- **完整启动方案**: `bin/startup_full.bat` 集成 Redis + Celery + FastAPI
- **快速启动**: `bin/startup.bat` 仅启动 FastAPI
- **优雅停止**: `bin/stop_all.bat` 停止所有服务
- **Redis 管理**: `bin/start_redis.bat` 和 `bin/start_redis.ps1`

#### 文档系统
- **项目管理**: 新增 `00-项目管理/` 目录（结构文档、更新日志）
- **核心文档**: 新增 `4-文档/核心文档/` 目录（API、部署指南）
- **功能说明**: 新增 `4-文档/功能说明/` 目录（各模块使用说明）
- **启动指南**: `bin/STARTUP_GUIDE.md` 详细启动步骤
- **快速参考**: `docs/QUICK_REFERENCE.md` 常用操作速查

#### 测试工具
- **后端测试**: `7-测试脚本/backend-tests/` 集成测试套件
- **诊断工具**: `7-测试脚本/diagnostics/` 系统健康检查
- **实用工具**: `7-测试脚本/utilities/` 辅助脚本（数据重置、索引应用）

### 🔄 变更功能 (Changed)

#### 后端重构
- **JWT 认证增强**: 支持 Header 和 Query 双重认证方式（兼容 SSE）
- **错误处理统一**: 所有异常返回统一格式，包含详细错误信息
- **日志系统优化**: 结构化日志，支持按模块级别过滤
- **数据库连接池**: 优化连接管理，防止连接泄漏

#### 前端优化
- **表格分页优化**: 支持自定义每页条数（20/50/100/200）
- **筛选条件增强**: 所有列表页支持多维度筛选
- **实时数据刷新**: SSE 推送 + 防抖轮询混合策略
- **响应式设计**: 优化移动端显示效果

#### 配置管理
- **环境变量规范**: 统一使用 `settings.py` 管理配置
- **密码策略**: 从源码移除硬编码密码（改用配置文件）
- **数据库初始化**: 支持 `SKIP_DB_INIT` 环境变量跳过重复建库

### 🗑️ 移除功能 (Removed)

#### 废弃文件清理（100+ 个文件）
- **旧文档清理**: 删除 Phase 1/2 开发阶段文档（已归档）
- **测试脚本整理**: 删除临时测试脚本（保留核心测试套件）
- **模型文件简化**: 删除 `order_schemas.py`, `order_tasks.py`, `performance_metrics.py` 等未使用模型
- **路由文件整合**: 删除 `admin_old.py`, `patrol_sse.py` 等旧版路由
- **工具类精简**: 删除 `auth.py`, `exceptions.py`, `logger.py`, `rate_limit.py` 等未使用工具

#### 具体删除清单
**后端代码** (1-后端代码/):
- 文档: CELERY_*.md, REDIS_*.md, COMPLETION_SUMMARY.md 等 9 个文件
- 模型: order_schemas.py, order_tasks.py, performance_metrics.py, slow_query.py 等
- 路由: admin_old.py, chat.py, monitor.py, orders.py, photo.py, user.py 等
- 任务: tasks/ 目录下所有文件（ai_tasks, maintenance_tasks, photo_tasks, report_tasks）
- 工具: auth.py, deps.py, exceptions.py, logger.py, permissions.py, rate_limit.py, sse.py, test_data.py
- 脚本: start_celery.ps1, start_redis.ps1, start_server.py, test_*.py, verify_*.py

**小程序代码** (2-小程序代码/):
- 功能测试清单.md, 开发完成报告.md, 测试指南.md, 真机测试指南.md, 项目交付文档.md

**数据库** (3-数据库/):
- 00_init.sql, 01_migration.sql, 02_indexes.sql, 03_test_data.sql
- monitor_schema.sql, phase2_stage1_order_and_role.sql
- README.md, 数据库设计文档.pdf

**文档** (4-文档/):
- 阶段性开发文档: PHASE*.md, READY_FOR_*.md, START_*.md（约 20 个）
- API 和设置文档: AI_SETUP.md, CELERY_INDEX.md, HOW_TO_START_CELERY.md 等
- 后端按钮修复专题文档（8 个文件）
- 课程实践任务书、项目总结报告等

**开发日志** (6-开发日志/):
- 根目录的开发日志.md, 整理*.md, 修复报告*.md 等（约 20 个）
- reports/ 目录的临时报告

**测试脚本** (7-测试脚本/):
- 根目录所有测试脚本（约 30 个 .py 文件）
- _deprecated/ 目录
- 临时文档: 变更清单.md, 功能完成总结.md, 快速*.md 等

**项目根目录**:
- DELIVERY_REPORT.md, PHASE_1_STEP_1_REPORT.md, PROJECT_STATUS.md
- README_PHASE1_STEP3.md
- docs/README.md, docs/DEVELOPMENT.md, docs/MOBILE_TESTING.md 等
- quick_start.py, scripts/

### 🐛 修复问题 (Fixed)

#### 关键 Bug 修复
- **审计日志空白**: 创建缺失的 AuditLog 表，修复审计功能
- **数据类型筛选失效**: 修复"全部数据"不包含测试数据的问题
- **F12 控制台轮询卡顿**: 添加防抖机制，降低请求频率
- **照片展开后自动收拢**: 修复事件冒泡问题，改为单击放大
- **SSE 进度条显示错误**: 改为在审计面板上方独立显示，不污染审计日志
- **Token 认证失效**: 修复 JWT 异常捕获不完整导致的 500 错误

#### 稳定性提升
- **数据库连接泄漏**: 修复未关闭游标导致的连接耗尽
- **SSE 连接断开**: 添加自动重连机制（2-3秒间隔）
- **任务阻塞**: 添加 isOperating 状态锁，防止并发任务
- **图片加载性能**: 实现懒加载，默认只显示 ID

### 🔒 安全改进 (Security)

- **密码管理**: 从源码移除硬编码数据库密码
- **JWT 增强**: 修复异常处理漏洞，防止 token 绕过
- **输入验证**: 所有用户输入进行 XSS 过滤（safeText）
- **文件上传**: 限制上传文件类型和大小（10MB）

### 📚 文档完善 (Documentation)

- **启动指南**: 详细的 Windows 环境启动步骤
- **API 文档**: FastAPI 自动生成交互式文档（/docs）
- **快速参考**: 常用操作和故障排查
- **架构说明**: 项目结构和模块职责说明

### 🚀 性能优化 (Performance)

- **数据库索引**: 为高频查询字段添加索引
- **分页查询**: 限制单页最大 200 条，防止 OOM
- **缓存机制**: 统计数据缓存（10 分钟 TTL）
- **图片压缩**: 测试数据照片压缩至 70% 质量

### 🛠️ 开发体验 (Developer Experience)

- **一键启动**: startup_full.bat 自动检测并启动所有服务
- **环境检测**: 自动检查 Docker/WSL/Python 环境
- **错误提示**: 详细的错误信息和解决建议
- **代码结构**: 清晰的目录划分和命名规范

### 📦 依赖更新

详见 `1-后端代码/requirements.txt`

---

## [1.0.0] - 2025-12-21

### 初始版本

- 基础的巡查记录管理功能
- 管理员认证系统
- 小程序端数据采集
- 地图可视化展示

---

[2.0.0]: https://github.com/yourname/highway-patrol-system/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourname/highway-patrol-system/releases/tag/v1.0.0
