#!/usr/bin/env python3
"""
简单启动脚本 - 绕过可能的初始化问题
"""
import os
import sys
from pathlib import Path

# 设置 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# 设置环境变量
os.environ['SKIP_DB_INIT'] = '1'

# 启动应用
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'app:app',
        host='127.0.0.1',
        port=5000,
        reload=False,
        workers=1,
        log_level='info'
    )
