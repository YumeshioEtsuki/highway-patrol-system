"""
索引分析工具
"""

import logging
from typing import List, Dict, Optional
from utils.utils import get_db_connection

logger = logging.getLogger(__name__)


class IndexAnalyzer:
    """数据库索引分析工具"""
    
    @staticmethod
    def get_table_indexes(table_name: str) -> List[Dict]:
        """获取表的所有索引"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                INDEX_NAME,
                COLUMN_NAME,
                SEQ_IN_INDEX,
                INDEX_TYPE
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """
            
            cursor.execute(sql, (table_name,))
            results = cursor.fetchall()
            
            indexes = {}
            for row in results:
                index_name = row[0]
                if index_name not in indexes:
                    indexes[index_name] = {
                        "name": index_name,
                        "columns": [],
                        "type": row[3]
                    }
                indexes[index_name]["columns"].append(row[1])
            
            cursor.close()
            conn.close()
            
            return list(indexes.values())
            
        except Exception as e:
            logger.error(f"Failed to get table indexes: {e}")
            return []
    
    @staticmethod
    def get_all_tables() -> List[str]:
        """获取数据库中的所有表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()"
            cursor.execute(sql)
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    @staticmethod
    def analyze_table_size(table_name: str) -> Dict:
        """分析表大小和行数"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                TABLE_ROWS,
                ROUND(DATA_LENGTH / 1024 / 1024, 2) as data_size_mb,
                ROUND(INDEX_LENGTH / 1024 / 1024, 2) as index_size_mb
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            """
            
            cursor.execute(sql, (table_name,))
            result = cursor.fetchone()
            
            if result:
                info = {
                    "table_name": table_name,
                    "rows": result[0],
                    "data_size_mb": float(result[1]),
                    "index_size_mb": float(result[2])
                }
            else:
                info = None
            
            cursor.close()
            conn.close()
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to analyze table size: {e}")
            return None
    
    @staticmethod
    def get_unused_indexes() -> List[Dict]:
        """获取未使用的索引"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # MySQL 不提供直接的未使用索引统计，使用 performance_schema
            sql = """
            SELECT 
                OBJECT_SCHEMA,
                OBJECT_NAME,
                INDEX_NAME
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE OBJECT_SCHEMA != 'mysql' 
            AND OBJECT_SCHEMA != 'performance_schema'
            AND COUNT_STAR = 0
            AND INDEX_NAME != 'PRIMARY'
            ORDER BY OBJECT_NAME, INDEX_NAME
            """
            
            cursor.execute(sql)
            results = cursor.fetchall()
            
            unused = [
                {
                    "table_name": row[1],
                    "index_name": row[2],
                    "status": "unused"
                }
                for row in results
            ]
            
            cursor.close()
            conn.close()
            
            return unused
            
        except Exception as e:
            logger.warning(f"Performance schema not available: {e}")
            return []
    
    @staticmethod
    def get_missing_indexes_for_table(table_name: str) -> List[Dict]:
        """推荐为表添加的索引"""
        recommendations = []
        
        try:
            # 分析常见的查询模式，推荐索引
            # 这是一个简化版本，实际应用中可以基于慢查询日志进行分析
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取表的列信息
            sql = """
            SELECT COLUMN_NAME, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            """
            
            cursor.execute(sql, (table_name,))
            columns = cursor.fetchall()
            
            # 根据列名推荐索引
            index_recommendations = {
                "status": "应为状态列添加索引",
                "user_id": "应为用户 ID 列添加索引",
                "timestamp": "应为时间戳列添加索引",
                "created_at": "应为创建时间列添加索引",
                "email": "应为邮箱列添加索引"
            }
            
            for column in columns:
                col_name = column[0]
                for keyword, recommendation in index_recommendations.items():
                    if keyword in col_name.lower():
                        recommendations.append({
                            "table_name": table_name,
                            "column_name": col_name,
                            "recommendation": recommendation,
                            "priority": "MEDIUM"
                        })
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to analyze missing indexes: {e}")
        
        return recommendations
    
    @staticmethod
    def analyze_index_efficiency(table_name: str) -> Dict:
        """分析索引效率"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取索引使用统计
            sql = """
            SELECT 
                INDEX_NAME,
                COUNT_STAR,
                COUNT_READ,
                COUNT_WRITE
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE OBJECT_SCHEMA = DATABASE() AND OBJECT_NAME = %s
            ORDER BY COUNT_STAR DESC
            """
            
            cursor.execute(sql, (table_name,))
            results = cursor.fetchall()
            
            efficiency = {
                "table_name": table_name,
                "total_indexes": len(results),
                "indexes": []
            }
            
            for row in results:
                efficiency["indexes"].append({
                    "index_name": row[0],
                    "total_accesses": row[1],
                    "read_count": row[2],
                    "write_count": row[3],
                    "efficiency": row[2] / max(row[1], 1)  # 读写比
                })
            
            cursor.close()
            conn.close()
            
            return efficiency
            
        except Exception as e:
            logger.warning(f"Performance schema not available: {e}")
            return {
                "table_name": table_name,
                "total_indexes": 0,
                "indexes": []
            }
    
    @staticmethod
    def get_index_health_summary() -> Dict:
        """获取索引健康总结"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 总索引数
            sql1 = """
            SELECT COUNT(DISTINCT INDEX_NAME)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND INDEX_NAME != 'PRIMARY'
            """
            cursor.execute(sql1)
            total_indexes = cursor.fetchone()[0]
            
            # 未使用索引数（如果性能架构可用）
            sql2 = """
            SELECT COUNT(*)
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE OBJECT_SCHEMA = DATABASE() 
            AND INDEX_NAME != 'PRIMARY'
            AND COUNT_STAR = 0
            """
            
            try:
                cursor.execute(sql2)
                unused_indexes = cursor.fetchone()[0]
            except:
                unused_indexes = 0
            
            # 计算健康分数
            health_score = 100
            if total_indexes > 0:
                unused_ratio = unused_indexes / total_indexes
                if unused_ratio > 0.2:
                    health_score -= unused_ratio * 30
            
            summary = {
                "total_indexes": total_indexes,
                "unused_indexes": unused_indexes,
                "health_score": max(0, health_score),
                "status": "optimal" if health_score >= 80 else "needs_attention"
            }
            
            cursor.close()
            conn.close()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get index health summary: {e}")
            return {
                "total_indexes": 0,
                "unused_indexes": 0,
                "health_score": 0,
                "status": "unknown"
            }
