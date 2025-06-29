import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class RiskManager:
    """风险管理器,提供止损,资金管理和风险控制功能"""
    
    def __init__(self, initial_capital: float, risk_params: Optional[Dict] = None):
        """
        初始化风险管理器
        
        参数:
        - initial_capital: 初始资金
        - risk_params: 风险参数字典
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # 默认风险参数
        self.default_risk_params = {
            'max_position_size': 0.2,         # 单一持仓最大比例
            'max_drawdown': 0.1,              # 最大可接受回撤
            'fixed_stop_loss': 0.05,          # 固定止损比例
            'trailing_stop_loss': 0.08,       # 跟踪止损比例
            'time_stop_loss': 10,             # 时间止损天数
            'position_sizing_method': 'risk',  # 仓位计算方法: risk, equal, kelly
            'risk_per_trade': 0.02,           # 每笔交易风险比例
            'volatility_lookback': 20,        # 波动率计算回溯期
            'kelly_fraction': 0.5             # Kelly公式分数
        }
        
        # 更新风险参数
        self.risk_params = {**self.default_risk_params, **(risk_params or {})}
        
        # 初始化持仓和风险记录
        self.positions = {}  # 当前持仓 {symbol: {'entry_price': 价格, 'entry_date': 日期, 'size': 数量, ...}}
        self.risk_records = []  # 风险记录
    
    def update_capital(self, new_capital: float):
        """更新当前资金"""
        self.current_capital = new_capital
        
        # 记录回撤
        drawdown = 1 - (self.current_capital / self.initial_capital)
        if drawdown > 0:
            self.risk_records.append({
                'type': 'drawdown',
                'value': drawdown,
                'capital': self.current_capital,
                'timestamp': pd.Timestamp.now()
            })
    
    def calculate_position_size(self, symbol: str, current_price: float, stop_price: float = None) -> Dict:
        """
        计算推荐的仓位大小
        
        参数:
        - symbol: 交易品种代码
        - current_price: 当前价格
        - stop_price: 止损价格,如果未提供则使用固定止损比例计算
        
        返回:
        - 字典,包含建议的仓位大小,金额和比例
        """
        # 计算止损价格(如果未提供)
        if stop_price is None:
            stop_price = current_price * (1 - self.risk_params['fixed_stop_loss'])
        
        # 计算风险金额(每股)
        risk_per_share = abs(current_price - stop_price)
        if risk_per_share <= 0:
            logger.warning(f"止损价格无效: {stop_price},使用默认止损")
            risk_per_share = current_price * self.risk_params['fixed_stop_loss']
        
        # 根据仓位计算方法确定头寸大小
        method = self.risk_params['position_sizing_method']
        
        if method == 'risk':
            # 基于风险的头寸计算
            risk_amount = self.current_capital * self.risk_params['risk_per_trade']
            shares = int(risk_amount / risk_per_share)
            
        elif method == 'equal':
            # 等额头寸计算
            position_amount = self.current_capital * self.risk_params['max_position_size']
            shares = int(position_amount / current_price)
            
        elif method == 'kelly':
            # 凯利公式计算(简化版)
            # 需要历史胜率和赔率数据,这里使用默认值
            win_rate = 0.55  # 假设的胜率
            win_loss_ratio = 2.0  # 假设的赔率
            
            # 计算凯利比例
            kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
            kelly_pct = max(0, kelly_pct * self.risk_params['kelly_fraction'])  # 应用凯利分数
            
            position_amount = self.current_capital * kelly_pct
            shares = int(position_amount / current_price)
            
        else:
            # 默认使用最大仓位比例
            position_amount = self.current_capital * self.risk_params['max_position_size']
            shares = int(position_amount / current_price)
        
        # 确保不超过最大仓位限制
        max_position_amount = self.current_capital * self.risk_params['max_position_size']
        if shares * current_price > max_position_amount:
            shares = int(max_position_amount / current_price)
        
        # 确保至少买入1股
        shares = max(1, shares)
        
        return {
            'symbol': symbol,
            'shares': shares,
            'amount': shares * current_price,
            'percentage': (shares * current_price) / self.current_capital,
            'stop_price': stop_price,
            'risk_amount': shares * risk_per_share,
            'risk_percentage': (shares * risk_per_share) / self.current_capital
        }
    
    def check_stop_loss(self, symbol: str, current_price: float, current_date: pd.Timestamp) -> Tuple[bool, str]:
        """
        检查是否触发止损
        
        参数:
        - symbol: 交易品种代码
        - current_price: 当前价格
        - current_date: 当前日期
        
        返回:
        - (是否止损, 止损原因)
        """
        if symbol not in self.positions:
            return False, ""
        
        position = self.positions[symbol]
        
        # 固定止损检查
        if 'stop_price' in position and current_price <= position['stop_price']:
            return True, "fixed_stop_loss"
        
        # 跟踪止损检查
        if 'highest_price' in position:
            trailing_stop = position['highest_price'] * (1 - self.risk_params['trailing_stop_loss'])
            if current_price <= trailing_stop:
                return True, "trailing_stop_loss"
        
        # 时间止损检查
        if 'entry_date' in position:
            holding_days = (current_date - position['entry_date']).days
            if holding_days >= self.risk_params['time_stop_loss']:
                return True, "time_stop_loss"
        
        return False, ""
    
    def update_position(self, symbol: str, current_price: float, current_date: pd.Timestamp, shares: int, is_buy: bool):
        """
        更新持仓信息
        
        参数:
        - symbol: 交易品种代码
        - current_price: 当前价格
        - current_date: 当前日期
        - shares: 交易数量
        - is_buy: 是否买入
        """
        if is_buy:
            if symbol not in self.positions:
                # 新建仓位
                self.positions[symbol] = {
                    'entry_price': current_price,
                    'entry_date': current_date,
                    'shares': shares,
                    'highest_price': current_price,
                    'stop_price': current_price * (1 - self.risk_params['fixed_stop_loss'])
                }
            else:
                # 加仓,更新平均成本
                position = self.positions[symbol]
                total_shares = position['shares'] + shares
                new_entry_price = (position['entry_price'] * position['shares'] + current_price * shares) / total_shares
                
                self.positions[symbol].update({
                    'entry_price': new_entry_price,
                    'shares': total_shares,
                    'highest_price': max(position['highest_price'], current_price)
                })
        else:
            # 减仓或平仓
            if symbol in self.positions:
                position = self.positions[symbol]
                if shares >= position['shares']:
                    # 平仓
                    del self.positions[symbol]
                else:
                    # 减仓
                    self.positions[symbol]['shares'] -= shares
    
    def update_market_data(self, symbol: str, current_price: float):
        """更新市场数据,用于跟踪止损等"""
        if symbol in self.positions:
            if current_price > self.positions[symbol]['highest_price']:
                self.positions[symbol]['highest_price'] = current_price
    
    def check_portfolio_risk(self) -> Tuple[bool, str]:
        """
        检查整体投资组合风险
        
        返回:
        - (是否需要降低风险, 原因)
        """
        # 检查总体回撤是否超过限制
        drawdown = 1 - (self.current_capital / self.initial_capital)
        if drawdown > self.risk_params['max_drawdown']:
            return True, f"最大回撤超过限制: {drawdown:.2%} > {self.risk_params['max_drawdown']:.2%}"
        
        # 检查持仓集中度
        total_position_value = sum(p['shares'] * p['entry_price'] for p in self.positions.values())
        if total_position_value > self.current_capital * 0.8:  # 假设最大总仓位为80%
            return True, f"总持仓比例过高: {total_position_value/self.current_capital:.2%} > 80%"
        
        return False, ""
    
    def get_risk_adjustment_action(self) -> Dict:
        """
        获取风险调整建议
        
        返回:
        - 风险调整动作
        """
        needs_adjustment, reason = self.check_portfolio_risk()
        
        if not needs_adjustment:
            return {'action': 'none', 'reason': '风险在可接受范围内'}
        
        # 根据风险情况给出调整建议
        if '回撤' in reason:
            return {
                'action': 'reduce_exposure',
                'reason': reason,
                'suggestion': '建议减少总体仓位,降低风险敞口',
                'reduction': 0.5  # 建议减仓50%
            }
        elif '持仓比例' in reason:
            return {
                'action': 'diversify',
                'reason': reason,
                'suggestion': '建议分散持仓,降低集中度风险',
                'max_per_position': 0.1  # 建议单一持仓不超过10%
            }
        
        return {
            'action': 'review',
            'reason': reason,
            'suggestion': '建议审查策略并调整风险参数'
        }
    
    def calculate_risk_metrics(self, equity_curve: pd.DataFrame) -> Dict:
        """
        计算风险指标
        
        参数:
        - equity_curve: 权益曲线DataFrame
        
        返回:
        - 风险指标字典
        """
        if equity_curve.empty:
            return {}
        
        # 计算日收益率
        if 'daily_return' not in equity_curve.columns:
            equity_curve['daily_return'] = equity_curve['equity'].pct_change()
        
        daily_returns = equity_curve['daily_return'].dropna()
        
        if len(daily_returns) < 2:
            return {
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'volatility': 0
            }
        
        # 计算最大回撤
        equity_values = equity_curve['equity'].values
        peak = np.maximum.accumulate(equity_values)
        drawdown = 1 - equity_values / peak
        max_drawdown = np.max(drawdown)
        
        # 计算年化收益率
        # 安全地处理索引类型
        if isinstance(equity_curve.index, pd.DatetimeIndex):
            # 日期索引
            total_days = (equity_curve.index[-1] - equity_curve.index[0]).days
        else:
            # 非日期索引,假设每行是一天
            total_days = len(equity_curve) - 1
            
        if total_days < 1:
            total_days = 1
        annual_return = ((equity_values[-1] / equity_values[0]) ** (365 / total_days)) - 1
        
        # 计算波动率
        volatility = daily_returns.std() * np.sqrt(252)
        
        # 计算Sharpe比率(年化)
        risk_free_rate = 0.0
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 计算Sortino比率(只考虑下行波动率)
        downside_returns = daily_returns[daily_returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0.0001
        sortino_ratio = (annual_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
        
        # 计算Calmar比率(年化收益率/最大回撤)
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'max_drawdown': max_drawdown,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'risk_free_rate': risk_free_rate
        } 
