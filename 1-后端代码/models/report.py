"""
报表系统 Pydantic Schemas
Phase 2 Stage 2
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


# Enums
class ReportTypeEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    custom = "custom"


class FrequencyEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class DeliveryMethodEnum(str, Enum):
    email = "email"
    wechat = "wechat"
    dingtalk = "dingtalk"


class FileTypeEnum(str, Enum):
    pdf = "pdf"
    xlsx = "xlsx"
    csv = "csv"


class StatusEnum(str, Enum):
    pending = "pending"
    generating = "generating"
    completed = "completed"
    failed = "failed"


# Request Schemas
class ReportTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: ReportTypeEnum
    config: Optional[Dict[str, Any]] = {}
    sql_template: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = {}
    enabled: bool = True


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    sql_template: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class ReportGenerateRequest(BaseModel):
    template_id: int = Field(..., gt=0)
    time_range_start: date
    time_range_end: date
    file_type: FileTypeEnum = FileTypeEnum.xlsx
    filters: Optional[Dict[str, Any]] = {}
    
    @validator('time_range_end')
    def validate_date_range(cls, v, values):
        if 'time_range_start' in values and v < values['time_range_start']:
            raise ValueError('结束日期不能早于开始日期')
        return v


class SubscriptionCreate(BaseModel):
    template_id: int = Field(..., gt=0)
    frequency: FrequencyEnum
    send_time: time = Field(default=time(9, 0))
    send_day: Optional[str] = None
    delivery_method: DeliveryMethodEnum = DeliveryMethodEnum.email
    delivery_target: str = Field(..., min_length=1)
    enabled: bool = True
    
    @validator('send_day')
    def validate_send_day(cls, v, values):
        if 'frequency' not in values:
            return v
        freq = values['frequency']
        if freq == FrequencyEnum.weekly:
            valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            if v and v.lower() not in valid_days:
                raise ValueError(f'周报发送日期必须是 {valid_days} 之一')
        elif freq == FrequencyEnum.monthly:
            if v and not (v.isdigit() and 1 <= int(v) <= 31):
                raise ValueError('月报发送日期必须是 1-31 之间的数字')
        return v


class SubscriptionUpdate(BaseModel):
    frequency: Optional[FrequencyEnum] = None
    send_time: Optional[time] = None
    send_day: Optional[str] = None
    delivery_target: Optional[str] = None
    enabled: Optional[bool] = None


# Response Schemas
class ReportTemplateResponse(BaseModel):
    id: int
    name: str
    type: str
    config: Optional[Dict[str, Any]]
    chart_config: Optional[Dict[str, Any]]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    enabled: bool

    class Config:
        from_attributes = True


class ReportGenerationResponse(BaseModel):
    id: int
    template_id: int
    template_name: Optional[str] = None
    generated_by: Optional[int]
    generation_time: datetime
    time_range_start: Optional[date]
    time_range_end: Optional[date]
    file_type: str
    file_size: Optional[int]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    status: str
    error_msg: Optional[str]
    row_count: Optional[int]

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: int
    template_id: int
    template_name: Optional[str] = None
    subscriber_id: int
    frequency: str
    send_time: Optional[time]
    send_day: Optional[str]
    delivery_method: str
    delivery_target: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportMetricResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    dimension: Optional[str]
    unit: Optional[str]
    format_type: str
    enabled: bool

    class Config:
        from_attributes = True


# Statistics Schemas
class DailyReportData(BaseModel):
    report_date: date
    department_name: str
    segment_name: str
    total_inspections: int
    pending_orders: int
    overdue_orders: int
    avg_resolution_hours: Optional[float]


class WeeklyReportData(BaseModel):
    report_week: str
    department_name: str
    total_inspections: int
    completed_orders: int
    avg_resolution_hours: Optional[float]


class ReportStatsSummary(BaseModel):
    """报表统计摘要"""
    total_generated: int
    last_24h: int
    failed_count: int
    avg_generation_time: Optional[float]
    total_file_size: Optional[int]


class ReportListQuery(BaseModel):
    """报表列表查询参数"""
    template_id: Optional[int] = None
    status: Optional[StatusEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
