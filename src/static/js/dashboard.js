/**
 * 运营总览 - 配置驱动脚本
 * 依赖：common.js, tasks.js
 */

const DASHBOARD_CONFIG = {
    kpis: [
        { key: 'total_records', label: '总记录数', fetch: '/api/admin/stats' },
        { key: 'pending', label: '待处理', fetch: '/api/admin/stats' },
        { key: 'recent_7days', label: '近7天新增', fetch: '/api/admin/stats' },
        { key: 'active_tasks', label: '活跃任务', fetch: '/api/tasks/list' },
    ],
    filters: [
        { name: 'date', type: 'date', label: '日期', default: () => new Date().toISOString().split('T')[0] },
        { name: 'task_type', type: 'select', label: '任务类型', options: [
            { value: '', label: '全部' },
            { value: 'compress_photo', label: '压缩照片' },
            { value: 'generate_thumbnail', label: '生成缩略图' },
            { value: 'export_excel', label: '导出 Excel' }
        ]}
    ],
    quickActions: [
        { label: '刷新 KPI', action: 'refreshKPI' },
        { label: '清理已完成任务', action: 'clearCompletedTasks' }
    ]
};

(async function initDashboard(){
    renderFilters();
    renderQuickActions();
    await renderKPI();
    renderRecentTasks();
})();

async function renderKPI(){
    const container = document.getElementById('kpiContainer');
    if (!container) return;
    container.innerHTML = '<div class="loading" style="text-align:center;padding:20px;color:#94a3b8;">📊 加载中...</div>';
    
    try {
        const client = window.APIClient;
        if (!client || typeof client.get !== 'function') {
            throw new Error('APIClient 未初始化，请先加载 tasks.js');
        }
        
        // 获取统计数据（使用实际存在的API）
        const statsRes = await client.get('/api/admin/stats');
        console.log('[dashboard] stats response:', statsRes);
        
        // 获取任务列表
        let activeTasks = 0;
        try {
            if (window.TaskManager && typeof window.TaskManager.getAllTasks === 'function') {
                activeTasks = window.TaskManager.getAllTasks().filter(t => 
                    t.status === 'running' || t.status === 'pending'
                ).length;
            }
        } catch (e) {
            console.warn('[dashboard] 获取任务数量失败:', e);
        }
        
        // 适配实际API返回的数据结构
        const total = statsRes.total_records || 0;
        const pending = statsRes.status_breakdown?.pending || 0;
        const recent7 = statsRes.recent_7_days || 0;
        
        const kpiData = [
            { label: '总记录数', value: total },
            { label: '待处理', value: pending },
            { label: '近7天新增', value: recent7 },
            { label: '活跃任务', value: activeTasks }
        ];
        
        container.innerHTML = '';
        kpiData.forEach(kpi => {
            const item = document.createElement('div');
            item.className = 'kpi-item';
            item.innerHTML = `<div class="kpi-title">${kpi.label}</div><div class="kpi-value">${kpi.value}</div>`;
            container.appendChild(item);
        });
    } catch (e) {
        console.error('[dashboard] 加载 KPI 失败:', e);
        container.innerHTML = '<div class="error-state" style="text-align:center;padding:20px;color:#ef4444;background:rgba(239,68,68,0.1);border-radius:12px;">⚠️ 加载失败：' + (e.message || '未知错误') + '</div>';
    }
}

function renderFilters(){
    const container = document.getElementById('filterForm');
    if (!container) return;
    container.innerHTML = '';
    DASHBOARD_CONFIG.filters.forEach(f => {
        const group = document.createElement('div');
        group.className = 'form-group';
        const label = document.createElement('label'); label.textContent = f.label; group.appendChild(label);
        let input;
        if (f.type === 'select'){
            input = document.createElement('select');
            (f.options||[]).forEach(opt=>{
                const o = document.createElement('option'); o.value=opt.value; o.textContent=opt.label; input.appendChild(o);
            });
        } else {
            input = document.createElement('input'); input.type = f.type;
        }
        input.id = f.name; input.name = f.name;
        if (f.default){ input.value = typeof f.default==='function'? f.default(): f.default; }
        group.appendChild(input);
        container.appendChild(group);
    });
    const actions = document.createElement('div');
    const applyBtn = document.createElement('button'); applyBtn.className='btn btn-primary'; applyBtn.textContent='应用过滤';
    applyBtn.onclick = () => { showNotification('过滤已应用', 'info'); renderRecentTasks(); };
    actions.appendChild(applyBtn);
    container.appendChild(actions);
}

function renderQuickActions(){
    const container = document.getElementById('quickActions');
    if (!container) return;
    DASHBOARD_CONFIG.quickActions.forEach(a => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary';
        btn.textContent = a.label;
        btn.onclick = () => {
            if (typeof window[a.action] === 'function') window[a.action]();
        };
        container.appendChild(btn);
    });
}

// 最近任务（复用 TaskManager 的状态）
function renderRecentTasks(){
    const container = document.getElementById('recentTasks');
    if (!container) return;
    container.innerHTML = '';
    if (!window.TaskManager || typeof window.TaskManager.getAllTasks !== 'function') {
        container.innerHTML = '<div class="empty-state" style="text-align:center;padding:20px;color:#94a3b8;">⏳ 加载中...</div>';
        return;
    }
    const tasks = window.TaskManager.getAllTasks().slice(-10).reverse();
    if (!tasks.length){ container.textContent = '暂无任务'; return; }
    tasks.forEach(t => {
        const row = document.createElement('div');
        row.style.display = 'grid';
        row.style.gridTemplateColumns = '2fr 1fr 1fr';
        row.style.gap = '8px';
        row.style.padding = '8px 0';
        row.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
        row.innerHTML = `<div>${t.name} <small style="color:#94a3b8">${t.task_id}</small></div><div>${t.state}</div><div>${formatDate(new Date())}</div>`;
        container.appendChild(row);
    });
}

// 快捷操作实现
async function refreshKPI() {
    try {
        await renderKPI();
        if (typeof showNotification === 'function') {
            showNotification('KPI 已刷新', 'success');
        }
    } catch (error) {
        console.error('[refreshKPI] 错误:', error);
    }
}

function clearCompletedTasks(){
    if (!TaskManager || !TaskManager.clearCompleted) {
        if (typeof showNotification === 'function') {
            showNotification('功能未就绪', 'warning');
        }
        return;
    }
    TaskManager.clearCompleted();
    renderRecentTasks();
    if (typeof showNotification === 'function') {
        showNotification('已清理完成任务', 'success');
    }
}
