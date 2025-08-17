import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BenchmarkComparison:
    """策略与基准指数比较分析类"""
    
    @staticmethod
    def compare_with_benchmark(strategy_equity: pd.DataFrame, benchmark_data: pd.DataFrame, 
                              initial_capital: float = 100000.0) -> Dict:
        """
        比较策略与基准指数的表现
        
        参数:
        - strategy_equity: 策略权益曲线DataFrame
        - benchmark_data: 基准指数数据DataFrame
        - initial_capital: 初始资金
        
        返回:
        - 比较结果字典
        """
        if strategy_equity.empty or benchmark_data.empty:
            logger.warning("策略权益曲线或基准指数数据为空")
            return {}
        
        # 确保数据对齐
        strategy_equity = strategy_equity.copy()
        benchmark_data = benchmark_data.copy()
        
        # 确保日期列是索引
        if 'date' in strategy_equity.columns:
            strategy_equity.set_index('date', inplace=True)
        
        if 'date' in benchmark_data.columns:
            benchmark_data.set_index('date', inplace=True)
        
        # 截取共同的日期范围
        common_dates = strategy_equity.index.intersection(benchmark_data.index)
        if len(common_dates) == 0:
            logger.warning("策略与基准数据没有共同的日期")
            return {}
        
        strategy_equity = strategy_equity.loc[common_dates]
        benchmark_data = benchmark_data.loc[common_dates]
        
        # 计算基准指数的权益曲线
        benchmark_close = benchmark_data['close']
        benchmark_returns = benchmark_close.pct_change().fillna(0)
        
        benchmark_equity = pd.Series(index=benchmark_returns.index, dtype=float)
        benchmark_equity.iloc[0] = initial_capital
        
        for i in range(1, len(benchmark_returns)):
            benchmark_equity.iloc[i] = benchmark_equity.iloc[i-1] * (1 + benchmark_returns.iloc[i])
        
        # 确保策略权益曲线具有equity列
        if 'equity' not in strategy_equity.columns:
            logger.warning("策略权益曲线缺少equity列")
            return {}
        
        # 计算比较指标
        strategy_values = strategy_equity['equity']
        
        # 收益率比较
        strategy_return = (strategy_values.iloc[-1] / strategy_values.iloc[0]) - 1
        benchmark_return = (benchmark_equity.iloc[-1] / benchmark_equity.iloc[0]) - 1
        
        # 计算年化收益率
        days_count = (strategy_values.index[-1] - strategy_values.index[0]).days
        years = max(days_count / 365, 0.01)  # 至少0.01年,避免除零错误
        
        strategy_annual_return = (1 + strategy_return) ** (1 / years) - 1
        benchmark_annual_return = (1 + benchmark_return) ** (1 / years) - 1
        
        # 计算超额收益
        excess_return = strategy_return - benchmark_return
        excess_annual_return = strategy_annual_return - benchmark_annual_return
        
        # 计算波动率
        strategy_daily_returns = strategy_values.pct_change().fillna(0)
        benchmark_daily_returns = benchmark_equity.pct_change().fillna(0)
        
        strategy_volatility = strategy_daily_returns.std() * np.sqrt(252)  # 年化波动率
        benchmark_volatility = benchmark_daily_returns.std() * np.sqrt(252)
        
        # 计算夏普比率和信息比率
        risk_free_rate = 0.0  # 可根据实际情况设置
        
        strategy_sharpe = (strategy_annual_return - risk_free_rate) / strategy_volatility if strategy_volatility > 0 else 0
        benchmark_sharpe = (benchmark_annual_return - risk_free_rate) / benchmark_volatility if benchmark_volatility > 0 else 0
        
        # 计算信息比率
        tracking_error = (strategy_daily_returns - benchmark_daily_returns).std() * np.sqrt(252)
        information_ratio = excess_annual_return / tracking_error if tracking_error > 0 else 0
        
        # 计算最大回撤
        strategy_cum_max = strategy_values.cummax()
        strategy_drawdown = 1 - strategy_values / strategy_cum_max
        strategy_max_drawdown = strategy_drawdown.max()
        
        benchmark_cum_max = benchmark_equity.cummax()
        benchmark_drawdown = 1 - benchmark_equity / benchmark_cum_max
        benchmark_max_drawdown = benchmark_drawdown.max()
        
        # 计算β和α
        covariance = strategy_daily_returns.cov(benchmark_daily_returns)
        variance = benchmark_daily_returns.var()
        beta = covariance / variance if variance > 0 else 1
        
        # Jensen's Alpha (年化)
        alpha = strategy_annual_return - (risk_free_rate + beta * (benchmark_annual_return - risk_free_rate))
        
        # 计算捕获率
        up_market = benchmark_daily_returns > 0
        down_market = benchmark_daily_returns < 0
        
        if up_market.sum() > 0:
            up_capture = (strategy_daily_returns[up_market].mean() / benchmark_daily_returns[up_market].mean()) * 100
        else:
            up_capture = 0
            
        if down_market.sum() > 0:
            down_capture = (strategy_daily_returns[down_market].mean() / benchmark_daily_returns[down_market].mean()) * 100
        else:
            down_capture = 0
        
        # 月度表现比较
        strategy_monthly = strategy_values.resample('M').last()
        benchmark_monthly = benchmark_equity.resample('M').last()
        
        strategy_monthly_returns = strategy_monthly.pct_change().fillna(0)
        benchmark_monthly_returns = benchmark_monthly.pct_change().fillna(0)
        
        win_months = (strategy_monthly_returns > benchmark_monthly_returns).sum()
        total_months = len(strategy_monthly_returns)
        win_rate = win_months / total_months if total_months > 0 else 0
        
        # 创建权益曲线比较图
        plt.figure(figsize=(10, 6))
        plt.plot(strategy_values / strategy_values.iloc[0], label='策略')
        plt.plot(benchmark_equity / benchmark_equity.iloc[0], label='基准')
        plt.title('策略与基准的权益曲线比较')
        plt.xlabel('日期')
        plt.ylabel('相对收益(初始值=1)')
        plt.legend()
        plt.grid(True)
        
        # 转换图表为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        equity_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        # 创建回撤比较图
        plt.figure(figsize=(10, 6))
        plt.plot(strategy_drawdown, label='策略回撤')
        plt.plot(benchmark_drawdown, label='基准回撤')
        plt.title('策略与基准的回撤比较')
        plt.xlabel('日期')
        plt.ylabel('回撤幅度')
        plt.legend()
        plt.grid(True)
        
        # 转换图表为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        drawdown_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        # 创建月度表现热图数据
        monthly_comparison = pd.DataFrame({
            '策略': strategy_monthly_returns,
            '基准': benchmark_monthly_returns,
            '超额': strategy_monthly_returns - benchmark_monthly_returns
        })
        
        # 整理月度数据为热图格式
        if not monthly_comparison.empty:
            monthly_data = []
            for idx, row in monthly_comparison.iterrows():
                year = idx.year
                month = idx.month
                monthly_data.append({
                    "year": year,
                    "month": month,
                    "strategy": float(row['策略']),
                    "benchmark": float(row['基准']),
                    "excess": float(row['超额'])
                })
        else:
            monthly_data = []
        
        # 汇总结果
        comparison_result = {
            'summary': {
                'total_return': {
                    'strategy': float(strategy_return),
                    'benchmark': float(benchmark_return),
                    'excess': float(excess_return)
                },
                'annual_return': {
                    'strategy': float(strategy_annual_return),
                    'benchmark': float(benchmark_annual_return),
                    'excess': float(excess_annual_return)
                },
                'sharpe_ratio': {
                    'strategy': float(strategy_sharpe),
                    'benchmark': float(benchmark_sharpe)
                },
                'max_drawdown': {
                    'strategy': float(strategy_max_drawdown),
                    'benchmark': float(benchmark_max_drawdown)
                },
                'volatility': {
                    'strategy': float(strategy_volatility),
                    'benchmark': float(benchmark_volatility)
                },
                'information_ratio': float(information_ratio),
                'alpha': float(alpha),
                'beta': float(beta),
                'up_capture': float(up_capture),
                'down_capture': float(down_capture),
                'win_rate': float(win_rate),
                'months_count': int(total_months),
                'win_months': int(win_months)
            },
            'charts': {
                'equity_comparison': equity_chart,
                'drawdown_comparison': drawdown_chart
            },
            'monthly_data': monthly_data
        }
        
        return comparison_result
    
    @staticmethod
    def get_benchmark_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取基准指数数据
        
        参数:
        - symbol: 基准指数代码,如'000001.SS'(上证指数)
        - start_date: 开始日期
        - end_date: 结束日期
        
        返回:
        - 基准指数数据DataFrame
        """
        # 此处应连接到实际数据源获取基准数据
        # 为演示使用,这里生成模拟数据
        
        logger.info(f"获取基准数据: {symbol}, {start_date} 至 {end_date}")
        
        # 生成日期序列
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        date_range = pd.date_range(start=start, end=end, freq='B')  # 仅工作日
        
        # 生成基准价格数据
        n = len(date_range)
        if n == 0:
            return pd.DataFrame()
            
        # 起始价格
        start_price = 3000.0  # 假设的指数起始点位
        
        # 生成随机价格序列,带有微弱的上涨趋势
        trend = 0.0002  # 每日平均上涨0.02%
        volatility = 0.01  # 日波动率1%
        
        prices = [start_price]
        for i in range(1, n):
            random_change = np.random.normal(trend, volatility)
            prices.append(prices[-1] * (1 + random_change))
        
        # 创建DataFrame
        benchmark_data = pd.DataFrame({
            'date': date_range,
            'open': prices,
            'high': [p * (1 + np.random.uniform(0, 0.005)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.005)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000000, 10000000) for _ in range(n)]
        })
        
        return benchmark_data
    
    @staticmethod
    def get_benchmark_list() -> List[Dict]:
        """
        获取可用的基准指数列表
        
        返回:
        - 可用基准指数列表
        """
        # 实际应用中应从数据源获取可用的基准指数
        # 这里返回一些常用指数作为示例
        
        benchmarks = [
            {"symbol": "000001.SS", "name": "上证指数", "market": "中国", "description": "上海证券交易所综合指数"},
            {"symbol": "399001.SZ", "name": "深证成指", "market": "中国", "description": "深圳证券交易所成份股指数"},
            {"symbol": "399005.SZ", "name": "中小板指", "market": "中国", "description": "深圳证券交易所中小企业板指数"},
            {"symbol": "399006.SZ", "name": "创业板指", "market": "中国", "description": "深圳证券交易所创业板指数"},
            {"symbol": "000016.SS", "name": "上证50", "market": "中国", "description": "上海证券交易所50只大盘蓝筹股指数"},
            {"symbol": "000300.SS", "name": "沪深300", "market": "中国", "description": "覆盖沪深两市大型蓝筹股的指数"},
            {"symbol": "000905.SS", "name": "中证500", "market": "中国", "description": "覆盖沪深两市小型蓝筹股的指数"},
            {"symbol": "SPY", "name": "标普500指数ETF", "market": "美国", "description": "跟踪标普500指数的ETF"},
            {"symbol": "QQQ", "name": "纳斯达克100指数ETF", "market": "美国", "description": "跟踪纳斯达克100指数的ETF"}
        ]
        
        return benchmarks 
