"""
验证和推荐逻辑 - 独立于 UI 实现
支持静态推荐值和 AI 动态生成
"""
import json
from pathlib import Path
from typing import Dict, Optional, Any
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


def _add_to_ai_cache(key: str, recommendations: Dict[str, str], metadata: Optional[Dict] = None) -> None:
    """将 AI 推荐值添加到缓存"""
    import hashlib
    from datetime import datetime
    
    cache = _load_ai_cache()
    
    # 创建历史记录条目
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations,
        "success": True,
        "prompt_hash": hashlib.md5(json.dumps(recommendations, sort_keys=True).encode()).hexdigest()[:8]
    }
    
    cache_entry = {
        "key": key.upper(),  # 冗余存储键名，防止交叉引用
        "recommendations": recommendations,
        # 用户显式反馈
        "rating": 0,  # 评分：正面反馈数 - 负面反馈数
        "feedback_count": 0,  # 总反馈次数
        "positive_feedback": 0,  # 正面反馈数
        "negative_feedback": 0,  # 负面反馈数
        # 系统自动指标
        "apply_count": 0,  # 推荐值被应用的次数
        "modification_count": 0,  # 应用后被修改的次数
        "generation_count": 1,  # 生成过多少次
        # 计算得出的指标
        "metrics": {
            "stability_score": 0,  # 稳定性评分 (0-1)
            "consistency_score": 0.5,  # 生成一致性 (0-1)
        },
        "confidence": 0,  # 综合置信度 (0-1)
        "history": [history_entry],  # 生成历史记录
    }
    
    # 如果有 AI 元数据（explanation, best_practices 等），也一并保存
    if metadata:
        cache_entry["metadata"] = metadata
    
    # 如果已存在该key的缓存，保留旧的评分数据和指标
    old_entry = cache.get(key.upper())
    if old_entry and isinstance(old_entry, dict) and "rating" in old_entry:
        cache_entry["rating"] = old_entry.get("rating", 0)
        cache_entry["feedback_count"] = old_entry.get("feedback_count", 0)
        cache_entry["positive_feedback"] = old_entry.get("positive_feedback", 0)
        cache_entry["negative_feedback"] = old_entry.get("negative_feedback", 0)
        cache_entry["apply_count"] = old_entry.get("apply_count", 0)
        cache_entry["modification_count"] = old_entry.get("modification_count", 0)
        cache_entry["generation_count"] = old_entry.get("generation_count", 0) + 1
        cache_entry["metrics"] = old_entry.get("metrics", {"stability_score": 0, "consistency_score": 0.5})
        cache_entry["confidence"] = old_entry.get("confidence", 0)
        # 合并历史记录（保留最近10条）
        old_history = old_entry.get("history", [])
        cache_entry["history"] = (old_history + [history_entry])[-10:]
    
    cache[key.upper()] = cache_entry
    
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
            cached_entry = ai_cache[key_upper]

            # 防止交叉引用：如果缓存中存的 key 不一致，则忽略该缓存
            if isinstance(cached_entry, dict) and cached_entry.get("key") not in (None, key_upper):
                print(f"[Cache] 检测到跨键缓存 (期望 {key_upper}, 实际 {cached_entry.get('key')})，已忽略")
            else:
                # 兼容旧格式（直接存储推荐值）和新格式（包含评分的结构）
                from lib.ai_helper import get_ai_helper
                ai_helper = get_ai_helper()

                def _normalize_cached(rec_map: Dict[str, str]) -> Dict[str, str]:
                    if not current_values:
                        return rec_map
                    try:
                        wrapped = {"recommendations": rec_map}
                        normalized = ai_helper._normalize_recommendations(key_upper, current_values, {}, wrapped)
                        return normalized.get("recommendations", rec_map)
                    except Exception as e:
                        print(f"[Cache] 规范化缓存失败: {e}")
                        return rec_map

                if isinstance(cached_entry, dict) and "recommendations" in cached_entry:
                    # 从历史记录中选择置信度最高的推荐值
                    best_recommendations = _get_best_recommendations_from_history(key_upper, cached_entry)
                    if best_recommendations:
                        print(f"[Cache] 使用置信度最高的历史推荐: {key_upper}")
                        return _normalize_cached(best_recommendations)
                    else:
                        print(f"[Cache] 使用缓存的 AI 推荐值: {key_upper}")
                        return _normalize_cached(cached_entry["recommendations"])
                else:
                    # 旧格式缓存，直接返回
                    print(f"[Cache] 使用旧格式缓存: {key_upper}")
                    return _normalize_cached(cached_entry)
    
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
                    
                    # 保存 AI 元数据
                    metadata = {
                        'explanation': ai_result.get('explanation', ''),
                        'best_practices': ai_result.get('best_practices', ''),
                        'warnings': ai_result.get('warnings', [])
                    }
                    
                    # 将 AI 推荐值和元数据添加到缓存
                    _add_to_ai_cache(key_upper, recommendations, metadata)
                    
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


