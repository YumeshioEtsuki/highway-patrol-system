# 全栈功能调试分析

## 执行时间
2025-12-27

## 目标
系统性诊断照片选择、任务提交、监控数据等功能的端到端问题

---

## 第1层：数据库检查

### 1.1 Photo 表数据
```sql
-- 检查是否有照片记录
SELECT COUNT(*) as total_photos FROM Photo;
SELECT photo_id, file_name, record_id, upload_time FROM Photo LIMIT 5;

-- 检查关联的巡查记录
SELECT COUNT(*) as total_records FROM InspectionRecord;
SELECT record_id, user_id, upload_time FROM InspectionRecord LIMIT 5;

-- 检查数据关联是否完整
SELECT p.photo_id, p.file_name, ir.record_id, ir.user_id 
FROM Photo p
LEFT JOIN InspectionRecord ir ON p.record_id = ir.record_id
LIMIT 10;
```

**预期结果：**
- [ ] Photo 表有至少 1 条记录
- [ ] InspectionRecord 表有至少 1 条记录
- [ ] Photo 与 InspectionRecord 能正确关联（photo_id 不为 NULL）

---

### 1.2 Performance_metrics 表状态
```sql
-- 检查是否有监控数据
SELECT COUNT(*) as total_metrics FROM performance_metrics;
SELECT * FROM performance_metrics ORDER BY timestamp DESC LIMIT 1;

-- 表结构检查
DESCRIBE performance_metrics;
```

**预期结果：**
- [ ] 表存在且有列：id, timestamp, queries_per_sec, active_connections 等
- [ ] 有至少 1 条历史记录（或可以接受为空，由后端实时采集）

---

## 第2层：后端接口响应格式检查

### 2.1 照片列表接口测试
**接口：** `GET /api/photos/user`
**预期返回：**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "filename": "auto_1.jpg",
      "upload_time": "2025-12-27 10:00:00",
      "size_bytes": 102400,
      "record_id": 1
    }
  ],
  "total": 1
}
```

**调试步骤：**
1. 打开浏览器开发者工具 → Network
2. 刷新 tasks.html
3. 查找请求 `/api/photos/user`
4. 检查响应状态码（应为 200）
5. 检查响应体（应为 JSON，data 为数组）

**常见问题：**
- [ ] 状态码 500（后端错误 → 检查服务器日志）
- [ ] 状态码 401（认证失败 → 检查 token）
- [ ] data 为 null 或空数组（数据库无照片）
- [ ] 字段名不匹配（如返回 uuid 但前端期望 photo_id）

---

### 2.2 监控指标接口测试
**接口：** `GET /api/admin/monitor/metrics/current`
**预期返回：**
```json
{
  "status": "success",
  "data": {
    "queries_per_sec": 1.2,
    "slow_queries_per_min": 0,
    "active_connections": 5,
    "avg_query_time_ms": 50.0,
    "cache_hit_ratio": 0.95,
    "lock_wait_time_ms": 0.0,
    "timestamp": "2025-12-27T10:00:00"
  }
}
```

**调试步骤：**
1. 打开浏览器开发者工具 → Network
2. 访问 monitor（/monitor）
3. 查找请求 `/api/admin/monitor/metrics/current`
4. 检查响应体

**常见问题：**
- [ ] `data: null`（表为空，后端未返回默认值 → 需修复）
- [ ] 缺少某些字段（前端期望 queries_per_sec 但响应无该字段）
- [ ] 时间戳格式不对（ISO 8601 vs Unix timestamp）

---

## 第3层：前端数据绑定检查

### 3.1 照片下拉绑定验证
**文件：** `static/js/tasks.js`

1. 打开控制台（F12 → Console）
2. 执行命令查看加载的照片数据：
```javascript
console.log('userPhotos:', window.userPhotos);
console.log('PHOTO_ID_RE test:', PHOTO_ID_RE.test('1'));  // 应为 true
```

**预期结果：**
- [ ] `window.userPhotos` 是数组
- [ ] 数组中每个对象有 `id` 和 `filename`
- [ ] `PHOTO_ID_RE.test('1')` 返回 true（整数 ID 格式正确）

### 3.2 下拉菜单 HTML 检查
1. 右键点击"选择照片"下拉框
2. 选择"检查元素"
3. 查看 `<select>` 内是否有 `<option>` 元素
```html
<select>
  <option value="">-- 请选择 --</option>
  <option value="1">auto_1.jpg</option>  <!-- 应该有这行 -->
</select>
```

**预期结果：**
- [ ] 下拉框有多个 option 元素（不止占位符）
- [ ] 每个 option 的 value 是整数或 UUID

---

## 第4层：数据契约检查

| 端点 | 返回字段 | 前端期望 | 匹配? |
|-----|--------|--------|------|
| `/api/photos/user` | `id`, `filename` | `photo_id \| id`, `filename` | ? |
| `/api/admin/monitor/metrics/current` | `queries_per_sec`, `active_connections` | 同左 | ? |

---

## 诊断流程

### Step 1: 检查数据库（5分钟）
在 MySQL 客户端执行第1层的 SQL 语句，确认数据是否存在。

### Step 2: 检查网络响应（5分钟）
打开浏览器开发工具，验证 API 返回的 JSON 格式是否符合前端期望。

### Step 3: 检查前端日志（5分钟）
查看浏览器控制台的 `[photos]` 和 `[monitor]` 日志，确认数据是否加载。

### Step 4: 定位不匹配（可选，10分钟）
若前三步发现问题，回到对应层的代码进行修正。

---

## 问题记录模板

如果发现问题，请填写：

### 问题 X：[描述]
- **发生位置：** （数据库 / 后端接口 / 前端）
- **症状：** （实际现象）
- **预期：** （应该的样子）
- **根因：** （推测原因）
- **解决方案：** （修复方向）

---

## 检查清单

- [ ] 第1层：数据库有照片和监控数据
- [ ] 第2层：后端 API 返回正确的 JSON 格式
- [ ] 第3层：前端正确加载和绑定数据
- [ ] 第4层：数据契约一致（字段名、类型、结构）
- [ ] 最终：功能端到端可用（选照片 → 提交任务 → 显示监控）
