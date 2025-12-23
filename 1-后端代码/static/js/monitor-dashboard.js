/**
 * 数据库监控仪表板 JavaScript
 */

// 全局状态
let charts = {};
let metricsData = null;
let authToken = null;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 从 localStorage 获取 token
    authToken = localStorage.getItem('token');
    
    if (!authToken) {
        // 如果没有 token，重定向到登录页面
        window.location.href = '/login';
        return;
    }

    // 初始化图表
    initCharts();
    
    // 加载数据
    await refreshData();
    
    // 定时刷新数据（每 30 秒）
    setInterval(refreshData, 30000);
});

/**
 * 刷新所有数据
 */
async function refreshData() {
    try {
        // 并行加载数据
        const [metrics, history, slowQueries, health, recommendations] = await Promise.all([
            getMetrics(),
            getMetricsHistory(),
            getSlowQueries(),
            getIndexHealth(),
            getRecommendations()
        ]);

        // 更新 UI
        updateMetrics(metrics);
        updateCharts(history);
        updateSlowQueries(slowQueries);
        updateIndexHealth(health);
        updateRecommendations(recommendations);

        // 更新健康状态指示
        updateHealthStatus(metrics, recommendations);

    } catch (error) {
        console.error('Error refreshing data:', error);
        showError('无法加载监控数据');
    }
}

/**
 * 获取当前性能指标
 */
