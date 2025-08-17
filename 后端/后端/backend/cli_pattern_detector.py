#!/usr/bin/env python3
"""
命令行K线形态检测工具
用法: python cli_pattern_detector.py --pattern double_green_parallel --stock 000001 --days 60
或者: python cli_pattern_detector.py --pattern three_black_crows --stock 000001 --days 60
"""

import argparse
import pandas as pd
import numpy as np
import sys
import os
import json
from datetime import datetime, timedelta
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import get_strategy, list_available_strategies
from strategies.double_green_parallel_strategy import DoubleGreenParallelStrategy
from strategies.three_black_crows_strategy import ThreeBlackCrowsStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_stock_data(stock_code, days=60):
    """加载股票数据(这里使用模拟数据)"""
    logger.info(f"加载股票 {stock_code} 的最近 {days} 天数据")
    
    # 在实际应用中,这里应该从数据库或API获取真实数据
    # 现在使用模拟数据
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    # 创建日期范围
    date_range = pd.date_range(start=start_date, end=today, freq='B')
    
    # 创建模拟数据
    np.random.seed(42)  # 固定随机种子以便复现
    
    data = {
        'date': date_range,
        'open': np.random.normal(10, 1, len(date_range)) * (1 + np.arange(len(date_range)) * 0.001),
        'high': None,
        'low': None,
        'close': None,
        'volume': np.random.randint(1000000, 5000000, len(date_range))
    }
    
    # 设置high, low, close
    data['close'] = data['open'] * np.random.normal(1, 0.02, len(date_range))
    data['high'] = np.maximum(data['open'], data['close']) * np.random.normal(1.01, 0.005, len(date_range))
    data['low'] = np.minimum(data['open'], data['close']) * np.random.normal(0.99, 0.005, len(date_range))
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    return df

def inject_pattern(df, pattern_type='double_green_parallel', position='random'):
    """注入特定K线形态到数据中"""
    logger.info(f"在{'随机' if position=='random' else position}位置注入{pattern_type}形态")
    
    if pattern_type == 'double_green_parallel':
        # 在数据中随机选择一个位置注入双绿并行形态
        if position == 'random':
            pos = np.random.randint(5, len(df) - 3)
        elif position == 'high':
            pos = len(df) - 3  # 高位
        elif position == 'low':
            pos = 5  # 低位
        elif position == 'middle':
            pos = len(df) // 2  # 中间位置
        else:
            try:
                pos = int(position)
                if pos < 2 or pos >= len(df) - 1:
                    logger.warning("位置超出范围,使用随机位置")
                    pos = np.random.randint(5, len(df) - 3)
            except:
                logger.warning("位置参数无效,使用随机位置")
                pos = np.random.randint(5, len(df) - 3)
        
        # 获取注入位置的日期
        date1 = df.index[pos]
        date2 = df.index[pos+1]
        
        # 获取前一天的收盘价
        prev_close = df.loc[df.index[pos-1], 'close']
        
        # 创建第一根阴线
        open1 = prev_close * 1.02  # 高开
        close1 = open1 * 0.97  # 收阴
        high1 = open1 * 1.01
        low1 = close1 * 0.99
        
        # 创建第二根阴线(平行于第一根)
        open2 = open1 * 1.001  # 开盘价接近
        close2 = close1 * 1.001  # 收盘价接近
        high2 = open2 * 1.01
        low2 = close2 * 0.99
        
        # 注入数据
        df.loc[date1, 'open'] = open1
        df.loc[date1, 'high'] = high1
        df.loc[date1, 'low'] = low1
        df.loc[date1, 'close'] = close1
        
        df.loc[date2, 'open'] = open2
        df.loc[date2, 'high'] = high2
        df.loc[date2, 'low'] = low2
        df.loc[date2, 'close'] = close2
        
        # 调整第二天的成交量
        df.loc[date2, 'volume'] = df.loc[date1, 'volume'] * 1.3  # 放量
        
        logger.info(f"在位置 {pos} 和 {pos+1} 注入了双绿并行形态")
    
    elif pattern_type == 'three_black_crows':
        # 在数据中选择一个位置注入顶部三鸦形态
        if position == 'random':
            pos = np.random.randint(5, len(df) - 4)
        elif position == 'high':
            pos = len(df) - 4  # 高位
        elif position == 'low':
            pos = 5  # 低位
        elif position == 'middle':
            pos = len(df) // 2  # 中间位置
        else:
            try:
                pos = int(position)
                if pos < 2 or pos >= len(df) - 2:
                    logger.warning("位置超出范围,使用随机位置")
                    pos = np.random.randint(5, len(df) - 4)
            except:
                logger.warning("位置参数无效,使用随机位置")
                pos = np.random.randint(5, len(df) - 4)
        
        # 注入前先创建上涨趋势(如果是高位或中位形态)
        if position in ['high', 'middle', 'random']:
            # 创建上涨趋势,共5天
            for i in range(pos-5, pos):
                if i >= 0:
                    base_price = df.loc[df.index[i-1], 'close'] if i > 0 else 10.0
                    df.loc[df.index[i], 'open'] = base_price * 1.01
                    df.loc[df.index[i], 'close'] = base_price * 1.03
                    df.loc[df.index[i], 'high'] = df.loc[df.index[i], 'close'] * 1.01
                    df.loc[df.index[i], 'low'] = df.loc[df.index[i], 'open'] * 0.99
        
        # 获取注入位置的日期
        date1 = df.index[pos]
        date2 = df.index[pos+1]
        date3 = df.index[pos+2]
        
        # 获取前一天的收盘价
        prev_close = df.loc[df.index[pos-1], 'close']
        
        # 创建第一根阴线
        open1 = prev_close * 1.02  # 高开
        close1 = open1 * 0.97      # 收阴
        high1 = open1 * 1.01
        low1 = close1 * 0.99
        
        # 创建第二根阴线
        open2 = (open1 + close1) / 2  # 开盘价在第一根K线实体内
        close2 = close1 * 0.98        # 收盘价低于第一根
        high2 = open2 * 1.01
        low2 = close2 * 0.99
        
        # 创建第三根阴线
        open3 = (open2 + close2) / 2  # 开盘价在第二根K线实体内
        close3 = close2 * 0.98        # 收盘价低于第二根
        high3 = open3 * 1.01
        low3 = close3 * 0.99
        
        # 注入数据
        df.loc[date1, 'open'] = open1
        df.loc[date1, 'high'] = high1
        df.loc[date1, 'low'] = low1
        df.loc[date1, 'close'] = close1
        
        df.loc[date2, 'open'] = open2
        df.loc[date2, 'high'] = high2
        df.loc[date2, 'low'] = low2
        df.loc[date2, 'close'] = close2
        
        df.loc[date3, 'open'] = open3
        df.loc[date3, 'high'] = high3
        df.loc[date3, 'low'] = low3
        df.loc[date3, 'close'] = close3
        
        # 调整成交量
        if position == 'high':
            # 高位三鸦:放量
            df.loc[date1, 'volume'] = df.loc[df.index[pos-1], 'volume'] * 1.1
            df.loc[date2, 'volume'] = df.loc[date1, 'volume'] * 1.2
            df.loc[date3, 'volume'] = df.loc[date2, 'volume'] * 1.3
        elif position == 'low':
            # 低位三鸦:缩量
            df.loc[date1, 'volume'] = df.loc[df.index[pos-1], 'volume'] * 0.9
            df.loc[date2, 'volume'] = df.loc[date1, 'volume'] * 0.8
            df.loc[date3, 'volume'] = df.loc[date2, 'volume'] * 0.7
        else:
            # 中位三鸦:成交量保持稳定
            df.loc[date1, 'volume'] = df.loc[df.index[pos-1], 'volume'] * 1.05
            df.loc[date2, 'volume'] = df.loc[date1, 'volume'] * 1.05
            df.loc[date3, 'volume'] = df.loc[date2, 'volume'] * 1.05
            
        logger.info(f"在位置 {pos}, {pos+1} 和 {pos+2} 注入了顶部三鸦形态")
        
    return df