def clear_ai_cache_item(key: str) -> bool:
    """清除单个环境变量的 AI 缓存"""
    try:
        cache = _load_ai_cache()
        key_upper = key.upper()
        if key_upper in cache:
            cache.pop(key_upper, None)
            if _save_ai_cache(cache):
                print(f"[Cache] 已清除 {key_upper} 的 AI 缓存")
                return True
        return False
    except Exception as e:
        print(f"[Cache] 清除 {key} 缓存失败: {e}")
        return False


def _get_best_recommendations_from_history(key: str, cached_entry: Dict) -> Optional[Dict[str, str]]:
    """从历史记录中选择最佳推荐值
    
    策略：
    1. 计算整体置信度分数
    2. 如果历史记录中有更高置信度的版本，使用历史版本
    3. 否则使用当前版本
    """
    history = cached_entry.get("history", [])
    current_recommendations = cached_entry.get("recommendations", {})

    # 防止交叉引用：缓存内的 key 与请求 key 不一致则直接返回当前推荐
    if isinstance(cached_entry, dict) and cached_entry.get("key") not in (None, key.upper()):
        return None

    # 补充写入 key 字段
    cached_entry["key"] = cached_entry.get("key", key.upper())
    
    # 如果没有历史记录，返回当前推荐
    if not history or len(history) == 0:
        return None
    
    # 计算当前推荐的置信度（使用多维评分）
    current_confidence = calculate_confidence_score(cached_entry)
    
    # 遍历历史记录，找到成功生成的最高置信度版本
    best_confidence = current_confidence
    best_recommendations = None
    
    for hist in history:
        if not hist.get("success", True):  # 跳过失败记录
            continue
        
        hist_recommendations = hist.get("recommendations", {})
        if not hist_recommendations:
            continue
        
        # 创建临时entry来计算历史记录的置信度
        temp_entry = cached_entry.copy()
        temp_entry["recommendations"] = hist_recommendations
        hist_confidence = calculate_confidence_score(temp_entry)
        
        # 如果历史记录置信度更高，选择它
        if hist_confidence > best_confidence:
            best_confidence = hist_confidence
            best_recommendations = hist_recommendations
    
    return best_recommendations


def view_ai_cache() -> Dict[str, Dict[str, str]]:
    """查看当前 AI 推荐值缓存"""
    cache = _load_ai_cache()
    
    # 转换为兼容格式用于显示
    display_cache = {}
    for key, value in cache.items():
        if isinstance(value, dict) and "recommendations" in value:
            entry = value.copy()
        else:
            # 旧格式，转换为新格式
            entry = {
                "recommendations": value,
                "rating": 0,
                "feedback_count": 0,
                "positive_feedback": 0,
                "negative_feedback": 0
            }

        # 确保生成计数存在（从历史记录数量计算）
        history_count = len(entry.get("history", []))
        entry["generation_count"] = max(entry.get("generation_count", 0), history_count)
        
        # 计算 confidence（0-1 之间的浮点数）
        feedback_count = entry.get("feedback_count", 0)
        positive = entry.get("positive_feedback", 0)
        if feedback_count > 0:
            entry["confidence"] = positive / feedback_count  # 0-1 的浮点数
        else:
            entry["confidence"] = 0
        
        display_cache[key] = entry
    
    return display_cache


