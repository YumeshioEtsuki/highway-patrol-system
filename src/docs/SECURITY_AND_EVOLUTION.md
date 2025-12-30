# 安全加固 & 演进建议

## 🔐 一、安全加固清单

### 1. **CSRF 防护**

#### 问题
```
POST 请求无 CSRF token，容易被跨站请求伪造
示例风险：攻击者在其他网站嵌入恶意表单，用户访问时自动提交任务
```

#### 实现方案

**后端（FastAPI）：**
```python
# app.py
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter

# 生成 CSRF token
@router.get("/csrf-token")
def get_csrf_token():
    token = secrets.token_urlsafe(32)
    # 存储到 session 或 Redis
    return {"csrf_token": token}

# 验证中间件
@router.post("/api/tasks/{task_type}")
def submit_task(csrf_token: str = Header(...)):
    if not verify_csrf_token(csrf_token):
        raise HTTPException(403, "CSRF token invalid")
    # ... 处理任务
```

**前端（已在 tasks_refactored.js 中实现）：**
```javascript
// 自动从 meta 标签读取
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

// 每个请求都加上
headers: {
    'X-CSRF-Token': csrfToken,
    'Authorization': `Bearer ${token}`
}
```

**HTML 模板：**
```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

---

### 2. **参数校验加固**

#### 问题
```
photo_id 无格式检查  → 路径穿越 (../../../etc/passwd)
文件大小无限制      → OOM 或 DoS 攻击
数值范围不完整      → 服务异常
```

#### 实现方案

**前端校验（第一道防线）：**
```javascript
class FormValidator {
    static validate(fields, data) {
        const errors = {};

        fields.forEach(field => {
            const value = data[field.name];

            // 1. 必填检查
            if (field.required && !value) {
                errors[field.name] = `${field.label} 必填`;
            }

            // 2. photo_id 格式检查（只允许 16 位十六进制）
            if (field.name === 'photo_id' && value) {
                if (!/^[a-f0-9]{16}$/.test(value)) {
                    errors[field.name] = 'photo_id 格式不正确';
                }
            }

            // 3. 数字范围检查
            if (field.type === 'number' && value) {
                const num = parseFloat(value);
                if (field.min !== undefined && num < field.min) {
                    errors[field.name] = `最小值 ${field.min}`;
                }
                if (field.max !== undefined && num > field.max) {
                    errors[field.name] = `最大值 ${field.max}`;
                }
            }

            // 4. 文件大小检查
            if (field.type === 'file' && value) {
                const file = document.getElementById(field.name).files[0];
                const MAX_SIZE = 50 * 1024 * 1024;  // 50MB
                if (file.size > MAX_SIZE) {
                    errors[field.name] = '文件过大（最大 50MB）';
                }
            }
        });

        return errors;
    }
}
```

**后端校验（第二道防线）：**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class CompressPhotoRequest(BaseModel):
    photo_id: str = Field(..., regex=r'^[a-f0-9]{16}$', description="照片ID")
    quality: int = Field(85, ge=1, le=100, description="压缩质量")

    @validator('photo_id')
    def validate_photo_id(cls, v):
        # 额外的安全检查：确保 ID 不存在目录遍历
        if '..' in v or '/' in v:
            raise ValueError('photo_id 包含非法字符')
        return v

class ExportReportRequest(BaseModel):
    start_date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    end_date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    
    @validator('start_date', 'end_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('日期格式不正确')
        return v
```

---

### 3. **文件上传安全**

#### 问题
```
无大小限制       → 磁盘满、内存溢出
无扩展名检查     → 上传恶意脚本
无病毒扫描       → 恶意文件传播
```

#### 实现方案

