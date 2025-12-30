#!/usr/bin/env python3
"""
测试SSE照片推送的稳定性
监控连接状态并记录断线情况
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={'username': 'admin', 'password': 'MIMASHI123'}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✓ 登录成功")
        return token
    return None

def test_sse_connection(token, duration=60):
    """测试SSE连接稳定性"""
    url = f"{BASE_URL}/api/sse/patrol-photo?token={token}"
    
    print(f"\n开始监控SSE连接（持续 {duration} 秒）...")
    print(f"连接URL: {url}")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 60)
    
    start_time = time.time()
    event_count = 0
    heartbeat_count = 0
    error_count = 0
    last_event_time = start_time
    
    try:
        import sseclient  # 需要安装: pip install sseclient-py
        response = requests.get(url, stream=True, timeout=None)
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed > duration:
                print(f"\n⏱ 测试时间到（{duration}秒），停止监控")
                break
            
            if event.data:
                try:
                    data = json.loads(event.data)
                    if data.get('event') == 'new_photo':
                        event_count += 1
                        photo_info = data.get('data', {})
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📸 收到照片事件 #{event_count}: "
                              f"record_id={photo_info.get('record_id')}, "
                              f"photo_id={photo_info.get('photo_id')}")
                        last_event_time = current_time
                except json.JSONDecodeError:
                    # 可能是心跳包
                    if 'heartbeat' in event.data or 'ping' in event.data:
                        heartbeat_count += 1
                        gap = current_time - last_event_time
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💓 心跳 #{heartbeat_count} "
                              f"(距上次事件 {gap:.1f}s)")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 其他事件: {event.data[:50]}")
            
            # 检测是否长时间没有事件（可能断线）
            if current_time - last_event_time > 10:
                print(f"⚠️  警告：{current_time - last_event_time:.1f}秒内无任何事件（可能断线）")
                
    except requests.exceptions.RequestException as e:
        error_count += 1
        print(f"\n❌ 连接错误: {e}")
    except KeyboardInterrupt:
        print(f"\n⏸ 用户中断测试")
    except Exception as e:
        error_count += 1
        print(f"\n❌ 未知错误: {e}")
    finally:
        end_time = time.time()
        total_duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 测试统计")
        print("=" * 60)
        print(f"总时长: {total_duration:.1f}秒")
        print(f"照片事件: {event_count} 个")
        print(f"心跳包: {heartbeat_count} 个")
        print(f"错误次数: {error_count} 次")
        
        if error_count == 0 and total_duration >= duration * 0.9:
            print("\n✅ 连接稳定！")
        elif error_count > 0:
            print(f"\n⚠️  连接不稳定（{error_count} 次错误）")
        else:
            print(f"\n⚠️  测试未完成（仅运行了 {total_duration:.1f}秒）")

def main():
    print("=" * 60)
    print("🧪 SSE照片推送稳定性测试")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ 登录失败，无法测试")
        return
    
    print("\n💡 提示：")
    print("1. 此测试会监控SSE连接60秒")
    print("2. 在另一个窗口生成带照片的测试数据，观察推送情况")
    print("3. 按 Ctrl+C 可提前停止测试")
    print()
    
    input("按回车键开始测试...")
    
    try:
        test_sse_connection(token, duration=60)
    except ImportError:
        print("\n⚠️  缺少依赖: sseclient-py")
        print("请运行: pip install sseclient-py")

if __name__ == "__main__":
    main()
