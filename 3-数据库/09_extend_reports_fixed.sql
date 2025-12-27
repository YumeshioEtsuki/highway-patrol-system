-- Phase 2 Stage 2: 智能报表与导出系统（修正版）
-- 创建时间: 2025-12-24
-- 说明: 适配现有数据库结构（user_id, segment_id, status）

USE road_patrol_db;

-- 1. 报表模板表
CREATE TABLE IF NOT EXISTS report_template (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    type ENUM('daily','weekly','monthly','custom') NOT NULL COMMENT '报表类型',
    config JSON COMMENT '字段配置 {dimensions:[],metrics:[],filters:{}}',
    sql_template TEXT COMMENT 'SQL 查询模板（支持变量替换）',
    chart_config JSON COMMENT '图表配置',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    enabled TINYINT DEFAULT 1,
    INDEX idx_type (type),
    INDEX idx_creator (created_by),
    INDEX idx_enabled (enabled),
    FOREIGN KEY (created_by) REFERENCES user(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表模板';

-- 2. 报表订阅表
CREATE TABLE IF NOT EXISTS report_subscription (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL,
    subscriber_id INT NOT NULL COMMENT '订阅用户 ID',
    frequency ENUM('daily','weekly','monthly') NOT NULL COMMENT '发送频率',
    send_time TIME COMMENT '发送时间（如 09:00:00）',
    send_day VARCHAR(20) COMMENT '发送日期（如 monday, 1-31）',
    delivery_method ENUM('email','wechat','dingtalk') DEFAULT 'email',
    delivery_target VARCHAR(255) COMMENT '接收地址（邮箱/企业微信 webhook）',
    enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES report_template(id) ON DELETE CASCADE,
    FOREIGN KEY (subscriber_id) REFERENCES user(user_id) ON DELETE CASCADE,
    INDEX idx_schedule (frequency, send_time, enabled),
    INDEX idx_subscriber (subscriber_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表订阅';

-- 3. 报表生成历史表
CREATE TABLE IF NOT EXISTS report_generation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL,
    generated_by INT COMMENT '生成人（NULL 表示定时任务）',
    generation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_range_start DATE COMMENT '报表数据起始日期',
    time_range_end DATE COMMENT '报表数据结束日期',
    file_path VARCHAR(500) COMMENT '文件存储路径',
    file_type ENUM('pdf','xlsx','csv') NOT NULL,
    file_size INT COMMENT '文件大小（字节）',
    download_url VARCHAR(500) COMMENT '下载链接',
    expires_at DATETIME COMMENT '下载链接过期时间',
    status ENUM('pending','generating','completed','failed') DEFAULT 'pending',
    error_msg TEXT,
    row_count INT COMMENT '数据行数',
    FOREIGN KEY (template_id) REFERENCES report_template(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES user(user_id) ON DELETE SET NULL,
    INDEX idx_status (status, generation_time),
    INDEX idx_expires (expires_at),
    INDEX idx_template (template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表生成历史';

-- 4. 报表发送日志表
CREATE TABLE IF NOT EXISTS report_send_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL COMMENT 'report_generation_history ID',
    subscription_id INT COMMENT '订阅 ID（手动发送则为 NULL）',
    sent_to VARCHAR(255) NOT NULL COMMENT '接收人邮箱/ID',
    send_method ENUM('email','wechat','dingtalk') NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending','sent','failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    error_msg TEXT,
    FOREIGN KEY (report_id) REFERENCES report_generation_history(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES report_subscription(id) ON DELETE SET NULL,
    INDEX idx_status (status, sent_at),
    INDEX idx_report (report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报表发送日志';

-- 5. 自定义统计指标表（已在前面创建，跳过）

-- 6. 插入预置报表模板
INSERT INTO report_template (name, type, config, chart_config, created_by, enabled) VALUES
-- 日报模板
('巡查日报', 'daily', JSON_OBJECT(
    'dimensions', JSON_ARRAY('department', 'segment'),
    'metrics', JSON_ARRAY('total_inspections', 'pending_orders', 'overdue_orders', 'avg_resolution_time'),
    'filters', JSON_OBJECT()
), JSON_OBJECT(
    'charts', JSON_ARRAY(
        JSON_OBJECT('type', 'bar', 'title', '各部门巡查量', 'metric', 'total_inspections'),
        JSON_OBJECT('type', 'pie', 'title', '问题类型分布', 'metric', 'problem_distribution')
    )
), NULL, 1),

-- 周报模板
('巡查周报', 'weekly', JSON_OBJECT(
    'metrics', JSON_ARRAY('weekly_trend', 'department_ranking', 'problem_type_analysis', 'efficiency_score'),
    'comparison', JSON_OBJECT('last_week', true, 'same_period_last_year', false)
), JSON_OBJECT(
    'charts', JSON_ARRAY(
        JSON_OBJECT('type', 'line', 'title', '周趋势对比', 'metric', 'weekly_trend'),
        JSON_OBJECT('type', 'bar', 'title', '部门排名', 'metric', 'department_ranking')
    )
), NULL, 1),

-- 月报模板
('巡查月报', 'monthly', JSON_OBJECT(
    'metrics', JSON_ARRAY('monthly_summary', 'kpi_achievement', 'recurrence_rate', 'quality_score'),
    'includes', JSON_ARRAY('executive_summary', 'detailed_breakdown', 'recommendations')
), JSON_OBJECT(
    'charts', JSON_ARRAY(
        JSON_OBJECT('type', 'line', 'title', '月度趋势', 'metric', 'monthly_summary'),
        JSON_OBJECT('type', 'gauge', 'title', 'KPI达成', 'metric', 'kpi_achievement')
    )
), NULL, 1);

-- 7. 更新已有指标（如果需要）
UPDATE report_metric SET enabled = 1 WHERE name IN ('total_inspections', 'pending_orders', 'overdue_orders');

-- 8. 创建报表统计视图（优化查询性能）
CREATE OR REPLACE VIEW v_daily_report_summary AS
SELECT 
    DATE(i.upload_time) AS report_date,
    COALESCE(d.name, '未分配部门') AS department_name,
    COALESCE(s.name, '未指定路段') AS segment_name,
    COUNT(i.record_id) AS total_inspections,
    SUM(CASE WHEN i.status = 'pending' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN i.status = 'pending' 
        AND TIMESTAMPDIFF(HOUR, i.upload_time, NOW()) > 48 THEN 1 ELSE 0 END) AS overdue_orders,
    AVG(CASE WHEN i.fix_time IS NOT NULL 
        THEN TIMESTAMPDIFF(HOUR, i.upload_time, i.fix_time) END) AS avg_resolution_hours
FROM inspectionrecord i
LEFT JOIN user u ON i.user_id = u.user_id
LEFT JOIN department d ON u.department_id = d.id
LEFT JOIN roadsegment s ON i.segment_id = s.id
GROUP BY report_date, department_name, segment_name;

CREATE OR REPLACE VIEW v_weekly_report_summary AS
SELECT 
    YEARWEEK(i.upload_time, 1) AS report_week,
    COALESCE(d.name, '未分配部门') AS department_name,
    COUNT(i.record_id) AS total_inspections,
    SUM(CASE WHEN i.status IN ('completed', 'resolved') THEN 1 ELSE 0 END) AS completed_orders,
    AVG(CASE WHEN i.fix_time IS NOT NULL 
        THEN TIMESTAMPDIFF(HOUR, i.upload_time, i.fix_time) END) AS avg_resolution_hours
FROM inspectionrecord i
LEFT JOIN user u ON i.user_id = u.user_id
LEFT JOIN department d ON u.department_id = d.id
GROUP BY report_week, department_name;

-- 9. 创建索引优化查询性能（只添加不存在的索引）
ALTER TABLE inspectionrecord ADD INDEX IF NOT EXISTS idx_report_dept (user_id, upload_time);
ALTER TABLE inspectionrecord ADD INDEX IF NOT EXISTS idx_report_segment (segment_id, upload_time);

COMMIT;

-- 验证表创建
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'road_patrol_db' 
AND TABLE_NAME LIKE 'report%'
ORDER BY CREATE_TIME DESC;
