// pages/patrol/detail/detail.js
const request = require('../../../utils/request');
const util = require('../../../utils/util');
const location = require('../../../utils/location');
const app = getApp();

Page({
  data: {
    id: null,
    record: {},
    photos: [],
    problemTypeText: '',
    statusText: '',
    statusColor: '',
    patrolTime: '',
    loading: true
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id });
      this.loadDetail();
    }
  },

  async loadDetail() {
    try {
      wx.showLoading({ title: '加载中...' });
      
      const res = await request.get(`/api/patrol/${this.data.id}`);
      
      // 后端可能返回 record 或直接返回数据
      const record = res.record || res;

      // 处理照片 - 支持多种格式
      let photos = [];
      if (record.photos && Array.isArray(record.photos)) {
        photos = record.photos.map(photo => {
          const url = photo.photo_url || photo.file_path || photo;
          return url.startsWith('http') ? url : `${app.globalData.baseUrl}${url}`;
        });
      }

      // 状态映射
      const statusMap = {
        pending: { text: '待处理', color: '#ef4444' },
        processing: { text: '处理中', color: '#f59e0b' },
        completed: { text: '已完成', color: '#10b981' },
        resolved: { text: '已解决', color: '#10b981' }
      };
      const statusInfo = statusMap[record.status] || statusMap.pending;

      // 问题类型映射
      const typeMap = {
        road_damage: '路面破损',
        guardrail: '护栏损坏',
        sign: '标志缺失',
        drainage: '排水问题',
        other: '其他问题'
      };
      const problemType = record.problem_type || record.issue_type || 'other';

      this.setData({
        record,
        photos,
        problemTypeText: typeMap[problemType] || '未知类型',
        statusText: statusInfo.text,
        statusColor: statusInfo.color,
        patrolTime: record.upload_time || record.patrol_time || record.created_at || '',
        loading: false
      });

      wx.hideLoading();
    } catch (err) {
      console.error('加载详情失败:', err);
      wx.hideLoading();
      wx.showToast({
        title: err.message || '加载失败',
        icon: 'none'
      });
      this.setData({ loading: false });
    }
  },

  openMap() {
    if (!this.data.record.latitude || !this.data.record.longitude) {
      wx.showToast({ title: '无GPS信息', icon: 'none' });
      return;
    }
    
    wx.openLocation({
      latitude: parseFloat(this.data.record.latitude),
      longitude: parseFloat(this.data.record.longitude),
      name: this.data.record.location_desc || '巡查位置',
      scale: 15
    });
  },

  previewPhoto(e) {
    const index = e.currentTarget.dataset.index;
    wx.previewImage({
      urls: this.data.photos,
      current: this.data.photos[index]
    });
  },

  goBack() {
    wx.navigateBack();
  }
})
