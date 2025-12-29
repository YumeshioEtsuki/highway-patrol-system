# models/schema.py

# 数据库建表语句（按外键依赖顺序排列，都使用 IF NOT EXISTS 避免重复创建错误）
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS Department (
        department_id INT PRIMARY KEY AUTO_INCREMENT,
        department_name VARCHAR(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';
    """,
    """
    CREATE TABLE IF NOT EXISTS RoadSegment (
        segment_id INT PRIMARY KEY AUTO_INCREMENT,
        segment_name VARCHAR(100) NOT NULL,
        start_number INT NOT NULL,
        end_number INT NOT NULL,
        department_id INT,
        region VARCHAR(20) DEFAULT '华东' COMMENT '所属地区：华北/华东/华中/华南/西北/西南/东北',
        FOREIGN KEY (department_id) REFERENCES Department(department_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路段信息表';
    """,
    """
    CREATE TABLE IF NOT EXISTS User (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        real_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20) UNIQUE,
        email VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME,
        role ENUM('inspector', 'admin') NOT NULL,
        department_id INT,
        FOREIGN KEY (department_id) REFERENCES Department(department_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
    """,
    """
    CREATE TABLE IF NOT EXISTS ProblemType (
        type_id INT PRIMARY KEY AUTO_INCREMENT,
        type_name VARCHAR(50) NOT NULL,
        parent_id INT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问题类型表';
    """,
    """
    CREATE TABLE IF NOT EXISTS InspectionRecord (
        record_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        upload_time DATETIME NOT NULL,
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        segment_id INT,
        problem_type_id INT,
        description TEXT,
        severity TINYINT,
        status ENUM('pending', 'processing', 'completed', 'resolved') DEFAULT 'pending',
        data_type ENUM('real','test') DEFAULT 'real' COMMENT '数据类型：real=真实数据，test=测试数据',
        admin_process_time DATETIME,
        fix_time DATETIME,
        process_note TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (segment_id) REFERENCES RoadSegment(segment_id),
        FOREIGN KEY (problem_type_id) REFERENCES ProblemType(type_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巡查记录表';
    """,
    """
    CREATE TABLE IF NOT EXISTS Photo (
        photo_id INT PRIMARY KEY AUTO_INCREMENT,
        record_id INT NOT NULL,
        photo_type ENUM('test_pictures', 'after_fix') NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        file_name VARCHAR(100),
        file_size INT,
        upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_watermarked BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (record_id) REFERENCES InspectionRecord(record_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='照片表';
    """,
    """
    CREATE TABLE IF NOT EXISTS AuditLog (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT,
        username VARCHAR(50),
        action VARCHAR(100) NOT NULL COMMENT '操作类型：登录/新增/修改/删除等',
        resource VARCHAR(255) COMMENT '操作资源：记录ID/用户ID等',
        details TEXT COMMENT '操作详情JSON',
        ip_address VARCHAR(45) COMMENT '操作IP地址',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_action (action),
        INDEX idx_timestamp (timestamp)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';
    """
]

# 索引创建语句（在表创建完成后执行）
CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_data_type ON InspectionRecord(data_type);"
]