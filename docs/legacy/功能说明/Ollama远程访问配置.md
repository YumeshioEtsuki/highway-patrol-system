# Ollama 远程访问配置指南

## 当前架构
开发机既是服务器，其他设备通过局域网访问后端，后端调用本机Ollama。

## Windows 配置步骤

### 1. 设置 Ollama 环境变量
打开 PowerShell（管理员）：

```powershell
# 设置允许所有IP访问
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')

# 或设置为机器用户变量（推荐）
setx OLLAMA_HOST "0.0.0.0:11434"
```

### 2. 重启 Ollama 服务
关闭当前 Ollama 进程，然后重新启动：

```powershell
# 停止 Ollama
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# 启动 Ollama（从开始菜单或命令行）
ollama serve
```

### 3. 验证配置
在**其他设备**上测试连接：

```powershell
# 替换 YOUR_SERVER_IP 为开发机的局域网IP（如 192.168.1.100）
curl http://YOUR_SERVER_IP:11434/api/tags
```

应该返回模型列表（包含 qwen:7b）。

### 4. 更新后端配置（已完成）
`.env` 文件已配置：
```env
OLLAMA_HOST=0.0.0.0
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen:7b
```

### 5. 防火墙设置
如果其他设备无法访问，需要开放端口：

```powershell
# 添加防火墙入站规则
New-NetFirewallRule -DisplayName "Ollama API" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow

# 同时开放后端端口
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 使用方式

### 本机访问（开发机）
- 后端：http://127.0.0.1:5000
- Ollama：自动连接本机

### 局域网其他设备访问
- 后端：http://你的IP:5000
- AI助手会自动通过后端调用Ollama，无需额外配置

## 安全提示
- `0.0.0.0` 表示监听所有网络接口
- 仅在信任的局域网内使用
- 如需外网访问，建议使用VPN或反向代理（如nginx）

## 故障排查

### 问题1：其他设备访问AI助手报错"Ollama未启动"
- 检查Ollama是否以 `0.0.0.0:11434` 监听
- 运行：`netstat -ano | Select-String "11434"`
- 应该看到 `0.0.0.0:11434` 或 `[::]:11434`

### 问题2：防火墙阻止
- 临时关闭防火墙测试
- 或添加上述防火墙规则

### 问题3：无法获取开发机IP
```powershell
# 查看本机局域网IP
ipconfig | Select-String "IPv4"
```

## 快速验证清单
- [ ] Ollama 监听 0.0.0.0:11434
- [ ] 防火墙开放 11434 和 5000 端口
- [ ] 其他设备能 ping 通开发机
- [ ] 访问 http://开发机IP:5000 能看到后台页面
- [ ] AI助手能正常回复
