// utils/request.js - API 请求封装
const app = getApp();

/**
 * 统一请求方法
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data = {}, header = {}, showLoading = true } = options;

    // 显示加载提示
    if (showLoading) {
      wx.showLoading({
        title: '加载中...',
        mask: true
      });
    }

    // 构建完整URL
    const fullUrl = url.startsWith('http') ? url : `${app.globalData.baseUrl}${url}`;

    // 添加token
    const token = app.globalData.token;
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: fullUrl,
      method,
      data,
      header: {
        'content-type': 'application/json',
        ...header
      },
      success: (res) => {
        wx.hideLoading();
        
        // 根据后端返回格式处理
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // token过期或未登录
          wx.showToast({
            title: '请先登录',
            icon: 'none'
          });
          setTimeout(() => {
            app.logout();
          }, 1500);
          reject(res);
        } else {
          wx.showToast({
            title: res.data.message || '请求失败',
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('请求失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

/**
 * GET 请求
 */
function get(url, data = {}, options = {}) {
  return request({
    url,
    method: 'GET',
    data,
    ...options
  });
}

/**
 * POST 请求
 */
function post(url, data = {}, options = {}) {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  });
}

/**
 * PUT 请求
 */
function put(url, data = {}, options = {}) {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  });
}

/**
 * DELETE 请求
 */
function del(url, data = {}, options = {}) {
  return request({
    url,
    method: 'DELETE',
    data,
    ...options
  });
}

/**
 * 上传文件
 */
function uploadFile(filePath, options = {}) {
  return new Promise((resolve, reject) => {
    const { url = '/api/photo/upload', name = 'file', formData = {} } = options;

    wx.showLoading({
      title: '上传中...',
      mask: true
    });

    const token = app.globalData.token;
    const header = {};
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.uploadFile({
      url: `${app.globalData.baseUrl}${url}`,
      filePath,
      name,
      formData,
      header,
      success: (res) => {
        wx.hideLoading();
        const data = JSON.parse(res.data);
        if (res.statusCode === 200) {
          resolve(data);
        } else {
          wx.showToast({
            title: data.message || '上传失败',
            icon: 'none'
          });
          reject(data);
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传失败:', err);
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

/**
 * 上传巡查记录（带照片）
 * 使用FormData方式提交
 */
function uploadPatrolRecord(data, photos = []) {
  return new Promise(async (resolve, reject) => {
    wx.showLoading({
      title: '提交中...',
      mask: true
    });

    try {
      const token = app.globalData.token;
      const header = {};
      if (token) {
        header['Authorization'] = `Bearer ${token}`;
      }

      // 如果有照片，使用wx.uploadFile
      if (photos.length > 0) {
        // 上传第一张照片并附带所有数据
        const formData = {
          segment_id: data.segment_id,
          issue_type_id: data.issue_type_id,
          description: data.description,
          severity: data.severity,
          latitude: data.latitude,
          longitude: data.longitude
        };

        wx.uploadFile({
          url: `${app.globalData.baseUrl}/api/patrol`,
          filePath: photos[0],
          name: 'photo',
          formData,
          header,
          success: async (res) => {
            const result = JSON.parse(res.data);
            if (res.statusCode === 200) {
              // 如果有多张照片，继续上传剩余照片
              if (photos.length > 1 && result.record_id) {
                try {
                  for (let i = 1; i < photos.length; i++) {
                    await uploadFile(photos[i], {
                      url: '/api/photo',
                      formData: { record_id: result.record_id }
                    });
                  }
                } catch (err) {
                  console.warn('部分照片上传失败:', err);
                }
              }
              wx.hideLoading();
              resolve(result);
            } else {
              wx.hideLoading();
              wx.showToast({
                title: result.message || '提交失败',
                icon: 'none'
              });
              reject(result);
            }
          },
          fail: (err) => {
            wx.hideLoading();
            console.error('提交失败:', err);
            wx.showToast({
              title: '提交失败',
              icon: 'none'
            });
            reject(err);
          }
        });
      } else {
        // 没有照片，直接POST
        wx.request({
          url: `${app.globalData.baseUrl}/api/patrol`,
          method: 'POST',
          data,
          header: {
            'content-type': 'application/x-www-form-urlencoded',
            ...header
          },
          success: (res) => {
            wx.hideLoading();
            if (res.statusCode === 200) {
              resolve(res.data);
            } else {
              wx.showToast({
                title: res.data.message || '提交失败',
                icon: 'none'
              });
              reject(res.data);
            }
          },
          fail: (err) => {
            wx.hideLoading();
            wx.showToast({
              title: '提交失败',
              icon: 'none'
            });
            reject(err);
          }
        });
      }
    } catch (err) {
      wx.hideLoading();
      reject(err);
    }
  });
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  uploadFile,
  uploadPatrolRecord
};