async function getMetrics() {
    const response = await fetch('/api/admin/monitor/metrics/current', {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to fetch metrics');
    const data = await response.json();
    metricsData = data.data;
    return data.data;
}

/**
 * 获取性能指标历史
 */
async function getMetricsHistory(hours = 24) {
    const response = await fetch(`/api/admin/monitor/metrics/history?hours=${hours}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to fetch history');
    return await response.json();
}

/**
 * 获取最近慢查询
 */
async function getSlowQueries(limit = 5) {
    const response = await fetch(`/api/admin/monitor/slow-queries/top?limit=${limit}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to fetch slow queries');
    return await response.json();
}

/**
 * 获取索引健康状态
 */
async function getIndexHealth() {
    const response = await fetch('/api/admin/monitor/indexes/health', {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to fetch index health');
    return await response.json();
}

/**
 * 获取优化建议
 */
async function getRecommendations() {
    const response = await fetch('/api/admin/monitor/recommendations', {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return await response.json();
}

/**
 * 更新性能指标卡片
 */
function updateMetrics(metrics) {
    if (!metrics) return;

    const html = `
        <div class="metric-card">
            <h3>查询速率</h3>
            <div class="metric-value">${(metrics.queries_per_sec || 0).toFixed(2)}</div>
            <div class="metric-unit">次/秒</div>
        </div>

        <div class="metric-card">
            <h3>慢查询</h3>
            <div class="metric-value">${metrics.slow_queries_per_min || 0}</div>
            <div class="metric-unit">次/分钟</div>
        </div>

        <div class="metric-card">
            <h3>活跃连接数</h3>
            <div class="metric-value">${metrics.active_connections || 0}</div>
            <div class="metric-unit">个</div>
        </div>

        <div class="metric-card">
            <h3>平均查询时间</h3>
            <div class="metric-value">${(metrics.avg_query_time_ms || 0).toFixed(1)}</div>
            <div class="metric-unit">毫秒</div>
        </div>

        <div class="metric-card">
            <h3>缓存命中率</h3>
            <div class="metric-value">${((metrics.cache_hit_ratio || 0) * 100).toFixed(1)}%</div>
            <div class="metric-unit">命中率</div>
        </div>

        <div class="metric-card">
            <h3>锁等待时间</h3>
            <div class="metric-value">${(metrics.lock_wait_time_ms || 0).toFixed(1)}</div>
            <div class="metric-unit">毫秒</div>
        </div>
    `;

    document.getElementById('metricsGrid').innerHTML = html;
}

/**
 * 初始化图表
 */
function initCharts() {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };

    // 查询速率图表
    const queriesCtx = document.getElementById('queriesChart').getContext('2d');
    charts.queries = new Chart(queriesCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '查询速率 (次/秒)',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: defaultOptions
    });

    // 查询延迟图表
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    charts.latency = new Chart(latencyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '平均查询时间 (毫秒)',
                data: [],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: defaultOptions
    });

    // 缓存命中率图表
    const cacheCtx = document.getElementById('cacheChart').getContext('2d');
    charts.cache = new Chart(cacheCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '缓存命中率 (%)',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: defaultOptions
    });

    // 连接数图表
    const connectionsCtx = document.getElementById('connectionsChart').getContext('2d');
    charts.connections = new Chart(connectionsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '活跃连接数',
                data: [],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: defaultOptions
    });
}

/**
 * 更新图表数据
 */
function updateCharts(historyData) {
    if (!historyData.data) return;

    const data = historyData.data;

    // 提取时间标签（每小时一个）
    const labels = data.timestamps ? data.timestamps.map(ts => {
        const date = new Date(ts);
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }) : [];

    // 更新查询速率
    if (charts.queries && data.queries_per_sec) {
        charts.queries.data.labels = labels;
        charts.queries.data.datasets[0].data = data.queries_per_sec;
        charts.queries.update();
    }

    // 更新查询延迟
    if (charts.latency && data.avg_query_time_ms) {
        charts.latency.data.labels = labels;
        charts.latency.data.datasets[0].data = data.avg_query_time_ms;
        charts.latency.update();
    }

    // 更新缓存命中率
    if (charts.cache && data.cache_hit_ratio) {
        charts.cache.data.labels = labels;
        charts.cache.data.datasets[0].data = data.cache_hit_ratio.map(v => (v * 100).toFixed(1));
        charts.cache.update();
    }

    // 更新活跃连接数
    if (charts.connections && data.active_connections) {
        charts.connections.data.labels = labels;
        charts.connections.data.datasets[0].data = data.active_connections;
        charts.connections.update();
    }
}

/**
 * 更新慢查询列表
 */
function updateSlowQueries(data) {
    if (!data.data || data.data.length === 0) {
        document.getElementById('slowQueriesList').innerHTML = '<div class="no-data">暂无慢查询</div>';
        return;
    }

    const html = data.data.slice(0, 5).map(query => `
        <div class="query-item">
            <div style="color: #ef4444; font-weight: 600;">
                ⏱️ ${query.duration || 0} ms
            </div>
            <div class="query-text">${escapeHtml(query.query || '')}</div>
            <div class="query-meta">
                <span>📊 扫描行数: ${query.rows_examined || 0}</span>
                <span>📤 返回行数: ${query.rows_returned || 0}</span>
                <span>⏰ 时间: ${new Date(query.timestamp).toLocaleString('zh-CN')}</span>
            </div>
        </div>
    `).join('');

    document.getElementById('slowQueriesList').innerHTML = html;
}

/**
 * 更新索引健康状态
 */
function updateIndexHealth(data) {
    if (!data.health_summary) {
        document.getElementById('indexHealthContent').innerHTML = '<div class="no-data">暂无数据</div>';
        return;
    }

    const health = data.health_summary;
    const unused = data.unused_indexes || [];

    let html = `
        <div style="margin-bottom: 20px;">
            <p style="color: #666; margin-bottom: 10px;">整体索引健康分数</p>
            <div class="health-score">${(health.health_score || 0).toFixed(1)}/100</div>
            <p style="color: #999; font-size: 13px; margin-top: 5px;">
                总索引数: ${health.total_indexes || 0} | 健康索引: ${health.healthy_indexes || 0}
            </p>
        </div>
    `;

    if (unused.length > 0) {
        html += `
            <h4 style="color: #333; margin: 15px 0 10px; font-weight: 600;">未使用的索引</h4>
            <table class="index-table">
                <thead>
                    <tr>
                        <th>表名</th>
                        <th>索引名</th>
                        <th>列</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    ${unused.map(idx => `
                        <tr>
                            <td>${escapeHtml(idx.table_name || '')}</td>
                            <td>${escapeHtml(idx.index_name || '')}</td>
                            <td>${escapeHtml(idx.columns || '')}</td>
                            <td>${escapeHtml(idx.created_date || '-')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    document.getElementById('indexHealthContent').innerHTML = html;
}

/**
 * 更新优化建议
 */
function updateRecommendations(data) {
    if (!data.data || data.data.length === 0) {
        document.getElementById('recommendationsList').innerHTML = '<div class="no-data">暂无建议</div>';
        return;
    }

    const html = data.data.map(rec => `
        <div class="recommendation-item ${rec.priority.toLowerCase()}">
            <span class="recommendation-priority ${rec.priority.toLowerCase()}">
                ${rec.priority === 'HIGH' ? '⚠️ 高优先级' : rec.priority === 'MEDIUM' ? '⚡ 中优先级' : '💡 低优先级'}
            </span>
            <p style="color: #333; font-weight: 600; margin-bottom: 8px;">${escapeHtml(rec.description || '')}</p>
            <p style="color: #666; font-size: 13px; margin-bottom: 10px;">
                📝 ${escapeHtml(rec.suggested_action || '暂无建议')}
            </p>
            <p style="color: #999; font-size: 13px; margin-bottom: 10px;">
                📈 预期性能提升: ${rec.estimated_improvement || 0}%
            </p>
            <div style="display: flex; gap: 10px;">
                <button class="button" onclick="applyRecommendation(${rec.id})">应用建议</button>
                <button class="button danger" onclick="dismissRecommendation(${rec.id})">忽略</button>
            </div>
        </div>
    `).join('');

    document.getElementById('recommendationsList').innerHTML = html;
}

/**
 * 更新健康状态指示
 */
function updateHealthStatus(metrics, recommendations) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    let status = 'healthy';
    let message = '系统运行正常';

    // 检查指标
    if (metrics) {
        if ((metrics.slow_queries_per_min || 0) > 10) {
            status = 'warning';
            message = '检测到大量慢查询';
        }

        if ((metrics.slow_queries_per_min || 0) > 20) {
            status = 'error';
            message = '严重: 慢查询过多，需要优化';
        }

        if ((metrics.cache_hit_ratio || 0) < 0.3) {
            if (status === 'healthy') {
                status = 'warning';
                message = '缓存命中率较低';
            }
        }
    }

    // 检查高优先级建议
    if (recommendations.data && recommendations.data.some(r => r.priority === 'HIGH')) {
        if (status === 'healthy') {
            status = 'warning';
            message = '存在高优先级优化建议';
        }
    }

    indicator.className = `status-indicator status-${status}`;
    statusText.textContent = message;
}

/**
 * 应用建议
 */
async function applyRecommendation(recommendationId) {
    if (!confirm('确认要应用此建议吗？')) return;

    try {
        const response = await fetch(`/api/admin/monitor/recommendations/${recommendationId}/apply`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (!response.ok) throw new Error('Failed to apply recommendation');

        alert('建议已应用');
        await refreshData();
    } catch (error) {
        console.error('Error applying recommendation:', error);
        alert('应用建议失败');
    }
}

/**
 * 忽略建议
 */
async function dismissRecommendation(recommendationId) {
    if (!confirm('确认要忽略此建议吗？')) return;

    try {
        const response = await fetch(`/api/admin/monitor/recommendations/${recommendationId}/dismiss`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (!response.ok) throw new Error('Failed to dismiss recommendation');

        await refreshData();
    } catch (error) {
        console.error('Error dismissing recommendation:', error);
        alert('忽略建议失败');
    }
}

/**
 * 生成优化建议
 */
async function generateRecommendations() {
    try {
        const response = await fetch('/api/admin/monitor/recommendations/generate', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (!response.ok) throw new Error('Failed to generate recommendations');

        const data = await response.json();
        alert(`已生成 ${data.generated || 0} 条建议，其中 ${data.saved || 0} 条已保存`);
        await refreshData();
    } catch (error) {
        console.error('Error generating recommendations:', error);
        alert('生成建议失败');
    }
}

/**
 * HTML 转义
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 显示错误
 */
function showError(message) {
    console.error(message);
    // 可以在页面上显示错误提示
}
