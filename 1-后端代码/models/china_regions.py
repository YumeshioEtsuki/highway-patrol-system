# -*- coding: utf-8 -*-
"""
中国省份/直辖市GPS边界数据
包含34个省级行政区的经纬度范围及主要城市坐标
"""

CHINA_PROVINCES_GPS = {
    "北京市": {
        "lat_range": [39.4, 41.6],  # [lat_min, lat_max]
        "lon_range": [115.7, 117.4],  # [lon_min, lon_max]
        "cities": {
            "北京": [39.9, 116.4]
        }
    },
    "天津市": {
        "lat_range": [38.3, 39.9],
        "lon_range": [116.7, 118.4],
        "cities": {
            "天津": [39.0, 117.2]
        }
    },
    "河北省": {
        "lat_range": [36.0, 42.6],
        "lon_range": [113.5, 119.9],
        "cities": {
            "石家庄": [37.9, 114.6],
            "唐山": [39.6, 118.0],
            "邯郸": [36.6, 114.5]
        }
    },
    "山西省": {
        "lat_range": [32.2, 40.4],
        "lon_range": [110.2, 114.3],
        "cities": {
            "太原": [37.9, 112.5],
            "大同": [40.1, 113.3],
            "长治": [36.2, 113.1]
        }
    },
    "内蒙古自治区": {
        "lat_range": [37.2, 53.4],
        "lon_range": [97.0, 126.0],
        "cities": {
            "呼和浩特": [40.8, 111.7],
            "包头": [40.7, 109.8],
            "赤峰": [42.3, 118.9]
        }
    },
    "辽宁省": {
        "lat_range": [40.1, 45.9],
        "lon_range": [121.0, 125.9],
        "cities": {
            "沈阳": [41.8, 123.4],
            "大连": [38.9, 121.6],
            "鞍山": [41.1, 122.9]
        }
    },
    "吉林省": {
        "lat_range": [42.2, 46.9],
        "lon_range": [121.7, 131.3],
        "cities": {
            "长春": [43.8, 125.3],
            "吉林": [43.0, 126.6],
            "四平": [43.2, 124.4]
        }
    },
    "黑龙江省": {
        "lat_range": [43.5, 53.6],
        "lon_range": [121.1, 135.1],
        "cities": {
            "哈尔滨": [45.8, 126.5],
            "齐齐哈尔": [47.3, 123.9],
            "佳木斯": [46.6, 130.4]
        }
    },
    "上海市": {
        "lat_range": [30.7, 31.9],
        "lon_range": [120.8, 122.2],
        "cities": {
            "上海": [31.2, 121.5]
        }
    },
    "江苏省": {
        "lat_range": [30.8, 35.1],
        "lon_range": [118.4, 121.9],
        "cities": {
            "南京": [32.1, 118.8],
            "苏州": [31.3, 120.6],
            "无锡": [31.6, 120.3]
        }
    },
    "浙江省": {
        "lat_range": [27.2, 34.7],
        "lon_range": [118.2, 123.3],
        "cities": {
            "杭州": [30.3, 120.2],
            "宁波": [29.9, 121.6],
            "温州": [28.0, 120.6]
        }
    },
    "安徽省": {
        "lat_range": [29.6, 34.9],
        "lon_range": [114.2, 119.7],
        "cities": {
            "合肥": [31.9, 117.2],
            "阜阳": [32.9, 115.8],
            "芜湖": [31.3, 118.4]
        }
    },
    "福建省": {
        "lat_range": [23.5, 28.4],
        "lon_range": [116.0, 120.8],
        "cities": {
            "福州": [26.1, 119.3],
            "厦门": [24.4, 118.1],
            "泉州": [24.9, 118.6]
        }
    },
    "江西省": {
        "lat_range": [24.4, 30.3],
        "lon_range": [113.9, 118.5],
        "cities": {
            "南昌": [28.7, 115.9],
            "九江": [29.7, 116.0],
            "赣州": [25.9, 115.2]
        }
    },
    "山东省": {
        "lat_range": [34.2, 38.3],
        "lon_range": [114.7, 122.4],
        "cities": {
            "济南": [36.7, 117.1],
            "青岛": [36.1, 120.3],
            "烟台": [37.5, 121.4]
        }
    },
    "河南省": {
        "lat_range": [32.1, 36.4],
        "lon_range": [112.9, 116.7],
        "cities": {
            "郑州": [34.7, 113.6],
            "开封": [34.3, 114.3],
            "洛阳": [34.6, 112.4]
        }
    },
    "湖北省": {
        "lat_range": [29.0, 33.7],
        "lon_range": [108.7, 116.1],
        "cities": {
            "武汉": [30.6, 114.3],
            "黄石": [30.2, 115.0],
            "十堰": [32.6, 110.8]
        }
    },
    "湖南省": {
        "lat_range": [24.7, 30.1],
        "lon_range": [108.8, 114.3],
        "cities": {
            "长沙": [28.2, 113.0],
            "株洲": [27.8, 113.1],
            "湘潭": [27.8, 112.9]
        }
    },
    "广东省": {
        "lat_range": [20.1, 25.1],
        "lon_range": [109.6, 117.0],
        "cities": {
            "广州": [23.1, 113.3],
            "深圳": [22.5, 114.1],
            "佛山": [23.0, 113.1]
        }
    },
    "广西壮族自治区": {
        "lat_range": [20.9, 26.4],
        "lon_range": [104.5, 112.0],
        "cities": {
            "南宁": [22.8, 108.3],
            "柳州": [24.3, 109.4],
            "桂林": [25.3, 110.3]
        }
    },
    "海南省": {
        "lat_range": [18.3, 20.6],
        "lon_range": [108.6, 111.0],
        "cities": {
            "海口": [19.0, 110.2],
            "三亚": [18.3, 109.3]
        }
    },
    "重庆市": {
        "lat_range": [28.2, 32.3],
        "lon_range": [105.4, 110.2],
        "cities": {
            "重庆": [29.4, 106.5]
        }
    },
    "四川省": {
        "lat_range": [24.0, 34.3],
        "lon_range": [97.2, 108.6],
        "cities": {
            "成都": [30.6, 104.1],
            "绵阳": [31.7, 104.7],
            "南充": [30.8, 106.1]
        }
    },
    "贵州省": {
        "lat_range": [24.6, 29.3],
        "lon_range": [103.6, 109.6],
        "cities": {
            "贵阳": [26.6, 106.7],
            "遵义": [27.7, 106.9],
            "毕节": [27.3, 105.3]
        }
    },
    "云南省": {
        "lat_range": [21.1, 29.2],
        "lon_range": [97.2, 106.1],
        "cities": {
            "昆明": [25.0, 102.7],
            "曲靖": [25.5, 103.8],
            "玉溪": [24.3, 102.5]
        }
    },
    "西藏自治区": {
        "lat_range": [26.9, 36.5],
        "lon_range": [78.2, 99.1],
        "cities": {
            "拉萨": [29.6, 91.1],
            "日喀则": [28.8, 88.8]
        }
    },
    "陕西省": {
        "lat_range": [31.8, 39.3],
        "lon_range": [105.4, 111.2],
        "cities": {
            "西安": [34.3, 108.9],
            "咸阳": [34.3, 108.7],
            "渭南": [34.4, 109.5]
        }
    },
    "甘肃省": {
        "lat_range": [32.6, 42.6],
        "lon_range": [92.1, 108.5],
        "cities": {
            "兰州": [36.1, 103.8],
            "天水": [34.6, 105.7],
            "武威": [37.9, 102.6]
        }
    },
    "青海省": {
        "lat_range": [31.4, 39.2],
        "lon_range": [89.0, 104.1],
        "cities": {
            "西宁": [36.6, 101.8],
            "海东": [36.5, 102.0]
        }
    },
    "宁夏回族自治区": {
        "lat_range": [35.1, 39.2],
        "lon_range": [104.2, 107.4],
        "cities": {
            "银川": [38.5, 106.3],
            "石嘴山": [39.0, 106.4]
        }
    },
    "新疆维吾尔自治区": {
        "lat_range": [34.2, 48.1],
        "lon_range": [73.4, 96.4],
        "cities": {
            "乌鲁木齐": [43.8, 87.6],
            "克拉玛依": [45.6, 84.9],
            "吐鲁番": [42.9, 89.2]
        }
    },
    "台湾省": {
        "lat_range": [21.9, 25.3],
        "lon_range": [120.1, 121.9],
        "cities": {
            "台北": [25.0, 121.5],
            "高雄": [22.6, 120.3]
        }
    },
    "香港特别行政区": {
        "lat_range": [22.1, 22.6],
        "lon_range": [113.8, 114.4],
        "cities": {
            "香港": [22.3, 114.2]
        }
    },
    "澳门特别行政区": {
        "lat_range": [22.1, 22.2],
        "lon_range": [113.5, 113.6],
        "cities": {
            "澳门": [22.16, 113.55]
        }
    }
}


