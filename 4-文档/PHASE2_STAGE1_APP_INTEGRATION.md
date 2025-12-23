# Phase 2 Stage 1: app.py 集成指南

## 完整的 app.py 更新代码

将以下代码添加到 `1-后端代码/app.py` 中：

### 1. 在导入部分添加

```python
# 在文件顶部，与其他导入一起添加

# Phase 2 Stage 1: 工单与权限系统
from routes import orders
from models import order_models
from utils.permissions import (
    get_current_user_info,
    PermissionChecker,
    log_audit_action
)

# 数据库初始化
from models.order_tasks import list_orders
```

### 2. 在应用初始化部分（生命周期事件）添加

```python
# 在 @app.on_event("startup") 中添加

@app.on_event("startup")
async def startup():
    """应用启动时初始化"""
    print("[INFO] 🚀 应用启动...")
    
    # 现有的初始化代码...
    # ...
    
    # Phase 2: 初始化工单系统
    if not os.getenv("SKIP_DB_INIT"):
        print("[INFO] 初始化工单与权限系统...")
        try:
            db_connection = get_db_connection()
            cursor = db_connection.cursor()
            
            # 检查新表是否存在
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'role'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("[INFO] 检测到工单系统未初始化，执行迁移...")
                # 可选：自动执行迁移脚本
                # execute_sql_file('3-数据库/phase2_stage1_order_and_role.sql')
            else:
                print("[✅] 工单系统已初始化")
            
            cursor.close()
            close_db_connection(db_connection)
        except Exception as e:
            print(f"[⚠️] 工单系统初始化警告: {str(e)}")
    
    print("[✅] 应用启动完成")
```

### 3. 在路由注册部分添加

```python
# 在其他 include_router 调用之后添加

# Phase 2 Stage 1: 工单管理
app.include_router(orders.router)

print("[✅] 工单管理路由已注册")
```

### 4. 添加权限检查中间件（可选但推荐）

```python
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time

class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件 - 记录所有修改操作"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录修改操作
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # 获取请求体
            body = await request.body()
            request.state.body = body
        
        # 记录开始时间
        request.state.start_time = time.time()
        
        response = await call_next(request)
        
        # 计算执行时间
        process_time = time.time() - request.state.start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

# 在应用中间件注册部分添加
app.add_middleware(AuditMiddleware)
```

### 5. 添加权限测试端点（用于调试）

```python
@app.get("/api/auth/me", tags=["auth"])
async def get_current_user(current_user: dict = Depends(get_current_user_info)):
    """
    获取当前登录用户信息
    
    用于前端检查用户权限状态
    """
    db_connection = get_db_connection()
    try:
        cursor = db_connection.cursor()
        
        # 获取用户的所有权限
        cursor.execute("""
            SELECT DISTINCT CONCAT(p.resource, ':', p.action)
            FROM user u
            JOIN role r ON u.role_id = r.id
            JOIN role_permission rp ON r.id = rp.role_id
            JOIN permission p ON rp.permission_id = p.id
            WHERE u.user_id = %s
        """, (current_user['user_id'],))
        
        permissions = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return {
            "user_id": current_user['user_id'],
            "username": current_user['username'],
            "real_name": current_user['real_name'],
            "role": current_user['role_name'],
            "is_admin": current_user['is_admin'],
            "permissions": permissions
        }
    finally:
        close_db_connection(db_connection)
```

## 完整代码示例

### 最小化集成版本

