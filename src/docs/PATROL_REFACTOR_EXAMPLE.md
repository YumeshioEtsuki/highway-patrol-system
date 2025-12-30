# Patrol.html 重构示例

## 原理说明：采用"配置驱动"模式重构巡查页面

基于 `tasks.html` 的成功经验，对 `patrol.html` 进行现代化改造。核心思想：

### 🎯 重构目标
1. **配置与 UI 分离**：将巡查表单定义为 JSON 配置
2. **动态渲染**：通过 JavaScript 根据配置生成表单
3. **统一 API 调用**：复用 `tasks.js` 中的 `APIClient`
4. **实时状态更新**：支持照片上传进度、位置获取状态

---

## 📋 重构步骤

### Step 1：定义巡查表单配置（JSON）

在新建的 `static/js/patrol.js` 中：

```javascript
/**
 * 巡查表单配置
 * 支持：文本框、下拉框、文件上传、日期选择、位置获取
 */
const PATROL_FORM_CONFIG = {
    basic_info: {
        label: '基础信息',
        icon: '📋',
        fields: [
            {
                name: 'patrol_date',
                type: 'date',
                label: '巡查日期',
                required: true,
                default: () => new Date().toISOString().split('T')[0]  // 今天
            },
            {
                name: 'road_section',
                type: 'select',
                label: '路段',
                required: true,
                dataSource: 'road_sections',  // 动态加载路段列表
                placeholder: '-- 选择路段 --'
            },
            {
                name: 'patrol_type',
                type: 'select',
                label: '巡查类型',
                required: true,
                options: [
                    { value: 'routine', label: '日常巡查' },
                    { value: 'special', label: '专项检查' },
                    { value: 'emergency', label: '应急响应' }
                ]
            }
        ]
    },
    location: {
        label: '位置信息',
        icon: '📍',
        fields: [
            {
                name: 'latitude',
                type: 'number',
                label: '纬度',
                readonly: true,
                placeholder: '点击"获取当前位置"'
            },
            {
                name: 'longitude',
                type: 'number',
                label: '经度',
                readonly: true,
                placeholder: '点击"获取当前位置"'
            },
            {
                name: 'address',
                type: 'text',
                label: '详细地址',
                placeholder: '自动获取或手动输入'
            }
        ],
        actions: [
            {
                name: 'get_location',
                label: '📍 获取当前位置',
                handler: 'getCurrentLocation'
            }
        ]
    },
    issue_report: {
        label: '问题描述',
        icon: '⚠️',
        fields: [
            {
                name: 'issue_type',
                type: 'select',
                label: '问题类型',
                options: [
                    { value: 'road_damage', label: '路面损坏' },
                    { value: 'guardrail', label: '护栏缺失' },
                    { value: 'sign_missing', label: '标志缺失' },
                    { value: 'vegetation', label: '植被侵占' },
                    { value: 'other', label: '其他' }
                ]
            },
            {
                name: 'severity',
                type: 'select',
                label: '严重程度',
                required: true,
                options: [
                    { value: 'low', label: '轻微' },
                    { value: 'medium', label: '中等' },
                    { value: 'high', label: '严重' },
                    { value: 'critical', label: '紧急' }
                ]
            },
            {
                name: 'description',
                type: 'textarea',
                label: '详细描述',
                required: true,
                placeholder: '请详细描述问题情况...',
                rows: 4
            }
        ]
    },
    photos: {
        label: '照片上传',
        icon: '📸',
        fields: [
            {
                name: 'photos',
                type: 'file',
                label: '上传照片',
                accept: 'image/*',
                multiple: true,
                hint: '支持多张照片，最大 10MB/张'
            }
        ],
        actions: [
            {
                name: 'capture_photo',
                label: '📷 拍照',
                handler: 'capturePhoto'
            }
        ]
    }
};
```

---

### Step 2：动态表单渲染器

