"""
验证和推荐逻辑 - 独立于 UI 实现
"""
from typing import Dict


def get_recommendations(key: str) -> Dict[str, str]:
    """根据环境变量键名返回各环境的推荐值"""
    
    recommendations = {
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
    
    key_upper = key.upper()
    return recommendations.get(key_upper, {
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


def get_help_text(key: str) -> str:
    """获取配置项的帮助文本"""
    helps = {
        "SKIP_DB_INIT": "是否跳过数据库初始化。0=执行初始化, 1=跳过。生产环境通常设为1，避免重复初始化。",
        "SECURE_MODE": "安全模式。0=从.env读取配置, 1=仅使用系统环境变量。生产推荐启用。",
        "DEBUG": "调试模式。True=开启详细日志, False=关闭。生产必须为False。",
        "LOG_LEVEL": "日志级别。DEBUG(最详细) > INFO > WARNING > ERROR > CRITICAL(最简洁)。",
        "DEFAULT_ADMIN_PASSWORD": "默认管理员密码。留空则自动生成16位随机强密码。",
        "REDIS_CACHE_ENABLED": "是否启用Redis缓存。建议在生产环境启用。",
    }
    return helps.get(key.upper(), "暂无帮助信息")
