"""
报表业务逻辑层
Phase 2 Stage 2
"""
import json
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from utils.utils import get_db_connection


async def create_template(name: str, type: str, config: dict, 
                         chart_config: dict, created_by: int) -> int:
    """创建报表模板"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO report_template (name, type, config, chart_config, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            name, type, 
            json.dumps(config) if config else None,
            json.dumps(chart_config) if chart_config else None,
            created_by
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


async def update_template(template_id: int, name: Optional[str] = None, config: Optional[dict] = None,
                          sql_template: Optional[str] = None, chart_config: Optional[dict] = None,
                          enabled: Optional[bool] = None) -> bool:
    """更新报表模板（仅更新提供的字段）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if config is not None:
            updates.append("config = %s")
            params.append(json.dumps(config))
        if sql_template is not None:
            updates.append("sql_template = %s")
            params.append(sql_template)
        if chart_config is not None:
            updates.append("chart_config = %s")
            params.append(json.dumps(chart_config))
        if enabled is not None:
            updates.append("enabled = %s")
            params.append(1 if enabled else 0)

        if not updates:
            return False

        updates.append("updated_at = NOW()")
        params.append(template_id)
        sql = f"UPDATE report_template SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


async def get_template(template_id: int) -> Optional[Dict]:
    """获取报表模板"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM report_template WHERE id = %s"
        cursor.execute(sql, (template_id,))
        row = cursor.fetchone()
        if row and row.get('config'):
            row['config'] = json.loads(row['config']) if isinstance(row['config'], str) else row['config']
        if row and row.get('chart_config'):
            row['chart_config'] = json.loads(row['chart_config']) if isinstance(row['chart_config'], str) else row['chart_config']
        return row
    finally:
        cursor.close()
        conn.close()


async def list_templates(type: Optional[str] = None, 
                        enabled: bool = True) -> List[Dict]:
    """列出报表模板"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conditions = ["enabled = %s"] if enabled is not None else []
        params = [1 if enabled else 0] if enabled is not None else []
        
        if type:
            conditions.append("type = %s")
            params.append(type)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM report_template WHERE {where_clause} ORDER BY created_at DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        for row in rows:
            if row.get('config'):
                row['config'] = json.loads(row['config']) if isinstance(row['config'], str) else row['config']
            if row.get('chart_config'):
                row['chart_config'] = json.loads(row['chart_config']) if isinstance(row['chart_config'], str) else row['chart_config']
        return rows
    finally:
        cursor.close()
        conn.close()


async def create_generation_record(template_id: int, generated_by: Optional[int],
                                   time_range_start: date, time_range_end: date,
                                   file_type: str) -> int:
    """创建报表生成记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO report_generation_history 
        (template_id, generated_by, time_range_start, time_range_end, file_type, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
        """
        cursor.execute(sql, (template_id, generated_by, time_range_start, time_range_end, file_type))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


async def update_generation_status(record_id: int, status: str, 
                                   file_path: Optional[str] = None,
                                   download_url: Optional[str] = None,
                                   file_size: Optional[int] = None,
                                   row_count: Optional[int] = None,
                                   error_msg: Optional[str] = None,
                                   expires_at: Optional[datetime] = None):
    """更新报表生成状态"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = ["status = %s"]
        params = [status]
        
        if file_path:
            updates.append("file_path = %s")
            params.append(file_path)
        if download_url:
            updates.append("download_url = %s")
            params.append(download_url)
        if file_size:
            updates.append("file_size = %s")
            params.append(file_size)
        if row_count is not None:
            updates.append("row_count = %s")
            params.append(row_count)
        if error_msg:
            updates.append("error_msg = %s")
            params.append(error_msg)
        if expires_at:
            updates.append("expires_at = %s")
            params.append(expires_at)
        
        params.append(record_id)
        sql = f"UPDATE report_generation_history SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


async def list_reports(template_id: Optional[int] = None, 
                      status: Optional[str] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None,
                      limit: int = 20, offset: int = 0) -> Tuple[List[Dict], int]:
    """列出报表历史"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conditions = []
        params = []
        
        if template_id:
            conditions.append("h.template_id = %s")
            params.append(template_id)
        if status:
            conditions.append("h.status = %s")
            params.append(status)
        if start_date:
            conditions.append("h.generation_time >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("h.generation_time <= %s")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Count query
        count_sql = f"SELECT COUNT(*) as total FROM report_generation_history h WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # List query with template name
        list_sql = f"""
        SELECT h.*, t.name as template_name
        FROM report_generation_history h
        LEFT JOIN report_template t ON h.template_id = t.id
        WHERE {where_clause}
        ORDER BY h.generation_time DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(list_sql, params + [limit, offset])
        rows = cursor.fetchall()
        
        return rows, total
    finally:
        cursor.close()
        conn.close()


async def create_subscription(template_id: int, subscriber_id: int,
                             frequency: str, send_time: str, send_day: Optional[str],
                             delivery_method: str, delivery_target: str) -> int:
    """创建报表订阅"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO report_subscription 
        (template_id, subscriber_id, frequency, send_time, send_day, 
         delivery_method, delivery_target)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (template_id, subscriber_id, frequency, send_time, 
                           send_day, delivery_method, delivery_target))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


