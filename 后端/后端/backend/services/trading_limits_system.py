"""
交易限制系统
"""

import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class LimitType(Enum):
    """限制类型"""
    DAILY_TRADES = "daily_trades"
    DAILY_VOLUME = "daily_volume"
    POSITION_SIZE = "position_size"
    COOLING_PERIOD = "cooling_period"
    MARKET_HOURS = "market_hours"

@dataclass
class TradingLimit:
    """交易限制"""
    limit_type: LimitType
    max_value: float
    current_value: float
    reset_time: float
    enabled: bool = True

class TradingLimitsSystem:
    """交易限制系统"""

    def __init__(self):
        self.limits: Dict[LimitType, TradingLimit] = {}
        self.trade_history = []
        self.last_trade_time = 0
        self._initialize_limits()

    def _initialize_limits(self):
        """初始化限制"""
        current_time = time.time()

        # 每日交易次数限制
        self.limits[LimitType.DAILY_TRADES] = TradingLimit(
            limit_type=LimitType.DAILY_TRADES,
            max_value=50,  # 每日最多50笔交易
            current_value=0,
            reset_time=self._get_next_market_open()
        )

        # 每日交易金额限制
        self.limits[LimitType.DAILY_VOLUME] = TradingLimit(
            limit_type=LimitType.DAILY_VOLUME,
            max_value=500000,  # 每日最多50万交易额
            current_value=0,
            reset_time=self._get_next_market_open()
        )

        # 单笔仓位限制
        self.limits[LimitType.POSITION_SIZE] = TradingLimit(
            limit_type=LimitType.POSITION_SIZE,
            max_value=100000,  # 单笔最多10万
            current_value=0,
            reset_time=current_time + 86400
        )

        # 交易冷却期
        self.limits[LimitType.COOLING_PERIOD] = TradingLimit(
            limit_type=LimitType.COOLING_PERIOD,
            max_value=60,  # 60秒冷却期
            current_value=0,
            reset_time=current_time
        )

    def _get_next_market_open(self) -> float:
        """获取下一个交易日开盘时间"""
        # 简化实现,实际应该考虑节假日
        import datetime
        now = datetime.datetime.now()
        next_day = now.replace(hour=9, minute=30, second=0, microsecond=0) + datetime.timedelta(days=1)
        return next_day.timestamp()

    def check_trading_allowed(self, trade_amount: float) -> tuple[bool, str]:
        """检查是否允许交易"""
        current_time = time.time()

        # 检查市场时间
        if not self._is_market_hours():
            return False, "非交易时间"

        # 检查冷却期
        if current_time - self.last_trade_time < self.limits[LimitType.COOLING_PERIOD].max_value:
            remaining = self.limits[LimitType.COOLING_PERIOD].max_value - (current_time - self.last_trade_time)
            return False, f"冷却期未结束,剩余 {remaining:.0f} 秒"

        # 检查每日交易次数
        self._reset_daily_limits_if_needed()
        daily_trades_limit = self.limits[LimitType.DAILY_TRADES]
        if daily_trades_limit.current_value >= daily_trades_limit.max_value:
            return False, f"每日交易次数已达上限 {daily_trades_limit.max_value}"

        # 检查每日交易金额
        daily_volume_limit = self.limits[LimitType.DAILY_VOLUME]
        if daily_volume_limit.current_value + trade_amount > daily_volume_limit.max_value:
            remaining = daily_volume_limit.max_value - daily_volume_limit.current_value
            return False, f"每日交易金额将超限,剩余额度 {remaining:.2f}"

        # 检查单笔仓位限制
        position_limit = self.limits[LimitType.POSITION_SIZE]
        if trade_amount > position_limit.max_value:
            return False, f"单笔交易金额超限 {trade_amount:.2f} > {position_limit.max_value:.2f}"

        return True, "交易检查通过"

    def _is_market_hours(self) -> bool:
        """检查是否在交易时间内"""
        import datetime
        now = datetime.datetime.now()

        # 周末不交易
        if now.weekday() >= 5:
            return False

        # 交易时间:9:30-11:30, 13:00-15:00
        morning_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
        morning_end = now.replace(hour=11, minute=30, second=0, microsecond=0)
        afternoon_start = now.replace(hour=13, minute=0, second=0, microsecond=0)
        afternoon_end = now.replace(hour=15, minute=0, second=0, microsecond=0)

        return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

    def _reset_daily_limits_if_needed(self):
        """重置每日限制"""
        current_time = time.time()

        for limit_type in [LimitType.DAILY_TRADES, LimitType.DAILY_VOLUME]:
            limit = self.limits[limit_type]
            if current_time >= limit.reset_time:
                limit.current_value = 0
                limit.reset_time = self._get_next_market_open()
                logger.info(f"重置每日限制: {limit_type.value}")

    def record_trade(self, trade_amount: float):
        """记录交易"""
        current_time = time.time()

        # 更新限制计数
        self.limits[LimitType.DAILY_TRADES].current_value += 1
        self.limits[LimitType.DAILY_VOLUME].current_value += trade_amount
        self.last_trade_time = current_time

        # 记录交易历史
        self.trade_history.append({
            "timestamp": current_time,
            "amount": trade_amount
        })

        logger.info(f"记录交易: 金额 {trade_amount:.2f}, 今日第 {self.limits[LimitType.DAILY_TRADES].current_value} 笔")

    def get_limits_status(self) -> Dict:
        """获取限制状态"""
        self._reset_daily_limits_if_needed()

        return {
            limit_type.value: {
                "max_value": limit.max_value,
                "current_value": limit.current_value,
                "usage_pct": (limit.current_value / limit.max_value) * 100 if limit.max_value > 0 else 0,
                "enabled": limit.enabled
            }
            for limit_type, limit in self.limits.items()
        }

# 全局交易限制系统实例
trading_limits_system = TradingLimitsSystem()
