"""
使用Tushare数据进行回测
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import json

# 设置Tushare Token
TOKEN = "2f204ad53468c48203e351b2e43b7ebd2c1ef1028c9d4c4e8ea3736c"

def init_tushare():
    """初始化Tushare"""
    try:
        ts.set_token(TOKEN)
        pro = ts.pro_api()
        print(" Tushare初始化成功")
        return pro
    except Exception as e:
        print(f" Tushare初始化失败: {e}")
        return None

def get_stock_data(pro, ts_code, start_date, end_date):
    """获取股票数据"""
    try:
        # 获取日线数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print(f" 未获取到 {ts_code} 的数据")
            return None
        
        # 按日期排序
        df = df.sort_values('trade_date')
        print(f" 获取 {ts_code} 数据成功,共 {len(df)} 条记录")
        return df
        
    except Exception as e:
        print(f" 获取 {ts_code} 数据失败: {e}")
        return None

def calculate_simple_strategy_returns(df):
    """计算简单移动平均策略的收益率"""
    if df is None or len(df) < 20:
        return []
    
    df = df.copy()
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # 生成交易信号:MA5上穿MA20买入,下穿卖出
    df['signal'] = 0
    df.loc[df['ma5'] > df['ma20'], 'signal'] = 1  # 买入信号
    df.loc[df['ma5'] < df['ma20'], 'signal'] = -1  # 卖出信号
    
    # 计算策略收益率
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    return df['strategy_returns'].dropna().tolist()

def run_backtest():
    """运行回测"""
    print(" 开始Tushare数据回测")
    print("=" * 50)
    
    # 初始化Tushare
    pro = init_tushare()
    if not pro:
        return
    
    # 回测参数
    stock_codes = ['000001.SZ', '000002.SZ']  # 平安银行,万科A
    start_date = '20240101'
    end_date = '20240630'
    
    print(f" 回测股票: {stock_codes}")
    print(f" 回测期间: {start_date} - {end_date}")
    print("-" * 50)
    
    all_returns = []
    trade_records = []
    
    # 获取每只股票的数据
    for i, stock_code in enumerate(stock_codes):
        print(f"\n 处理 {stock_code}...")
        
        # 获取股票数据
        stock_data = get_stock_data(pro, stock_code, start_date, end_date)
        
        if stock_data is not None:
            # 计算策略收益率
            strategy_returns = calculate_simple_strategy_returns(stock_data)
            all_returns.extend(strategy_returns)
            
            # 模拟交易记录
            if len(stock_data) > 10:
                entry_price = stock_data.iloc[5]['close']
                exit_price = stock_data.iloc[-5]['close']
                profit = (exit_price - entry_price) * 1000 - 60  # 1000股,手续费60
                
                trade_records.append({
                    'trade_id': f'T{i+1:03d}',
                    'symbol': stock_code,
                    'entry_time': '2024-02-01T09:30:00',
                    'exit_time': '2024-05-01T15:00:00',
                    'entry_price': float(entry_price),
                    'exit_price': float(exit_price),
                    'quantity': 1000,
                    'profit': float(profit),
                    'commission': 60.0
                })
                
                print(f"   模拟交易: 买入价 {entry_price:.2f}, 卖出价 {exit_price:.2f}, 盈亏 {profit:.2f}")
    
    if not all_returns:
        print(" 未获取到任何有效数据")
        return
    
    print(f"\n 数据处理完成,共 {len(all_returns)} 个收益率数据点")
    
    # 调用增强回测API
    print("\n 调用增强回测API...")
    
    try:
        api_data = {
            "strategy_returns": all_returns[:100],  # 限制数据量
            "trade_records": trade_records,
            "initial_capital": 100000
        }
        
        response = requests.post(
            "http://localhost:8000/api/enhanced-analysis/enhanced-backtest",
            json=api_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(" API回测成功!")
            
            # 显示结果
            data = result.get('data', {})
            basic_metrics = data.get('basic_metrics', {})
            
            print("\n 回测结果:")
            print(f"  总收益率: {basic_metrics.get('total_return', 0):.2%}")
            print(f"  年化收益率: {basic_metrics.get('annual_return', 0):.2%}")
            print(f"  夏普比率: {basic_metrics.get('sharpe_ratio', 0):.2f}")
            print(f"  最大回撤: {basic_metrics.get('max_drawdown', 0):.2%}")
            print(f"  胜率: {basic_metrics.get('win_rate', 0):.2%}")
            print(f"  总交易次数: {basic_metrics.get('total_trades', 0)}")
            
            risk_metrics = data.get('risk_metrics', {})
            print(f"\n 风险指标:")
            print(f"  95% VaR: {risk_metrics.get('var_95', 0):.2%}")
            
            overall_score = data.get('overall_score', {})
            print(f"\n 综合评分: {overall_score.get('overall_score', 0):.1f}/100")
            print(f"  评级: {overall_score.get('rating', 'N/A')}")
            
        else:
            print(f" API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(" 无法连接到API服务器")
        print("请确保后端服务正在运行: python backend/app.py")
    except Exception as e:
        print(f" API调用异常: {e}")
    
    print("\n" + "=" * 50)
    print(" 回测完成!")

if __name__ == "__main__":
    run_backtest()
