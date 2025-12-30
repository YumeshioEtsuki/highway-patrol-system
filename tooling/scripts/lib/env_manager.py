"""
环境变量管理核心类 - 处理读写和修改逻辑
遵循行业规范：单一职责、可测试、易集成
"""
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


class EnvManager:
    """环境变量管理器"""
    
    def __init__(self, root: Path):
        self.root = Path(root)
        self.tooling_env = self.root / "tooling" / "env"
        self.env_example = self.root / ".env.example"
        self.files = {
            "dev": self.tooling_env / "local.dev.env",
            "test": self.tooling_env / "local.test.env",
            "demo": self.tooling_env / "local.demo.env",
            "prod": self.tooling_env / "production.env",
        }
    
    def get_current_values(self, key: str) -> Dict[str, str]:
        """获取指定键在所有环境中的当前值"""
        result = {}
        for env, path in self.files.items():
            result[env] = self._read_key_from_file(path, key)
        return result
    
    def set_value(self, key: str, env: str, value: str) -> bool:
        """设置指定环境的变量值"""
        path = self.files.get(env)
        if not path or not path.exists():
            return False
        
        content = path.read_text(encoding="utf-8")
        
        # 如果键存在，替换；否则追加
        if re.search(rf"^{re.escape(key)}=", content, re.MULTILINE):
            new_content = re.sub(
                rf"^{re.escape(key)}=.*$",
                f"{key}={value}",
                content,
                flags=re.MULTILINE
            )
        else:
            new_content = content.rstrip() + f"\n{key}={value}\n"
        
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            return True
        return False
    
    def set_values_batch(self, key: str, envs: list, value: str) -> Tuple[int, list]:
        """批量设置多个环境的值，返回 (更新数, 失败环境列表)"""
        updated = 0
        failed = []
        
        for env in envs:
            if self.set_value(key, env, value):
                updated += 1
            else:
                failed.append(env)
        
        return updated, failed
    
    def get_all_keys(self) -> set:
        """获取所有出现过的键"""
        keys = set()
        for path in self.files.values():
            if path.exists():
                content = path.read_text(encoding="utf-8")
                matches = re.findall(r"^([A-Z_]+)=", content, re.MULTILINE)
                keys.update(matches)
        return sorted(keys)
    
    def get_all_values(self, env: str) -> Dict[str, str]:
        """获取指定环境的所有键值对"""
        result = {}
        path = self.files.get(env)
        
        if not path or not path.exists():
            return result
        
        content = path.read_text(encoding="utf-8")
        for line in content.split('\n'):
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                if key:
                    result[key] = val
        
        return result
    
    def validate_syntax(self, path: Path) -> Tuple[bool, str]:
        """验证 .env 文件语法"""
        if not path.exists():
            return False, f"文件不存在: {path}"
        
        content = path.read_text(encoding="utf-8")
        for i, line in enumerate(content.split("\n"), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" not in line:
                return False, f"第{i}行语法错误：缺少 '='  -> {line[:50]}"
        
        return True, "✓ 语法正确"
    
    @staticmethod
    def _read_key_from_file(path: Path, key: str) -> str:
        """从文件读取单个键的值"""
        if not path.exists():
            return "(未配置)"
        
        content = path.read_text(encoding="utf-8")
        match = re.search(rf"^{re.escape(key)}=(.*)$", content, re.MULTILINE)
        return match.group(1) if match else "(未配置)"
