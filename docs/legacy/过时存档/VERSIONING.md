# 版本控制与发布策略（highway-patrol-system）

本项目采用 Git + 语义化版本（SemVer）管理版本与分支，结合标签发布稳定版本。适用于单体仓库包含后端、数据库脚本与小程序代码的场景。

## 版本命名（SemVer）
- 格式：`MAJOR.MINOR.PATCH`
  - MAJOR：不兼容的重大变更（例如：权限体系、数据结构大改）
  - MINOR：向后兼容的新功能（例如：新增报表、通知通道）
  - PATCH：向后兼容的修复（例如：修复 NPE、SQL 优化）
- 建议示例：
  - `v1.0.0`：Phase 1 之前的“初版”（如有历史快照）
  - `v1.5.0`：Phase 1 全部完成后的稳定版
  - `v2.0.0`：Phase 2 Stage 1（工单 + 权限系统）完成版

## 分支策略
- `main`：稳定发布分支（仅合并已通过测试的代码），打标签发布
- `develop`（可选）：日常集成分支（多人协作时使用）
- `feature/*`：特性分支（例如：`feature/orders-rbac`、`feature/reports`）
- `hotfix/*`：线上紧急修复

小团队也可只用 `main` + `feature/*`，在完成后直接合并到 `main` 并打标签。

## 标签与里程碑
- 使用 `git tag -a vX.Y.Z -m "说明"` 创建注解标签
- 建议里程碑：
  - `v1.0.0`：pre-Phase1 初版（需要历史快照导入）
  - `v1.5.0`：Phase 1 全量完成
  - `v2.0.0`：Phase 2 Stage 1 完成（当前）
  - 后续：Stage 2（报表）→ `v2.1.0`，Stage 3（地图）→ `v2.2.0` 等

## 大文件与二进制
- 建议使用 Git LFS 管理图片与其他大文件
- 跟踪示例（需要安装 Git LFS 后执行）：
  ```bash
  git lfs install
  git lfs track "1-后端代码/photos/**"
  git add .gitattributes
  git commit -m "chore(lfs): track photos"
  ```

## 提交信息规范（推荐）
- 格式：`<type>(scope): subject`
- 常用 type：
  - `feat`：新功能
  - `fix`：修复
  - `chore`：构建/配置/脚手架
  - `docs`：文档
  - `refactor`：重构（无功能变化）
  - `perf`：性能
  - `test`：测试
- 示例：
  - `feat(orders): add assign/review APIs`
  - `chore(git): add .gitignore and lfs config`

## 从“当前代码”创建版本基线
当前工作区不包含 pre-Phase1 的历史快照。建议：

1) 先以“当前状态”创建仓库与标签（v2.0.0）
```powershell
Set-Location "d:\MySQL Project\highway-patrol-system"
git init
git checkout -b main
git add .
git commit -m "chore(repo): initialize with Phase 2 Stage 1 code"
git tag -a v2.0.0 -m "Phase 2 Stage 1: 工单 + RBAC"
```

2) 如果您稍后提供“pre-Phase1 代码包/备份”，可导入为独立的历史基线：
```powershell
# 假设已将 pre-Phase1 代码解压到临时目录 C:\temp\hps-prephase1
Set-Location "d:\MySQL Project\highway-patrol-system"
# 创建孤儿分支，不影响当前历史
git checkout --orphan pre-phase1
# 清空索引（不删除磁盘文件，谨慎操作）
git rm -r --cached .
# 复制旧代码覆盖当前工作区，然后：
#   将 C:\temp\hps-prephase1 的内容拷贝到当前目录
# 再执行提交
git add .
git commit -m "chore(baseline): import pre-Phase1 baseline"
git tag -a v1.0.0 -m "Pre-Phase1 baseline"
# 返回 main
git checkout main
```

3) 若已存在 Phase 1 完成版快照，可用相同步骤导入并标记 `v1.5.0`。

## 发布流程（最简）
1. 本地合并到 `main`
2. 运行测试/验证脚本（如：`verify_phase2_stage1.py`）
3. 打标签：`git tag -a vX.Y.Z -m "说明"`
4. 推送：
   ```powershell
   git remote add origin <your-remote-url>
   git push -u origin main --tags
   ```

## 备份建议
- 建议同时保留数据库 schema 的版本脚本（`3-数据库/`）并在变更时新增迁移 SQL
- 为大文件/照片目录启用 LFS 或在生产环境中避免提交实际业务照片

## FAQ
- Q: 现在就能打 `v1.0.0` 吗？
  - A: 不建议。没有旧版快照的情况下，`v1.0.0` 应等待导入 pre-Phase1 代码后标记，避免误导。
- Q: 没有 `develop` 分支可以吗？
  - A: 可以。小团队完全可以只用 `main` + `feature/*` 简化。
- Q: 照片是否纳入版本控制？
  - A: 建议用 LFS 或忽略业务上传照片，仅保留示例/占位文件。
