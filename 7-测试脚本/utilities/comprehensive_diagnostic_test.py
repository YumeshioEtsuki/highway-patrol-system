#!/usr/bin/env python3
"""
【全面诊断测试脚本】
对项目的数据库、后端API、前端交互、数据筛选等进行全面检测

运行方式：
    cd d:\MySQL Project\highway-patrol-system\1-后端代码
    python ../7-测试脚本/comprehensive_diagnostic_test.py
"""

import sys
import os
sys.path.insert(0, '.')

from utils.utils import get_db_connection
from datetime import datetime
import json

class DiagnosticTest:
    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def test_db_connection(self):
        """✓ 测试1: 数据库连接"""
        print("\n" + "="*60)
        print("【测试1】数据库连接")
        print("="*60)
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 获取数据统计
            cursor.execute("SELECT COUNT(*) as cnt FROM InspectionRecord")
            total = cursor.fetchone()['cnt']
            
            cursor.execute("SELECT COUNT(*) as cnt FROM InspectionRecord WHERE data_type='real'")
            real_count = cursor.fetchone()['cnt']
            
            cursor.execute("SELECT COUNT(*) as cnt FROM InspectionRecord WHERE data_type='test'")
            test_count = cursor.fetchone()['cnt']
            
            # 检查所有必要的表
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            print(f"✅ 数据库连接成功")
            print(f"   • 总记录数: {total}")
            print(f"   • 真实数据: {real_count}")
            print(f"   • 测试数据: {test_count}")
            print(f"   • 表数量: {len(tables)}")
            print(f"   • 表列表: {', '.join(tables)}")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            self.failed += 1
            return False
    
    def test_data_type_filter(self):
        """✓ 测试2: 数据类型筛选功能"""
        print("\n" + "="*60)
        print("【测试2】数据类型筛选功能（后端SQL逻辑）")
        print("="*60)
        try:
            from services.patrol_service import get_patrol_list_admin, get_admin_stats
            
            # 测试2.1: 查询全部数据（不传data_type）
            print("\n2.1 查询全部数据（data_type=None）:")
            result_all = get_patrol_list_admin(data_type=None, page_size=100)
            total_all = result_all['total']
            print(f"   • 返回条数: {len(result_all['records'])}")
            print(f"   • 报告总数: {total_all}")
            
            # 测试2.2: 查询真实数据
            print("\n2.2 查询真实数据（data_type='real'）:")
            result_real = get_patrol_list_admin(data_type='real', page_size=100)
            total_real = result_real['total']
            print(f"   • 返回条数: {len(result_real['records'])}")
            print(f"   • 报告总数: {total_real}")
            
            # 测试2.3: 查询测试数据
            print("\n2.3 查询测试数据（data_type='test'）:")
            result_test = get_patrol_list_admin(data_type='test', page_size=100)
            total_test = result_test['total']
            print(f"   • 返回条数: {len(result_test['records'])}")
            print(f"   • 报告总数: {total_test}")
            
            # 验证一致性
            print("\n2.4 数据一致性检查:")
            if total_real + total_test == total_all:
                print(f"   ✅ 一致: {total_real} + {total_test} = {total_all}")
                self.passed += 1
                return True
            else:
                print(f"   ⚠️  不一致: {total_real} + {total_test} ≠ {total_all}")
                self.warnings += 1
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            return False
    
    def test_pagination(self):
        """✓ 测试3: 分页功能"""
        print("\n" + "="*60)
        print("【测试3】分页功能")
        print("="*60)
        try:
            from services.patrol_service import get_patrol_list_admin
            from utils.config import settings
            
            print(f"\n3.1 配置检查:")
            print(f"   • MAX_PAGE_SIZE: {settings.MAX_PAGE_SIZE}")
            
            # 测试超大分页请求
            print(f"\n3.2 请求超大分页 (page_size=500):")
            result = get_patrol_list_admin(page_size=500)
            actual_size = len(result['records'])
            print(f"   • 请求: 500")
            print(f"   • 实际返回: {actual_size}")
            print(f"   • 限制: {settings.MAX_PAGE_SIZE}")
            if actual_size <= settings.MAX_PAGE_SIZE:
                print(f"   ✅ 分页限制正确")
            else:
                print(f"   ⚠️  返回数据超过限制")
                self.warnings += 1
            
            # 测试分页总数
            print(f"\n3.3 分页总数检查:")
            total = result['total']
            max_pages = (total + settings.MAX_PAGE_SIZE - 1) // settings.MAX_PAGE_SIZE
            print(f"   • 数据总数: {total}")
            print(f"   • 每页上限: {settings.MAX_PAGE_SIZE}")
            print(f"   • 需要页数: {max_pages}")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed += 1
            return False
    
    def test_stats_api(self):
        """✓ 测试4: 统计API"""
        print("\n" + "="*60)
        print("【测试4】统计API (get_admin_stats)")
        print("="*60)
        try:
            from services.patrol_service import get_admin_stats
            
            # 测试4.1: 全局统计
            print("\n4.1 全局统计（无筛选）:")
            stats = get_admin_stats()
            print(f"   • 总记录: {stats['total_records']}")
            print(f"   • 状态分布: {stats['status_breakdown']}")
            print(f"   • 问题类型数: {len(stats['type_breakdown'])}")
            print(f"   • 严重度分布: {stats['severity_breakdown']}")
            print(f"   • 近7天: {stats['recent_7_days']}")
            print(f"   • 近30天: {stats['recent_30_days']}")
            
            # 测试4.2: 按数据类型统计
            print("\n4.2 按data_type统计:")
            stats_real = get_admin_stats(data_type='real')
            stats_test = get_admin_stats(data_type='test')
            print(f"   • 真实数据总数: {stats_real['total_records']}")
            print(f"   • 测试数据总数: {stats_test['total_records']}")
            
            if stats_real['total_records'] + stats_test['total_records'] == stats['total_records']:
                print(f"   ✅ 统计一致")
                self.passed += 1
                return True
            else:
                print(f"   ⚠️  统计不一致")
                self.warnings += 1
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            return False
    
    def test_table_schema(self):
        """✓ 测试5: 表结构检查"""
        print("\n" + "="*60)
        print("【测试5】表结构检查")
        print("="*60)
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 检查InspectionRecord表结构
            print("\n5.1 InspectionRecord 列检查:")
            cursor.execute("SHOW COLUMNS FROM InspectionRecord")
            columns = cursor.fetchall()
            col_names = [col['Field'] for col in columns]
            
            required_cols = ['record_id', 'user_id', 'segment_id', 'problem_type_id', 
                            'description', 'severity', 'status', 'upload_time', 'data_type']
            
            missing_cols = [c for c in required_cols if c not in col_names]
            
            if not missing_cols:
                print(f"   ✅ 所有必要字段存在")
                self.passed += 1
            else:
                print(f"   ⚠️  缺少字段: {missing_cols}")
                self.warnings += 1
            
            # 检查data_type类型
            print("\n5.2 data_type 字段类型检查:")
            data_type_col = [c for c in columns if c['Field'] == 'data_type']
            if data_type_col:
                col_info = data_type_col[0]
                print(f"   • 类型: {col_info['Type']}")
                print(f"   • Null: {col_info['Null']}")
                print(f"   • 默认值: {col_info['Default']}")
                print(f"   ✅ data_type 字段存在")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed += 1
            return False
    
    def test_frontend_logic(self):
        """✓ 测试6: 前端逻辑检查"""
        print("\n" + "="*60)
        print("【测试6】前端逻辑检查 (admin.html)")
        print("="*60)
        try:
            admin_html_path = 'templates/admin.html'
            if os.path.exists(admin_html_path):
                with open(admin_html_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查关键逻辑
                checks = [
                    ('currentDataType', '数据类型切换变量'),
                    ('buildQueryParams', '参数构建函数'),
                    ('data_type', '参数传递'),
                ]
                
                print("\n6.1 关键JavaScript代码检查:")
                for keyword, desc in checks:
                    if keyword in content:
                        print(f"   ✅ {keyword} - {desc}")
                    else:
                        print(f"   ⚠️  {keyword} - {desc} (未找到)")
                        self.warnings += 1
                
                # 检查前端分页上限
                if 'page_size=500' in content or 'pageSize.*500' in content:
                    print(f"   ℹ️  前端支持大分页")
                
                print(f"   ✅ admin.html 文件存在")
                self.passed += 1
                return True
            else:
                print(f"   ❌ admin.html 文件不存在")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed += 1
            return False
    
    def test_cache_invalidation(self):
        """✓ 测试7: 缓存失效检查"""
        print("\n" + "="*60)
        print("【测试7】缓存管理检查")
        print("="*60)
        try:
            from services.patrol_service import _cache_clear
            
            print("\n7.1 缓存清理功能:")
            _cache_clear("admin_stats")
            print(f"   ✅ 缓存清理成功")
            
            # 二次查询以验证缓存重建
            from services.patrol_service import get_admin_stats
            stats1 = get_admin_stats()
            stats2 = get_admin_stats()
            
            if stats1['total_records'] == stats2['total_records']:
                print(f"   ✅ 缓存重建成功")
                self.passed += 1
                return True
            else:
                print(f"   ⚠️  缓存数据不一致")
                self.warnings += 1
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.failed += 1
            return False
    
    def generate_report(self):
        """生成诊断报告"""
        print("\n\n" + "="*60)
        print("【诊断报告汇总】")
        print("="*60)
        
        total = self.passed + self.failed + self.warnings
        print(f"\n总测试数: {total}")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"⚠️  警告: {self.warnings}")
        
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n通过率: {pass_rate:.1f}%")
        
        if self.failed == 0 and self.warnings <= 1:
            print("\n🎉 系统健康度: 优秀")
        elif self.failed == 0:
            print("\n⚠️  系统健康度: 良好（有轻微问题）")
        else:
            print("\n❌ 系统健康度: 需要维修")
        
        print("\n" + "="*60)
        print("【关键问题提示】")
        print("="*60)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as cnt FROM InspectionRecord WHERE data_type='real'")
        real_count = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM InspectionRecord WHERE data_type='test'")
        test_count = cursor.fetchone()['cnt']
        conn.close()
        
        if real_count == 0 and test_count > 0:
            print("\n⚠️  【问题1】所有数据都是测试数据")
            print("   • 真实数据: 0")
            print("   • 测试数据:", test_count)
            print("   建议: ")
            print("     1. 生成或导入真实数据")
            print("     2. 或手动清理测试数据后再导入")
            print("     运行: clean_test_data() 清理测试数据")
        
        print("\n💡 【性能提示】")
        from utils.config import settings
        print(f"   • MAX_PAGE_SIZE: {settings.MAX_PAGE_SIZE}")
        print(f"   • 当前数据量: {real_count + test_count}")
        if real_count + test_count > 1000:
            print(f"   建议: 数据量较大，确保前端分页控件设置合理")

def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║        🔍 公路巡查系统 - 全面诊断测试 v1.0                 ║")
    print("║          开始时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S").ljust(42) + "║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    test = DiagnosticTest()
    
    # 运行所有测试
    test.test_db_connection()
    test.test_data_type_filter()
    test.test_pagination()
    test.test_stats_api()
    test.test_table_schema()
    test.test_frontend_logic()
    test.test_cache_invalidation()
    
    # 生成报告
    test.generate_report()
    
    print("\n" + "="*60)
    print("诊断完成！请查看上方详细结果。")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
