# logger.py
"""
统一日志系统
提供结构化日志输出，替代print()调试语句
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# 创建日志目录
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, level=logging.INFO):
    """
    创建并配置日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
        level: 日志级别
    
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 控制台处理器（彩色输出）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（保存到日志文件）
    try:
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ 日志文件写入失败: {e}，仅使用控制台输出")
    
    return logger


# 创建默认的应用日志记录器
app_logger = setup_logger("app")

# 便捷函数
def log_info(message: str, logger_name: str = "app"):
    """记录信息日志"""
    logger = logging.getLogger(logger_name)
    logger.info(message)

def log_error(message: str, exc_info=False, logger_name: str = "app"):
    """记录错误日志"""
    logger = logging.getLogger(logger_name)
    logger.error(message, exc_info=exc_info)

def log_warning(message: str, logger_name: str = "app"):
    """记录警告日志"""
    logger = logging.getLogger(logger_name)
    logger.warning(message)

def log_debug(message: str, logger_name: str = "app"):
    """记录调试日志"""
    logger = logging.getLogger(logger_name)
    logger.debug(message)
