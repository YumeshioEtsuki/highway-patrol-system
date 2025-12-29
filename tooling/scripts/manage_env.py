#!/usr/bin/env python3
"""
🎨 环境变量管理工具 - 可视化CLI
用于方便地添加、查看、修改环境变量配置，并基于环境变量的语义给出分组建议。

用法: python manage_env.py
"""
import sys
import re
import json
from pathlib import Path
from add_config import add_config_to_file, TOOLING_ENV, ENV_EXAMPLE, MAPPING

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_menu(options):
    """打印菜单"""
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print(f"  0. 退出")
    print()

def view_config(file_path: Path):
    """查看配置文件内容"""
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        content = file_path.read_text(encoding="utf-8")
        print(f"\n📄 {file_path.name} 内容:\n")
        print("-" * 60)
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip():
                print(f"{i:3d}: {line}")
        print("-" * 60)
    except Exception as e:
        print(f"❌ 读取失败: {e}")

def add_new_config():
    """交互式添加新配置"""
    print_header("添加新配置")
    
    # 获取键名
    key = input("  📝 输入配置键名（如: DEFAULT_ADMIN_PASSWORD）: ").strip()
    if not key:
        print("❌ 键名不能为空")
        return
    
    # 获取值
    value = input(f"  📝 输入 {key} 的值（回车留空）: ").strip()
    
    # 获取注释
    comment = input("  📝 输入注释说明（可选，回车跳过）: ").strip()
    
    # 选择环境
    print("\n  🌍 选择要添加的环境:")
    environments = ["dev", "test", "demo", "prod"]
    for i, env in enumerate(environments, 1):
        print(f"    {i}. {env}")
    print(f"    0. 全选")
    
    choice = input("\n  输入选项（多个用逗号分隔，如: 1,2,3）: ").strip()
    
    if choice == "0":
        selected_envs = environments
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            selected_envs = [environments[i] for i in indices if 0 <= i < len(environments)]
        except (ValueError, IndexError):
            print("❌ 输入格式错误")
            return
    
    if not selected_envs:
        print("❌ 未选择任何环境")
        return
    
    # 确认
    print(f"\n  ✅ 确认信息:")
    print(f"     键名: {key}")
    print(f"     值: {value if value else '(空)'}")
    print(f"     注释: {comment if comment else '(无)'}")
    print(f"     环境: {', '.join(selected_envs)}")
    confirm = input("\n  是否继续？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 更新 .env.example
    print(f"\n  ⏳ 正在更新...\n")
    updated = 0
    
    if add_config_to_file(ENV_EXAMPLE, key, "", comment or f"配置: {key}"):
        print(f"  ✅ .env.example 已更新")
        updated += 1
    else:
        print(f"  ⚠️  .env.example 未更新或已存在 {key}")
    
    # 更新各环境文件
    for env in selected_envs:
        file_path = TOOLING_ENV / MAPPING[env]
        if add_config_to_file(file_path, key, value, comment):
            print(f"  ✅ {env:6} 已更新")
            updated += 1
        else:
            print(f"  ⚠️  {env:6} 未更新或已存在 {key}")
    
    if updated > 0:
        print(f"\n  ✅ 成功更新 {updated} 个文件")
    else:
        print(f"\n  ❌ 没有文件被更新")


def recommend_groups_for_key(key: str):
    """内置启发式：根据键名给出各环境的推荐值"""
    k = key.strip().upper()
    if k == "SKIP_DB_INIT":
        return {"dev": "0", "test": "0", "demo": "0", "prod": "1"}
    if k == "SECURE_MODE":
        return {"dev": "0", "test": "0", "demo": "0", "prod": "1"}
    if k == "BOOTSTRAP_ADMIN":
        return {"dev": "0", "test": "0", "demo": "0", "prod": "0"}
    if k == "DEBUG":
        return {"dev": "True", "test": "True", "demo": "True", "prod": "False"}
    if k == "DEFAULT_ADMIN_PASSWORD":
        # 生产建议留空，开发/测试给出默认口令（可被覆盖）
        return {"dev": "MIMASHI123", "test": "MIMASHI123", "demo": "MIMASHI123", "prod": ""}
    # 默认：不做强建议，全部留空
    return {"dev": "", "test": "", "demo": "", "prod": ""}


def try_ai_suggest(key: str, current_values: dict):
    """可选AI建议：通过 ENV_AI_SUGGEST_URL 调用外部服务，失败则返回None"""
    import os
    url = os.getenv("ENV_AI_SUGGEST_URL")
    if not url:
        return None
    payload = {"key": key, "current": current_values}
    try:
        import urllib.request
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, dict) and all(e in data for e in ("dev","test","demo","prod")):
                return data
    except Exception:
        return None
    return None


