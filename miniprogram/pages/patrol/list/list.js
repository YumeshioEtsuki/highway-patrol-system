// pages/patrol/list/list.js
const request = require('../../../utils/request');
const util = require('../../../utils/util');
const auth = require('../../../utils/auth');
const app = getApp();

Page({
  data: {
    recordList: [],
    totalCount: 0,
    pendingCount: 0,
    completedCount: 0,
    filterStatus: '',
    loading: false,
    page: 1,
    pageSize: 20,
    hasMore: true
  },

  onLoad() {
    this.checkAuth();
  },

  onShow() {
    // 每次显示页面时刷新数据
    if (auth.isLogin()) {
      this.loadRecords();
      this.loadStats();
    }
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true });
    this.loadRecords().then(() => {
      wx.stopPullDownRefresh();
    });
    this.loadStats();
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    if (this.data.loading || !this.data.hasMore) return;
    
    this.setData({ page: this.data.page + 1 });
    this.loadRecords(true);
  },

  /**
   * 检查登录状态
   */
  async checkAuth() {
    try {
      await auth.checkAuth();
      this.loadRecords();
      this.loadStats();
    } catch (err) {
      // checkAuth会自动跳转到登录页
    }
  },

  /**
   * 加载记录列表
   */
  async loadRecords() {
    this.setData({ loading: true });
    try {
      const params = {};
      if (this.data.filterStatus) {
        params.status = this.data.filterStatus;
      }
      console.log('[请求参数]', params);
      const res = await request.get('/api/patrol', params);
      console.log('[响应数据]', res);
      // 处理数据
      const records = (res.records || []).map(item => ({
        ...item,
        problemTypeText: util.getProblemTypeName(item.problem_type),
        statusText: util.getStatusInfo(item.status).name,
        statusColor: util.getStatusInfo(item.status).color,
        timeText: util.relativeTime(item.patrol_time),
        thumbnail: item.photos && item.photos.length > 0 ? 
          `${app.globalData.baseUrl}${item.photos[0].photo_url}` : null,
        photoCount: item.photos ? item.photos.length : 0
      }));
      this.setData({
        recordList: records,
        loading: false
      });
    } catch (err) {
      console.error('加载记录失败:', err);
      wx.showToast({ title: '加载记录失败', icon: 'none' });
      wx.setStorageSync('lastError', { type: 'loadRecords', error: err, time: Date.now() });
      this.setData({ loading: false });
    }
  },

  /**
   * 加载统计数据
   */
  async loadStats() {
    try {
      const userId = app.globalData.userInfo?.user_id || app.globalData.userInfo?.userId;
      if (!userId || !app.globalData.token) return;
      console.log('[统计请求]', { user_id: userId });
      const res = await request.get('/api/stats', { user_id: userId }, { showLoading: false });
      console.log('[统计响应]', res);
      this.setData({
        totalCount: res.total_records || 0,
        pendingCount: res.pending_count || 0,
        completedCount: res.completed_count || 0
      });
    } catch (err) {
      console.error('加载统计失败:', err);
      wx.showToast({ title: '加载统计失败', icon: 'none' });
      wx.setStorageSync('lastError', { type: 'loadStats', error: err, time: Date.now() });
    }
  },

  /**
   * 筛选状态改变
   */
  onFilterChange(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({
      filterStatus: status,
      page: 1,
      hasMore: true
    });
    this.loadRecords();
  },

  /**
   * 跳转到详情页
   */
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/patrol/detail/detail?id=${id}`
    });
  },

  /**
   * 跳转到创建页
   */
  goToCreate() {
    wx.navigateTo({
      url: '/pages/patrol/create/create'
    });
  }
})
