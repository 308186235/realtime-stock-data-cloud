import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append('.')
from backend.strategies.double_black_crows_detector import DoubleBlackCrowsDetector
from backend.strategies.double_black_crows_strategy import DoubleBlackCrowsStrategy

def generate_sample_data(days=120):
    """
    生成包含双飞乌鸦形态的样本数据
    
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
    
    # 创建典型的上涨趋势
    for i in range(30, 70):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
    
    # 创建各种场景的关键点
    key_points = {}
    
    # 1. 创建强双飞乌鸦形态（高位、放量）
    strong_crow_idx1 = 70
    strong_crow_idx2 = 71
    
    # 确保前期处于高位
    for i in range(65, strong_crow_idx1):
        close[i] = close[i-1] * (1 + np.random.uniform(0.008, 0.015))
    
    # 第一根K线 - 阴线或带上影线的小阳线
    close[strong_crow_idx1] = close[strong_crow_idx1-1] * 0.99
    
    # 第二根K线 - 高开低走的阴线
    close[strong_crow_idx2] = close[strong_crow_idx1] * 0.97
    
    # 形态后的下跌确认
    for i in range(strong_crow_idx2 + 1, strong_crow_idx2 + 5):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.015))
    
    key_points['strong_crows'] = (strong_crow_idx1, strong_crow_idx2)
    
    # 2. 创建弱双飞乌鸦形态（中位置、缩量）
    weak_crow_idx1 = 85
    weak_crow_idx2 = 86
    
    # 中位置上涨
    for i in range(80, weak_crow_idx1):
        close[i] = close[i-1] * (1 + np.random.uniform(0.002, 0.01))
    
    # 第一根K线 - 小阴线
    close[weak_crow_idx1] = close[weak_crow_idx1-1] * 0.995
    
    # 第二根K线 - 高开低走的阴线
    close[weak_crow_idx2] = close[weak_crow_idx1] * 0.985
    
    # 形态后的小幅震荡
    for i in range(weak_crow_idx2 + 1, weak_crow_idx2 + 5):
        close[i] = close[i-1] * (1 + np.random.uniform(-0.01, 0.01))
    
    key_points['weak_crows'] = (weak_crow_idx1, weak_crow_idx2)
    
    # 3. 创建假信号（阳包阴反转）
    false_crow_idx1 = 100
    false_crow_idx2 = 101
    false_crow_idx3 = 102  # 反转K线
    
    # 上涨到高位
    for i in range(95, false_crow_idx1):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.012))
    
    # 双飞乌鸦形态
    close[false_crow_idx1] = close[false_crow_idx1-1] * 0.99
    close[false_crow_idx2] = close[false_crow_idx1] * 0.98
    
    # 阳包阴反转
    close[false_crow_idx3] = close[false_crow_idx1] * 1.02
    
    # 后续上涨
    for i in range(false_crow_idx3 + 1, false_crow_idx3 + 4):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
    
    key_points['false_signal'] = (false_crow_idx1, false_crow_idx2, false_crow_idx3)
    
    # 生成OHLC数据
    high = np.zeros(days)
    low = np.zeros(days)
    open_prices = np.zeros(days)
    
    # 一般K线
    for i in range(days):
        if i not in [strong_crow_idx1, strong_crow_idx2, weak_crow_idx1, weak_crow_idx2, 
                    false_crow_idx1, false_crow_idx2, false_crow_idx3]:
            daily_range = close[i] * np.random.uniform(0.01, 0.03)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/4, daily_range/4)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 强双飞乌鸦形态
    # 第一根K线 - 带长上影线的阴线
    open_prices[strong_crow_idx1] = close[strong_crow_idx1-1] * 1.02  # 高开
    high[strong_crow_idx1] = open_prices[strong_crow_idx1] * 1.03     # 长上影线
    low[strong_crow_idx1] = min(open_prices[strong_crow_idx1], close[strong_crow_idx1]) * 0.99
    
    # 第二根K线 - 高开低走的明显阴线
    open_prices[strong_crow_idx2] = close[strong_crow_idx1] * 1.01   # 高开
    high[strong_crow_idx2] = open_prices[strong_crow_idx2] * 1.015   # 上影线
    low[strong_crow_idx2] = close[strong_crow_idx2] * 0.99          # 下影线
    
    # 弱双飞乌鸦形态
    # 第一根K线 - 小阴线
    open_prices[weak_crow_idx1] = close[weak_crow_idx1-1] * 1.005  # 小幅高开
    high[weak_crow_idx1] = open_prices[weak_crow_idx1] * 1.01      # 小上影线
    low[weak_crow_idx1] = min(open_prices[weak_crow_idx1], close[weak_crow_idx1]) * 0.995
    
    # 第二根K线 - 高开低走的小阴线
    open_prices[weak_crow_idx2] = close[weak_crow_idx1] * 1.005    # 高开
    high[weak_crow_idx2] = open_prices[weak_crow_idx2] * 1.01      # 上影线
    low[weak_crow_idx2] = close[weak_crow_idx2] * 0.995            # 下影线
    
    # 假信号形态
    # 第一根K线 - 阴线
    open_prices[false_crow_idx1] = close[false_crow_idx1-1] * 1.015  # 高开
    high[false_crow_idx1] = open_prices[false_crow_idx1] * 1.02      # 上影线
    low[false_crow_idx1] = min(open_prices[false_crow_idx1], close[false_crow_idx1]) * 0.99
    
    # 第二根K线 - 阴线
    open_prices[false_crow_idx2] = close[false_crow_idx1] * 1.01     # 高开
    high[false_crow_idx2] = open_prices[false_crow_idx2] * 1.015     # 上影线
    low[false_crow_idx2] = close[false_crow_idx2] * 0.99            # 下影线
    
    # 第三根K线 - 阳包阴反转
    open_prices[false_crow_idx3] = close[false_crow_idx2] * 0.99    # 略低开
    high[false_crow_idx3] = open_prices[false_crow_idx3] * 1.04     # 长上影线
    low[false_crow_idx3] = min(open_prices[false_crow_idx3], close[false_crow_idx3]) * 0.995
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=days)
    
    # 强形态放量
    volume[strong_crow_idx1] = volume[strong_crow_idx1-1] * 1.3    # 第一根K线放量
    volume[strong_crow_idx2] = volume[strong_crow_idx1] * 1.5      # 第二根K线明显放量
    
    # 弱形态缩量
    volume[weak_crow_idx1] = volume[weak_crow_idx1-1] * 0.9       # 第一根K线缩量
    volume[weak_crow_idx2] = volume[weak_crow_idx1] * 0.8         # 第二根K线缩量
    
    # 假信号形态
    volume[false_crow_idx1] = volume[false_crow_idx1-1] * 1.2     # 第一根K线放量
    volume[false_crow_idx2] = volume[false_crow_idx1] * 1.3       # 第二根K线放量
    volume[false_crow_idx3] = volume[false_crow_idx2] * 1.8       # 第三根K线大幅放量
    
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
    detector = DoubleBlackCrowsDetector()
    detector.visualize_pattern(df, signals, pattern_details, "双飞乌鸦形态检测结果")
    
    # 2. 如果有关键点，为每种场景绘制单独的细节图
    if key_points:
        for scenario, points in key_points.items():
            # 获取场景窗口
            start_idx = max(0, points[0] - 10)
            end_idx = min(len(df), points[-1] + 10)
            
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
            if 'ma10' in scenario_window.columns:
                ax1.plot(scenario_window.index, scenario_window['ma10'], label='MA10', color='purple')
            
            # 标注关键K线
            if scenario == 'strong_crows':
                crow1_idx, crow2_idx = points
                scenario_title = "强双飞乌鸦形态（高位+放量）"
            elif scenario == 'weak_crows':
                crow1_idx, crow2_idx = points
                scenario_title = "弱双飞乌鸦形态（中位+缩量）"
            elif scenario == 'false_signal':
                crow1_idx, crow2_idx, reverse_idx = points
                scenario_title = "假信号（反转突破）"
                # 标注反转K线
                reverse_date = df.index[reverse_idx]
                if reverse_date in scenario_window.index:
                    ax1.annotate('阳包阴反转',
                                xy=(reverse_date, scenario_window.loc[reverse_date, 'high']),
                                xytext=(0, 20),
                                textcoords='offset points',
                                color='red',
                                arrowprops=dict(arrowstyle='->', color='red'))
            
            crow1_date = df.index[crow1_idx]
            crow2_date = df.index[crow2_idx]
            
            if crow1_date in scenario_window.index and crow2_date in scenario_window.index:
                # 连接两根K线
                ax1.plot([crow1_date, crow2_date],
                         [scenario_window.loc[crow1_date, 'high'], scenario_window.loc[crow2_date, 'high']],
                         'ro-', markersize=6, linewidth=1.5)
                
                # 标注第一根K线
                ax1.annotate('第一根乌鸦',
                            xy=(crow1_date, scenario_window.loc[crow1_date, 'high']),
                            xytext=(-30, 20),
                            textcoords='offset points',
                            color='black',
                            fontsize=8,
                            arrowprops=dict(arrowstyle='->', color='black'))
                
                # 标注第二根K线
                ax1.annotate('第二根乌鸦',
                            xy=(crow2_date, scenario_window.loc[crow2_date, 'high']),
                            xytext=(30, 20),
                            textcoords='offset points',
                            color='black',
                            fontsize=8,
                            arrowprops=dict(arrowstyle='->', color='black'))
            
            # 绘制成交量
            ax2.bar(scenario_window.index, scenario_window['volume'], color='skyblue', alpha=0.7)
            
            # 标注成交量特征
            if scenario == 'strong_crows':
                ax2.annotate('放量',
                           xy=(crow2_date, scenario_window.loc[crow2_date, 'volume']),
                           xytext=(0, 10),
                           textcoords='offset points',
                           color='red',
                           fontsize=8)
            elif scenario == 'weak_crows':
                ax2.annotate('缩量',
                           xy=(crow2_date, scenario_window.loc[crow2_date, 'volume']),
                           xytext=(0, 10),
                           textcoords='offset points',
                           color='blue',
                           fontsize=8)
            
            # 设置标题和标签
            ax1.set_title(scenario_title)
            ax1.set_ylabel('价格')
            ax2.set_ylabel('成交量')
            
            # 添加形态特征说明
            details_text = ""
            for date in [crow2_date]:
                if date in pattern_details:
                    strength = pattern_details[date]['strength']
                    features = pattern_details[date]['features']
                    if 'position' in features:
                        details_text += f"位置: {features['position']}\n"
                    if 'volume' in features:
                        details_text += f"成交量: {features['volume']}\n"
                    if 'arrangement' in features:
                        details_text += f"排列: {features['arrangement']}\n"
                    if 'action' in pattern_details[date]:
                        details_text += f"建议: {pattern_details[date]['action']}"
            
            if details_text:
                ax1.text(0.02, 0.02, details_text,
                        transform=ax1.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", alpha=0.8),
                        fontsize=8)
            
            plt.tight_layout()
            plt.savefig(f'double_black_crows_{scenario}.png')
            print(f"已生成 {scenario} 场景图表")
    
    return True

def main():
    """主函数"""
    print("双飞乌鸦形态检测测试")
    print("=" * 50)
    
    # 尝试使用真实数据
    real_data, _ = test_with_real_data()
    
    if real_data is not None:
        df = real_data
    else:
        # 生成样本数据
        df, key_points = generate_sample_data(days=120)
    
    # 创建检测器
    detector = DoubleBlackCrowsDetector()
    
    # 检测形态
    signals, pattern_details = detector.detect_double_crows(df)
    
    # 创建策略
    strategy = DoubleBlackCrowsStrategy()
    strategy_signals = strategy.generate_signals(df)
    
    # 打印检测结果
    if len(pattern_details) > 0:
        print(f"\n检测到 {len(pattern_details)} 个双飞乌鸦形态:")
        for date, details in pattern_details.items():
            strength = details['strength']
            strength_text = "强" if strength >= 0.8 else "中" if strength >= 0.5 else "弱"
            print(f"\n日期: {date}")
            print(f"信号强度: {strength:.2f} ({strength_text})")
            print(f"行动建议: {details['action']}")
            print("形态特征:")
            for key, value in details['features'].items():
                if key not in ['overall_strength', 'position_score', 'candle_score', 'volume_score', 'indicator_score']:
                    print(f"  - {key}: {value}")
    else:
        print("\n未检测到双飞乌鸦形态")
    
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
        # 以60%的仓位为例
        decision = strategy.generate_trading_decisions(df, current_position=0.6)
        print("\n交易决策示例 (假设当前仓位60%):")
        for key, value in decision.items():
            if key not in ['date', 'signal']:
                print(f"{key}: {value}")
    
    # 可视化结果
    visualize_results(df, signals, pattern_details, 
                    key_points if real_data is None else None)
    
    print("\n测试完成!")
    
if __name__ == "__main__":
    main() 