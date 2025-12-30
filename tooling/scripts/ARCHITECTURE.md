# 环境变量管理工具 - 架构说明

## 📁 文件结构

```
tooling/scripts/
├── lib/                              # 📚 核心业务逻辑层
│   ├── __init__.py                   # 导出统一接口
│   ├── env_manager.py                # 环境变量管理器（Model）
│   ├── validators.py                 # 验证和推荐逻辑
│   └── ai_helper.py                  # AI 助手（NEW）
│
├── web/                              # 🌐 Web 界面层
│   ├── env_manager_app.py            # FastAPI 应用（Controller）
│   ├── templates/                    # Jinja2 模板（View）
│   │   ├── index.html               # 首页：可视化配置表格
│   │   ├── analyze.html             # 分析页：推荐值对比
│   │   ├── result.html              # 结果页：操作反馈
│   │   ├── list.html                # 列表页：所有配置
│   │   ├── help.html                # 帮助页：使用文档
│   │   └── error.html               # 错误页
│   └── static/                      # 静态资源
│
├── cli/                              # 🖥️ 命令行界面层
│   ├── manage_env.py                # 交互式 CLI
│   └── validate.py                  # 验证工具
│
├── env/                              # 📋 配置文件存储
│   ├── local.dev.env
│   ├── local.test.env
│   ├── local.demo.env
│   └── production.env
│
├── .env.ai                           # AI 配置文件
├── test_ai.py                        # AI 功能测试
└── README.md                         # 完整文档
```

## 🏗️ 架构设计

### 分层架构（MVC Pattern）

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                    │
│  ┌──────────────┐              ┌──────────────┐        │
│  │   Web UI     │              │   CLI Tool   │        │
│  │ (FastAPI)    │              │  (Interactive)│       │
│  └──────┬───────┘              └──────┬───────┘        │
│         │                             │                 │
└─────────┼─────────────────────────────┼─────────────────┘
          │                             │
          └──────────┬──────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  lib/                                            │   │
│  │  ├── EnvManager      (环境变量 CRUD)            │   │
│  │  ├── validators      (验证 + 推荐)              │   │
│  │  └── AIHelper        (AI 智能推荐)              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                   Data Access Layer                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  .env files  │    │  Ollama API  │    │  Static  │  │
│  │  (读写)      │    │  (AI 推荐)   │    │  (备选)  │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 核心类关系

```
┌─────────────────┐
│   EnvManager    │  管理 .env 文件读写
├─────────────────┤
│ + get_current_values()  │
│ + set_value()           │
│ + set_values_batch()    │
│ + get_all_keys()        │
└─────────────────┘
         │
         │ 被调用
         ▼
┌─────────────────┐
│   validators    │  验证和推荐
├─────────────────┤
│ + get_recommendations() │  ◄─┐
│ + validate_config()      │    │ 尝试使用 AI
│ + get_help_text()        │    │
└─────────────────┘          │
         │                    │
         │ 可选依赖           │
         ▼                    │
┌─────────────────┐          │
│   AIHelper      │  ─────────┘
├─────────────────┤
│ + is_available()         │
│ + get_env_recommendations() │
│ + get_help_text()        │
└─────────────────┘
         │
         │ 调用
         ▼
┌─────────────────┐
│  Ollama API     │  本地 AI 服务
│  (可选)          │
└─────────────────┘
```

## 🔄 数据流

### 场景 1：用户修改配置（Web 界面）

```
1. 用户访问首页
   GET / → env_manager_app.py
   ↓
2. 控制器调用 EnvManager
   manager.get_all_keys() + manager.get_current_values()
   ↓
3. 渲染表格显示所有配置
   templates/index.html
   ↓
4. 用户点击 "Edit" 按钮
   POST /analyze → env_manager_app.py
   ↓
5. 控制器请求推荐值
   get_recommendations(key, current_values, use_ai=True)
   ↓
6. validators 尝试 AI
   AIHelper.get_env_recommendations() → Ollama API
   ↓ (成功)
   返回 AI 推荐 + 说明
   ↓ (失败)
   返回静态推荐
   ↓
7. 渲染分析页面
   templates/analyze.html（显示当前值 vs 推荐值）
   ↓
8. 用户选择环境并应用
   POST /apply → env_manager_app.py
   ↓
9. 控制器调用 EnvManager
   manager.set_values_batch(key, envs, value)
   ↓
10. 写入 .env 文件
    tooling/env/*.env
```

