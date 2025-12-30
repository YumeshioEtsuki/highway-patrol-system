# 后端Web UI按钮显示逻辑流程图

## 初始化流程

```
页面加载
  ↓
DOMContentLoaded 事件触发
  ↓
检查 localStorage 中是否有 access_token
  ├─ 无token → 显示登录表单，隐藏patrol-section
  │
  └─ 有token → 调用 authFetch('/api/me')
      ↓
      获取用户信息 (CurrentUser: {user_id, username, role})
      ↓
      隐藏登录表单，显示patrol-section
      ↓
      检查 role 字段
      ├─ role == 'admin' → 显示admin按钮 (display: inline-flex)
      │                 → 连接SSE实时照片流
      │
      └─ role != 'admin' → 隐藏admin按钮 (display: none)
      
      加载基础数据（路段、问题类型、巡查记录）
```

## 登录流程

```
用户输入用户名和密码
  ↓
点击"登录"按钮 → handleLogin()
  ↓
POST /api/login {username, password}
  ↓
后端验证凭证
  ├─ 验证失败 → 返回 {error: "用户名或密码错误"}
  │            → 显示错误提示，留在登录表单
  │
  └─ 验证成功 → 返回 {
                   access_token: "JWT_TOKEN",
                   token_type: "bearer", 
                   user: {
                       user_id: 1,
                       username: "admin",
                       real_name: "系统管理员",
                       role: "admin",  ← 关键字段
                       ...
                   }
               }
                ↓
             前端接收响应，保存token到localStorage
                ↓
             显示欢迎信息 "欢迎，系统管理员！"
                ↓
             隐藏登录表单，显示patrol-section
                ↓
             检查 user.role 字段  ← ✅ 修复：登录时检查role
             ├─ role == 'admin' → 显示admin按钮 (display: inline-flex) ✅ 修复新增
             │
             └─ role != 'admin' → 隐藏admin按钮 (display: none) ✅ 修复新增
                ↓
             加载基础数据（路段、问题类型、巡查记录）
```

## 页面显示元素状态

### 未登录状态
```
┌─────────────────────────────────────┐
│        登录表单                      │
│  ┌──────────────────────────────┐  │
│  │ 用户名: [________]           │  │
│  │ 密码: [________]             │  │
│  │ [登录按钮]                   │  │
│  └──────────────────────────────┘  │
│                                     │
│ 👤 欢迎，___！       ← 隐藏         │
│ [退出登录] [管理员页面] ← 隐藏       │
│                                     │
│ ➕ 新建巡查记录     ← 隐藏          │
│ ...                                 │
└─────────────────────────────────────┘
```

### 已登录为管理员
```
┌─────────────────────────────────────┐
│        登录表单          ← 隐藏      │
│  ┌──────────────────────────────┐  │
│  │ ...                          │  │ ← 隐藏
│  └──────────────────────────────┘  │
│                                     │
│ 👤 欢迎，系统管理员！ ← 显示        │
│ [退出登录] [📊 管理员页面] ← 显示    │
│                                     │
│ ➕ 新建巡查记录       ← 显示        │
│ ┌──────────────────────────────┐  │
│ │ 路段: [选择下拉]             │  │
│ │ 问题类型: [选择下拉]         │  │
│ │ 描述: [文本框]               │  │
│ │ 严重程度: [滑块]             │  │
│ │ 定位: [获取GPS按钮]          │  │
│ │ 照片: [文件上传]             │  │
│ │ [提交按钮]                   │  │
│ └──────────────────────────────┘  │
│                                     │
│ 📋 巡查记录                         │
│ (显示列表)                          │
└─────────────────────────────────────┘
```

### 已登录为普通巡查员
```
┌─────────────────────────────────────┐
│        登录表单          ← 隐藏      │
│                                     │
│ 👤 欢迎，巡查员！   ← 显示          │
│ [退出登录]              ← 显示      │
│ [📊 管理员页面]         ← 隐藏 ✅   │
│                                     │
│ ➕ 新建巡查记录       ← 显示        │
│ ...                                 │
│                                     │
│ 📋 巡查记录                         │
│ ...                                 │
└─────────────────────────────────────┘
```

## 关键代码位置

### 登录时的role检查 ✅
**文件**：patrol.html
**函数**：handleLogin()
**行号**：398-402

```javascript
// 检查用户角色，如果是管理员则显示管理员按钮
if (user.role === 'admin') {
    document.getElementById('admin-btn').style.display = 'inline-flex';
} else {
    document.getElementById('admin-btn').style.display = 'none';
}
```