def submit_ai_feedback(key: str, is_positive: bool) -> bool:
    """
    提交 AI 推荐的反馈评分
    
    参数：
        key: 环境变量名称
        is_positive: True 表示正面反馈（👍），False 表示负面反馈（👎）
    
    返回：
        是否成功提交反馈
    """
    cache = _load_ai_cache()
    key_upper = key.upper()
    
    if key_upper not in cache:
        print(f"[Feedback] 未找到缓存的推荐值: {key_upper}")
        return False
    
    cached_entry = cache[key_upper]
    
    # 兼容旧格式
    if not isinstance(cached_entry, dict) or "recommendations" not in cached_entry:
        # 转换为新格式
        cached_entry = {
            "recommendations": cached_entry,
            "rating": 0,
            "feedback_count": 0,
            "positive_feedback": 0,
            "negative_feedback": 0
        }
    
    # 更新评分
    if is_positive:
        cached_entry["positive_feedback"] = cached_entry.get("positive_feedback", 0) + 1
        cached_entry["rating"] = cached_entry.get("rating", 0) + 1
    else:
        cached_entry["negative_feedback"] = cached_entry.get("negative_feedback", 0) + 1
        cached_entry["rating"] = cached_entry.get("rating", 0) - 1
    
    cached_entry["feedback_count"] = cached_entry.get("feedback_count", 0) + 1
    
    cache[key_upper] = cached_entry
    
    if _save_ai_cache(cache):
        print(f"[Feedback] 已记录 {key_upper} 的{'正面' if is_positive else '负面'}反馈")
        return True
    
    return False


def get_ai_cache_stats(key: str) -> Optional[Dict]:
    """
    获取 AI 推荐的统计信息（评分、反馈数等）
    
    返回：
        包含评分信息的字典，如果不存在则返回 None
    """
    cache = _load_ai_cache()
    key_upper = key.upper()
    
    if key_upper not in cache:
        return None
    
    cached_entry = cache[key_upper]
    
    if isinstance(cached_entry, dict) and "rating" in cached_entry:
        feedback_count = cached_entry.get("feedback_count", 0)
        positive = cached_entry.get("positive_feedback", 0)
        
        # 计算置信度（正面反馈占比）
        confidence = (positive / feedback_count * 100) if feedback_count > 0 else 0
        
        return {
            "rating": cached_entry.get("rating", 0),
            "feedback_count": feedback_count,
            "positive_feedback": positive,
            "negative_feedback": cached_entry.get("negative_feedback", 0),
            "confidence": round(confidence, 1),
            "has_metadata": "metadata" in cached_entry
        }
    
    return None


def _view_ai_cache_legacy() -> Dict[str, Dict[str, str]]:
    """查看当前 AI 推荐值缓存（遗留函数）"""
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

