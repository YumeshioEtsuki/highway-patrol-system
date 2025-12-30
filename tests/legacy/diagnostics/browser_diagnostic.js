
console.log('='.repeat(60));
console.log('前端诊断脚本 - 在浏览器 Console 中运行');
console.log('='.repeat(60));

// ===== 第一部分：数据绑定诊断 =====
console.log('\n[照片数据诊断]');
console.log('window.userPhotos 是否存在:', typeof window.userPhotos !== 'undefined');
if (window.userPhotos) {
    console.log('  - 总数:', window.userPhotos.length);
    console.log('  - 前3条:', window.userPhotos.slice(0, 3));
} else {
    console.log('  ⚠️  window.userPhotos 未定义');
}

// ===== 第二部分：Select 元素诊断 =====
console.log('\n[照片选择框诊断]');
const photoSelect = document.getElementById('photo_id');
if (photoSelect) {
    console.log('✓ photo_id select 元素存在');
    console.log('  - 选项数:', photoSelect.options.length);
    const opts = [];
    for (let i = 1; i <= Math.min(3, photoSelect.options.length - 1); i++) {
        opts.push(\`value=\${photoSelect.options[i].value}, text=\${photoSelect.options[i].text}\`);
    }
    console.log('  - 前3项:', opts.join(' | '));
} else {
    console.log('✗ photo_id select 元素不存在');
}

// ===== 第三部分：Monitor API 诊断 =====
console.log('\n[Monitor 数据诊断]');
fetch('/api/admin/monitor/metrics/current', {
    headers: {'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || '')}
})
.then(r => r.json())
.then(data => {
    console.log('✓ Monitor API 响应:');
    console.log('  status:', data.status);
    console.log('  data:', data.data ? '有数据' : '⚠️ null');
    if (data.data) {
        console.log('  数据字段:', Object.keys(data.data).join(', '));
    }
})
.catch(err => console.error('✗ Monitor API 请求失败:', err));

// ===== 第四部分：照片 API 诊断 =====
console.log('\n[照片 API 诊断]');
fetch('/api/photos/user', {
    headers: {'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || '')}
})
.then(r => r.json())
.then(data => {
    console.log('✓ 照片 API 响应:');
    console.log('  success:', data.success);
    console.log('  total:', data.total);
    if (data.data && data.data.length > 0) {
        console.log('  数据结构:', Object.keys(data.data[0]).join(', '));
        console.log('  前3条数据:');
        data.data.slice(0, 3).forEach((p, i) => {
            console.log(\`    [\${i}] id=\${p.id} (type: \${typeof p.id}), filename=\${p.filename}\`);
        });
    } else {
        console.log('  ⚠️ 无数据');
    }
})
.catch(err => console.error('✗ 照片 API 请求失败:', err));

console.log('\n诊断完成！');
console.log('='.repeat(60));
