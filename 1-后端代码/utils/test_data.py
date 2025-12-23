# utils/test_data.py

# 延迟导入，避免在模块加载时执行密码哈希
def get_hashed_password(plain_password):
    """获取哈希后的密码（延迟执行）"""
    from .algorithm import hash_password
    return hash_password(plain_password)

# 使用函数引用而不是直接哈希
def get_test_data():
    """获取测试数据（密码会在调用时哈希）"""
    PASSWORD = get_hashed_password("REDACTED")
    password = get_hashed_password("mimashi123")
    
    return {
    "Department": [
        {"department_name": "公路养护中心"},
        {"department_name": "桥梁管理处"}
    ],
    "RoadSegment": [
        {"segment_name": "G1京哈高速-北京段", "start_number": 0, "end_number": 50, "department_id": 1, "region": "华北"},
        {"segment_name": "G2京沪高速-天津段", "start_number": 0, "end_number": 120, "department_id": 1, "region": "华北"},
        {"segment_name": "G3京台高速-河北段", "start_number": 0, "end_number": 80, "department_id": 1, "region": "华北"},
        {"segment_name": "G20青银高速-山西段", "start_number": 200, "end_number": 350, "department_id": 1, "region": "华北"},
        {"segment_name": "S1京承高速-北京段", "start_number": 0, "end_number": 40, "department_id": 1, "region": "华北"},
        
        {"segment_name": "G15沈海高速-山东段", "start_number": 300, "end_number": 450, "department_id": 1, "region": "华东"},
        {"segment_name": "G40沪陕高速-安徽段", "start_number": 500, "end_number": 680, "department_id": 1, "region": "华东"},
        {"segment_name": "S2机场高速-上海段", "start_number": 0, "end_number": 25, "department_id": 1, "region": "华东"},
        
        {"segment_name": "G4京港澳高速-湖北段", "start_number": 800, "end_number": 950, "department_id": 2, "region": "华中"},
        {"segment_name": "G5京昆高速-河南段", "start_number": 600, "end_number": 750, "department_id": 2, "region": "华中"},
        {"segment_name": "G50沪渝高速-湖南段", "start_number": 400, "end_number": 580, "department_id": 2, "region": "华中"},
        
        {"segment_name": "G55二广高速-广东段", "start_number": 1200, "end_number": 1400, "department_id": 2, "region": "华南"},
        {"segment_name": "G75兰海高速-广西段", "start_number": 1500, "end_number": 1700, "department_id": 2, "region": "华南"},
        
        {"segment_name": "G6京藏高速-陕西段", "start_number": 900, "end_number": 1100, "department_id": 1, "region": "西北"},
        {"segment_name": "G7京新高速-新疆段", "start_number": 2000, "end_number": 2300, "department_id": 1, "region": "西北"},
        {"segment_name": "G30连霍高速-甘肃段", "start_number": 1800, "end_number": 2000, "department_id": 1, "region": "西北"},
        
        {"segment_name": "G60沪昆高速-贵州段", "start_number": 1300, "end_number": 1500, "department_id": 2, "region": "西南"},
        {"segment_name": "G65包茂高速-重庆段", "start_number": 1100, "end_number": 1300, "department_id": 2, "region": "西南"},
        {"segment_name": "G85渝昆高速-云南段", "start_number": 1600, "end_number": 1850, "department_id": 2, "region": "西南"},
        {"segment_name": "G318国道-四川段", "start_number": 0, "end_number": 200, "department_id": 2, "region": "西南"},
        {"segment_name": "G318国道-西藏段", "start_number": 200, "end_number": 500, "department_id": 2, "region": "西南"}
    ],
    "User": [
        {
            "username": "admin",
            "password": PASSWORD,
            "real_name": "系统管理员",
            "phone": "11451419198",
            "email": "admin@example.com",
            "role": "admin",
            "department_id": 1
        },
        {
            "username": "inspector",
            "password": password,
            "real_name": "张三",
            "phone": "13900139000",
            "role": "inspector",
            "department_id": 2
        }
    ],
    "ProblemType": [
        {"type_name": "🛣️ 路面破损（裂缝/坑洼）", "parent_id": None},
        {"type_name": "🚧 护栏损坏（缺失/变形）", "parent_id": None},
        {"type_name": "🪧 标志标线（缺失/模糊）", "parent_id": None},
        {"type_name": "💧 排水问题（积水/堵塞）", "parent_id": None},
        {"type_name": "🌳 路域环境（杂草/垃圾）", "parent_id": None},
        {"type_name": "🌉 桥梁隧道（裂缝/渗漏）", "parent_id": None},
        {"type_name": "🚥 交通设施（信号灯/监控）", "parent_id": None},
        {"type_name": "💡 照明系统（路灯损坏）", "parent_id": None},
        {"type_name": "⛰️ 边坡塌方（落石/滑坡）", "parent_id": None},
        {"type_name": "🚗 交通事故（车辆故障）", "parent_id": None},
        {"type_name": "🚚 违规占道（违停/摆摊）", "parent_id": None},
        {"type_name": "❄️ 冰雪灾害（结冰/积雪）", "parent_id": None},
        {"type_name": "🌀 自然灾害（水毁/风灾）", "parent_id": None},
        {"type_name": "🏗️ 施工隐患（材料/围挡）", "parent_id": None},
        {"type_name": "📋 其他问题", "parent_id": None}
    ],
    "InspectionRecord": [
        # 已移除默认测试记录，用户可通过前端表单提交新记录
    ],
    "Photo": [
        # 已移除默认测试照片
    ]
}

# 为了向后兼容，提供一个全局变量（但建议使用 get_test_data()）
TEST_DATA = None  # 需要时调用 get_test_data()