# 🔐 安全配置指南

## 📋 快速配置步骤

### 1. 创建本地配置文件

在项目根目录执行：

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

或手动复制 `.env.example` 并重命名为 `.env`。

### 2. 修改密码

打开 `.env` 文件，修改以下配置为真实值：

```env
DATABASE_PASSWORD=你的MySQL数据库密码
JWT_SECRET_KEY=随机生成的密钥（至少32位）
SECRET_KEY=随机生成的密钥（至少32位）
```

**生成强密钥示例**（PowerShell）：
```powershell
# 生成 32 字节随机密钥
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

### 3. 验证配置

启动应用时，系统会自动加载 `.env` 文件：

```powershell
# 方式1：使用启动脚本（推荐）
.\bin\startup_full.bat

# 方式2：直接启动
cd "1-后端代码"
python -m uvicorn app:app --reload
```

如果密码未配置，会看到明确的错误提示：
```
ValueError: DATABASE_PASSWORD 未配置！
请设置环境变量 DATABASE_PASSWORD 或在 .env 文件中配置 DATABASE_PASSWORD=your_password
```

---

## 🚀 生产环境部署

### Windows 服务器

使用系统环境变量（更安全）：

```powershell
# 设置永久环境变量（需管理员权限）
[System.Environment]::SetEnvironmentVariable("DATABASE_PASSWORD", "your_password", "Machine")

# 或仅当前会话
$env:DATABASE_PASSWORD = "your_password"
```

### Docker 部署

使用 `docker-compose.yml`：

```yaml
services:
  app:
    build: .
    environment:
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
    env_file:
      - .env  # 或使用 Docker secrets
```

### 云平台

- **Azure App Service**: 应用设置 → 新增应用程序设置
- **AWS Elastic Beanstalk**: 配置 → 软件 → 环境属性
- **阿里云/腾讯云**: 参考各平台环境变量配置文档

---

## 🔒 安全模式（SECURE_MODE）

在生产/CI 环境，建议启用安全模式：不读取任何 `.env` 文件，仅使用系统环境变量。

```bat
set SECURE_MODE=1
set DB_PASSWORD=your_password
rem 也可使用：set DATABASE_PASSWORD=your_password
rem 可选：Redis/Celery 别名支持
rem   set REDIS_PASS=your_redis_password
rem   set BROKER_URL=redis://localhost:6379/1
rem   set RESULT_BACKEND=redis://localhost:6379/2

.\bin\startup_full.bat
rem 或
.\bin\startup.bat
```

关闭安全模式，恢复 `.env` 模式：

```bat
set SECURE_MODE=0
.\bin\startup_full.bat
```

---

## ⚠️ 安全注意事项

### ❌ 禁止行为
1. **永远不要提交 `.env` 文件到 Git**
2. **不要在代码中硬编码密码**
3. **不要将密码写入日志文件**
4. **不要通过 URL 参数传递密码**

### ✅ 推荐做法
1. **使用 `.env.example` 作为配置模板**（只包含键名，不含真实值）
2. **团队协作时通过安全渠道共享密码**（如密码管理器）
3. **生产环境使用专业密钥管理服务**：
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
4. **定期轮换密码**（建议每季度）
5. **不同环境使用不同密码**（开发/测试/生产）

---

## 🔧 故障排查

### 问题1: "DATABASE_PASSWORD 未配置"

**原因**: `.env` 文件不存在或密码字段为空

**解决**:
```powershell
# 1. 检查文件是否存在
Test-Path .env

# 2. 查看文件内容
Get-Content .env | Select-String "DATABASE_PASSWORD"

# 3. 如果不存在，从示例复制
Copy-Item .env.example .env
```

### 问题2: ".env 文件无效"

**原因**: 文件编码问题或格式错误

**解决**:
- 确保文件使用 UTF-8 编码（无 BOM）
- 每行格式为 `KEY=VALUE`（等号两边不要有空格）
- 不要用引号包裹值（除非值本身包含空格）

### 问题3: "环境变量未生效"

**检查优先级**（从高到低）：
1. 系统环境变量
2. `.env` 文件
3. 代码中的默认值

```powershell
# 查看当前环境变量
$env:DATABASE_PASSWORD

### 问题4: Celery/Redis 连接配置

**环境变量说明：**
- 支持 `CELERY_BROKER_URL` 与别名 `BROKER_URL`
- 支持 `CELERY_RESULT_BACKEND` 与别名 `RESULT_BACKEND`
- 支持 `REDIS_PASSWORD` 与别名 `REDIS_PASS`

**示例（安全模式）**
```bat
set SECURE_MODE=1
set BROKER_URL=redis://localhost:6379/1
set RESULT_BACKEND=redis://localhost:6379/2
set REDIS_PASS=your_redis_password
.\bin\startup_full.bat
```
```

---

## 📚 相关文档

- [启动指南](ops/STARTUP_GUIDE.md)
- [部署文档](../4-文档/核心文档/SETUP.md)
- [API 文档](../4-文档/核心文档/API接口文档.md)

---

## 🆘 需要帮助？

如遇问题，请检查：
1. `.env` 文件是否存在于项目根目录
2. 密码中是否包含特殊字符（如需转义）
3. 是否安装了 `python-dotenv` 依赖

```powershell
pip show python-dotenv
```
