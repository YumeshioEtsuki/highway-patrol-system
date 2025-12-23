# utils/auth.py
from functools import wraps
from flask import session, jsonify, abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "请先登录"}), 401
        if session.get('role') != 'admin':
            return jsonify({"error": "权限不足：仅管理员可访问"}), 403
        return f(*args, **kwargs)
    return decorated_function