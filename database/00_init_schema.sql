-- ============================================================================
-- 公路巡查系统 数据库初始化脚本
-- ============================================================================
-- 功能：一次性创建完整数据库和所有表
-- 执行：mysql -u root -p < 00_init.sql
-- 注意：此脚本会删除旧数据库（如存在），请备份重要数据！
-- ============================================================================

-- 删除旧数据库（如果存在）
DROP DATABASE IF EXISTS road_patrol_db;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS road_patrol_db 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE road_patrol_db;

-- ============================================================================
-- 1. 部门表
-- ============================================================================
CREATE TABLE Department (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_dept_name (department_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- ============================================================================
-- 2. 路段表
-- ============================================================================
CREATE TABLE RoadSegment (
    segment_id INT PRIMARY KEY AUTO_INCREMENT,
    segment_name VARCHAR(100) NOT NULL,
    start_number INT NOT NULL,
    end_number INT NOT NULL,
    department_id INT NOT NULL,
    region VARCHAR(50) DEFAULT NULL COMMENT '所属地区：华北/华东/华中/华南/西北/西南/东北',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    INDEX idx_department (department_id),
    INDEX idx_region (region)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路段信息表';

-- ============================================================================
-- 3. 用户表
-- ============================================================================
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（Argon2加密）',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(20) UNIQUE COMMENT '联系电话',
    email VARCHAR(100) COMMENT '邮箱',
    role ENUM('inspector', 'admin') NOT NULL DEFAULT 'inspector' COMMENT '角色：inspector=检查员, admin=管理员',
    department_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME COMMENT '最后登录时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户状态',
    FOREIGN KEY (department_id) REFERENCES Department(department_id),
    INDEX idx_department (department_id),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表（认证）';

-- ============================================================================
-- 4. 问题类型表
-- ============================================================================
CREATE TABLE ProblemType (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    parent_id INT COMMENT '父类型ID（用于分层）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_parent (parent_id),
    INDEX idx_name (type_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问题类型表（分类）';

-- ============================================================================
-- 5. 巡查记录表
-- ============================================================================
CREATE TABLE InspectionRecord (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    segment_id INT NOT NULL,
    problem_type_id INT,
    description TEXT COMMENT '问题描述',
    severity TINYINT COMMENT '严重程度（1-5）',
    status ENUM('pending', 'processing', 'completed', 'resolved') DEFAULT 'pending' COMMENT '处理状态',
    data_type ENUM('real', 'test') DEFAULT 'real' COMMENT '数据类型：real=真实, test=测试',
    region VARCHAR(50) COMMENT '所属地区（冗余字段，提高查询性能）',
    admin_process_time DATETIME COMMENT '管理员处理时间',
    fix_time DATETIME COMMENT '修复完成时间',
    process_note TEXT COMMENT '处理备注',
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (segment_id) REFERENCES RoadSegment(segment_id),
    FOREIGN KEY (problem_type_id) REFERENCES ProblemType(type_id),
    -- 核心查询索引
    INDEX idx_user_id (user_id),
    INDEX idx_upload_time (upload_time DESC),
    INDEX idx_status (status),
    INDEX idx_data_type (data_type),
    INDEX idx_region (region),
    INDEX idx_segment_id (segment_id),
    INDEX idx_problem_type (problem_type_id),
    INDEX idx_status_time (status, upload_time DESC),
    INDEX idx_user_upload (user_id, upload_time DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巡查记录表';

-- ============================================================================
-- 6. 照片表
-- ============================================================================
CREATE TABLE Photo (
    photo_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    photo_type ENUM('test_pictures', 'after_fix') NOT NULL COMMENT '照片类型',
    file_path VARCHAR(255) NOT NULL COMMENT '文件路径',
    file_name VARCHAR(100) COMMENT '文件名',
    file_size INT COMMENT '文件大小（字节）',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_watermarked BOOLEAN DEFAULT TRUE COMMENT '是否加水印',
    FOREIGN KEY (record_id) REFERENCES InspectionRecord(record_id),
    INDEX idx_record_id (record_id),
    INDEX idx_upload_time (upload_time),
    INDEX idx_type (photo_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='照片表';

-- ============================================================================
-- 7. 审计日志表（记录管理员关键操作）
-- ============================================================================
CREATE TABLE AuditLog (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL COMMENT '操作类型（如：REVIEW, REJECT, EXPORT）',
    resource VARCHAR(100) NOT NULL COMMENT '资源类型（如：InspectionRecord）',
    resource_id INT COMMENT '资源ID',
    details TEXT COMMENT '操作详情',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_action_time (action, timestamp DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';

-- ============================================================================
-- 初始化完成
-- ============================================================================
SELECT '✅ 数据库初始化完成！' AS Status;
SELECT CONCAT('✅ 已创建 ', COUNT(*), ' 个表') FROM information_schema.TABLES 
WHERE TABLE_SCHEMA='road_patrol_db';
