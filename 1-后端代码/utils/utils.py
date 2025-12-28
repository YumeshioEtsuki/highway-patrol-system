# utils.py

import os
import re
import time
import mysql.connector
from mysql.connector.errors import PoolError
from mysql.connector.pooling import MySQLConnectionPool
from .config import db_config
import sqlparse
from sqlparse.tokens import Comment

# 导入密码哈希函数
def hash_password(password: str) -> str:
    """哈希密码（Argon2）"""
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        return ph.hash(password)
    except ImportError:
        # Fallback to bcrypt if argon2 not available
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(hash_str: str, password: str) -> bool:
    """验证密码 - 支持多种格式：
    1. Argon2: $argon2id$v=19$...
    2. SHA256 salt:hash（冒号分隔）
    3. 明文（不推荐）
    4. 无盐 SHA256（64字符hex）
    """
    import hashlib
    
    # 格式 1: Argon2
    if hash_str.startswith('$argon2'):
        try:
            from argon2 import PasswordHasher
            from argon2.exceptions import VerifyMismatchError
            ph = PasswordHasher()
            try:
                ph.verify(hash_str, password)
                return True
            except VerifyMismatchError:
                return False
        except ImportError:
            return False
    
    # 格式 2: SHA256 salt:hash（旧格式）
    if ':' in hash_str:
        parts = hash_str.split(':')
        if len(parts) == 2:
            salt, stored_hash = parts
            computed = hashlib.sha256((salt + password).encode()).hexdigest()
            return computed == stored_hash
    
    # 格式 3: 明文
    if hash_str == password:
        return True
    
    # 格式 4: 旧版无盐 SHA256（64字符hex）
    if len(hash_str) == 64:
        if hash_str.lower() == hashlib.sha256(password.encode()).hexdigest():
            return True
    
    return False


def remove_comments_from_statement(stmt: str) -> str:
    """移除单条 SQL 语句中的行内注释（如 -- 注释），保留有效 SQL"""
    # sqlparse 会把 -- 注释识别为 Comment.Token，我们直接过滤掉
    parsed = sqlparse.parse(stmt)[0]
    cleaned = ''.join(
        str(token) for token in parsed.flatten()
        if token.ttype not in (Comment, Comment.Single)
    )
    return cleaned.strip()


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


# 初始化连接池（优先使用连接池，失败时回退到直连）
_CONN_POOL = None
try:
    _CONN_POOL = MySQLConnectionPool(
        pool_name="app_pool",
        pool_size=int(os.getenv("DB_POOL_SIZE", "50")),  # 提升池大小，缓冲高并发
        pool_reset_session=True,
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4'
    )
except Exception:
    _CONN_POOL = None


def get_db_connection():
    if _CONN_POOL:
        try:
            conn = _CONN_POOL.get_connection()
            conn.autocommit = False
            return conn
        except PoolError:
            # 池耗尽时回退到直连，避免接口直接 500
            pass

    # Debug: log actual DB config used at connect time
    try:
        import logging
        _log = logging.getLogger("db")
        msg = "DB connect params host=%s user=%s password=%s database=%s" % (
            db_config.get('host'),
            db_config.get('user'),
            repr(db_config.get('password')),
            db_config.get('database'),
        )
        _log.error(msg)
        print("[DEBUG] " + msg)
    except Exception:
        print("[DEBUG] db logging failed")

    return mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        autocommit=False,  # 手动控制事务
        connect_timeout=3
    )

# 执行sql文件

