"""
慢查询日志数据模型
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SlowQueryLogBase(BaseModel):
    """慢查询日志基类"""
    query: str
    duration_ms: float
    rows_examined: int = 0
    rows_returned: int = 0
    lock_time_ms: float = 0.0
    user_id: Optional[int] = None
    endpoint: Optional[str] = None


class SlowQueryLogCreate(SlowQueryLogBase):
    """创建慢查询日志"""
    pass


class SlowQueryLog(SlowQueryLogBase):
    """慢查询日志返回模型"""
    id: int
    query_hash: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class SlowQueryStats(BaseModel):
    """慢查询统计数据"""
    total: int
    avg_duration: float
    max_duration: float
    min_duration: float
    total_rows_examined: int
    most_common_endpoint: Optional[str] = None
    queries_per_minute: float


class SlowQueryTrend(BaseModel):
    """慢查询趋势数据"""
    timestamp: datetime
    count: int
    avg_duration: float


class SlowQueryDetail(BaseModel):
    """慢查询详细信息"""
    query: str
    execution_count: int
    avg_duration: float
    total_duration: float
    max_duration: float
    min_duration: float
    first_seen: datetime
    last_seen: datetime
    most_common_endpoint: Optional[str] = None
