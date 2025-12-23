// utils/auth.js - 认证工具
const request = require('./request');

/**
 * 微信登录
 */
function wxLogin() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (res) => {
        if (res.code) {
          resolve(res.code);
        } else {
          reject(new Error('获取code失败'));
        }
      },
      fail: reject
    });
  });
}

/**
 * 获取用户信息
 */
function getUserProfile() {
  return new Promise((resolve, reject) => {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        resolve(res.userInfo);
      },
      fail: reject
    });
  });
}

/**
 * 后端登录
 * @param {string} code - 微信登录code
 * @param {object} userInfo - 用户信息
 * @param {string} role - 角色 'patrol' 或 'admin'
 */
async function login(code, userInfo, role = 'patrol') {
  // 后端暂无微信登录接口，使用“注册或登录”策略：
  // 1) 以 code 生成一个唯一用户名
  // 2) 尝试注册（已存在则忽略错误）
  // 3) 用固定密码登录获取 token
  const suffix = (code || '').slice(-8) || 'user';
  const username = role === 'admin' ? `admin_wx_${suffix}` : `wx_${suffix}`;
  const password = role === 'admin' ? 'Admin123456!' : 'Wx123456!';
  const realName = role === 'admin' ? (userInfo?.nickName || '管理员用户') : (userInfo?.nickName || '微信用户');

  // 先尝试注册
  try {
    // phone 使用 null，避免空字符串触发唯一约束
    await request.post('/api/register', {
      username,
      password,
      real_name: realName,
      phone: null
    }, { showLoading: false });
  } catch (err) {
    // 如果已存在则忽略
    if (!(err?.statusCode === 400 || err?.statusCode === 422)) {
      throw err;
    }
  }

  // 再登录
  const res = await request.post('/api/login', {
    username,
    password
  });

  // 保存全局信息
  const app = getApp();
  app.globalData.token = res.access_token || res.token;
  app.globalData.userInfo = {
    ...userInfo,
    username,
    role: res.user?.role || role
  };
  app.globalData.userRole = res.user?.role || role;

  return res;
}

/**
 * 检查是否登录
 */
function isLogin() {
  const app = getApp();
  return !!app.globalData.token;
}

/**
 * 检查权限（必须登录）
 */
function checkAuth() {
  return new Promise((resolve, reject) => {
    if (isLogin()) {
      resolve(true);
    } else {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      setTimeout(() => {
        wx.reLaunch({
          url: '/pages/login/login'
        });
        reject(false);
      }, 1500);
    }
  });
}

module.exports = {
  wxLogin,
  getUserProfile,
  login,
  isLogin,
  checkAuth
};
