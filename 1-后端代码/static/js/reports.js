/**
 * 报表中心 - 配置驱动脚本
 * 依赖：common.js, tasks.js（APIClient/TaskManager/FormRenderer）
 */

// 报表任务配置（可扩展）
const REPORT_TASK_CONFIG = {
    report_export: {
        icon: '📤',
        name: '报表导出',
        tasks: {
            export_excel: {
                label: '导出 Excel',
                endpoint: '/api/reports/export/excel',
                fields: [
                    { name: 'start_date', type: 'date', label: '开始日期', required: true },
                    { name: 'end_date', type: 'date', label: '结束日期', required: true },
                    { name: 'include_photos', type: 'select', label: '是否包含照片', options: [
                        { value: 'yes', label: '是' },
                        { value: 'no', label: '否' }
                    ], default: 'no' }
                ]
            },
            export_pdf: {
                label: '导出 PDF',
                endpoint: '/api/reports/export/pdf',
                fields: [
                    { name: 'start_date', type: 'date', label: '开始日期', required: true },
                    { name: 'end_date', type: 'date', label: '结束日期', required: true },
                    { name: 'title', type: 'text', label: '标题', placeholder: '（可选）报表标题' }
                ]
            }
        }
    },
    monthly_reports: {
        icon: '🗓️',
        name: '月报生成',
        tasks: {
            generate_monthly: {
                label: '生成月报',
                endpoint: '/api/reports/monthly/generate',
                fields: [
                    { name: 'year', type: 'number', label: '年份', min: 2020, max: 2030, required: true, default: new Date().getFullYear() },
                    { name: 'month', type: 'number', label: '月份', min: 1, max: 12, required: true, default: (new Date().getMonth() + 1) }
                ]
            }
        }
    }
};

// 页面渲染逻辑
(function initReportsPage() {
    const categoriesContainer = document.createElement('div');
    const formContainer = document.getElementById('formContainer');
    const tasksList = document.getElementById('tasksList');

    // 渲染类别按钮
    categoriesContainer.style.display = 'flex';
    categoriesContainer.style.flexDirection = 'column';
    categoriesContainer.style.gap = '8px';

    Object.keys(REPORT_TASK_CONFIG).forEach(catKey => {
        const cat = REPORT_TASK_CONFIG[catKey];
        const header = document.createElement('div');
        header.className = 'category-header';
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '8px';
        header.innerHTML = `<span>${cat.icon}</span><strong>${cat.name}</strong>`;
        categoriesContainer.appendChild(header);

        const tasks = cat.tasks;
        Object.keys(tasks).forEach(taskKey => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-secondary';
            btn.textContent = tasks[taskKey].label;
            btn.onclick = () => renderTaskForm(catKey, taskKey);
            categoriesContainer.appendChild(btn);
        });
    });

    // 左侧放分类按钮
    const panel = document.querySelector('.panel');
    panel.insertBefore(categoriesContainer, formContainer);

    // 默认显示第一个任务
    const firstCategory = Object.keys(REPORT_TASK_CONFIG)[0];
    const firstTask = Object.keys(REPORT_TASK_CONFIG[firstCategory].tasks)[0];
    renderTaskForm(firstCategory, firstTask);

    // 渲染任务表单
    function renderTaskForm(catKey, taskKey) {
        const cfg = REPORT_TASK_CONFIG[catKey].tasks[taskKey];
        formContainer.innerHTML = '';

        const card = document.createElement('div');
        card.className = 'form-card';
        card.style.display = 'block';
        card.innerHTML = `<h2>${cfg.label}</h2>`;

        cfg.fields.forEach(field => {
            const group = document.createElement('div');
            group.className = 'form-group';
            const label = document.createElement('label');
            label.textContent = field.label + (field.required ? ' *' : '');
            group.appendChild(label);

            let input;
            if (field.type === 'select') {
                input = document.createElement('select');
                (field.options || []).forEach(opt => {
                    const o = document.createElement('option');
                    o.value = opt.value; o.textContent = opt.label; input.appendChild(o);
                });
                if (field.default) input.value = field.default;
            } else {
                input = document.createElement('input');
                input.type = field.type;
                if (field.placeholder) input.placeholder = field.placeholder;
                if (field.min !== undefined) input.min = field.min;
                if (field.max !== undefined) input.max = field.max;
                if (field.default !== undefined) input.value = (typeof field.default === 'function') ? field.default() : field.default;
            }
            input.id = field.name; input.name = field.name;
            if (field.required) input.required = true;
            group.appendChild(input);

            if (field.hint) {
                const helper = document.createElement('div');
                helper.className = 'form-helper'; helper.textContent = field.hint; group.appendChild(helper);
            }

            card.appendChild(group);
        });

        const actions = document.createElement('div');
        actions.className = 'form-actions';
        const submitBtn = document.createElement('button');
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = '提交';
        submitBtn.onclick = async () => {
            const payload = collectPayload(cfg.fields);
            const errors = validateFields(cfg.fields, payload);
            if (Object.keys(errors).length) {
                showNotification(Object.values(errors).join('; '), 'error');
                return;
            }
            try {
                submitBtn.disabled = true;
                submitBtn.textContent = '提交中...';
                
                const res = await (window.APIClient ? window.APIClient.post(cfg.endpoint, payload) : Promise.reject(new Error('APIClient 未初始化')));
                if (res && res.task_id) {
                    // 添加任务到全局 TaskManager（从 tasks.js 继承）
                    if (window.TaskManager && typeof window.TaskManager.submit === 'function') {
                        window.TaskManager.tasks.set(res.task_id, {
                            id: res.task_id,
                            name: cfg.label,
                            state: 'PENDING',
                            result: null,
                            created_at: new Date(),
                            updated_at: new Date()
                        });
                        window.TaskManager.startPolling(res.task_id);
                    }
                    refreshTasks();
                    showNotification('✅ 任务已提交 ID: ' + res.task_id, 'success');
                    // 清空表单
                    cfg.fields.forEach(f => {
                        const el = document.getElementById(f.name);
                        if (el) el.value = f.default || '';
                    });
                } else {
                    showNotification('任务提交成功，但未返回 task_id', 'warning');
                }
            } catch (e) {
                console.error(e);
                showNotification('提交失败，请稍后重试: ' + (e.message || ''), 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '提交';
            }
        };
        actions.appendChild(submitBtn);
        card.appendChild(actions);

        formContainer.appendChild(card);
    }

    function collectPayload(fields) {
        const data = {};
        fields.forEach(f => {
            const el = document.getElementById(f.name);
            if (!el) return;
            data[f.name] = el.value;
        });
        return data;
    }

    function validateFields(fields, data) {
        const errors = {};
        fields.forEach(f => {
            const v = data[f.name];
            if (f.required && (v === '' || v === undefined)) {
                errors[f.name] = `${f.label} 必填`;
                return;
            }
            if (f.type === 'number') {
                const num = Number(v);
                if (f.min !== undefined && num < f.min) errors[f.name] = `${f.label} 最小 ${f.min}`;
                if (f.max !== undefined && num > f.max) errors[f.name] = `${f.label} 最大 ${f.max}`;
            }
        });
        return errors;
    }
})();

// 复用任务列表渲染（来自 tasks.js）
function refreshTasks() {
    if (typeof window.renderTasksList === 'function') {
        window.renderTasksList();
    } else {
        // 简单刷新逻辑占位：实际由 tasks.js 中的轮询管理
        console.log('Refresh tasks list');
    }
}
