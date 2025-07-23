"""
技术指标分析服务 - 完整版
基于Qlib的技术指标计算,为AI决策提供数据支持
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术指标分析器"""

    def __init__(self):
        self.indicators = {}
        
    def calculate_ma(self, prices: List[float], period: int = 20) -> List[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return [None] * len(prices)
            
        ma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma = sum(prices[i-period+1:i+1]) / period
                ma_values.append(ma)
        return ma_values
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """计算RSI"""
        if len(prices) < period + 1:
            return [None] * len(prices)
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        rsi_values = [None]
        avg_gain = avg_loss = 0
        
        for i in range(period-1, len(gains)):
            if i == period - 1:
                avg_gain = sum(gains[:period]) / period
                avg_loss = sum(losses[:period]) / period
            else:
                avg_gain = (avg_gain * (period-1) + gains[i]) / period
                avg_loss = (avg_loss * (period-1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        while len(rsi_values) < len(prices):
            rsi_values.insert(1, None)
            
        return rsi_values
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """计算MACD"""
        if len(prices) < 26:
            return {
                'macd': [None] * len(prices),
                'signal': [None] * len(prices),
                'histogram': [None] * len(prices)
            }
        
        def ema(data, period):
            multiplier = 2 / (period + 1)
            ema_values = [data[0]]
            for i in range(1, len(data)):
                ema_val = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
                ema_values.append(ema_val)
            return ema_values
        
        ema_fast = ema(prices, 12)
        ema_slow = ema(prices, 26)
        
        macd_line = []
        for i in range(len(prices)):
            if i < 25:
                macd_line.append(None)
            else:
                macd_line.append(ema_fast[i] - ema_slow[i])
        
        return {
            'macd': macd_line,
            'signal': [None] * len(prices),
            'histogram': [None] * len(prices)
        }
    
    def analyze_stock(self, stock_code: str, prices: List[float]) -> Dict:
        """分析股票技术指标"""
        try:
            analysis = {
                'stock_code': stock_code,
                'timestamp': datetime.now().isoformat(),
                'indicators': {}
            }
            
            analysis['indicators']['ma5'] = self.calculate_ma(prices, 5)
            analysis['indicators']['ma10'] = self.calculate_ma(prices, 10)
            analysis['indicators']['ma20'] = self.calculate_ma(prices, 20)
            analysis['indicators']['rsi'] = self.calculate_rsi(prices)
            analysis['indicators']['macd'] = self.calculate_macd(prices)
            
            analysis['signals'] = self._generate_signals(analysis['indicators'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"技术分析失败 {stock_code}: {e}")
            return {'error': str(e)}
    
    def _generate_signals(self, indicators: Dict) -> Dict:
        """生成交易信号"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'overall_trend': 'neutral'
        }
        
        try:
            latest_rsi = indicators['rsi'][-1] if indicators['rsi'][-1] is not None else 50
            
            if latest_rsi < 30:
                signals['buy_signals'].append('RSI超卖')
            elif latest_rsi > 70:
                signals['sell_signals'].append('RSI超买')
            
            ma5 = indicators['ma5'][-1]
            ma20 = indicators['ma20'][-1]
            if ma5 is not None and ma20 is not None:
                if ma5 > ma20:
                    signals['buy_signals'].append('短期均线上穿')
                    signals['overall_trend'] = 'bullish'
                else:
                    signals['sell_signals'].append('短期均线下穿')
                    signals['overall_trend'] = 'bearish'
                
        except Exception as e:
            logger.error(f"信号生成失败: {e}")
        
        return signals

# 全局实例
technical_analyzer = TechnicalAnalyzer()

def get_technical_analysis(stock_code: str, prices: List[float]) -> Dict:
    """获取技术分析"""
    return technical_analyzer.analyze_stock(stock_code, prices)
