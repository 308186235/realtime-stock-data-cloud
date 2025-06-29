from datetime import datetime, timedelta
import numpy as np
from typing import Dict

class OrderEngine:
    """
    高频日内交易订单引擎
    新增功能:
    - 实时滑点计算
    - 高频交易优化
    - 尾盘交易风控
    """
    
    def __init__(self):
        self.open_orders = {}
        self.slippage_model = SlippageModel()
        self.volatility_threshold = 0.15
        
    async def execute_intraday_order(self, order: Dict):
        """执行日内订单(T+0)"""
        # 实时计算滑点
        slippage = self.slippage_model.calculate(
            symbol=order['symbol'],
            quantity=order['quantity'],
            order_type=order['type']
        )
        
        # 高频交易优化(每3秒刷新一次报价)
        while True:
            best_price = self._get_best_price(order['symbol'])
            
            # 尾盘交易风控(收盘前30分钟)
            if self._is_close_period():
                if self._check_volatility(order['symbol']):
                    order['quantity'] *= 0.5
                
            # 执行逻辑
            if order['type'] == 'LIMIT':
                if best_price >= order['price']:
                    return self._fill_order(order, best_price - slippage)
            
            await asyncio.sleep(3)

    class SlippageModel:
        """实时滑点计算模型(基于市场深度和波动率)"""
        def calculate(self, symbol: str, quantity: float):
            # 结合市场深度,波动率和时间因子计算滑点
            base_slippage = (quantity / avg_depth) * bid_ask_spread
            volatility_factor = 1 + predicted_volatility * 0.5
            time_factor = 1.2 if self._is_close_period() else 1.0
            return base_slippage * volatility_factor * time_factor
        def __init__(self):
            self.historical_slippage = {}
            
        def calculate(self, symbol: str, quantity: float, order_type: str) -> float:
            # 获取实时市场深度数据
            bid_ask_spread = MarketData.get_bid_ask_spread(symbol)
            
            # 计算基础滑点(根据订单量占市场深度的比例)
            base_slippage = (quantity / MarketData.get_avg_depth(symbol)) * bid_ask_spread
            
            # 波动率加成因子(使用GARCH模型预测波动率)
            volatility_factor = 1 + RiskEngine.get_volatility(symbol, window=15) * 0.5
            
            # 时间衰减因子(尾盘时段增加滑点)
            time_factor = 1.2 if self._is_close_period() else 1.0
            
            return round(base_slippage * volatility_factor * time_factor, 4)
        
        def _is_close_period(self):
            now = datetime.now().time()
            return now >= time(14, 30) and now <= time(15, 0)

    def _check_volatility(self, symbol: str) -> bool:
        """实时波动率检测(基于1分钟K线)"""
        latest_vol = MarketData.get_recent_volatility(symbol, window=15)
        return latest_vol > self.volatility_threshold

    def _is_close_period(self) -> bool:
        """是否处于尾盘时段(14:30-15:00)"""
        now = datetime.now().time()
        return now >= time(14, 30) and now <= time(15, 0)
