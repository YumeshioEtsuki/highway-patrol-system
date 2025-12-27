#!/usr/bin/env python3
"""
🚀 快速启动脚本 - 一键启动开发环境

用法：
    python quick_start.py                      # 启动后端
    python quick_start.py --with-celery        # 启动后端 + Celery worker + beat
    python quick_start.py --debug              # 启动 + 诊断
    python quick_start.py --reset              # 重建数据库
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List

# 在 Windows 控制台避免 GBK 编码报错，强制使用 UTF-8 并替换无法编码的字符
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  🚀 公路巡查系统 - 快速启动                             ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def reset_database():
    """重建数据库（仅执行 scripts/reset_db.py）"""
    print("\n[1/1] 正在初始化数据库...")
    try:
        subprocess.run([
            sys.executable,
            '1-后端代码/scripts/reset_db.py'
        ], check=True)
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def run_diagnostics():
    """运行诊断"""
    print("\n" + "="*60)
    print("🔍 运行网络连接诊断...")
    print("="*60 + "\n")
    try:
        subprocess.run([
            sys.executable,
            'scripts/MOBILE_DEBUG_GUIDE.py'
        ], check=False)
    except Exception as e:
        print(f"诊断失败: {e}")

def _check_port_in_use(port: int) -> bool:
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def _kill_process_on_port(port: int) -> bool:
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
                        print(f"[INFO] 尝试结束进程 {pid}...")
                        # 先尝试 /F /PID
                        result = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        if result.returncode != 0:
                            # 若 /PID 失败，尝试通过 /IM 按镜像名杀死
                            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
                        return True
        return False
    except Exception as e:
        print(f"[WARN] 端口清理异常: {e}")
        return False

def start_backend(skip_db_init: bool = False):
    """启动后端服务，自动清理端口并可选跳过DB初始化"""
    print("\n" + "="*60)
    print("🖥️  启动后端服务...")
    print("="*60)
    print("""
⚠️  确保以下条件已满足：
    ✓ MySQL 服务已启动
    ✓ Redis 服务已启动（若启用 Celery）
    ✓ 数据库已初始化（首次运行请用 --reset）
    
📝 快捷键：
    Ctrl+C 停止服务
    
📖 访问地址：
    API 文档: http://127.0.0.1:5000/docs
    应用首页: http://127.0.0.1:5000
    """)

    backend_dir = Path('1-后端代码')

    # 清理占用端口
    PORT = 5000
    if _check_port_in_use(PORT):
        print(f"[WARN] 端口 {PORT} 已被占用，尝试自动清理...")
        import time
        
        # 尝试多次清理
        for attempt in range(1, 4):
            if _kill_process_on_port(PORT):
                time.sleep(2)  # 等待进程彻底关闭
                if not _check_port_in_use(PORT):
                    print(f"[OK] 端口 {PORT} 已释放")
                    break
            elif attempt < 3:
                print(f"[INFO] 清理第 {attempt} 次失败，2秒后重试...")
                time.sleep(2)
        
        # 若仍未清理成功
        if _check_port_in_use(PORT):
            print(f"[ERROR] 无法自动清理端口 {PORT}")
            print(f"\n💡 请手动清理：")
            print(f"   1. 打开 PowerShell（管理员）")
            print(f"   2. 运行以下命令：")
            print(f"      netstat -ano | findstr :5000")
            print(f"      taskkill /F /IM python.exe")
            print(f"   3. 或关闭 VS Code 以释放所有 Python 进程")
            print(f"   4. 然后重新运行 quick_start.py")
            return

    env = os.environ.copy()
    if skip_db_init:
        env['SKIP_DB_INIT'] = '1'

    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app:app',
            '--host', '0.0.0.0',
            '--port', str(PORT),
            '--reload'
        ], cwd=backend_dir, env=env)
    except KeyboardInterrupt:
        print("\n\n👋 后端服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 尝试：")
        print("   1. 检查 MySQL 是否运行")
        print("   2. 运行 python quick_start.py --reset 重建数据库")
        print("   3. 查看 docs/SETUP.md")


def start_celery_processes(backend_dir: Path, queues: str = "photo,ai,report,maintenance") -> List[subprocess.Popen]:
    """启动 Celery worker 与 beat，返回进程列表"""
    procs: List[subprocess.Popen] = []
    try:
        worker = subprocess.Popen([
            sys.executable, "-m", "celery",
            "-A", "celery_app",
            "worker",
            "--loglevel", "info",
            "--pool", "solo",
            "-Q", queues
        ], cwd=backend_dir)
        procs.append(worker)
        beat = subprocess.Popen([
            sys.executable, "-m", "celery",
            "-A", "celery_app",
            "beat",
            "--loglevel", "info"
        ], cwd=backend_dir)
        procs.append(beat)
        print(f"[OK] Celery worker + beat 已启动 (队列: {queues})")
    except Exception as e:
        print(f"[WARN] 启动 Celery 失败: {e}")
    return procs

def main():
    print_banner()
    
    # 解析命令行参数
    if '--reset' in sys.argv:
        if reset_database():
            print("\n✅ 环境已准备就绪！现在可以启动后端")
            print("   运行: python quick_start.py")
        return
    
    if '--debug' in sys.argv:
        run_diagnostics()
        return

    # 可选：启动前应用索引（统一使用 3-数据库/02_indexes.sql）
    if '--apply-indexes' in sys.argv:
        try:
            backend_dir = Path('1-后端代码').resolve()
            idx_path = Path.cwd() / '3-数据库' / '02_indexes.sql'
            if idx_path.exists():
                # 将后端目录加入 sys.path，调用 execute_sql_file
                sys.path.insert(0, str(backend_dir))
                from utils.utils import execute_sql_file
                print(f"[INFO] 应用索引脚本: {idx_path}")
                ok = execute_sql_file(str(idx_path), skip_read_only_queries=True, print_query_results=False, stop_on_error=False)
                print("[OK] 索引脚本执行完成" if ok else "[WARN] 索引脚本执行部分失败")
            else:
                print(f"[WARN] 未找到索引脚本: {idx_path}")
        except Exception as e:
            print(f"[WARN] 索引脚本执行失败: {e}")
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
使用方法:
    python quick_start.py                      # 启动后端服务
    python quick_start.py --with-celery        # 启动后端 + Celery worker + beat
    python quick_start.py --reset              # 重建数据库
    python quick_start.py --apply-indexes      # 启动前应用索引
    python quick_start.py --skip-db-init       # 跳过数据库初始化
    python quick_start.py --debug              # 运行网络诊断
    python quick_start.py --help               # 显示此帮助

第一次使用流程:
    1. python quick_start.py --reset            # 初始化
    2. python quick_start.py --apply-indexes    # 可选：索引优化
    3. python quick_start.py                    # 启动后端
    3. 在小程序中测试登录

真机连接故障:
    1. python quick_start.py --debug        # 诊断
    2. 按照诊断结果修改配置
    3. 参考 docs/MOBILE_TESTING.md 详细指南
        """)
        return
    
    # 默认：启动后端
    # 解析是否跳过DB初始化
    skip = '--skip-db-init' in sys.argv
    with_celery = '--with-celery' in sys.argv

    backend_dir = Path('1-后端代码')
    procs = []
    if with_celery:
        procs = start_celery_processes(backend_dir)

    try:
        start_backend(skip_db_init=skip)
    finally:
        # 退出时清理 Celery 进程
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass

if __name__ == '__main__':
    main()
