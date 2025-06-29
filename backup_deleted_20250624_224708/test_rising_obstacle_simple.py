import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append('.')

# Import the detector class directly
from backend.strategies.rising_obstacle_detector import RisingObstacleDetector

def generate_sample_data(days=120):
    """
    生成包含下降受阻形态的样本数据
    
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
    
    # 创建下跌趋势
    for i in range(30, 70):
        close[i] = close[i-1] * (1 - np.random.uniform(0.005, 0.01))
    
    # 创建下降受阻形态
    obstacle_idx = 70
    
    # 在支撑位附近企稳
    close[obstacle_idx] = close[obstacle_idx-1] * 0.98
    
    # 受阻后的反弹
    for i in range(obstacle_idx + 1, obstacle_idx + 5):
        close[i] = close[i-1] * (1 + np.random.uniform(0.005, 0.01))
    
    # 生成OHLC数据
    high = np.zeros(days)
    low = np.zeros(days)
    open_prices = np.zeros(days)
    
    # 一般K线
    for i in range(days):
        if i != obstacle_idx:
            daily_range = close[i] * np.random.uniform(0.01, 0.03)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/4, daily_range/4)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 下降受阻K线 - 带长下影线
    open_prices[obstacle_idx] = close[obstacle_idx-1] * 0.99  # 略低开
    high[obstacle_idx] = open_prices[obstacle_idx] * 1.01     # 小幅反弹  
    low[obstacle_idx] = open_prices[obstacle_idx] * 0.94      # 长下影线
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=days)
    volume[obstacle_idx-3:obstacle_idx] = volume[obstacle_idx-4] * 1.3  # 下跌放量
    volume[obstacle_idx] = volume[obstacle_idx-1] * 0.7                # 受阻缩量
    
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
    
    # 计算均线，用于检测
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    print(f"样本数据生成完成，共 {len(df)} 个交易日")
    return df

def main():
    """主函数"""
    print("下降受阻形态检测测试")
    print("=" * 50)
    
    # 生成样本数据
    df = generate_sample_data(days=120)
    
    try:
        # 创建检测器
        print("创建下降受阻检测器...")
        detector = RisingObstacleDetector()
        
        # 检测形态
        print("检测下降受阻形态...")
        signals, pattern_details = detector.detect_rising_obstacle(df)
        
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
                
                # 显示特征详情
                if 'features' in details:
                    print("形态特征:")
                    for key, value in details['features'].items():
                        if key not in ['overall_strength', 'support_score', 'signal_score', 'trend_score', 'confirm_score']:
                            print(f"  - {key}: {value}")
        else:
            print("\n未检测到下降受阻形态")
        
        # 可视化结果
        print("\n生成可视化分析图...")
        detector.visualize_pattern(df, signals, pattern_details, "下降受阻形态分析")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 