#!/usr/bin/env python3
"""
调试启动 - 捕获详细日志
"""
import os
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)

os.environ['SKIP_DB_INIT'] = '1'

print("[STARTUP] Configuring logging...")
logger = logging.getLogger('debug_startup')

logger.info("Python version: %s", sys.version)
logger.info("Python executable: %s", sys.executable)

# 导入 FastAPI
logger.info("Importing FastAPI...")
from fastapi import FastAPI
logger.info("FastAPI imported OK")

# 导入应用
logger.info("Importing app from app.py...")
from app import app as fastapi_app
logger.info("App imported OK, routes: %d", len(fastapi_app.routes))

# 导入 uvicorn
logger.info("Importing uvicorn...")
import uvicorn
logger.info("Uvicorn %s imported OK", uvicorn.__version__)

# 创建配置
logger.info("Creating Uvicorn config...")
config = uvicorn.Config(
    fastapi_app,
    host="127.0.0.1",
    port=5000,
    log_level="debug",
    access_log=True,
    use_colors=True,
)
logger.info("Config created OK")

# 创建服务器
logger.info("Creating Uvicorn server...")
server = uvicorn.Server(config)
logger.info("Server created OK")

# 启动服务器
logger.info("Starting server...")
try:
    import asyncio
    asyncio.run(server.serve())
except KeyboardInterrupt:
    logger.info("Keyboard interrupt received")
except Exception as e:
    logger.exception("Server error: %s", e)
finally:
    logger.info("Server shutdown complete")
