# 📋 脚本使用指南

项目中各类脚本的用途与使用方法。

## 目录结构

```
scripts/
├── dev/       开发与测试脚本
├── deploy/    部署脚本（规划）
└── migrate/   数据迁移脚本（规划）
```

## 开发脚本 (scripts/dev/)

### 数据相关

- **generate_fake_records** - 生成测试数据
  ```bash
  python ../7-测试脚本/add_hangzhou_data.py
  ```

- **cleanup** - 清理测试数据
  ```bash
  python ../7-测试脚本/cleanup.py
  ```

- **final_verification** - 验证数据生成结果
  ```bash
  python ../7-测试脚本/final_verification.py
  ```

### 诊断脚本

- **diagnose_data** - 诊断数据库状态
  ```bash
  python ../7-测试脚本/diagnose_data.py
  ```

- **comprehensive_check** - 全面检查
  ```bash
  python ../7-测试脚本/comprehensive_check.py
  ```

### API 测试

- **test_admin_api** - 测试管理员 API
  ```bash
  python ../7-测试脚本/test_admin_api.py
  ```

- **test_export** - 测试导出功能
  ```bash
  python ../7-测试脚本/test_export_excel.py
  ```

## 使用示例

### 场景 1: 初始化测试数据

```bash
cd 1-后端代码
# 启动后端
uvicorn app:app --host 0.0.0.0 --port 5000

# 新终端
cd 7-测试脚本
python add_hangzhou_data.py
```

### 场景 2: 全面诊断

```bash
cd 1-后端代码
python ../7-测试脚本/diagnose_data.py
```

### 场景 3: 清理并重置

```bash
cd 1-后端代码
python reset_db.py
python ../7-测试脚本/cleanup.py
```

## 常见脚本清单

| 脚本 | 位置 | 用途 |
|------|------|------|
| `add_hangzhou_data.py` | 7-测试脚本 | 生成杭州地区测试数据 |
| `cleanup.py` | 7-测试脚本 | 清理所有测试数据 |
| `diagnose_data.py` | 7-测试脚本 | 诊断数据库状态 |
| `test_admin_api.py` | 7-测试脚本 | 测试管理员 API |
| `reset_db.py` | 1-后端代码 | 重置数据库 |
| `start_server.py` | 1-后端代码 | 自动启动服务器并处理端口冲突 |

## 脚本开发规范

新增脚本时，请遵循：

1. **位置**: 放在 `7-测试脚本/` 或 `scripts/dev/`
2. **命名**: 使用 `snake_case`，清晰描述用途
3. **文档**: 脚本顶部注释说明用途
4. **错误处理**: 包含异常捕获和友好提示
5. **日志**: 重要操作添加日志输出

### 脚本模板

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本描述：说明脚本的用途

用法:
    python script_name.py [参数]

示例:
    python script_name.py --verbose
"""

import sys
from pathlib import Path

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent.parent / '1-后端代码'))

def main():
    """主函数"""
    try:
        # 你的代码
        print("✅ 操作成功")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

**更新日期**: 2025-12-23