def edit_by_group_suggestion():
    """按分组建议一键批量修改"""
    print_header("分组建议与批量应用")
    key = input("  📝 目标键名（如: SKIP_DB_INIT/DEBUG/SECURE_MODE）: ").strip()
    if not key:
        print("❌ 键名不能为空")
        return

    # 收集当前值
    current = {}
    files = {
        "dev": TOOLING_ENV / MAPPING["dev"],
        "test": TOOLING_ENV / MAPPING["test"],
        "demo": TOOLING_ENV / MAPPING["demo"],
        "prod": TOOLING_ENV / MAPPING["prod"],
    }
    for env_name, path in files.items():
        val = "(未配置)"
        if path.exists():
            content = path.read_text(encoding="utf-8")
            m = re.search(rf"^{re.escape(key)}=(.*)$", content, re.MULTILINE)
            if m:
                val = m.group(1)
        current[env_name] = val

    # 推荐值（AI优先，失败则启发式）
    ai = try_ai_suggest(key, current)
    rec = ai if ai else recommend_groups_for_key(key)

    print("\n  📋 当前值 vs 推荐值:")
    for env in ("dev","test","demo","prod"):
        print(f"    {env:4} 当前={current.get(env)} \t→ 推荐={rec.get(env)}")

    # 选择要应用的环境
    print("\n  🌍 选择要应用推荐值的环境: 1=dev, 2=test, 3=demo, 4=prod, 0=全选")
    choice = input("  输入选项（如: 1,4 或 0）: ").strip()
    if choice == "0":
        selected = ["dev","test","demo","prod"]
    else:
        try:
            idxs = [int(x.strip()) for x in choice.split(",")]
            map_idx = {1:"dev",2:"test",3:"demo",4:"prod"}
            selected = [map_idx[i] for i in idxs if i in map_idx]
        except Exception:
            print("❌ 输入格式错误")
            return
    if not selected:
        print("❌ 未选择任何环境")
        return

    # 执行更新
    print("\n  ⏳ 正在应用推荐值...\n")
    updated = 0
    for env in selected:
        path = files[env]
        if not path.exists():
            print(f"  ⚠️  文件不存在: {path}")
            continue
        content = path.read_text(encoding="utf-8")
        if re.search(rf"^{re.escape(key)}=", content, re.MULTILINE):
            new_content = re.sub(rf"^{re.escape(key)}=.*$", f"{key}={rec.get(env,'')}", content, flags=re.MULTILINE)
        else:
            new_content = content + f"\n{key}={rec.get(env,'')}\n"
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            print(f"  ✅ {env:4} -> {key}={rec.get(env,'')}")
            updated += 1
        else:
            print(f"  ℹ️  {env:4} 无需更新")

    if updated:
        print(f"\n  ✅ 已更新 {updated} 个环境文件")
    else:
        print("\n  ❌ 没有文件被更新")

