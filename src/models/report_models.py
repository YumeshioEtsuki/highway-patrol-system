"""
报表系统 ORM 模型
Phase 2 Stage 2
"""
from datetime import datetime, date
from typing import Optional
from enum import Enum


class ReportType(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    CUSTOM = 'custom'


class ReportFrequency(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class DeliveryMethod(str, Enum):
    EMAIL = 'email'
    WECHAT = 'wechat'
    DINGTALK = 'dingtalk'


class FileType(str, Enum):
    PDF = 'pdf'
    XLSX = 'xlsx'
    CSV = 'csv'


class GenerationStatus(str, Enum):
    PENDING = 'pending'
    GENERATING = 'generating'
    COMPLETED = 'completed'
    FAILED = 'failed'


class SendStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'


class ReportTemplate:
    """报表模板"""
    def __init__(self, id: int = None, name: str = None, type: str = None,
                 config: dict = None, sql_template: str = None, 
                 chart_config: dict = None, created_by: int = None,
                 created_at: datetime = None, updated_at: datetime = None,
                 enabled: int = 1):
        self.id = id
        self.name = name
        self.type = type
        self.config = config
        self.sql_template = sql_template
        self.chart_config = chart_config
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.enabled = enabled

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'config': self.config,
            'sql_template': self.sql_template,
            'chart_config': self.chart_config,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'enabled': bool(self.enabled)
        }


class ReportSubscription:
    """报表订阅"""
    def __init__(self, id: int = None, template_id: int = None, 
                 subscriber_id: int = None, frequency: str = None,
                 send_time: str = None, send_day: str = None,
                 delivery_method: str = 'email', delivery_target: str = None,
                 enabled: int = 1, created_at: datetime = None,
                 updated_at: datetime = None):
        self.id = id
        self.template_id = template_id
        self.subscriber_id = subscriber_id
        self.frequency = frequency
        self.send_time = send_time
        self.send_day = send_day
        self.delivery_method = delivery_method
        self.delivery_target = delivery_target
        self.enabled = enabled
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'subscriber_id': self.subscriber_id,
            'frequency': self.frequency,
            'send_time': str(self.send_time) if self.send_time else None,
            'send_day': self.send_day,
            'delivery_method': self.delivery_method,
            'delivery_target': self.delivery_target,
            'enabled': bool(self.enabled),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReportGenerationHistory:
    """报表生成历史"""
    def __init__(self, id: int = None, template_id: int = None,
                 generated_by: int = None, generation_time: datetime = None,
                 time_range_start: date = None, time_range_end: date = None,
                 file_path: str = None, file_type: str = None,
                 file_size: int = None, download_url: str = None,
                 expires_at: datetime = None, status: str = 'pending',
                 error_msg: str = None, row_count: int = None):
        self.id = id
        self.template_id = template_id
        self.generated_by = generated_by
        self.generation_time = generation_time or datetime.now()
        self.time_range_start = time_range_start
        self.time_range_end = time_range_end
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.download_url = download_url
        self.expires_at = expires_at
        self.status = status
        self.error_msg = error_msg
        self.row_count = row_count

    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'generated_by': self.generated_by,
            'generation_time': self.generation_time.isoformat() if self.generation_time else None,
            'time_range_start': self.time_range_start.isoformat() if self.time_range_start else None,
            'time_range_end': self.time_range_end.isoformat() if self.time_range_end else None,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'download_url': self.download_url,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status,
            'error_msg': self.error_msg,
            'row_count': self.row_count
        }


class ReportSendLog:
    """报表发送日志"""
    def __init__(self, id: int = None, report_id: int = None,
                 subscription_id: int = None, sent_to: str = None,
                 send_method: str = None, sent_at: datetime = None,
                 status: str = 'pending', retry_count: int = 0,
                 error_msg: str = None):
        self.id = id
        self.report_id = report_id
        self.subscription_id = subscription_id
        self.sent_to = sent_to
        self.send_method = send_method
        self.sent_at = sent_at or datetime.now()
        self.status = status
        self.retry_count = retry_count
        self.error_msg = error_msg

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'subscription_id': self.subscription_id,
            'sent_to': self.sent_to,
            'send_method': self.send_method,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'retry_count': self.retry_count,
            'error_msg': self.error_msg
        }


class ReportMetric:
    """自定义统计指标"""
    def __init__(self, id: int = None, name: str = None, 
                 display_name: str = None, description: str = None,
                 sql_expression: str = None, dimension: str = None,
                 unit: str = None, format_type: str = 'number',
                 sort_order: int = 0, enabled: int = 1,
                 created_at: datetime = None, updated_at: datetime = None):
        self.id = id
        self.name = name
        self.display_name = display_name
        self.description = description
        self.sql_expression = sql_expression
        self.dimension = dimension
        self.unit = unit
        self.format_type = format_type
        self.sort_order = sort_order
        self.enabled = enabled
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'sql_expression': self.sql_expression,
            'dimension': self.dimension,
            'unit': self.unit,
            'format_type': self.format_type,
            'sort_order': self.sort_order,
            'enabled': bool(self.enabled),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
