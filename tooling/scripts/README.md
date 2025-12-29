# 🎨 环境变量管理工具 - 完整指南

本项目的环境变量管理工具已经按照行业规范进行了现代化重构。采用分层架构（MVC）、关注点分离、可复用的核心库，对标 Django、Spring Boot、Laravel 等企业级框架的设计模式。

---

## 📊 项目结构

```
tooling/scripts/
├── lib/                          # 🏛️ 核心业务逻辑（可复用库）
│   ├── env_manager.py            # 环境变量管理类（Model）
│   ├── validators.py             # 验证和推荐逻辑
│   └── __init__.py
├── cli/                          # 🖥️ 命令行工具（使用 lib）
│   ├── manage_env.py             # 交互式 CLI（Controller）
│   └── validate.py
├── web/                          # 🌐 Web 管理工具（使用 lib）
│   ├── app.py                    # FastAPI 应用
│   ├── templates/                # HTML 模板
│   ├── static/                   # CSS/JS 资源
│   └── __init__.py
├── env/                          # 📋 环境配置文件
│   ├── local.dev.env
│   ├── local.test.env
│   ├── local.demo.env
│   └── production.env
└── README.md                     # 本文档
```

---

## 🎯 为什么这个设计符合行业规范？

### ✅ 分层架构（MVC + 关注点分离）

| 层 | 位置 | 职责 | 对标框架 |
|----|------|------|---------|
| **Model** | `lib/env_manager.py` | 数据读写、业务逻辑 | Django Models, Eloquent |
| **Validator** | `lib/validators.py` | 数据验证、规则引擎 | Django Forms, Pydantic |
| **View** | `web/templates/` | UI 渲染 | Jinja2, Django Templates |
| **Controller** | `web/app.py`, `cli/manage_env.py` | 请求处理、路由 | Flask Routes, FastAPI |

**优势**：
- ✅ 核心逻辑独立，不依赖 UI 框架，易于测试
- ✅ Web 和 CLI 共享相同的业务逻辑（不重复代码）
- ✅ 未来可轻松扩展 REST API、移动应用等

### ✅ 可复用的核心库

```python
# lib/__init__.py 导出统一接口
from lib import EnvManager, validate_config, get_recommendations

# Web 使用它
from lib import EnvManager

# CLI 也使用它
from lib import EnvManager, validate_config

# 未来 API 也用它
# 一次修改，到处生效
```

### ✅ 多种启动方式（用户友好）

| 方式 | 用途 | 命令 |
|------|------|------|
| **Web 工具** | 可视化操作，最推荐 | `bin/env-manager-web.bat` |
| **菜单界面** | 新手友好，快速选择 | `bin/menu.bat` |
| **CLI 工具** | 命令行爱好者，脚本集成 | `python tooling/scripts/cli/manage_env.py` |

对标：Django `manage.py`、Laravel `artisan`

---

## 🚀 快速开始

### 方式 1：Web 工具（推荐 👍）

**最简单，最友好，最可视化！**

```bash
# Windows
.\bin\env-manager-web.bat

# Linux/macOS
bash bin/env-manager-web.sh

# PowerShell
.\bin\env-manager-web.ps1
```

然后在浏览器中打开：http://127.0.0.1:5051

**功能**：
- 📝 输入键名（如 `SKIP_DB_INIT`）
- 🔍 查看当前值和推荐值
- ✅ 一键应用推荐值
- 🎯 或输入自定义值应用
- 📋 查看所有环境的完整配置

### 方式 2：菜单界面（通用）

```bash
# Windows
.\bin\menu.bat

# 然后选择菜单选项
```

选项：
1. 🌐 Web 环境变量管理工具
2. 📟 CLI 环境变量管理工具
3. 🚀 项目启动（快速开发）
4. 🚀 项目启动（完整）
5. 📊 数据库检查

### 方式 3：CLI 工具（高级用户）

```bash
cd tooling/scripts
python manage_env.py
```

交互式菜单：
1. 查看配置
2. 添加新配置
3. 修改环境变量
4. 编辑单个文件
5. 分组建议与批量应用

---

