-- =====================================================
-- Phase 2 Stage 1: 工单状态机 + 多角色权限系统
-- =====================================================

-- =====================================================
-- 1. 扩展 User 表 - 支持多角色与权限
-- =====================================================

ALTER TABLE user ADD COLUMN role_id INT AFTER role;
ALTER TABLE user ADD COLUMN can_view_segments JSON COMMENT '可见路段列表 (JSON 数组)';
ALTER TABLE user ADD COLUMN last_login_ip VARCHAR(45) AFTER last_login;
ALTER TABLE user ADD COLUMN is_active TINYINT DEFAULT 1 AFTER role_id;

-- =====================================================
-- 2. 创建角色表
-- =====================================================

CREATE TABLE IF NOT EXISTS role (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '角色名: inspector, dispatcher, reviewer, auditor, admin',
    display_name VARCHAR(100) NOT NULL COMMENT '显示名称',
    description TEXT COMMENT '角色描述',
    priority INT DEFAULT 0 COMMENT '角色优先级 (管理员最高)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认角色
INSERT IGNORE INTO role (name, display_name, description, priority) VALUES
    ('inspector', '巡查员', '现场巡查，提交问题记录', 1),
    ('dispatcher', '派单人', '接收问题，分配处理任务', 3),
    ('processor', '处理人', '处理派单任务，提交处理结果', 2),
    ('auditor', '复核人', '审核处理结果，确认完成度', 4),
    ('admin', '管理员', '系统管理、配置、权限控制', 100);

-- =====================================================
-- 3. 创建权限表
-- =====================================================

CREATE TABLE IF NOT EXISTS permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    resource VARCHAR(100) NOT NULL COMMENT '资源: order, photo, report, user, config',
    action VARCHAR(50) NOT NULL COMMENT '操作: create, read, update, delete, export, batch_operate',
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_resource_action (resource, action),
    INDEX idx_resource (resource)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入权限
INSERT IGNORE INTO permission (resource, action, description) VALUES
    ('order', 'create', '创建工单'),
    ('order', 'read', '查看工单'),
    ('order', 'update', '更新工单'),
    ('order', 'delete', '删除工单'),
    ('order', 'assign', '派单'),
    ('order', 'process', '标记处理中'),
    ('order', 'review', '审核/复核'),
    ('order', 'reject', '驳回'),
    ('order', 'export', '导出'),
    ('order', 'batch_assign', '批量派单'),
    ('order', 'batch_review', '批量审核'),
    ('photo', 'read', '查看照片'),
    ('photo', 'delete', '删除照片'),
    ('report', 'read', '查看报表'),
    ('report', 'export', '导出报表'),
    ('report', 'create', '创建自定义报表'),
    ('user', 'read', '查看用户'),
    ('user', 'update', '更新用户'),
    ('user', 'delete', '删除用户'),
    ('config', 'read', '查看配置'),
    ('config', 'update', '修改配置');

-- =====================================================
-- 4. 创建角色权限映射表
-- =====================================================

CREATE TABLE IF NOT EXISTS role_permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    data_scope VARCHAR(50) DEFAULT 'own' COMMENT 'own=仅本人, dept=部门内, all=全部',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    KEY fk_role (role_id),
    KEY fk_permission (permission_id),
    FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permission(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 分配权限给各角色
INSERT IGNORE INTO role_permission (role_id, permission_id, data_scope) 
SELECT r.id, p.id, CASE 
    WHEN r.name = 'inspector' AND p.action IN ('create', 'read', 'export') THEN 'own'
    WHEN r.name = 'dispatcher' AND p.action IN ('read', 'assign', 'batch_assign') THEN 'all'
    WHEN r.name = 'processor' AND p.action IN ('read', 'process', 'update') THEN 'own'
    WHEN r.name = 'auditor' AND p.action IN ('read', 'review', 'reject', 'batch_review') THEN 'all'
    WHEN r.name = 'admin' THEN 'all'
END
FROM role r CROSS JOIN permission p
WHERE (
    (r.name = 'inspector' AND p.resource IN ('order', 'photo') AND p.action IN ('create', 'read', 'export'))
    OR (r.name = 'dispatcher' AND p.resource = 'order' AND p.action IN ('read', 'assign', 'batch_assign'))
    OR (r.name = 'processor' AND p.resource = 'order' AND p.action IN ('read', 'process', 'update'))
    OR (r.name = 'auditor' AND p.resource = 'order' AND p.action IN ('read', 'review', 'reject', 'batch_review'))
    OR (r.name = 'admin')
);

-- =====================================================
-- 5. 创建用户权限覆盖表 (特殊权限)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_permission_override (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    permission_id INT,
    resource VARCHAR(100),
    action VARCHAR(50),
    allowed TINYINT DEFAULT 1 COMMENT '1=允许, 0=禁止',
    remark VARCHAR(255),
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    KEY fk_user (user_id),
    KEY fk_permission (permission_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 6. 扩展 InspectionRecord 表 - 支持工单流转
-- =====================================================

ALTER TABLE inspectionrecord ADD COLUMN order_status VARCHAR(50) DEFAULT 'new' COMMENT '工单状态: new→assigned→processing→reviewed→archived';
ALTER TABLE inspectionrecord ADD COLUMN assigned_user_id INT COMMENT '派单人';
ALTER TABLE inspectionrecord ADD COLUMN assigned_time DATETIME COMMENT '派单时间';
ALTER TABLE inspectionrecord ADD COLUMN processor_id INT COMMENT '处理人';
ALTER TABLE inspectionrecord ADD COLUMN process_time DATETIME COMMENT '处理时间';
ALTER TABLE inspectionrecord ADD COLUMN reviewer_id INT COMMENT '复核人';
ALTER TABLE inspectionrecord ADD COLUMN review_time DATETIME COMMENT '复核时间';
ALTER TABLE inspectionrecord ADD COLUMN review_remark TEXT COMMENT '复核意见';
ALTER TABLE inspectionrecord ADD COLUMN reject_count INT DEFAULT 0 COMMENT '驳回次数';
ALTER TABLE inspectionrecord ADD COLUMN reject_reason TEXT COMMENT '最后驳回原因';

-- 添加索引以提高查询性能
ALTER TABLE inspectionrecord ADD INDEX idx_order_status (order_status);
ALTER TABLE inspectionrecord ADD INDEX idx_assigned_user (assigned_user_id);
ALTER TABLE inspectionrecord ADD INDEX idx_processor (processor_id);
ALTER TABLE inspectionrecord ADD INDEX idx_reviewer (reviewer_id);
ALTER TABLE inspectionrecord ADD INDEX idx_status_time (order_status, upload_time);

-- =====================================================
-- 7. 创建工单流转日志表
-- =====================================================

CREATE TABLE IF NOT EXISTS order_flow_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL COMMENT '对应 inspectionrecord.id',
    old_status VARCHAR(50) COMMENT '旧状态',
    new_status VARCHAR(50) COMMENT '新状态',
    operator_id INT NOT NULL COMMENT '操作人',
    operator_role VARCHAR(50) COMMENT '操作人角色',
    operation VARCHAR(50) COMMENT '操作类型: assign, process, review, reject, archive',
    remark TEXT COMMENT '备注/驳回原因',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    
    KEY idx_order (order_id),
    KEY idx_operator (operator_id),
    KEY idx_time (operation_time),
    KEY idx_status (old_status, new_status),
    FOREIGN KEY (order_id) REFERENCES inspectionrecord(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 8. 创建 SLA 配置表
-- =====================================================

CREATE TABLE IF NOT EXISTS sla_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    problem_type_id INT NOT NULL COMMENT '问题类型',
    name VARCHAR(100),
    dispatch_sla_hours INT DEFAULT 24 COMMENT '派单 SLA (小时)',
    process_sla_hours INT DEFAULT 72 COMMENT '处理 SLA (小时)',
    review_sla_hours INT DEFAULT 24 COMMENT '复核 SLA (小时)',
    total_sla_hours INT DEFAULT 120 COMMENT '总体 SLA (小时)',
    priority INT DEFAULT 5 COMMENT '优先级',
    enabled TINYINT DEFAULT 1,
    remark TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    KEY idx_problem_type (problem_type_id),
    KEY idx_enabled (enabled),
    FOREIGN KEY (problem_type_id) REFERENCES problemtype(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 9. 创建 SLA 违规告警表
-- =====================================================

CREATE TABLE IF NOT EXISTS sla_alert (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    sla_type VARCHAR(50) COMMENT 'dispatch, process, review, total',
    due_time DATETIME COMMENT 'SLA 截止时间',
    alert_level VARCHAR(50) COMMENT 'warning, critical',
    alerted_at DATETIME COMMENT '告警时间',
    resolved_at DATETIME COMMENT '解决时间',
    resolved_by INT COMMENT '解决人',
    
    KEY idx_order (order_id),
    KEY idx_due_time (due_time),
    KEY idx_alert_level (alert_level),
    FOREIGN KEY (order_id) REFERENCES inspectionrecord(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 10. 创建操作审计日志表
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id INT NOT NULL,
    operator_name VARCHAR(50),
    resource_type VARCHAR(50) COMMENT 'order, photo, user, config',
    resource_id INT,
    action VARCHAR(50) COMMENT 'create, update, delete, export, assign, review',
    old_value JSON COMMENT '变更前值',
    new_value JSON COMMENT '变更后值',
    change_summary TEXT COMMENT '变更摘要',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50) DEFAULT 'success' COMMENT 'success, failed',
    error_msg TEXT,
    
    KEY idx_operator (operator_id),
    KEY idx_resource (resource_type, resource_id),
    KEY idx_time (operation_time),
    KEY idx_action (action),
    KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 自动化日志清理 (保留 6 个月)
CREATE EVENT IF NOT EXISTS clean_old_audit_logs
ON SCHEDULE EVERY 1 DAY
STARTS NOW()
DO
DELETE FROM audit_log WHERE operation_time < DATE_SUB(NOW(), INTERVAL 6 MONTH);

-- =====================================================
-- 11. 创建 IP 白名单表 (管理员安全)
-- =====================================================

CREATE TABLE IF NOT EXISTS admin_ip_whitelist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ip_address VARCHAR(45) NOT NULL,
    ip_range_start VARCHAR(45) COMMENT '范围开始 (用于 CIDR)',
    ip_range_end VARCHAR(45) COMMENT '范围结束',
    description VARCHAR(255),
    enabled TINYINT DEFAULT 1,
    added_by INT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_ip (ip_address),
    KEY idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 12. 创建 JWT 刷新令牌表
-- =====================================================

CREATE TABLE IF NOT EXISTS refresh_token (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL COMMENT 'Token 的 SHA256',
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_ip VARCHAR(45),
    revoked_at DATETIME COMMENT '撤销时间',
    
    KEY idx_user (user_id),
    KEY idx_expires (expires_at),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 13. 创建部门与路段映射表 (细粒度权限)
-- =====================================================

CREATE TABLE IF NOT EXISTS department_segment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    department_id INT NOT NULL,
    segment_id INT NOT NULL,
    primary_dept TINYINT DEFAULT 0 COMMENT '是否为主负责部门',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_dept_segment (department_id, segment_id),
    KEY idx_department (department_id),
    KEY idx_segment (segment_id),
    FOREIGN KEY (department_id) REFERENCES department(id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id) REFERENCES roadsegment(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 14. 视图：工单概览
-- =====================================================

CREATE OR REPLACE VIEW vw_order_overview AS
SELECT 
    ir.id,
    ir.order_status,
    ir.description,
    ir.upload_time,
    ir.assigned_time,
    ir.process_time,
    ir.review_time,
    u_creator.real_name AS creator_name,
    u_assigned.real_name AS assigned_by,
    u_processor.real_name AS processor_name,
    u_reviewer.real_name AS reviewer_name,
    pt.name AS problem_type,
    d.name AS department,
    rs.name AS road_segment,
    ir.reject_count,
    ir.order_status AS status_for_dashboard
FROM inspectionrecord ir
LEFT JOIN user u_creator ON ir.user_id = u_creator.user_id
LEFT JOIN user u_assigned ON ir.assigned_user_id = u_assigned.user_id
LEFT JOIN user u_processor ON ir.processor_id = u_processor.user_id
LEFT JOIN user u_reviewer ON ir.reviewer_id = u_reviewer.user_id
LEFT JOIN problemtype pt ON ir.problem_id = pt.id
LEFT JOIN roadsegment rs ON ir.road_id = rs.id
LEFT JOIN department d ON rs.department_id = d.id;

-- =====================================================
-- 15. 视图：SLA 统计
-- =====================================================

CREATE OR REPLACE VIEW vw_sla_statistics AS
SELECT 
    sc.id,
    sc.name,
    COUNT(ir.id) AS total_orders,
    SUM(CASE WHEN ir.order_status = 'archived' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, ir.upload_time, ir.assigned_time) > sc.dispatch_sla_hours AND ir.assigned_time IS NOT NULL THEN 1 ELSE 0 END) AS dispatch_sla_miss,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, ir.assigned_time, ir.process_time) > sc.process_sla_hours AND ir.process_time IS NOT NULL THEN 1 ELSE 0 END) AS process_sla_miss,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, ir.process_time, ir.review_time) > sc.review_sla_hours AND ir.review_time IS NOT NULL THEN 1 ELSE 0 END) AS review_sla_miss,
    ROUND(100.0 * SUM(CASE WHEN TIMESTAMPDIFF(HOUR, ir.upload_time, ir.review_time) <= sc.total_sla_hours AND ir.review_time IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(ir.id), 0), 2) AS sla_compliance_rate
FROM sla_config sc
LEFT JOIN problemtype pt ON sc.problem_type_id = pt.id
LEFT JOIN inspectionrecord ir ON ir.problem_id = pt.id
WHERE sc.enabled = 1
GROUP BY sc.id;

-- =====================================================
-- 索引优化
-- =====================================================

-- 频繁查询的索引
CREATE INDEX IF NOT EXISTS idx_user_role ON user(role_id, is_active);
CREATE INDEX IF NOT EXISTS idx_order_timestamps ON inspectionrecord(upload_time, order_status, assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_time_operator ON audit_log(operation_time DESC, operator_id);

-- =====================================================
-- 数据迁移注意事项
-- =====================================================

/*
1. 现有用户迁移：
   - 根据现有 user.role ('inspector' or 'admin') 分配新的 role_id
   
   UPDATE user u
   SET u.role_id = (SELECT id FROM role WHERE name = 
       CASE WHEN u.role = 'inspector' THEN 'inspector' ELSE 'admin' END)
   WHERE u.role_id IS NULL;

2. 现有检查记录：
   - 所有已存在的记录 order_status 设为 'archived' (认为已完成)
   - 但建议在应用层提醒管理员进行审查

3. SLA 配置：
   - 管理员需要配置各问题类型的 SLA
   - 默认建议：派单 24h, 处理 72h, 复核 24h

4. 权限检查：
   - 在应用中实现权限拦截中间件
   - 使用 FastAPI Depends 做依赖注入

5. 向后兼容：
   - 旧 API 继续支持，但在内部转换为新权限体系
   - 渐进式迁移业务逻辑
*/

-- =====================================================
-- 配置完成检查
-- =====================================================

-- 验证所有表都已创建
SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME IN (
    'role', 'permission', 'role_permission', 'user_permission_override',
    'order_flow_log', 'sla_config', 'sla_alert', 'audit_log',
    'admin_ip_whitelist', 'refresh_token', 'department_segment'
)
ORDER BY TABLE_NAME;

-- =====================================================
-- 结束
-- =====================================================

-- EOF: 工单状态机 + 多角色权限系统迁移脚本
