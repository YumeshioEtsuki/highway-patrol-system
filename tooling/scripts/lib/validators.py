"""
验证和推荐逻辑 - 独立于 UI 实现
支持静态推荐值和 AI 动态生成
"""
import json
from pathlib import Path
from typing import Dict, Optional
from .ai_helper import get_ai_helper


# 静态推荐值（作为 AI 不可用时的备选方案）
STATIC_RECOMMENDATIONS = {
    # 数据库初始化
    "SKIP_DB_INIT": {
        "dev": "0",
        "test": "0",
        "demo": "0",
        "prod": "1",
    },
    
    # 安全模式
    "SECURE_MODE": {
        "dev": "0",
        "test": "0",
        "demo": "0",
        "prod": "1",
    },
    
    # 调试模式
    "DEBUG": {
        "dev": "True",
        "test": "True",
        "demo": "False",
        "prod": "False",
    },
    
    # 日志级别
    "LOG_LEVEL": {
        "dev": "DEBUG",
        "test": "DEBUG",
        "demo": "INFO",
        "prod": "WARNING",
    },
    
    # 管理员密码（应该在部署时设置，不要在配置中显示）
    "DEFAULT_ADMIN_PASSWORD": {
        "dev": "",
        "test": "",
        "demo": "",
        "prod": "",
    },
    
    # 缓存
    "REDIS_CACHE_ENABLED": {
        "dev": "1",
        "test": "1",
        "demo": "1",
        "prod": "1",
    },
}

# AI 推荐值缓存文件路径
AI_CACHE_FILE = Path(__file__).parent.parent / "ai_recommendations_cache.json"


def _load_ai_cache() -> Dict[str, Dict[str, str]]:
    """加载 AI 推荐值缓存"""
    if not AI_CACHE_FILE.exists():
        return {}
    
    try:
        with open(AI_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Cache] 加载缓存失败: {e}")
        return {}


def _save_ai_cache(cache: Dict[str, Dict[str, str]]) -> bool:
    """保存 AI 推荐值到缓存"""
    try:
        AI_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AI_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Cache] 保存缓存失败: {e}")
        return False


def _add_to_ai_cache(key: str, recommendations: Dict[str, str]) -> None:
    """将 AI 推荐值添加到缓存"""
    cache = _load_ai_cache()
    cache[key.upper()] = recommendations
    
    if _save_ai_cache(cache):
        print(f"[Cache] 已缓存 {key.upper()} 的 AI 推荐值")


def get_recommendations(key: str, current_values: Optional[Dict[str, str]] = None, use_ai: bool = True) -> Dict[str, str]:
    """
    根据环境变量键名返回各环境的推荐值
    
    优先级：AI 缓存 > AI 实时生成 > 静态推荐
    
    参数：
        key: 环境变量名称
        current_values: 当前各环境的值（用于 AI 分析）
        use_ai: 是否尝试使用 AI 生成推荐（默认 True）
    
    返回：
        {"dev": "推荐值", "test": "推荐值", "demo": "推荐值", "prod": "推荐值"}
    """
    key_upper = key.upper()
    
    # 1. 优先检查 AI 缓存
    if use_ai:
        ai_cache = _load_ai_cache()
        if key_upper in ai_cache:
            print(f"[Cache] 使用缓存的 AI 推荐值: {key_upper}")
            return ai_cache[key_upper]
    
    # 2. 尝试使用 AI 实时生成推荐
    if use_ai and current_values:
        ai_helper = get_ai_helper()
        if ai_helper.is_available():
            try:
                ai_result = ai_helper.get_env_recommendations(key_upper, current_values)
                if ai_result and "recommendations" in ai_result:
                    recommendations = ai_result["recommendations"]
                    print(f"[AI] 为 {key_upper} 生成推荐值")
                    print(f"[AI] 说明: {ai_result.get('explanation', '')}")
                    
                    # 将 AI 推荐值添加到缓存
                    _add_to_ai_cache(key_upper, recommendations)
                    
                    return recommendations
            except Exception as e:
                print(f"[AI] 生成失败，使用静态推荐: {e}")
    
    # 3. 回退到静态推荐
    return STATIC_RECOMMENDATIONS.get(key_upper, {
        "dev": "",
        "test": "",
        "demo": "",
        "prod": "",
    })


