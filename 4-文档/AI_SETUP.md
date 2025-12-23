# DeepSeek API 密钥配置说明

## 获取 DeepSeek API 密钥步骤：

1. **注册账户**
   - 访问 https://platform.deepseek.com/
   - 用邮箱/手机号注册（国内用户推荐）
   - 邮件验证后登录

2. **获取 API 密钥**
   - 进入"API Keys"页面
   - 点击"Create API Key"
   - 复制生成的密钥（形如 `REDACTEDxxx...`）

3. **配置环境变量**
   
   **方式 A：在项目根目录创建 `.env` 文件**
   ```
   DEEPSEEK_API_KEY=sk_你的API密钥
   ```
   
   **方式 B：直接设置系统环境变量**
   
   Windows PowerShell:
   ```powershell
   $env:DEEPSEEK_API_KEY = "sk_你的API密钥"
   ```
   
   Windows CMD:
   ```cmd
   set DEEPSEEK_API_KEY=sk_你的API密钥
   ```
   
   Linux/Mac:
   ```bash
   export DEEPSEEK_API_KEY="sk_你的API密钥"
   ```

4. **重启 FastAPI 应用**
   ```bash
   cd 1-后端代码
   python -m uvicorn app:app --reload --host 127.0.0.1 --port 5000
   ```

5. **测试连接**
   - 打开任何页面（patrol.html 或 admin.html）
   - 点击右下角 💬 浮球
   - 输入问题测试

## DeepSeek API 配额：

- 新注册用户：免费额度充足（约 RMB 500 - 1000 元等额）
- 定价低廉：价格约为 OpenAI 的 1/10
- 支持流式响应、批量请求等

## 常见问题：

**Q: 没有配置 API 密钥会怎样？**
A: 浮窗可以打开，但提交问题会返回"AI 服务尚未配置"的错误

**Q: 如何切换为其他 AI 模型（如 Claude、OpenAI）？**
A: 编辑 `routes/chat.py` 文件，修改 API 地址和请求格式即可

**Q: 可以离线使用吗？**
A: 当前版本依赖 DeepSeek API。如需离线，可改用 Ollama 或其他本地模型（需额外配置）

## 文件位置：

- 后端接口：[routes/chat.py](../../routes/chat.py)
- 前端组件：[templates/ai-assistant.html](../../templates/ai-assistant.html)
- 主应用：[app.py](../../app.py) - 已注册路由
