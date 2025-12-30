"""
项目结构验证脚本
验证所有关键文件和目录是否已正确迁移
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

def verify_structure():
    """验证项目结构"""
    print("\n" + "="*50)
    print("  PROJECT STRUCTURE VERIFICATION")
    print("="*50 + "\n")
    
    checks = []
    
    # 1. 检查核心目录
    required_dirs = [
        "src", "miniprogram", "database", "docs", "tests",
        "scripts", "assets", "bin", "tooling", "logs"
    ]
    
    print("📁 Checking main directories...")
    for dir_name in required_dirs:
        dir_path = ROOT / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        checks.append(exists)
        status = "✓" if exists else "✗"
        color = "\033[92m" if exists else "\033[91m"
        print(f"  {color}{status}\033[0m {dir_name}/")
    
    # 2. 检查根目录清洁度
    print("\n📄 Checking root directory cleanliness...")
    root_files = list(ROOT.glob("*"))
    file_count = len([f for f in root_files if f.is_file()])
    clean = file_count <= 10
    checks.append(clean)
    status = "✓" if clean else "✗"
    color = "\033[92m" if clean else "\033[91m"
    print(f"  {color}{status}\033[0m Root files: {file_count} (target: ≤10)")
    
    # 3. 检查关键文件
    print("\n🔧 Checking critical files...")
    critical_files = [
        "README.md",
        ".env.example",
        ".gitignore",
        "PROJECT_STRUCTURE.md",
        "src/app.py",
        "src/settings.py",
        "database/00_init_schema.sql",
        "bin/startup.bat",
    ]
    
    for file_path in critical_files:
        full_path = ROOT / file_path
        exists = full_path.exists() and full_path.is_file()
        checks.append(exists)
        status = "✓" if exists else "✗"
        color = "\033[92m" if exists else "\033[91m"
        print(f"  {color}{status}\033[0m {file_path}")
    
    # 4. 检查旧目录是否已清理
    print("\n🗑️  Checking old directories removed...")
    old_dirs = [
        "1-后端代码", "2-小程序代码", "3-数据库",
        "4-文档", "5-演示材料", "6-开发日志", "7-测试脚本",
        "00-项目管理"
    ]
    
    for old_dir in old_dirs:
        dir_path = ROOT / old_dir
        removed = not dir_path.exists()
        checks.append(removed)
        status = "✓" if removed else "✗"
        color = "\033[92m" if removed else "\033[91m"
        print(f"  {color}{status}\033[0m {old_dir}/ removed")
    
    # 5. 检查脚本路径引用
    print("\n📝 Checking script path references...")
    startup_bat = ROOT / "bin" / "startup.bat"
    if startup_bat.exists():
        content = startup_bat.read_text(encoding="utf-8", errors="ignore")
        has_old_path = "1-后端代码" in content or "1-後端代碼" in content
        has_new_path = "src\\" in content or "src/" in content
        updated = not has_old_path and has_new_path
        checks.append(updated)
        status = "✓" if updated else "✗"
        color = "\033[92m" if updated else "\033[91m"
        print(f"  {color}{status}\033[0m bin/startup.bat paths updated")
    else:
        checks.append(False)
        print(f"  \033[91m✗\033[0m bin/startup.bat not found")
    
    # 总结
    print("\n" + "="*50)
    passed = sum(checks)
    total = len(checks)
    success = passed == total
    
    if success:
        print(f"\033[92m✓ ALL CHECKS PASSED ({passed}/{total})\033[0m")
        print("  Project structure refactoring completed successfully!")
    else:
        print(f"\033[91m✗ SOME CHECKS FAILED ({passed}/{total})\033[0m")
        print("  Please review the failed items above.")
    
    print("="*50 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(verify_structure())
