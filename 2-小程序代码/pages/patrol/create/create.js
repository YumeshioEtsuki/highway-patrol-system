// pages/patrol/create/create.js
const request = require('../../../utils/request');
const location = require('../../../utils/location');
const auth = require('../../../utils/auth');
const app = getApp();

Page({
  data: {
    formData: {
      location_desc: '',
      problem_desc: '',
      problem_type: 'road_damage',
      severity: 3
    },
    location: null,
    photos: [],
    photoUrls: [], // 上传后的照片URL
    severityLevels: [1, 2, 3, 4, 5], // 严重程度等级
    problemTypes: [
      { label: '路面破损', value: 'road_damage' },
      { label: '护栏损坏', value: 'guardrail' },
      { label: '标志缺失', value: 'sign' },
      { label: '排水问题', value: 'drainage' },
      { label: '其他问题', value: 'other' }
    ],
    problemTypeIndex: 0,
    submitting: false
  },

  onLoad() {
    auth.checkAuth().catch(() => {});
    // 自动获取位置
    this.getLocation();
  },

  /**
   * 获取位置
   */
  async getLocation() {
    try {
      wx.showLoading({ title: '定位中...' });
      const loc = await location.getLocation();
      wx.hideLoading();
      
      this.setData({ location: loc });
      wx.showToast({
        title: '定位成功',
        icon: 'success'
      });
    } catch (err) {
      wx.hideLoading();
      console.error('定位失败:', err);
    }
  },

  /**
   * 问题类型改变
   */
  onProblemTypeChange(e) {
    const index = e.detail.value;
    this.setData({
      problemTypeIndex: index,
      'formData.problem_type': this.data.problemTypes[index].value
    });
  },

  /**
   * 严重程度改变
   */
  onSeverityChange(e) {
    const level = e.currentTarget.dataset.level;
    this.setData({
      'formData.severity': level
    });
  },

  /**
   * 选择照片
   */
  choosePhoto() {
    const maxCount = 9 - this.data.photos.length;
    
    if (maxCount <= 0) {
      wx.showToast({ title: '最多只能上传9张照片', icon: 'none' });
      return;
    }
    
    wx.chooseMedia({
      count: maxCount,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'], // 使用压缩图，节省流量
      maxDuration: 10,
      camera: 'back',
      success: (res) => {
        const tempFiles = res.tempFiles.map(file => file.tempFilePath);
        this.setData({
          photos: [...this.data.photos, ...tempFiles]
        });
        
        wx.showToast({
          title: `已添加${tempFiles.length}张照片`,
          icon: 'success',
          duration: 1500
        });
      },
      fail: (err) => {
        console.error('选择照片失败:', err);
        if (err.errMsg && err.errMsg.includes('cancel')) {
          // 用户取消，不提示
        } else {
          wx.showToast({ title: '选择照片失败', icon: 'none' });
        }
      }
    });
  },

  /**
   * 删除照片
   */
  deletePhoto(e) {
    const index = e.currentTarget.dataset.index;
    const photos = this.data.photos;
    photos.splice(index, 1);
    this.setData({ photos });
  },

  /**
   * 上传照片
   */
  async uploadPhotos() {
    const photos = this.data.photos;
    if (photos.length === 0) return [];

    wx.showLoading({ title: `上传照片 0/${photos.length}` });
    
    const uploadPromises = photos.map((photoPath, index) => {
      return request.uploadFile(photoPath).then(res => {
        // 更新进度
        wx.showLoading({ title: `上传照片 ${index + 1}/${photos.length}` });
        return res;
      });
    });

    try {
      const results = await Promise.all(uploadPromises);
      wx.hideLoading();
      return results.map(res => res.photo_url);
    } catch (err) {
      wx.hideLoading();
      console.error('照片上传失败:', err);
      throw new Error('照片上传失败，请重试');
    }
  },

  /**
   * 表单提交
   */
  async onSubmit(e) {
    if (this.data.submitting) return;

    const formData = e.detail.value;

    // 验证必填项
    if (!this.data.location) {
      wx.showToast({ title: '请先获取位置', icon: 'none' });
      return;
    }

    if (!formData.location_desc.trim()) {
      wx.showToast({ title: '请填写位置描述', icon: 'none' });
      return;
    }

    if (!formData.problem_desc.trim()) {
      wx.showToast({ title: '请填写问题描述', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    try {
      // 构建FormData数据（匹配后端接口）
      const submitData = {
        segment_id: 1,  // 固定路段ID，实际应该让用户选择
        issue_type_id: this.getProblemTypeId(this.data.formData.problem_type),
        description: `${formData.location_desc.trim()} - ${formData.problem_desc.trim()}`,
        severity: this.data.formData.severity,
        latitude: this.data.location.latitude,
        longitude: this.data.location.longitude
      };

      // 使用FormData方式提交（带照片）
      await request.uploadPatrolRecord(submitData, this.data.photos);

      wx.showToast({
        title: '提交成功',
        icon: 'success'
      });

      setTimeout(() => {
        wx.navigateBack();
      }, 1500);

    } catch (err) {
      console.error('提交失败:', err);
      this.setData({ submitting: false });
      wx.showToast({
        title: err.message || '提交失败',
        icon: 'none'
      });
    }
  },

  /**
   * 获取问题类型ID
   */
  getProblemTypeId(problemType) {
    const mapping = {
      'road_damage': 1,
      'guardrail': 2,
      'sign': 3,
      'drainage': 4,
      'other': 5
    };
    return mapping[problemType] || 1;
  },

  /**
   * 取消
   */
  onCancel() {
    wx.showModal({
      title: '确认取消',
      content: '当前填写的内容将不会保存',
      success: (res) => {
        if (res.confirm) {
          wx.navigateBack();
        }
      }
    });
  }
})
