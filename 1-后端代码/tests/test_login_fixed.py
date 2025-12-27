#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

url = 'http://127.0.0.1:5000/api/login'
data = {
    'user': 'admin',
    'password': 'admin'
}

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print(f"响应体: {response.text}")
    if response.status_code == 200:
        print(f"✅ 登录成功!")
        print(f"JSON: {response.json()}")
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")
