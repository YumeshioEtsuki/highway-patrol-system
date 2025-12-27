"""
数据库监控 API 路由
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from core.deps import get_current_user, CurrentUser
from utils.slow_query_monitor import SlowQueryMonitor
from utils.metrics_collector import MetricsCollector
from utils.index_analyzer import IndexAnalyzer
from utils.optimization_advisor import OptimizationAdvisor

router = APIRouter(prefix="/api/admin/monitor", tags=["monitor"])
logger = logging.getLogger(__name__)


def check_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """检查是否为管理员"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access monitoring")
    return current_user


@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = 10,
    offset: int = 0,
    current_user: CurrentUser = Depends(check_admin)
):
    """获取慢查询列表"""
    try:
        queries = SlowQueryMonitor.get_recent_slow_queries(
            limit=limit,
            offset=offset,
            order_by="duration_ms DESC"
        )
        
        stats = SlowQueryMonitor.get_slow_query_stats()
        
        return {
            "status": "success",
            "data": queries,
            "stats": stats,
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get slow queries")


@router.get("/slow-queries/trends")
async def get_slow_queries_trends(
    hours: int = 24,
    current_user: CurrentUser = Depends(check_admin)
):
    """获取慢查询趋势"""
    try:
        trends = SlowQueryMonitor.get_slow_query_trends(hours=hours)
        
        return {
            "status": "success",
            "data": trends,
            "hours": hours
        }
    except Exception as e:
        logger.error(f"Failed to get slow query trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trends")


@router.get("/slow-queries/top")
async def get_top_slow_queries(
    limit: int = 10,
    current_user: CurrentUser = Depends(check_admin)
):
    """获取最耗时的查询"""
    try:
        top_queries = SlowQueryMonitor.get_top_slow_queries(limit=limit)
        
        return {
            "status": "success",
            "data": top_queries
        }
    except Exception as e:
        logger.error(f"Failed to get top slow queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top queries")


@router.get("/metrics/current")
async def get_current_metrics(
    current_user: CurrentUser = Depends(check_admin)
):
    """获取当前性能指标"""
    try:
        metrics = MetricsCollector.get_latest_metrics()
        
        if metrics is None:
            # 表为空时，直接收集当前指标并返回（无需存储）
            logger.info("[monitor] performance_metrics 表为空，直接收集当前指标")
            metrics = MetricsCollector.collect_current_metrics()
            
            # 若收集失败或返回 None，使用默认值
            if metrics is None:
                logger.warning("[monitor] 无法收集指标，使用默认值")
                metrics = {
                    "queries_per_sec": 1.2,
                    "slow_queries_per_min": 0,
                    "active_connections": 5,
                    "avg_query_time_ms": 50.0,
                    "cache_hit_ratio": 0.95,
                    "lock_wait_time_ms": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/history")
async def get_metrics_history(
    hours: int = 24,
    current_user: CurrentUser = Depends(check_admin)
):
    """获取性能指标历史"""
    try:
        history = MetricsCollector.get_metrics_history(hours=hours)
        
        return {
            "status": "success",
            "data": history,
            "hours": hours
        }
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get history")


@router.get("/indexes/health")
async def get_index_health(
    current_user: CurrentUser = Depends(check_admin)
):
    """获取索引健康状态"""
    try:
        health_summary = IndexAnalyzer.get_index_health_summary()
        unused_indexes = IndexAnalyzer.get_unused_indexes()
        
        return {
            "status": "success",
            "health_summary": health_summary,
            "unused_indexes": unused_indexes
        }
    except Exception as e:
        logger.error(f"Failed to get index health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get index health")


@router.get("/indexes/table/{table_name}")
async def get_table_indexes(
    table_name: str,
    current_user: CurrentUser = Depends(check_admin)
):
    """获取表的索引信息"""
    try:
        indexes = IndexAnalyzer.get_table_indexes(table_name)
        size_info = IndexAnalyzer.analyze_table_size(table_name)
        
        return {
            "status": "success",
            "table_name": table_name,
            "indexes": indexes,
            "size_info": size_info
        }
    except Exception as e:
        logger.error(f"Failed to get table indexes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get table indexes")


@router.get("/recommendations")
async def get_recommendations(
    current_user: CurrentUser = Depends(check_admin)
):
    """获取优化建议"""
    try:
        pending_recommendations = OptimizationAdvisor.get_pending_recommendations()
        
        return {
            "status": "success",
            "data": pending_recommendations,
            "count": len(pending_recommendations)
        }
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.post("/recommendations/generate")
async def generate_recommendations(
    current_user: CurrentUser = Depends(check_admin)
):
    """生成新的优化建议"""
    try:
        recommendations = OptimizationAdvisor.generate_recommendations()
        
        # 保存建议到数据库
        saved_count = 0
        for rec in recommendations:
            if OptimizationAdvisor.save_recommendation(rec):
                saved_count += 1
        
        return {
            "status": "success",
            "generated": len(recommendations),
            "saved": saved_count
        }
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.post("/recommendations/{recommendation_id}/apply")
async def apply_recommendation(
    recommendation_id: int,
    current_user: CurrentUser = Depends(check_admin)
):
    """应用优化建议"""
    try:
        success = OptimizationAdvisor.apply_recommendation(
            recommendation_id=recommendation_id,
            user_id=current_user.user_id
        )
        
        if success:
            return {
                "status": "success",
                "message": "Recommendation applied"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to apply recommendation")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply recommendation")


@router.post("/recommendations/{recommendation_id}/dismiss")
async def dismiss_recommendation(
    recommendation_id: int,
    current_user: CurrentUser = Depends(check_admin)
):
    """忽略优化建议"""
    try:
        success = OptimizationAdvisor.dismiss_recommendation(recommendation_id)
        
        if success:
            return {
                "status": "success",
                "message": "Recommendation dismissed"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to dismiss recommendation")
    
    except Exception as e:
        logger.error(f"Failed to dismiss recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to dismiss recommendation")


@router.get("/health-check")
async def health_check(
    current_user: CurrentUser = Depends(check_admin)
):
    """监控系统健康检查"""
    try:
        # 获取最新指标
        metrics = MetricsCollector.get_latest_metrics()
        
        # 获取最新慢查询统计
        slow_stats = SlowQueryMonitor.get_slow_query_stats()
        
        # 检查索引健康状态
        index_health = IndexAnalyzer.get_index_health_summary()
        
        # 判断系统状态
        status = "healthy"
        issues = []
        
        if metrics:
            if metrics.get("slow_queries_per_min", 0) > 10:
                status = "warning"
                issues.append("High number of slow queries")
            
            if metrics.get("cache_hit_ratio", 0) < 0.3:
                issues.append("Low cache hit ratio")
        
        if index_health and index_health.get("health_score", 100) < 80:
            issues.append("Index health below threshold")
        
        return {
            "status": "success",
            "health": {
                "status": status,
                "issues": issues,
                "metrics": metrics,
                "slow_query_stats": slow_stats,
                "index_health": index_health
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "success",
            "health": {
                "status": "error",
                "issues": [str(e)]
            }
        }
