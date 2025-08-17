#!/usr/bin/env python3
"""
增强交易策略风险控制
"""

import os
import shutil
import re
import json
from datetime import datetime


class TradingRiskEnhancer:
    """交易风险控制增强器"""

    def __init__(self):
        self.backup_dir = f"trading_risk_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.enhanced_files = []

    def enhance_all_risk_controls(self):
        """增强所有风险控制"""
        print("🛡️ 增强交易策略风险控制")
        print("=" * 50)

        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)

        # 1. 增强止损机制
        self._enhance_stop_loss_mechanism()

        # 2. 优化策略参数配置
        self._optimize_strategy_parameters()

        # 3. 添加风险管理模块
        self._add_risk_management_module()

        # 4. 创建交易限制系统
        self._create_trading_limits_system()

        # 5. 实现仓位管理
        self._implement_position_management()

        print(f"\n✅ 交易风险控制增强完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print(f"🛡️ 增强了 {len(self.enhanced_files)} 个文件")

    def _enhance_stop_loss_mechanism(self):
        """增强止损机制"""
        print("\n🛡️ 增强止损机制...")

        # 需要增强止损的文件
        trading_files = [
            'auto_cleanup_trading_agent.py',
            'backend/ai/agent_system.py',
            'backend/services/trading_service.py'
        ]

        for file_path in trading_files:
            if os.path.exists(file_path):
                self._enhance_stop_loss_in_file(file_path)

    def _optimize_strategy_parameters(self):
        """优化策略参数配置"""
        print("\n⚙️ 优化策略参数配置...")

        # 创建策略参数配置文件
        strategy_config = {
            "risk_management": {
                "max_position_size": 0.1,  # 最大仓位比例10%
                "max_daily_loss": 0.05,    # 最大日亏损5%
                "stop_loss_pct": 0.08,     # 止损比例8%
                "take_profit_pct": 0.15,   # 止盈比例15%
                "max_drawdown": 0.20       # 最大回撤20%
            },
            "trading_rules": {
                "min_trade_amount": 1000,   # 最小交易金额
                "max_trade_amount": 50000,  # 最大交易金额
                "max_positions": 10,        # 最大持仓数量
                "cooling_period": 300       # 冷却期(秒)
            },
            "market_conditions": {
                "volatility_threshold": 0.05,  # 波动率阈值
                "volume_threshold": 1000000,   # 成交量阈值
                "price_change_limit": 0.10     # 价格变动限制
            }
        }

        config_file = "backend/config/trading_strategy_config.json"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(strategy_config, f, indent=2, ensure_ascii=False)

        self.enhanced_files.append(config_file)
        print(f"✅ 创建策略配置: {config_file}")

    def _add_risk_management_module(self):
        """添加风险管理模块"""
        print("\n🛡️ 添加风险管理模块...")

        risk_manager_code = '''"""
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
'''

        risk_manager_file = "backend/services/trading_risk_manager.py"
        os.makedirs(os.path.dirname(risk_manager_file), exist_ok=True)

        with open(risk_manager_file, 'w', encoding='utf-8') as f:
            f.write(risk_manager_code)

        self.enhanced_files.append(risk_manager_file)
        print(f"✅ 创建风险管理模块: {risk_manager_file}")

    def _backup_file(self, file_path: str):
        """备份文件"""
        if not os.path.exists(file_path):
            return

        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"⚠️ 备份失败 {file_path}: {e}")

    def _enhance_stop_loss_in_file(self, file_path: str):
        """在文件中增强止损机制"""
        try:
            self._backup_file(file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 添加风险管理导入
            if 'from backend.services.trading_risk_manager import trading_risk_manager' not in content:
                import_line = 'from backend.services.trading_risk_manager import trading_risk_manager\n'

                # 在其他导入语句后添加
                if 'import ' in content:
                    lines = content.split('\n')
                    import_index = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            import_index = i

                    if import_index >= 0:
                        lines.insert(import_index + 1, import_line.strip())
                        content = '\n'.join(lines)

            # 增强交易决策函数
            if 'def consider_buy(' in content or 'def consider_sell(' in content:
                # 添加风险检查逻辑
                risk_check_code = '''
        # 风险检查
        risk_check_result = trading_risk_manager.check_trade_risk(
            stock_code=code,
            quantity=quantity,
            price=current_price,
            trade_type="buy"
        )

        if not risk_check_result[0]:
            logger.warning(f"交易风险检查失败: {risk_check_result[1]}")
            return False

        # 计算止损和止盈价格
        stop_loss_price = trading_risk_manager.calculate_stop_loss_price(current_price, "buy")
        take_profit_price = trading_risk_manager.calculate_take_profit_price(current_price, "buy")

        logger.info(f"风险控制 - 止损价: {stop_loss_price:.2f}, 止盈价: {take_profit_price:.2f}")
'''

                # 在交易决策函数中添加风险检查
                content = re.sub(
                    r'(def consider_buy\([^)]*\):[^{]*?)(if [^:]*:)',
                    r'\1' + risk_check_code + r'\n        \2',
                    content,
                    flags=re.DOTALL
                )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.enhanced_files.append(file_path)
            print(f"✅ 增强止损机制: {file_path}")

        except Exception as e:
            print(f"⚠️ 增强止损机制失败 {file_path}: {e}")

    def _create_trading_limits_system(self):
        """创建交易限制系统"""
        print("\n🚫 创建交易限制系统...")

        trading_limits_code = '''"""
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
'''

        limits_file = "backend/services/trading_limits_system.py"
        os.makedirs(os.path.dirname(limits_file), exist_ok=True)

        with open(limits_file, 'w', encoding='utf-8') as f:
            f.write(trading_limits_code)

        self.enhanced_files.append(limits_file)
        print(f"✅ 创建交易限制系统: {limits_file}")

    def _implement_position_management(self):
        """实现仓位管理"""
        print("\n📊 实现仓位管理...")

        position_manager_code = '''"""
仓位管理系统
"""

import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PositionType(Enum):
    """仓位类型"""
    LONG = "long"   # 多头
    SHORT = "short" # 空头

@dataclass
class PositionInfo:
    """仓位信息"""
    stock_code: str
    position_type: PositionType
    quantity: int
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    entry_time: float
    last_update_time: float

class PositionManager:
    """仓位管理器"""

    def __init__(self, total_capital: float = 100000):
        self.total_capital = total_capital
        self.positions: Dict[str, PositionInfo] = {}
        self.cash_balance = total_capital
        self.reserved_cash = 0  # 预留现金

    def calculate_position_size(self, stock_code: str, price: float,
                              risk_pct: float = 0.02) -> int:
        """计算仓位大小"""
        # 基于风险百分比计算仓位
        risk_amount = self.total_capital * risk_pct

        # 假设止损比例为8%
        stop_loss_pct = 0.08
        position_value = risk_amount / stop_loss_pct

        # 计算股票数量(手数,100股为一手)
        quantity = int(position_value / price / 100) * 100

        # 确保不超过可用资金
        max_quantity = int(self.cash_balance / price / 100) * 100
        quantity = min(quantity, max_quantity)

        logger.info(f"计算仓位 {stock_code}: 风险金额 {risk_amount:.2f}, 建议数量 {quantity}")
        return quantity

    def add_position(self, stock_code: str, quantity: int, price: float,
                    position_type: PositionType = PositionType.LONG) -> bool:
        """添加仓位"""
        trade_value = quantity * price

        # 检查资金是否充足
        if trade_value > self.cash_balance:
            logger.error(f"资金不足: 需要 {trade_value:.2f}, 可用 {self.cash_balance:.2f}")
            return False

        current_time = time.time()

        if stock_code in self.positions:
            # 更新现有仓位
            existing_pos = self.positions[stock_code]
            total_quantity = existing_pos.quantity + quantity
            total_value = existing_pos.quantity * existing_pos.avg_price + trade_value
            new_avg_price = total_value / total_quantity

            existing_pos.quantity = total_quantity
            existing_pos.avg_price = new_avg_price
            existing_pos.current_price = price
            existing_pos.market_value = total_quantity * price
            existing_pos.last_update_time = current_time

            logger.info(f"更新仓位 {stock_code}: 数量 {total_quantity}, 均价 {new_avg_price:.2f}")
        else:
            # 创建新仓位
            position = PositionInfo(
                stock_code=stock_code,
                position_type=position_type,
                quantity=quantity,
                avg_price=price,
                current_price=price,
                market_value=trade_value,
                unrealized_pnl=0,
                realized_pnl=0,
                entry_time=current_time,
                last_update_time=current_time
            )

            self.positions[stock_code] = position
            logger.info(f"新建仓位 {stock_code}: 数量 {quantity}, 价格 {price:.2f}")

        # 更新现金余额
        self.cash_balance -= trade_value
        return True

    def reduce_position(self, stock_code: str, quantity: int, price: float) -> bool:
        """减少仓位"""
        if stock_code not in self.positions:
            logger.error(f"仓位不存在: {stock_code}")
            return False

        position = self.positions[stock_code]

        if quantity > position.quantity:
            logger.error(f"减仓数量超过持仓: {quantity} > {position.quantity}")
            return False

        # 计算实现盈亏
        realized_pnl = (price - position.avg_price) * quantity
        position.realized_pnl += realized_pnl

        # 更新仓位
        position.quantity -= quantity
        position.current_price = price
        position.market_value = position.quantity * price
        position.last_update_time = time.time()

        # 更新现金余额
        self.cash_balance += quantity * price

        # 如果仓位清零,删除记录
        if position.quantity == 0:
            del self.positions[stock_code]
            logger.info(f"清仓 {stock_code}: 实现盈亏 {realized_pnl:.2f}")
        else:
            logger.info(f"减仓 {stock_code}: 数量 {quantity}, 实现盈亏 {realized_pnl:.2f}")

        return True

    def update_prices(self, price_data: Dict[str, float]):
        """更新价格数据"""
        for stock_code, price in price_data.items():
            if stock_code in self.positions:
                position = self.positions[stock_code]
                position.current_price = price
                position.market_value = position.quantity * price
                position.unrealized_pnl = (price - position.avg_price) * position.quantity
                position.last_update_time = time.time()

    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        total_market_value = sum(pos.market_value for pos in self.positions.values())
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())

        return {
            "total_capital": self.total_capital,
            "cash_balance": self.cash_balance,
            "total_market_value": total_market_value,
            "total_assets": self.cash_balance + total_market_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_pnl": total_unrealized_pnl + total_realized_pnl,
            "position_count": len(self.positions),
            "asset_allocation": {
                "cash_pct": (self.cash_balance / self.total_capital) * 100,
                "stock_pct": (total_market_value / self.total_capital) * 100
            }
        }

    def get_position_details(self) -> List[Dict]:
        """获取仓位详情"""
        return [
            {
                "stock_code": pos.stock_code,
                "position_type": pos.position_type.value,
                "quantity": pos.quantity,
                "avg_price": pos.avg_price,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_pct": (pos.unrealized_pnl / (pos.avg_price * pos.quantity)) * 100,
                "weight": (pos.market_value / self.total_capital) * 100
            }
            for pos in self.positions.values()
        ]

    def check_position_limits(self, stock_code: str, quantity: int, price: float) -> Tuple[bool, str]:
        """检查仓位限制"""
        trade_value = quantity * price

        # 检查单股仓位限制(不超过总资金的10%)
        max_single_position = self.total_capital * 0.1
        current_value = self.positions.get(stock_code, PositionInfo("", PositionType.LONG, 0, 0, 0, 0, 0, 0, 0, 0)).market_value

        if current_value + trade_value > max_single_position:
            return False, f"单股仓位超限: {current_value + trade_value:.2f} > {max_single_position:.2f}"

        # 检查总仓位限制(不超过总资金的80%)
        total_position_value = sum(pos.market_value for pos in self.positions.values())
        max_total_position = self.total_capital * 0.8

        if total_position_value + trade_value > max_total_position:
            return False, f"总仓位超限: {total_position_value + trade_value:.2f} > {max_total_position:.2f}"

        return True, "仓位检查通过"

# 全局仓位管理器实例
position_manager = PositionManager()
'''

        position_file = "backend/services/position_manager.py"
        os.makedirs(os.path.dirname(position_file), exist_ok=True)

        with open(position_file, 'w', encoding='utf-8') as f:
            f.write(position_manager_code)

        self.enhanced_files.append(position_file)
        print(f"✅ 创建仓位管理系统: {position_file}")

if __name__ == "__main__":
    enhancer = TradingRiskEnhancer()
    enhancer.enhance_all_risk_controls()
