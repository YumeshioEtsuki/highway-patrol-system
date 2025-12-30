# 🚀 如何立即开始使用 Celery 任务队列

## 当前状态
✅ **代码 100% 完成**  
✅ **依赖已安装**  
✅ **文档已准备就绪**  
⏳ **需要启动 Redis 服务**

---

## 🎯 3 步快速启动（预计 5 分钟）

### Step 1: 选择并安装 Redis（3 选 1）

#### 🥇 选项 A：Docker（最简单，推荐）
```bash
# 1. 下载并安装 Docker Desktop
# 访问: https://www.docker.com/products/docker-desktop
# 下载适合 Windows 的安装包

# 2. 安装完成后，打开 PowerShell 运行：
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
.\start_redis.ps1

# 如果脚本检测到 Docker，会自动启动 Redis 容器
```

#### 🥈 选项 B：Memurai（Windows 原生，最稳定）
```bash
# 1. 访问 https://www.memurai.com/get-memurai
# 2. 下载 Memurai Installer
# 3. 双击安装，默认选项即可
# 4. 安装后自动作为 Windows 服务运行
# 5. 验证安装：
redis-cli ping
# 应返回: PONG
```

#### 🥉 选项 C：WSL2 + Redis（Linux 方式）
```bash
# 1. 启用 WSL2（管理员 PowerShell）
wsl --install

# 2. 重启计算机

# 3. 打开 Ubuntu 终端，运行：
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# 4. 验证：
redis-cli ping
# 应返回: PONG
```

---

### Step 2: 启动 Celery Worker
```powershell
# 打开 PowerShell，进入后端目录
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"

# 方式 A：使用脚本（会打开 3 个窗口：Worker + Beat + Flower）
.\start_celery.ps1

# 方式 B：只启动 Worker（最简单）
celery -A celery_app worker --loglevel=info --pool=solo -Q photo,ai,report,maintenance
```

成功标志：
```
[INFO] Connected to redis://localhost:6379/1
[INFO] mingle: searching for neighbors
[INFO] mingle: all alone
[INFO] celery ready.
```

---

### Step 3: 启动后端并测试
```powershell
# 新开一个 PowerShell 终端
cd "d:\MySQL Project\highway-patrol-system\1-后端代码"
set SKIP_DB_INIT=1
uvicorn app:app --host 0.0.0.0 --port 5000

# 后端启动后，新开第三个终端运行测试
python test_celery_tasks.py
```

---

## 📋 测试检查清单

运行 `test_celery_tasks.py` 后，您应该看到：

- ✅ **Celery 连接测试**: 通过（发现 Worker）
- ✅ **照片压缩测试**: 通过（如果有测试图片）
- ⚠️ **AI 质量检查**: 需要 Ollama 服务
- ✅ **报告导出测试**: 通过
- ✅ **任务状态查询**: 通过

---

## 🎨 在 Swagger UI 中测试

1. 打开浏览器: http://127.0.0.1:5000/docs

2. 找到 **tasks** 分组

3. 测试 `POST /api/tasks/photo/compress`:
   ```json
   {
     "photo_path": "photos/test.jpg",
     "quality": 85
   }
   ```
   
   响应:
   ```json
   {
     "task_id": "abc123-456-def...",
     "status": "PENDING"
   }
   ```

4. 使用返回的 `task_id` 查询状态:
   `GET /api/tasks/status/{task_id}`

---

## 🖥️ 监控界面（可选）

### Flower Web UI
```bash
# 如果运行了 start_celery.ps1，Flower 已自动启动
# 访问: http://127.0.0.1:5555
```

功能：
- 📊 实时查看任务队列状态
- 📈 任务执行统计图表
- 🔍 搜索和查看历史任务
- ⏸️ 暂停/恢复 Worker

---

## 🤖 启动 AI 功能（可选）

如果您想测试 AI 质量检查功能：

```bash
# 1. 启动 Ollama 服务
ollama serve

# 2. 新开终端，确认模型存在
ollama list
# 应该看到: qwen:7b

# 3. 如果没有，拉取模型
ollama pull qwen:7b

# 4. 在 Swagger UI 中测试
POST /api/tasks/photo/quality-check
{
  "photo_path": "photos/test.jpg"
}
```

---

## ❓ 遇到问题？

### 问题 1: Redis 连接失败
```
[ERROR] Consumer: Cannot connect to redis://localhost:6379/1
```

**解决**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 如果没有响应，重新启动 Redis:
# Docker 方式:
docker restart redis-celery

# Memurai 方式:
net start Memurai
```

---

### 问题 2: Worker 看不到任务
```
任务状态一直是 PENDING
```

**解决**:
```bash
# 1. 确认 Worker 正在运行
celery -A celery_app inspect active

# 2. 检查队列名称是否正确
# 照片任务必须使用 photo 队列
# AI 任务必须使用 ai 队列
```

---

### 问题 3: AI 任务失败
```
[ERROR] Ollama API connection failed
```

**解决**:
```bash
# 1. 启动 Ollama 服务
ollama serve

# 2. 确认模型存在
ollama list | findstr qwen

# 3. 测试 API
curl http://127.0.0.1:11434/api/tags
```

---

## 📚 更多文档

| 文档 | 用途 |
|-----|------|
| [CELERY_QUICK_START.md](../1-后端代码/CELERY_QUICK_START.md) | 5 分钟快速入门 |
| [CELERY_SETUP.md](../1-后端代码/CELERY_SETUP.md) | 详细配置指南 |
| [CELERY_COMPLETION_SUMMARY.md](./CELERY_COMPLETION_SUMMARY.md) | 完成总结 |

---

## 🎉 成功标志

当一切正常运行时，您应该看到：

1. ✅ Redis: `redis-cli ping` 返回 `PONG`
2. ✅ Worker: 终端显示 `celery ready`
3. ✅ Backend: 访问 http://127.0.0.1:5000/docs 正常
4. ✅ Test: `python test_celery_tasks.py` 大部分测试通过
5. ✅ Monitor: http://127.0.0.1:5555 可访问（可选）

---

## 💡 下一步

完成 Celery 测试后，我们将进入 **Phase 1 Step 3: 数据库监控集成**

功能预览：
- 慢查询日志
- 索引健康检查
- 性能监控仪表板
- 自动优化建议

---

**需要帮助？** 参考文档或运行测试脚本进行诊断。

**准备好了？** 告诉我测试结果，我们继续下一步！
