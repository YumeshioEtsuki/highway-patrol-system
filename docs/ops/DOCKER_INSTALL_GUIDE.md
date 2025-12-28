# Docker Desktop 安装指南

## 📦 为什么选择 Docker + Redis？

### 优势
- ✅ **一键安装** - 无需手动配置环境变量
- ✅ **自动更新** - 始终使用最新稳定版
- ✅ **数据持久化** - 数据自动保存，重启不丢失
- ✅ **资源隔离** - 不污染系统环境
- ✅ **跨平台** - Windows/Mac/Linux 统一体验
- ✅ **自动重启** - 开机自动启动 Redis

### 对比传统安装

| 特性 | Docker Redis | Windows 原生版 |
|-----|-------------|--------------|
| 安装难度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 更新维护 | 自动 | 手动下载 |
| 数据安全 | 持久化卷 | 手动备份 |
| 版本选择 | 任意版本 | 5.0.14（停更）|
| 资源占用 | ~30MB | ~10MB |

---

## 🚀 Docker Desktop 安装步骤

### 步骤1：下载 Docker Desktop

**官方下载地址：**
https://www.docker.com/products/docker-desktop/

**直接下载链接（Windows）：**
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

**系统要求：**
- Windows 10 64位：专业版、企业版或教育版（Build 19041 或更高版本）
- Windows 11 64位：家庭版或专业版
- 启用 WSL 2 功能
- 至少 4GB RAM

### 步骤2：安装 Docker Desktop

1. **运行安装程序**
   - 双击 `Docker Desktop Installer.exe`
   - 勾选 "Use WSL 2 instead of Hyper-V"（推荐）
   - 点击 "Ok" 开始安装

2. **等待安装完成**
   - 安装过程约 3-5 分钟
   - 可能需要重启电脑

3. **首次启动**
   - 安装完成后启动 Docker Desktop
   - 接受服务条款
   - 跳过登录（可选）

### 步骤3：启用 WSL 2

如果 Docker 提示需要 WSL 2：

```powershell
# 以管理员身份运行 PowerShell

# 1. 启用 WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. 重启电脑
Restart-Computer

# 4. 下载并安装 WSL 2 Linux 内核更新包
# https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

# 5. 设置 WSL 2 为默认版本
wsl --set-default-version 2
```

### 步骤4：验证安装

打开 PowerShell 或 CMD：

```bash
# 查看 Docker 版本
docker --version
# 预期输出: Docker version 24.x.x, build xxxxxxx

# 测试运行
docker run hello-world
# 应该看到 "Hello from Docker!" 消息
```

---

## 🐳 启动 Redis

### 方式1：使用启动脚本（推荐）

```bash
# Windows CMD
.\bin\start_redis.bat

# PowerShell
.\bin\start_redis.ps1
```

### 方式2：手动命令

```bash
# 创建并启动 Redis 容器
docker run -d \
  --name highway-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  --restart unless-stopped \
  redis:7-alpine redis-server --appendonly yes

# 验证运行状态
docker ps | findstr redis

# 测试连接
docker exec -it highway-redis redis-cli ping
# 预期输出: PONG
```

---

## ⚙️ Docker Desktop 配置（可选优化）

### 资源限制

打开 Docker Desktop → Settings → Resources

**推荐配置：**
- CPU：2-4 核
- Memory：2-4 GB
- Swap：1 GB
- Disk：20 GB

### 自动启动

Settings → General
- ✅ Start Docker Desktop when you log in
- ✅ Use the WSL 2 based engine

### 镜像加速（中国大陆）

Settings → Docker Engine，添加镜像源：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

点击 "Apply & Restart"

---

## 🔍 常见问题

### 问题1：Docker Desktop 启动失败

**错误信息：** "Docker Desktop - starting..."一直转圈

**解决方案：**
```bash
# 1. 完全退出 Docker Desktop
# 右键托盘图标 → Quit Docker Desktop

# 2. 清理 Docker 数据（谨慎！会删除所有容器）
rd /s /q %LOCALAPPDATA%\Docker

# 3. 重启 Docker Desktop
```

### 问题2：WSL 2 安装失败

**错误信息：** "WSL 2 installation is incomplete"

**解决方案：**
1. 下载 WSL 2 内核更新包：
   https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
2. 安装后重启 Docker Desktop

### 问题3：端口冲突

**错误信息：** "port is already allocated"

**解决方案：**
```bash
# 查找占用 6379 的进程
netstat -ano | findstr :6379

# 停止 Docker 容器
docker stop highway-redis

# 或使用其他端口
docker run -d --name highway-redis -p 6380:6379 redis:7-alpine
```

### 问题4：容器无法访问

**错误信息：** "Connection refused"

**解决方案：**
```bash
# 1. 检查容器状态
docker ps

# 2. 查看容器日志
docker logs highway-redis

# 3. 重启容器
docker restart highway-redis

# 4. 检查防火墙
# Windows Defender 防火墙 → 允许应用通过防火墙 → 勾选 Docker Desktop
```

---

## 📚 Docker 基础命令

### 容器管理

```bash
# 查看所有容器
docker ps -a

# 查看运行中的容器
docker ps

# 启动容器
docker start <container_name>

# 停止容器
docker stop <container_name>

# 重启容器
docker restart <container_name>

# 删除容器
docker rm <container_name>

# 删除所有停止的容器
docker container prune
```

### 镜像管理

```bash
# 查看所有镜像
docker images

# 拉取镜像
docker pull redis:7-alpine

# 删除镜像
docker rmi redis:7-alpine

# 清理未使用的镜像
docker image prune -a
```

### 数据卷管理

```bash
# 查看所有数据卷
docker volume ls

# 查看数据卷详情
docker volume inspect redis-data

# 删除数据卷（慎用！）
docker volume rm redis-data

# 清理未使用的数据卷
docker volume prune
```

### 日志和调试

```bash
# 查看容器日志
docker logs highway-redis

# 实时日志
docker logs -f highway-redis

# 最近100行
docker logs --tail 100 highway-redis

# 进入容器终端
docker exec -it highway-redis sh

# 查看容器资源使用
docker stats highway-redis
```

---

## 🎓 学习资源

### 官方文档
- Docker 官方文档: https://docs.docker.com/
- Redis 官方文档: https://redis.io/docs/
- Docker Hub Redis: https://hub.docker.com/_/redis

### 视频教程
- Docker 入门教程: https://www.bilibili.com/video/BV1og4y1q7M4
- Redis 从入门到精通: https://www.bilibili.com/video/BV1Rv41177Af

### 推荐阅读
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Redis 性能优化](https://redis.io/docs/management/optimization/)
- [本项目 Redis 使用说明](../4-文档/功能说明/REDIS_CELERY说明.md)

---

## ✅ 安装完成检查清单

- [ ] Docker Desktop 已安装并运行
- [ ] WSL 2 已启用（Windows）
- [ ] `docker --version` 命令正常
- [ ] Redis 容器已创建并运行
- [ ] `docker exec highway-redis redis-cli ping` 返回 PONG
- [ ] Python 可连接 Redis：`python -c "import redis; r=redis.Redis(); print(r.ping())"`
- [ ] FastAPI 应用启动无错误

---

**下一步：** 运行 `.\bin\startup_full.bat` 启动完整系统！

**最后更新：** 2025-12-26  
**Docker Desktop 版本：** 4.25+