```javascript
/**
 * 巡查表单渲染器
 */
class PatrolFormRenderer {
    constructor(config) {
        this.config = config;
        this.formData = {};
    }

    /**
     * 渲染完整表单
     * @param {string} containerId - 容器 ID
     */
    render(containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        Object.keys(this.config).forEach(sectionKey => {
            const section = this.config[sectionKey];
            const sectionHTML = this.renderSection(sectionKey, section);
            container.innerHTML += sectionHTML;
        });

        // 绑定事件
        this.bindEvents();
        // 设置默认值
        this.setDefaults();
    }

    /**
     * 渲染一个表单区块
     */
    renderSection(sectionKey, section) {
        const fieldsHTML = section.fields.map(field => {
            return this.renderField(field);
        }).join('');

        const actionsHTML = section.actions ? section.actions.map(action => {
            return `<button type="button" class="btn btn-outline" data-action="${action.handler}">${action.label}</button>`;
        }).join('') : '';

        return `
            <div class="form-section" data-section="${sectionKey}">
                <h3 class="section-title">${section.icon} ${section.label}</h3>
                <div class="section-fields">
                    ${fieldsHTML}
                </div>
                ${actionsHTML ? `<div class="section-actions">${actionsHTML}</div>` : ''}
            </div>
        `;
    }

    /**
     * 渲染单个字段
     */
    renderField(field) {
        const required = field.required ? '<span class="required">*</span>' : '';
        const hint = field.hint ? `<small class="field-hint">${field.hint}</small>` : '';

        let inputHTML = '';

        switch (field.type) {
            case 'text':
            case 'number':
            case 'date':
                inputHTML = `<input 
                    type="${field.type}" 
                    name="${field.name}" 
                    id="${field.name}"
                    placeholder="${field.placeholder || ''}"
                    ${field.required ? 'required' : ''}
                    ${field.readonly ? 'readonly' : ''}
                >`;
                break;

            case 'select':
                const options = field.dataSource 
                    ? `<option value="">加载中...</option>`  // 动态加载
                    : field.options.map(opt => 
                        `<option value="${opt.value}">${opt.label}</option>`
                      ).join('');
                inputHTML = `<select name="${field.name}" id="${field.name}" ${field.required ? 'required' : ''}>
                    <option value="">${field.placeholder || '-- 请选择 --'}</option>
                    ${options}
                </select>`;
                break;

            case 'textarea':
                inputHTML = `<textarea 
                    name="${field.name}" 
                    id="${field.name}"
                    rows="${field.rows || 3}"
                    placeholder="${field.placeholder || ''}"
                    ${field.required ? 'required' : ''}
                ></textarea>`;
                break;

            case 'file':
                inputHTML = `<input 
                    type="file" 
                    name="${field.name}" 
                    id="${field.name}"
                    accept="${field.accept || ''}"
                    ${field.multiple ? 'multiple' : ''}
                >`;
                break;
        }

        return `
            <div class="form-group" data-field="${field.name}">
                <label for="${field.name}">${field.label}${required}</label>
                ${inputHTML}
                ${hint}
            </div>
        `;
    }

    /**
     * 设置默认值
     */
    setDefaults() {
        Object.values(this.config).forEach(section => {
            section.fields.forEach(field => {
                if (field.default) {
                    const value = typeof field.default === 'function' 
                        ? field.default() 
                        : field.default;
                    const element = document.getElementById(field.name);
                    if (element) {
                        element.value = value;
                    }
                }
            });
        });
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 绑定自定义操作按钮
        document.querySelectorAll('[data-action]').forEach(btn => {
            const action = btn.getAttribute('data-action');
            btn.addEventListener('click', () => {
                if (typeof window[action] === 'function') {
                    window[action]();
                }
            });
        });

        // 动态加载数据源
        this.loadDataSources();
    }

    /**
     * 动态加载数据源（如路段列表）
     */
    async loadDataSources() {
        Object.values(this.config).forEach(async section => {
            for (const field of section.fields) {
                if (field.dataSource === 'road_sections') {
                    try {
                        const response = await fetch('/api/road-sections');
                        const data = await response.json();
                        const select = document.getElementById(field.name);
                        select.innerHTML = '<option value="">-- 请选择 --</option>' +
                            data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');
                    } catch (err) {
                        console.error('加载路段列表失败:', err);
                    }
                }
            }
        });
    }

    /**
     * 收集表单数据
     */
    collectData() {
        const data = {};
        Object.values(this.config).forEach(section => {
            section.fields.forEach(field => {
                const element = document.getElementById(field.name);
                if (element) {
                    if (field.type === 'file') {
                        data[field.name] = element.files;
                    } else {
                        data[field.name] = element.value;
                    }
                }
            });
        });
        return data;
    }

    /**
     * 验证表单
     */
    validate() {
        const errors = [];
        Object.values(this.config).forEach(section => {
            section.fields.forEach(field => {
                if (field.required) {
                    const element = document.getElementById(field.name);
                    if (!element || !element.value) {
                        errors.push(`${field.label} 为必填项`);
                    }
                }
            });
        });
        return errors;
    }
}
```

---

### Step 3：业务逻辑处理

