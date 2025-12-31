"""
测试自适应权重系统
演示权重如何根据历史数据自动调整
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from lib import get_adaptive_weights_info

def print_separator():
    print("\n" + "="*80 + "\n")

def main():
    print("🧠 自适应权重系统测试")
    print_separator()
    
    # 获取当前权重信息
    info = get_adaptive_weights_info()
    
    print(f"📊 当前模式: {info['weight_mode']}")
    print(f"   说明: {info['description']}")
    print_separator()
    
    print("🎯 当前权重分配:")
    weights = info['current_weights']
    print(f"   用户反馈:   {weights['feedback']*100:.1f}%")
    print(f"   稳定性:     {weights['stability']*100:.1f}%")
    print(f"   生成一致性: {weights['consistency']*100:.1f}%")
    print(f"   应用频率:   {weights['frequency']*100:.1f}%")
    print_separator()
    
    print("📈 全局统计:")
    stats = info['global_stats']
    print(f"   总缓存项数: {stats['total_samples']}")
    print(f"   已应用数:   {stats['total_applied']}")
    print(f"   平均稳定性: {stats['avg_stability']*100:.1f}%")
    print(f"   平均反馈:   {stats['avg_feedback']*100:.1f}%")
    print(f"   高稳定性比例: {stats['high_stability_ratio']*100:.1f}%")
    print(f"   高反馈比例:   {stats['high_feedback_ratio']*100:.1f}%")
    print_separator()
    
    print("💡 权重调整逻辑:")
    print("   • 样本数 >20 且高稳定性比例 >70% → 稳定性权重增至 50%")
    print("   • 样本数 >20 且高反馈比例 >70% → 反馈权重增至 40%")
    print("   • 样本数 <10 → 降低频率权重避免过拟合")
    print("   • 默认权重: 反馈30% + 稳定性40% + 一致性20% + 频率10%")
    print_separator()
    
    print("✨ 规则增强:")
    print("   • 应用10次且0次修改 → 奖励 +15%")
    print("   • 连续3次点赞且0踩 → 奖励 +10%")
    print("   • 三高组合(反馈/稳定/一致性均>80%) → 奖励 +10%")
    print("   • 修改率 >50% → 惩罚 -20%")
    print_separator()
    
    print("🎓 系统状态评估:")
    if stats['total_applied'] < 10:
        print("   ⚠️  数据量较少，系统正在学习中...")
        print("   📝 建议: 继续使用推荐功能，积累更多数据")
    elif stats['total_applied'] < 20:
        print("   ✅ 数据量适中，系统使用默认权重")
        print("   📝 建议: 再积累一些数据后，系统将自动优化权重")
    else:
        if info['weight_mode'] == 'high_stability':
            print("   🎯 系统检测到高稳定性趋势，已自动增加稳定性权重")
            print("   💪 这说明推荐的准确性很高！")
        elif info['weight_mode'] == 'high_feedback':
            print("   👍 系统检测到高质量用户反馈，已自动增加反馈权重")
            print("   💪 用户参与度很高！")
        else:
            print("   ✅ 数据充足，系统运行正常")
    
    print("\n")

if __name__ == "__main__":
    main()