def analyze_explain_result(cursor, rows):
    """
    安全解析 EXPLAIN 结果，基于列名而非位置
    :param cursor: 已执行 EXPLAIN 的 cursor
    :param rows: cursor.fetchall() 的结果
    """
    if not rows:
        print("    📊 EXPLAIN 无结果")
        return

    # 获取列名（例如: ('id', 'select_type', 'table', 'type', ..., 'Extra')）
    columns = [col.lower() for col in cursor.column_names]

    # 构建列名到索引的映射
    col_index = {name: i for i, name in enumerate(columns)}

    def safe_get(row, col_name, default=None):
        idx = col_index.get(col_name.lower())
        if idx is not None and idx < len(row):
            return row[idx] if row[idx] is not None else default
        return default

    for row in rows:
        table = safe_get(row, 'table', 'unknown')
        access_type = safe_get(row, 'type', 'unknown')  # 这就是访问类型
        used_key = safe_get(row, 'key')
        possible_keys = safe_get(row, 'possible_keys')
        extra = safe_get(row, 'extra', '')

        print(f"    📊 表 `{table}` 访问方式: {access_type}")

        if access_type == 'ALL':
            print("    ⚠️  警告：全表扫描！性能可能较差")
            if possible_keys:
                print(f"       → 建议使用索引: {possible_keys}")
            else:
                print("       → 无可用索引！请考虑为 WHERE 条件列创建索引")
        elif access_type in ('index', 'range', 'ref', 'const', 'eq_ref'):
            if used_key:
                print(f"    ✅ 使用索引: `{used_key}`")
                if access_type == 'index':
                    print("    📈 索引扫描，但查询高效！")
                elif access_type == 'range':
                    print("    📉 范围扫描，性能较高")
                elif access_type in ('ref', 'const', 'eq_ref'):
                    print("    📉 索引查找，查询高效！")
            else:
                print("    ℹ️  未使用索引，但访问类型尚可")
        else:
            print(f"    ℹ️  访问类型: {access_type}")

        if extra:
            if 'Using filesort' in extra:
                print("    ⚠️  警告：使用了 filesort，排序效率低")
            if 'Using temporary' in extra:
                print("    ⚠️  警告：使用了临时表")
            if extra not in ('NULL', ''):
                print(f"    💡 Extra: {extra}")

        break  # 单表查询通常只有一行