```javascript
// 初始化表单
const patrolForm = new PatrolFormRenderer(PATROL_FORM_CONFIG);
patrolForm.render('patrolFormContainer');

/**
 * 获取当前位置
 */
async function getCurrentLocation() {
    if (!navigator.geolocation) {
        showNotification('浏览器不支持定位功能', 'error');
        return;
    }

    showLoading('正在获取位置...');

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            document.getElementById('latitude').value = lat.toFixed(6);
            document.getElementById('longitude').value = lng.toFixed(6);

            // 逆地理编码获取地址
            try {
                const response = await fetch(`/api/geocode?lat=${lat}&lng=${lng}`);
                const data = await response.json();
                document.getElementById('address').value = data.address;
            } catch (err) {
                console.error('获取地址失败:', err);
            }

            hideLoading();
            showNotification('位置获取成功', 'success');
        },
        (error) => {
            hideLoading();
            showNotification('定位失败: ' + error.message, 'error');
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * 拍照（调用相机）
 */
function capturePhoto() {
    const input = document.getElementById('photos');
    input.setAttribute('capture', 'camera');
    input.click();
}

/**
 * 提交巡查记录
 */
async function submitPatrolRecord() {
    // 验证表单
    const errors = patrolForm.validate();
    if (errors.length > 0) {
        showNotification(errors.join('; '), 'error');
        return;
    }

    // 收集数据
    const data = patrolForm.collectData();

    // 构建 FormData（支持文件上传）
    const formData = new FormData();
    Object.keys(data).forEach(key => {
        if (key === 'photos' && data[key] instanceof FileList) {
            Array.from(data[key]).forEach(file => {
                formData.append('photos', file);
            });
        } else {
            formData.append(key, data[key]);
        }
    });

    showLoading('提交中...');

    try {
        const response = await fetch('/api/patrol/submit', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': getCSRFToken()
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('提交成功！', 'success');
            // 清空表单
            document.querySelector('form').reset();
        } else {
            showNotification('提交失败: ' + result.message, 'error');
        }
    } catch (err) {
        showNotification('网络错误', 'error');
        console.error(err);
    } finally {
        hideLoading();
    }
}
```

---

### Step 4：HTML 模板简化

**原 patrol.html**（1129 行，硬编码表单）:
```html
<div class="card">
    <h2>📋 基础信息</h2>
    <div class="form-group">
        <label>巡查日期</label>
        <input type="date" id="patrol_date">
    </div>
    <div class="form-group">
        <label>路段</label>
        <select id="road_section">
            <option>-- 请选择 --</option>
            <!-- 100+ 行硬编码选项 -->
        </select>
    </div>
    <!-- ... 重复 30+ 个字段 ... -->
</div>
```

**新 patrol.html**（简化为 ~300 行）:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="csrf-token" content="{{ csrf_token if csrf_token is defined else '' }}">
    <title>巡查系统 - 现场记录</title>
    <link rel="stylesheet" href="/static/css/patrol.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>🚗 公路巡查</h1>
            <span class="user-badge">{{ username }}</span>
        </div>

        <!-- 动态渲染的表单 -->
        <form id="patrolForm" onsubmit="submitPatrolRecord(); return false;">
            <div id="patrolFormContainer"></div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">✅ 提交巡查记录</button>
            </div>
        </form>
    </div>

    <!-- 通用工具 -->
    <script src="/static/js/common.js"></script>
    <!-- 巡查业务逻辑 -->
    <script src="/static/js/patrol.js"></script>
</body>
</html>
```

---

## 📊 重构对比

| 维度 | 原版 patrol.html | 重构后 |
|------|-----------------|--------|
| **代码行数** | 1129 行 | ~300 HTML + 400 JS |
| **表单定义** | HTML 硬编码 | JSON 配置 |
| **字段新增成本** | 需修改 HTML + JS（约 50 行） | 只需添加 JSON 配置（约 5 行） |
| **数据源加载** | 手动编写 AJAX | 配置 `dataSource` 自动加载 |
| **验证逻辑** | 分散在各处 | 统一在 `validate()` |
| **可测试性** | 难以单元测试 | 配置可 mock，易测试 |
| **国际化** | 文本散落各处 | 集中在配置中，易翻译 |

---

## 🎯 应用到其他页面

相同模式可应用于：

1. **reports.html**（报表页面）
   - 配置：导出日报、导出月报、生成统计图表
   - 复用 `TaskManager` 进行异步任务管理

2. **admin.html**（管理后台）
   - 配置：用户管理、权限设置、系统配置
   - 复用表单渲染器

3. **monitor.html**（监控页面）
   - 配置：实时图表、告警规则
   - 复用 `APIClient` 进行轮询

---

## ✅ 最佳实践总结

### 1. **配置优先**
将 UI 表单定义为 JSON 配置，代码只负责渲染和逻辑。

### 2. **动态渲染**
通过 `PatrolFormRenderer` 根据配置生成 HTML。

### 3. **统一工具**
复用 `common.js` 中的通知、日期格式化、CSRF 处理。

### 4. **渐进增强**
先完成核心功能，再添加拍照、定位等高级功能。

### 5. **保持兼容**
确保 Jinja2 变量（如 `{{ csrf_token }}`）正常渲染。

---

## 🚀 下一步行动

1. **立即应用**：用此模式重构 patrol.html
2. **推广到其他页面**：reports.html, monitor.html
3. **建立组件库**：将渲染器封装为可复用组件
4. **编写文档**：团队共享最佳实践

