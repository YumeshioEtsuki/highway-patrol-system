"""
AI 助手功能测试脚本
"""
import sys
from pathlib import Path

# 添加 lib 到路径
sys.path.insert(0, str(Path(__file__).parent))

from lib import (
    get_ai_helper, 
    get_recommendations, 
    get_help_text,
    view_ai_cache,
    clear_ai_cache,
    remove_from_ai_cache,
)

def test_ai_availability():
    """测试 AI 服务可用性"""
    print("=" * 60)
    print("测试 1: AI 服务可用性")
    print("=" * 60)
    
    ai_helper = get_ai_helper()
    is_available = ai_helper.is_available()
    
    if is_available:
        print("✅ Ollama 服务正常运行")
        print(f"   API URL: {ai_helper.api_url}")
        print(f"   Model: {ai_helper.model}")
    else:
        print("❌ Ollama 服务未运行")
        print("   请确保 Ollama 已启动: ollama serve")
    
    print()
    return is_available


def test_recommendations():
    """测试推荐值生成"""
    print("=" * 60)
    print("测试 2: AI 推荐值生成")
    print("=" * 60)
    
    # 测试用例
    test_key = "DEBUG"
    current_values = {
        "dev": "True",
        "test": "False",
        "demo": "False",
        "prod": "False"
    }
    
    print(f"环境变量: {test_key}")
    print(f"当前值: {current_values}")
    print()
    
    # 使用 AI 生成推荐
    print("正在请求 AI 推荐...")
    recommendations = get_recommendations(test_key, current_values=current_values, use_ai=True)
    
    print(f"推荐值:")
    for env, val in recommendations.items():
        print(f"  {env}: {val}")
    
    print()


def test_help_text():
    """测试帮助文档生成"""
    print("=" * 60)
    print("测试 3: AI 帮助文档生成")
    print("=" * 60)
    
    test_key = "LOG_LEVEL"
    
    print(f"环境变量: {test_key}")
    print()
    print("正在请求 AI 帮助...")
    
    help_text = get_help_text(test_key, use_ai=True)
    
    print("帮助文档:")
    print(help_text)
    print()


def test_static_fallback():
    """测试静态回退"""
    print("=" * 60)
    print("测试 4: 静态值回退（AI 禁用）")
    print("=" * 60)
    
    test_key = "SKIP_DB_INIT"
    
    print(f"环境变量: {test_key}")
    print()
    
    # 禁用 AI
    recommendations = get_recommendations(test_key, use_ai=False)
    
    print("推荐值（静态）:")
    for env, val in recommendations.items():
        print(f"  {env}: {val}")
    
    print()


def test_ai_cache():
    """测试 AI 缓存功能"""
    print("=" * 60)
    print("测试 5: AI 缓存机制")
    print("=" * 60)
    
    # 查看当前缓存
    print("当前缓存状态:")
    view_ai_cache()
    print()
    
    # 测试缓存读取（第二次调用应该更快）
    test_key = "DEBUG"
    current_values = {
        "dev": "True",
        "test": "False",
        "demo": "False",
        "prod": "False"
    }
    
    print(f"第二次查询 {test_key} (应使用缓存):")
    recommendations = get_recommendations(test_key, current_values=current_values, use_ai=True)
    
    print(f"推荐值:")
    for env, val in recommendations.items():
        print(f"  {env}: {val}")
    
    print()


def test_cache_management():
    """测试缓存管理功能"""
    print("=" * 60)
    print("测试 6: 缓存管理")
    print("=" * 60)
    
    print("查看所有缓存:")
    cache = view_ai_cache()
    print()
    
    if cache:
        # 删除一个缓存项
        first_key = list(cache.keys())[0]
        print(f"删除缓存项: {first_key}")
        remove_from_ai_cache(first_key)
        print()
        
        print("删除后的缓存:")
        view_ai_cache()
        print()
    
    print("提示: 使用 clear_ai_cache() 可清除所有缓存")
    print()


if __name__ == "__main__":
    print("\n🤖 AI 助手功能测试\n")
    
    # 测试 AI 可用性
    ai_available = test_ai_availability()
    
    if ai_available:
        # AI 可用，运行完整测试
        test_recommendations()
        test_help_text()
        test_ai_cache()
        test_cache_management()
    else:
        print("⚠️  AI 服务不可用，跳过 AI 测试")
        print()
    
    # 测试静态回退
    test_static_fallback()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    print()
    
    if not ai_available:
        print("💡 提示：")
        print("   1. 安装 Ollama: https://ollama.ai")
        print("   2. 启动服务: ollama serve")
        print("   3. 下载模型: ollama pull qwen:7b")
        print()
    else:
        print("💡 缓存管理命令：")
        print("   from lib import view_ai_cache, clear_ai_cache, remove_from_ai_cache")
        print("   view_ai_cache()      # 查看所有缓存")
        print("   clear_ai_cache()     # 清除所有缓存")
        print("   remove_from_ai_cache('DEBUG')  # 删除指定缓存")
        print()
