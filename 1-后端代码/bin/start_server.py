#!/usr/bin/env python3
"""
服务器启动脚本 - 自动处理端口冲突
"""
import os
import sys
from pathlib import Path
import asyncio
import socket
import subprocess

"""
SKIP_DB_INIT 控制是否在应用启动生命周期中执行数据库初始化。
此脚本不再强制设置为 1，改为：
- 支持通过环境变量 `SKIP_DB_INIT=1` 控制
- 支持命令行参数 `--skip-db-init` 控制
"""
# 确保工作目录和 sys.path 指向后端根目录
BACKEND_ROOT = Path(__file__).resolve().parent.parent
os.chdir(BACKEND_ROOT)
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# 解析启动参数，允许通过环境变量或参数控制 DB 初始化
if "--skip-db-init" in sys.argv:
    os.environ["SKIP_DB_INIT"] = "1"

# 统一由 utils.config 加载 .env；此处导入应用
from app import app
from utils.utils import execute_sql_file

def check_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_process_on_port(port):
    """停止占用指定端口的进程 (Windows)"""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True)
        output = ''
        try:
            output = result.stdout.decode('utf-8')
        except Exception:
            output = result.stdout.decode('gbk', errors='ignore')

        for line in output.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = [p.strip() for p in line.split() if p.strip()]
                if len(parts) > 0:
                    pid = parts[-1]
                    if pid.isdigit():
                        print(f"[INFO] 发现端口 {port} 被进程 {pid} 占用，正在停止...")
                        result = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        if result.returncode != 0:
                            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
                        print(f"[OK] 已停止进程 {pid}")
                        return True
        return False
    except Exception as e:
        print(f"[WARN] 清理端口失败: {e}")
        return False

if __name__ == '__main__':
    PORT = 5000
    HOST = "0.0.0.0"  # 监听所有IP，支持真机访问
    # CLI 选项支持
    APPLY_INDEXES = os.getenv("APPLY_INDEXES_ON_START", "0") == "1" or ("--apply-indexes" in sys.argv)
    SKIP_DB_INIT = os.getenv("SKIP_DB_INIT", "0") == "1" or ("--skip-db-init" in sys.argv)
    if any(flag in sys.argv for flag in ("-h", "--help")):
        print("""
用法: start_server.py [--skip-db-init] [--apply-indexes]

选项:
  --skip-db-init    启动时跳过数据库初始化（开发快速启动）
  --apply-indexes   启动前执行索引与审计表检查/创建
        """)
        sys.exit(0)
    
    # 启动前检查端口
    if check_port_in_use(PORT):
        print(f"[WARN] 端口 {PORT} 已被占用，尝试自动清理...")
        if kill_process_on_port(PORT):
            import time
            time.sleep(2)  # 等待端口完全释放
            if check_port_in_use(PORT):
                print(f"[ERROR] 端口 {PORT} 仍被占用，请手动检查")
                sys.exit(1)
            print(f"[OK] 端口 {PORT} 已释放")
        else:
            print(f"[ERROR] 无法清理端口 {PORT}，请手动停止占用进程")
            sys.exit(1)
    
    # 可选：启动前应用索引优化
    if APPLY_INDEXES:
        try:
            # 使用数据库目录中的索引脚本（从后端/bin/ 向上到项目根目录，再找 3-数据库）
            idx_path = Path(__file__).resolve().parent.parent.parent / "3-数据库" / "02_create_indexes.sql"
            if idx_path.exists():
                print(f"[INFO] Applying index script: {idx_path}")
                ok = execute_sql_file(str(idx_path), skip_read_only_queries=True, print_query_results=False, stop_on_error=False)
                print("[OK] Index script completed" if ok else "[WARN] Index script partially failed")
            else:
                print(f"[WARN] Index script not found: {idx_path}")
        except Exception as e:
            print(f"[WARN] Index script execution failed: {e}")

    # 启动服务器
    import uvicorn
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True,
        timeout_keep_alive=75,  # 增加keep-alive超时（支持SSE长连接）
        timeout_graceful_shutdown=5
    )
    server = uvicorn.Server(config)
    
    print(f"\n{'='*60}")
    print(f"  [*] Server starting...")
    print(f"  [*] Address: http://{HOST}:{PORT}")
    print(f"  [*] API docs: http://{HOST}:{PORT}/docs")
    print(f"  [*] AI assistant integrated (Ollama + Qwen)")
    if SKIP_DB_INIT:
        print(f"  [WARN] SKIP_DB_INIT=1 enabled: skipping database initialization")
        print(f"         If first run or tables missing, some endpoints may return empty.")
        print(f"         Run reset_db.py or remove SKIP_DB_INIT and restart.")
    if APPLY_INDEXES:
        print(f"  [*] APPLY_INDEXES enabled: running index and audit table script")
    print(f"  Press Ctrl+C to stop server")
    print(f"{'='*60}\n")
    
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped")
