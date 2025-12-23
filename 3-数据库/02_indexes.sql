-- ============================================================================
-- 数据库性能优化 - 索引脚本
-- ============================================================================
-- 功能：为关键查询添加必要索引以提升查询性能
-- 执行：mysql -u root -p road_patrol_db < 02_indexes.sql
-- 说明：所有操作都使用 CREATE INDEX IF NOT EXISTS 确保幂等性
-- 参考：EXPLAIN SELECT ... 查看查询计划是否使用索引
-- ============================================================================

USE road_patrol_db;

-- 说明：核心索引已在 00_init.sql 中创建，以下为额外优化索引

-- ============================================================================
-- 额外性能优化索引
-- ============================================================================

-- 1. 用户与时间的组合查询
CREATE INDEX IF NOT EXISTS idx_user_created 
ON InspectionRecord(user_id, upload_time DESC);

-- 2. 路段与时间的组合查询
CREATE INDEX IF NOT EXISTS idx_segment_time 
ON InspectionRecord(segment_id, upload_time DESC);

-- 3. 照片与记录的快速关联
CREATE INDEX IF NOT EXISTS idx_photo_record_upload 
ON Photo(record_id, upload_time);

-- 4. 状态与问题类型的组合查询（统计分析）
CREATE INDEX IF NOT EXISTS idx_status_problem 
ON InspectionRecord(status, problem_type_id);

-- 5. 地区与时间的组合查询（地理统计）
CREATE INDEX IF NOT EXISTS idx_region_time 
ON InspectionRecord(region, upload_time DESC);

-- 6. 检查是否需要添加外键索引（优化 JOIN 性能）
-- （通常 MySQL 在 FOREIGN KEY 列上会自动创建索引，但以下显式创建以确保）
CREATE INDEX IF NOT EXISTS idx_record_id_fk 
ON Photo(record_id);

-- ============================================================================
-- 验证索引创建结果
-- ============================================================================
SHOW INDEX FROM InspectionRecord;
SHOW INDEX FROM Photo;

SELECT '✅ 性能优化完成！' AS Status;
SELECT '💡 建议：使用 EXPLAIN 命令验证查询计划是否正确使用了索引' AS Reminder;

-- 性能测试示例：
-- EXPLAIN SELECT * FROM InspectionRecord WHERE user_id = 1 AND upload_time >= '2024-01-01';
-- EXPLAIN SELECT * FROM InspectionRecord WHERE region = 'Asia' AND status = 'pending';
-- EXPLAIN SELECT * FROM Photo WHERE record_id = 1 ORDER BY upload_time DESC;