### 页面加载时的role检查 ✅
**文件**：patrol.html
**函数**：DOMContentLoaded事件处理器
**行号**：970-974

```javascript
if (data.role === 'admin') {
    document.getElementById('admin-btn').style.display = 'inline-flex';
} else {
    // 如果不是管理员，确保隐藏管理员按钮
    document.getElementById('admin-btn').style.display = 'none';
}
```

### SSE实时照片流（仅admin）✅
**文件**：patrol.html
**函数**：DOMContentLoaded事件处理器
**行号**：982

```javascript
// 连接 SSE 实时照片流（如果是管理员）
if (data.role === 'admin') {
    connectSSEPhotos(token);
}
```

### 后端权限保护 ✅
**文件**：admin.html
**函数**：ensureAdmin()
**行号**：397

```javascript
if (user.role !== 'admin') {
    showAuthBlock('当前账号非管理员，请使用管理员账号登录');
    return false;
}
```

## 数据流验证

### API响应中的role字段

#### /api/login 响应
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": {
        "user_id": 1,
        "username": "admin",
        "real_name": "系统管理员",
        "phone": "11451419198",
        "email": "admin@example.com",
        "created_at": "2025-12-22T04:22:04",
        "last_login": "2025-12-22T16:30:34",
        "role": "admin"  ← ✅ 包含role字段
    }
}
```

#### /api/me 响应
```json
{
    "user_id": 1,
    "username": "admin",
    "role": "admin"  ← ✅ 包含role字段
}
```

## 完整流程执行示例

### 场景1：admin用户登录
```
1. 页面加载 → localStorage无token → 显示登录表单
2. 输入 admin / REDACTED
3. 调用 POST /api/login
4. 后端返回包含 role='admin' 的user对象
5. handleLogin()执行：
   - 保存token到localStorage
   - 显示"欢迎，系统管理员！"
   - 隐藏登录表单，显示patrol-section
   - ✅ 检查 user.role === 'admin'
   - ✅ 显示admin按钮
   - 加载数据
6. 用户看到：欢迎信息 + 两个按钮（退出登录、管理员页面） + 巡查表单
```

### 场景2：inspector用户登录
```
1. 页面加载 → 显示登录表单
2. 输入 inspector_user / Password123
3. 调用 POST /api/login
4. 后端返回包含 role='inspector' 的user对象
5. handleLogin()执行：
   - 保存token到localStorage
   - 显示"欢迎，[用户名]！"
   - 隐藏登录表单，显示patrol-section
   - ✅ 检查 user.role === 'admin' 为 false
   - ✅ 隐藏admin按钮
   - 加载数据
6. 用户看到：欢迎信息 + 一个按钮（退出登录） + 巡查表单
```

### 场景3：刷新页面（已登录）
```
1. 页面加载 → localStorage有有效token
2. DOMContentLoaded触发
3. 调用 authFetch('/api/me')
4. 后端返回用户信息包含role字段
5. 检查 data.role 值
6. 根据role显示/隐藏admin按钮
7. 连接SSE（如果是admin）
8. 加载数据
```

### 场景4：点击退出登录
```
1. 用户点击"退出登录"按钮
2. 调用 logout()函数
3. POST /api/logout 通知后端
4. localStorage.removeItem('access_token')
5. localStorage.removeItem('token_expires')
6. location.reload() 刷新页面
7. 页面重新加载，检查token，发现localStorage为空
8. 显示登录表单
```

## 修复总结

| 检查项 | 修复前 | 修复后 | 状态 |
|------|------|------|------|
| handleLogin中role检查 | ❌ 无 | ✅ 有 | 已修复 |
| DOMContentLoaded中else分支 | ❌ 无 | ✅ 有 | 已修复 |
| 后端/api/login返回role | ✅ 有 | ✅ 有 | 正常 |
| 后端/api/me返回role | ✅ 有 | ✅ 有 | 正常 |
| admin.html权限检查 | ✅ 有 | ✅ 有 | 正常 |
| logout函数实现 | ✅ 有 | ✅ 有 | 正常 |

## 文档索引

- [完整修复指南](修复验证指南-后端按钮显示.md) - 详细的验证步骤
- [问题排查总结](问题排查总结-backend_ui_buttons.md) - 详细的问题分析
- [项目结构](功能完成情况速查表.md) - 项目整体架构

---

*此文档为技术流程图，描述了修复前后的完整数据流和代码执行路径*
