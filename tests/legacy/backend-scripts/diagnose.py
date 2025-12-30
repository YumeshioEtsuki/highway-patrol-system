#!/usr/bin/env python3
"""
诊断脚本 - 检查 app 导入和创建
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 设置 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

os.environ['SKIP_DB_INIT'] = '1'

# 加载 .env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env")

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("❌ DEEPSEEK_API_KEY is required! 请在环境变量或 .env 中设置")

print("[INFO] Importing app...")
try:
    from app import app
    print("[OK] App imported successfully")
    print(f"[OK] App routes: {len(app.routes)} routes registered")
    
    # 检查 /api/chat/health 路由是否存在
    chat_routes = [r for r in app.routes if '/chat' in str(r.path)]
    print(f"[OK] Chat routes found: {len(chat_routes)}")
    for r in chat_routes:
        print(f"  - {r.path} {r.methods}")
        
except Exception as e:
    print(f"[ERROR] Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