def detect_patterns(df, pattern_type, params=None):
    """检测K线形态"""
    logger.info(f"开始检测 {pattern_type} 形态")
    
    if params is None:
        params = {}
    
    # 获取策略实例
    strategy = get_strategy(pattern_type, params)
    
    # 生成信号
    signals = strategy.generate_signals(df)
    
    # 找出非零信号
    detected_indices = [i for i, s in enumerate(signals) if s != 0]
    
    logger.info(f"检测到 {len(detected_indices)} 个 {pattern_type} 形态")
    
    # 整理检测结果
    results = []
    for idx in detected_indices:
        date = df.index[idx]
        signal_value = signals[idx]
        direction = "看涨" if signal_value > 0 else "看跌"
        
        # 获取该位置的K线数据
        candle = df.iloc[idx].to_dict()
        
        results.append({
            "date": date.strftime("%Y-%m-%d"),
            "index": idx,
            "signal": signal_value,
            "direction": direction,
            "candle": candle
        })
    
    return results

def save_results(results, pattern_type, stock_code, output_file=None):
    """保存检测结果"""
    if output_file is None:
        output_file = f"{pattern_type}_{stock_code}_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"检测结果已保存到 {output_file}")

def main():
    parser = argparse.ArgumentParser(description="K线形态检测命令行工具")
    parser.add_argument("--pattern", type=str, default="double_green_parallel", 
                        help="要检测的K线形态:double_green_parallel, three_black_crows 等")
    parser.add_argument("--stock", type=str, default="000001", help="股票代码")
    parser.add_argument("--days", type=int, default=60, help="回溯天数")
    parser.add_argument("--inject", action="store_true", help="是否注入形态到数据中")
    parser.add_argument("--position", type=str, default="random", help="注入形态的位置(random/high/middle/low或数字索引)")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--list", action="store_true", help="列出所有可用的形态")
    
    args = parser.parse_args()
    
    # 列出所有可用形态
    if args.list:
        available_strategies = list_available_strategies()
        print("\n可用的K线形态:")
        for strategy in available_strategies:
            print(f"- {strategy['name']}: {strategy['description']}")
        return
    
    # 加载股票数据
    df = load_stock_data(args.stock, args.days)
    
    # 如果指定了注入形态,则注入
    if args.inject:
        df = inject_pattern(df, args.pattern, args.position)
    
    # 检测形态
    results = detect_patterns(df, args.pattern)
    
    # 输出检测结果
    if results:
        print(f"\n检测到 {len(results)} 个 {args.pattern} 形态:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 日期: {result['date']}, 信号: {result['signal']}, 方向: {result['direction']}")
        
        # 保存结果
        save_results(results, args.pattern, args.stock, args.output)
    else:
        print(f"\n未检测到 {args.pattern} 形态")

if __name__ == "__main__":
    main() 