```python
# 1-后端代码/app.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os

# 导入路由
from routes import patrol, user, admin, photo, patrol_sse, orders
from utils.utils import get_db_connection, close_db_connection, initialize_database
from utils.config import settings
from utils.permissions import get_current_user_info

# 初始化应用
app = FastAPI(
    title="公路巡查系统",
    description="完整的公路巡查数据采集与管理系统",
    version="2.0.0"
)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境使用通配符，生产环境应改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 应用生命周期
@app.on_event("startup")
async def startup():
    """应用启动时初始化"""
    print("[INFO] 🚀 应用启动中...")
    
    # 初始化数据库
    if not os.getenv("SKIP_DB_INIT"):
        print("[INFO] 初始化数据库...")
        initialize_database()
    
    print("[✅] 应用启动完成")

@app.on_event("shutdown")
async def shutdown():
    """应用关闭时清理"""
    print("[INFO] 应用关闭")

# 注册路由
app.include_router(patrol.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(photo.router)
app.include_router(patrol_sse.router)

# Phase 2: 工单与权限系统
app.include_router(orders.router)

# 首页与文档
@app.get("/")
async def root():
    """根路径 - 返回前端界面"""
    return FileResponse("templates/test.html")

@app.get("/monitor")
async def monitor():
    """监控仪表板"""
    return FileResponse("templates/monitor.html")

# 健康检查
@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "ok", "version": "2.0.0"}

# 当前用户信息
@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user_info)):
    """获取当前用户信息"""
    return {
        "status": "success",
        "user": current_user
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

## 数据库初始化

### 自动迁移（可选）

如果想在应用启动时自动执行迁移，修改 `startup` 事件：

```python
@app.on_event("startup")
async def startup():
    print("[INFO] 🚀 应用启动中...")
    
    if not os.getenv("SKIP_DB_INIT"):
        print("[INFO] 初始化数据库...")
        initialize_database()
        
        # Phase 2: 执行新迁移脚本
        print("[INFO] 执行 Phase 2 迁移...")
        db_connection = get_db_connection()
        try:
            # 这里假设 execute_sql_file 函数已经存在
            from utils.utils import execute_sql_file
            execute_sql_file('3-数据库/phase2_stage1_order_and_role.sql')
            print("[✅] Phase 2 迁移完成")
        except Exception as e:
            print(f"[⚠️] Phase 2 迁移失败: {str(e)}")
        finally:
            close_db_connection(db_connection)
    
    print("[✅] 应用启动完成")
```

## 测试脚本

创建 `test_phase2_stage1.py` 来验证集成：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phase 2 Stage 1 集成测试
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

# 测试用 Token (从登录获取)
TEST_TOKEN = "your_jwt_token_here"

def test_order_list():
    """测试工单列表"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/orders",
        headers=headers,
        params={"limit": 10, "offset": 0}
    )
    
    print(f"✅ 工单列表: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_get_current_user():
    """测试获取当前用户"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    
    print(f"✅ 当前用户: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_order_stats():
    """测试工单统计"""
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/orders/stats/overview",
        headers=headers
    )
    
    print(f"✅ 工单统计: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("🧪 Phase 2 Stage 1 测试开始...\n")
    
    try:
        test_get_current_user()
        print("\n" + "="*50 + "\n")
        
        test_order_list()
        print("\n" + "="*50 + "\n")
        
        test_order_stats()
        print("\n" + "="*50 + "\n")
        
        print("✅ 所有测试通过!")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
```

## 部署检查清单

- [ ] 已下载并阅读 PHASE2_STAGE1_DEPLOYMENT.md
- [ ] 已执行数据库迁移脚本
- [ ] 已更新 app.py 并导入新路由
- [ ] 已验证 API 端点可访问
- [ ] 已创建测试用户和角色
- [ ] 已配置 SLA 参数
- [ ] 已验证权限检查生效
- [ ] 已测试审计日志记录

## 常见集成问题

### 1. 找不到 order_models 模块

**解决**: 确保 `models/order_models.py` 存在，并在 app.py 中正确导入

```python
from models import order_models  # 必须导入
```

### 2. 权限检查总是失败

**解决**: 确保：
1. JWT Token 有效
2. 用户已分配角色
3. 角色已被分配权限

```sql
-- 检查用户角色
SELECT u.username, r.name FROM user u
LEFT JOIN role r ON u.role_id = r.id;

-- 检查角色权限
SELECT r.name, p.resource, p.action
FROM role r
JOIN role_permission rp ON r.id = rp.role_id
JOIN permission p ON rp.permission_id = p.id
ORDER BY r.name;
```

### 3. 工单 API 返回 404

**解决**: 确保：
1. 数据库迁移已成功
2. inspectionrecord 表中有记录
3. API 路径正确 (`/api/orders` 不是 `/orders`)

### 4. 缓存问题

**解决**: 清除 Redis 缓存：

```python
from utils.redis_client import redis_client
redis_client.flushdb()
```

---

**当部署完成后，系统将支持完整的工单流转流程和多角色权限管理。**

