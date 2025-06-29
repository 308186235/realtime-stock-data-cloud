import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append('.')
from backend.strategies.rising_obstacle_detector import RisingObstacleDetector
from backend.strategies.rising_obstacle_strategy import RisingObstacleStrategy

def generate_sample_data(days=120):
    """
    生成包含下降受阻形态的样本数据
    
    Args:
        days (int): 数据天数
        
    Returns:
        pd.DataFrame: 样本数据
        dict: 关键点信息
    """
    print("生成样本数据...")
    
    # 创建日期范围
    date_range = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # 初始化随机价格走势
    np.random.seed(42)  # 确保可重复性
    close = 100 + np.random.randn(days).cumsum()
    
    # 创建各种场景的关键点
    key_points = {}
    
    # 1. 创建强下降受阻形态（历史支撑+缩量+锤子线）
    strong_idx = 40
    
    # 创建下跌趋势
    for i in range(20, strong_idx):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.012))
    
    # 在支撑位附近企稳（接近历史低点）
    close[strong_idx] = close[strong_idx-1] * 0.97
    
    # 受阻后的反弹
    for i in range(strong_idx + 1, strong_idx + 5):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
    
    key_points['strong_obstacle'] = strong_idx
    
    # 2. 创建中等下降受阻形态（均线支撑+十字星）
    medium_idx = 70
    
    # 创建下跌趋势
    for i in range(50, medium_idx):
        close[i] = close[i-1] * (1 - np.random.uniform(0.003, 0.008))
    
    # 在支撑位附近企稳
    close[medium_idx] = close[medium_idx-1] * 0.99
    
    # 受阻后的震荡
    for i in range(medium_idx + 1, medium_idx + 5):
        if i % 2 == 0:
            close[i] = close[i-1] * (1 + np.random.uniform(0.002, 0.008))
        else:
            close[i] = close[i-1] * (1 - np.random.uniform(0.001, 0.004))
    
    key_points['medium_obstacle'] = medium_idx
    
    # 3. 创建假支撑形态（短暂受阻后继续下跌）
    false_idx = 90
    
    # 创建下跌趋势
    for i in range(80, false_idx):
        close[i] = close[i-1] * (1 - np.random.uniform(0.004, 0.01))
    
    # 短暂企稳
    close[false_idx] = close[false_idx-1] * 0.98
    close[false_idx+1] = close[false_idx] * 1.01  # 小幅反弹
    
    # 继续下跌
    for i in range(false_idx + 2, false_idx + 6):
        close[i] = close[i-1] * (1 - np.random.uniform(0.006, 0.015))
    
    key_points['false_support'] = false_idx
    
    # 生成OHLC数据
    high = np.zeros(days)
    low = np.zeros(days)
    open_prices = np.zeros(days)
    
    # 一般K线
    for i in range(days):
        if i not in [strong_idx, medium_idx, false_idx]:
            daily_range = close[i] * np.random.uniform(0.01, 0.03)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/4, daily_range/4)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 强下降受阻形态 - 锤子线
    open_prices[strong_idx] = close[strong_idx-1] * 0.98  # 低开
    high[strong_idx] = max(open_prices[strong_idx], close[strong_idx]) * 1.01  # 小上影线
    low[strong_idx] = min(open_prices[strong_idx], close[strong_idx]) * 0.92  # 长下影线
    
    # 中等下降受阻形态 - 十字星
    open_prices[medium_idx] = close[medium_idx-1] * 0.995  # 略低开
    high[medium_idx] = open_prices[medium_idx] * 1.01  # 小上影线
    low[medium_idx] = open_prices[medium_idx] * 0.98  # 小下影线
    close[medium_idx] = open_prices[medium_idx] * 1.002  # 接近平开平收
    
    # 假支撑形态 - 无明显特征的小阴线
    open_prices[false_idx] = close[false_idx-1] * 0.99  # 低开
    high[false_idx] = open_prices[false_idx] * 1.01  # 小上影线
    low[false_idx] = close[false_idx] * 0.99  # 小下影线
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=days)
    
    # 强形态缩量
    volume[strong_idx-3:strong_idx] = volume[strong_idx-4] * 1.4  # 下跌放量
    volume[strong_idx] = volume[strong_idx-1] * 0.6  # 支撑位缩量
    
    # 中等形态量能变化不明显
    volume[medium_idx] = volume[medium_idx-1] * 0.9  # 轻微缩量
    
    # 假支撑形态不缩量
    volume[false_idx] = volume[false_idx-1] * 1.1  # 略微放量
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    df.set_index('date', inplace=True)
    
    print(f"样本数据生成完成，共 {len(df)} 个交易日")
    return df, key_points

