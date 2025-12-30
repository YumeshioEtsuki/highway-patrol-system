"""
依赖项检查 - 在应用启动时验证外部服务可用性
用于识别缺失的关键依赖并提供友好的错误提示
"""

import httpx
import asyncio
from core.logger import setup_logger

logger = setup_logger(__name__)


class DependencyChecker:
    """依赖项检查器"""
    
    @staticmethod
    async def check_ollama(host: str = "127.0.0.1", port: int = 11434, timeout: int = 5) -> dict:
        """
        检查 Ollama 服务
        
        返回:
            {
                "available": bool,
                "status": "ok" | "warning" | "error",
                "message": str,
                "models": list
            }
        """
        ollama_url = f"http://{host}:{port}/api/tags"
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(ollama_url)
                
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get('name') for m in data.get('models', [])]
                    
                    return {
                        "available": True,
                        "status": "ok",
                        "message": f"Ollama 服务就绪（{len(models)} 个模型）",
                        "models": models
                    }
                else:
                    return {
                        "available": False,
                        "status": "error",
                        "message": f"Ollama 服务异常 (HTTP {response.status_code})",
                        "models": []
                    }
        except httpx.ConnectError:
            return {
                "available": False,
                "status": "error",
                "message": f"无法连接 Ollama ({host}:{port}) - 服务未启动",
                "models": []
            }
        except asyncio.TimeoutError:
            return {
                "available": False,
                "status": "error",
                "message": f"Ollama 连接超时 ({timeout}s)",
                "models": []
            }
        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "message": f"检查失败: {str(e)}",
                "models": []
            }
    
    @staticmethod
    async def check_redis(host: str = "localhost", port: int = 6379, timeout: int = 5) -> dict:
        """
        检查 Redis 服务
        
        返回:
            {
                "available": bool,
                "status": "ok" | "warning" | "error",
                "message": str
            }
        """
        try:
            # 尝试通过 http 检查（如果 redis 容器有 HTTP 接口）
            # 或者通过导入 redis 库检查
            try:
                import redis
                r = redis.Redis(host=host, port=port, socket_connect_timeout=timeout)
                r.ping()
                
                return {
                    "available": True,
                    "status": "ok",
                    "message": f"Redis 已连接 ({host}:{port})"
                }
            except Exception:
                return {
                    "available": False,
                    "status": "warning",
                    "message": f"Redis 连接失败 ({host}:{port}) - 缓存功能不可用，将使用内存缓存"
                }
        except Exception as e:
            return {
                "available": False,
                "status": "warning",
                "message": f"Redis 检查失败: {str(e)} - 将使用内存缓存"
            }
    
    @staticmethod
    async def check_database(
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "test",
        timeout: int = 5
    ) -> dict:
        """
        检查数据库连接
        
        返回:
            {
                "available": bool,
                "status": "ok" | "error",
                "message": str
            }
        """
        try:
            import mysql.connector
            
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                connection_timeout=timeout
            )
            conn.close()
            
            return {
                "available": True,
                "status": "ok",
                "message": f"数据库已连接 ({user}@{host}:{port}/{database})"
            }
        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "message": f"数据库连接失败: {str(e)}"
            }
    
    @staticmethod
    async def run_startup_checks(config: dict = None) -> dict:
        """
        运行所有启动检查
        
        参数:
            config: 依赖项配置
        {
            "ollama": {"host": "127.0.0.1", "port": 11434},
            "redis": {"host": "localhost", "port": 6379},
            "database": {"host": "localhost", "port": 3306, "user": "root", "password": ""}
        }
        
        返回:
            {
                "all_critical_available": bool,
                "checks": {
                    "ollama": {...},
                    "redis": {...},
                    "database": {...}
                }
            }
        """
        config = config or {}
        checks = {}
        
        # 检查 Ollama（可选）
        if config.get("check_ollama", True):
            ollama_config = config.get("ollama", {})
            checks["ollama"] = await DependencyChecker.check_ollama(
                host=ollama_config.get("host", "127.0.0.1"),
                port=ollama_config.get("port", 11434)
            )
            logger.info(f"Ollama 检查: {checks['ollama']['message']}")
        
        # 检查 Redis（可选）
        if config.get("check_redis", True):
            redis_config = config.get("redis", {})
            checks["redis"] = await DependencyChecker.check_redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379)
            )
            logger.info(f"Redis 检查: {checks['redis']['message']}")
        
        # 检查数据库（关键）
        if config.get("check_database", True):
            db_config = config.get("database", {})
            checks["database"] = await DependencyChecker.check_database(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 3306),
                user=db_config.get("user", "root"),
                password=db_config.get("password", ""),
                database=db_config.get("database", "road_patrol_db")
            )
            logger.info(f"数据库检查: {checks['database']['message']}")
        
        # 判断关键依赖是否可用
        all_critical_available = checks.get("database", {}).get("available", False)
        
        return {
            "all_critical_available": all_critical_available,
            "checks": checks
        }
