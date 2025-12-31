"""
AI 助手 - 使用 Ollama 为环境变量提供智能推荐

功能：
- 根据环境变量名称和项目上下文生成推荐值
- 提供配置说明和最佳实践建议
"""

import json
import os
import requests
from typing import Dict, Optional, Any
from pathlib import Path
from functools import lru_cache

# Ollama 配置
OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen:7b"  # 可配置其他模型如 llama2, mixtral 等
REQUEST_TIMEOUT = 30  # 秒

# AI 专用 .env 文件路径（用于 AI_DEBUG_LOG 等）
AI_ENV_PATH = Path(__file__).resolve().parent.parent / ".env.ai"

# 类型提示：对常见键强制类型，避免被噪声值误判
TYPE_HINTS = {
    # 引导/控制类
    "BOOTSTRAP_ADMIN": "bool_01",
    "SECURE_MODE": "bool_01",
    "SKIP_DB_INIT": "bool_01",
    # 数据库
    "DATABASE_HOST": "host",
    "DATABASE_PORT": "port",
    "DATABASE_USER": "string",
    "DATABASE_PASSWORD": "password",
    "DATABASE_NAME": "string",
    # Redis
    "REDIS_HOST": "host",
    "REDIS_PORT": "port",
    "REDIS_DB": "number",
    "REDIS_PASSWORD": "password",
    # JWT
    "JWT_ALGORITHM": "string",
    "JWT_EXPIRE_HOURS": "number",
    # 默认密码
    "DEFAULT_ADMIN_PASSWORD": "password",
}


@lru_cache(maxsize=1)
def _load_ai_env():
    """尝试加载 .env.ai，便于开启 AI_DEBUG_LOG 等配置"""
    if not AI_ENV_PATH.exists():
        return False
    try:
        try:
            from dotenv import load_dotenv
            load_dotenv(AI_ENV_PATH)
            return True
        except Exception:
            # 简单解析
            for line in AI_ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            return True
    except Exception:
        return False


