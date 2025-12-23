"""
报告导出异步任务

功能：
- 大型 Excel 报告导出
- 月度/季度报告生成
- PDF 报告生成
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from celery_app import celery_app
from utils.logger import setup_logger
from models.tasks import get_patrol_list_admin, get_admin_stats

logger = setup_logger(__name__)


@celery_app.task(bind=True, name="tasks.report_tasks.export_large_excel", max_retries=2)
def export_large_excel(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    导出大型 Excel 报告（异步）
    
    参数：
        start_date: 开始日期
        end_date: 结束日期
        status_filter: 状态筛选
    
    返回：
        {
            "success": bool,
            "file_path": str,
            "records_count": int,
            "file_size": int
        }
    """
    try:
        logger.info(f"开始导出 Excel: {start_date} - {end_date}")
        
        # 查询数据
        data = get_patrol_list_admin(
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter,
            page=1,
            page_size=10000  # 大批量
        )
        
        records = data.get("records", [])
        
        if not records:
            return {
                "success": False,
                "error": "没有数据可导出"
            }
        
        # 生成 Excel
        import pandas as pd
        df = pd.DataFrame(records)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"patrol_report_{timestamp}.xlsx"
        output_dir = os.path.join("exports")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        # 写入 Excel
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="巡查记录")
        
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Excel 导出完成: {file_path}, {len(records)} 条记录, {file_size} 字节")
        
        return {
            "success": True,
            "file_path": file_path,
            "records_count": len(records),
            "file_size": file_size
        }
    
    except Exception as e:
        logger.error(f"Excel 导出失败: {e}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=120)
        
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(bind=True, name="tasks.report_tasks.generate_monthly_report")
def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
    """
    生成月度报告
    
    参数：
        year: 年份
        month: 月份
    
    返回：
        {
            "success": bool,
            "report_path": str,
            "summary": dict
        }
    """
    try:
        logger.info(f"开始生成月度报告: {year}-{month:02d}")
        
        # 计算月份范围
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        # 获取统计数据
        stats = get_admin_stats(start_date=start_date, end_date=end_date)
        
        # 生成报告内容
        report_content = f"""
# {year}年{month}月 公路巡查月度报告

## 总体数据
- 总记录数：{stats.get('total_records', 0)}
- 待处理：{stats.get('pending_count', 0)}
- 处理中：{stats.get('processing_count', 0)}
- 已完成：{stats.get('completed_count', 0)}

## 问题分布
{stats.get('problem_type_distribution', [])}

## 路段统计
{stats.get('segment_distribution', [])}

---
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        output_dir = os.path.join("reports")
        os.makedirs(output_dir, exist_ok=True)
        report_filename = f"monthly_report_{year}{month:02d}.md"
        report_path = os.path.join(output_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        logger.info(f"月度报告生成完成: {report_path}")
        
        return {
            "success": True,
            "report_path": report_path,
            "summary": stats
        }
    
    except Exception as e:
        logger.error(f"月度报告生成失败: {e}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=120)
        
        return {
            "success": False,
            "error": str(e)
        }