def validate_config(key: str, value: str) -> tuple:
    """
    验证配置值是否合法
    返回 (is_valid, message)
    """
    k = key.upper()
    
    # 布尔型验证
    if k in ("SKIP_DB_INIT", "SECURE_MODE", "REDIS_CACHE_ENABLED"):
        if value not in ("0", "1", "True", "False"):
            return False, f"应为 0/1 或 True/False，收到: {value}"
        return True, "✓"
    
    # DEBUG 验证
    if k == "DEBUG":
        if value not in ("True", "False"):
            return False, f"应为 True/False，收到: {value}"
        return True, "✓"
    
    # LOG_LEVEL 验证
    if k == "LOG_LEVEL":
        valid = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if value not in valid:
            return False, f"应为 {valid}之一，收到: {value}"
        return True, "✓"
    
    # 密码字段验证
    if "PASSWORD" in k:
        if len(value) < 8 and value != "":
            return False, "密码长度应 >= 8 字符，或保持空值由系统生成"
        return True, "✓"
    
    return True, "✓"


def get_help_text(key: str, use_ai: bool = True) -> str:
    """
    获取配置项的帮助文本
    
    参数：
        key: 环境变量名称
        use_ai: 是否尝试使用 AI 生成帮助（默认 True）
    
    返回：
        帮助文本字符串
    """
    # 静态帮助文本（备选方案）
    static_helps = {
        "SKIP_DB_INIT": "是否跳过数据库初始化。0=执行初始化, 1=跳过。生产环境通常设为1，避免重复初始化。",
        "SECURE_MODE": "安全模式。0=从.env读取配置, 1=仅使用系统环境变量。生产推荐启用。",
        "DEBUG": "调试模式。True=开启详细日志, False=关闭。生产必须为False。",
        "LOG_LEVEL": "日志级别。DEBUG(最详细) > INFO > WARNING > ERROR > CRITICAL(最简洁)。",
        "DEFAULT_ADMIN_PASSWORD": "默认管理员密码。留空则自动生成16位随机强密码。",
        "REDIS_CACHE_ENABLED": "是否启用Redis缓存。建议在生产环境启用。",
    }
    
    key_upper = key.upper()
    
    # 尝试使用 AI 生成帮助
    if use_ai:
        ai_helper = get_ai_helper()
        if ai_helper.is_available():
            try:
                ai_help = ai_helper.get_help_text(key_upper)
                if ai_help:
                    print(f"[AI] 为 {key_upper} 生成帮助文档")
                    return ai_help
            except Exception as e:
                print(f"[AI] 生成帮助失败: {e}")
    
    # 回退到静态帮助
    return static_helps.get(key_upper, "暂无帮助信息")


def clear_ai_cache() -> bool:
    """清除所有 AI 推荐值缓存"""
    try:
        if AI_CACHE_FILE.exists():
            AI_CACHE_FILE.unlink()
            print("[Cache] 已清除所有 AI 缓存")
            return True
        return False
    except Exception as e:
        print(f"[Cache] 清除缓存失败: {e}")
        return False


def view_ai_cache() -> Dict[str, Dict[str, str]]:
    """查看当前 AI 推荐值缓存"""
    cache = _load_ai_cache()
    if not cache:
        print("[Cache] 缓存为空")
    else:
        print(f"[Cache] 当前缓存了 {len(cache)} 个环境变量的 AI 推荐值:")
        for key in sorted(cache.keys()):
            print(f"  - {key}")
    return cache


def remove_from_ai_cache(key: str) -> bool:
    """从缓存中移除指定的环境变量"""
    key_upper = key.upper()
    cache = _load_ai_cache()
    
    if key_upper in cache:
        del cache[key_upper]
        if _save_ai_cache(cache):
            print(f"[Cache] 已从缓存中移除 {key_upper}")
            return True
    else:
        print(f"[Cache] 缓存中不存在 {key_upper}")
    
    return False
