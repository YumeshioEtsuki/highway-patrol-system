/**
 * 任务中心核心脚本 (重构版)
 * 
 * 架构设计：
 * 1. TaskManager - 统一的任务配置和提交管理
 * 2. FormRenderer - 动态表单渲染
 * 3. TaskPoller - 任务状态轮询
 * 4. APIClient - 统一的 HTTP 客户端（含 CSRF + 错误处理）
 * 
 * 使用示例：
 *   - 提交任务：taskManager.submit('compress_photo', {photo_id, quality})
 *   - 刷新列表：refreshTasks()
 *   - 监听状态：自动轮询 task_id 每 2 秒
 */

// ==================== 常量与配置定义 ====================

// 业务校验范围（需与后端保持一致）
// photo_id 可以是整数（数据库自增主键）或 UUID
const PHOTO_ID_RE = /^(\d+|[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$/i;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const YEAR_MIN = 2020;
const YEAR_MAX = new Date().getFullYear();

/**
 * 任务类型配置
 * 扩展时只需添加新配置，无需修改代码
 */
const TASK_CONFIG = {
    photo_processing: {
        icon: '📸',
        name: '照片处理',
        tasks: {
            compress_photo: {
                label: '压缩照片',
                endpoint: '/api/tasks/photo/compress',
                fields: [
                    {
                        name: 'photo_id',
                        type: 'select',
                        label: '选择照片',
                        required: true,
                        placeholder: '-- 从已上传照片选择 --',
                        dataSource: 'photos'  // 动态加载
                    },
                    {
                        name: 'quality',
                        type: 'number',
                        label: '压缩质量',
                        min: 1,
                        max: 100,
                        default: 85,
                        hint: '1-100，数值越小文件越小'
                    }
                ]
            },
            generate_thumbnail: {
                label: '生成缩略图',
                endpoint: '/api/tasks/photo/thumbnail',
                fields: [
                    {
                        name: 'photo_id',
                        type: 'select',
                        label: '选择照片',
                        required: true,
                        dataSource: 'photos'
                    },
                    {
                        name: 'width',
                        type: 'number',
                        label: '宽度',
                        min: 50,
                        max: 2000,
                        default: 200,
                        hint: '像素值'
                    },
                    {
                        name: 'height',
                        type: 'number',
                        label: '高度',
                        min: 50,
                        max: 2000,
                        default: 200,
                        hint: '像素值'
                    }
                ]
            },
            batch_process: {
                label: '批量处理',
                endpoint: '/api/tasks/photo/batch',
                fields: [
                    {
                        name: 'photo_ids',
                        type: 'textarea',
                        label: '照片 ID 列表',
                        required: true,
                        placeholder: '每行一个 photo_id',
                        hint: '将 photo_id 用回车分隔'
                    },
                    {
                        name: 'operation',
                        type: 'select',
                        label: '操作',
                        options: [
                            {value: 'compress', label: '压缩'},
                            {value: 'thumbnail', label: '缩略图'}
                        ],
                        default: 'compress'
                    }
                ]
            }
        }
    },

    ai_analysis: {
        icon: '🤖',
        name: 'AI 分析',
        tasks: {
            quality_check: {
                label: 'AI 质量检测',
                endpoint: '/api/tasks/ai/quality-check',
                fields: [
                    {
                        name: 'photo_id',
                        type: 'select',
                        label: '选择照片',
                        required: true,
                        dataSource: 'photos'
                    },
                    {
                        name: 'threshold',
                        type: 'number',
                        label: '质量阈值',
                        min: 0,
                        max: 1,
                        step: 0.1,
                        default: 0.7,
                        hint: '0-1，低于此值被认为质量不合格'
                    }
                ]
            },
            analyze_record: {
                label: '分析巡查记录',
                endpoint: '/api/tasks/ai/analyze-record',
                fields: [
                    {
                        name: 'record_id',
                        type: 'number',
                        label: '记录 ID',
                        required: true,
                        min: 1
                    },
                    {
                        name: 'analysis_type',
                        type: 'select',
                        label: '分析类型',
                        options: [
                            {value: 'comprehensive', label: '综合分析'},
                            {value: 'risk', label: '风险评估'},
                            {value: 'quality', label: '质量检查'}
                        ],
                        default: 'comprehensive'
                    }
                ]
            }
        }
    },

    report_export: {
        icon: '📊',
        name: '报表导出',
        tasks: {
            export_report: {
                label: '导出报表',
                endpoint: '/api/tasks/report/export',
                fields: [
                    {
                        name: 'start_date',
                        type: 'date',
                        label: '开始日期',
                        required: true
                    },
                    {
                        name: 'end_date',
                        type: 'date',
                        label: '结束日期',
                        required: true
                    },
                    {
                        name: 'status',
                        type: 'select',
                        label: '状态筛选',
                        options: [
                            {value: '', label: '全部'},
                            {value: 'pending', label: '待处理'},
                            {value: 'processing', label: '处理中'},
                            {value: 'completed', label: '已完成'}
                        ],
                        default: ''
                    }
                ]
            },
            generate_monthly: {
                label: '生成月报',
                endpoint: '/api/tasks/report/monthly',
                fields: [
                    {
                        name: 'year',
                        type: 'number',
                        label: '年份',
                        min: 2020,
                        max: YEAR_MAX,
                        default: new Date().getFullYear(),
                        required: true
                    },
                    {
                        name: 'month',
                        type: 'number',
                        label: '月份',
                        min: 1,
                        max: 12,
                        default: new Date().getMonth() + 1,
                        required: true
                    }
                ]
            }
        }
    },

    maintenance: {
        icon: '🛠️',
        name: '系统维护',
        tasks: {
            cleanup_cache: {
                label: '清理缓存',
                endpoint: '/api/tasks/maintenance/cleanup-cache',
                fields: [],
                confirmMessage: '确定要清理缓存吗？'
            },
            health_check: {
                label: '健康检查',
                endpoint: '/api/tasks/maintenance/health-check',
                fields: []
            },
            collect_metrics: {
                label: '收集性能指标',
                endpoint: '/api/tasks/maintenance/collect-metrics',
                fields: []
            }
        }
    }
};

// 常量已在文件顶部声明

// ==================== 工具类 ====================

/**
 * API 客户端 - 统一处理 HTTP 请求
 * - 自动加入 CSRF token
 * - 错误处理和重试
 * - 请求超时控制
 */
class APIClient {
    constructor(timeout = 30000) {
        this.timeout = timeout;
        this.retries = 3;
    }

    /**
     * 获取 CSRF token
     */
    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    /**
     * 统一的 fetch 封装
     */
    async request(endpoint, {method = 'GET', body = null, retryCount = 0} = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAccessToken()}`,
                'X-CSRF-Token': this.getCsrfToken()
            };

            const options = {
                method,
                headers,
                signal: AbortSignal.timeout(this.timeout)
            };

            if (body) {
                options.body = JSON.stringify(body);
            }

            const response = await fetch(endpoint, options);

            // 处理 HTTP 错误
            if (!response.ok) {
                const error = new Error(`HTTP ${response.status}`);
                error.status = response.status;
                throw error;
            }

            return await response.json();
        } catch (error) {
            // 网络错误或超时，自动重试
            if (retryCount < this.retries && 
                (error.name === 'AbortError' || !error.status)) {
                console.warn(`请求失败，${1000 * (retryCount + 1)}ms 后重试...`);
                await new Promise(r => setTimeout(r, 1000 * (retryCount + 1)));
                return this.request(endpoint, {method, body, retryCount: retryCount + 1});
            }

            error.message = error.status === 422 
                ? '参数验证失败' 
                : error.status === 401 
                ? '认证失败' 
                : error.message;
            throw error;
        }
    }

    post(endpoint, body) {
        return this.request(endpoint, {method: 'POST', body});
    }

    get(endpoint) {
        return this.request(endpoint, {method: 'GET'});
    }
}

const apiClient = new APIClient();

// 兼容其他页面（dashboard.js / reports.js）对全局 APIClient 的依赖
// 暴露一个轻量代理到 window，提供 get/post 方法
window.APIClient = {
    get: (...args) => apiClient.get(...args),
    post: (...args) => apiClient.post(...args)
};

/**
 * 表单验证器
 */
class FormValidator {
    static validate(fields, data) {
        const errors = {};

        fields.forEach(field => {
            const value = data[field.name];

            // 必填检查
            if (field.required && !value) {
                errors[field.name] = `${field.label} 必填`;
                return;
            }

            // 数字范围检查
            if (field.type === 'number' && value !== undefined && value !== '') {
                const numValue = parseFloat(value);
                if (isNaN(numValue)) {
                    errors[field.name] = `${field.label} 必须是数字`;
                    return;
                }
                if (field.min !== undefined && numValue < field.min) {
                    errors[field.name] = `${field.label} 不能小于 ${field.min}`;
                }
                if (field.max !== undefined && numValue > field.max) {
                    errors[field.name] = `${field.label} 不能大于 ${field.max}`;
                }
            }

            // photo_id 校验：接受整数或 UUID 格式
            if (field.name === 'photo_id' && value) {
                if (!PHOTO_ID_RE.test(value)) {
                    errors[field.name] = '照片 ID 格式不正确（应为整数或UUID）';
                }
            }

            // 年/月业务范围校验（与后端一致）
            if (field.name === 'year' && value !== undefined && value !== '') {
                const num = Number(value);
                if (Number.isNaN(num) || num < YEAR_MIN) {
                    errors[field.name] = `年份必须不小于 ${YEAR_MIN}`;
                }
            }
            if (field.name === 'month' && value !== undefined && value !== '') {
                const num = Number(value);
                if (Number.isNaN(num) || num < 1 || num > 12) {
                    errors[field.name] = '月份必须在 1-12 之间';
                }
            }
        });

        return errors;
    }
}

/**
 * 任务管理器 - 核心业务逻辑
 */
class TaskManager {
    constructor() {
        this.tasks = new Map();  // 用于跟踪已提交的任务
        this.pollers = new Map();  // 任务状态轮询器
    }

    /**
     * 提交任务
     */
    async submit(categoryKey, taskKey, payload) {
        const category = TASK_CONFIG[categoryKey];
        const taskConfig = category.tasks[taskKey];

        if (!taskConfig) {
            throw new Error('任务配置不存在');
        }

        // 表单验证
        const errors = FormValidator.validate(taskConfig.fields, payload);
        if (Object.keys(errors).length > 0) {
            // 始终抛出 Error，避免字符串导致 error.message 为 undefined
            throw new Error(Object.values(errors)[0]);
        }

        try {
            // 提交请求
            console.debug('[taREDACTEDsubmit] endpoint:', taskConfig.endpoint, 'payload:', payload);
            const response = await apiClient.post(taskConfig.endpoint, payload);

            if (!response.success) {
                throw new Error(response.detail || '任务提交失败');
            }

            const taskId = response.task_id;
            const now = new Date();

            // 创建任务记录
            const task = {
                id: taskId,
                name: taskConfig.label,
                state: 'PENDING',
                result: null,
                created_at: now,
                updated_at: now
            };

            // 保存到本地
            this.tasks.set(taskId, task);

            // 启动轮询（每 2 秒查询一次状态）
            this.startPolling(taskId);

            return {success: true, task_id: taskId};
        } catch (error) {
            console.error('任务提交失败:', error);
            throw error;
        }
    }

    /**
     * 启动单个任务的状态轮询
     */
    startPolling(taskId) {
        // 避免重复轮询
        if (this.pollers.has(taskId)) {
            return;
        }

        let consecutiveErrors = 0;
        const pollInterval = setInterval(async () => {
            try {
                // 优先从报表 API 查询，回退到任务 API
                let response = null;
                try {
                    response = await apiClient.get(`/api/reports/task/${taskId}`);
                } catch {
                    response = await apiClient.get(`/api/tasks/status/${taskId}`);
                }

                const task = response.task || {
                    state: response.state,
                    result: response.result,
                    error: response.error
                };

                if (!task) {
                    clearInterval(pollInterval);
                    this.pollers.delete(taskId);
                    return;
                }

                const storedTask = this.tasks.get(taskId);
                if (storedTask) {
                    storedTask.state = task.state;
                    storedTask.result = task.result;
                    storedTask.error = task.error;
                    storedTask.updated_at = new Date();
                }

                // 如果任务完成或失败，停止轮询
                if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(task.state)) {
                    clearInterval(pollInterval);
                    this.pollers.delete(taskId);
                }

                consecutiveErrors = 0;
                renderTasksList();  // 实时更新 UI

            } catch (error) {
                consecutiveErrors++;
                console.warn(`轮询 ${taskId} 失败 (${consecutiveErrors}/3):`, error.message);

                // 连续失败 3 次则停止轮询
                if (consecutiveErrors >= 3) {
                    clearInterval(pollInterval);
                    this.pollers.delete(taskId);
                }
            }
        }, 2000);  // 2 秒轮询一次

        this.pollers.set(taskId, pollInterval);
    }

    /**
     * 获取所有任务（按时间倒序）
     */
    getAllTasks() {
        return Array.from(this.tasks.values())
            .sort((a, b) => b.created_at - a.created_at);
    }

    /**
     * 清空已完成任务
     */
    clearCompleted() {
        for (const [id, task] of this.tasks) {
            if (['SUCCESS', 'FAILURE'].includes(task.state)) {
                this.tasks.delete(id);
            }
        }
    }
}

const taskManager = new TaskManager();

// 暴露 TaskManager 实例到全局，供仪表盘/报表中心复用
window.TaskManager = taskManager;

// ==================== UI 渲染函数 ====================

/**
 * 初始化页面 - 渲染类别菜单和表单容器
 */
async function initPage() {
    // 获取用户信息
    const user = await loadUserInfo();
    const badge = document.getElementById('userBadge');
    if (badge) {
        badge.textContent = user.username;
    }

    // 渲染类别菜单
    if (document.getElementById('taskCategories')) {
        renderCategories();
    }

    // 初始化任务列表
    await refreshTasks();

    // 每 10 秒自动刷新一次任务列表（作为轮询的补充）
    setInterval(refreshTasks, 10000);
}

/**
 * 渲染任务类别菜单
 */
function renderCategories() {
    const container = document.getElementById('taskCategories');
    if (!container) return; // 非任务中心页面
    container.innerHTML = '';

    Object.entries(TASK_CONFIG).forEach(([categoryKey, category]) => {
        const categoryEl = document.createElement('div');
        categoryEl.className = 'taREDACTEDcategory';

        const headerEl = document.createElement('div');
        headerEl.className = 'taREDACTEDcategory-header';
        headerEl.innerHTML = `
            <span class="taREDACTEDcategory-icon">${category.icon}</span>
            <span class="taREDACTEDcategory-title">${category.name}</span>
            <span class="taREDACTEDcategory-toggle">▼</span>
        `;

        const bodyEl = document.createElement('div');
        bodyEl.className = 'taREDACTEDcategory-body';

        const tasksEl = document.createElement('div');
        tasksEl.className = 'category-tasks';

        Object.entries(category.tasks).forEach(([taskKey, task]) => {
            const btnEl = document.createElement('button');
            btnEl.className = 'category-taREDACTEDbtn';
            btnEl.textContent = task.label;
            btnEl.onclick = (e) => {
                e.stopPropagation();
                selectTask(categoryKey, taskKey);
            };
            tasksEl.appendChild(btnEl);
        });

        bodyEl.appendChild(tasksEl);
        categoryEl.appendChild(headerEl);
        categoryEl.appendChild(bodyEl);

        // 展开/收起
        headerEl.onclick = () => {
            headerEl.classList.toggle('active');
            bodyEl.classList.toggle('active');
        };

        container.appendChild(categoryEl);
    });

    // 默认打开第一个类别
    const firstHeader = container.querySelector('.taREDACTEDcategory-header');
    if (firstHeader) {
        firstHeader.classList.add('active');
        firstHeader.nextElementSibling.classList.add('active');
    }
}

/**
 * 选择任务类型 - 渲染对应的表单
 */
function selectTask(categoryKey, taskKey) {
    const category = TASK_CONFIG[categoryKey];
    const taskConfig = category.tasks[taskKey];

    const formContainer = document.getElementById('formContainer');
    formContainer.innerHTML = renderForm(categoryKey, taskKey, taskConfig);

    // 更新菜单样式
    document.querySelectorAll('.category-taREDACTEDbtn').forEach(btn => {
        btn.style.background = btn.textContent === taskConfig.label 
            ? 'rgba(91,139,255,0.24)' 
            : 'rgba(91,139,255,0.08)';
    });
}

/**
 * 动态渲染表单
 */
function renderForm(categoryKey, taskKey, taskConfig) {
    const fieldsHtml = taskConfig.fields.map(field => {
        switch (field.type) {
            case 'number':
                return `
                    <div class="form-group">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <input 
                            type="number" 
                            id="${field.name}"
                            min="${field.min ?? ''}" 
                            max="${field.max ?? ''}"
                            step="${field.step ?? 1}"
                            value="${field.default ?? ''}"
                            placeholder="${field.placeholder ?? ''}"
                        />
                        ${field.hint ? `<div class="form-helper">${field.hint}</div>` : ''}
                    </div>
                `;

            case 'date':
                return `
                    <div class="form-group">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <input 
                            type="date" 
                            id="${field.name}"
                            value="${field.default ?? ''}"
                        />
                    </div>
                `;

            case 'select':
                let options = '';
                if (field.dataSource === 'photos') {
                    // 仅使用数据库整数 photo_id 作为值，文件名作为展示文本
                    options = (window.userPhotos || [])
                        .filter(p => p && p.id !== undefined && p.id !== null)
                        .map(p => `<option value="${p.id}">${p.filename ?? String(p.id)}</option>`)
                        .join('');
                } else {
                    options = field.options?.map(o => `<option value="${o.value}">${o.label}</option>`).join('') || '';
                }

                return `
                    <div class="form-group">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <select id="${field.name}">
                            <option value="">${field.placeholder || '-- 请选择 --'}</option>
                            ${options}
                        </select>
                    </div>
                `;

            case 'textarea':
                return `
                    <div class="form-group">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <textarea 
                            id="${field.name}"
                            placeholder="${field.placeholder ?? ''}"
                        ></textarea>
                        ${field.hint ? `<div class="form-helper">${field.hint}</div>` : ''}
                    </div>
                `;

            default:
                return '';
        }
    }).join('');

    return `
        <div class="form-card active">
            <h2>📝 ${TASK_CONFIG[categoryKey].tasks[taskKey].label}</h2>
            ${fieldsHtml}
            <div class="form-actions">
                <button 
                    class="btn btn-primary" 
                    onclick="submitForm('${categoryKey}', '${taskKey}')"
                >
                    提交任务
                </button>
            </div>
        </div>
    `;
}

/**
 * 提交表单
 */
async function submitForm(categoryKey, taskKey) {
    const taskConfig = TASK_CONFIG[categoryKey].tasks[taskKey];
    const btn = event.target;

    // 检查是否需要二次确认
    if (taskConfig.confirmMessage && !confirm(taskConfig.confirmMessage)) {
        return;
    }

    // 收集表单数据
    const payload = {};
    taskConfig.fields.forEach(field => {
        let value = document.getElementById(field.name)?.value;

        if (field.type === 'number' && value !== '') {
            const num = Number(value);
            if (!Number.isFinite(num)) {
                throw new Error(`${field.label} 必须是有效数字`);
            }
            value = Math.trunc(num);
        }

        if (field.name === 'photo_ids' && value) {
            // 多行输入转数组
            value = value.trim().split('\n').filter(v => v.trim());
        }

        if (value !== undefined && value !== '') {
            // 照片 ID：后端期望字符串类型，保持字符串提交
            if (field.name === 'photo_id') {
                const str = String(value);
                if (!/^\d+$/.test(str) && !PHOTO_ID_RE.test(str)) {
                    throw new Error('照片 ID 格式不正确（应为整数或UUID）');
                }
                payload[field.name] = str;  // 始终作为字符串
            } else {
                payload[field.name] = value;
            }
        }
    });

    try {
        btn.classList.add('loading');

        const result = await taskManager.submit(categoryKey, taskKey, payload);
        showNotification(`✅ 任务已提交！ID: ${result.task_id}`, 'success');

        // 清空表单
        taskConfig.fields.forEach(field => {
            const el = document.getElementById(field.name);
            if (el) el.value = field.default ?? '';
        });

        // 刷新任务列表
        renderTasksList();

    } catch (error) {
        const msg = error?.message || error?.detail || error || '未知错误';
        console.error('任务提交失败:', error);
        showNotification(`❌ ${msg}`, 'error');
    } finally {
        btn.classList.remove('loading');
    }
}

/**
 * 渲染任务列表
 */
function renderTasksList() {
    const container = document.getElementById('tasksList');
    if (!container) return;
    const tasks = taskManager.getAllTasks();

    if (tasks.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无任务</div>';
        return;
    }

    container.innerHTML = tasks.map(task => {
        const statusClass = getStatusClass(task.state);
        const statusText = getStatusText(task.state);
        const timeStr = formatTime(task.updated_at);

        return `
            <div class="taREDACTEDcard">
                <div class="taREDACTEDinfo">
                    <div class="taREDACTEDname">${task.name}</div>
                    <div class="taREDACTEDid">ID: ${task.id}</div>
                    <div class="taREDACTEDmeta">更新于：${timeStr}</div>
                </div>
                <div class="taREDACTEDstatus ${statusClass}">
                    <span>${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

// ==================== 工具函数 ====================

/**
 * 获取任务状态样式类
 */
function getStatusClass(state) {
    const map = {
        'PENDING': 'pending',
        'STARTED': 'running',
        'RUNNING': 'running',
        'SUCCESS': 'success',
        'FAILURE': 'failed',
        'RETRY': 'running',
        'REVOKED': 'failed'
    };
    return map[state] || 'pending';
}

/**
 * 获取任务状态显示文本
 */
function getStatusText(state) {
    const map = {
        'PENDING': '⏳ 等待中',
        'STARTED': '🔄 执行中',
        'RUNNING': '🔄 执行中',
        'SUCCESS': '✅ 已完成',
        'FAILURE': '❌ 失败',
        'RETRY': '🔄 重试中',
        'REVOKED': '⛔ 已取消'
    };
    return map[state] || state;
}

/**
 * 格式化时间显示
 */
function formatTime(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff / 60000) + ' 分钟前';
    if (diff < 86400000) return Math.floor(diff / 3600000) + ' 小时前';
    
    return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 显示通知
 */
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) {
        console.warn('[showNotification] 通知容器未找到');
        return;
    }
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 4000);
}

/**
 * 获取访问令牌
 */
function getAccessToken() {
    return localStorage.getItem('access_token') || sessionStorage.getItem('token') || '';
}

/**
 * 加载用户信息
 */
async function loadUserInfo() {
    try {
        const response = await apiClient.get('/api/user/profile');
        // 后端返回格式：{username, role, is_superuser}
        return {
            username: response.username || 'admin',
            role: response.role || 'admin',
            is_superuser: response.is_superuser || false
        };
    } catch (error) {
        console.warn('加载用户信息失败:', error);
        // 404或其他错误时返回默认用户信息
        return {
            username: '游客',
            role: 'guest',
            is_superuser: false
        };
    }
}

/**
 * 加载照片列表（用于 select 下拉框）
 */
async function loadUserPhotos() {
    try {
        const response = await apiClient.get('/api/photos/user');
        const rawPhotos = response.data || [];

        // 规范化：保留所有记录，优先使用整数 photo_id 作为 id；列表仍可显示非整数项
        let withIntId = 0;
        window.userPhotos = rawPhotos.map(p => {
            const photoId = p.photo_id || p.id; // 优先 photo_id（整数）
            const filename = p.filename || p.name || p.original_name || p.file_name || String(p.id || '未知文件');
            if (photoId && /^\d+$/.test(String(photoId))) withIntId++;
            return { id: photoId, filename };
        });

        console.debug('[photos] 加载成功，总数:', window.userPhotos.length, '含整数ID:', withIntId);
    } catch (error) {
        console.warn('加载照片列表失败:', error);
        window.userPhotos = [];
    }
}

/**
 * 刷新任务列表
 */
async function refreshTasks() {
    try {
        // 如果本地还有未完成的任务，继续轮询
        const unfinishedTasks = taskManager.getAllTasks()
            .filter(t => !['SUCCESS', 'FAILURE', 'REVOKED'].includes(t.state));

        unfinishedTasks.forEach(task => {
            if (!taskManager.pollers.has(task.id)) {
                taskManager.startPolling(task.id);
            }
        });

        renderTasksList();
    } catch (error) {
        console.error('刷新任务列表失败:', error);
    }
}

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', async () => {
    await loadUserPhotos();
    await initPage();
});
