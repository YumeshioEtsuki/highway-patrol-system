"""
测试 AI 分析功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from workers.ai.tasks import check_photo_quality, analyze_patrol_record

def test_analyze_record():
    """测试分析巡查记录"""
    print("=" * 50)
    print("测试 AI 分析巡查记录")
    print("=" * 50)
    
    # 使用一个存在的记录 ID（从数据库中选择）
    record_id = 1  # 可以修改为实际存在的记录ID
    analysis_type = "comprehensive"
    
    print(f"\n正在分析记录 ID: {record_id}, 类型: {analysis_type}")
    
    try:
        result = analyze_patrol_record(record_id, analysis_type)
        print("\n分析结果:")
        print(f"  成功: {result.get('success')}")
        if result.get('success'):
            print(f"  风险等级: {result.get('risk_level')}")
            print(f"  问题数量: {result.get('issues_count')}")
            if result.get('analysis'):
                print(f"  分析内容: {result['analysis'][:200]}...")
            if result.get('recommendations'):
                print(f"  建议:")
                for rec in result['recommendations'][:3]:
                    print(f"    - {rec}")
        else:
            print(f"  错误: {result.get('error')}")
    except Exception as e:
        print(f"  异常: {e}")

def test_check_quality():
    """测试照片质量检查"""
    print("\n" + "=" * 50)
    print("测试 AI 照片质量检查")
    print("=" * 50)
    
    # 使用一个测试图片路径
    photo_path = "photos/test_photo.jpg"  # 可以修改为实际存在的照片路径
    
    print(f"\n正在检查照片: {photo_path}")
    
    if not os.path.exists(photo_path):
        print(f"  警告: 照片不存在，跳过此测试")
        print(f"  请创建测试照片或修改 photo_path 变量")
        return
    
    try:
        result = check_photo_quality(photo_path)
        print("\n质量检查结果:")
        print(f"  成功: {result.get('success')}")
        if result.get('success'):
            print(f"  质量评分: {result.get('quality_score')}/10")
            print(f"  是否清晰: {result.get('is_clear')}")
            if result.get('issues'):
                print(f"  发现问题:")
                for issue in result['issues']:
                    print(f"    - {issue}")
            if result.get('suggestions'):
                print(f"  改进建议: {result['suggestions'][:200]}...")
        else:
            print(f"  错误: {result.get('error')}")
    except Exception as e:
        print(f"  异常: {e}")

if __name__ == "__main__":
    print("\n开始 AI 功能测试...\n")
    
    # 测试分析巡查记录（不需要 Ollama）
    test_analyze_record()
    
    # 测试照片质量检查（需要 Ollama）
    # test_check_quality()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
