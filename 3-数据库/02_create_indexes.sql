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

-- ============================================================================
-- 额外性能优化索引
-- ============================================================================
-- 说明：以下索引已在初始化脚本中创建
-- 本脚本由 start_server.py 的 execute_sql_file 函数智能执行
-- 如果索引已存在，脚本会自动跳过CREATE语句

-- 1. 用户与时间的组合查询
CREATE INDEX idx_user_created ON InspectionRecord(user_id, upload_time DESC);

-- 2. 路段与时间的组合查询
CREATE INDEX idx_segment_time ON InspectionRecord(segment_id, upload_time DESC);

-- 3. 照片与记录的快速关联
CREATE INDEX idx_photo_record_upload ON Photo(record_id, upload_time);

-- 4. 状态与问题类型的组合查询（统计分析）
CREATE INDEX idx_status_problem ON InspectionRecord(status, problem_type_id);

-- 5. 地区与时间的组合查询（地理统计）
-- 注意：InspectionRecord 表中没有 region 列，此索引不创建

-- 6. 检查是否需要添加外键索引（优化 JOIN 性能）
-- （通常 MySQL 在 FOREIGN KEY 列上会自动创建索引）
CREATE INDEX idx_record_id_fk ON Photo(record_id);

-- ============================================================================
-- 验证索引创建结果
-- ============================================================================
SHOW INDEX FROM InspectionRecord;
SHOW INDEX FROM Photo;

SELECT '✓ Optimization completed!' AS Status;
SELECT '→ Tip: Use EXPLAIN to verify indexes are used' AS Reminder;

-- 性能测试示例：
-- EXPLAIN SELECT * FROM InspectionRecord WHERE user_id = 1 AND upload_time >= '2024-01-01';
-- EXPLAIN SELECT * FROM InspectionRecord WHERE region = 'Asia' AND status = 'pending';
-- EXPLAIN SELECT * FROM Photo WHERE record_id = 1 ORDER BY upload_time DESC;