```python
import os
import magic  # python-magic 库
from pathlib import Path

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_DAILY_UPLOAD = 1 * 1024 * 1024 * 1024  # 1GB/天/用户

async def upload_photo(
    file: UploadFile,
    current_user: CurrentUser = Depends(get_current_user)
):
    """上传照片 - 多层安全检查"""
    
    # 1. 检查文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "文件过大")
    
    # 2. 检查扩展名
    ext = Path(file.filename).suffix.lower().lstrip('.')
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "不支持的文件类型")
    
    # 3. 检查 MIME 类型（使用 magic 库）
    mime = magic.from_buffer(contents, mime=True)
    if not mime.startswith('image/'):
        raise HTTPException(400, "上传内容不是图片")
    
    # 4. 检查用户日上传量
    today_uploaded = await get_user_daily_upload_size(current_user.user_id)
    if today_uploaded + len(contents) > MAX_DAILY_UPLOAD:
        raise HTTPException(429, "今日上传量已达上限")
    
    # 5. 保存文件（使用 UUID 重命名，避免目录遍历）
    import uuid
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    # 6. 记录到数据库
    photo_id = hashlib.sha256(f"{current_user.user_id}_{filename}_{time.time()}".encode()).hexdigest()[:16]
    # ... 存储 photo_id -> file_path 映射
    
    return {"success": True, "photo_id": photo_id}
```

---

### 4. **认证与授权**

#### 问题
```
任何登录用户都能查看/修改其他用户的任务
无 API 速率限制
长时间有效的 token
```

#### 实现方案

```python
# 认证检查
@router.post("/api/tasks/photo/compress")
async def compress_photo(
    req: CompressPhotoRequest,
    current_user: CurrentUser = Depends(get_current_user)  # 必须登录
):
    # 检查用户是否拥有该照片
    photo = await get_photo_by_id(req.photo_id)
    if photo.user_id != current_user.user_id:
        raise HTTPException(403, "无权访问")
    
    # ... 提交任务

# 速率限制
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/tasks/photo/compress")
@limiter.limit("5/minute")  # 1 分钟最多 5 个请求
async def compress_photo(request: Request, ...):
    pass

# Token 过期时间
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 分钟过期

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

### 5. **SQL 注入防护**

#### 问题
```
虽然使用了参数化查询（很好！），但仍需定期检查
```

#### 检查清单

```python
# ✅ 好的做法 - 参数化查询
cursor.execute(
    "SELECT * FROM patrol_record WHERE record_id = %s",
    (record_id,)
)

# ❌ 危险 - 字符串拼接
cursor.execute(f"SELECT * FROM patrol_record WHERE record_id = {record_id}")

# ✅ 使用 ORM（更安全）
record = db.query(InspectionRecord).filter(
    InspectionRecord.record_id == record_id
).first()
```

---

### 6. **日志和监控**

#### 实现

```python
import logging
from pythonjsonlogger import jsonlogger

# 结构化日志
logger = logging.getLogger(__name__)
handler = logging.FileHandler('app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

@router.post("/api/tasks/photo/compress")
async def compress_photo(req: CompressPhotoRequest, current_user: CurrentUser):
    logger.info("compress_photo", extra={
        "user_id": current_user.user_id,
        "photo_id": req.photo_id,
        "quality": req.quality,
        "ip": request.client.host,
        "timestamp": datetime.utcnow().isoformat()
    })
    # ...

# 监控异常情况
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error("unexpected_error", extra={
        "error": str(exc),
        "path": request.url.path,
        "method": request.method,
        "ip": request.client.host
    })
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)
```

---

## 🚀 二、演进建议

### 1. **短期 (1-3 个月)**

#### 1.1 使用消息队列优化任务提交
```python
# 当前：同步调用 Celery.delay()
# 改进：通过消息队列解耦

# 使用 RabbitMQ 或 Kafka
from kombu import Connection, Exchange, Queue

exchange = Exchange('tasks', type='direct')
queue = Queue('photo_compress', exchange=exchange)

with Connection('amqp://guest:guest@localhost//') as conn:
    queue.maybe_bind(conn)
    queue.put({'photo_id': 'xxx', 'quality': 85})
```

#### 1.2 实现任务优先级
```javascript
// 前端支持选择优先级
const priorities = {
    'low': 0,
    'normal': 1,
    'high': 2,
    'urgent': 3
};

// 后端根据优先级分配 worker
@celery_app.task(priority=req.priority)
def compress_photo(photo_id, quality):
    pass