def get_province_gps_bounds(province_name: str):
    """获取省份的GPS边界范围
    
    Args:
        province_name: 省份名称（如"浙江省"、"北京市"）
    
    Returns:
        {lat_min, lat_max, lon_min, lon_max} 或 None
    """
    if province_name in CHINA_PROVINCES_GPS:
        data = CHINA_PROVINCES_GPS[province_name]
        return {
            "lat_min": data["lat_range"][0],
            "lat_max": data["lat_range"][1],
            "lon_min": data["lon_range"][0],
            "lon_max": data["lon_range"][1]
        }
    return None


def get_city_gps_bounds(province_name: str, city_name: str, expand_km: float = 100.0):
    """获取城市的GPS边界范围（以城市中心为圆心，设定半径）
    
    Args:
        province_name: 省份名称
        city_name: 城市名称
        expand_km: 从城市中心向外扩展的公里数（1度约111km，默认100km）
    
    Returns:
        {lat_min, lat_max, lon_min, lon_max} 或 None
    """
    if province_name not in CHINA_PROVINCES_GPS:
        return None
    
    cities = CHINA_PROVINCES_GPS[province_name].get("cities", {})
    if city_name not in cities:
        return None
    
    lat_center, lon_center = cities[city_name]
    # 每度约111公里
    degrees_expand = expand_km / 111.0
    
    return {
        "lat_min": lat_center - degrees_expand,
        "lat_max": lat_center + degrees_expand,
        "lon_min": lon_center - degrees_expand,
        "lon_max": lon_center + degrees_expand
    }


def get_all_provinces():
    """获取所有省份名称列表"""
    return list(CHINA_PROVINCES_GPS.keys())


def get_province_cities(province_name: str):
    """获取某省份的所有城市列表"""
    if province_name in CHINA_PROVINCES_GPS:
        return list(CHINA_PROVINCES_GPS[province_name].get("cities", {}).keys())
    return []