def _get_global_stats() -> Dict[str, float]:
    """
    计算全局统计信息，用于自适应权重调整
    
    返回：
        包含全局统计的字典
    """
    cache = _load_ai_cache()
    
    total_samples = 0
    total_applied = 0
    high_stability_count = 0
    high_feedback_count = 0
    
    stability_list = []
    feedback_list = []
    
    for entry in cache.values():
        if not isinstance(entry, dict):
            continue
        
        total_samples += 1
        apply_count = entry.get("apply_count", 0)
        
        if apply_count > 0:
            total_applied += 1
            
            # 计算稳定性
            modification_count = entry.get("modification_count", 0)
            stability = (apply_count - modification_count) / apply_count
            stability_list.append(stability)
            
            if stability > 0.8:
                high_stability_count += 1
            
            # 计算反馈
            positive = entry.get("positive_feedback", 0)
            negative = entry.get("negative_feedback", 0)
            if positive + negative > 0:
                feedback_score = positive / (positive + negative)
                feedback_list.append(feedback_score)
                if feedback_score > 0.8:
                    high_feedback_count += 1
    
    # 计算平均值
    avg_stability = sum(stability_list) / len(stability_list) if stability_list else 0.5
    avg_feedback = sum(feedback_list) / len(feedback_list) if feedback_list else 0.5
    
    return {
        'total_samples': total_samples,
        'total_applied': total_applied,
        'avg_stability': avg_stability,
        'avg_feedback': avg_feedback,
        'high_stability_ratio': high_stability_count / max(total_applied, 1),
        'high_feedback_ratio': high_feedback_count / max(len(feedback_list), 1),
    }


def calculate_confidence_score(entry: Dict, use_adaptive_weights: bool = True) -> float:
    """
    计算多维置信度评分 (0-1) - 支持自适应权重
    
    综合考虑：
    - 用户显式反馈（默认 30%权重）
    - 稳定性评分（默认 40%权重）
    - 生成一致性（默认 20%权重）  
    - 应用频率（默认 10%权重）
    
    参数：
        entry: 缓存条目
        use_adaptive_weights: 是否使用自适应权重（默认 True）
    
    返回：
        综合置信度评分 (0-1)
    """
    # 计算各个指标
    positive = entry.get("positive_feedback", 0)
    negative = entry.get("negative_feedback", 0)
    if positive + negative > 0:
        explicit_feedback = positive / (positive + negative)
    else:
        explicit_feedback = 0.5
    
    apply_count = entry.get("apply_count", 0)
    modification_count = entry.get("modification_count", 0)
    if apply_count > 0:
        stability = (apply_count - modification_count) / apply_count
    else:
        stability = 0.5
    
    consistency = entry.get("metrics", {}).get("consistency_score", 0.5)
    frequency = min(apply_count / 10, 1.0)
    
    # 初始权重（固定权重）
    weights = {
        'feedback': 0.3,
        'stability': 0.4,
        'consistency': 0.2,
        'frequency': 0.1
    }
    
    # 自适应权重调整
    if use_adaptive_weights:
        global_stats = _get_global_stats()
        total_applied = global_stats['total_applied']
        
        # 规则1：如果有足够样本（>20），根据历史表现调整权重
        if total_applied > 20:
            avg_stability = global_stats['avg_stability']
            high_stability_ratio = global_stats['high_stability_ratio']
            
            # 如果稳定性普遍很高（>0.7），说明稳定性是好指标，增加权重
            if high_stability_ratio > 0.7:
                weights['stability'] = 0.5
                weights['feedback'] = 0.25
                weights['consistency'] = 0.15
                weights['frequency'] = 0.1
                print(f"[自适应权重] 检测到高稳定性趋势，增加稳定性权重至 50%")
            
            # 如果反馈很活跃且准确，增加反馈权重
            elif global_stats['high_feedback_ratio'] > 0.7:
                weights['feedback'] = 0.4
                weights['stability'] = 0.35
                weights['consistency'] = 0.15
                weights['frequency'] = 0.1
                print(f"[自适应权重] 检测到高质量用户反馈，增加反馈权重至 40%")
        
        # 规则2：如果样本很少（<10），降低频率权重，因为数据不足
        if total_applied < 10:
            weights['frequency'] = 0.05
            # 把剩余的权重平分给其他三个
            remaining = 0.95
            weights['feedback'] = 0.3 * (remaining / 0.9)
            weights['stability'] = 0.4 * (remaining / 0.9)
            weights['consistency'] = 0.2 * (remaining / 0.9)
    
    # 规则增强：基于专家知识的额外奖励/惩罚
    bonus = 0
    
    # 奖励：连续稳定且高应用
    if apply_count >= 10 and modification_count == 0:
        bonus += 0.15
        print(f"[规则增强] 应用10次且从未修改，奖励 +15%")
    
    # 奖励：持续正面反馈
    if positive >= 3 and negative == 0:
        bonus += 0.1
        print(f"[规则增强] 连续3次点赞，奖励 +10%")
    
    # 惩罚：高修改率
    if apply_count > 0 and (modification_count / apply_count) > 0.5:
        bonus -= 0.2
        print(f"[规则增强] 修改率过高 ({modification_count}/{apply_count})，惩罚 -20%")
    
    # 奖励：三高组合（高反馈+高稳定+高一致性）
    if explicit_feedback > 0.8 and stability > 0.8 and consistency > 0.8:
        bonus += 0.1
        print(f"[规则增强] 三高组合，额外奖励 +10%")
    
    # 计算基础置信度
    base_confidence = (
        explicit_feedback * weights['feedback'] +
        stability * weights['stability'] +
        consistency * weights['consistency'] +
        frequency * weights['frequency']
    )
    
    # 应用规则增强
    final_confidence = min(max(base_confidence + bonus, 0), 1.0)
    
    return round(final_confidence, 3)


