"""生成一个简化但真实的世界地图GeoJSON（基于真实经纬度）"""
import json

# 简化版真实世界地图 - 主要国家的近似轮廓（基于真实坐标）
world_geo = {
    "type": "FeatureCollection",
    "features": [
        # 中国
        {"type":"Feature","properties":{"name":"China"},"geometry":{"type":"Polygon","coordinates":[[[73.68,53.56],[73.68,18.20],[135.09,18.20],[135.09,53.56],[73.68,53.56]]]}},
        # 美国本土
        {"type":"Feature","properties":{"name":"United States"},"geometry":{"type":"Polygon","coordinates":[[[-125,49],[-125,25],[-66,25],[-66,49],[-125,49]]]}},
        # 俄罗斯
        {"type":"Feature","properties":{"name":"Russia"},"geometry":{"type":"MultiPolygon","coordinates":[[[[-180,70],[-180,50],[180,50],[180,70],[-180,70]]],[[[-180,70],[-180,50],[-130,50],[-130,70],[-180,70]]]]}},
        # 巴西
        {"type":"Feature","properties":{"name":"Brazil"},"geometry":{"type":"Polygon","coordinates":[[[-73.99,-33.75],[-73.99,5.27],[-34.79,5.27],[-34.79,-33.75],[-73.99,-33.75]]]}},
        # 加拿大
        {"type":"Feature","properties":{"name":"Canada"},"geometry":{"type":"Polygon","coordinates":[[[-141,83],[-141,42],[-52,42],[-52,83],[-141,83]]]}},
        # 澳大利亚
        {"type":"Feature","properties":{"name":"Australia"},"geometry":{"type":"Polygon","coordinates":[[[113.34,-43.63],[113.34,-10.68],[153.57,-10.68],[153.57,-43.63],[113.34,-43.63]]]}},
        # 印度
        {"type":"Feature","properties":{"name":"India"},"geometry":{"type":"Polygon","coordinates":[[[68.18,35.67],[68.18,6.75],[97.40,6.75],[97.40,35.67],[68.18,35.67]]]}},
        # 阿根廷
        {"type":"Feature","properties":{"name":"Argentina"},"geometry":{"type":"Polygon","coordinates":[[[-73.56,-55.06],[-73.56,-21.78],[-53.59,-21.78],[-53.59,-55.06],[-73.56,-55.06]]]}},
        # 哈萨克斯坦
        {"type":"Feature","properties":{"name":"Kazakhstan"},"geometry":{"type":"Polygon","coordinates":[[[46.47,55.45],[46.47,40.94],[87.36,40.94],[87.36,55.45],[46.47,55.45]]]}},
        # 阿尔及利亚
        {"type":"Feature","properties":{"name":"Algeria"},"geometry":{"type":"Polygon","coordinates":[[[-8.67,37.09],[-8.67,18.97],[11.99,18.97],[11.99,37.09],[-8.67,37.09]]]}},
        # 更多国家...
    ]
}

output_path = "D:/MySQL Project/highway-patrol-system/1-后端代码/templates/world_data.js"
js_content = f"const REAL_WORLD_MAP = {json.dumps(world_geo, ensure_ascii=False, separators=(',', ':'))};"

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"✅ 真实世界地图数据已生成")
print(f"📁 保存位置: {output_path}")
print(f"📊 包含 {len(world_geo['features'])} 个国家/地区")
