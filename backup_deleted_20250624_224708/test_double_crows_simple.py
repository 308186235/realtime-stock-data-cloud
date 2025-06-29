import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# Add the parent directory to path
sys.path.append('.')

# Import the detector and strategy classes directly
from backend.strategies.double_black_crows_detector import DoubleBlackCrowsDetector
from backend.strategies.double_black_crows_strategy import DoubleBlackCrowsStrategy

def generate_sample_data(days=120):
    """
    生成包含双飞乌鸦形态的样本数据
    
    Args:
        days (int): 数据天数
        
    Returns:
        pd.DataFrame: 样本数据
    """
    print("生成样本数据...")
    
    # 创建日期范围
    date_range = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # 初始化随机价格走势
    np.random.seed(42)
    close = 100 + np.random.randn(days).cumsum()
    
    # 创建上涨趋势
    for i in range(30, 70):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.015))
    
    # 在高位创建典型的双飞乌鸦形态
    crow_idx1 = 70
    crow_idx2 = 71
    
    # 确保形态前处于高位
    for i in range(65, crow_idx1):
        close[i] = close[i-1] * (1 + np.random.uniform(0.008, 0.015))
    
    # 第一根K线 - 阴线或带上影线的小阳线
    close[crow_idx1] = close[crow_idx1-1] * 0.99
    
    # 第二根K线 - 高开低走的阴线
    close[crow_idx2] = close[crow_idx1] * 0.97
    
    # 形态后的下跌确认
    for i in range(crow_idx2 + 1, crow_idx2 + 5):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.015))
    
    # 生成OHLC数据
    high = np.zeros(days)
    low = np.zeros(days)
    open_prices = np.zeros(days)
    
    # 一般K线
    for i in range(days):
        if i not in [crow_idx1, crow_idx2]:
            daily_range = close[i] * np.random.uniform(0.01, 0.03)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/4, daily_range/4)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 双飞乌鸦形态
    # 第一根K线 - 带长上影线的阴线
    open_prices[crow_idx1] = close[crow_idx1-1] * 1.02  # 高开
    high[crow_idx1] = open_prices[crow_idx1] * 1.03     # 长上影线
    low[crow_idx1] = min(open_prices[crow_idx1], close[crow_idx1]) * 0.99
    
    # 第二根K线 - 高开低走的明显阴线
    open_prices[crow_idx2] = close[crow_idx1] * 1.01   # 高开
    high[crow_idx2] = open_prices[crow_idx2] * 1.015   # 上影线
    low[crow_idx2] = close[crow_idx2] * 0.99          # 下影线
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=days)
    volume[crow_idx1] = volume[crow_idx1-1] * 1.3    # 第一根K线放量
    volume[crow_idx2] = volume[crow_idx1] * 1.5      # 第二根K线明显放量
    
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
    
    # 计算简单的均线，用于检测
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    print(f"样本数据生成完成，共 {len(df)} 个交易日")
    return df

def main():
    """主函数"""
    print("双飞乌鸦形态检测测试")
    print("=" * 50)
    
    # 生成样本数据
    df = generate_sample_data(days=120)
    
    try:
        # 创建检测器
        print("创建双飞乌鸦检测器...")
        detector = DoubleBlackCrowsDetector()
        
        # 检测形态
        print("检测双飞乌鸦形态...")
        signals, pattern_details = detector.detect_double_crows(df)
        
        # 创建策略
        print("创建双飞乌鸦策略...")
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
                
                # 显示特征详情
                print("形态特征:")
                for key, value in details['features'].items():
                    if key not in ['overall_strength', 'position_score', 'candle_score', 'volume_score', 'indicator_score']:
                        print(f"  - {key}: {value}")
        else:
            print("\n未检测到双飞乌鸦形态")
        
        # 生成交易决策示例
        if (strategy_signals != 0).any():
            # 以60%的仓位为例
            decision = strategy.generate_trading_decisions(df, current_position=0.6)
            print("\n交易决策示例 (假设当前仓位60%):")
            for key, value in decision.items():
                if key not in ['date', 'signal']:
                    print(f"{key}: {value}")
        
        # 可视化结果
        print("\n生成可视化分析图...")
        detector.visualize_pattern(df, signals, pattern_details, "双飞乌鸦形态分析")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 