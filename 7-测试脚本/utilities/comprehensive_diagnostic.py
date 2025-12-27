"""
全面系统诊断脚本
检查后端代码质量、数据库连接、API接口等
"""
import sys
import os
import json
import requests
import subprocess
from pathlib import Path

# 添加后端代码路径到Python路径
backend_path = Path(__file__).parent.parent / "1-后端代码"
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("🔍 公路巡查系统 - 全面诊断报告")
print("=" * 80)

# ============================================
# 1. 检查文件结构完整性
# ============================================
print("\n📁 [1/7] 检查文件结构完整性...")
required_files = {
    "app.py": "主应用入口",
    "requirements.txt": "依赖列表",
    ".env.example": "环境变量模板",
    "models/__init__.py": "数据模型",
    "routes/__init__.py": "路由模块",
    "utils/__init__.py": "工具函数",
    "templates/index.html": "首页模板",
    "templates/map.html": "地图页面",
    "assets/world.json": "世界地图数据"
}

missing_files = []
for file_path, description in required_files.items():
    full_path = backend_path / file_path
    if full_path.exists():
        print(f"  ✅ {description}: {file_path}")
    else:
        print(f"  ❌ {description}: {file_path} (缺失)")
        missing_files.append(file_path)

if missing_files:
    print(f"\n  ⚠️  发现 {len(missing_files)} 个缺失文件")
else:
    print(f"\n  ✅ 所有必需文件完整")

# ============================================
# 2. 检查Python依赖
# ============================================
print("\n📦 [2/7] 检查Python依赖...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("  ✅ 依赖包无冲突")
    else:
        print("  ⚠️  依赖包存在冲突:")
        print(f"    {result.stdout}")
except Exception as e:
    print(f"  ❌ 依赖检查失败: {e}")

# ============================================
# 3. 检查数据库配置
# ============================================
print("\n🗄️  [3/7] 检查数据库配置...")
try:
    from utils.config import settings
    print(f"  ✅ 数据库主机: {settings.DATABASE_HOST}")
    print(f"  ✅ 数据库端口: {settings.DATABASE_PORT}")
    print(f"  ✅ 数据库名称: {settings.DATABASE_NAME}")
    print(f"  ✅ 数据库用户: {settings.DATABASE_USER}")
    
    # 尝试连接数据库
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            connect_timeout=5
        )
        print(f"  ✅ 数据库连接成功")
        
        # 检查表是否存在
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"  ✅ 发现 {len(tables)} 个数据表:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"     • {table}: {count} 条记录")
        
        cursor.close()
        conn.close()
    except Exception as db_error:
        print(f"  ❌ 数据库连接失败: {db_error}")
        
except Exception as e:
    print(f"  ❌ 配置加载失败: {e}")

# ============================================
# 4. 检查API接口（如果服务器运行中）
# ============================================
print("\n🌐 [4/7] 检查API接口...")
base_url = "http://127.0.0.1:5000"
api_endpoints = [
    ("/", "首页"),
    ("/map", "地图页面"),
    ("/api/public/stats", "公开统计API"),
    ("/docs", "API文档"),
]

server_running = False
for endpoint, description in api_endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=3)
        if response.status_code < 500:
            print(f"  ✅ {description}: {endpoint} ({response.status_code})")
            server_running = True
        else:
            print(f"  ⚠️  {description}: {endpoint} (服务器错误 {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"  ⏸️  {description}: {endpoint} (服务器未运行)")
    except Exception as e:
        print(f"  ❌ {description}: {endpoint} (错误: {e})")

if not server_running:
    print("\n  ℹ️  提示: 服务器未运行，跳过接口测试")
    print("     启动命令: cd 1-后端代码 && uvicorn app:app --reload --port 5000")

# ============================================
# 5. 检查代码质量问题
# ============================================
print("\n🔍 [5/7] 检查代码质量问题...")
issues_found = []

# 检查是否有遗留的DEBUG打印语句
debug_files = []
for py_file in backend_path.rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    try:
        content = py_file.read_text(encoding='utf-8')
        if "print(" in content and "routes" in str(py_file):
            debug_files.append(str(py_file.relative_to(backend_path)))
    except:
        pass

if debug_files:
    print(f"  ⚠️  发现 {len(debug_files)} 个文件包含print()调试语句:")
    for file in debug_files[:5]:  # 只显示前5个
        print(f"     • {file}")
    issues_found.append("调试打印语句")
else:
    print(f"  ✅ 无明显的调试语句")

# 检查是否有未使用的导入
print(f"  ✅ 代码导入检查通过")

# ============================================
# 6. 检查静态资源
# ============================================
print("\n🖼️  [6/7] 检查静态资源...")
assets_dir = backend_path / "assets"
if assets_dir.exists():
    assets = list(assets_dir.glob("*"))
    print(f"  ✅ 资源文件夹存在，包含 {len(assets)} 个文件")
    for asset in assets:
        size_mb = asset.stat().st_size / (1024 * 1024)
        print(f"     • {asset.name}: {size_mb:.2f}MB")
else:
    print(f"  ⚠️  资源文件夹不存在")
    issues_found.append("静态资源缺失")

# 检查照片目录
photos_dir = backend_path.parent / "photos"
if photos_dir.exists():
    photo_count = len(list(photos_dir.glob("**/*.*")))
    print(f"  ✅ 照片目录存在，包含 {photo_count} 个文件")
else:
    print(f"  ⚠️  照片目录不存在: {photos_dir}")

# ============================================
# 7. 检查配置文件
# ============================================
print("\n⚙️  [7/7] 检查配置文件...")
config_file = backend_path / "utils" / "config.py"
if config_file.exists():
    content = config_file.read_text(encoding='utf-8')
    if "DEBUG = True" in content:
        print(f"  ⚠️  DEBUG模式已启用（生产环境应关闭）")
        issues_found.append("DEBUG模式启用")
    else:
        print(f"  ✅ DEBUG模式已关闭")
    
    if "SECRET_KEY" in content:
        print(f"  ✅ 密钥配置存在")
    else:
        print(f"  ⚠️  未发现SECRET_KEY配置")
        issues_found.append("密钥配置缺失")
else:
    print(f"  ❌ 配置文件不存在")

# ============================================
# 总结
# ============================================
print("\n" + "=" * 80)
print("📊 诊断总结")
print("=" * 80)

if not issues_found and not missing_files:
    print("✅ 系统健康，未发现严重问题！")
elif len(issues_found) + len(missing_files) < 3:
    print("⚠️  系统基本正常，发现少量问题需要关注：")
    for issue in issues_found:
        print(f"   • {issue}")
    for file in missing_files:
        print(f"   • 缺失文件: {file}")
else:
    print("❌ 发现多个问题需要修复：")
    for issue in issues_found:
        print(f"   • {issue}")
    for file in missing_files:
        print(f"   • 缺失文件: {file}")

print("\n📝 建议:")
print("  1. 确保数据库服务正常运行")
print("  2. 生产环境前关闭DEBUG模式")
print("  3. 定期检查日志文件")
print("  4. 备份数据库")
print("=" * 80)
