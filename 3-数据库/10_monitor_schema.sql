-- =====================================================
-- 数据库监控系统表结构
-- =====================================================

-- 慢查询日志表
CREATE TABLE IF NOT EXISTS slow_query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE,
    query LONGTEXT NOT NULL,
    duration_ms FLOAT NOT NULL,
    rows_examined INT DEFAULT 0,
    rows_returned INT DEFAULT 0,
    lock_time_ms FLOAT DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    endpoint VARCHAR(255),
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_duration (duration_ms),
    INDEX idx_query_hash (query_hash),
    INDEX idx_endpoint (endpoint),
    
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 性能指标表（时序数据）
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    queries_per_sec FLOAT,
    slow_queries_per_min INT,
    active_connections INT,
    avg_query_time_ms FLOAT,
    cache_hit_ratio FLOAT,
    lock_wait_time_ms FLOAT DEFAULT 0,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io_reads INT,
    disk_io_writes INT,
    
    INDEX idx_timestamp (timestamp),
    INDEX idx_queries_per_sec (queries_per_sec),
    INDEX idx_cache_hit_ratio (cache_hit_ratio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 优化建议表
CREATE TABLE IF NOT EXISTS optimization_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,  -- 'index', 'query', 'cache', 'connection', 'partition'
    priority VARCHAR(20),  -- 'HIGH', 'MEDIUM', 'LOW'
    description TEXT NOT NULL,
    suggested_action TEXT,
    estimated_improvement FLOAT,
    affected_table VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'applied', 'dismissed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    applied_by INT,
    
    INDEX idx_status (status),
    INDEX idx_type (type),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at),
    
    FOREIGN KEY (applied_by) REFERENCES user(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 索引分析结果表
CREATE TABLE IF NOT EXISTS index_analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    index_name VARCHAR(255),
    analysis_type VARCHAR(50),  -- 'missing', 'unused', 'redundant'
    status VARCHAR(50),  -- 'active', 'unused', 'potential'
    rows_affected INT,
    estimated_benefit FLOAT,
    last_analyzed DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_table_name (table_name),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_last_analyzed (last_analyzed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 查询分析缓存（存储 EXPLAIN 结果）
CREATE TABLE IF NOT EXISTS query_analysis_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE,
    explain_output JSON,
    analysis_result JSON,
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    
    INDEX idx_query_hash (query_hash),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 告警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    operator VARCHAR(10),  -- '>', '<', '=', '>=', '<='
    threshold FLOAT NOT NULL,
    severity VARCHAR(20),  -- 'warning', 'critical'
    enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    
    INDEX idx_metric_name (metric_name),
    INDEX idx_enabled (enabled),
    
    FOREIGN KEY (created_by) REFERENCES user(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 告警历史表
CREATE TABLE IF NOT EXISTS alert_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id INT NOT NULL,
    metric_name VARCHAR(100),
    current_value FLOAT,
    threshold FLOAT,
    severity VARCHAR(20),
    message TEXT,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    
    INDEX idx_rule_id (rule_id),
    INDEX idx_triggered_at (triggered_at),
    INDEX idx_resolved_at (resolved_at),
    
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 创建视图用于数据聚合
-- =====================================================

-- 慢查询汇总视图
CREATE OR REPLACE VIEW vw_slow_query_summary AS
SELECT 
    MD5(query) AS query_hash,
    query,
    COUNT(*) AS execution_count,
    AVG(duration_ms) AS avg_duration,
    SUM(duration_ms) AS total_duration,
    MAX(duration_ms) AS max_duration,
    MIN(duration_ms) AS min_duration,
    MIN(timestamp) AS first_seen,
    MAX(timestamp) AS last_seen,
    (SELECT endpoint FROM slow_query_logs sl2 
     WHERE MD5(sl2.query) = MD5(query) 
     GROUP BY endpoint ORDER BY COUNT(*) DESC LIMIT 1) AS most_common_endpoint
FROM slow_query_logs
GROUP BY query;

-- 性能指标最新视图
CREATE OR REPLACE VIEW vw_latest_metrics AS
SELECT 
    *
FROM performance_metrics
WHERE timestamp = (SELECT MAX(timestamp) FROM performance_metrics);

-- 活跃告警视图
CREATE OR REPLACE VIEW vw_active_alerts AS
SELECT 
    ah.*
FROM alert_history ah
WHERE ah.resolved_at IS NULL
ORDER BY ah.triggered_at DESC;

-- =====================================================
-- 创建存储过程
-- =====================================================

-- 清理旧的慢查询日志（保留 30 天）
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS cleanup_old_slow_queries()
BEGIN
    DELETE FROM slow_query_logs
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);
END//
DELIMITER ;

-- 清理旧的性能指标（保留 90 天）
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS cleanup_old_metrics()
BEGIN
    DELETE FROM performance_metrics
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
END//
DELIMITER ;

-- 创建定时事件（每天执行清理）
CREATE EVENT IF NOT EXISTS evt_daily_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    CALL cleanup_old_slow_queries();
    CALL cleanup_old_metrics();
END;

-- =====================================================
-- 初始化默认告警规则
-- =====================================================

INSERT IGNORE INTO alert_rules (metric_name, operator, threshold, severity) VALUES
('slow_queries_per_min', '>', 20, 'critical'),
('slow_queries_per_min', '>', 10, 'warning'),
('cache_hit_ratio', '<', 0.5, 'warning'),
('cache_hit_ratio', '<', 0.3, 'critical'),
('avg_query_time_ms', '>', 200, 'warning'),
('avg_query_time_ms', '>', 500, 'critical'),
('active_connections', '>', 100, 'warning'),
('active_connections', '>', 200, 'critical');

-- =====================================================
-- 执行初始化（可选）
-- =====================================================

-- 添加默认缓存命中率告警规则
INSERT IGNORE INTO alert_rules (metric_name, operator, threshold, severity, created_at) VALUES
('lock_wait_time_ms', '>', 100, 'warning', NOW());
