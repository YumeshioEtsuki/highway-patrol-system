/**
 * 浏览器 Console 诊断脚本
 * 直接复制粘贴到浏览器 DevTools Console 中运行
 */

console.log('='.repeat(70));
console.log('前端提交诊断');
console.log('='.repeat(70));

// 测试 1: 检查表单数据收集
console.log('\n[1] 表单数据收集模拟');
const photoIdField = document.getElementById('photo_id');
const qualityField = document.getElementById('quality');

if (photoIdField && qualityField) {
    const photoId = photoIdField.value;
    const quality = qualityField.value;
    console.log(`  photo_id 值: "${photoId}" (type: ${typeof photoId})`);
    console.log(`  quality 值: "${quality}" (type: ${typeof quality})`);
    
    // 模拟前端提交逻辑
    let payload = {};
    
    // 处理 photo_id
    if (photoId !== '' && photoId !== undefined) {
        const str = String(photoId);
        if (/^\d+$/.test(str) || /^[0-9a-f]{8}/.test(str)) {
            payload.photo_id = str;  // 字符串
            console.log(`  → photo_id 已转换为字符串: "${payload.photo_id}"`);
        }
    }
    
    // 处理 quality
    if (quality !== '' && quality !== undefined) {
        const num = Number(quality);
        if (Number.isFinite(num)) {
            payload.quality = Math.trunc(num);
            console.log(`  → quality 已转换为整数: ${payload.quality}`);
        }
    }
    
    console.log('\n  最终 payload:', JSON.stringify(payload));
} else {
    console.log('  ✗ 找不到表单元素');
}

// 测试 2: 检查 token
console.log('\n[2] 认证令牌检查');
const token = localStorage.getItem('access_token') || sessionStorage.getItem('token');
if (token) {
    console.log(`  ✓ 令牌已存在 (长度: ${token.length})`);
} else {
    console.log(`  ✗ 令牌不存在`);
}

// 测试 3: 手动发送压缩照片请求
console.log('\n[3] 手动发送压缩照片请求');
const testPayload = {
    photo_id: "1",
    quality: 85
};
console.log(`  发送: ${JSON.stringify(testPayload)}`);

fetch('/api/tasks/photo/compress', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || 'NO_TOKEN'}`
    },
    body: JSON.stringify(testPayload)
})
.then(r => {
    console.log(`  HTTP 状态: ${r.status}`);
    return r.json();
})
.then(data => {
    if (data.success) {
        console.log(`  ✓ 成功: ${JSON.stringify(data)}`);
    } else {
        console.log(`  ✗ 失败: ${JSON.stringify(data, null, 2)}`);
    }
})
.catch(err => {
    console.log(`  ✗ 请求错误: ${err.message}`);
});

console.log('\n' + '='.repeat(70));
