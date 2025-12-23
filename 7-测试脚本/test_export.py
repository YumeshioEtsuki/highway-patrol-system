#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试导出功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '1-后端代码'))

from models.tasks import export_patrol_records_to_excel

print("开始测试导出...")
try:
    excel_bytes = export_patrol_records_to_excel(filters=None)
    print(f"✅ 导出成功！文件大小: {len(excel_bytes)} bytes")
    
    # 保存到文件测试
    with open('test_output.xlsx', 'wb') as f:
        f.write(excel_bytes)
    print("✅ 已保存到 test_output.xlsx，可以尝试打开验证")
    
except Exception as e:
    print(f"❌ 导出失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
