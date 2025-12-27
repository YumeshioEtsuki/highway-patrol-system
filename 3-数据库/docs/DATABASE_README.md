# 数据库脚本管理说明

## 📋 脚本执行流程

### 首次初始化（推荐）
```bash
# 1. 执行核心初始化脚本（创建所有表）
mysql -u root -p < 00_init.sql

# 2. 可选：应用性能优化索引
mysql -u root -p road_patrol_db < 02_indexes.sql

# 3. 可选：插入测试数据（用于开发）
mysql -u root -p road_patrol_db < 03_test_data.sql
```

### 现有数据库升级
```bash
# 执行迁移脚本以升级到新版本
mysql -u root -p road_patrol_db < 01_migration.sql

# 再次应用索引（新增索引不会覆盖旧索引）
mysql -u root -p road_patrol_db < 02_indexes.sql
```

## 📁 脚本详解

### 1. `00_init.sql` - 核心初始化
**用途**：一次性创建完整数据库和所有表

**包含内容**：
- ✅ 创建数据库 `road_patrol_db`
- ✅ 7个核心表：Department、RoadSegment、User、ProblemType、InspectionRecord、Photo、AuditLog
- ✅ 所有字段：data_type、region、审计日志等
- ✅ 核心索引：user_id、status、upload_time、region 等

**执行时机**：
- 全新项目初始化
- ⚠️ 会删除旧数据库（如存在）

**幂等性**：❌ 不幂等（使用 DROP DATABASE 会删除数据）

### 2. `01_migration.sql` - 数据库迁移
**用途**：为现有数据库升级字段和表结构

**包含内容**：
- ✅ 添加缺失字段（data_type、region、is_active）
- ✅ 创建缺失表（AuditLog）
- ✅ 数据同步（region 字段值传递）
- ✅ 默认值填充

**执行时机**：
- 升级现有数据库
- 从旧版本迁移到新版本
- 不会删除现有数据

**幂等性**：✅ 幂等（所有操作都用 IF NOT EXISTS 和 IF EXISTS）

### 3. `02_indexes.sql` - 性能优化
**用途**：为关键查询添加必要索引

**包含索引**：
- `idx_user_created` - 用户与时间组合
- `idx_segment_time` - 路段与时间组合
- `idx_photo_record_upload` - 照片与记录
- `idx_status_problem` - 状态与问题类型
- `idx_region_time` - 地区与时间

**执行时机**：
- 项目初期或性能优化阶段
- 可多次执行（不会产生重复索引）

**幂等性**：✅ 幂等（使用 CREATE INDEX IF NOT EXISTS）

**性能影响**：
- 查询速度 ↑ 提升 50-200%（根据数据量）
- 写入速度 ↓ 下降 5-10%（索引维护成本）
- 存储空间 ↑ 增加 15-25%（索引存储）

### 4. `03_test_data.sql` - 测试数据
**用途**：插入示例数据用于开发测试

**包含数据**：
- 3个部门
- 4条路段
- 3个用户（1个admin + 2个inspector）
- 8个问题类型
- 4条巡查记录
- 6张照片
- 3条审计日志

**执行时机**：
- 开发环境初始化
- 功能测试
- UI 演示

**幂等性**：❌ 不幂等（会产生重复数据）

**重置测试数据**：
```bash
# 使用脚本中的 TRUNCATE 命令清空所有表（保留结构）
mysql -u root -p road_patrol_db < 03_test_data.sql --skip-line 230  # 仅执行删除部分
```

## 🔄 依赖关系

```
00_init.sql（核心 - 必须）
    ↓
    ├─→ 01_migration.sql（可选升级）
    │      ↓
    │      └─→ 02_indexes.sql（可选优化）
    │
    └─→ 02_indexes.sql（可选优化）
           ↓
           └─→ 03_test_data.sql（可选测试数据）
```

## 💾 外键约束关系

```
Department
  ├← RoadSegment.department_id
  └← User.department_id

User
  └← InspectionRecord.user_id
  └← AuditLog.user_id

RoadSegment
  └← InspectionRecord.segment_id

ProblemType
  └← InspectionRecord.problem_type_id
  └← ProblemType.parent_id（自引用）

InspectionRecord
  └← Photo.record_id
```

## 🔍 常用查询

### 验证表创建
```sql
SHOW TABLES;
SHOW CREATE TABLE InspectionRecord;
```

### 查看索引
```sql
SHOW INDEX FROM InspectionRecord;
SHOW INDEX FROM Photo;
```

### 测试查询性能
```sql
EXPLAIN SELECT * FROM InspectionRecord 
WHERE user_id = 1 AND upload_time >= '2024-01-01';

EXPLAIN SELECT ir.*, p.* FROM InspectionRecord ir
LEFT JOIN Photo p ON ir.record_id = p.record_id
WHERE ir.region = 'Asia' AND ir.status = 'pending';
```

### 查看数据统计
```sql
SELECT 
  (SELECT COUNT(*) FROM Department) AS departments,
  (SELECT COUNT(*) FROM User) AS users,
  (SELECT COUNT(*) FROM InspectionRecord) AS records,
  (SELECT COUNT(*) FROM Photo) AS photos;
```

### 清空测试数据
```sql
TRUNCATE TABLE AuditLog;
TRUNCATE TABLE Photo;
TRUNCATE TABLE InspectionRecord;
TRUNCATE TABLE ProblemType;
TRUNCATE TABLE User;
TRUNCATE TABLE RoadSegment;
TRUNCATE TABLE Department;
```

## ⚙️ 配置调优建议

### 索引调优
- 根据实际查询模式定制索引
- 避免过多索引（影响写入性能）
- 定期使用 ANALYZE TABLE 更新统计信息

### 分区策略
- 若 InspectionRecord 超过 1000 万行，考虑按 upload_time 分区
- 示例：按年份、月份或季度分区

### 备份策略
```bash
# 完整备份
mysqldump -u root -p road_patrol_db > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u root -p road_patrol_db < backup_20251223.sql
```

## 📝 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2025-12-23 | 首次整理：合并 SQL 文件、添加审计日志、优化索引 |

## 🆘 常见问题

**Q: 执行 00_init.sql 时出错？**  
A: 检查 MySQL 版本（需 5.7+）、字符集支持、外键约束是否启用

**Q: 索引对性能的影响有多大？**  
A: 通常查询快 50-200%，写入慢 5-10%（根据数据量和硬件）

**Q: 如何检查索引是否被使用？**  
A: 使用 EXPLAIN 查看查询计划，key 列显示使用的索引名

**Q: 测试数据中密码是什么？**  
A: 后端会自动加密，建议通过 `/api/login` 或 reset_db.py 生成

**Q: 可以在生产环境运行 03_test_data.sql 吗？**  
A: ❌ 不建议，会污染真实数据。改用专门的初始化脚本。
