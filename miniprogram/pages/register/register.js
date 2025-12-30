// pages/register/register.js
const request = require('../../utils/request');
const app = getApp();

Page({
  data: {
    submitting: false
  },

  async onSubmit(e) {
    if (this.data.submitting) return;
    const { username, real_name, phone, password } = e.detail.value;
    if (!username || !password || !real_name) {
      wx.showToast({ title: '请填写必填项', icon: 'none' });
      return;
    }
    this.setData({ submitting: true });
    try {
      // 注册
      const res = await request.post('/api/register', {
        username,
        password,
        real_name,
        phone: phone || null,
        email: null
      });

      if (!res.success) throw new Error(res.message || '注册失败');

      // 登录
      const loginRes = await request.post('/api/login', { username, password });
      const token = loginRes.access_token || loginRes.token;
      app.saveLoginInfo(token, {
        username,
        role: loginRes.user?.role || 'inspector'
      });

      wx.showToast({ title: '注册并登录成功', icon: 'success' });
      setTimeout(() => {
        wx.switchTab({ url: '/pages/patrol/list/list' });
      }, 800);
    } catch (err) {
      wx.showToast({ title: err.message || '提交失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  }
});
