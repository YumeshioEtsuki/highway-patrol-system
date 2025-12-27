#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端修复清单 - 需要手动应用到 HTML 文件
"""

FRONTEND_FIXES = {
    "patrol.html": [
        {
            "issue": "Token 过期检查缺失",
            "fix": """
            // 在所有 fetch 之前添加：
            function ensureTokenValid() {
                const token = localStorage.getItem('access_token');
                const expires = localStorage.getItem('token_expires');
                if (!token || !expires || Date.now() > parseInt(expires)) {
                    alert('登录已过期，请重新登录');
                    logout();
                    return false;
                }
                return true;
            }
            
            // 登录时保存过期时间（例如 1 小时）：
            const expiresIn = 3600000; // 1 hour
            localStorage.setItem('token_expires', Date.now() + expiresIn);
            """
        },
        {
            "issue": "API 错误处理不完整",
            "fix": """
            // 统一的 API 调用函数：
            async function apiCall(method, endpoint, data = null) {
                if (!ensureTokenValid()) return null;
                
                const token = localStorage.getItem('access_token');
                const options = {
                    method: method,
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                };
                
                if (data) options.body = JSON.stringify(data);
                
                try {
                    const res = await fetch(`/api${endpoint}`, options);
                    
                    if (res.status === 401) {
                        alert('认证失败，请重新登录');
                        logout();
                        return null;
                    }
                    
                    if (!res.ok) {
                        const error = await res.json();
                        throw new Error(error.detail || '请求失败');
                    }
                    
                    return await res.json();
                } catch (e) {
                    alert(`错误: ${e.message}`);
                    console.error(e);
                    return null;
                }
            }
            """
        },
        {
            "issue": "表单验证缺失",
            "fix": """
            // 在 handleLogin() 前添加验证：
            function validateLogin(username, password) {
                if (!username || !password) {
                    alert('用户名和密码不能为空');
                    return false;
                }
                if (username.length < 3) {
                    alert('用户名至少 3 个字符');
                    return false;
                }
                if (password.length < 6) {
                    alert('密码至少 6 个字符');
                    return false;
                }
                return true;
            }
            """
        }
    ],
    "admin.html": [
        {
            "issue": "操作按钮在加载时没有禁用",
            "fix": """
            // 添加加载状态管理：
            let isLoading = false;
            
            function setButtonsDisabled(disabled) {
                document.querySelectorAll('.btn-verify, .btn-status, .btn-reinit, .btn-enter').forEach(btn => {
                    btn.disabled = disabled;
                    btn.style.opacity = disabled ? '0.5' : '1';
                    btn.style.cursor = disabled ? 'not-allowed' : 'pointer';
                });
            }
            
            // 在每个操作的开始和结束时调用：
            setButtonsDisabled(true);
            try {
                // 操作代码
            } finally {
                setButtonsDisabled(false);
            }
            """
        },
        {
            "issue": "SSE 连接失败没有提示",
            "fix": """
            // 改进 SSE 错误处理：
            photoSource.onerror = (event) => {
                console.error('SSE 连接错误:', event);
                const container = document.getElementById('live-photos');
                const error = document.createElement('div');
                error.style.color = 'red';
                error.textContent = '⚠️ 实时推送已断开，请刷新页面';
                container.appendChild(error);
                
                // 尝试重连
                setTimeout(() => {
                    console.log('正在重连...');
                    startPhotoStream();
                }, 3000);
            };
            """
        }
    ]
}

print("\n前端修复任务列表:\n")
for filename, fixes in FRONTEND_FIXES.items():
    print(f"\n📄 {filename}")
    for i, fix_item in enumerate(fixes, 1):
        print(f"  [{i}] ⚠️ {fix_item['issue']}")
        print(f"      补丁: {fix_item['fix'][:100]}...")
