# 测试脚本说明文档

## 📁 测试脚本目录

本目录包含系统开发和测试过程中创建的各种诊断和测试脚本。

---

## 🔧 主要脚本

### 1. comprehensive_check.py ⭐ **推荐使用**
**用途：** 全面系统健康检查  
**功能：**
- 检查数据库连接和表结构
- 检测API服务器状态
- 验证认证功能
- 测试管理员API
- 检查文件结构完整性
- 生成详细诊断报告

**使用方法：**
```bash
cd d:\MySQL Project\highway-patrol-system
python 7-测试脚本/comprehensive_check.py
```

**适用场景：**
- 系统部署后的健康检查
- 问题排查的首选工具
- 定期维护检查

---

### 2. run_test.py
**用途：** 快速启动服务器并执行基础功能测试  
**功能：**
- 自动启动后端服务器（带健康检查轮询）
- 测试登录、验证、SSE等核心功能
- 支持 SKIP_DB_INIT 环境变量

**使用方法：**
```bash
cd d:\MySQL Project\highway-patrol-system
python 7-测试脚本/run_test.py
```

**环境变量：**
- `USE_RELOAD=1`: 启用开发模式热重载

---

### 3. speed_test.py
**用途：** MySQL数据库性能诊断  
**功能：**
- 测试数据库连接速度
- 测试简单查询性能
- 测试复杂JOIN查询
- 检测记录数量

**使用方法：**
```bash
cd d:\MySQL Project\highway-patrol-system
python 7-测试脚本/speed_test.py
```

**适用场景：**
- 系统响应慢时的性能分析
- 数据库瓶颈诊断

---

### 4. test_export.py
**用途：** 测试Excel导出功能  
**功能：**
- 测试管理员登录
- 测试Excel文件生成
- 验证文件大小和内容

**使用方法：**
```bash
cd d:\MySQL Project\highway-patrol-system
python 7-测试脚本/test_export.py
```

---

### 5. test_admin_auth.py
**用途：** 测试管理员认证和权限  
**功能：**
- 测试管理员登录
- 测试Token验证
- 测试管理员API权限

**使用方法：**
```bash
cd d:\MySQL Project\highway-patrol-system
python 7-测试脚本/test_admin_auth.py
```

---

## 📋 历史/调试脚本

以下脚本是问题排查过程中创建的，已被更完善的工具替代：

### debug_check.py
早期的数据库记录检查脚本，功能已整合到 comprehensive_check.py

### diagnostic.py / diagnostic_report.py
系统问题诊断报告生成器，已被 comprehensive_check.py 替代

### frontend_fixes.py
前端修复建议脚本，相关修复已应用到代码

### generate_summary.py
生成开发总结的工具脚本

---

## 🚀 快速使用指南

### 新部署后的检查流程

1. **运行全面检查**
   ```bash
   python 7-测试脚本/comprehensive_check.py
   ```

2. **如果数据库为空，初始化测试数据**
   - 访问 http://127.0.0.1:5000/admin.html
   - 登录（admin/REDACTED）
   - 选择"完整重置（含测试数据）"

3. **再次运行检查确认**
   ```bash
   python 7-测试脚本/comprehensive_check.py
   ```

### 问题排查流程

1. **系统慢/无响应**
   ```bash
   python 7-测试脚本/speed_test.py
   ```

2. **登录失败**
   ```bash
   python 7-测试脚本/test_admin_auth.py
   ```

3. **导出失败**
   ```bash
   python 7-测试脚本/test_export.py
   ```

4. **不确定问题**
   ```bash
   python 7-测试脚本/comprehensive_check.py
   ```

---

## ⚠️ 注意事项

1. 所有脚本需要后端服务器运行在 `http://127.0.0.1:5000`
2. 部分脚本需要管理员账号（admin/REDACTED）
3. 确保MySQL数据库服务正在运行
4. Python虚拟环境需要激活（如使用 `.venv`）

---

## 📝 维护建议

- 定期运行 `comprehensive_check.py` 进行健康检查
- 性能问题时优先使用 `speed_test.py`
- 新功能开发后使用 `run_test.py` 验证基础功能
- 生产部署前必须通过所有测试

---

**最后更新：** 2025年12月21日
**维护者：** 系统开发团队
