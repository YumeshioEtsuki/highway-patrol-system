// app.js - 公路巡查小程序
App({
  globalData: {
    userInfo: null,
    token: null,
    // API 基础地址（根据实际情况修改）
    // 开发工具：使用 127.0.0.1
    // 真机测试：改为电脑的局域网IP
    baseUrl: 'http://10.61.42.124:5000',  // 真机测试：使用局域网IP
    // baseUrl: 'http://127.0.0.1:5000',  // 开发工具测试时使用这个
    userRole: null  // 'patrol' 或 'admin'
  },

  onLaunch() {
    console.log('小程序启动');
    // 检查登录状态
    this.checkLoginStatus();
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      this.globalData.userRole = userInfo.role;
      console.log('已登录:', userInfo);
    }
  },

  // 保存登录信息
  saveLoginInfo(token, userInfo) {
    this.globalData.token = token;
    this.globalData.userInfo = userInfo;
    this.globalData.userRole = userInfo.role;
    wx.setStorageSync('token', token);
    wx.setStorageSync('userInfo', userInfo);
  },

  // 退出登录
  logout() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    this.globalData.userRole = null;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    wx.reLaunch({
      url: '/pages/login/login'
    });
  }
})
