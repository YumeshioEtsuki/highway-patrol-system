-- ============================================================================
-- 初始测试数据
-- ============================================================================
-- 功能：插入示例数据用于开发/测试
-- 执行：mysql -u root -p road_patrol_db < 03_test_data.sql
-- 说明：所有数据为示例值，生产环境需要替换为真实数据
-- 密码：使用 Argon2 哈希（在后端自动处理）
-- ============================================================================

USE road_patrol_db;

-- ============================================================================
-- 1. 插入部门数据
-- ============================================================================
INSERT INTO Department (department_name) VALUES 
('公路养护部'),
('交通运输部'),
('基础设施部');

-- ============================================================================
-- 2. 插入路段数据
-- ============================================================================
INSERT INTO RoadSegment (segment_name, start_number, end_number, department_id, region) VALUES 
('国道G107', 1000, 2000, 1, '华北'),
('京哈高速', 2000, 3000, 1, '华北'),
('沪浙高速', 3000, 4000, 2, '华东'),
('京藏高速', 4000, 5000, 2, '华北');

-- ============================================================================
-- 3. 插入用户数据（密码需使用后端 Argon2 加密，此处为占位符）
-- ============================================================================
INSERT INTO User (username, password, real_name, phone, email, role, department_id, created_at) VALUES 
('admin', '$argon2id$v=19$m=65536,t=3,p=4$...', '系统管理员', '11451419198', 'admin@example.com', 'admin', 1, NOW()),
('inspector1', '$argon2id$v=19$m=65536,t=3,p=4$...', '巡查员1', '11451419199', 'inspector1@example.com', 'inspector', 1, NOW()),
('inspector2', '$argon2id$v=19$m=65536,t=3,p=4$...', '巡查员2', '11451419200', 'inspector2@example.com', 'inspector', 2, NOW());

-- ============================================================================
-- 4. 插入问题类型数据
-- ============================================================================
INSERT INTO ProblemType (type_name, parent_id) VALUES 
('路面破损', NULL),
  ('坑洼', 1),
  ('裂纹', 1),
('护栏损坏', NULL),
  ('护栏变形', 4),
  ('护栏缺失', 4),
('标线模糊', NULL),
('排水系统', NULL);

-- ============================================================================
-- 5. 插入巡查记录数据
-- ============================================================================
INSERT INTO InspectionRecord (user_id, upload_time, latitude, longitude, segment_id, problem_type_id, description, severity, status, data_type, region) VALUES 
(2, DATE_SUB(NOW(), INTERVAL 5 DAY), 39.915, 116.404, 1, 2, '路面有明显坑洼', 3, 'pending', 'test', '华北'),
(2, DATE_SUB(NOW(), INTERVAL 3 DAY), 39.920, 116.410, 1, 3, '路面有细微裂纹', 2, 'processing', 'test', '华北'),
(3, DATE_SUB(NOW(), INTERVAL 1 DAY), 30.287, 120.155, 3, 5, '护栏严重变形', 4, 'resolved', 'real', '华东'),
(3, NOW(), 30.290, 120.160, 3, 6, '护栏缺失一段', 3, 'pending', 'real', '华东');

-- ============================================================================
-- 6. 插入照片数据
-- ============================================================================
INSERT INTO Photo (record_id, photo_type, file_path, file_name, file_size, is_watermarked) VALUES 
(1, 'test_pictures', '1-后端代码/photos/road_pothole_1.jpg', 'road_pothole_1.jpg', 317489, TRUE),
(1, 'test_pictures', '1-后端代码/photos/road_pothole_2.jpg', 'road_pothole_2.jpg', 287645, TRUE),
(2, 'test_pictures', '1-后端代码/photos/road_crack_1.jpg', 'road_crack_1.jpg', 254823, TRUE),
(3, 'test_pictures', '1-后端代码/photos/guardrail_damage_1.jpg', 'guardrail_damage_1.jpg', 412356, TRUE),
(3, 'after_fix', '1-后端代码/photos/guardrail_after_fix_1.jpg', 'guardrail_after_fix_1.jpg', 398245, TRUE),
(4, 'test_pictures', '1-后端代码/photos/guardrail_missing_1.jpg', 'guardrail_missing_1.jpg', 365234, TRUE);

-- ============================================================================
-- 7. 插入审计日志样例数据
-- ============================================================================
INSERT INTO AuditLog (user_id, action, resource, resource_id, details, timestamp) VALUES 
(1, 'REVIEW', 'InspectionRecord', 1, '已审核，标记为处理中', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'EXPORT', 'InspectionRecord', NULL, '导出过去7天的巡查记录', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 'REJECT', 'InspectionRecord', 2, '拒绝：照片不清晰', NOW());

-- ============================================================================
-- 验证数据插入
-- ============================================================================
SELECT '✅ 测试数据插入完成！' AS Status;
SELECT 'ℹ️ 数据统计' AS Info;
SELECT '部门' AS 类型, COUNT(*) AS 数量 FROM Department UNION ALL
SELECT '路段', COUNT(*) FROM RoadSegment UNION ALL
SELECT '用户', COUNT(*) FROM User UNION ALL
SELECT '问题类型', COUNT(*) FROM ProblemType UNION ALL
SELECT '巡查记录', COUNT(*) FROM InspectionRecord UNION ALL
SELECT '照片', COUNT(*) FROM Photo UNION ALL
SELECT '审计日志', COUNT(*) FROM AuditLog;

-- ============================================================================
-- 删除测试数据（如需重置）
-- ============================================================================
-- TRUNCATE TABLE AuditLog;
-- TRUNCATE TABLE Photo;
-- TRUNCATE TABLE InspectionRecord;
-- TRUNCATE TABLE ProblemType;
-- TRUNCATE TABLE User;
-- TRUNCATE TABLE RoadSegment;
-- TRUNCATE TABLE Department;