### 场景 2：CLI 工具使用

```
1. 运行命令
   python manage_env.py
   ↓
2. 显示交互菜单
   cli/manage_env.py
   ↓
3. 用户选择操作
   如：修改环境变量
   ↓
4. CLI 调用相同的核心库
   from lib import EnvManager, get_recommendations
   ↓
5. 业务逻辑处理（与 Web 完全相同）
   EnvManager.set_value()
   ↓
6. 写入 .env 文件
```

## 🎯 设计优势

### 1. 分层清晰
- **表示层**：Web/CLI 可独立开发和测试
- **业务层**：核心逻辑可复用，易于单元测试
- **数据层**：.env 文件和 AI 服务解耦

### 2. 关注点分离
- `env_manager.py`：只负责文件 I/O
- `validators.py`：只负责验证和推荐
- `ai_helper.py`：只负责 AI 集成
- `env_manager_app.py`：只负责路由和请求处理

### 3. 可扩展性
- **添加新 UI**：实现新的表示层，复用 `lib/`
- **切换 AI 服务**：修改 `AIHelper`，不影响其他代码
- **添加新验证规则**：修改 `validators.py`，自动应用到 Web 和 CLI

### 4. 容错性
- AI 不可用时自动回退到静态推荐
- 验证失败时提供清晰的错误消息
- 文件操作失败时不影响其他环境

### 5. 可测试性
```python
# 核心逻辑独立，易于单元测试
def test_env_manager():
    manager = EnvManager(Path("/test/project"))
    assert manager.get_current_values("DEBUG") == {...}

def test_ai_fallback():
    # AI 不可用时的行为
    recommendations = get_recommendations("KEY", use_ai=False)
    assert recommendations == STATIC_RECOMMENDATIONS["KEY"]
```

## 🆚 对比：重构前 vs 重构后

| 方面 | 重构前 | 重构后 |
|------|--------|--------|
| **代码组织** | 单一脚本，混乱 | 分层架构，清晰 |
| **复用性** | 无法复用 | 核心库可被 Web/CLI/API 共享 |
| **扩展性** | 难以扩展 | 易于添加新功能 |
| **测试** | 难以测试 | 每层独立可测试 |
| **AI 集成** | 不支持 | 原生支持，可选启用 |
| **用户体验** | 命令行 | Web + CLI + 菜单 |
| **文档** | 无 | 完整 README + 注释 |

## 🔧 技术栈

- **Backend**: FastAPI (异步 Web 框架)
- **Template**: Jinja2 (模板引擎)
- **AI**: Ollama (本地 LLM 服务)
- **CLI**: Python argparse + interactive input
- **Testing**: Python unittest / pytest
- **Platform**: 跨平台 (Windows/Linux/macOS)

## 📝 最佳实践

1. **单一职责原则**：每个模块只做一件事
2. **依赖倒置**：高层模块不依赖低层模块（通过接口解耦）
3. **开放封闭原则**：对扩展开放，对修改封闭
4. **测试驱动**：核心逻辑先写测试
5. **文档优先**：代码即文档，清晰的注释和类型提示

## 🚀 后续改进计划

- [ ] 添加配置版本控制（Git 集成）
- [ ] 支持配置模板（快速初始化新环境）
- [ ] 配置差异对比工具
- [ ] Web 界面支持批量编辑
- [ ] 配置变更审计日志
- [ ] REST API 完整实现
- [ ] 配置加密存储（敏感信息）
- [ ] 支持更多 AI 模型（OpenAI, Claude）

## 📚 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://ollama.ai/)
- [12 Factor App](https://12factor.net/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
