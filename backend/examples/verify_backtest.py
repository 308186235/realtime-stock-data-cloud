"""
验证Tushare数据真实性和详细分析回测结果
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime

# 设置Tushare Token
TOKEN = "2f204ad53468c48203e351b2e43b7ebd2c1ef1028c9d4c4e8ea3736c"

def verify_tushare_data():
    """验证Tushare数据的真实性"""
    print(" 验证Tushare数据真实性")
    print("=" * 60)
    
    try:
        ts.set_token(TOKEN)
        pro = ts.pro_api()
        print(" Tushare API连接成功")
        
        # 获取平安银行最近几天的数据
        stock_code = '000001.SZ'
        end_date = '20240630'
        start_date = '20240625'  # 最近几天
        
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        
        if not df.empty:
            print(f"\n {stock_code} 最近数据验证:")
            df = df.sort_values('trade_date')
            for _, row in df.iterrows():
                print(f"  {row['trade_date']}: 开盘 {row['open']:.2f}, 收盘 {row['close']:.2f}, 成交量 {row['vol']:,.0f}")
            
            # 检查数据合理性
            price_range = df['close'].max() - df['close'].min()
            avg_price = df['close'].mean()
            print(f"\n 数据合理性检查:")
            print(f"  平均价格: {avg_price:.2f} 元")
            print(f"  价格波动范围: {price_range:.2f} 元")
            print(f"  相对波动: {price_range/avg_price:.2%}")
            
            if 5 <= avg_price <= 50 and price_range/avg_price < 0.2:
                print("   数据看起来合理")
            else:
                print("   数据可能异常")
        else:
            print(" 未获取到数据")
            
    except Exception as e:
        print(f" 验证失败: {e}")

def detailed_backtest_analysis():
    """详细的回测分析"""
    print("\n 详细回测分析")
    print("=" * 60)
    
    try:
        ts.set_token(TOKEN)
        pro = ts.pro_api()
        
        stock_code = '000001.SZ'  # 平安银行
        start_date = '20240101'
        end_date = '20240630'
        
        # 获取数据
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        print(f" {stock_code} 详细分析:")
        print(f"  数据期间: {df['trade_date'].min()} - {df['trade_date'].max()}")
        print(f"  数据条数: {len(df)} 条")
        print(f"  期初价格: {df.iloc[0]['close']:.2f} 元")
        print(f"  期末价格: {df.iloc[-1]['close']:.2f} 元")
        print(f"  期间涨跌: {(df.iloc[-1]['close']/df.iloc[0]['close']-1):.2%}")
        
        # 计算技术指标
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        # 生成交易信号
        df['signal'] = 0
        df.loc[df['ma5'] > df['ma20'], 'signal'] = 1  # 买入信号
        df.loc[df['ma5'] < df['ma20'], 'signal'] = -1  # 卖出信号
        
        # 计算信号变化
        df['signal_change'] = df['signal'].diff()
        
        # 统计交易信号
        buy_signals = len(df[df['signal_change'] == 2])  # 从-1或0变为1
        sell_signals = len(df[df['signal_change'] == -2])  # 从1变为-1
        hold_days = len(df[df['signal'] == 1])
        
        print(f"\n 交易信号统计:")
        print(f"  买入信号次数: {buy_signals}")
        print(f"  卖出信号次数: {sell_signals}")
        print(f"  持仓天数: {hold_days}")
        print(f"  持仓比例: {hold_days/len(df):.2%}")
        
        # 模拟完整交易过程
        trades = []
        position = 0  # 0=空仓, 1=持仓
        entry_price = 0
        entry_date = None
        
        for i, row in df.iterrows():
            if i < 20:  # 等待MA20计算完成
                continue
                
            current_signal = row['signal']
            
            # 买入信号且当前空仓
            if current_signal == 1 and position == 0:
                position = 1
                entry_price = row['close']
                entry_date = row['trade_date']
                
            # 卖出信号且当前持仓
            elif current_signal == -1 and position == 1:
                exit_price = row['close']
                exit_date = row['trade_date']
                
                # 计算交易结果
                profit_rate = (exit_price - entry_price) / entry_price
                profit_amount = profit_rate * 10000 - 60  # 假设1万元投入,手续费60元
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'profit_rate': profit_rate,
                    'profit_amount': profit_amount,
                    'days': (pd.to_datetime(exit_date, format='%Y%m%d') - 
                            pd.to_datetime(entry_date, format='%Y%m%d')).days
                })
                
                position = 0
        
        # 分析交易结果
        if trades:
            print(f"\n 完整交易记录 (共{len(trades)}笔):")
            total_profit = 0
            winning_trades = 0
            
            for i, trade in enumerate(trades, 1):
                status = "盈利" if trade['profit_rate'] > 0 else "亏损"
                print(f"  交易{i}: {trade['entry_date']} -> {trade['exit_date']}")
                print(f"    价格: {trade['entry_price']:.2f} -> {trade['exit_price']:.2f}")
                print(f"    收益率: {trade['profit_rate']:.2%} ({status})")
                print(f"    持仓天数: {trade['days']}天")
                print()
                
                total_profit += trade['profit_amount']
                if trade['profit_rate'] > 0:
                    winning_trades += 1
            
            # 重新计算胜率
            actual_win_rate = winning_trades / len(trades)
            print(f" 真实交易统计:")
            print(f"  总交易次数: {len(trades)}")
            print(f"  盈利交易: {winning_trades}")
            print(f"  亏损交易: {len(trades) - winning_trades}")
            print(f"  真实胜率: {actual_win_rate:.2%}")
            print(f"  总盈亏: {total_profit:.2f} 元")
            
            # 分析胜率低的原因
            print(f"\n 胜率分析:")
            if actual_win_rate < 0.5:
                print("   胜率确实偏低,可能原因:")
                print("    1. 移动平均线策略在震荡市中容易产生假信号")
                print("    2. 2024年上半年市场可能处于震荡或下跌趋势")
                print("    3. 策略参数(MA5/MA20)可能不适合当前市场环境")
                print("    4. 缺乏止损机制,亏损交易损失较大")
            
            # 检查市场趋势
            overall_trend = (df.iloc[-1]['close'] / df.iloc[0]['close'] - 1)
            print(f"\n 市场环境分析:")
            print(f"  整体趋势: {overall_trend:.2%}")
            if overall_trend < 0:
                print("   期间整体下跌,趋势跟踪策略表现不佳属正常")
            elif overall_trend > 0.1:
                print("   期间整体上涨,策略应该表现更好")
            else:
                print("   期间震荡整理,趋势策略容易被套")
                
        else:
            print(" 未产生完整交易")
            
    except Exception as e:
        print(f" 分析失败: {e}")

if __name__ == "__main__":
    verify_tushare_data()
    detailed_backtest_analysis()