async def list_user_subscriptions(user_id: int) -> List[Dict]:
    """列出用户的报表订阅"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT s.*, t.name as template_name
        FROM report_subscription s
        LEFT JOIN report_template t ON s.template_id = t.id
        WHERE s.subscriber_id = %s AND s.enabled = 1
        ORDER BY s.created_at DESC
        """
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


async def delete_subscription(subscription_id: int, user_id: int) -> bool:
    """删除订阅（只能删除自己的）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM report_subscription WHERE id = %s AND subscriber_id = %s"
        cursor.execute(sql, (subscription_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


async def get_daily_report_data(start_date: date, end_date: date, 
                                department: Optional[str] = None) -> List[Dict]:
    """获取日报数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conditions = ["report_date BETWEEN %s AND %s"]
        params = [start_date, end_date]
        
        if department:
            conditions.append("department_name = %s")
            params.append(department)
        
        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM v_daily_report_summary WHERE {where_clause}"
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


async def get_weekly_report_data(week_start: date, week_end: date) -> List[Dict]:
    """获取周报数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 计算周数范围
        start_week = week_start.isocalendar()[1]
        end_week = week_end.isocalendar()[1]
        
        sql = """
        SELECT * FROM v_weekly_report_summary 
        WHERE report_week BETWEEN %s AND %s
        """
        cursor.execute(sql, (start_week, end_week))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


async def get_report_stats() -> Dict:
    """获取报表统计"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT 
            COUNT(*) as total_generated,
            SUM(CASE WHEN generation_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as last_24h,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(file_size) as avg_file_size,
            SUM(file_size) as total_file_size
        FROM report_generation_history
        WHERE generation_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        cursor.execute(sql)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


async def get_metrics() -> List[Dict]:
    """获取所有启用的统计指标"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM report_metric WHERE enabled = 1 ORDER BY sort_order, id"
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# =====================================================
# 同步封装：供 Celery 任务使用
# =====================================================


def get_template_sync(template_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM report_template WHERE id = %s", (template_id,))
        row = cursor.fetchone()
        if row and row.get('config'):
            row['config'] = json.loads(row['config']) if isinstance(row['config'], str) else row['config']
        if row and row.get('chart_config'):
            row['chart_config'] = json.loads(row['chart_config']) if isinstance(row['chart_config'], str) else row['chart_config']
        return row
    finally:
        cursor.close()
        conn.close()


def create_generation_record_sync(template_id: int, generated_by: Optional[int],
                                  start_date: date, end_date: date, file_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO report_generation_history
            (template_id, generated_by, time_range_start, time_range_end, file_type, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            """,
            (template_id, generated_by, start_date, end_date, file_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_generation_status_sync(record_id: int, status: str,
                                  file_path: Optional[str] = None,
                                  download_url: Optional[str] = None,
                                  file_size: Optional[int] = None,
                                  row_count: Optional[int] = None,
                                  error_msg: Optional[str] = None,
                                  expires_at: Optional[datetime] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = ["status = %s"]
        params = [status]
        if file_path:
            updates.append("file_path = %s")
            params.append(file_path)
        if download_url:
            updates.append("download_url = %s")
            params.append(download_url)
        if file_size is not None:
            updates.append("file_size = %s")
            params.append(file_size)
        if row_count is not None:
            updates.append("row_count = %s")
            params.append(row_count)
        if error_msg:
            updates.append("error_msg = %s")
            params.append(error_msg)
        if expires_at:
            updates.append("expires_at = %s")
            params.append(expires_at)
        params.append(record_id)
        sql = f"UPDATE report_generation_history SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def list_due_subscriptions_sync() -> List[Dict]:
    """简单规则：按分钟匹配 send_time，enabled=1"""
    now = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT * FROM report_subscription
            WHERE enabled = 1
              AND HOUR(send_time) = %s
              AND MINUTE(send_time) = %s
            """,
            (now.hour, now.minute)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def cleanup_expired_reports_sync() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM report_generation_history WHERE expires_at IS NOT NULL AND expires_at < NOW()"
        )
        deleted = cursor.rowcount
        conn.commit()
        return deleted
    finally:
        cursor.close()
        conn.close()
