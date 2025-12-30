# 📱 真机测试完全指南

## 问题诊断

### 症状：小程序提示 "网络连接失败"

这通常有以下几个原因，请按顺序检查：

---

## 第一步：确认后端服务运行

```bash
# 1. 进入后端目录
cd "1-后端代码"

# 2. 启动服务（注意：是 uvicorn，不是 start_server.py）
python -m uvicorn app:app --host 0.0.0.0 --port 5000

# 3. 看到这句话说明启动成功：
# INFO:     Uvicorn running on http://0.0.0.0:5000
```

✅ 确认后端输出类似：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

---

## 第二步：获取电脑的局域网 IP

```powershell
# 在 PowerShell 中运行
ipconfig
```

找到 **WLAN 或无线适配器** 下的 **IPv4 地址**，例如：
- `192.168.1.100`
- `10.0.0.50`
- `10.61.42.124` （你的情况）

记下这个 IP！

---

## 第三步：更新小程序配置

编辑 **2-小程序代码/app.js**，找到 baseUrl 配置：

```javascript
// 原来的配置
baseUrl: 'http://10.61.42.124:5000',

// 改为你的 IP（例如）
baseUrl: 'http://192.168.1.100:5000',
```

> ⚠️ 注意：必须和你的电脑 WiFi IP 一致！

---

## 第四步：测试网络连接

### 4a. 在电脑本机测试

```bash
# 在电脑上打开浏览器，访问：
http://127.0.0.1:5000/docs

# 应该看到 Swagger API 文档
```

如果无法访问 → 后端未正常启动，返回第一步

### 4b. 在手机浏览器测试

1. **确保手机和电脑在同一个 WiFi**
   - 不能是手机热点
   - 必须是同一个路由器的 WiFi

2. **在手机浏览器访问**
   ```
   http://<你的电脑IP>:5000
   ```
   例如：`http://192.168.1.100:5000`

3. **看到响应说明网络OK**
   - 可能看到错误页面（如404）
   - 重点是能"连接到"服务器，而不是超时

---

## 第五步：排查防火墙

如果手机浏览器仍超时无法连接：

### Windows Defender 防火墙设置

1. **打开防火墙设置**
   ```
   设置 → 隐私和安全 → Windows 安全中心 → 防火墙和网络保护
   ```

2. **允许 Python 通过防火墙**
   - 点击"允许应用通过防火墙"
   - 找到 `Python.exe`
   - 勾选 ✓ 专用 和 ✓ 公用

### 或用管理员 PowerShell 添加规则

```powershell
# 以管理员身份运行 PowerShell
netsh advfirewall firewall add rule name="Allow Python 5000" `
    dir=in action=allow protocol=tcp localport=5000
```

---

## 第六步：小程序配置

### 在微信开发者工具中

1. **清除缓存**
   - 菜单：工具 → 清除缓存 → 清除所有
   - 或快捷键：`Ctrl+Shift+Q`

2. **重新编译**
   - 菜单：项目 → 编译

3. **测试真机登录**
   - 用手机扫描二维码
   - 或直接在真机上运行小程序

---

## 常见问题

### Q1：看到"网络连接失败"，但 ip:5000 在浏览器能打开
**原因**：小程序可能没有正确配置 baseUrl

**解决**：
- 确认更新了 app.js 中的 baseUrl
- 清除小程序缓存（Ctrl+Shift+Q）
- 重新上传代码

### Q2：手机浏览器访问 ip:5000 超时（无反应）
**原因**：防火墙阻止、网络不互通、或 IP 错误

**检查清单**：
```
☐ ipconfig 查到的 IP 是否正确
☐ Windows 防火墙是否已允许 Python
☐ 手机和电脑是否真的在同一个 WiFi
☐ WiFi 是否启用了"设备隔离"（某些企业/校园网会有）
☐ 后端是否用 --host 0.0.0.0 启动（不能是 127.0.0.1）
```

### Q3：电脑本机可以，手机无法连接
**原因**：大多数是防火墙或 WiFi 限制

**尝试**：
1. 暂时关闭 Windows Defender 防火墙（仅测试）
2. 用手机连接电脑的个人热点而非 WiFi
3. 检查路由器设置是否启用了设备隔离

### Q4：登录后仍显示数据为 0
**原因**：数据库没有巡查记录

**解决**：
```bash
cd 1-后端代码
python -c "from models.tasks import generate_fake_records; generate_fake_records(count=100)"
```

---

## 快速恢复指南

如果弄乱了，快速恢复开发环境：

```bash
# 1. 重建数据库
cd 1-后端代码

# 删除旧数据库（MySQL 中）
mysql -u root -p -e "DROP DATABASE IF EXISTS road_patrol_db;"

# 重新初始化
python -c "from utils.utils import initialize_database; initialize_database()"

# 2. 生成测试数据
python -c "from models.tasks import generate_fake_records; generate_fake_records(100)"

# 3. 启动后端
python -m uvicorn app:app --host 0.0.0.0 --port 5000
```

---

## 部署到生产环境

> ⚠️ 不要在生产环境使用开发配置

生产部署时需要：
- [ ] 关闭 DEBUG 模式
- [ ] 更新 SECRET_KEY（使用强随机密钥）
- [ ] 限制 ALLOW_ORIGINS（仅允许前端域名）
- [ ] 使用 HTTPS 和 SSL 证书
- [ ] 配置反向代理（Nginx/Apache）
- [ ] 删除测试数据
- [ ] 配置数据库备份

详见 [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)

---

## 获取帮助

**查看日志**：
```bash
# 后端会输出详细日志
# 看是否有错误提示或警告

# 或查看日志文件（如果配置了）
tail -f logs/app.log
```

**小程序调试**：
- 微信开发者工具 → 调试工具 → Console
- 看是否有 JavaScript 错误
- 查看 Network 标签看 API 请求是否成功

---

**祝测试顺利！** 🎉

如问题未解决，请提供：
1. 后端输出日志
2. 小程序 Console 错误信息
3. 手机浏览器能否访问 `http://IP:5000`
4. 电脑 `ipconfig` 的输出
