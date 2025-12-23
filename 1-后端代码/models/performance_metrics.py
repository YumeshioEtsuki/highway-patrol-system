"""
性能指标数据模型
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class PerformanceMetricsBase(BaseModel):
    """性能指标基类"""
    queries_per_sec: float
    slow_queries_per_min: int
    active_connections: int
    avg_query_time_ms: float
    cache_hit_ratio: float
    lock_wait_time_ms: float = 0.0
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_io_reads: Optional[int] = None
    disk_io_writes: Optional[int] = None


class PerformanceMetricsCreate(PerformanceMetricsBase):
    """创建性能指标"""
    pass


class PerformanceMetrics(PerformanceMetricsBase):
    """性能指标返回模型"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class PerformanceMetricsHistory(BaseModel):
    """性能指标历史数据（用于图表）"""
    timestamps: List[datetime]
    queries_per_sec: List[float]
    slow_queries_per_min: List[int]
    active_connections: List[int]
    avg_query_time_ms: List[float]
    cache_hit_ratio: List[float]


class PerformanceAlert(BaseModel):
    """性能告警"""
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # "warning", "critical"
    message: str
    timestamp: datetime


class IndexHealth(BaseModel):
    """索引健康状态"""
    total_indexes: int
    healthy_indexes: int
    missing_indexes: int
    unused_indexes: int
    redundant_indexes: int
    health_score: float  # 0-100


class OptimizationRecommendation(BaseModel):
    """优化建议"""
    type: str  # "index", "query", "cache", "connection", "partition"
    priority: str  # "HIGH", "MEDIUM", "LOW"
    description: str
    suggested_action: Optional[str] = None
    estimated_improvement: Optional[float] = None
    affected_table: Optional[str] = None
    status: str = "pending"  # "pending", "applied", "dismissed"
    created_at: datetime