def get_adaptive_weights_info() -> Dict[str, Any]:
    """
    获取当前自适应权重系统的状态信息
    
    返回：
        包含权重信息和全局统计的字典
    """
    global_stats = _get_global_stats()
    
    # 根据全局统计确定当前使用的权重
    weights = {
        'feedback': 0.3,
        'stability': 0.4,
        'consistency': 0.2,
        'frequency': 0.1
    }
    
    weight_mode = "default"
    
    if global_stats['total_applied'] > 20:
        if global_stats['high_stability_ratio'] > 0.7:
            weights = {'feedback': 0.25, 'stability': 0.5, 'consistency': 0.15, 'frequency': 0.1}
            weight_mode = "high_stability"
        elif global_stats['high_feedback_ratio'] > 0.7:
            weights = {'feedback': 0.4, 'stability': 0.35, 'consistency': 0.15, 'frequency': 0.1}
            weight_mode = "high_feedback"
    elif global_stats['total_applied'] < 10:
        total = 0.95
        weights = {
            'feedback': 0.3 * (total / 0.9),
            'stability': 0.4 * (total / 0.9),
            'consistency': 0.2 * (total / 0.9),
            'frequency': 0.05
        }
        weight_mode = "low_sample"
    
    return {
        'current_weights': weights,
        'weight_mode': weight_mode,
        'global_stats': global_stats,
        'description': {
            'default': '默认权重（样本数适中）',
            'high_stability': '高稳定性模式（稳定性指标表现优异）',
            'high_feedback': '高反馈模式（用户反馈质量高）',
            'low_sample': '低样本模式（数据不足，降低频率权重）'
        }.get(weight_mode, '未知模式')
    }


def record_ai_recommendation_applied(key: str) -> None:
    """
    记录用户应用了某个 AI 推荐值
    
    参数：
        key: 环境变量名称
    """
    key_upper = key.upper()
    cache = _load_ai_cache()
    
    if key_upper not in cache:
        print(f"[Cache] 缓存中不存在 {key_upper}")
        return
    
    entry = cache[key_upper]
    if not isinstance(entry, dict):
        return
    
    # 增加应用计数
    entry["apply_count"] = entry.get("apply_count", 0) + 1
    
    # 重新计算置信度
    entry["confidence"] = calculate_confidence_score(entry)
    
    cache[key_upper] = entry
    _save_ai_cache(cache)
    print(f"[Cache] 已记录 {key_upper} 的应用 (apply_count={entry['apply_count']})")


