// pages/admin/detail/detail.js
const request = require('../../../utils/request');
const util = require('../../../utils/util');
const app = getApp();

Page({
  data: {
    id: null,
    record: {},
    photos: [],
    remark: '',
    problemTypeText: '',
    statusText: '',
    statusColor: '',
    loading: true,
    submitting: false
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
        loading: false
      });

      wx.hideLoading();
    } catch (err) {
      console.error('加载失败:', err);
      wx.hideLoading();
      wx.showToast({ title: err.message || '加载失败', icon: 'none' });
      this.setData({ loading: false });
    }
  },

  onRemarkInput(e) {
    this.setData({ remark: e.detail.value });
  },

  async updateStatus(newStatus) {
    const remarkText = this.data.remark.trim();
    
    if (!remarkText) {
      wx.showToast({ title: '请填写处理备注', icon: 'none' });
      return;
    }

    if (this.data.submitting) return;

    try {
      this.setData({ submitting: true });
      wx.showLoading({ title: '处理中...' });

      // 根据状态选择不同的API端点
      const endpoint = newStatus === 'processing' 
        ? `/api/admin/patrol/${this.data.id}/process`
        : `/api/admin/patrol/${this.data.id}/complete`;

      await request.post(endpoint, {
        remark: remarkText
      });

      wx.hideLoading();
      wx.showToast({ title: '处理成功', icon: 'success' });
      
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (err) {
      console.error('处理失败:', err);
      wx.hideLoading();
      wx.showToast({ title: err.message || '处理失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  handleProcessing() {
    this.updateStatus('processing');
  },

  handleComplete() {
    this.updateStatus('completed');
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
