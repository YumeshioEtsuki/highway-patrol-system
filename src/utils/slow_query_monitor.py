"""
慢查询监控工具
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.utils import get_db_connection
from settings import settings

logger = logging.getLogger(__name__)

# 注：SlowQueryLog 和 SlowQueryStats 已在重构时移除
# 此模块仅保留用于兼容性，实际功能已禁用

# 慢查询阈值（毫秒）
SLOW_QUERY_THRESHOLD = 1000


class SlowQueryMonitor:
    """慢查询监控器"""
    
    @staticmethod
    def log_query(
        query: str,
        duration_ms: float,
        rows_examined: int = 0,
        rows_returned: int = 0,
        lock_time_ms: float = 0.0,
        user_id: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> bool:
        """
        记录查询（如果超过阈值）
        
        Args:
            query: SQL 语句
            duration_ms: 执行耗时（毫秒）
            rows_examined: 扫描行数
            rows_returned: 返回行数
            lock_time_ms: 锁定时间
            user_id: 用户 ID
            endpoint: API 端点
            
        Returns:
            是否记录了慢查询
        """
        if duration_ms <= SLOW_QUERY_THRESHOLD:
            return False
        
        try:
            # 计算查询哈希值
            query_hash = hashlib.md5(query.encode()).hexdigest()
            
            # 插入数据库
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO slow_query_logs 
            (query_hash, query, duration_ms, rows_examined, rows_returned, 
             lock_time_ms, timestamp, user_id, endpoint)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)
            """
            
            cursor.execute(sql, (
                query_hash,
                query[:65535],  # MySQL TEXT 字段限制
                duration_ms,
                rows_examined,
                rows_returned,
                lock_time_ms,
                user_id,
                endpoint
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.warning(f"Slow query detected: {duration_ms}ms - {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log slow query: {e}")
            return False
    
    @staticmethod
    def get_recent_slow_queries(
        limit: int = 50,
        offset: int = 0,
        order_by: str = "duration_ms"
    ) -> List[Dict]:
        """获取最近的慢查询"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 验证 order_by 参数（防止 SQL 注入）
            allowed_fields = ["duration_ms", "timestamp", "rows_examined"]
            order_field = "duration_ms" if order_by not in allowed_fields else order_by
            
            sql = f"""
            SELECT id, query, duration_ms, rows_examined, rows_returned,
                   timestamp, user_id, endpoint
            FROM slow_query_logs
            ORDER BY {order_field} DESC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(sql, (limit, offset))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []
    
    @staticmethod
    def get_slow_query_stats() -> Optional[Dict]:
        """获取慢查询统计"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取统计数据
            sql = """
            SELECT 
                COUNT(*) as total,
                AVG(duration_ms) as avg_duration,
                MAX(duration_ms) as max_duration,
                MIN(duration_ms) as min_duration,
                SUM(rows_examined) as total_rows_examined,
                COUNT(DISTINCT endpoint) as unique_endpoints
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """
            
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                stats = {
                    "total": result[0] or 0,
                    "avg_duration": float(result[1] or 0),
                    "max_duration": float(result[2] or 0),
                    "min_duration": float(result[3] or 0),
                    "total_rows_examined": result[4] or 0,
                    "unique_endpoints": result[5] or 0,
                    "queries_per_minute": (result[0] or 0) / 1440  # 24 小时
                }
            else:
                stats = None
            
            cursor.close()
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get slow query stats: {e}")
            return None
    
    @staticmethod
    def get_slow_query_trends(hours: int = 24) -> Dict:
        """获取慢查询趋势数据"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
                COUNT(*) as count,
                AVG(duration_ms) as avg_duration
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL %s HOUR)
            GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00')
            ORDER BY hour ASC
            """
            
            cursor.execute(sql, (hours,))
            results = cursor.fetchall()
            
            trends = {
                "timestamps": [],
                "counts": [],
                "avg_durations": []
            }
            
            for row in results:
                trends["timestamps"].append(row[0])
                trends["counts"].append(row[1])
                trends["avg_durations"].append(float(row[2] or 0))
            
            cursor.close()
            conn.close()
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get slow query trends: {e}")
            return {"timestamps": [], "counts": [], "avg_durations": []}
    
    @staticmethod
    def get_top_slow_queries(limit: int = 10) -> List[Dict]:
        """获取最耗时的查询"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                query,
                COUNT(*) as execution_count,
                AVG(duration_ms) as avg_duration,
                MAX(duration_ms) as max_duration,
                SUM(duration_ms) as total_duration
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY query
            ORDER BY total_duration DESC
            LIMIT %s
            """
            
            cursor.execute(sql, (limit,))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get top slow queries: {e}")
            return []
    
    @staticmethod
    def delete_slow_query_logs(days_before: int = 30) -> int:
        """删除旧的慢查询日志"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            DELETE FROM slow_query_logs
            WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            cursor.execute(sql, (days_before,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Deleted {deleted_count} old slow query logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete slow query logs: {e}")
            return 0
