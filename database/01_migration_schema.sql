-- ============================================================================
-- 数据库迁移脚本（可选）
-- ============================================================================
-- 功能：为现有数据库升级字段和表结构
-- 场景：当从旧数据库升级到新版本时执行
-- 执行：mysql -u root -p road_patrol_db < 01_migration.sql
-- 注意：所有 ALTER 操作都使用 IF NOT EXISTS/IF EXISTS 确保幂等性
-- ============================================================================

USE road_patrol_db;

-- 迁移 1：为 InspectionRecord 添加 data_type 字段（区分真实/测试数据）
-- 创建日期：2025-12-22
-- 说明：支持多模式（检视/运维），避免测试数据污染
ALTER TABLE InspectionRecord 
ADD COLUMN IF NOT EXISTS data_type ENUM('real', 'test') DEFAULT 'real' 
AFTER status COMMENT '数据类型：real=真实数据，test=测试数据';

-- 迁移 2：为 RoadSegment 添加 region 字段（地区字段）
ALTER TABLE RoadSegment 
ADD COLUMN IF NOT EXISTS region VARCHAR(50) DEFAULT NULL 
AFTER department_id COMMENT '所属地区：华北/华东/华中/华南/西北/西南/东北';

-- 迁移 3：为 InspectionRecord 添加 region 冗余字段（提升查询性能）
ALTER TABLE InspectionRecord 
ADD COLUMN IF NOT EXISTS region VARCHAR(50) DEFAULT NULL 
AFTER data_type COMMENT '所属地区（冗余字段，从RoadSegment继承）';

-- 迁移 4：创建 AuditLog 审计日志表（如不存在）
CREATE TABLE IF NOT EXISTS AuditLog (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resource_id INT,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_action_time (action, timestamp DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';

-- 迁移 5：为 Department 添加 created_at 字段
ALTER TABLE Department 
ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
COMMENT '创建时间';

-- 迁移 6：为 User 添加额外字段
ALTER TABLE User 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE COMMENT '账户状态';

-- 迁移 7：同步 region 数据（将 RoadSegment 的 region 赋值给 InspectionRecord）
-- 使用 IGNORE 防止重复键错误
UPDATE IGNORE InspectionRecord ir
INNER JOIN RoadSegment rs ON ir.segment_id = rs.segment_id
SET ir.region = rs.region
WHERE ir.region IS NULL AND rs.region IS NOT NULL;

-- 迁移 8：为现有数据设置默认 region（若仍为 NULL）
UPDATE RoadSegment SET region = 'Asia' WHERE region IS NULL;
UPDATE InspectionRecord SET region = 'Asia' WHERE region IS NULL;

-- ============================================================================
-- 迁移完成
-- ============================================================================
SELECT '✅ 数据库迁移完成！' AS Status;
SELECT 'ℹ️ 请根据实际情况修改 region 字段值' AS Reminder;