```

#### 1.3 添加任务日志查看界面
```html
<!-- 新增任务详情页 -->
<div id="taskDetail" style="display:none;">
    <h3>任务日志</h3>
    <div id="taskLogs" style="height: 400px; overflow-y: auto; background: #000; color: #0f0; font-family: monospace;"></div>
</div>
```

```javascript
// 实时获取任务日志
async function fetchTaskLogs(taskId) {
    const response = await apiClient.get(`/api/tasks/${taskId}/logs`);
    document.getElementById('taskLogs').innerText = response.logs.join('\n');
}

// 通过 SSE 实时推送日志
const eventSource = new EventSource(`/api/tasks/${taskId}/logs/stream`);
eventSource.addEventListener('log', (e) => {
    const log = JSON.parse(e.data);
    appendToLogs(log.message);
});
```

---

### 2. **中期 (3-6 个月) - 迁移到 Vue 3**

#### 2.1 组件设计

```vue
<!-- TaskForm.vue - 可复用的任务表单组件 -->
<template>
  <div class="taREDACTEDform">
    <h2>{{ config.label }}</h2>
    <form @submit.prevent="submit">
      <TaskInput 
        v-for="field in config.fields"
        :key="field.name"
        :field="field"
        v-model="formData[field.name]"
      />
      <button type="submit" :disabled="loading">提交</button>
    </form>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue';

const props = defineProps({
  config: Object,
  onSubmit: Function
});

const loading = ref(false);
const formData = ref({});

const submit = async () => {
  loading.value = true;
  try {
    await props.onSubmit(formData.value);
  } finally {
    loading.value = false;
  }
};
</script>

<!-- TaskCard.vue - 任务状态卡片 -->
<template>
  <div :class="['taREDACTEDcard', `status-${task.state}`]">
    <div class="taREDACTEDinfo">
      <h4>{{ task.name }}</h4>
      <p>{{ task.id }}</p>
    </div>
    <div class="taREDACTEDactions">
      <button v-if="canRetry" @click="retry">重试</button>
      <button v-if="canCancel" @click="cancel">取消</button>
    </div>
    <StatusBadge :state="task.state" />
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue';

const props = defineProps({
  task: Object
});

const canRetry = computed(() => ['FAILURE'].includes(props.task.state));
const canCancel = computed(() => ['PENDING', 'RUNNING'].includes(props.task.state));

const retry = () => console.log('重试任务:', props.task.id);
const cancel = () => console.log('取消任务:', props.task.id);
</script>
```

#### 2.2 Pinia 状态管理

```javascript
// stores/tasks.js
import { defineStore } from 'pinia';

export const useTaskStore = defineStore('tasks', {
    state: () => ({
        tasks: new Map(),
        selectedTask: null,
        loading: false
    }),

    getters: {
        allTasks: (state) => Array.from(state.tasks.values()),
        completedTasks: (state) => 
            Array.from(state.tasks.values())
                .filter(t => ['SUCCESS', 'FAILURE'].includes(t.state))
    },

    actions: {
        async submitTask(categoryKey, taskKey, payload) {
            this.loading = true;
            try {
                const response = await apiClient.post(
                    TASK_CONFIG[categoryKey].tasks[taskKey].endpoint,
                    payload
                );
                const task = {
                    id: response.task_id,
                    state: 'PENDING',
                    ...payload
                };
                this.tasks.set(task.id, task);
                return task;
            } finally {
                this.loading = false;
            }
        },

        updateTask(taskId, updates) {
            const task = this.tasks.get(taskId);
            if (task) {
                Object.assign(task, updates);
            }
        }
    }
});
```

---

### 3. **长期 (6-12 个月) - 实时推送 + 高可用**

#### 3.1 WebSocket 替代轮询

```python
# FastAPI WebSocket 端点
from fastapi import WebSocket

@router.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()
    user = verify_token(token)
    
    # 订阅用户任务更新
    task_channel = f"user_{user.user_id}_tasks"
    redis_pubsub = redis_client.pubsub()
    redis_pubsub.subscribe(task_channel)
    
    try:
        for message in redis_pubsub.listen():
            if message['type'] == 'message':
                task_update = json.loads(message['data'])
                await websocket.send_json(task_update)
    finally:
        redis_pubsub.unsubscribe(task_channel)
        await websocket.close()
