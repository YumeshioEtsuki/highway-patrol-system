"""下载真实的世界地图GeoJSON数据"""
import urllib.request
import json

print("正在下载世界地图数据...")

# 尝试多个CDN源
sources = [
    "https://geo.datav.aliyun.com/areas_v3/bound/world.json",
    "https://unpkg.com/world-atlas@2/countries-110m.json",
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
]

for i, url in enumerate(sources, 1):
    try:
        print(f"\n尝试源 {i}: {url}")
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            geo_data = json.loads(data)
            
            # 保存到本地
            output_path = "D:/MySQL Project/highway-patrol-system/1-后端代码/assets/world.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geo_data, f, ensure_ascii=False)
            
            print(f"✅ 下载成功！")
            print(f"文件大小: {len(data)} 字节")
            print(f"保存位置: {output_path}")
            
            # 显示一些信息
            if 'features' in geo_data:
                print(f"包含 {len(geo_data['features'])} 个地理实体")
            
            break
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        if i < len(sources):
            print("尝试下一个源...")
        else:
            print("\n所有源都失败了，请检查网络连接")
