/**
 * 通用工具库 - common.js
 * 
 * 功能清单：
 * 1. showNotification - 全局通知（成功/失败/信息）
 * 2. formatDate - 时间格式化
 * 3. formatFileSize - 文件大小格式化
 * 4. debounce - 防抖函数
 * 5. throttle - 节流函数
 * 6. getCookie - 获取 Cookie
 * 7. setCookie - 设置 Cookie
 * 8. getCSRFToken - 获取 CSRF Token
 * 9. copyToClipboard - 复制到剪贴板
 * 10. downloadFile - 下载文件
 */

// ==================== 通知系统 ====================

/**
 * 显示全局通知
 * @param {string} message - 通知内容
 * @param {string} type - 类型：'success' | 'error' | 'info' | 'warning'
 * @param {number} duration - 持续时间（毫秒），默认 3000
 */
function showNotification(message, type = 'info', duration = 3000) {
    // 查找或创建通知容器
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }

    // 设置样式和内容
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.display = 'block';

    // 自动隐藏
    setTimeout(() => {
        notification.style.display = 'none';
    }, duration);
}

// ==================== 日期时间工具 ====================

/**
 * 格式化日期时间
 * @param {Date|string|number} date - 日期对象、ISO 字符串或时间戳
 * @param {string} format - 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 * 
 * 支持的占位符：
 * - YYYY: 四位年份
 * - MM: 两位月份
 * - DD: 两位日期
 * - HH: 24 小时制小时
 * - mm: 分钟
 * - ss: 秒
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    const d = new Date(date);
    if (isNaN(d.getTime())) {
        return 'Invalid Date';
    }

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

/**
 * 计算相对时间（如"3 分钟前"）
 * @param {Date|string|number} date - 日期
 * @returns {string} 相对时间描述
 */
function timeAgo(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return '刚刚';
    if (minutes < 60) return `${minutes} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 7) return `${days} 天前`;
    return formatDate(date, 'YYYY-MM-DD');
}

// ==================== 文件工具 ====================

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数，默认 2
 * @returns {string} 格式化后的大小（如 "1.23 MB"）
 */
function formatFileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 下载文件
 * @param {string} url - 文件 URL
 * @param {string} filename - 保存文件名
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ==================== 性能优化 ====================

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 * 
 * 使用示例：
 * const debouncedSearch = debounce(() => search(), 300);
 * input.addEventListener('input', debouncedSearch);
 */
function debounce(func, delay = 300) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 间隔时间（毫秒）
 * @returns {Function} 节流后的函数
 * 
 * 使用示例：
 * const throttledScroll = throttle(() => handleScroll(), 100);
 * window.addEventListener('scroll', throttledScroll);
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ==================== Cookie 工具 ====================

/**
 * 获取 Cookie
 * @param {string} name - Cookie 名称
 * @returns {string|null} Cookie 值
 */
function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

/**
 * 设置 Cookie
 * @param {string} name - Cookie 名称
 * @param {string} value - Cookie 值
 * @param {number} days - 有效天数
 */
function setCookie(name, value, days = 7) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

/**
 * 删除 Cookie
 * @param {string} name - Cookie 名称
 */
function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

// ==================== CSRF 工具 ====================

/**
 * 获取 CSRF Token（从 meta 标签）
 * @returns {string|null} CSRF Token
 */
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

// ==================== 剪贴板工具 ====================

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<void>}
 */
async function copyToClipboard(text) {
    try {
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(text);
            showNotification('已复制到剪贴板', 'success');
        } else {
            // 兼容旧浏览器
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showNotification('已复制到剪贴板', 'success');
        }
    } catch (err) {
        console.error('复制失败:', err);
        showNotification('复制失败', 'error');
    }
}

// ==================== 表单验证 ====================

/**
 * 验证电子邮件格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * 验证手机号码（中国）
 * @param {string} phone - 手机号
 * @returns {boolean} 是否有效
 */
function isValidPhone(phone) {
    const re = /^1[3-9]\d{9}$/;
    return re.test(phone);
}

/**
 * 验证身份证号码（中国）
 * @param {string} idCard - 身份证号
 * @returns {boolean} 是否有效
 */
function isValidIDCard(idCard) {
    const re = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
    return re.test(idCard);
}

// ==================== URL 工具 ====================

/**
 * 从 URL 参数获取值
 * @param {string} name - 参数名
 * @returns {string|null} 参数值
 */
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * 更新 URL 参数（不刷新页面）
 * @param {string} name - 参数名
 * @param {string} value - 参数值
 */
function updateUrlParam(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.pushState({}, '', url);
}

// ==================== 对象工具 ====================

/**
 * 深度克隆对象
 * @param {any} obj - 要克隆的对象
 * @returns {any} 克隆后的对象
 */
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    
    const clonedObj = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            clonedObj[key] = deepClone(obj[key]);
        }
    }
    return clonedObj;
}

/**
 * 判断对象是否为空
 * @param {object} obj - 对象
 * @returns {boolean} 是否为空
 */
function isEmptyObject(obj) {
    return Object.keys(obj).length === 0;
}

// ==================== 数组工具 ====================

/**
 * 数组去重
 * @param {Array} arr - 数组
 * @returns {Array} 去重后的数组
 */
function unique(arr) {
    return [...new Set(arr)];
}

/**
 * 根据对象属性分组
 * @param {Array} arr - 数组
 * @param {string} key - 分组键
 * @returns {Object} 分组后的对象
 */
function groupBy(arr, key) {
    return arr.reduce((result, item) => {
        (result[item[key]] = result[item[key]] || []).push(item);
        return result;
    }, {});
}

// ==================== 数字工具 ====================

/**
 * 格式化数字（千位分隔符）
 * @param {number} num - 数字
 * @returns {string} 格式化后的字符串
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 生成随机数
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {number} 随机数
 */
function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ==================== 字符串工具 ====================

/**
 * 截断字符串
 * @param {string} str - 字符串
 * @param {number} length - 最大长度
 * @param {string} suffix - 后缀，默认 '...'
 * @returns {string} 截断后的字符串
 */
function truncate(str, length, suffix = '...') {
    if (str.length <= length) return str;
    return str.substring(0, length) + suffix;
}

/**
 * 转义 HTML 特殊字符
 * @param {string} str - 字符串
 * @returns {string} 转义后的字符串
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 生成 UUID
 * @returns {string} UUID 字符串
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// ==================== 加载状态 ====================

/**
 * 显示全局加载指示器
 * @param {string} message - 加载提示信息
 */
function showLoading(message = '加载中...') {
    let loader = document.getElementById('globalLoader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'globalLoader';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.7);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            color: #fff;
            font-size: 16px;
        `;
        loader.innerHTML = `
            <div style="width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.3); border-top-color: #5b8bff; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            <div style="margin-top: 16px;">${message}</div>
        `;
        document.body.appendChild(loader);
    }
    loader.style.display = 'flex';
}

/**
 * 隐藏全局加载指示器
 */
function hideLoading() {
    const loader = document.getElementById('globalLoader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// ==================== 导出 ====================

// 如果使用模块化（ES6 Modules），可以导出这些函数
// export { showNotification, formatDate, ... };

// 在浏览器环境下，这些函数会自动添加到全局作用域
console.log('✅ common.js 已加载 - 通用工具库就绪');
