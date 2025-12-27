#!/usr/bin/env python3
"""
仪表盘与报表系统 - 快速启动脚本

功能：自动启动所有必要的服务（Redis、Celery Worker、FastAPI）
用法：python quick-start.py

注意：此脚本用于开发环境，不适合生产部署
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime


class Colors:
    """终端颜色输出"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}  {msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}\n")


def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")


def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")


def check_redis():
    """检查 Redis 是否运行"""
    print_info("检查 Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print_success("Redis 连接成功")
        return True
    except Exception as e:
        print_error(f"Redis 连接失败: {e}")
        print_info("请先启动 Redis: redis-server")
        return False


def start_celery_worker():
    """启动 Celery Worker"""
    print_info("启动 Celery Worker...")
    
    backend_path = Path(__file__).parent / "1-后端代码"
    if not backend_path.exists():
        print_error(f"后端目录不存在: {backend_path}")
        return None
    
    try:
        process = subprocess.Popen(
            [
                "celery", "-A", "celery_app", "worker",
                "-l", "info", "-Q", "report"
            ],
            cwd=str(backend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if sys.platform != 'win32' else None
        )
        print_success(f"Celery Worker 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print_error(f"启动 Celery Worker 失败: {e}")
        return None


def start_fastapi():
    """启动 FastAPI 应用"""
    print_info("启动 FastAPI 应用...")
    
    backend_path = Path(__file__).parent / "1-后端代码"
    if not backend_path.exists():
        print_error(f"后端目录不存在: {backend_path}")
        return None
    
    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "app:app", "--reload",
                "--host", "127.0.0.1", "--port", "5000"
            ],
            cwd=str(backend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if sys.platform != 'win32' else None
        )
        print_success(f"FastAPI 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print_error(f"启动 FastAPI 失败: {e}")
        return None


def verify_system():
    """验证系统就绪"""
    print_info("验证系统就绪...")
    time.sleep(3)  # 等待服务启动
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            print_success("系统已就绪")
            return True
        else:
            print_error(f"系统健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"系统验证失败: {e}")
        return False


def main():
    print_header("仪表盘与报表系统 - 快速启动")
    
    print_info(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("系统：仪表盘、报表、任务管理")
    print_info("组件：FastAPI + Celery + Redis")
    
    # 检查 Redis
    if not check_redis():
        print_warning("Redis 是必需的，请先启动")
        print_info("启动命令：redis-server")
        sys.exit(1)
    
    processes = []
    
    try:
        # 启动 Celery Worker
        print_header("启动 Celery Worker")
        celery_proc = start_celery_worker()
        if celery_proc:
            processes.append(("Celery Worker", celery_proc))
        else:
            print_warning("Celery Worker 启动失败，继续启动 FastAPI...")
        
        # 启动 FastAPI
        print_header("启动 FastAPI 应用")
        fastapi_proc = start_fastapi()
        if fastapi_proc:
            processes.append(("FastAPI", fastapi_proc))
            time.sleep(2)
        else:
            print_error("FastAPI 启动失败")
            sys.exit(1)
        
        # 验证系统
        print_header("验证系统就绪")
        if verify_system():
            print_success("所有服务已启动！")
            
            # 显示访问信息
            print_header("访问信息")
            print(f"{Colors.BOLD}仪表盘：{Colors.ENDC}   http://127.0.0.1:5000/dashboard.html")
            print(f"{Colors.BOLD}报表中心：{Colors.ENDC} http://127.0.0.1:5000/reports.html")
            print(f"{Colors.BOLD}任务中心：{Colors.ENDC} http://127.0.0.1:5000/tasks.html")
            print(f"{Colors.BOLD}API 文档：{Colors.ENDC} http://127.0.0.1:5000/docs")
            
            # 显示验证命令
            print_header("快速验证")
            print(f"运行以下命令验证系统就绪：")
            print(f"  {Colors.BOLD}python bin/verify-dashboard-reports.py{Colors.ENDC}")
            
            # 等待用户中断
            print_header("运行中...")
            print("按 Ctrl+C 停止所有服务")
            print()
            
            # 保持进程运行
            while True:
                time.sleep(1)
        else:
            print_error("系统验证失败")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print_header("关闭服务")
        print_info("正在关闭所有服务...")
        
        for name, proc in processes:
            try:
                if sys.platform == 'win32':
                    os.kill(proc.pid, signal.SIGTERM)
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                print_info(f"{name} 已关闭")
            except Exception as e:
                print_warning(f"关闭 {name} 失败: {e}")
        
        print_success("所有服务已关闭")
        sys.exit(0)
    
    except Exception as e:
        print_error(f"发生错误: {e}")
        
        # 清理进程
        for name, proc in processes:
            try:
                if sys.platform == 'win32':
                    os.kill(proc.pid, signal.SIGTERM)
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except:
                pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
