#!/usr/bin/env python3
"""
验证路由是否被正确注册
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "src"
sys.path.insert(0, str(BACKEND_DIR))

try:
    from app import app
    
    print("\n" + "="*60)
    print("检查所有已注册的路由")
    print("="*60)
    
    found_clear_cache = False
    found_admin_stats = False
    
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', set())
            path = route.path
            
            if 'clear-cache' in path:
                print(f"\n✅ 找到clear-cache路由！")
                print(f"   路径: {path}")
                print(f"   方法: {methods}")
                found_clear_cache = True
            
            if path == '/api/admin/stats':
                print(f"\n✅ 找到admin/stats路由！")
                print(f"   路径: {path}")
                print(f"   方法: {methods}")
                found_admin_stats = True
            
            if any(x in path for x in ['/api/admin', '/api/patrol', '/api/sse']):
                print(f"   {methods} {path}")
    
    print("\n" + "="*60)
    print("验证结果")
    print("="*60)
    
    if found_clear_cache:
        print("✅ clear-cache 路由已正确注册")
    else:
        print("❌ clear-cache 路由未找到！")
        
    if found_admin_stats:
        print("✅ admin/stats 路由已正确注册")
    else:
        print("❌ admin/stats 路由未找到！")
    
    print()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