class AIHelper:
    """AI 助手类 - 提供智能推荐和分析"""
    
    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = OLLAMA_MODEL):
        _load_ai_env()
        self.api_url = api_url
        self.model = model
        self._available = None

    def _log_debug(self, *args):
        if os.environ.get("AI_DEBUG_LOG", "").lower() in ("1", "true", "yes", "on"):  # 简易开关
            try:
                print("[AIHelper DEBUG]", *args)
            except Exception:
                pass
    
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
            # 规范化推荐值（即便无上下文，也用当前值纠偏类型）
            result = self._normalize_recommendations(key, current_values, {}, result)

            return result
        
        except Exception as e:
            # AI 失败不影响核心功能，静默处理
            print(f"[AI Helper] 请求失败: {e}")
            return None
    
    def get_env_recommendations_with_context(
        self,
        key: str,
        current_values: Dict[str, str],
        env_context: Dict[str, Dict[str, Dict[str, str]]],  # 现在包含 value 和 comment
        cache_info: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        使用 AI 为环境变量生成推荐值（带完整项目上下文和缓存参考）
        
        参数：
            key: 环境变量名称
            current_values: 该变量在各环境的当前值
            env_context: 所有环境的完整配置 {"dev": {...}, "test": {...}, ...}
            cache_info: 缓存的推荐信息，用于参考（可选）
        
        返回：同 get_env_recommendations
        """
        if not self.is_available():
            return None
        
        try:
            # 构建带上下文的提示词
            prompt = self._build_context_aware_prompt(key, current_values, env_context, cache_info)
            
            # 调用 Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个经验丰富的 DevOps 工程师和配置管理专家。你会仔细分析项目的现有配置，理解项目架构和业务需求，然后提供准确的配置建议。\n\n关键要求：只输出有效的JSON，不要输出任何其他文字、解释或markdown标记。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "format": "json"
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                print(f"[AI Helper] HTTP错误 {response.status_code}: {response.text[:200]}")
                return None
            
            ai_response = response.json()
            content = ai_response.get("message", {}).get("content", "{}")
            self._log_debug("context-aware raw content", content[:500])
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"[AI Helper] JSON解析失败: {e}")
                print(f"[AI Helper] 原始响应: {content[:500]}")
                return None
            
            if not self._validate_response(result):
                print(f"[AI Helper] 响应格式验证失败: {result}")
                return None
            
            # 后处理：规范化推荐值类型
            result = self._normalize_recommendations(key, current_values, env_context, result)
            self._log_debug("context-aware normalized", result)
            
            return result
        
        except Exception as e:
            print(f"[AI Helper] 上下文感知请求失败: {e}")
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
        prompt = f"""你是一个经验丰富的 DevOps 工程师，正在为一个 FastAPI 项目配置环境变量。

项目类型: {project_type}
环境变量名: {key}

当前各环境的配置:
- dev (开发环境): {current_values.get('dev', '(未设置)')}
- test (测试环境): {current_values.get('test', '(未设置)')}
- demo (演示环境): {current_values.get('demo', '(未设置)')}
- prod (生产环境): {current_values.get('prod', '(未设置)')}

请分析这个环境变量的用途，并返回 JSON 格式的推荐配置：

{{
    "recommendations": {{
        "dev": "具体的单一值（如: 0, True, DEBUG, localhost等）",
        "test": "具体的单一值",
        "demo": "具体的单一值",
        "prod": "具体的单一值"
    }},
    "explanation": "结论/原因/建议 三段式，不超过200字，如：结论：...；原因：...；建议：...",
    "best_practices": "最佳实践建议（50字以内）",
    "warnings": ["注意事项1", "注意事项2"]
}}

**重要要求**：
1. recommendations 中的值必须是**纯净的单一值**，不要包含任何描述或解释文字
2. 值必须是可以直接写入 .env 文件的格式（字符串、数字、布尔值）
3. 例如："0" 而不是 "推荐使用0，因为..."
4. 例如："True" 而不是 "建议设为True以启用调试"
5. 开发环境优先调试便利，生产环境优先安全和性能
6. 如果是布尔值，使用 True/False 或 0/1
7. 如果是数字，直接返回数字字符串如 "8080"
8. 如果是路径，使用相对路径如 "photos" 或 "./data"
9. 如果是密码相关，开发环境可以简单，生产环境留空让系统生成
10. HOST/ADDRESS/DOMAIN 等必须是主机名或 IPv4，不得返回 0/1/True/False/纯数字，缺省请用 localhost"""
        
        return prompt
    
    def _build_context_aware_prompt(
        self,
        key: str,
        current_values: Dict[str, str],
        env_context: Dict[str, Dict[str, Dict[str, str]]],  # 现在包含 value 和 comment
        cache_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建上下文感知的 AI 提示词,带缓存参考"""
        
        # 智能精简上下文：优先传递相关配置，避免噪声
        key_prefix = key.split('_')[0] if '_' in key else key
        
        # 格式化各环境的配置
        env_configs = []
        for env_name in ["dev", "test", "demo", "prod"]:
            if env_name in env_context:
                config = env_context[env_name]
                
                # 分类：与当前key同前缀的优先，其他限制数量
                same_prefix = {}
                others = {}
                for k, v_data in config.items():
                    if k.split('_')[0] == key_prefix or k == key:
                        same_prefix[k] = v_data
                    else:
                        others[k] = v_data
                
                # 合并：同前缀全部保留，其他最多保留15个常见配置
                filtered = same_prefix.copy()
                if len(others) <= 15:
                    filtered.update(others)
                else:
                    # 优先保留常见关键配置
                    priority_patterns = ['DEBUG', 'DB_', 'REDIS_', 'JWT_', 'SECRET', 'HOST', 'PORT', 'SECURE', 'SKIP_', 'LOG_']
                    priority_items = {k: v for k, v in others.items() 
                                     if any(pattern in k for pattern in priority_patterns)}
                    remaining = {k: v for k, v in others.items() if k not in priority_items}
                    filtered.update(priority_items)
                    # 剩余的按字母序取前几个
                    remaining_sorted = sorted(remaining.items())[:max(0, 15-len(priority_items))]
                    filtered.update(dict(remaining_sorted))
                
                if filtered:
                    config_lines = []
                    for k, v_data in sorted(filtered.items()):
                        val = v_data.get('value', '') if isinstance(v_data, dict) else v_data
                        comment = v_data.get('comment', '') if isinstance(v_data, dict) else ''
                        if comment:
                            config_lines.append(f"  # {comment}")
                        config_lines.append(f"  {k}={val}")
                    env_configs.append(f"\n【{env_name.upper()} 环境配置】\n" + "\n".join(config_lines))
        
        context_section = "\n".join(env_configs) if env_configs else "(无相关配置项)"
        
        # 构建缓存参考部分
        cache_reference = ""
        if cache_info and isinstance(cache_info, dict):
            if cache_info.get("key") not in (None, key.upper()):
                cache_info = None  # 防止跨键引用

        if cache_info and isinstance(cache_info, dict):
            confidence = cache_info.get("confidence", 0)
            if confidence >= 0.8:
                # 高置信度，强烈推荐参考
                recommendations = cache_info.get("recommendations", {})
                rec_str = ", ".join([f"{k}={v}" for k, v in recommendations.items()])
                apply_count = cache_info.get("apply_count", 0)
                cache_reference = f"""

【系统提示：已验证的推荐参考】
系统曾为此变量生成过推荐值，用户对这个推荐的满意度达到 {confidence*100:.0f}%（应用 {apply_count} 次）：
  推荐值: {rec_str}

请考虑这个已验证的推荐作为参考。如果你认为有更好的方案，也可以提出新建议。
"""
            elif confidence >= 0.5:
                # 中置信度，作为参考但可改进
                recommendations = cache_info.get("recommendations", {})
                rec_str = ", ".join([f"{k}={v}" for k, v in recommendations.items()])
                cache_reference = f"""

【参考信息】
系统曾提过相似的推荐（用户满意度 {confidence*100:.0f}%）：{rec_str}
你可以参考这个推荐，但请评估是否需要改进。
"""
        
        prompt = f"""你是一个经验丰富的 DevOps 工程师，正在为一个 FastAPI 项目配置环境变量。

项目信息：
- 项目类型: FastAPI Web Application (高速公路巡查系统)
- 数据库: MySQL
- 缓存: Redis
- 认证: JWT
- 文件上传: 支持照片上传

当前需要配置的环境变量: {key}

该变量在各环境的当前值:
- dev (开发环境): {current_values.get('dev', '(未设置)')}
- test (测试环境): {current_values.get('test', '(未设置)')}
- demo (演示环境): {current_values.get('demo', '(未设置)')}
- prod (生产环境): {current_values.get('prod', '(未设置)')}

为了帮助你理解项目上下文，以下是各环境的完整配置：
{context_section}{cache_reference}

请根据以上信息，为 {key} 提供准确的配置建议。返回 JSON 格式：

{{
    "recommendations": {{
        "dev": "具体的单一值（如: 0, True, DEBUG, localhost等）",
        "test": "具体的单一值",
        "demo": "具体的单一值",
        "prod": "具体的单一值"
    }},
    "explanation": "结论/原因/建议 三段式，不超过200字，如：结论：...；原因：...；建议：...",
    "best_practices": "最佳实践建议（50字以内）",
    "warnings": ["注意事项1", "注意事项2"]
}}

**关键要求**：
1. recommendations 中的值必须是**纯净的单一值**，不要包含任何描述或解释文字
2. 值必须可以直接写入 .env 文件（字符串、数字、布尔值）
3. 例如："0" 而不是 "推荐使用0，因为..."
4. 例如："True" 而不是 "建议设为True以启用调试"
5. 仔细分析项目现有配置，理解变量的实际用途
6. 开发环境优先调试便利，生产环境优先安全和性能
7. 如果是布尔值，使用 True/False 或 0/1
8. 如果是数字，直接返回数字字符串如 "8080"
9. 如果是路径，使用相对路径如 "photos" 或 "./data"
10. 如果是密码相关，开发环境可以简单，生产环境留空让系统生成

特殊说明（必须严格遵守）：
- BOOTSTRAP_ADMIN: 必须为 0 或 1（0=首次启动时创建管理员，1=跳过创建）
  例如: dev=0, test=1, demo=0, prod=1
  
- SECURE_MODE: 必须为 0 或 1（0=从.env读取，1=仅用系统环境变量）
  例如: dev=0, test=0, demo=1, prod=1
  
- SKIP_DB_INIT: 必须为 0 或 1（0=执行数据库初始化，1=跳过）
  例如: dev=0, test=0, demo=1, prod=1
  
- DEBUG: 必须为 True 或 False（注意大小写）
  例如: dev=True, test=True, demo=False, prod=False
  
- DATABASE_PORT, REDIS_PORT: 必须为纯数字字符串
  例如: dev=3306, test=3306, demo=3306, prod=3306
  
- DATABASE_PASSWORD, REDIS_PASSWORD: 生产/演示环境必须为空字符串
  例如: dev=dev_password, test=test_password, demo="", prod=""

- HOST/ADDRESS/DOMAIN 等: 必须是主机名或 IPv4，不得返回 0/1/True/False/纯数字，缺省请用 localhost
    例如: dev=localhost, test=localhost, demo=localhost, prod=localhost
  
- UPLOAD_FOLDER: 必须为相对路径，不要引号
  例如: dev=photos, test=photos, demo=photos, prod=photos

重要提醒：请只输出上述JSON格式的内容，不要添加任何markdown标记（如```json）、额外解释文字或其他内容。"""
        
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
    
    def _normalize_recommendations(self, key: str, current_values: Dict[str, str], env_context: Optional[Dict[str, Dict[str, Dict[str, str]]]], result: Dict) -> Dict:
        """综合当前值/上下文推断类型并规范化推荐值"""
        recommendations = result.get("recommendations", {})
        raw_recommendations = dict(recommendations)
        normalized = {}
        key_upper = key.upper()
        env_context = env_context or {}

        # 归一化 best_practices 字段名与类型
        best_practices_aliases = ["best_practices", "best_practice", "best_实践", "best_ practices", "best_practises", "best_ Practices"]
        best_items = []
        for alias in best_practices_aliases:
            if alias in result:
                raw_best = result.get(alias)
                if isinstance(raw_best, str):
                    best_items.append(raw_best)
                elif isinstance(raw_best, list):
                    best_items.extend([str(x) for x in raw_best])
        # 去重并清洗
        best_items = [s.strip() for s in best_items if str(s).strip()]
        seen = set()
        best_items = [s for s in best_items if not (s in seen or seen.add(s))]
        result["best_practices"] = best_items

        # 智能推断变量类型（不依赖命名模式，优先看现有值特征、上下文注释、同组键）
        var_type = self._infer_variable_type(key_upper, recommendations, current_values, env_context)
        self._log_debug("normalize", key_upper, "detected type", var_type, "current", current_values, "raw rec", recommendations)

        for env, value in recommendations.items():
            str_value = str(value).strip()
            current_value = str(current_values.get(env, "") or "").strip()
            normalized[env] = self._normalize_by_type(var_type, key_upper, str_value, env, current_value)

        result["recommendations"] = normalized
        # 标记被纠偏的环境，便于 UI/日志展示
        corrections = []
        for env, raw_val in raw_recommendations.items():
            norm_val = normalized.get(env)
            if norm_val is None:
                continue
            raw_s = str(raw_val).strip()
            if raw_s != norm_val:
                corrections.append(f"{env}: {raw_s} -> {norm_val}")
        if corrections:
            result["corrections"] = corrections
        # 保证 explanation 三段式&字数限制
        result["explanation"] = self._enforce_explanation_structure(
            key_upper,
            normalized,
            result.get("explanation", ""),
            result.get("best_practices", ""),
        )
        return result

    def _enforce_explanation_structure(self, key_upper: str, recs: Dict[str, str], original: str, best: str) -> str:
        """强制 explanation 为 结论/原因/建议 三段式，<=200 字"""
        if original and all(tag in original for tag in ("结论", "原因", "建议")) and len(original) <= 200:
            return original.strip()

        rec_pairs = ", ".join([f"{env}={val}" for env, val in recs.items()]) if recs else "无有效推荐"

        def _clean(text: str) -> str:
            return " ".join(str(text).replace("；", ";").replace("。", ";").split())

        # 尝试复用 AI 原因，避免重复的模板化措辞
        reason_src = _clean(original)[:120] if original else "依据当前值和上下文自动校正类型并保持一致性"

        if isinstance(best, list):
            best_part = _clean("; ".join(best))
        else:
            best_part = _clean(best) if best else ""

        suggestion = best_part or "按环境区分易用与安全，落地前与真实部署核对"

        text = (
            f"结论：为 {key_upper} 推荐 {rec_pairs}。"
            f"原因：{reason_src}。"
            f"建议：{suggestion}。"
        )
        return text

    def _infer_variable_type(self, key: str, sample_recommendations: Dict[str, str], current_values: Dict[str, str], env_context: Optional[Dict[str, Dict[str, Dict[str, str]]]]) -> str:
        """多信号综合推断类型：值特征 > 注释/同组上下文 > 命名模式"""
        key_upper = key.upper()
        env_context = env_context or {}

        def clean_values(raw_vals):
            vals = []
            for v in raw_vals:
                if v is None:
                    continue
                s = str(v).strip()
                if s in ('', '(empty)', 'None', 'null', '(未设置)', '(未配置)'):
                    continue
                vals.append(s)
            return vals

        sample_values = clean_values(sample_recommendations.values())
        current_vals = clean_values(current_values.values())

        # 0) 类型提示优先
        hint = TYPE_HINTS.get(key_upper)
        if hint:
            return hint

        # 从注释取关键词
        comment_tokens = []
        for env, env_data in env_context.items():
            item = env_data.get(key_upper) or env_data.get(key)
            if isinstance(item, dict):
                comment = item.get('comment', '') or ''
                if comment:
                    comment_tokens.append(comment.lower())

        def looks_like_bool(val: str) -> bool:
            return val.lower() in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off')

        def looks_like_port(val: str) -> bool:
            if not val.replace('-', '').isdigit():
                return False
            try:
                num = int(val)
                return 1 <= num <= 65535
            except:
                return False

        def looks_like_host(val: str) -> bool:
            # 包含字母/数字/点/短横线，且不是纯数字/布尔
            if looks_like_bool(val):
                return False
            if val.isdigit():
                return False
            if ' ' in val:
                return False
            if any(c in val for c in ['/', '\\', ':']):
                return False
            # IPv4 兼容
            parts = val.split('.')
            if len(parts) >= 2 and all(p.isdigit() and p != '' and 0 <= int(p) <= 255 for p in parts):
                return True
            return (any(ch.isalpha() for ch in val) and any(ch in '.-' for ch in val)) or val.lower() == 'localhost'

        def looks_like_path(val: str) -> bool:
            return '/' in val or '\\' in val or val.startswith('.')

        def looks_like_url(val: str) -> bool:
            return '://' in val

        def majority_type(values):
            score = {'bool_tf':0, 'bool_01':0, 'port':0, 'number':0, 'host':0, 'path':0, 'password':0, 'string':0}
            for v in values:
                if looks_like_url(v):
                    score['string'] += 1
                elif looks_like_path(v):
                    score['path'] += 1
                elif looks_like_host(v):
                    score['host'] += 2
                elif looks_like_port(v):
                    score['port'] += 2
                elif looks_like_bool(v):
                    # 倾向布尔 True/False
                    if v.lower() in ('true','false'):
                        score['bool_tf'] += 2
                    else:
                        score['bool_01'] += 2
                elif len(v) >= 12 and any(not c.isalnum() for c in v) and any(c.isdigit() for c in v) and any(c.isalpha() for c in v):
                    score['password'] += 2
                elif v.replace('-', '').isdigit():
                    score['number'] += 1
                else:
                    score['string'] += 1
            # 取最高分
            best = max(score.items(), key=lambda x: x[1])
            if best[1] == 0:
                return 'string'
            return best[0]

        # 如果当前值里明显是主机/IP，优先认定为 host，避免 0/1 干扰
        for v in current_vals:
            if looks_like_host(v):
                value_type = 'host'
                break
        else:
            # 1) 值特征优先：样本值 + 当前值（当前值优先）
            current_type = majority_type(current_vals) if current_vals else None
            value_type = majority_type(sample_values + current_vals)
            if current_type and current_type != 'string':
                value_type = current_type
        # 2) 注释信号
        comment_joined = ' '.join(comment_tokens)
        if comment_joined:
            tokens_map = {
                'host': ['host','ip','address','server','domain'],
                'port': ['port'],
                'password': ['password','secret','token','key'],
                'path': ['path','dir','folder','directory'],
                'bool': ['enable','disable','flag','switch','toggle','on','off'],
                'number': ['count','size','limit','retry','timeout','ttl','expire'],
            }
            for t in tokens_map['host']:
                if t in comment_joined:
                    value_type = 'host'
            for t in tokens_map['port']:
                if t in comment_joined:
                    value_type = 'port'
            for t in tokens_map['password']:
                if t in comment_joined:
                    value_type = 'password'
            for t in tokens_map['path']:
                if t in comment_joined:
                    value_type = 'path'
            for t in tokens_map['bool']:
                if t in comment_joined and value_type == 'string':
                    value_type = 'bool_01'
            for t in tokens_map['number']:
                if t in comment_joined and value_type == 'string':
                    value_type = 'number'

        # 3) 同组键参考（同前缀，如 DATABASE_*）
        prefix = key_upper.split('_')[0] if '_' in key_upper else ''
        if prefix:
            sibling_keys = []
            for env, env_data in env_context.items():
                for k in env_data.keys():
                    ku = k.upper()
                    if ku.startswith(prefix) and ku != key_upper:
                        sibling_keys.append(ku)
            sibling_str = ' '.join(sibling_keys)
            if 'PORT' in sibling_str and value_type == 'string':
                value_type = 'host'
            if any(tok in sibling_str for tok in ['PASS','SECRET','TOKEN']) and value_type == 'string':
                value_type = 'password'

        # 4) 若值特征为空，回退命名模式
        if value_type == 'string':
            # 名称模式回退（更温和）
            name_based = self._infer_by_name(key_upper, sample_values)
            if name_based:
                value_type = name_based

        # 5) HOST 类键的兜底：避免被错误判成布尔/数字
        if any(tag in key_upper for tag in ['HOST', 'ADDRESS', 'DOMAIN', 'SERVER']):
            if value_type in ('bool_01', 'bool_tf', 'number', 'port'):
                value_type = 'host'

        # 名称类键的兜底：避免被 0/1 误判
        if 'NAME' in key_upper or 'USER' in key_upper or 'ACCOUNT' in key_upper:
            if value_type in ('bool_01', 'bool_tf', 'number', 'port', 'host'):
                value_type = 'string'

        return value_type or 'string'

    def _infer_by_name(self, key_upper: str, sample_values: list) -> Optional[str]:
        # 旧的模式匹配逻辑，作为弱回退
        bool_patterns = ['SKIP_', 'ENABLE', 'DISABLE', 'IS_', 'HAS_', 'SECURE_', 'BOOTSTRAP_', 
                        'CACHE_ENABLED', 'USE_', 'ALLOW_', 'REQUIRE_']
        if key_upper == 'DEBUG':
            return 'bool_tf'
        if any(pattern in key_upper for pattern in bool_patterns):
            if sample_values:
                if any(v in ('True', 'False', 'true', 'false') for v in sample_values):
                    return 'bool_tf'
            return 'bool_01'
        if 'PORT' in key_upper:
            return 'port'
        password_patterns = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'AUTH_STRING']
        if any(pattern in key_upper for pattern in password_patterns):
            return 'password'
        if any(pattern in key_upper for pattern in ['HOST', 'ADDRESS', 'SERVER', 'DOMAIN']):
            return 'host'
        if any(pattern in key_upper for pattern in ['FOLDER', 'PATH', 'DIR', 'DIRECTORY']):
            return 'path'
        number_patterns = ['COUNT', 'SIZE', 'LIMIT', 'MAX', 'MIN', 'TIMEOUT', 'EXPIRE', 
                          'INTERVAL', 'RETRY', '_DB', 'TTL', 'HOURS', 'SECONDS', 'MINUTES',
                          'WORKERS', 'THREADS', 'POOL_SIZE']
        if any(pattern in key_upper for pattern in number_patterns):
            return 'number'
        if sample_values:
            if all(v.isdigit() or (v.startswith('-') and v[1:].isdigit()) for v in sample_values):
                return 'number'
            if all(v in ('0', '1', 'True', 'False', 'true', 'false', 'yes', 'no') for v in sample_values):
                if all(v in ('True', 'False', 'true', 'false') for v in sample_values):
                    return 'bool_tf'
                return 'bool_01'
        return None
    
    def _normalize_by_type(self, var_type: str, key: str, value: str, env: str, current_value: Optional[str] = None) -> str:
        """根据推断的类型规范化值；如果当前值已合理则优先保留"""
        current_value = (current_value or "").strip()
        if var_type == 'bool_01':
            # 0/1 布尔型
            if value.lower() in ('true', '1', 'yes', 'on'):
                return '1'
            elif value.lower() in ('false', '0', 'no', 'off', ''):
                return '0'
            else:
                # 根据环境给默认值
                return (current_value if current_value in ('0','1') else ('0' if env in ('dev', 'test') else '1'))
        
        elif var_type == 'bool_tf':
            # True/False 布尔型
            if value.lower() in ('true', '1', 'yes', 'on'):
                return 'True'
            elif value.lower() in ('false', '0', 'no', 'off', ''):
                return 'False'
            else:
                if current_value in ('True','False'):
                    return current_value
                return 'True' if env in ('dev', 'test') else 'False'
        
        elif var_type == 'port':
            # 端口号
            try:
                port = int(''.join(filter(str.isdigit, value)))
                if 1 <= port <= 65535:
                    return str(port)
                else:
                    raise ValueError
            except:
                # 根据变量名猜测默认端口
                if 'DATABASE' in key or 'MYSQL' in key:
                    return '3306'
                elif 'REDIS' in key:
                    return '6379'
                elif 'HTTP' in key or 'WEB' in key or 'API' in key:
                    return '8000'
                elif 'POSTGRES' in key:
                    return '5432'
                elif 'MONGO' in key:
                    return '27017'
                else:
                    return '8080'
        
        elif var_type == 'number':
            # 纯数字
            try:
                # 提取数字部分
                num_str = ''.join(filter(lambda x: x.isdigit() or x == '-', value))
                if num_str and num_str != '-':
                    num = int(num_str)
                    return str(num)
                else:
                    raise ValueError
            except:
                # 根据变量名给默认值
                if 'REDIS_DB' in key:
                    return current_value or '0'
                elif 'EXPIRE' in key or 'TTL' in key:
                    return current_value or '3600'
                elif 'TIMEOUT' in key:
                    return current_value or '30'
                elif 'RETRY' in key:
                    return current_value or '3'
                elif 'POOL' in key:
                    return current_value or '10'
                else:
                    return current_value or '0'
        
        elif var_type == 'password':
            # 密码：生产/演示环境留空
            invalid_tokens = ('', '(empty)', 'None', 'null', '(未设置)', '(未配置)')
            # 若当前值非空，优先保留（即便在 prod/demo）
            if current_value and current_value not in invalid_tokens:
                return current_value
            if env in ('prod', 'demo'):
                return ''
            if value and value not in invalid_tokens:
                return value
            return f'{env}_password_123'
        
        elif var_type == 'host':
            # 主机名
            cleaned = value.strip('"\' ')
            cleaned_current = current_value.strip('"\' ')
            invalid_tokens = ('', '(empty)', 'None', 'null', '(未设置)', '(未配置)', 'true', 'false', '1', '0')

            def valid_host(v: str) -> bool:
                if v.lower() in invalid_tokens:
                    return False
                if ' ' in v:
                    return False
                if any(c in v for c in ['/', '\\', ':']):
                    return False
                if v.isdigit():
                    return False
                # IPv4 支持
                parts = v.split('.')
                if len(parts) >= 2 and all(p.isdigit() and p != '' and 0 <= int(p) <= 255 for p in parts):
                    return True
                return (any(ch.isalpha() for ch in v) and any(ch in '.-' for ch in v)) or v.lower() == 'localhost'

            # 保留当前值（若有效），否则使用推荐值，最后回退 localhost
            if cleaned_current and valid_host(cleaned_current):
                return cleaned_current
            if cleaned and valid_host(cleaned):
                return cleaned
            return 'localhost'
        
        elif var_type == 'path':
            # 路径/文件夹
            if value in ('', '(empty)', 'None', 'null', '(未设置)', '(未配置)'):
                if 'UPLOAD' in key:
                    return 'photos'
                elif 'LOG' in key:
                    return 'logs'
                elif 'DATA' in key:
                    return 'data'
                else:
                    return 'files'
            else:
                return value.strip('"\' ').rstrip('/')
        
        else:
            # 字符串类型
            invalid_tokens = ('', '(empty)', 'None', 'null', '(未设置)', '(未配置)')
            bad_literal = value.lower() in ('0','1','true','false')
            if (value in invalid_tokens or bad_literal) and current_value not in invalid_tokens:
                # 对名称/账号/JWT 等键优先保留现有值
                if ('NAME' in key or 'USER' in key or 'ACCOUNT' in key or key in ('JWT_ALGORITHM', 'JWT_SECRET', 'JWT_AUDIENCE', 'JWT_ISSUER')):
                    return current_value.strip('"\' ')
            if value in invalid_tokens and current_value not in invalid_tokens:
                return current_value.strip('"\' ')
            if value in ('(empty)', 'None', 'null', '(未设置)'):
                return ''
            return value.strip('"\' ')


# 全局单例
_ai_helper_instance = None


def get_ai_helper() -> AIHelper:
    """获取 AI 助手单例"""
    global _ai_helper_instance
    if _ai_helper_instance is None:
        _ai_helper_instance = AIHelper()
    return _ai_helper_instance
