// pages/login/login.js
const auth = require('../../utils/auth');
const app = getApp();

Page({
  data: {
    roleType: 'patrol', // 默认选择巡查员
    isLogging: false
  },

  onLoad() {
    // 如果已登录，跳转到对应页面
    if (auth.isLogin()) {
      this.redirectToHome();
    }
  },

  /**
   * 选择角色
   */
  selectRole(e) {
    const role = e.currentTarget.dataset.role;
    this.setData({
      roleType: role
    });
  },

  /**
   * 处理登录
   */
  async handleLogin() {
    if (this.data.isLogging) return;

    this.setData({ isLogging: true });

    try {
      // 1. 获取用户信息授权
      const userInfo = await auth.getUserProfile();
      console.log('获取用户信息成功:', userInfo);

      // 2. 微信登录获取code
      const code = await auth.wxLogin();
      console.log('微信登录成功，code:', code);

      // 3. 调用后端登录接口
      const res = await auth.login(code, userInfo, this.data.roleType);
      console.log('后端登录成功:', res);

      // 4. 保存登录信息
      const token = res.access_token || res.token || app.globalData.token;
      app.saveLoginInfo(token, {
        ...res.user,
        role: res.user?.role || this.data.roleType,
        username: res.user?.username || app.globalData.userInfo?.username
      });

      // 5. 提示并跳转
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      });

      setTimeout(() => {
        this.redirectToHome();
      }, 1500);

    } catch (err) {
      console.error('登录失败:', err);
      this.setData({ isLogging: false });
      
      if (err.errMsg && err.errMsg.includes('getUserProfile')) {
        wx.showToast({
          title: '需要授权才能登录',
          icon: 'none'
        });
      } else if (err.errMsg && err.errMsg.includes('request:fail')) {
        // 网络请求失败
        wx.showModal({
          title: '网络连接失败',
          content: '无法连接到服务器。\n\n真机测试请检查：\n1. 手机和电脑在同一WiFi\n2. app.js中baseUrl已改为电脑IP\n3. 后端服务器已启动',
          showCancel: false
        });
      } else {
        wx.showToast({
          title: err.message || '登录失败，请重试',
          icon: 'none',
          duration: 2000
        });
      }
    }
  },

  /**
   * 跳转到首页
   */
  redirectToHome() {
    const role = this.data.roleType || app.globalData.userRole;
    
    if (role === 'admin') {
      wx.switchTab({
        url: '/pages/admin/list/list'
      });
    } else {
      wx.switchTab({
        url: '/pages/patrol/list/list'
      });
    }
  }
  ,
  /**
   * 进入完善资料/注册页面
   */
  gotoRegister() {
    wx.navigateTo({ url: '/pages/register/register' });
  },
  /**
   * 清除缓存并回到登录
   */
  clearCache() {
    app.logout();
  }
})