def edit_existing_config():
    """编辑现有配置"""
    print_header("编辑现有配置")
    
    # 获取要编辑的键名
    key = input("  📝 输入要编辑的配置键名（如: SKIP_DB_INIT）: ").strip()
    if not key:
        print("❌ 键名不能为空")
        return
    
    # 搜索包含该键的所有文件
    print(f"\n  🔍 搜索包含 {key} 的文件...\n")
    
    files_to_edit = []
    
    # 检查 .env.example
    if ENV_EXAMPLE.exists():
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
        if f"{key}=" in content:
            files_to_edit.append(("模板", ENV_EXAMPLE, content))
    
    # 检查所有环境文件
    for env_name, file_name in MAPPING.items():
        file_path = TOOLING_ENV / file_name
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            if f"{key}=" in content:
                files_to_edit.append((env_name, file_path, content))
    
    if not files_to_edit:
        print(f"❌ 未找到包含 {key} 的文件")
        return
    
    # 显示当前值
    print(f"  ✅ 找到 {len(files_to_edit)} 个文件包含 {key}:\n")
    for i, (name, path, content) in enumerate(files_to_edit, 1):
        # 提取当前值
        match = re.search(rf"^{re.escape(key)}=(.*)$", content, re.MULTILINE)
        current_value = match.group(1) if match else "(未找到)"
        print(f"    {i}. {name:8} ({path.name:20}) = {current_value}")
    
    # 获取新值
    print()
    new_value = input(f"  📝 输入 {key} 的新值: ").strip()
    
    # 确认
    print(f"\n  ✅ 将更新:")
    print(f"     配置键: {key}")
    print(f"     新值: {new_value}")
    print(f"     文件数: {len(files_to_edit)}")
    confirm = input("\n  是否继续？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 执行更新
    print(f"\n  ⏳ 正在更新...\n")
    updated = 0
    
    for name, file_path, content in files_to_edit:
        try:
            # 使用正则表达式替换
            new_content = re.sub(
                rf"^{re.escape(key)}=.*$",
                f"{key}={new_value}",
                content,
                flags=re.MULTILINE
            )
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                # 提取新旧值用于显示
                old_match = re.search(rf"^{re.escape(key)}=(.*)$", content, re.MULTILINE)
                old_value = old_match.group(1) if old_match else "(未找到)"
                print(f"  ✅ {name:8} {old_value:20} → {new_value}")
                updated += 1
            else:
                print(f"  ⚠️  {name:8} 无需更新")
        except Exception as e:
            print(f"  ❌ {name:8} 更新失败: {e}")
    
    if updated > 0:
        print(f"\n  ✅ 成功更新 {updated} 个文件")
    else:
        print(f"\n  ❌ 没有文件被更新")

def view_all_configs():
    """查看所有配置文件"""
    print_header("查看所有配置")
    
    files_to_view = [
        ("模板", ENV_EXAMPLE),
        *[(env, TOOLING_ENV / MAPPING[env]) for env in MAPPING.keys()]
    ]
    
    for i, (name, path) in enumerate(files_to_view, 1):
        print(f"  {i}. {name}")
    print(f"  0. 返回菜单")
    
    choice = input("\n  选择要查看的文件: ").strip()
    
    try:
        idx = int(choice)
        if idx == 0:
            return
        if 1 <= idx <= len(files_to_view):
            view_config(files_to_view[idx-1][1])
            input("\n  按 Enter 继续...")
        else:
            print("❌ 选择无效")
    except ValueError:
        print("❌ 输入格式错误")

def view_config_summary():
    """查看配置摘要"""
    print_header("配置摘要")
    
    files_info = [
        ("根目录模板", ENV_EXAMPLE),
        ("开发环境", TOOLING_ENV / MAPPING["dev"]),
        ("测试环境", TOOLING_ENV / MAPPING["test"]),
        ("演示环境", TOOLING_ENV / MAPPING["demo"]),
        ("生产环境", TOOLING_ENV / MAPPING["prod"]),
    ]
    
    for name, path in files_info:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            config_count = len([l for l in content.split('\n') if '=' in l and not l.strip().startswith('#')])
            print(f"  ✅ {name:12} - {config_count:2d} 项配置  ({path.name})")
        else:
            print(f"  ❌ {name:12} - 文件不存在")
    
    input("\n  按 Enter 继续...")

def main():
    """主菜单"""
    while True:
        print_header("🎨 环境变量管理工具")
        print("  快速管理项目的环境变量配置文件")
        print()
        print_menu([
            "添加新配置",
            "编辑现有配置",
            "分组建议与批量应用",
            "查看所有配置",
            "配置摘要",
        ])
        
        choice = input("  请选择: ").strip()
        
        if choice == "0":
            print("\n  👋 再见！\n")
            sys.exit(0)
        elif choice == "1":
            add_new_config()
        elif choice == "2":
            edit_existing_config()
        elif choice == "3":
            edit_by_group_suggestion()
        elif choice == "4":
            view_all_configs()
        elif choice == "5":
            view_config_summary()
        else:
            print("❌ 选择无效，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  👋 已中断\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ 发生错误: {e}\n")
        sys.exit(1)

