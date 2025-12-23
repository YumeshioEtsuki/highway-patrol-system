import urllib.request
import json
import os

# 创建static文件夹
static_dir = r"d:\MySQL Project\highway-patrol-system\1-后端代码\static"
os.makedirs(static_dir, exist_ok=True)
print(f"✓ Created directory: {static_dir}")

# 下载真实的世界地图GeoJSON
urls = [
    "https://raw.githubusercontent.com/apache/echarts/master/test/data/map/json/world.json",
    "https://code.highcharts.com/mapdata/custom/world.geo.json",
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"
]

output_file = os.path.join(static_dir, "world.json")

for url in urls:
    try:
        print(f"\nTrying to download from: {url}")
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            
            # 验证是否为有效的JSON
            try:
                json_data = json.loads(data)
                print(f"✓ Successfully downloaded {len(data)} bytes")
                print(f"✓ Valid JSON with {len(json_data)} keys")
                
                # 保存到文件
                with open(output_file, 'wb') as f:
                    f.write(data)
                
                print(f"✓ Saved to: {output_file}")
                print(f"✓ File size: {os.path.getsize(output_file)} bytes")
                break
                
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON: {e}")
                continue
                
    except Exception as e:
        print(f"✗ Failed: {e}")
        continue
else:
    print("\n✗ All download attempts failed")
