# 🔧 本地开发规范

本地开发中的最佳实践与规范。

## 开发环境配置

### 激活虚拟环境

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 进入后端开发目录

```bash
cd 1-后端代码
```

## 代码风格

### 编码规范

项目使用 `.editorconfig` 统一编码风格：

- **Python**: 4 个空格缩进，UTF-8 编码
- **JavaScript/TypeScript**: 2 个空格缩进
- **SQL**: 2 个空格缩进
- **Markdown**: 保留尾部空行

VS Code 已自动支持该配置，确保启用 "EditorConfig for VS Code" 扩展。

### Python 代码规范

- 遵循 PEP 8 标准
- 使用类型注解：`def get_user(user_id: int) -> User:`
- 导入顺序：标准库 → 第三方库 → 本地模块
- 函数/类前后各空一行

### 提交规范

Git 提交信息格式：

```
<type>: <subject>

<body>
<footer>
```

**类型** (type):
- `feat`: 新功能
- `fix`: 修复问题
- `refactor`: 重构代码
- `test`: 添加测试
- `docs`: 文档更新
- `chore`: 工具/依赖更新

**示例**:

```
feat: 添加用户导出功能

支持导出所有用户数据为 Excel 格式，包括审计日志。

Closes #123
```

## 本地测试

### 启动开发服务器

```bash
cd 1-后端代码
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### API 测试

访问 Swagger UI 进行交互式测试：

```
http://localhost:5000/docs
```

或使用命令行工具 (httpx/curl)：

```bash
# 测试登录
curl -X POST "http://localhost:5000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 数据库操作

```bash
# 连接数据库
mysql -u root -p road_patrol_db

# 查询表
SELECT COUNT(*) FROM InspectionRecord;
SELECT * FROM User;
```

### 运行测试脚本

```bash
# 诊断数据库
python 7-测试脚本/diagnose_data.py

# 测试 API
python 7-测试脚本/test_admin_api.py

# 生成测试数据
python 7-测试脚本/add_hangzhou_data.py
```

## 日志与调试

### 启用调试输出

在 `1-后端代码/.env` 中：

```dotenv
DEBUG=True
```

### 查看日志

```bash
# 后端日志位置
1-后端代码/logs/

# 实时查看（Linux/macOS）
tail -f 1-后端代码/logs/app.log
```

### 使用 Python 调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 VS Code 调试器（F5）
```

## 依赖管理

### 安装新包

```bash
pip install package_name

# 更新 requirements.txt
pip freeze > 1-后端代码/requirements.txt
```

### 查看已安装包

```bash
pip list
pip show package_name
```

## 常见开发任务

### 添加新 API 端点

1. 在 `models/schemas.py` 定义请求/响应模型
2. 在 `models/tasks.py` 编写业务逻辑
3. 在 `routes/` 中创建端点
4. 在 `app.py` 中注册路由
5. 在 `/docs` 中验证

### 修改数据库表结构

1. 编辑 `models/schema.py` 中的 SQL
2. 或创建新的 `.sql` 文件放在 `3-数据库/`
3. 运行 `python reset_db.py` 或执行 SQL 脚本
4. 更新相关模型与任务函数

### 更新依赖版本

```bash
# 查看过期的包
pip list --outdated

# 更新单个包
pip install --upgrade package_name

# 更新 requirements.txt
pip freeze > 1-后端代码/requirements.txt
```

## IDE 配置

### VS Code 推荐扩展

- **Python** (Microsoft)
- **Pylance** (类型检查)
- **Database Client** (数据库浏览)
- **Thunder Client** / **REST Client** (API 测试)
- **EditorConfig for VS Code** (编码规范)

### 调试配置

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app:app", "--reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/1-后端代码",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/1-后端代码"
      }
    }
  ]
}
```

然后按 **F5** 启动调试。

## 常见问题

### Q: 导入错误 "无法解析导入 utils.utils"
A: 确保从 `1-后端代码` 目录启动或运行脚本。`.vscode/settings.json` 中已配置 `extraPaths`。

### Q: 数据库连接超时
A: 检查 MySQL 是否正在运行，以及 `.env` 中的主机/用户/密码配置是否正确。

### Q: 端口 5000 被占用
A: 使用 `python 1-后端代码/start_server.py` 自动处理，或手动指定其他端口：
```bash
uvicorn app:app --port 5001
```

### Q: 如何清除缓存数据
A: 统计数据缓存可通过调用 `/api/admin/clean-test-data` 清除；或重启后端服务器。

---

**更新日期**: 2025-12-23
