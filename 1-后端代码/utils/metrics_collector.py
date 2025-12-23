"""
性能指标收集工具
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from utils.utils import get_db_connection

logger = logging.getLogger(__name__)


class MetricsCollector:
    """性能指标收集器"""
    
    @staticmethod
    def collect_current_metrics() -> Dict:
        """收集当前的性能指标"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            metrics = {}
            
            # 1. 查询速率和慢查询数
            sql_slow = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN duration_ms > 1000 THEN 1 END) as slow_count
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
            """
            cursor.execute(sql_slow)
            result = cursor.fetchone()
            metrics["queries_per_sec"] = (result[0] or 0) / 60
            metrics["slow_queries_per_min"] = result[1] or 0
            
            # 2. 活跃连接数
            sql_conn = "SHOW STATUS LIKE 'Threads_connected'"
            cursor.execute(sql_conn)
            result = cursor.fetchone()
            metrics["active_connections"] = int(result[1]) if result else 0
            
            # 3. 平均查询时间
            sql_avg_time = """
            SELECT AVG(duration_ms)
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """
            cursor.execute(sql_avg_time)
            result = cursor.fetchone()
            metrics["avg_query_time_ms"] = float(result[0]) if result[0] else 0
            
            # 4. 缓存命中率（如果使用 Redis）
            metrics["cache_hit_ratio"] = MetricsCollector._get_cache_hit_ratio()
            
            # 5. 锁等待时间
            sql_lock = """
            SELECT AVG(lock_time_ms)
            FROM slow_query_logs
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            AND lock_time_ms > 0
            """
            cursor.execute(sql_lock)
            result = cursor.fetchone()
            metrics["lock_wait_time_ms"] = float(result[0]) if result[0] else 0
            
            # 6. CPU 和内存使用率
            metrics["cpu_usage"] = None  # 需要系统级别采集
            metrics["memory_usage"] = None  # 需要系统级别采集
            metrics["disk_io_reads"] = None
            metrics["disk_io_writes"] = None
            
            cursor.close()
            conn.close()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}
    
    @staticmethod
    def _get_cache_hit_ratio() -> float:
        """获取缓存命中率"""
        try:
            from utils.redis_client import redis_client
            
            # 获取 Redis 统计信息
            info = redis_client.info("stats")
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            
            total = hits + misses
            if total == 0:
                return 1.0
            
            return hits / total
            
        except Exception as e:
            logger.warning(f"Failed to get cache hit ratio: {e}")
            return 0.5  # 默认返回 50%
    
    @staticmethod
    def save_metrics(metrics: Dict) -> bool:
        """保存性能指标到数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO performance_metrics 
            (timestamp, queries_per_sec, slow_queries_per_min, active_connections,
             avg_query_time_ms, cache_hit_ratio, lock_wait_time_ms,
             cpu_usage, memory_usage, disk_io_reads, disk_io_writes)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                metrics.get("queries_per_sec", 0),
                metrics.get("slow_queries_per_min", 0),
                metrics.get("active_connections", 0),
                metrics.get("avg_query_time_ms", 0),
                metrics.get("cache_hit_ratio", 0),
                metrics.get("lock_wait_time_ms", 0),
                metrics.get("cpu_usage"),
                metrics.get("memory_usage"),
                metrics.get("disk_io_reads"),
                metrics.get("disk_io_writes")
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            return False
    
    @staticmethod
    def get_metrics_history(hours: int = 24) -> Dict:
        """获取历史性能指标数据"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                timestamp,
                queries_per_sec,
                slow_queries_per_min,
                active_connections,
                avg_query_time_ms,
                cache_hit_ratio,
                lock_wait_time_ms
            FROM performance_metrics
            WHERE timestamp > DATE_SUB(NOW(), INTERVAL %s HOUR)
            ORDER BY timestamp ASC
            """
            
            cursor.execute(sql, (hours,))
            results = cursor.fetchall()
            
            history = {
                "timestamps": [],
                "queries_per_sec": [],
                "slow_queries_per_min": [],
                "active_connections": [],
                "avg_query_time_ms": [],
                "cache_hit_ratio": [],
                "lock_wait_time_ms": []
            }
            
            for row in results:
                history["timestamps"].append(row[0].isoformat())
                history["queries_per_sec"].append(float(row[1]))
                history["slow_queries_per_min"].append(row[2])
                history["active_connections"].append(row[3])
                history["avg_query_time_ms"].append(float(row[4]))
                history["cache_hit_ratio"].append(float(row[5]))
                history["lock_wait_time_ms"].append(float(row[6]))
            
            cursor.close()
            conn.close()
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return {}
    
    @staticmethod
    def get_latest_metrics() -> Dict:
        """获取最新的性能指标"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                id, timestamp,
                queries_per_sec, slow_queries_per_min, active_connections,
                avg_query_time_ms, cache_hit_ratio, lock_wait_time_ms
            FROM performance_metrics
            ORDER BY timestamp DESC
            LIMIT 1
            """
            
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                metrics = {
                    "id": result[0],
                    "timestamp": result[1].isoformat(),
                    "queries_per_sec": float(result[2]),
                    "slow_queries_per_min": result[3],
                    "active_connections": result[4],
                    "avg_query_time_ms": float(result[5]),
                    "cache_hit_ratio": float(result[6]),
                    "lock_wait_time_ms": float(result[7])
                }
            else:
                metrics = None
            
            cursor.close()
            conn.close()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics: {e}")
            return None
    
    @staticmethod
    def cleanup_old_metrics(days: int = 90) -> int:
        """清理旧的性能指标"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            DELETE FROM performance_metrics
            WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            cursor.execute(sql, (days,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Deleted {deleted_count} old metrics")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            return 0
