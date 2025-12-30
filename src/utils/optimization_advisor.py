"""
自动优化建议工具
"""

import logging
from typing import List, Dict
from utils.utils import get_db_connection
from utils.slow_query_monitor import SlowQueryMonitor
from utils.index_analyzer import IndexAnalyzer

logger = logging.getLogger(__name__)


class OptimizationAdvisor:
    """自动优化建议生成器"""
    
    @staticmethod
    def generate_recommendations() -> List[Dict]:
        """生成优化建议"""
        recommendations = []
        
        # 1. 分析慢查询，推荐索引
        recommendations.extend(OptimizationAdvisor._recommend_missing_indexes())
        
        # 2. 检测未使用的索引
        recommendations.extend(OptimizationAdvisor._recommend_remove_unused_indexes())
        
        # 3. 缓存优化建议
        recommendations.extend(OptimizationAdvisor._recommend_caching_strategy())
        
        # 4. 连接池优化建议
        recommendations.extend(OptimizationAdvisor._recommend_connection_pool())
        
        return recommendations
    
    @staticmethod
    def _recommend_missing_indexes() -> List[Dict]:
        """推荐添加的索引"""
        recommendations = []
        
        try:
            # 获取最常见的慢查询
            slow_queries = SlowQueryMonitor.get_top_slow_queries(limit=5)
            
            for query in slow_queries:
                query_text = query.get("query", "")
                execution_count = query.get("execution_count", 0)
                avg_duration = query.get("avg_duration", 0)
                
                # 如果查询被执行多次且耗时长，推荐优化
                if execution_count >= 5 and avg_duration > 1000:
                    # 检查是否包含 WHERE 子句
                    if "WHERE" in query_text.upper():
                        recommendations.append({
                            "type": "index",
                            "priority": "HIGH" if avg_duration > 5000 else "MEDIUM",
                            "description": f"考虑为频繁查询添加索引（已执行 {execution_count} 次，平均耗时 {avg_duration:.0f}ms）",
                            "suggested_action": "分析 WHERE 子句中的字段，添加合适的索引",
                            "estimated_improvement": 40.0,
                            "affected_table": OptimizationAdvisor._extract_table_name(query_text)
                        })
            
        except Exception as e:
            logger.error(f"Failed to recommend missing indexes: {e}")
        
        return recommendations
    
    @staticmethod
    def _recommend_remove_unused_indexes() -> List[Dict]:
        """推荐删除未使用的索引"""
        recommendations = []
        
        try:
            unused_indexes = IndexAnalyzer.get_unused_indexes()
            
            for index in unused_indexes:
                recommendations.append({
                    "type": "index",
                    "priority": "LOW",
                    "description": f"表 {index['table_name']} 中的索引 {index['index_name']} 未被使用",
                    "suggested_action": f"DROP INDEX {index['index_name']} ON {index['table_name']}",
                    "estimated_improvement": 5.0,  # 释放存储空间和写性能
                    "affected_table": index['table_name']
                })
        
        except Exception as e:
            logger.error(f"Failed to recommend removing unused indexes: {e}")
        
        return recommendations
    
    @staticmethod
    def _recommend_caching_strategy() -> List[Dict]:
        """推荐缓存策略"""
        recommendations = []
        
        try:
            # 获取最常执行的查询
            slow_queries = SlowQueryMonitor.get_top_slow_queries(limit=5)
            
            for query in slow_queries:
                execution_count = query.get("execution_count", 0)
                avg_duration = query.get("avg_duration", 0)
                
                # 如果查询被执行很多次
                if execution_count >= 20:
                    recommendations.append({
                        "type": "cache",
                        "priority": "HIGH" if execution_count >= 100 else "MEDIUM",
                        "description": f"频繁执行的查询（{execution_count} 次）适合缓存",
                        "suggested_action": "为此查询实现 Redis 缓存，TTL 设置为 5-60 分钟",
                        "estimated_improvement": 50.0,
                        "affected_table": OptimizationAdvisor._extract_table_name(query.get("query", ""))
                    })
        
        except Exception as e:
            logger.error(f"Failed to recommend caching strategy: {e}")
        
        return recommendations
    
    @staticmethod
    def _recommend_connection_pool() -> List[Dict]:
        """推荐连接池优化"""
        recommendations = []
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 检查活跃连接数
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            result = cursor.fetchone()
            active_connections = int(result[1]) if result else 0
            
            cursor.close()
            conn.close()
            
            # 如果活跃连接数很高
            if active_connections > 50:
                recommendations.append({
                    "type": "connection",
                    "priority": "HIGH",
                    "description": f"当前活跃连接数很高（{active_connections} 个）",
                    "suggested_action": "增加连接池大小或启用连接重用",
                    "estimated_improvement": 20.0,
                    "affected_table": None
                })
        
        except Exception as e:
            logger.error(f"Failed to recommend connection pool optimization: {e}")
        
        return recommendations
    
    @staticmethod
    def _extract_table_name(query: str) -> str:
        """从 SQL 中提取表名"""
        try:
            # 简单的表名提取逻辑
            query_upper = query.upper()
            
            if "FROM" in query_upper:
                from_index = query_upper.index("FROM")
                rest = query[from_index + 5:].strip()
                table_name = rest.split()[0].replace("`", "")
                return table_name
            
            return None
        except:
            return None
    
    @staticmethod
    def save_recommendation(recommendation: Dict) -> bool:
        """保存优化建议到数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO optimization_recommendations
            (type, priority, description, suggested_action, estimated_improvement, affected_table, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """
            
            cursor.execute(sql, (
                recommendation.get("type"),
                recommendation.get("priority"),
                recommendation.get("description"),
                recommendation.get("suggested_action"),
                recommendation.get("estimated_improvement"),
                recommendation.get("affected_table")
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")
            return False
    
    @staticmethod
    def get_pending_recommendations() -> List[Dict]:
        """获取待处理的优化建议"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                id, type, priority, description, suggested_action,
                estimated_improvement, affected_table, created_at
            FROM optimization_recommendations
            WHERE status = 'pending'
            ORDER BY priority = 'HIGH' DESC, created_at DESC
            """
            
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to get pending recommendations: {e}")
            return []
    
    @staticmethod
    def apply_recommendation(recommendation_id: int, user_id: int) -> bool:
        """应用优化建议"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            UPDATE optimization_recommendations
            SET status = 'applied', applied_at = NOW(), applied_by = %s
            WHERE id = %s
            """
            
            cursor.execute(sql, (user_id, recommendation_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Applied recommendation {recommendation_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to apply recommendation: {e}")
            return False
    
    @staticmethod
    def dismiss_recommendation(recommendation_id: int) -> bool:
        """忽略优化建议"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            UPDATE optimization_recommendations
            SET status = 'dismissed'
            WHERE id = %s
            """
            
            cursor.execute(sql, (recommendation_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to dismiss recommendation: {e}")
            return False
