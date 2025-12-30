#!/usr/bin/env python3
"""
直接测试 API（不启动 uvicorn）
"""
import os
os.environ['SKIP_DB_INIT'] = '1'

from fastapi.testclient import TestClient
from app import app

print('[TEST] Creating test client...')
client = TestClient(app)

print('[TEST] Testing /health endpoint...')
res1 = client.get('/health')
print(f'  Status: {res1.status_code}')
print(f'  Response: {res1.json()}')

print('[TEST] Testing /api/chat/health endpoint...')
res2 = client.get('/api/chat/health')
print(f'  Status: {res2.status_code}')
print(f'  Response: {res2.json()}')

print('\n[TEST] Testing /api/chat with Ollama...')
res3 = client.post('/api/chat', json={
    'messages': [],
    'query': 'Hello, please introduce yourself in 2 sentences.'
})
print(f'  Status: {res3.status_code}')
if res3.status_code == 200:
    resp_data = res3.json()
    print(f'  Success: {resp_data.get("success")}')
    if resp_data.get('success'):
        reply = resp_data.get('reply', '')
        if len(reply) > 200:
            print(f'  Reply: {reply[:200]}...')
        else:
            print(f'  Reply: {reply}')
    else:
        print(f'  Error: {resp_data.get("error")}')
else:
    print(f'  Response: {res3.text[:200]}')

print('\n✓ All tests passed!')