## 🏗️ 核心类和函数

### `lib.EnvManager`

```python
from lib import EnvManager
from pathlib import Path

# 创建管理器
manager = EnvManager(Path("/path/to/project"))

# 获取所有环境的键值
current = manager.get_current_values("SKIP_DB_INIT")
# → {"dev": "0", "test": "0", "demo": "0", "prod": "1"}

# 设置单个环境的值
success = manager.set_value("SKIP_DB_INIT", "dev", "0")

# 批量设置多个环境的值
updated, failed = manager.set_values_batch(
    "LOG_LEVEL", 
    ["dev", "test"], 
    "DEBUG"
)
# → (2, []) 成功更新 2 个环境

# 获取所有出现过的键
all_keys = manager.get_all_keys()

# 验证文件语法
is_valid, msg = manager.validate_syntax(path)
```

### `lib.validators`

```python
from lib import get_recommendations, validate_config, get_help_text

# 获取推荐值
rec = get_recommendations("SKIP_DB_INIT")
# → {"dev": "0", "test": "0", "demo": "0", "prod": "1"}

# 验证配置值
is_valid, msg = validate_config("LOG_LEVEL", "INVALID")
# → (False, "应为 DEBUG,INFO,WARNING,ERROR,CRITICAL之一，收到: INVALID")

# 获取帮助文本
help_text = get_help_text("SECURE_MODE")
# → "安全模式。0=从.env读取配置, 1=仅使用系统环境变量。..."
```

---

## 🔧 现有的配置项和推荐值

| 配置项 | 含义 | 推荐值 |  |  |  |
|--------|------|--------|-------|--------|--------|
|  | | dev | test | demo | prod |
| **SKIP_DB_INIT** | 跳过数据库初始化 | 0 | 0 | 0 | 1 |
| **SECURE_MODE** | 安全模式（仅用系统环境变量） | 0 | 0 | 0 | 1 |
| **DEBUG** | 调试模式 | True | True | False | False |
| **LOG_LEVEL** | 日志级别 | DEBUG | DEBUG | INFO | WARNING |
| **REDIS_CACHE_ENABLED** | 启用 Redis 缓存 | 1 | 1 | 1 | 1 |
| **DEFAULT_ADMIN_PASSWORD** | 默认管理员密码 | (自动生成) | (自动生成) | (自动生成) | (自动生成) |

---

## 📚 扩展与集成示例

### 添加新的配置项

编辑 `lib/validators.py` 中的 `get_recommendations()` 函数：

```python
def get_recommendations(key: str) -> Dict[str, str]:
    recommendations = {
        # ... 现有配置 ...
        
        # 添加新配置
        "MY_NEW_CONFIG": {
            "dev": "dev_value",
            "test": "test_value",
            "demo": "demo_value",
            "prod": "prod_value",
        },
    }
    
    # ...
```

然后在 Web 和 CLI 中自动生效！

### 在 CI/CD 中使用

```yaml
# .github/workflows/config.yml
name: Update Config

on: [workflow_dispatch]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: |
          from pathlib import Path
          from tooling.scripts.lib import EnvManager
          
          manager = EnvManager(Path.cwd())
          manager.set_values_batch("LOG_LEVEL", ["prod"], "WARNING")
```

### 添加 REST API

在 `web/app.py` 中添加：

```python
@app.post("/api/config/{key}")
async def set_config(key: str, envs: list, value: str):
    """API 端点"""
    is_valid, msg = validate_config(key, value)
    if not is_valid:
        return {"error": msg}
    
    updated, failed = manager.set_values_batch(key, envs, value)
    return {"updated": updated, "failed": failed}
```

核心逻辑 (`lib/env_manager.py`) 完全不变！

---

## 📖 学习资源

本设计参考了业界最佳实践：

1. **Django Framework** (Python) - 分层架构、Admin 管理界面
2. **Spring Boot** (Java) - 依赖注入、配置管理
3. **Laravel** (PHP) - Artisan CLI、优雅的 API
4. **Express.js** (Node.js) - 中间件模式、路由
5. **12 Factor App** - 配置外部化原则
6. **Clean Code** (Robert C. Martin) - 关注点分离

