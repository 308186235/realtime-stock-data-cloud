import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到路径以导入所需模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from inverted_three_red_strategy_standalone import InvertedThreeRedStrategy
from backend.backtesting.strategy_base import StrategyBase

class InvertedThreeRedBacktest(StrategyBase):
    """
    倒三红形策略的回测适配器
    将独立的倒三红形策略适配到回测引擎
    """
    
    def __init__(self, params=None):
        """
        初始化倒三红形回测策略
        
        参数:
        - params: 字典,包含策略参数
        """
        # 初始化基类
        super().__init__(params or {})
        self.name = "倒三红形策略(回测)"
        
        # 创建策略实例
        default_params = InvertedThreeRedStrategy().get_default_parameters()
        # 合并默认参数和用户参数
        strategy_params = {**default_params, **self.params}
        
        # 初始化倒三红形策略实例
        self.detector = InvertedThreeRedStrategy(strategy_params)
    
    def generate_signals(self, data):
        """
        根据数据生成交易信号
        
        参数:
        - data: DataFrame,包含OHLCV数据
        
        返回:
        - 字典,包含股票代码和对应的交易信号
        """
        # 初始化信号字典
        signals = {}
        
        # 检查数据是否包含必要的列
        required_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要的列: {col}")
        
        # 按股票代码分组处理数据
        for symbol, group in data.groupby('symbol'):
            # 对每个股票的数据按日期排序
            symbol_data = group.sort_values('date')
            
            # 使用策略检测倒三红形
            detected_signals = self.detector.generate_signals(symbol_data)
            
            # 获取最新日期的信号
            latest_signal = detected_signals.iloc[-1] if not detected_signals.empty else 0
            
            # 只有当有明确信号时才添加到结果中
            if latest_signal != 0:
                # 获取当前收盘价
                current_price = symbol_data['close'].iloc[-1]
                
                if latest_signal > 0:  # 买入信号
                    signals[symbol] = {
                        'action': 'BUY',
                        'price': current_price,
                        'size': self.params.get('low_position_position', 0.2)  # 默认低位仓位为20%
                    }
                elif latest_signal < 0:  # 卖出信号
                    # 根据位置确定减仓比例
                    position_type = self._determine_position_type(symbol_data)
                    
                    if position_type == 'high':
                        reduction = self.params.get('high_position_reduction', 0.7)  # 高位减仓70%
                    else:  # 中位
                        reduction = self.params.get('mid_position_reduction', 0.3)  # 中位减仓30%
                    
                    signals[symbol] = {
                        'action': 'SELL',
                        'price': current_price,
                        'size': reduction  # 按比例减仓
                    }
        
        return signals
    
    def _determine_position_type(self, data):
        """
        判断当前价格位置
        
        参数:
        - data: DataFrame,包含OHLCV数据
        
        返回:
        - str: 位置类型 ('high', 'middle', 'low')
        """
        if len(data) < 60:  # 至少需要60个数据点
            return 'middle'
        
        # 获取最近60个交易日的数据
        recent_data = data.tail(60)
        
        # 计算历史最高最低价
        hist_high = recent_data['high'].max()
        hist_low = recent_data['low'].min()
        price_range = hist_high - hist_low
        
        if price_range == 0:
            return 'middle'
        
        # 获取当前收盘价
        current_price = data['close'].iloc[-1]
        
        # 计算当前价格在价格区间中的相对位置
        relative_position = (current_price - hist_low) / price_range
        
        # 定义高位阈值和低位阈值
        high_threshold = self.params.get('high_position_threshold', 0.8)
        low_threshold = self.params.get('low_position_threshold', 0.2)
        
        # 判断位置类型
        if relative_position >= high_threshold:
            return 'high'
        elif relative_position <= low_threshold:
            return 'low'
        else:
            return 'middle' 