def record_ai_recommendation_modified(key: str) -> None:
    """
    记录应用后的推荐值被用户修改了
    
    参数：
        key: 环境变量名称
    """
    key_upper = key.upper()
    cache = _load_ai_cache()
    
    if key_upper not in cache:
        print(f"[Cache] 缓存中不存在 {key_upper}")
        return
    
    entry = cache[key_upper]
    if not isinstance(entry, dict):
        return
    
    apply_count = entry.get("apply_count", 0)
    if apply_count > 0:
        # 只有应用过才能记录修改
        entry["modification_count"] = entry.get("modification_count", 0) + 1
        
        # 重新计算稳定性评分
        modification_count = entry["modification_count"]
        stability = (apply_count - modification_count) / apply_count
        
        if "metrics" not in entry:
            entry["metrics"] = {}
        entry["metrics"]["stability_score"] = round(stability, 3)
        
        # 重新计算置信度
        entry["confidence"] = calculate_confidence_score(entry)
        
        cache[key_upper] = entry
        _save_ai_cache(cache)
        print(f"[Cache] 已记录 {key_upper} 的修改 (modification_count={entry['modification_count']})")


def check_and_record_modifications(current_values: Dict[str, str]) -> None:
    """
    检查缓存中的推荐值是否被修改
    
    用于监测用户是否改动了之前应用的推荐值。
    该函数应该定期被调用（比如每次加载页面时）
    
    参数：
        current_values: 当前的环境变量值 {"ENV_NAME": "value", ...}
    """
    cache = _load_ai_cache()
    
    for key, entry in cache.items():
        if not isinstance(entry, dict) or "recommendations" not in entry:
            continue
        
        apply_count = entry.get("apply_count", 0)
        if apply_count == 0:
            # 没有应用过，跳过检查
            continue
        
        recommendations = entry["recommendations"]
        
        # 检查当前值是否与推荐值不同
        for env_name, recommended_value in recommendations.items():
            current_value = current_values.get(env_name, "")
            
            # 如果当前值与推荐值不同，且之前没有记录修改，则记录
            if current_value != recommended_value:
                modification_count = entry.get("modification_count", 0)
                # 只在第一次检测到修改时记录
                if modification_count < apply_count:
                    record_ai_recommendation_modified(key)
                    break  # 每个推荐只需记录一次修改


def get_cache_with_confidence(key: str) -> Optional[Dict]:
    """
    获取缓存条目并包含最新的置信度信息
    
    参数：
        key: 环境变量名称
    
    返回：
        包含置信度的缓存条目，如果不存在则返回 None
    """
    cache = _load_ai_cache()
    key_upper = key.upper()
    
    if key_upper not in cache:
        return None
    
    entry = cache[key_upper]
    if not isinstance(entry, dict):
        return None

    # 防止交叉引用：缓存内的 key 与请求 key 不一致则忽略
    if entry.get("key") not in (None, key_upper):
        return None

    # 补充写入 key 字段，便于后续校验
    entry["key"] = entry.get("key", key_upper)
    
    # 确保有最新的置信度计算
    entry["confidence"] = calculate_confidence_score(entry)

    # 复用最新的三段式解释生成，避免旧缓存说明格式陈旧
    try:
        ai_helper = get_ai_helper()
        metadata = entry.get("metadata", {}) or {}
        best = metadata.get("best_practices", "")
        if isinstance(best, list):
            best = "；".join([str(x).strip() for x in best if str(x).strip()])
        explanation = ai_helper._enforce_explanation_structure(
            key_upper,
            entry.get("recommendations", {}),
            metadata.get("explanation", ""),
            best,
        )
        metadata["explanation"] = explanation
        metadata["best_practices"] = best
        entry["metadata"] = metadata
    except Exception as e:
        print(f"[Cache] 规范化缓存说明失败: {e}")
    
    return entry
