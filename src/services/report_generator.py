"""
报表生成引擎（Stage 2）
- 按模板类型查询视图/SQL
- 生成 Excel/CSV 文件
- 返回文件路径、大小、行数

注意：PDF 生成暂未实现，若请求 pdf 将降级为 csv。
"""
import os
import csv
import json
from datetime import datetime, date
from typing import Dict, Any, List, Tuple, Optional
from utils.utils import get_db_connection

try:
    from openpyxl import Workbook  # 轻量依赖
    HAS_OPENPYXL = True
except ImportError:  # openpyxl 可选
    HAS_OPENPYXL = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_PDF = True
except ImportError:  # reportlab 可选
    HAS_PDF = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "exports"))
os.makedirs(EXPORT_DIR, exist_ok=True)


def _fetch_data(template: Dict[str, Any], start_date: date, end_date: date, filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    """根据模板类型抓取数据"""
    t_type = template.get("type")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if t_type == "daily":
            sql = "SELECT * FROM v_daily_report_summary WHERE report_date BETWEEN %s AND %s"
            params = [start_date, end_date]
            if filters.get("department_name"):
                sql += " AND department_name = %s"
                params.append(filters["department_name"])
            if filters.get("segment_name"):
                sql += " AND segment_name = %s"
                params.append(filters["segment_name"])
            cursor.execute(sql, params)
        elif t_type == "weekly":
            # YEARWEEK 按 ISO 周
            sql = "SELECT * FROM v_weekly_report_summary WHERE report_week BETWEEN YEARWEEK(%s,1) AND YEARWEEK(%s,1)"
            params = [start_date, end_date]
            cursor.execute(sql, params)
        else:
            # custom / monthly: 若 sql_template 存在则直接执行
            sql_template = template.get("sql_template")
            if not sql_template:
                raise ValueError(f"模板 {template.get('name')} 缺少 sql_template，无法生成")
            # 简单占位符替换
            sql = sql_template.replace(":start_date", "%s").replace(":end_date", "%s")
            params = [start_date, end_date]
            cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows, t_type
    finally:
        cursor.close()
        conn.close()


def _write_csv(headers: List[str], rows: List[Dict[str, Any]], file_path: str) -> Tuple[str, int, int]:
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([row.get(h) for h in headers])
    return file_path, os.path.getsize(file_path), len(rows)


def _write_xlsx(headers: List[str], rows: List[Dict[str, Any]], file_path: str) -> Tuple[str, int, int]:
    if not HAS_OPENPYXL:
        # 降级为 csv
        csv_path = file_path.replace('.xlsx', '.csv')
        return _write_csv(headers, rows, csv_path)
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h) for h in headers])
    wb.save(file_path)
    return file_path, os.path.getsize(file_path), len(rows)


def _write_pdf(headers: List[str], rows: List[Dict[str, Any]], file_path: str) -> Tuple[str, int, int]:
    if not HAS_PDF:
        csv_path = file_path.replace('.pdf', '.csv')
        return _write_csv(headers, rows, csv_path)
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    data = [headers]
    for row in rows:
        data.append([row.get(h, "") for h in headers])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    story = []
    styles = getSampleStyleSheet()
    title = Paragraph("报表导出", styles["Title"])
    story.append(title)
    story.append(table)
    doc.build(story)
    return file_path, os.path.getsize(file_path), len(rows)


def generate_report(template: Dict[str, Any], start_date: date, end_date: date,
                    file_type: str = "xlsx", filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    filters = filters or {}
    rows, t_type = _fetch_data(template, start_date, end_date, filters)
    if not rows:
        raise ValueError("无可导出的数据")

    headers = list(rows[0].keys())
    safe_name = template.get("name", "report").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if file_type == "pdf":
        filename = f"{safe_name}_{timestamp}.pdf"
        file_path = os.path.join(EXPORT_DIR, filename)
        file_path, file_size, row_count = _write_pdf(headers, rows, file_path)
        # 若降级到 csv，重置文件类型与文件名
        if not file_path.endswith(".pdf"):
            file_type = "csv"
            filename = os.path.basename(file_path)
    elif file_type == "csv":
        filename = f"{safe_name}_{timestamp}.csv"
        file_path = os.path.join(EXPORT_DIR, filename)
        file_path, file_size, row_count = _write_csv(headers, rows, file_path)
    else:  # 默认 xlsx
        filename = f"{safe_name}_{timestamp}.xlsx"
        file_path = os.path.join(EXPORT_DIR, filename)
        file_path, file_size, row_count = _write_xlsx(headers, rows, file_path)

    download_url = f"/api/reports/download?path={filename}"
    return {
        "file_path": file_path,
        "file_size": file_size,
        "row_count": row_count,
        "download_url": download_url,
        "file_type": file_type
    }
