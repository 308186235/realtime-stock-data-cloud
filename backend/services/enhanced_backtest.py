"""
增强策略回测服务
基于Qlib回测框架的增强回测功能,提供更精确的回测指标和风险评估
注意:此模块不影响现有回测功能,提供额外的分析能力
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """回测结果数据结构"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_loss_ratio: float
    total_trades: int
    volatility: float
    calmar_ratio: float

@dataclass
class RiskMetrics:
    """风险指标数据结构"""
    var_95: float  # 95%置信度的VaR
    var_99: float  # 99%置信度的VaR
    beta: float  # 贝塔系数
    alpha: float  # 阿尔法系数
    tracking_error: float  # 跟踪误差

class EnhancedBacktestEngine:
    """增强回测引擎 - 基于Qlib思路"""
    
    def __init__(self):
        self.risk_free_rate = 0.03  # 无风险利率3%
        
    def run_enhanced_backtest(self, 
                            strategy_returns: List[float],
                            benchmark_returns: List[float] = None,
                            trade_records: List[Dict] = None,
                            initial_capital: float = 100000) -> Dict:
        """运行增强回测分析"""
        try:
            if not strategy_returns:
                raise ValueError("策略收益率数据不能为空")
            
            returns = np.array(strategy_returns)
            
            # 基础回测指标
            basic_metrics = self._calculate_basic_metrics(returns, trade_records)
            
            # 风险指标
            risk_metrics = self._calculate_risk_metrics(returns, benchmark_returns)
            
            # 综合评分
            overall_score = self._calculate_overall_score(basic_metrics, risk_metrics)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'basic_metrics': basic_metrics.__dict__,
                'risk_metrics': risk_metrics.__dict__,
                'overall_score': overall_score,
                'recommendations': self._generate_recommendations(basic_metrics, risk_metrics)
            }
            
        except Exception as e:
            logger.error(f"增强回测失败: {e}")
            return {'error': str(e)}
    
    def _calculate_basic_metrics(self, returns: np.ndarray, trade_records: List[Dict]) -> BacktestResult:
        """计算基础回测指标"""
        # 累计收益率
        cumulative_returns = np.cumprod(1 + returns) - 1
        total_return = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0
        
        # 年化收益率
        trading_days = len(returns)
        years = trading_days / 252 if trading_days > 0 else 1
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # 波动率
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        
        # 夏普比率
        excess_returns = returns - self.risk_free_rate/252
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
        
        # 最大回撤
        cumulative_wealth = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_wealth)
        drawdowns = (cumulative_wealth - running_max) / running_max
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        
        # 交易统计
        total_trades = len(trade_records) if trade_records else 0
        winning_trades = sum(1 for trade in trade_records if trade.get('profit', 0) > 0) if trade_records else 0
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏比
        if trade_records:
            profits = [trade.get('profit', 0) for trade in trade_records if trade.get('profit', 0) > 0]
            losses = [abs(trade.get('profit', 0)) for trade in trade_records if trade.get('profit', 0) < 0]
            avg_profit = np.mean(profits) if profits else 0
            avg_loss = np.mean(losses) if losses else 1
            profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 0
        else:
            profit_loss_ratio = 0
        
        # Calmar比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return BacktestResult(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            total_trades=total_trades,
            volatility=volatility,
            calmar_ratio=calmar_ratio
        )
    
    def _calculate_risk_metrics(self, returns: np.ndarray, benchmark_returns: List[float] = None) -> RiskMetrics:
        """计算风险指标"""
        # VaR计算
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        var_99 = np.percentile(returns, 1) if len(returns) > 0 else 0
        
        # 如果有基准数据,计算Beta和Alpha
        if benchmark_returns and len(benchmark_returns) == len(returns):
            benchmark_array = np.array(benchmark_returns)
            
            # Beta系数
            covariance = np.cov(returns, benchmark_array)[0, 1]
            benchmark_variance = np.var(benchmark_array)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            # Alpha系数
            benchmark_annual_return = np.mean(benchmark_array) * 252
            strategy_annual_return = np.mean(returns) * 252
            alpha = strategy_annual_return - (self.risk_free_rate + beta * (benchmark_annual_return - self.risk_free_rate))
            
            # 跟踪误差
            tracking_error = np.std(returns - benchmark_array) * np.sqrt(252)
        else:
            beta = 0
            alpha = 0
            tracking_error = 0
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            beta=beta,
            alpha=alpha,
            tracking_error=tracking_error
        )
    
    def _calculate_overall_score(self, basic_metrics: BacktestResult, risk_metrics: RiskMetrics) -> Dict:
        """计算综合评分"""
        # 收益评分 (0-100)
        return_score = min(max(basic_metrics.annual_return * 100, 0), 100)
        
        # 风险评分 (0-100, 风险越低分数越高)
        risk_score = max(100 - abs(basic_metrics.max_drawdown) * 100, 0)
        
        # 夏普比率评分
        sharpe_score = min(max(basic_metrics.sharpe_ratio * 20, 0), 100)
        
        # 胜率评分
        win_rate_score = basic_metrics.win_rate * 100
        
        # 综合评分 (加权平均)
        overall_score = (
            return_score * 0.3 +
            risk_score * 0.3 +
            sharpe_score * 0.25 +
            win_rate_score * 0.15
        )
        
        # 评级
        if overall_score >= 80:
            rating = "优秀"
        elif overall_score >= 60:
            rating = "良好"
        elif overall_score >= 40:
            rating = "一般"
        else:
            rating = "较差"
        
        return {
            'overall_score': overall_score,
            'rating': rating,
            'component_scores': {
                'return_score': return_score,
                'risk_score': risk_score,
                'sharpe_score': sharpe_score,
                'win_rate_score': win_rate_score
            }
        }
    
    def _generate_recommendations(self, basic_metrics: BacktestResult, risk_metrics: RiskMetrics) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if basic_metrics.sharpe_ratio < 1.0:
            recommendations.append("夏普比率偏低,建议优化风险收益比")
        
        if basic_metrics.max_drawdown < -0.2:
            recommendations.append("最大回撤过大,建议加强风险控制")
        
        if basic_metrics.win_rate < 0.4:
            recommendations.append("胜率较低,建议优化入场时机")
        
        if basic_metrics.profit_loss_ratio < 1.5:
            recommendations.append("盈亏比偏低,建议优化止盈止损策略")
        
        if basic_metrics.volatility > 0.3:
            recommendations.append("策略波动率较高,建议分散投资降低风险")
        
        if not recommendations:
            recommendations.append("策略表现良好,建议继续优化细节")
        
        return recommendations

# 全局实例
enhanced_backtest_engine = EnhancedBacktestEngine()

def run_enhanced_backtest(strategy_returns: List[float], 
                         benchmark_returns: List[float] = None,
                         trade_records: List[Dict] = None,
                         initial_capital: float = 100000) -> Dict:
    """运行增强回测 - 供其他模块调用"""
    return enhanced_backtest_engine.run_enhanced_backtest(
        strategy_returns, benchmark_returns, trade_records, initial_capital
    )
