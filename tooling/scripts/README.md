# 🎨 环境变量管理工具

用于方便地添加、查看和修改项目的环境变量配置。

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `add_config.py` | 核心脚本，执行实际的配置更新 |
| `manage_env.py` | 可视化 CLI 工具（推荐使用） |
| `manage_env.bat` | Windows 快捷启动脚本 |
| `manage_env.ps1` | PowerShell 启动脚本 |

## 🚀 使用方法

### 方法 1：可视化工具（推荐）

**Windows:**
```bash
# 方式 1: 双击 manage_env.bat
manage_env.bat

# 方式 2: PowerShell
.\manage_env.ps1

# 方式 3: 命令行
cd tooling\scripts
python manage_env.py
```

**Linux/Mac:**
```bash
cd tooling/scripts
python manage_env.py
```

然后按照菜单提示操作。

### 方法 2：命令行（直接调用）

```bash
# 基本用法
python add_config.py MY_KEY "my_value" --envs dev,test,demo

# 添加注释
python add_config.py MY_KEY "my_value" --envs dev,test,demo --comment "这是我的配置"

# 跳过 .env.example（仅更新环境文件）
python add_config.py MY_KEY "my_value" --envs dev,test,demo --skip-example
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