def test_with_real_data():
    """
    使用真实数据进行测试（如果有）
    """
    try:
        # 尝试读取真实数据
        df = pd.read_csv('sample_stock_data.csv', index_col='date', parse_dates=True)
        print(f"使用真实数据测试，共 {len(df)} 个交易日")
        return df, None
    except:
        print("未找到真实数据，使用生成的样本数据")
        return None, None

def visualize_results(df, signals, pattern_details, key_points=None):
    """
    可视化检测结果
    
    Args:
        df (pd.DataFrame): 价格数据
        signals (pd.Series): 检测信号
        pattern_details (dict): 形态详情
        key_points (dict): 关键点信息
    """
    # 1. 绘制总体图表
    detector = RisingObstacleDetector()
    detector.visualize_pattern(df, signals, pattern_details, "下降受阻形态检测结果")
    
    # 2. 如果有关键点，为每种场景绘制单独的细节图
    if key_points:
        for scenario, point in key_points.items():
            # 获取场景窗口
            start_idx = max(0, point - 10)
            end_idx = min(len(df), point + 10)
            
            scenario_window = df.iloc[start_idx:end_idx]
            scenario_signals = signals.iloc[start_idx:end_idx]
            
            # 过滤形态详情
            scenario_details = {date: details for date, details in pattern_details.items()
                               if date in scenario_window.index}
            
            # 创建子图
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # 绘制K线图
            for i in range(len(scenario_window)):
                date = scenario_window.index[i]
                op, hi, lo, cl = scenario_window.iloc[i][['open', 'high', 'low', 'close']]
                
                # K线颜色
                color = 'red' if cl >= op else 'green'
                
                # K线实体
                ax1.plot([date, date], [op, cl], color=color, linewidth=3)
                
                # 上下影线
                ax1.plot([date, date], [lo, min(op, cl)], color=color, linewidth=1)
                ax1.plot([date, date], [max(op, cl), hi], color=color, linewidth=1)
            
            # 绘制均线
            if 'ma5' in scenario_window.columns:
                ax1.plot(scenario_window.index, scenario_window['ma5'], label='MA5', color='blue')
            if 'ma20' in scenario_window.columns:
                ax1.plot(scenario_window.index, scenario_window['ma20'], label='MA20', color='purple')
            
            # 标注关键K线
            if scenario == 'strong_obstacle':
                scenario_title = "强下降受阻形态（历史支撑+缩量+锤子线）"
            elif scenario == 'medium_obstacle':
                scenario_title = "中等下降受阻形态（均线支撑+十字星）"
            elif scenario == 'false_support':
                scenario_title = "假支撑形态（短暂受阻后继续下跌）"
            
            # 找到关键日期
            key_date = df.index[point]
            
            if key_date in scenario_window.index:
                # 标注关键K线
                ax1.plot(key_date, scenario_window.loc[key_date, 'low'], 'ro', markersize=8)
                
                # 标注形态
                ax1.annotate('下降受阻信号',
                           xy=(key_date, scenario_window.loc[key_date, 'low']),
                           xytext=(-30, -30),
                           textcoords='offset points',
                           color='black',
                           fontsize=10,
                           arrowprops=dict(arrowstyle='->', color='black'))
            
            # 绘制成交量
            ax2.bar(scenario_window.index, scenario_window['volume'], color='skyblue', alpha=0.7)
            
            # 标注成交量特征
            if scenario == 'strong_obstacle':
                ax2.annotate('缩量',
                           xy=(key_date, scenario_window.loc[key_date, 'volume']),
                           xytext=(0, 10),
                           textcoords='offset points',
                           color='red',
                           fontsize=8)
            
            # 设置标题和标签
            ax1.set_title(scenario_title)
            ax1.set_ylabel('价格')
            ax2.set_ylabel('成交量')
            
            # 添加形态特征说明
            details_text = ""
            if key_date in pattern_details:
                strength = pattern_details[key_date]['strength']
                features = pattern_details[key_date]['features']
                
                details_text = f"信号强度: {strength:.2f}\n"
                if 'support' in features:
                    details_text += f"支撑类型: {features['support']}\n"
                if 'signals' in features:
                    details_text += f"信号类型: {', '.join(features['signals'])}\n"
                if 'action' in pattern_details[key_date]:
                    details_text += f"建议: {pattern_details[key_date]['action']}"
            
            if details_text:
                ax1.text(0.02, 0.02, details_text,
                        transform=ax1.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", alpha=0.8),
                        fontsize=8)
            
            plt.tight_layout()
            plt.savefig(f'rising_obstacle_{scenario}.png')
            print(f"已生成 {scenario} 场景图表")
    
    return True