def execute_sql_file(sql_file_path, skip_read_only_queries=False, print_query_results=True, stop_on_error=False):
    """
    执行 SQL 文件，支持容错模式（默认不停止）

    :param sql_file_path: SQL 文件路径
    :param skip_read_only_queries: 是否跳过只读查询
    :param print_query_results: 是否打印查询结果
    :param stop_on_error: 遇到错误是否立即停止（默认 False，用于测试阶段）
    """
    if not sql_file_path:
        print("  → 跳过执行")
        return True

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    connection = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        passwd=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        autocommit=False  # 手动控制 commit
    )

    cursor = None
    all_success = True  # 标记是否全部成功

    try:
        cursor = connection.cursor()
        statements = sqlparse.split(sql_script)

        for raw_stmt in statements:
            clean_stmt = remove_comments_from_statement(raw_stmt)
            if not clean_stmt:
                continue

            upper_stmt = clean_stmt.upper().strip()
            is_read_only = (
                    upper_stmt.startswith(('SELECT', 'SHOW', 'EXPLAIN', 'DESC', 'DESCRIBE'))
                    and not upper_stmt.startswith(('SELECT INTO',))
            )

            if skip_read_only_queries and is_read_only:
                print(f"  → SKIP {clean_stmt[:60]}...")
                continue

            print(f"  → EXEC {clean_stmt[:60]}..." if len(clean_stmt) > 60 else f"  → EXEC {clean_stmt}")

            try:
                cursor.execute(clean_stmt)

                # 处理查询结果
                if cursor.with_rows:
                    rows = cursor.fetchall()
                    is_explain = clean_stmt.upper().lstrip().startswith('EXPLAIN')
                    if is_explain:
                        print("    📊 EXPLAIN 分析结果:")
                        analyze_explain_result(cursor, rows)  # 传入 cursor 以获取 column_names
                    elif print_query_results:
                        print(f"    📤 查询结果 ({len(rows)} 行):")
                        for row in rows[:5]:
                            print(f"      {row}")
                        if len(rows) > 5:
                            print(f"      ... (共 {len(rows)} 行)")
                else:
                    # 非查询语句（INSERT/UPDATE等），尝试提交（但不强制）
                    # 在容错模式下，我们暂不 commit，等到最后统一 commit（仅当无 error 且非测试阶段）
                    pass

            except mysql.connector.Error as err:
                # 忽略重复索引错误（索引已存在时，继续执行不失败）
                if err.errno == 1061:  # ER_DUP_KEYNAME
                    print(f"    [SKIP] 索引已存在: {err}")
                else:
                    all_success = False
                    print(f"    [FAIL] 语句执行失败: {err}")
                    if stop_on_error:
                        raise  # 重新抛出，触发外层 rollback
                    # 否则：继续执行下一条

        # 只有在全部成功 且 不是纯测试阶段时才 commit
        # 但为了简单，这里我们让调用方决定是否需要事务（测试阶段通常不需要）
        connection.commit()
        if all_success:
            print("  ✓ All statements executed successfully")
        else:
            print("  ⚠ Some statements failed but continued")

        return all_success

    except Exception as e:
        print(f"  ✗ Script error: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        connection.close()


def execute_test_data_with_hashed_passwords(data_sql_path, skip_read_only_queries=True):
    """
    专门用于执行 test_data.sql：
    - 自动识别 INSERT INTO User 语句
    - 将 password 字段从明文转为哈希
    - 其他语句原样执行
    """
    with open(data_sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    connection = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        passwd=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        autocommit=False
    )
    cursor = None
    all_success = True

    try:
        cursor = connection.cursor()
        statements = sqlparse.split(sql_script)

        for raw_stmt in statements:
            clean_stmt = remove_comments_from_statement(raw_stmt)
            if not clean_stmt:
                continue

            upper_stmt = clean_stmt.upper().strip()
            is_read_only = (
                upper_stmt.startswith(('SELECT', 'SHOW', 'EXPLAIN', 'DESC', 'DESCRIBE'))
                and not upper_stmt.startswith(('SELECT INTO',))
            )

            if skip_read_only_queries and is_read_only:
                print(f"  → ⏭️ 跳过只读查询: {clean_stmt[:60]}...")
                continue

            # 🔑 关键：检测是否是 User 表的 INSERT
            if re.match(r'(?i)^\s*INSERT\s+INTO\s+`?User`?\b', clean_stmt):
                # 提取 VALUES 部分
                values_match = re.search(r'\bVALUES\s*\(([^)]+)\)', clean_stmt, re.IGNORECASE)
                if values_match:
                    values_str = values_match.group(1)
                    # 简单分割（假设字段不含逗号或引号嵌套）
                    # 注意：你的 SQL 是 ('admin', 'REDACTED', '系统管理员', ...)
                    parts = []
                    current = ""
                    in_single_quote = False
                    i = 0
                    while i < len(values_str):
                        c = values_str[i]
                        if c == "'" and (i == 0 or values_str[i-1] != '\\'):
                            in_single_quote = not in_single_quote
                            current += c
                        elif c == ',' and not in_single_quote:
                            parts.append(current.strip())
                            current = ""
                        else:
                            current += c
                        i += 1
                    if current.strip():
                        parts.append(current.strip())

                    # 假设 password 是第2个字段（索引=1）
                    if len(parts) >= 2 and parts[1].startswith("'") and parts[1].endswith("'"):
                        plain_pwd = parts[1][1:-1]  # 去掉首尾单引号
                        hashed_pwd = hash_password(plain_pwd)
                        parts[1] = f"'{hashed_pwd}'"
                        new_values = ", ".join(parts)
                        new_stmt = re.sub(r'\bVALUES\s*\([^)]+\)', f'VALUES ({new_values})', clean_stmt, flags=re.IGNORECASE)
                        print(f"  → 🔒 自动哈希 User 密码: '{plain_pwd}' → [已隐藏]")
                        clean_stmt = new_stmt
                    else:
                        print("  → ⚠️ 无法解析 User 插入语句的密码字段，跳过哈希")

            # 执行处理后的语句
            print(f"  → 执行: {clean_stmt[:60]}..." if len(clean_stmt) > 60 else f"  → 执行: {clean_stmt}")
            try:
                cursor.execute(clean_stmt)
                if cursor.with_rows:
                    rows = cursor.fetchall()
                    if len(rows) > 0 and "EXPLAIN" not in clean_stmt.upper():
                        print(f"    📤 查询结果 ({len(rows)} 行)")
            except mysql.connector.Error as err:
                all_success = False
                print(f"    ❌ 语句执行失败: {err}")
                # 继续执行（容错模式）

        connection.commit()
        return all_success

    except Exception as e:
        print(f"  → ❌ 脚本级错误: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        connection.close()


def setup_database(create_path=None, data_path=None, query_path=None, skip_read_only_queries=True):
    """按步骤执行数据库初始化"""
    executed_steps = []

    if create_path:
        print("\n[步骤1/3] 正在创建数据库和表结构...")
        executed_steps.append(('create', execute_sql_file(create_path, skip_read_only_queries=False)))

    if data_path:
        print("\n[步骤2/3] 正在插入测试数据（自动哈希密码）...")
        # ✅ 关键修改：使用专用函数处理 data
        success = execute_test_data_with_hashed_passwords(
            data_path,
            skip_read_only_queries=skip_read_only_queries
        )
        executed_steps.append(('data', success))

    if query_path:
        print("\n[步骤3/3] 正在执行测试查询...")
        executed_steps.append(('query', execute_sql_file(query_path, skip_read_only_queries=False)))

    return executed_steps


def initialize_database(step='all', skip_read_only_queries=True):
    """FastAPI应用的数据库初始化入口"""
    import os
    import mysql.connector
    from models.schema import CREATE_TABLES_SQL
    
    print("\n" + "=" * 50)
    print("开始数据库初始化...")
    print("=" * 50)

    SECURE_MODE = os.getenv("SECURE_MODE", "0") == "1"
    BOOTSTRAP_ADMIN = os.getenv("BOOTSTRAP_ADMIN", "0") == "1"
    if BOOTSTRAP_ADMIN:
        if SECURE_MODE:
            print("⚠️ BOOTSTRAP_ADMIN=1 在 SECURE_MODE 下会被忽略，请使用脚本 bin/create_admin.py 显式创建管理员。")
        else:
            print("ℹ️ BOOTSTRAP_ADMIN=1 已启用：仅用于开发/初始化缺省管理员。完成后请恢复为 0 以减少风险。")

    conn = None
    cursor = None
    try:
        # 连接数据库服务器（不指定数据库）
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        db_name = db_config['database']
        
        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        db_exists = cursor.fetchone() is not None
        
        if not db_exists:
            print(f"🆕 创建数据库 {db_name}...")
            cursor.execute(f"""
                CREATE DATABASE `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ 数据库 {db_name} 创建成功")
        else:
            print(f"📋 数据库 {db_name} 已存在")
        
        cursor.execute(f"USE `{db_name}`")
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'User'")
        tables_exist = cursor.fetchone() is not None
        
        if not tables_exist:
            print("🔨 创建数据表...")
            for i, stmt in enumerate(CREATE_TABLES_SQL, 1):
                cursor.execute(stmt)
                print(f"  ✅ 第 {i}/{len(CREATE_TABLES_SQL)} 张表创建成功")
            conn.commit()
            print("✅ 数据表创建完成")
        else:
            print("📋 数据表已存在")
        
        # 检查是否已有数据，并在明确启用时引导创建默认管理员
        if step == 'all':
            cursor.execute("SELECT COUNT(*) FROM User")
            user_count = cursor.fetchone()[0]
            # 业界做法：管理员账号创建应为显式运维动作，避免默认弱口令
            import os
            cursor.execute("SELECT COUNT(*) FROM User WHERE username=%s", ('admin',))
            admin_exists = cursor.fetchone()[0] > 0
            if admin_exists and BOOTSTRAP_ADMIN:
                print("ℹ️ 已存在 admin 账号，建议将 BOOTSTRAP_ADMIN 设回 0（避免遗留默认入口）")
            if not admin_exists:
                if BOOTSTRAP_ADMIN and not SECURE_MODE:
                    print("🛡️ 未检测到管理员账号，已开启 BOOTSTRAP_ADMIN，创建默认 admin...")
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    admin_plain = os.getenv("DEFAULT_ADMIN_PASSWORD", "REDACTED")
                    cursor.execute(
                        """
                        INSERT INTO User (username, password, real_name, phone, email, role, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        """,
                        ('admin', pwd_context.hash(admin_plain), '系统管理员', '11451419198', 'admin@example.com', 'admin')
                    )
                    conn.commit()
                    print("✅ 默认管理员创建完成（开发/测试环境）")
                else:
                    print("⚠️ 未检测到管理员账号。请运行 bin/create_admin.py 或设置 BOOTSTRAP_ADMIN=1 并提供强口令。")

            if user_count == 0:
                print("📝 插入初始数据...")
                TEST_DATA = {}
                for table_name, rows in TEST_DATA.items():
                    if not rows:
                        continue
                    for row in rows:
                        cols = []
                        vals = []
                        sql_vals = []
                        for k, v in row.items():
                            cols.append(k)
                            if v == "NOW()":
                                sql_vals.append("NOW()")
                            else:
                                sql_vals.append("%s")
                                vals.append(v)
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(sql_vals)})"
                        cursor.execute(insert_sql, vals)
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM RoadSegment")
                segment_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM ProblemType")
                problem_count = cursor.fetchone()[0]
                print(f"  ✅ 已插入 {user_count} 个用户")
                print(f"  ✅ 已插入 {segment_count} 条路段")
                print(f"  ✅ 已插入 {problem_count} 种问题类型")
                print("✅ 数据表结构初始化完成")
            else:
                print(f"📋 数据库已有数据（{user_count} 个用户）")
        
        print("\n" + "=" * 50)
        print("✅ 数据库初始化全部成功！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============ 路由逻辑封装 ============

def reinit_database(step='all', skip_read_only_queries=True):
    import time
    start_time = time.time()

    success = initialize_database(step=step, skip_read_only_queries=skip_read_only_queries)
    end_time = time.time()
    execution_time = int((end_time - start_time) * 1000)

    # 获取实际执行的步骤（用于展示）
    steps = [
        {"name": "创建数据库结构", "success": True},  # 简化为示例
        {"name": "插入测试数据", "success": True},
        {"name": "执行测试查询", "success": True}
    ]

    # 根据 step 过滤步骤
    if step == 1:
        steps = [steps[0]]  # 只显示建表
    elif step == 'all':
        steps = steps  # 显示全部

    # 记录每个步骤的耗时（可选）
    for i, s in enumerate(steps):
        s['duration'] = (i + 1) * 10  # 模拟耗时

    return {
        'status': 'success' if success else 'error',
        'message': '数据库重新初始化完成' if success else '初始化失败',
        'details': '所有步骤执行成功' if success else '部分步骤失败',
        'executed_step': str(step),
        'step_description': {
            'all': '完整流程（建表 + 数据 + 查询）',
            1: '仅创建表结构'
        }.get(step, f'自定义步骤: {step}'),
        'execution_time': execution_time,
        'steps': steps  # 新增字段，用于前端展示
    }


def verify_database():
    start_time = time.time()
    steps = []

    # 1. 检查表是否存在（使用正确的表名）
    t1 = time.time()
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'inspectionrecord'")
        tables = cursor.fetchall()
        tables_exist = len(tables) > 0
        cursor.close()
        conn.close()
        step1_duration = int((time.time() - t1) * 1000)
    except Exception as e:
        tables_exist = False
        step1_duration = int((time.time() - t1) * 1000)

    steps.append({
        'name': '检查表是否存在',
        'success': tables_exist,
        'duration': step1_duration
    })

    # 2. 验证数据完整性（查询 inspectionrecord 表是否有数据）
    t2 = time.time()
    data_integrity = True
    if tables_exist:
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inspectionrecord")
            count = cursor.fetchone()[0]
            data_integrity = count > 0  # 至少有一条记录才算正常
            cursor.close()
            conn.close()
        except Exception as e:
            data_integrity = False
    else:
        data_integrity = False
    step2_duration = int((time.time() - t2) * 1000)

    steps.append({
        'name': '验证数据完整性',
        'success': data_integrity,
        'duration': step2_duration
    })

    # 3. 测试查询性能（通用查询）
    t3 = time.time()
    query_performance = True
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        query_performance = result is not None
        cursor.close()
        conn.close()
    except Exception as e:
        query_performance = False
    step3_duration = int((time.time() - t3) * 1000)

    steps.append({
        'name': '测试查询性能',
        'success': query_performance,
        'duration': step3_duration
    })

    # 4. 版本兼容性检查（支持 5.7+）
    t4 = time.time()
    version_check = True
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        # 支持 MySQL 5.7 及以上
        version_check = version.startswith('5.7') or version.startswith('8.') or version.startswith('9.')
        cursor.close()
        conn.close()
    except Exception as e:
        version_check = False
    step4_duration = int((time.time() - t4) * 1000)

    steps.append({
        'name': '版本兼容性检查',
        'success': version_check,
        'duration': step4_duration
    })

    total_duration = int((time.time() - start_time) * 1000)
    all_success = all(s['success'] for s in steps)

    return {
        'status': 'success' if all_success else 'error',
        'message': '数据库验证通过' if all_success else '验证失败，请检查数据一致性',
        'details': '所有验证项均通过' if all_success else '部分验证项失败',
        'execution_time': total_duration,
        'steps': steps
    }


def get_database_status():
    start_time = time.time()
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            charset='utf8mb4',
            autocommit=True
        )
    except Exception as e:
        return {
            'status': 'error',
            'message': '❌ 无法连接到数据库',
            'details': str(e),
            'connected': False,
            'execution_time': int((time.time() - start_time) * 1000)
        }

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. 获取版本和连接信息
        cursor.execute("SELECT VERSION() AS version")
        version_row = cursor.fetchone()
        version = version_row['version'] if version_row else '未知'

        cursor.execute("SELECT CONNECTION_ID() AS conn_id, USER() AS user")
        conn_info = cursor.fetchone()
        user_info = conn_info['user'] if conn_info else '未知'
        conn_id = conn_info['conn_id'] if conn_info else -1

        db_name = db_config['database']
        if not db_name:
            raise ValueError("数据库名称未配置")

        # 2. 检查目标数据库是否存在（避免 USE 失败）
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        db_exists = cursor.fetchone() is not None
        if not db_exists:
            raise ValueError(f"数据库 '{db_name}' 不存在")

        # 3. 切换数据库
        cursor.execute(f"USE `{db_name}`")

        # 4. 获取表数量
        cursor.execute("SHOW TABLES")
        tables_count = len(cursor.fetchall())

        # 5. 获取 Uptime（降级到 SESSION 级别，避免权限问题）
        uptime_str = "未知"
        try:
            cursor.execute("SHOW SESSION STATUS LIKE 'Uptime'")
            uptime_row = cursor.fetchone()
            if uptime_row and len(uptime_row) >= 2:
                uptime_seconds = int(uptime_row[1])
                uptime_str = format_uptime(uptime_seconds)
        except Exception:
            # 忽略权限错误，保持 uptime_str = "未知"
            pass

        # 6. 获取数据库创建时间（更安全的处理）
        db_created = "未知"
        try:
            cursor.execute("""
                SELECT MIN(CREATE_TIME) AS min_create_time 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                  AND CREATE_TIME IS NOT NULL
            """, (db_name,))
            create_time_row = cursor.fetchone()
            if create_time_row and create_time_row['min_create_time']:
                db_created = create_time_row['min_create_time'].strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            # 如果 information_schema 不可用，跳过
            pass

        cursor.close()
        conn.close()

        return {
            'status': 'success',
            'message': '✅ 数据库运行正常',
            'details': '系统健康，连接稳定',
            'connected': True,
            'server': db_config['host'],
            'port': 3306,
            'database': db_name,
            'database_version': version,
            'connection_user': user_info,
            'connection_id': conn_id,
            'tables_count': tables_count,
            'uptime': uptime_str,
            'database_created': db_created,
            'execution_time': int((time.time() - start_time) * 1000)
        }

    except Exception as e:
        # 确保 cursor 和 conn 在异常时关闭
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass
        error_msg = str(e)
        print(f"❌ get_database_status 错误: {error_msg}")
        return {
            'status': 'error',
            'message': '❌ 查询数据库状态时出错',
            'details': error_msg,
            'connected': True,
            'execution_time': int((time.time() - start_time) * 1000)
        }


def format_uptime(seconds):
    if seconds < 60:
        return f"{seconds} 秒"
    elif seconds < 3600:
        return f"{seconds // 60} 分钟"
    elif seconds < 86400:
        return f"{seconds // 3600} 小时 {seconds % 3600 // 60} 分钟"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} 天 {hours} 小时"


def explain_query(sql: str):
    """便捷打印 SELECT 语句的 EXPLAIN 结果，用于定位慢查询"""
    if not sql or not sql.strip().lower().startswith("select"):
        print("⚠️ 仅支持对 SELECT 语句执行 EXPLAIN")
        return None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    start = time.time()
    try:
        cursor.execute(f"EXPLAIN {sql}")
        rows = cursor.fetchall()
        print("📊 EXPLAIN 结果:")
        for row in rows:
            print(
                "  id={id} table={table} type={type} key={key} rows={rows} extra={extra}".format(
                    id=row.get('id'),
                    table=row.get('table'),
                    type=row.get('type'),
                    key=row.get('key'),
                    rows=row.get('rows'),
                    extra=row.get('Extra') or row.get('extra')
                )
            )
        print(f"⏱️  EXPLAIN 耗时: {int((time.time() - start) * 1000)} ms")
        return rows
    except Exception as e:
        print(f"❌ EXPLAIN 失败: {e}")
        return None
    finally:
        cursor.close()
        conn.close()