```

```javascript
// 前端 WebSocket 连接
class TaskWebSocket {
    constructor(url, token) {
        this.ws = new WebSocket(`${url}?token=${token}`);
        this.ws.onmessage = (e) => {
            const update = JSON.parse(e.data);
            taskManager.updateTask(update.task_id, update);
            renderTasksList();
        };
    }
}

const taskWs = new TaskWebSocket('ws://localhost:8000/ws/tasks', getAccessToken());
```

#### 3.2 任务进度显示

```python
# 后端定期发送进度
@celery_app.task(bind=True)
def compress_photo(self, photo_id, quality):
    steps = ['reading', 'processing', 'saving', 'cleanup']
    for step in steps:
        # 更新任务进度
        self.update_state(
            state='PROGRESS',
            meta={'current': steps.index(step), 'total': len(steps)}
        )
        # ... 执行步骤
        time.sleep(1)
```

```javascript
// 前端接收进度更新
taskWs.ws.onmessage = (e) => {
    const {task_id, state, meta} = JSON.parse(e.data);
    if (state === 'PROGRESS') {
        const percent = (meta.current / meta.total) * 100;
        updateProgressBar(task_id, percent);
    }
};
```

#### 3.3 任务批量操作

```javascript
// 支持批量提交
async function submitBatch(tasks) {
    const results = await Promise.all(
        tasks.map(t => taskManager.submit(t.category, t.type, t.payload))
    );
    showNotification(`批量提交 ${results.length} 个任务`);
}

// 支持选择和批量处理
function selectTasks(taskIds) {
    selectedTasks = new Set(taskIds);
}

async function retrySelected() {
    for (const taskId of selectedTasks) {
        await taskManager.retryTask(taskId);
    }
}
```

---

### 4. **架构升级**

#### 当前架构
```
Frontend (Vanilla JS) 
    ↓
FastAPI (REST)
    ↓
Celery + Redis
    ↓
MySQL + 文件系统
```

#### 目标架构 (12 个月后)
```
Frontend (Vue 3) 
    ↓ (REST + WebSocket)
API Gateway (Kong/Traefik)
    ├─ FastAPI (REST)
    ├─ WebSocket Server
    └─ gRPC Service
    ↓
Message Queue (RabbitMQ/Kafka)
    ↓
Celery Workers (auto-scaling)
    ↓
Database (MySQL/PostgreSQL)
Cache (Redis Cluster)
File Storage (S3/MinIO)
Task Logger (ELK Stack)
```

---

## 📋 三、完整的安全检查清单

- [ ] **认证**
  - [ ] JWT token 有过期时间（≤ 30 分钟）
  - [ ] Refresh token 机制
  - [ ] 登出时清除 token

- [ ] **授权**
  - [ ] 用户只能查看/修改自己的任务
  - [ ] 管理员可查看所有任务
  - [ ] API 速率限制（5/分钟）

- [ ] **输入校验**
  - [ ] 前端：必填、格式、长度检查
  - [ ] 后端：Pydantic 重复校验
  - [ ] photo_id 白名单（16 位十六进制）
  - [ ] 日期格式校验（YYYY-MM-DD）

- [ ] **文件安全**
  - [ ] 文件大小限制（≤ 50MB）
  - [ ] 扩展名白名单
  - [ ] MIME 类型检查
  - [ ] 病毒扫描（ClamAV）
  - [ ] 用户日上传量限制（1GB）

- [ ] **数据安全**
  - [ ] SQL 参数化查询
  - [ ] 敏感数据加密存储
  - [ ] 访问日志记录
  - [ ] 定期备份

- [ ] **API 安全**
  - [ ] HTTPS only
  - [ ] CORS 配置正确
  - [ ] CSRF token
  - [ ] 请求签名（X-CSRF-Token）

- [ ] **监控**
  - [ ] 异常告警
  - [ ] 性能指标
  - [ ] 用户行为日志
  - [ ] 定期安全审计

