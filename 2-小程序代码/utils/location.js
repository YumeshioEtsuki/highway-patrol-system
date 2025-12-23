// utils/location.js - 定位工具
/**
 * 获取当前位置
 */
function getLocation() {
  return new Promise((resolve, reject) => {
    wx.getLocation({
      type: 'gcj02', // 返回国测局坐标
      success: (res) => {
        resolve({
          latitude: res.latitude,
          longitude: res.longitude,
          address: `纬度:${res.latitude.toFixed(6)}, 经度:${res.longitude.toFixed(6)}`
        });
      },
      fail: (err) => {
        console.error('获取位置失败:', err);
        wx.showModal({
          title: '定位失败',
          content: '请在设置中开启位置权限',
          confirmText: '去设置',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting();
            }
          }
        });
        reject(err);
      }
    });
  });
}

/**
 * 选择位置（打开地图选点）
 */
function chooseLocation() {
  return new Promise((resolve, reject) => {
    wx.chooseLocation({
      success: (res) => {
        resolve({
          latitude: res.latitude,
          longitude: res.longitude,
          address: res.address || res.name
        });
      },
      fail: reject
    });
  });
}

/**
 * 打开地图查看位置
 */
function openLocation(latitude, longitude, name = '巡查位置') {
  wx.openLocation({
    latitude,
    longitude,
    name,
    scale: 15
  });
}

module.exports = {
  getLocation,
  chooseLocation,
  openLocation
};