def calculate_ma(df):
    """计算常用均线"""
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    return df

def main():
    """主函数"""
    print("下降受阻形态检测测试")
    print("=" * 50)
    
    # 尝试使用真实数据
    real_data, _ = test_with_real_data()
    
    if real_data is not None:
        df = real_data
    else:
        # 生成样本数据
        df, key_points = generate_sample_data(days=120)
    
    # 计算均线
    df = calculate_ma(df)
    
    # 创建检测器
    detector = RisingObstacleDetector()
    
    # 检测形态
    signals, pattern_details = detector.detect_rising_obstacle(df)
    
    # 创建策略
    strategy = RisingObstacleStrategy()
    strategy_signals = strategy.generate_signals(df)
    
    # 打印检测结果
    if len(pattern_details) > 0:
        print(f"\n检测到 {len(pattern_details)} 个下降受阻形态:")
        for date, details in pattern_details.items():
            strength = details['strength']
            strength_text = "强" if strength >= 0.8 else "中" if strength >= 0.5 else "弱"
            print(f"\n日期: {date}")
            print(f"信号强度: {strength:.2f} ({strength_text})")
            if 'action' in details:
                print(f"行动建议: {details['action']}")
            if 'support_info' in details:
                support = details['support_info']
                print(f"支撑位: {support['price']:.2f} ({support['type']})")
            print("形态特征:")
            if 'features' in details:
                for key, value in details['features'].items():
                    if key not in ['overall_strength', 'support_score', 'signal_score', 'trend_score', 'confirm_score']:
                        print(f"  - {key}: {value}")
    else:
        print("\n未检测到下降受阻形态")
    
    # 比较检测器和策略的结果
    if (signals != 0).sum() != (strategy_signals != 0).sum():
        print("\n检测器和策略结果不一致:")
        print(f"检测器信号数量: {(signals != 0).sum()}")
        print(f"策略信号数量: {(strategy_signals != 0).sum()}")
        
        # 打印差异
        diff = (signals != strategy_signals)
        if diff.any():
            for date in diff[diff].index:
                print(f"差异日期: {date}, 检测器信号: {signals[date]}, 策略信号: {strategy_signals[date]}")
    
    # 生成交易决策示例
    if (strategy_signals != 0).any():
        # 以20%的仓位为例
        decision = strategy.generate_trading_decisions(df, current_position=0.2)
        print("\n交易决策示例 (假设当前仓位20%):")
        for key, value in decision.items():
            if key not in ['date', 'signal']:
                print(f"{key}: {value}")
    
    # 可视化结果
    visualize_results(df, signals, pattern_details, 
                    key_points if real_data is None else None)
    
    print("\n测试完成!")
    
if __name__ == "__main__":
    main() 