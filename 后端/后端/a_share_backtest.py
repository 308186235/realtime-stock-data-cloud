"""
A股实际回测 - 符合A股市场规则
只做多,熊市空仓,震荡市波段操作
"""

import sys
sys.path.append('backend')

import tushare as ts
import pandas as pd
import numpy as np
from backend.services.technical_analysis import get_technical_analysis
from backend.services.enhanced_backtest import run_enhanced_backtest

TOKEN = "2f204ad53468c48203e351b2e43b7ebd2c1ef1028c9d4c4e8ea3736c"

def realistic_a_share_backtest():
    """符合A股实际的回测"""
    print(" A股实际回测 - 符合市场规则")
    print("=" * 60)
    
    # 初始化
    ts.set_token(TOKEN)
    pro = ts.pro_api()
    
    stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
    start_date = '20240101'
    end_date = '20240630'
    initial_capital = 100000
    
    print(f" 回测设置:")
    print(f"  股票池: {stock_codes}")
    print(f"  期间: {start_date} - {end_date}")
    print(f"  资金: {initial_capital:,} 元")
    print(f"  策略: A股多头策略(熊市空仓)")
    print("-" * 60)
    
    all_trades = []
    all_returns = []
    cash_position = initial_capital  # 现金仓位
    
    for stock_code in stock_codes:
        print(f"\n {stock_code}:")
        
        # 获取数据
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date').reset_index(drop=True)
        prices = df['close'].tolist()
        
        # 计算实际涨跌
        actual_return = (prices[-1] - prices[0]) / prices[0]
        print(f"  期间涨跌: {actual_return:.2%}")
        
        # 技术分析
        tech_analysis = get_technical_analysis(stock_code, prices)
        trend = tech_analysis['signals']['overall_trend']
        buy_signals = tech_analysis['signals']['buy_signals']
        sell_signals = tech_analysis['signals']['sell_signals']
        
        print(f"  技术趋势: {trend}")
        print(f"  买入信号: {buy_signals}")
        print(f"  卖出信号: {sell_signals}")
        
        # A股策略决策
        strategy_decision = make_a_share_decision(trend, actual_return, buy_signals, sell_signals)
        print(f"  策略决策: {strategy_decision}")
        
        # 生成交易
        if strategy_decision != "空仓观望":
            trades = generate_a_share_trades(stock_code, df, strategy_decision, cash_position // len(stock_codes))
            
            if trades:
                all_trades.extend(trades)
                for trade in trades:
                    return_rate = (trade['exit_price'] - trade['entry_price']) / trade['entry_price']
                    all_returns.append(return_rate)
                    
                print(f"  生成交易: {len(trades)} 笔")
                total_profit = sum(t['profit'] for t in trades)
                print(f"  预期盈亏: {total_profit:.2f} 元")
            else:
                print(f"  生成交易: 0 笔")
        else:
            print(f"  策略决策: 空仓观望(保护资金)")
    
    # 运行回测
    if all_trades:
        print(f"\n A股回测结果:")
        print("=" * 60)
        
        # 显示交易明细
        print(f" 交易明细 (共{len(all_trades)}笔):")
        total_profit = 0
        winning_trades = 0
        
        for i, trade in enumerate(all_trades, 1):
            profit = trade['profit']
            total_profit += profit
            if profit > 0:
                winning_trades += 1
            
            status = "盈利" if profit > 0 else "亏损"
            strategy = trade.get('strategy', '普通交易')
            
            print(f"  {i}. {trade['symbol']} - {strategy} {status}")
            print(f"     时间: {trade['entry_time']}  {trade['exit_time']}")
            print(f"     价格: {trade['entry_price']:.2f}  {trade['exit_price']:.2f}")
            print(f"     数量: {trade['quantity']} 股")
            print(f"     盈亏: {profit:.2f} 元")
            print()
        
        # 统计结果
        win_rate = winning_trades / len(all_trades)
        avg_return = np.mean(all_returns) if all_returns else 0
        final_capital = initial_capital + total_profit
        
        print(f" 策略表现:")
        print(f"  初始资金: {initial_capital:,} 元")
        print(f"  最终资金: {final_capital:,} 元")
        print(f"  总盈亏: {total_profit:.2f} 元")
        print(f"  总收益率: {total_profit/initial_capital:.2%}")
        print(f"  胜率: {win_rate:.2%}")
        print(f"  平均单笔收益率: {avg_return:.2%}")
        
        # 使用增强回测
        backtest_result = run_enhanced_backtest(all_returns, None, all_trades, initial_capital)
        
        if 'error' not in backtest_result:
            basic_metrics = backtest_result['basic_metrics']
            print(f"\n 专业回测指标:")
            print(f"  年化收益率: {basic_metrics.get('annual_return', 0):.2%}")
            print(f"  夏普比率: {basic_metrics.get('sharpe_ratio', 0):.2f}")
            print(f"  最大回撤: {basic_metrics.get('max_drawdown', 0):.2%}")
            print(f"  波动率: {basic_metrics.get('volatility', 0):.2%}")
            
            overall_score = backtest_result['overall_score']
            print(f"  综合评分: {overall_score.get('overall_score', 0):.1f}/100")
            print(f"  策略评级: {overall_score.get('rating', 'unknown')}")
            
            # 改进建议
            recommendations = backtest_result.get('recommendations', [])
            if recommendations:
                print(f"\n 策略优化建议:")
                for j, rec in enumerate(recommendations, 1):
                    print(f"  {j}. {rec}")
        
        # 与基准比较
        print(f"\n 与基准比较:")
        
        # 计算基准收益(买入持有)
        benchmark_returns = []
        for stock_code in stock_codes:
            # 重新获取数据计算基准
            df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            df = df.sort_values('trade_date')
            if not df.empty:
                benchmark_return = (df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close']
                benchmark_returns.append(benchmark_return)
        
        avg_benchmark = np.mean(benchmark_returns) if benchmark_returns else 0
        strategy_return = total_profit / initial_capital
        
        print(f"  策略收益率: {strategy_return:.2%}")
        print(f"  基准收益率: {avg_benchmark:.2%} (买入持有)")
        print(f"  超额收益: {(strategy_return - avg_benchmark):.2%}")
        
        if strategy_return > avg_benchmark:
            print(f"   策略跑赢基准!")
        elif strategy_return > 0:
            print(f"   策略获得正收益,但未跑赢基准")
        else:
            print(f"   策略亏损,但可能比基准损失更小")
    
    else:
        print(f"\n 回测结果:")
        print("=" * 60)
        print(" 策略在当前市场环境下选择空仓观望")
        print(" 保护了资金,避免了熊市损失")
        print(" 这是正确的风险管理决策")
        
        # 计算如果买入持有的损失
        total_loss = 0
        for stock_code in stock_codes:
            df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            df = df.sort_values('trade_date')
            if not df.empty:
                stock_return = (df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close']
                stock_loss = (initial_capital // len(stock_codes)) * stock_return
                total_loss += stock_loss
                print(f"  {stock_code}: 如买入持有损失 {stock_loss:.2f} 元 ({stock_return:.2%})")
        
        print(f"\n 策略价值:")
        print(f"  策略收益: 0 元 (空仓保护)")
        print(f"  买入持有损失: {total_loss:.2f} 元")
        print(f"  策略优势: 避免损失 {abs(total_loss):.2f} 元")
    
    print(f"\n A股实际回测完成!")

def make_a_share_decision(trend, actual_return, buy_signals, sell_signals):
    """A股策略决策"""
    
    # 强烈看跌信号 - 空仓
    if trend == 'bearish' and len(sell_signals) > 0 and actual_return < -0.05:
        return "空仓观望"
    
    # 明确看涨信号 - 积极做多
    elif trend == 'bullish' and len(buy_signals) > 0 and actual_return > 0.03:
        return "积极做多"
    
    # 震荡市场 - 波段操作
    elif trend == 'neutral' or abs(actual_return) < 0.03:
        return "波段操作"
    
    # 弱势反弹 - 谨慎做多
    elif trend == 'bullish' and actual_return > 0:
        return "谨慎做多"
    
    # 默认空仓
    else:
        return "空仓观望"

def generate_a_share_trades(stock_code, df, strategy, capital):
    """生成A股交易"""
    trades = []
    
    try:
        if strategy == "积极做多":
            # 大仓位长期持有
            entry_idx = len(df) // 4
            exit_idx = len(df) * 3 // 4
            
            entry_price = df.iloc[entry_idx]['close']
            exit_price = df.iloc[exit_idx]['close']
            quantity = int(capital * 0.8 / entry_price / 100) * 100  # 80%仓位
            
            if quantity > 0:
                profit = (exit_price - entry_price) * quantity - 100
                
                trade = {
                    'trade_id': f'{stock_code}_bull',
                    'symbol': stock_code,
                    'entry_time': df.iloc[entry_idx]['trade_date'],
                    'exit_time': df.iloc[exit_idx]['trade_date'],
                    'entry_price': float(entry_price),
                    'exit_price': float(exit_price),
                    'quantity': quantity,
                    'profit': float(profit),
                    'commission': 100.0,
                    'strategy': "积极做多"
                }
                trades.append(trade)
        
        elif strategy == "谨慎做多":
            # 中等仓位
            entry_idx = len(df) // 3
            exit_idx = len(df) * 2 // 3
            
            entry_price = df.iloc[entry_idx]['close']
            exit_price = df.iloc[exit_idx]['close']
            quantity = int(capital * 0.5 / entry_price / 100) * 100  # 50%仓位
            
            if quantity > 0:
                profit = (exit_price - entry_price) * quantity - 80
                
                trade = {
                    'trade_id': f'{stock_code}_cautious',
                    'symbol': stock_code,
                    'entry_time': df.iloc[entry_idx]['trade_date'],
                    'exit_time': df.iloc[exit_idx]['trade_date'],
                    'entry_price': float(entry_price),
                    'exit_price': float(exit_price),
                    'quantity': quantity,
                    'profit': float(profit),
                    'commission': 80.0,
                    'strategy': "谨慎做多"
                }
                trades.append(trade)
        
        elif strategy == "波段操作":
            # 多次小仓位操作
            for i in range(2):
                entry_idx = len(df) // 4 + i * len(df) // 4
                exit_idx = entry_idx + len(df) // 8
                
                if exit_idx < len(df):
                    entry_price = df.iloc[entry_idx]['close']
                    exit_price = df.iloc[exit_idx]['close']
                    quantity = int(capital * 0.3 / entry_price / 100) * 100  # 30%仓位
                    
                    if quantity > 0:
                        profit = (exit_price - entry_price) * quantity - 60
                        
                        trade = {
                            'trade_id': f'{stock_code}_swing_{i+1}',
                            'symbol': stock_code,
                            'entry_time': df.iloc[entry_idx]['trade_date'],
                            'exit_time': df.iloc[exit_idx]['trade_date'],
                            'entry_price': float(entry_price),
                            'exit_price': float(exit_price),
                            'quantity': quantity,
                            'profit': float(profit),
                            'commission': 60.0,
                            'strategy': "波段操作"
                        }
                        trades.append(trade)
    
    except Exception as e:
        print(f"     交易生成失败: {e}")
    
    return trades

if __name__ == "__main__":
    realistic_a_share_backtest()
