"""
AI 助手 - 使用 Ollama 为环境变量提供智能推荐

功能：
- 根据环境变量名称和项目上下文生成推荐值
- 提供配置说明和最佳实践建议
"""

import json
import requests
from typing import Dict, Optional, Any
from pathlib import Path

# Ollama 配置
OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen:7b"  # 可配置其他模型如 llama2, mixtral 等
REQUEST_TIMEOUT = 30  # 秒


class AIHelper:
    """AI 助手类 - 提供智能推荐和分析"""
    
    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = OLLAMA_MODEL):
        self.api_url = api_url
        self.model = model
        self._available = None
    
    def is_available(self) -> bool:
        """检查 Ollama 服务是否可用"""
        if self._available is not None:
            return self._available
        
        try:
            response = requests.get(
                self.api_url.replace('/api/chat', '/api/tags'),
                timeout=3
            )
            self._available = response.status_code == 200
        except Exception:
            self._available = False
        
        return self._available
    
    def get_env_recommendations(
        self, 
        key: str, 
        current_values: Dict[str, str],
        project_type: str = "FastAPI Web Application"
    ) -> Optional[Dict[str, Any]]:
        """
        使用 AI 为环境变量生成推荐值
        
        参数：
            key: 环境变量名称（如 SKIP_DB_INIT, DEBUG）
            current_values: 各环境当前值 {"dev": "0", "test": "0", ...}
            project_type: 项目类型描述
        
        返回：
            {
                "recommendations": {"dev": "推荐值", "test": "推荐值", ...},
                "explanation": "为什么这样推荐的说明",
                "best_practices": "最佳实践建议",
                "warnings": ["注意事项1", "注意事项2"]
            }
            
            如果 AI 不可用或失败，返回 None
        """
        if not self.is_available():
            return None
        
        try:
            # 构建提示词
            prompt = self._build_recommendation_prompt(key, current_values, project_type)
            
            # 调用 Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个经验丰富的 DevOps 工程师，专门负责环境变量配置和安全最佳实践。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "format": "json"  # 要求返回 JSON 格式
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                return None
            
            # 解析响应
            ai_response = response.json()
            content = ai_response.get("message", {}).get("content", "{}")
            
            # 解析 JSON
            result = json.loads(content)
            
            # 验证返回格式
            if not self._validate_response(result):
                return None
            
            return result
        
        except Exception as e:
            # AI 失败不影响核心功能，静默处理
            print(f"[AI Helper] 请求失败: {e}")
            return None
    
    def get_help_text(self, key: str, context: str = "") -> Optional[str]:
        """
        使用 AI 生成配置项的帮助文档
        
        参数：
            key: 环境变量名称
            context: 额外上下文信息
        
        返回：
            帮助文档字符串，失败返回 None
        """
        if not self.is_available():
            return None
        
        try:
            prompt = f"""请为以下环境变量提供清晰的帮助文档：

环境变量名: {key}
{f"上下文: {context}" if context else ""}

请用中文返回 JSON 格式：
{{
    "description": "简短描述（1-2句话）",
    "usage": "如何使用",
    "examples": ["示例1", "示例2"],
    "notes": "注意事项"
}}"""
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "format": "json"
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                return None
            
            ai_response = response.json()
            content = ai_response.get("message", {}).get("content", "{}")
            result = json.loads(content)
            
            # 格式化返回
            help_text = f"{result.get('description', '')}\n"
            help_text += f"用法: {result.get('usage', '')}\n"
            
            examples = result.get('examples', [])
            if examples:
                help_text += f"示例: {', '.join(examples)}\n"
            
            notes = result.get('notes', '')
            if notes:
                help_text += f"⚠️ {notes}"
            
            return help_text.strip()
        
        except Exception:
            return None
    
    def _build_recommendation_prompt(
        self, 
        key: str, 
        current_values: Dict[str, str],
        project_type: str
    ) -> str:
        """构建 AI 提示词"""
        prompt = f"""作为 DevOps 专家，请为以下环境变量提供配置推荐：

项目类型: {project_type}
环境变量名: {key}

当前配置:
- dev: {current_values.get('dev', '(未设置)')}
- test: {current_values.get('test', '(未设置)')}
- demo: {current_values.get('demo', '(未设置)')}
- prod: {current_values.get('prod', '(未设置)')}

请根据行业最佳实践，返回 JSON 格式的推荐：

{{
    "recommendations": {{
        "dev": "推荐值",
        "test": "推荐值",
        "demo": "推荐值",
        "prod": "推荐值"
    }},
    "explanation": "为什么这样推荐（1-2句话）",
    "best_practices": "最佳实践建议",
    "warnings": ["注意事项1", "注意事项2"]
}}

要求：
1. 考虑不同环境的特点（dev=开发, test=测试, demo=演示, prod=生产）
2. 生产环境必须安全
3. 开发环境优先方便调试
4. 提供具体值，不要用占位符"""
        
        return prompt
    
    def _validate_response(self, result: Dict) -> bool:
        """验证 AI 返回的数据格式"""
        if not isinstance(result, dict):
            return False
        
        if "recommendations" not in result:
            return False
        
        recommendations = result["recommendations"]
        if not isinstance(recommendations, dict):
            return False
        
        # 至少要有 dev 和 prod 的推荐
        if "dev" not in recommendations or "prod" not in recommendations:
            return False
        
        return True


# 全局单例
_ai_helper_instance = None


def get_ai_helper() -> AIHelper:
    """获取 AI 助手单例"""
    global _ai_helper_instance
    if _ai_helper_instance is None:
        _ai_helper_instance = AIHelper()
    return _ai_helper_instance
