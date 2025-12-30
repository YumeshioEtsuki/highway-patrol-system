# 🚀 环境配置与启动指南

新成员快速上手指南。

## 前置要求

- Python 3.12+
- MySQL 8.0+
- VS Code (推荐)

## 第一次克隆与设置

### 1. 创建虚拟环境（如果尚未创建）

```bash
# 进入项目根目录
cd highway-patrol-system

# 创建虚拟环境（Python 3.12+）
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# macOS/Linux:
source .venv/bin/activate
```

### 2. 安装依赖

```bash
# 进入后端目录
cd 1-后端代码

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制模板为实际配置
cp .env.example .env

# 编辑 .env，填入你的数据库信息
# DATABASE_HOST=localhost
# DATABASE_PORT=3306
# DATABASE_USER=root
# DATABASE_PASSWORD=你的密码
# DATABASE_NAME=road_patrol_db
```

### 4. 初始化数据库

```bash
# 确保 MySQL 正在运行
# 然后启动后端，它会自动初始化数据库

# 或手动初始化
python utils/utils.py
```

## 启动后端

```bash
# 从 1-后端代码 目录
cd 1-后端代码

# 激活虚拟环境（如未激活）
# Windows: ..\\.venv\Scripts\Activate.ps1
# macOS/Linux: source ../.venv/bin/activate

# 启动开发服务器
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# 访问
# 前端页面: http://localhost:5000
# Swagger 文档: http://localhost:5000/docs
# ReDoc 文档: http://localhost:5000/redoc
```

## 常用开发命令

```bash
# 生成测试数据（1000条）
# 进入后端目录后，从浏览器管理页生成，或：
python -c "from models.tasks import generate_fake_records; print(generate_fake_records(count=1000, with_photos=False))"

# 清理测试数据
python -c "from models.tasks import clean_test_data; print(clean_test_data())"

# 重置数据库
python reset_db.py

# 检查数据库连接
python -c "from utils.config import settings; print(f'Host: {settings.DATABASE_HOST}, DB: {settings.DATABASE_NAME}')"
```

## 配置参考

### 环境变量 (.env)

```dotenv
# 数据库
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=REDACTED
DATABASE_NAME=road_patrol_db

# 应用
DEBUG=True
SECRET_KEY=your_secret_key_here
MAX_PAGE_SIZE=200

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# 文件上传
UPLOAD_FOLDER=photos
MAX_UPLOAD_SIZE=10485760

# CORS
ALLOW_ORIGINS=["http://localhost:3000"]

# 启动控制
SKIP_DB_INIT=False
```

## VS Code 配置

推荐扩展：
- Python (Microsoft)
- Pylance
- Database Client
- Thunder Client / REST Client

`.vscode/settings.json` 已自动配置 Pylance 以识别后端导入，无需额外设置。

## 项目目录速查

```
highway-patrol-system/
├── 1-后端代码/          FastAPI 应用
│   ├── app.py           主应用文件
│   ├── .env             开发环境配置（本地，不提交）
│   ├── .env.example     配置模板
│   ├── models/          数据库模型
│   ├── routes/          API 路由
│   ├── utils/           工具函数
│   └── templates/       前端模板
├── 3-数据库/            数据库脚本
├── docs/                文档（此目录）
└── 7-测试脚本/          测试与诊断脚本
```

## 故障排查

### 导入错误："无法解析导入 utils.utils"
- 确保从 `1-后端代码` 目录启动或运行脚本
- 检查 `python.analysis.extraPaths` 在 `.vscode/settings.json` 中配置了 `"1-后端代码"`

### 数据库连接失败
```bash
# 检查 MySQL 是否运行
mysql -u root -p

# 检查配置
python -c "from utils.config import db_config; print(db_config)"

# 检查表是否存在
mysql -u root -p road_patrol_db -e "SHOW TABLES;"
```

### 端口 5000 被占用
```bash
# 查找占用端口的进程
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# 使用不同端口启动
uvicorn app:app --port 5001
```

## 获取帮助

- 查看 API 文档: http://localhost:5000/docs
- 查阅项目文档: `docs/` 和 `4-文档/`
- 检查开发日志: `6-开发日志/`
- 运行诊断脚本: `python 7-测试脚本/diagnose_data.py`

---

**更新日期**: 2025-12-23