---

## ❓ FAQ

**Q: 为什么不直接编辑 .env 文件？**
A: Web 工具提供了：
- 可视化界面（无需记住文件路径）
- 自动验证（防止输入错误）
- 推荐值建议（降低配置难度）
- 多文件同步更新（dev/test/demo/prod 一键应用）

**Q: 安全吗？**
A: 
- Web 工具仅在本地运行（`127.0.0.1:5051`）
- 不会上传敏感信息
- 生产环境推荐使用 SECURE_MODE（从系统环境变量读取）

**Q: 能自动化修改配置吗？**
A: 可以！直接使用 `lib.EnvManager`：
```python
from lib import EnvManager
manager = EnvManager(project_root)
manager.set_value("KEY", "prod", "value")
```

**Q: 支持 Windows 和 Linux 吗？**
A: 完全支持！
- Windows: `.bat` 和 `.ps1` 脚本
- Linux/macOS: `.sh` 脚本
- 跨平台: Python 脚本

---

## 总结

✨ **这是一个符合行业规范的现代化工具链：**

1. **分层清晰** - Model/View/Controller，对标 Django/Spring Boot
2. **可复用** - 核心逻辑独立，Web/CLI/API 共享
3. **易测试** - 业务逻辑与 UI 分离
4. **易扩展** - 添加新功能不影响现有代码
5. **用户友好** - 多种交互方式（Web/CLI/菜单）
6. **文档完整** - 代码清晰，说明详细
7. **生产就绪** - 安全、多平台、高性能

🚀 **开始使用**：
```bash
.\bin\env-manager-web.bat
```

## 📝 示例

### 添加一个新的 API KEY

```
菜单选择: 1 (添加新配置)
输入配置键名: MY_API_KEY
输入值: sk-abc123def456
输入注释: 用于第三方API调用
选择环境: 1,2,3 (dev, test, demo)
确认: y
```

结果：
- ✅ `.env.example` 添加了 `MY_API_KEY=` 的注释说明
- ✅ `tooling/env/local.dev.env` 添加了 `MY_API_KEY=sk-abc123def456`
- ✅ `tooling/env/local.test.env` 添加了 `MY_API_KEY=sk-abc123def456`
- ✅ `tooling/env/local.demo.env` 添加了 `MY_API_KEY=sk-abc123def456`

## 🔍 配置文件结构

```
项目根目录/
├── .env.example              ← 模板（setup 时使用）
├── .env                      ← 当前配置（不提交到 Git）
└── tooling/env/
    ├── local.dev.env         ← 开发环境（startup_full.bat 默认）
    ├── local.test.env        ← 测试环境
    ├── local.demo.env        ← 演示环境
    └── production.env        ← 生产环境
```

## ⚙️ 工作流程

```
add_config.py / manage_env.py
    ↓
更新 .env.example（为新用户提供配置模板）
    ↓
更新 tooling/env/*.env（为不同环境配置）
    ↓
start_server.py 启动时加载选定的环境文件到 .env
    ↓
应用程序读取最终的 .env 配置
```

## 💡 最佳实践

1. **添加新配置时**：使用可视化工具 `manage_env.py`，会自动更新所有必要的文件
2. **紧急修改密码**：直接编辑对应的 `.env` 文件（如果配置已存在）
3. **提交代码**：确保 `.env` 在 `.gitignore` 中，不要提交真实密码

## 🔒 安全建议

- `.env` 文件包含敏感信息，始终保持在 `.gitignore` 中
- 生产环境敏感配置应使用系统环境变量或密钥管理服务
- 定期检查 `.env.example` 中是否有遗漏的新配置项

## 🐛 常见问题

### Q: 添加配置后仍未生效？
A: 检查是否需要重启应用。大多数配置在启动时加载。

### Q: 可以删除或修改已添加的配置吗？
A: 当前工具不支持删除，但支持手动编辑文件。管理工具的删除功能将在后续版本中添加。

### Q: .env.example 中留空的配置值如何填充？
A: 运行 `setup.bat` 时按提示填入，或手动编辑 `.env` 文件。
