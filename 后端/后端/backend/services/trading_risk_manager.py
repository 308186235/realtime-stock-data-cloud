"""
交易风险管理模块
"""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Position:
    """持仓信息"""
    stock_code: str
    quantity: int
    entry_price: float
    current_price: float
    entry_time: float
    stop_loss_price: float
    take_profit_price: float

    @property
    def profit_loss_pct(self) -> float:
        """盈亏百分比"""
        return (self.current_price - self.entry_price) / self.entry_price

    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price

@dataclass
class RiskMetrics:
    """风险指标"""
    total_exposure: float
    max_position_risk: float
    portfolio_var: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float

class TradingRiskManager:
    """交易风险管理器"""

    def __init__(self, config_file: str = "backend/config/trading_strategy_config.json"):
        self.config = self._load_config(config_file)
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = 0.0
        self.total_capital = 100000.0  # 默认总资金
        self.trade_history = []
        self.risk_alerts = []

    def _load_config(self, config_file: str) -> Dict:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载风险配置失败: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "risk_management": {
                "max_position_size": 0.1,
                "max_daily_loss": 0.05,
                "stop_loss_pct": 0.08,
                "take_profit_pct": 0.15,
                "max_drawdown": 0.20
            },
            "trading_rules": {
                "min_trade_amount": 1000,
                "max_trade_amount": 50000,
                "max_positions": 10,
                "cooling_period": 300
            }
        }

    def check_trade_risk(self, stock_code: str, quantity: int, price: float,
                        trade_type: str) -> Tuple[bool, str]:
        """检查交易风险"""

        # 1. 检查仓位限制
        position_risk = self._check_position_risk(stock_code, quantity, price)
        if not position_risk[0]:
            return position_risk

        # 2. 检查资金限制
        capital_risk = self._check_capital_risk(quantity, price)
        if not capital_risk[0]:
            return capital_risk

        # 3. 检查日亏损限制
        daily_loss_risk = self._check_daily_loss_risk()
        if not daily_loss_risk[0]:
            return daily_loss_risk

        # 4. 检查市场条件
        market_risk = self._check_market_conditions(stock_code, price)
        if not market_risk[0]:
            return market_risk

        return True, "风险检查通过"

    def _check_position_risk(self, stock_code: str, quantity: int,
                           price: float) -> Tuple[bool, str]:
        """检查仓位风险"""
        trade_value = quantity * price
        max_position_value = self.total_capital * self.config["risk_management"]["max_position_size"]

        if trade_value > max_position_value:
            return False, f"单笔交易金额超限: {trade_value:.2f} > {max_position_value:.2f}"

        # 检查持仓数量限制
        if len(self.positions) >= self.config["trading_rules"]["max_positions"]:
            return False, f"持仓数量超限: {len(self.positions)}"

        return True, "仓位风险检查通过"

    def _check_capital_risk(self, quantity: int, price: float) -> Tuple[bool, str]:
        """检查资金风险"""
        trade_amount = quantity * price
        min_amount = self.config["trading_rules"]["min_trade_amount"]
        max_amount = self.config["trading_rules"]["max_trade_amount"]

        if trade_amount < min_amount:
            return False, f"交易金额过小: {trade_amount:.2f} < {min_amount}"

        if trade_amount > max_amount:
            return False, f"交易金额过大: {trade_amount:.2f} > {max_amount}"

        return True, "资金风险检查通过"

    def _check_daily_loss_risk(self) -> Tuple[bool, str]:
        """检查日亏损风险"""
        max_daily_loss = self.total_capital * self.config["risk_management"]["max_daily_loss"]

        if abs(self.daily_pnl) > max_daily_loss and self.daily_pnl < 0:
            return False, f"日亏损超限: {self.daily_pnl:.2f} < -{max_daily_loss:.2f}"

        return True, "日亏损风险检查通过"

    def _check_market_conditions(self, stock_code: str, price: float) -> Tuple[bool, str]:
        """检查市场条件"""
        # 这里可以添加市场条件检查逻辑
        # 例如:波动率,成交量,技术指标等
        return True, "市场条件检查通过"

    def calculate_stop_loss_price(self, entry_price: float, trade_type: str) -> float:
        """计算止损价格"""
        stop_loss_pct = self.config["risk_management"]["stop_loss_pct"]

        if trade_type.lower() == "buy":
            return entry_price * (1 - stop_loss_pct)
        else:  # sell
            return entry_price * (1 + stop_loss_pct)

    def calculate_take_profit_price(self, entry_price: float, trade_type: str) -> float:
        """计算止盈价格"""
        take_profit_pct = self.config["risk_management"]["take_profit_pct"]

        if trade_type.lower() == "buy":
            return entry_price * (1 + take_profit_pct)
        else:  # sell
            return entry_price * (1 - take_profit_pct)

    def add_position(self, stock_code: str, quantity: int, entry_price: float):
        """添加持仓"""
        stop_loss_price = self.calculate_stop_loss_price(entry_price, "buy")
        take_profit_price = self.calculate_take_profit_price(entry_price, "buy")

        position = Position(
            stock_code=stock_code,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            entry_time=time.time(),
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )

        self.positions[stock_code] = position
        logger.info(f"添加持仓: {stock_code}, 数量: {quantity}, 价格: {entry_price}")

    def update_position_price(self, stock_code: str, current_price: float):
        """更新持仓价格"""
        if stock_code in self.positions:
            self.positions[stock_code].current_price = current_price

    def check_stop_loss_trigger(self, stock_code: str) -> bool:
        """检查止损触发"""
        if stock_code not in self.positions:
            return False

        position = self.positions[stock_code]
        return position.current_price <= position.stop_loss_price

    def check_take_profit_trigger(self, stock_code: str) -> bool:
        """检查止盈触发"""
        if stock_code not in self.positions:
            return False

        position = self.positions[stock_code]
        return position.current_price >= position.take_profit_price

    def get_risk_metrics(self) -> RiskMetrics:
        """获取风险指标"""
        total_exposure = sum(pos.market_value for pos in self.positions.values())
        max_position_risk = max([pos.market_value / self.total_capital
                               for pos in self.positions.values()], default=0)

        return RiskMetrics(
            total_exposure=total_exposure,
            max_position_risk=max_position_risk,
            portfolio_var=0.0,  # 需要历史数据计算
            sharpe_ratio=0.0,   # 需要历史数据计算
            max_drawdown=0.0,   # 需要历史数据计算
            win_rate=0.0        # 需要历史数据计算
        )

    def generate_risk_report(self) -> Dict:
        """生成风险报告"""
        metrics = self.get_risk_metrics()

        return {
            "timestamp": time.time(),
            "total_positions": len(self.positions),
            "total_exposure": metrics.total_exposure,
            "exposure_ratio": metrics.total_exposure / self.total_capital,
            "max_position_risk": metrics.max_position_risk,
            "daily_pnl": self.daily_pnl,
            "risk_alerts": self.risk_alerts,
            "positions": [
                {
                    "stock_code": pos.stock_code,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "profit_loss_pct": pos.profit_loss_pct,
                    "market_value": pos.market_value
                }
                for pos in self.positions.values()
            ]
        }

# 全局风险管理器实例
trading_risk_manager = TradingRiskManager()
