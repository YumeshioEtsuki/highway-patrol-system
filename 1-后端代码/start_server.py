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
if "--skip-db-init" in sys.argv:
    os.environ["SKIP_DB_INIT"] = "1"

# 统一由 utils.config 负责加载 .env（位于后端目录）

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
            # 使用数据库目录中的索引脚本
            idx_path = Path(__file__).resolve().parent.parent / "3-数据库" / "02_indexes.sql"
            if idx_path.exists():
                print(f"[INFO] 应用索引脚本: {idx_path}")
                ok = execute_sql_file(str(idx_path), skip_read_only_queries=True, print_query_results=False, stop_on_error=False)
                print("[OK] 索引脚本执行完成" if ok else "[WARN] 索引脚本执行部分失败")
            else:
                print(f"[WARN] 未找到索引脚本: {idx_path}")
        except Exception as e:
            print(f"[WARN] 索引脚本执行失败: {e}")

    # 启动服务器
    import uvicorn
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    
    print(f"\n{'='*60}")
    print(f"  🚀 服务器启动中...")
    print(f"  📍 地址: http://{HOST}:{PORT}")
    print(f"  📚 API 文档: http://{HOST}:{PORT}/docs")
    print(f"  💬 AI 助手已集成 (Ollama + 千问)")
    if SKIP_DB_INIT:
        print(f"  ⚠️ 已启用 SKIP_DB_INIT=1：将跳过数据库初始化")
        print(f"     若为首次启动或表缺失，部分接口将返回空数据或需要初始化。")
        print(f"     可执行 reset_db.py 或移除 SKIP_DB_INIT 后重启。")
    if APPLY_INDEXES:
        print(f"  🧩 已启用 APPLY_INDEXES：启动前运行索引与审计表脚本")
    print(f"  按 Ctrl+C 停止服务器")
    print(f"{'='*60}\n")
    
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\n[INFO] 服务器已停止")
