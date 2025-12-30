// utils/util.js - 通用工具函数

/**
 * 格式化时间
 */
function formatTime(date) {
  if (!date) return '';
  
  const d = new Date(date);
  const year = d.getFullYear();
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');
  const hour = d.getHours().toString().padStart(2, '0');
  const minute = d.getMinutes().toString().padStart(2, '0');
  const second = d.getSeconds().toString().padStart(2, '0');

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

/**
 * 格式化日期
 */
function formatDate(date) {
  if (!date) return '';
  
  const d = new Date(date);
  const year = d.getFullYear();
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');

  return `${year}-${month}-${day}`;
}

/**
 * 相对时间（如：刚刚、3分钟前）
 */
function relativeTime(date) {
  if (!date) return '';
  
  const now = new Date();
  const past = new Date(date);
  const diff = now - past;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return formatDate(date);
}

/**
 * 问题类型映射
 */
const problemTypes = {
  'road_damage': '路面破损',
  'guardrail': '护栏损坏',
  'sign': '标志缺失',
  'drainage': '排水问题',
  'other': '其他问题'
};

function getProblemTypeName(type) {
  return problemTypes[type] || type;
}

/**
 * 严重程度映射
 */
const severityLevels = {
  1: { name: '轻微', color: '#10b981' },
  2: { name: '一般', color: '#3b82f6' },
  3: { name: '较重', color: '#f59e0b' },
  4: { name: '严重', color: '#ef4444' },
  5: { name: '紧急', color: '#dc2626' }
};

function getSeverityInfo(level) {
  return severityLevels[level] || { name: '未知', color: '#6b7a8f' };
}

/**
 * 状态映射
 */
const statusMap = {
  'pending': { name: '待处理', color: '#f59e0b' },
  'processing': { name: '处理中', color: '#3b82f6' },
  'completed': { name: '已完成', color: '#10b981' },
  'resolved': { name: '已解决', color: '#6b7a8f' }
};

function getStatusInfo(status) {
  return statusMap[status] || { name: '未知', color: '#6b7a8f' };
}

/**
 * 防抖函数
 */
function debounce(fn, delay = 500) {
  let timer = null;
  return function(...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

/**
 * 节流函数
 */
function throttle(fn, interval = 1000) {
  let lastTime = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      fn.apply(this, args);
    }
  };
}

module.exports = {
  formatTime,
  formatDate,
  relativeTime,
  getProblemTypeName,
  getSeverityInfo,
  getStatusInfo,
  debounce,
  throttle
};
