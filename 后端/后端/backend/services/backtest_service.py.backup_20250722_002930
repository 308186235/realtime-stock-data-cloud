import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from sqlalchemy.orm import Session
import uuid
from typing import List, Dict, Any, Optional

from strategies import StrategyFactory
# from utils.visualization import generate_performance_chart  # 函数不存在，暂时注释
from models.models import Backtest, Trade, Strategy, User
from services.data_service import get_historical_data

logger = logging.getLogger(__name__)

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def run_backtest(self, user_id: int, backtest_config: Dict[str, Any]) -> str:
        """
        运行回测
        
        Args:
            user_id: 用户ID
            backtest_config: 回测配置
            
        Returns:
            backtest_id: 回测ID
        """
        # 创建回测记录
        backtest = Backtest(
            name=backtest_config.get('name', f"回测 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
            start_date=backtest_config['start_date'],
            end_date=backtest_config['end_date'],
            initial_capital=backtest_config.get('initial_capital', 100000.0),
            commission=backtest_config.get('commission', 0.0003),
            status="pending",
            config=backtest_config
        )
        
        # 获取用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            backtest.users.append(user)
        
        # 保存回测记录
        self.db.add(backtest)
        self.db.commit()
        self.db.refresh(backtest)
        
        try:
            # 更新状态为运行中
            backtest.status = "running"
            self.db.commit()
            
            # 执行回测
            result = self._execute_backtest(backtest)
            
            # 更新回测结果
            backtest.results = result
            backtest.status = "completed"
            self.db.commit()
            
            return backtest.backtest_id
            
        except Exception as e:
            # 回测失败
            backtest.status = "failed"
            backtest.results = {"error": str(e)}
            self.db.commit()
            raise
    
    def _execute_backtest(self, backtest: Backtest) -> Dict[str, Any]:
        """执行回测计算"""
        config = backtest.config
        symbols = config.get('symbols', [])
        strategies = config.get('strategies', [])
        start_date = backtest.start_date
        end_date = backtest.end_date
        initial_capital = backtest.initial_capital
        commission = backtest.commission
        
        # 初始化结果
        trades = []
        portfolio_values = []
        current_capital = initial_capital
        current_positions = {symbol: 0 for symbol in symbols}
        
        # 获取所有股票的历史数据
        all_data = {}
        for symbol in symbols:
            # 获取历史数据
            data = get_historical_data(symbol, start_date, end_date)
            if data is not None:
                all_data[symbol] = data
        
        # 构建回测日期序列
        all_dates = set()
        for symbol, data in all_data.items():
            all_dates.update(data.index)
        all_dates = sorted(all_dates)
        
        # 初始化结果指标
        equity_curve = []
        
        # 遍历每个交易日
        for current_date in all_dates:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 计算当前资产价值
            portfolio_value = current_capital
            for symbol, position in current_positions.items():
                if position > 0 and symbol in all_data and date_str in all_data[symbol].index:
                    current_price = all_data[symbol].loc[date_str, 'close']
                    portfolio_value += position * current_price
            
            # 添加到权益曲线
            equity_curve.append({
                'date': date_str,
                'equity': portfolio_value
            })
            
            # 对每个策略生成交易信号
            for strategy_config in strategies:
                strategy_type = strategy_config.get('type')
                params = strategy_config.get('params', {})
                
                # 对每个股票执行策略
                for symbol in symbols:
                    if symbol not in all_data:
                        continue
                        
                    # 获取当前日期之前的数据
                    current_data = all_data[symbol].loc[:date_str]
                    
                    # 生成信号 (这里需要实现具体策略的信号生成逻辑)
                    signal = self._generate_signal(strategy_type, current_data, params)
                    
                    # 根据信号生成交易
                    if signal != 0:  # 0表示无信号
                        current_price = current_data.iloc[-1]['close']
                        
                        if signal > 0 and current_positions[symbol] == 0:  # 买入信号
                            # 计算能买入的最大股数 (简化为10%资金)
                            max_capital = current_capital * 0.1
                            shares = int(max_capital / current_price)
                            
                            if shares > 0:
                                cost = shares * current_price * (1 + commission)
                                current_capital -= cost
                                current_positions[symbol] += shares
                                
                                # 记录买入交易
                                trade = {
                                    'date': date_str,
                                    'symbol': symbol,
                                    'action': 'BUY',
                                    'price': current_price,
                                    'shares': shares,
                                    'cost': cost,
                                    'profit': 0.0
                                }
                                trades.append(trade)
                                
                                # 保存到数据库
                                db_trade = Trade(
                                    backtest_id=backtest.id,
                                    symbol=symbol,
                                    action='BUY',
                                    date=datetime.strptime(date_str, '%Y-%m-%d'),
                                    price=current_price,
                                    shares=shares,
                                    cost=cost,
                                    profit=0.0
                                )
                                self.db.add(db_trade)
                                
                        elif signal < 0 and current_positions[symbol] > 0:  # 卖出信号
                            shares = current_positions[symbol]
                            revenue = shares * current_price * (1 - commission)
                            cost_basis = sum([t['cost'] for t in trades if t['symbol'] == symbol and t['action'] == 'BUY'])
                            profit = revenue - cost_basis
                            
                            current_capital += revenue
                            current_positions[symbol] = 0
                            
                            # 记录卖出交易
                            trade = {
                                'date': date_str,
                                'symbol': symbol,
                                'action': 'SELL',
                                'price': current_price,
                                'shares': shares,
                                'revenue': revenue,
                                'profit': profit
                            }
                            trades.append(trade)
                            
                            # 保存到数据库
                            db_trade = Trade(
                                backtest_id=backtest.id,
                                symbol=symbol,
                                action='SELL',
                                date=datetime.strptime(date_str, '%Y-%m-%d'),
                                price=current_price,
                                shares=shares,
                                revenue=revenue,
                                profit=profit
                            )
                            self.db.add(db_trade)
        
        # 提交交易记录
        self.db.commit()
        
        # 计算回测指标
        metrics = self._calculate_metrics(equity_curve, trades)
        
        # 创建基准比较
        benchmark_report = None
        if config.get('benchmark_comparison', {}).get('enabled', False):
            benchmark_symbol = config.get('benchmark_comparison', {}).get('symbol')
            if benchmark_symbol and benchmark_symbol in all_data:
                benchmark_data = all_data[benchmark_symbol]
                benchmark_report = self._calculate_benchmark_comparison(equity_curve, benchmark_data)
        
        # 准备图表数据 (实际项目中需要生成真实的图表)
        charts = {
            "equity_curve": "base64_encoded_equity_curve_image",
            "drawdown_curve": "base64_encoded_drawdown_curve_image",
            "monthly_returns": "base64_encoded_monthly_returns_image",
            "trade_distribution": "base64_encoded_trade_distribution_image"
        }
        
        # 构建最终结果
        result = {
            "metrics": metrics,
            "charts": charts,
            "trades": trades,
            "equity_curve": equity_curve,
            "benchmark_report": benchmark_report
        }
        
        return result
    
    def _generate_signal(self, strategy_type: str, data: pd.DataFrame, params: Dict[str, Any]) -> int:
        """
        生成交易信号
        
        Args:
            strategy_type: 策略类型
            data: 历史数据
            params: 策略参数
            
        Returns:
            signal: 1表示买入,-1表示卖出,0表示无信号
        """
        # 根据不同的策略类型生成信号
        if strategy_type == "ma_cross":
            return self._ma_cross_strategy(data, params)
        elif strategy_type == "rsi":
            return self._rsi_strategy(data, params)
        elif strategy_type == "bollinger_bands":
            return self._bollinger_bands_strategy(data, params)
        elif strategy_type == "inverted_three_red":
            return self._inverted_three_red_strategy(data, params)
        # 添加更多策略...
        
        return 0  # 默认无信号
    
    def _ma_cross_strategy(self, data: pd.DataFrame, params: Dict[str, Any]) -> int:
        """移动平均线交叉策略"""
        short_period = params.get('short_period', 5)
        long_period = params.get('long_period', 20)
        
        if len(data) < long_period + 2:
            return 0
            
        # 计算移动平均线
        data['ma_short'] = data['close'].rolling(window=short_period).mean()
        data['ma_long'] = data['close'].rolling(window=long_period).mean()
        
        # 获取最后两行
        last = data.iloc[-1]
        prev = data.iloc[-2]
        
        # 判断金叉和死叉
        if prev['ma_short'] <= prev['ma_long'] and last['ma_short'] > last['ma_long']:
            return 1  # 金叉买入
        elif prev['ma_short'] >= prev['ma_long'] and last['ma_short'] < last['ma_long']:
            return -1  # 死叉卖出
            
        return 0
    
    def _rsi_strategy(self, data: pd.DataFrame, params: Dict[str, Any]) -> int:
        """RSI策略"""
        period = params.get('period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        
        if len(data) < period + 1:
            return 0
            
        # 计算价格变化
        delta = data['close'].diff()
        
        # 计算涨跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算RS和RSI
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # 获取最后一个RSI值
        last_rsi = data['rsi'].iloc[-1]
        
        # 生成信号
        if last_rsi < oversold:
            return 1  # 超卖买入
        elif last_rsi > overbought:
            return -1  # 超买卖出
            
        return 0
    
    def _bollinger_bands_strategy(self, data: pd.DataFrame, params: Dict[str, Any]) -> int:
        """布林带策略"""
        period = params.get('period', 20)
        std_dev = params.get('std_dev', 2)
        
        if len(data) < period + 1:
            return 0
            
        # 计算移动平均线
        data['ma'] = data['close'].rolling(window=period).mean()
        
        # 计算标准差
        data['std'] = data['close'].rolling(window=period).std()
        
        # 计算上下轨
        data['upper'] = data['ma'] + (data['std'] * std_dev)
        data['lower'] = data['ma'] - (data['std'] * std_dev)
        
        # 获取最后一个收盘价
        last_close = data['close'].iloc[-1]
        last_upper = data['upper'].iloc[-1]
        last_lower = data['lower'].iloc[-1]
        
        # 生成信号
        if last_close < last_lower:
            return 1  # 价格触及下轨,买入
        elif last_close > last_upper:
            return -1  # 价格触及上轨,卖出
            
        return 0
    
    def _inverted_three_red_strategy(self, data: pd.DataFrame, params: Dict[str, Any]) -> int:
        """倒三红形态策略"""
        body_decrease_threshold = params.get('body_decrease_threshold', 0.67)
        upper_shadow_increase_threshold = params.get('upper_shadow_increase_threshold', 1.0)
        volume_threshold = params.get('volume_threshold', 1.5)
        
        if len(data) < 5:
            return 0
            
        # 获取最后3根K线
        candles = data.iloc[-3:].copy()
        
        # 计算实体长度 (绝对值)
        candles['body'] = abs(candles['close'] - candles['open'])
        
        # 计算上影线长度
        candles['upper_shadow'] = candles.apply(
            lambda x: max(x['high'] - x['close'], x['high'] - x['open']), 
            axis=1
        )
        
        # 判断是否为三根阳线
        is_bullish = (candles['close'] > candles['open']).all()
        
        if not is_bullish:
            return 0
            
        # 判断实体是否递减
        body_decreasing = (
            candles['body'].iloc[0] > candles['body'].iloc[1] * body_decrease_threshold and
            candles['body'].iloc[1] > candles['body'].iloc[2] * body_decrease_threshold
        )
        
        # 判断上影线是否递增
        upper_shadow_increasing = (
            candles['upper_shadow'].iloc[2] > candles['upper_shadow'].iloc[1] * upper_shadow_increase_threshold and
            candles['upper_shadow'].iloc[1] > candles['upper_shadow'].iloc[0] * upper_shadow_increase_threshold
        )
        
        # 判断成交量特征
        if 'volume' in candles.columns:
            avg_volume = data['volume'].iloc[-5:-3].mean()  # 取前两天的平均成交量
            last_volume = candles['volume'].iloc[-1]
            volume_condition = last_volume > avg_volume * volume_threshold
        else:
            volume_condition = True  # 如果没有成交量数据,忽略该条件
        
        # 综合判断形态是否成立
        if body_decreasing and upper_shadow_increasing and volume_condition:
            # 这通常是看跌信号
            return -1
            
        return 0
    
    def _calculate_metrics(self, equity_curve: List[Dict[str, Any]], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算回测指标"""
        if not equity_curve:
            return {}
        
        # 提取权益曲线数据
        equity_values = [point['equity'] for point in equity_curve]
        initial_equity = equity_values[0]
        final_equity = equity_values[-1]
        
        # 计算总收益率
        total_return = (final_equity / initial_equity) - 1
        
        # 计算年化收益率 (假设252个交易日)
        days = len(equity_curve)
        annual_return = ((1 + total_return) ** (252 / days)) - 1 if days > 0 else 0
        
        # 计算最大回撤
        max_drawdown = 0
        peak_value = equity_values[0]
        
        for value in equity_values:
            if value > peak_value:
                peak_value = value
            drawdown = (peak_value - value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)
        
        # 计算胜率
        profitable_trades = sum(1 for trade in trades if trade.get('action') == 'SELL' and trade.get('profit', 0) > 0)
        total_sell_trades = sum(1 for trade in trades if trade.get('action') == 'SELL')
        win_rate = profitable_trades / total_sell_trades if total_sell_trades > 0 else 0
        
        # 计算盈亏比
        total_profit = sum(trade.get('profit', 0) for trade in trades if trade.get('action') == 'SELL' and trade.get('profit', 0) > 0)
        total_loss = abs(sum(trade.get('profit', 0) for trade in trades if trade.get('action') == 'SELL' and trade.get('profit', 0) < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # 计算夏普比率 (假设无风险利率为0.02)
        if len(equity_values) > 1:
            returns = [equity_values[i] / equity_values[i-1] - 1 for i in range(1, len(equity_values))]
            avg_return = sum(returns) / len(returns)
            risk_free_rate = 0.02 / 252  # 日化无风险利率
            std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe_ratio = (avg_return - risk_free_rate) / std_dev * (252 ** 0.5) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0
            
        # 计算波动率
        if len(equity_values) > 1:
            returns = [equity_values[i] / equity_values[i-1] - 1 for i in range(1, len(equity_values))]
            volatility = (sum(r ** 2 for r in returns) / len(returns)) ** 0.5 * (252 ** 0.5)
        else:
            volatility = 0
            
        # 整合指标
        metrics = {
            "total_return": total_return,
            "annual_return": annual_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "trade_count": total_sell_trades,
            "avg_trade_duration": 0,  # 需计算平均持仓时间
            "volatility": volatility
        }
        
        return metrics
    
    def _calculate_benchmark_comparison(self, equity_curve: List[Dict[str, Any]], benchmark_data: pd.DataFrame) -> Dict[str, Any]:
        """计算与基准的比较"""
        # 提取权益曲线数据
        equity_dates = [point['date'] for point in equity_curve]
        equity_values = [point['equity'] for point in equity_curve]
        
        # 初始化基准数据
        benchmark_values = []
        
        # 获取对应日期的基准价格
        for date in equity_dates:
            if date in benchmark_data.index:
                benchmark_values.append(benchmark_data.loc[date, 'close'])
            else:
                # 如果没有当天数据,使用前一天的收盘价
                previous_dates = benchmark_data.index[benchmark_data.index < date]
                if not previous_dates.empty:
                    benchmark_values.append(benchmark_data.loc[previous_dates[-1], 'close'])
                else:
                    benchmark_values.append(None)
        
        # 过滤掉没有基准数据的点
        valid_indices = [i for i, v in enumerate(benchmark_values) if v is not None]
        valid_equity = [equity_values[i] for i in valid_indices]
        valid_benchmark = [benchmark_values[i] for i in valid_indices]
        
        if not valid_indices:
            return None
            
        # 计算收益率
        strategy_return = (valid_equity[-1] / valid_equity[0]) - 1
        benchmark_return = (valid_benchmark[-1] / valid_benchmark[0]) - 1
        
        # 计算阿尔法 (超额收益)
        alpha = strategy_return - benchmark_return
        
        # 计算贝塔 (市场敏感度)
        # 先计算每日收益率
        strategy_daily_returns = [(valid_equity[i] / valid_equity[i-1]) - 1 for i in range(1, len(valid_equity))]
        benchmark_daily_returns = [(valid_benchmark[i] / valid_benchmark[i-1]) - 1 for i in range(1, len(valid_benchmark))]
        
        # 计算协方差和方差
        if len(strategy_daily_returns) > 1:
            mean_strategy = sum(strategy_daily_returns) / len(strategy_daily_returns)
            mean_benchmark = sum(benchmark_daily_returns) / len(benchmark_daily_returns)
            
            covariance = sum((s - mean_strategy) * (b - mean_benchmark) for s, b in zip(strategy_daily_returns, benchmark_daily_returns)) / len(strategy_daily_returns)
            variance = sum((b - mean_benchmark) ** 2 for b in benchmark_daily_returns) / len(benchmark_daily_returns)
            
            beta = covariance / variance if variance > 0 else 1
        else:
            beta = 1
            
        # 计算相关性
        if len(strategy_daily_returns) > 1:
            mean_strategy = sum(strategy_daily_returns) / len(strategy_daily_returns)
            mean_benchmark = sum(benchmark_daily_returns) / len(benchmark_daily_returns)
            
            numerator = sum((s - mean_strategy) * (b - mean_benchmark) for s, b in zip(strategy_daily_returns, benchmark_daily_returns))
            denominator_s = sum((s - mean_strategy) ** 2 for s in strategy_daily_returns) ** 0.5
            denominator_b = sum((b - mean_benchmark) ** 2 for b in benchmark_daily_returns) ** 0.5
            
            correlation = numerator / (denominator_s * denominator_b) if denominator_s * denominator_b > 0 else 0
        else:
            correlation = 0
            
        # 计算信息比率
        if len(strategy_daily_returns) > 1:
            # 每日超额收益
            excess_returns = [s - b for s, b in zip(strategy_daily_returns, benchmark_daily_returns)]
            mean_excess = sum(excess_returns) / len(excess_returns)
            std_excess = (sum((e - mean_excess) ** 2 for e in excess_returns) / len(excess_returns)) ** 0.5
            
            information_ratio = mean_excess / std_excess * (252 ** 0.5) if std_excess > 0 else 0
        else:
            information_ratio = 0
            
        # 计算跟踪误差
        if len(strategy_daily_returns) > 1:
            # 每日超额收益的标准差
            excess_returns = [s - b for s, b in zip(strategy_daily_returns, benchmark_daily_returns)]
            mean_excess = sum(excess_returns) / len(excess_returns)
            tracking_error = (sum((e - mean_excess) ** 2 for e in excess_returns) / len(excess_returns)) ** 0.5 * (252 ** 0.5)
        else:
            tracking_error = 0
            
        # 构建比较报告
        benchmark_report = {
            "symbol": benchmark_data.index.name or "Unknown",
            "strategy_return": strategy_return,
            "benchmark_return": benchmark_return,
            "alpha": alpha,
            "beta": beta,
            "correlation": correlation,
            "information_ratio": information_ratio,
            "tracking_error": tracking_error
        }
        
        return benchmark_report
        
# 全局回测服务实例
def get_backtest_service(db: Session):
    """获取回测服务实例"""
    return BacktestEngine(db)

class BacktestService:
    """
    Service for backtesting trading strategies.
    Provides functionality to backtest strategies on historical data and analyze results.
    """
    
    def __init__(self, data_path='data/historical'):
        """
        Initialize the backtest service.
        
        Args:
            data_path (str): Path to historical data
        """
        self.data_path = data_path
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        logger.info("Backtest Service initialized")
    
    async def run_backtest(self, strategy_id, stock_code, start_date=None, end_date=None, 
                     initial_capital=100000.0, include_chart=False, parameters=None):
        """
        Run a backtest for a specific strategy and stock.
        
        Args:
            strategy_id (str): Strategy identifier
            stock_code (str): Stock code to backtest on
            start_date (str): Start date for backtest (YYYY-MM-DD)
            end_date (str): End date for backtest (YYYY-MM-DD)
            initial_capital (float): Initial capital for backtest
            include_chart (bool): Whether to include a performance chart
            parameters (dict): Custom strategy parameters
            
        Returns:
            dict: Backtest results
        """
        try:
            # Get historical data
            historical_data = await self._get_historical_data(stock_code, start_date, end_date)
            
            if historical_data.empty:
                return {"error": f"No historical data available for {stock_code}"}
            
            # Create strategy instance with custom parameters if provided
            strategy = StrategyFactory.get_strategy(strategy_id, parameters)
            
            # Generate trading signals
            signals = strategy.generate_signals(historical_data)
            
            # Run backtest with signals
            backtest_results = self._evaluate_performance(
                historical_data, 
                signals, 
                initial_capital
            )
            
            # Format results
            formatted_results = {
                "strategy_id": strategy_id,
                "stock_code": stock_code,
                "parameters": strategy.parameters,
                "performance": backtest_results,
                "period": {
                    "start": historical_data.index[0].strftime('%Y-%m-%d'),
                    "end": historical_data.index[-1].strftime('%Y-%m-%d'),
                    "days": len(historical_data)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Add chart if requested
            if include_chart:
                # chart = generate_performance_chart(
                #     historical_data,
                #     signals,
                #     title=f"{strategy.name} Backtest on {stock_code}"
                # )
                # formatted_results["chart"] = chart
                formatted_results["chart"] = "Chart generation temporarily disabled"
            
            # Save backtest results
            self._save_backtest_results(formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during backtest: {e}")
            return {"error": str(e)}
    
    async def get_available_data(self):
        """
        Get list of available historical data for backtesting.
        
        Returns:
            list: Available stock data
        """
        # In a real implementation, this would scan data directory or database
        # For this example, we'll return a mock list
        
        return [
            {"code": "000001.SZ", "name": "平安银行", "data_range": "2018-01-01 to 2023-12-31"},
            {"code": "600519.SH", "name": "贵州茅台", "data_range": "2018-01-01 to 2023-12-31"},
            {"code": "300750.SZ", "name": "宁德时代", "data_range": "2018-06-11 to 2023-12-31"},
            {"code": "601318.SH", "name": "中国平安", "data_range": "2018-01-01 to 2023-12-31"},
            {"code": "000333.SZ", "name": "美的集团", "data_range": "2018-01-01 to 2023-12-31"}
        ]
    
    async def get_backtest_history(self, limit=10):
        """
        Get history of previous backtests.
        
        Args:
            limit (int): Maximum number of history items to return
            
        Returns:
            list: Backtest history items
        """
        # In a real implementation, this would retrieve from database
        # For this example, we'll return a mock history
        
        mock_history = [
            {
                "id": "bt_001",
                "strategy_id": "ma_cross",
                "stock_code": "600519.SH",
                "date": "2023-05-10",
                "period": "2022-01-01 to 2022-12-31",
                "performance": {
                    "total_return": 0.185,
                    "win_rate": 0.65,
                    "profit_factor": 1.75,
                    "sharpe_ratio": 1.2
                }
            },
            {
                "id": "bt_002",
                "strategy_id": "rsi_strategy",
                "stock_code": "300750.SZ",
                "date": "2023-05-09",
                "period": "2022-01-01 to 2022-12-31",
                "performance": {
                    "total_return": 0.12,
                    "win_rate": 0.58,
                    "profit_factor": 1.45,
                    "sharpe_ratio": 0.9
                }
            },
            {
                "id": "bt_003",
                "strategy_id": "bollinger_bands",
                "stock_code": "000001.SZ",
                "date": "2023-05-08",
                "period": "2022-01-01 to 2022-12-31",
                "performance": {
                    "total_return": 0.095,
                    "win_rate": 0.61,
                    "profit_factor": 1.38,
                    "sharpe_ratio": 0.85
                }
            }
        ]
        
        return mock_history[:limit]
    
    def _evaluate_performance(self, data, signals, initial_capital):
        """
        Evaluate strategy performance based on signals and historical data.
        
        Args:
            data (pd.DataFrame): Historical price data
            signals (pd.Series): Trading signals (1=buy, -1=sell, 0=hold)
            initial_capital (float): Initial capital
            
        Returns:
            dict: Performance metrics
        """
        # Make a copy of data to avoid modifying original
        df = data.copy()
        
        # Create position column (1 if we have a position, 0 otherwise)
        positions = signals.shift(1).fillna(0)
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['returns'] * positions
        
        # Calculate cumulative returns
        df['cum_returns'] = (1 + df['returns']).cumprod()
        df['cum_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
        
        # Calculate portfolio value
        df['portfolio_value'] = initial_capital * df['cum_strategy_returns']
        
        # Calculate performance metrics
        total_trades = positions.diff().fillna(0).abs().sum() / 2
        winning_trades = ((positions == 1) & (df['returns'] > 0)).sum() + ((positions == -1) & (df['returns'] < 0)).sum()
        
        if total_trades > 0:
            win_rate = winning_trades / total_trades
        else:
            win_rate = 0
            
        # Calculate profit factor
        gross_profits = df.loc[df['strategy_returns'] > 0, 'strategy_returns'].sum()
        gross_losses = abs(df.loc[df['strategy_returns'] < 0, 'strategy_returns'].sum())
        
        if gross_losses > 0:
            profit_factor = gross_profits / gross_losses
        else:
            profit_factor = float('inf') if gross_profits > 0 else 0
            
        # Calculate Sharpe ratio (annualized, assuming daily data)
        risk_free_rate = 0.0
        sharpe_ratio = (df['strategy_returns'].mean() - risk_free_rate) / df['strategy_returns'].std() * np.sqrt(252) if df['strategy_returns'].std() > 0 else 0
        
        # Calculate drawdown
        rolling_max = df['portfolio_value'].cummax()
        drawdown = (df['portfolio_value'] - rolling_max) / rolling_max
        max_drawdown = abs(drawdown.min())
        
        # Calculate monthly returns
        if len(df) > 20:  # Only if we have enough data
            df['year_month'] = df.index.strftime('%Y-%m')
            monthly_returns = df.groupby('year_month')['strategy_returns'].sum()
        else:
            monthly_returns = pd.Series()
        
        # Calculate daily value at risk (VaR) at 95% confidence
        if len(df) > 10:
            var_95 = np.percentile(df['strategy_returns'], 5)
        else:
            var_95 = 0
        
        # Format monthly returns for response
        monthly_returns_formatted = {}
        for month, ret in monthly_returns.items():
            monthly_returns_formatted[month] = float(ret)
        
        return {
            'total_return': float(df['cum_strategy_returns'].iloc[-1] - 1),
            'annualized_return': float((df['cum_strategy_returns'].iloc[-1] ** (252 / len(df))) - 1) if len(df) > 0 else 0,
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'total_trades': int(total_trades),
            'var_95': float(var_95),
            'monthly_returns': monthly_returns_formatted,
            'final_capital': float(df['portfolio_value'].iloc[-1]) if len(df) > 0 else initial_capital
        }
    
    async def _get_historical_data(self, stock_code, start_date=None, end_date=None):
        """
        Get historical market data for a stock.
        
        Args:
            stock_code (str): Stock code
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Historical market data
        """
        # In a real implementation, this would fetch data from a database or API
        # For this example, we'll generate mock data
        
        # Parse date strings if provided
        if start_date:
            start = pd.to_datetime(start_date)
        else:
            start = pd.to_datetime('2022-01-01')
            
        if end_date:
            end = pd.to_datetime(end_date)
        else:
            end = pd.to_datetime('2022-12-31')
        
        # Generate mock data
        days = (end - start).days + 1
        dates = pd.date_range(start=start, periods=min(days, 252))
        
        # Use stock code to seed random generator for reproducibility
        seed = sum(ord(c) for c in stock_code)
        np.random.seed(seed)
        
        # Generate a random walk for stock prices
        close = 100 * (1 + 0.0001 * np.random.normal(0, 1, len(dates)).cumsum())
        
        # Add some trend based on stock code
        if stock_code.startswith('6'):
            # Add upward trend for stocks starting with 6
            trend_factor = 0.0002
        else:
            # Add slight downward trend for others
            trend_factor = -0.0001
            
        close = close * (1 + trend_factor * np.arange(len(dates)))
        
        high = close * (1 + np.random.uniform(0, 0.02, len(dates)))
        low = close * (1 - np.random.uniform(0, 0.02, len(dates)))
        open_price = close * (1 + np.random.normal(0, 0.01, len(dates)))
        volume = np.random.uniform(1000000, 10000000, len(dates))
        
        # Create DataFrame
        df = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        return df
    
    def _save_backtest_results(self, results):
        """
        Save backtest results for future reference.
        
        Args:
            results (dict): Backtest results
            
        Returns:
            bool: Success flag
        """
        # In a real implementation, this would save to a database
        # For this example, we'll log the save operation
        
        logger.info(f"Saved backtest results for {results['strategy_id']} on {results['stock_code']}")
        
        # Create a unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{results['strategy_id']}_{results['stock_code']}_{timestamp}.json"
        file_path = os.path.join(self.data_path, filename)
        
        # Remove chart from saved results if present (too large for JSON)
        results_to_save = results.copy()
        if 'chart' in results_to_save:
            del results_to_save['chart']
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(results_to_save, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving backtest results: {e}")
            return False 
