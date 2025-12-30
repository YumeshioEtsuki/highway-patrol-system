// pages/profile/profile.js
const app = getApp();

Page({
  data: {
    userInfo: {},
    userRole: '',
    baseUrl: ''
  },

  onShow() {
    this.setData({
      userInfo: app.globalData.userInfo || {},
      userRole: app.globalData.userRole || '',
      baseUrl: app.globalData.baseUrl || ''
    });
  },

  copyText(e) {
    const text = e.currentTarget.dataset.text;
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' });
      }
    });
  },

  switchRole() {
    const newRole = this.data.userRole === 'admin' ? 'patrol' : 'admin';
    wx.showModal({
      title: '切换角色',
      content: `确定切换到${newRole === 'admin' ? '管理员' : '巡查员'}模式？`,
      success: (res) => {
        if (res.confirm) {
          app.globalData.userRole = newRole;
          app.globalData.userInfo.role = newRole;
          this.setData({ userRole: newRole });
          
          wx.showToast({ title: '切换成功', icon: 'success' });
          
          setTimeout(() => {
            wx.switchTab({
              url: newRole === 'admin' ? '/pages/admin/list/list' : '/pages/patrol/list/list'
            });
          }, 1500);
        }
      }
    });
  },

  showHelp() {
    wx.showModal({
      title: '使用帮助',
      content: '【巡查员】\n• 创建巡查记录\n• 上传现场照片\n• 查看处理进度\n\n【管理员】\n• 审核待处理记录\n• 标记处理状态\n• 添加处理备注\n\n【常见问题】\n• GPS定位：需在室外或信号好的地方\n• 照片上传：建议使用WiFi，支持最多9张\n• 角色切换：点击"切换角色"即可',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有本地缓存数据吗？清除后需要重新登录。',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '清除中...' });
          
          // 清除本地存储
          try {
            wx.clearStorageSync();
            wx.hideLoading();
            wx.showToast({ title: '清除成功', icon: 'success' });
            
            setTimeout(() => {
              app.logout();
            }, 1500);
          } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: '清除失败', icon: 'none' });
          }
        }
      }
    });
  },

  showAbout() {
    wx.showModal({
      title: '公路巡查系统',
      content: '版本：v1.0.0\n\n基于微信小程序的公路巡查数据采集系统\n\n功能：\n✓ 实时GPS定位\n✓ 照片自动压缩\n✓ 在线审核处理\n✓ 多角色权限\n\n© 2025 Highway Patrol System',
      showCancel: false,
      confirmText: '好的'
    });
  },

  handleLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.logout();
        }
      }
    });
  }
})
