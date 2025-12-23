// pages/admin/list/list.js
const request = require('../../../utils/request');
const util = require('../../../utils/util');
const app = getApp();

Page({
  data: {
    recordList: [],
    pendingCount: 0,
    processingCount: 0,
    completedCount: 0,
    filterStatus: 'pending',
    loading: false
  },

  onLoad() {},

  onShow() {
    this.loadRecords();
    this.loadStats();
  },

  onPullDownRefresh() {
    this.loadRecords().then(() => wx.stopPullDownRefresh());
    this.loadStats();
  },

  async loadRecords() {
    this.setData({ loading: true });
    try {
      const params = this.data.filterStatus ? { status_filter: this.data.filterStatus } : {};
      const res = await request.get('/api/admin/patrol/list', params);
      
      const records = (res.records || []).map(item => ({
        ...item,
        problemTypeText: util.getProblemTypeName(item.problem_type),
        statusText: util.getStatusInfo(item.status).name,
        statusColor: util.getStatusInfo(item.status).color,
        timeText: util.relativeTime(item.patrol_time),
        thumbnail: item.photos?.[0] ? `${app.globalData.baseUrl}${item.photos[0].photo_url}` : null
      }));

      this.setData({ recordList: records, loading: false });
    } catch (err) {
      console.error('加载失败:', err);
      this.setData({ loading: false });
    }
  },

  async loadStats() {
    try {
      const res = await request.get('/api/admin/stats', {}, { showLoading: false });
      this.setData({
        pendingCount: res.pending || 0,
        processingCount: res.processing || 0,
        completedCount: res.completed || 0
      });
    } catch (err) {
      console.error('统计加载失败:', err);
    }
  },

  onFilterChange(e) {
    this.setData({ filterStatus: e.currentTarget.dataset.status });
    this.loadRecords();
  },

  goToDetail(e) {
    wx.navigateTo({
      url: `/pages/admin/detail/detail?id=${e.currentTarget.dataset.id}`
    });
  }
})
