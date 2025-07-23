"""
技术指标计算模块
实现常用的技术分析指标：MA、MACD、RSI、BOLL、KDJ等
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def moving_average(prices: List[float], period: int) -> List[float]:
        """
        计算移动平均线 (MA)
        
        Args:
            prices: 价格序列
            period: 周期
            
        Returns:
            移动平均线值列表
        """
        if len(prices) < period:
            return [np.nan] * len(prices)
        
        ma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                ma_values.append(np.nan)
            else:
                ma_values.append(np.mean(prices[i-period+1:i+1]))
        
        return ma_values
    
    @staticmethod
    def exponential_moving_average(prices: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线 (EMA)
        
        Args:
            prices: 价格序列
            period: 周期
            
        Returns:
            EMA值列表
        """
        if len(prices) == 0:
            return []
        
        alpha = 2.0 / (period + 1)
        ema_values = [prices[0]]  # 第一个值等于第一个价格
        
        for i in range(1, len(prices)):
            ema = alpha * prices[i] + (1 - alpha) * ema_values[-1]
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[float]]:
        """
        计算MACD指标
        
        Args:
            prices: 价格序列
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            包含MACD、信号线、柱状图的字典
        """
        if len(prices) < slow_period:
            return {
                'macd': [np.nan] * len(prices),
                'signal': [np.nan] * len(prices),
                'histogram': [np.nan] * len(prices)
            }
        
        # 计算快慢EMA
        ema_fast = TechnicalIndicators.exponential_moving_average(prices, fast_period)
        ema_slow = TechnicalIndicators.exponential_moving_average(prices, slow_period)
        
        # 计算MACD线
        macd_line = [fast - slow if not (np.isnan(fast) or np.isnan(slow)) else np.nan 
                     for fast, slow in zip(ema_fast, ema_slow)]
        
        # 计算信号线（MACD的EMA）
        valid_macd = [x for x in macd_line if not np.isnan(x)]
        if len(valid_macd) >= signal_period:
            signal_ema = TechnicalIndicators.exponential_moving_average(valid_macd, signal_period)
            # 填充前面的NaN值
            signal_line = [np.nan] * (len(macd_line) - len(signal_ema)) + signal_ema
        else:
            signal_line = [np.nan] * len(macd_line)
        
        # 计算柱状图
        histogram = [macd - signal if not (np.isnan(macd) or np.isnan(signal)) else np.nan 
                    for macd, signal in zip(macd_line, signal_line)]
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        计算相对强弱指标 (RSI)
        
        Args:
            prices: 价格序列
            period: 周期
            
        Returns:
            RSI值列表
        """
        if len(prices) < period + 1:
            return [np.nan] * len(prices)
        
        # 计算价格变化
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 分离上涨和下跌
        gains = [change if change > 0 else 0 for change in price_changes]
        losses = [-change if change < 0 else 0 for change in price_changes]
        
        rsi_values = [np.nan]  # 第一个值为NaN
        
        # 计算初始平均增益和损失
        if len(gains) >= period:
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            # 计算第一个RSI值
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(100 - (100 / (1 + rs)))
            
            # 计算后续RSI值
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                
                if avg_loss == 0:
                    rsi_values.append(100.0)
                else:
                    rs = avg_gain / avg_loss
                    rsi_values.append(100 - (100 / (1 + rs)))
        
        # 填充剩余的NaN值
        while len(rsi_values) < len(prices):
            rsi_values.append(np.nan)
        
        return rsi_values
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        计算布林带 (Bollinger Bands)
        
        Args:
            prices: 价格序列
            period: 周期
            std_dev: 标准差倍数
            
        Returns:
            包含上轨、中轨、下轨的字典
        """
        if len(prices) < period:
            return {
                'upper': [np.nan] * len(prices),
                'middle': [np.nan] * len(prices),
                'lower': [np.nan] * len(prices)
            }
        
        # 计算中轨（移动平均线）
        middle_band = TechnicalIndicators.moving_average(prices, period)
        
        # 计算上下轨
        upper_band = []
        lower_band = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(np.nan)
                lower_band.append(np.nan)
            else:
                # 计算标准差
                price_slice = prices[i-period+1:i+1]
                std = np.std(price_slice)
                
                upper_band.append(middle_band[i] + std_dev * std)
                lower_band.append(middle_band[i] - std_dev * std)
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }
    
    @staticmethod
    def kdj(high_prices: List[float], low_prices: List[float], close_prices: List[float], 
            period: int = 9, k_period: int = 3, d_period: int = 3) -> Dict[str, List[float]]:
        """
        计算KDJ指标
        
        Args:
            high_prices: 最高价序列
            low_prices: 最低价序列
            close_prices: 收盘价序列
            period: RSV周期
            k_period: K值平滑周期
            d_period: D值平滑周期
            
        Returns:
            包含K、D、J值的字典
        """
        if len(high_prices) < period or len(low_prices) < period or len(close_prices) < period:
            return {
                'k': [np.nan] * len(close_prices),
                'd': [np.nan] * len(close_prices),
                'j': [np.nan] * len(close_prices)
            }
        
        # 计算RSV
        rsv_values = []
        for i in range(len(close_prices)):
            if i < period - 1:
                rsv_values.append(np.nan)
            else:
                highest = max(high_prices[i-period+1:i+1])
                lowest = min(low_prices[i-period+1:i+1])
                
                if highest == lowest:
                    rsv = 50.0  # 避免除零
                else:
                    rsv = (close_prices[i] - lowest) / (highest - lowest) * 100
                
                rsv_values.append(rsv)
        
        # 计算K值（RSV的移动平均）
        k_values = []
        k_prev = 50.0  # 初始K值
        
        for rsv in rsv_values:
            if np.isnan(rsv):
                k_values.append(np.nan)
            else:
                k = (2 * k_prev + rsv) / 3
                k_values.append(k)
                k_prev = k
        
        # 计算D值（K值的移动平均）
        d_values = []
        d_prev = 50.0  # 初始D值
        
        for k in k_values:
            if np.isnan(k):
                d_values.append(np.nan)
            else:
                d = (2 * d_prev + k) / 3
                d_values.append(d)
                d_prev = d
        
        # 计算J值
        j_values = [3 * k - 2 * d if not (np.isnan(k) or np.isnan(d)) else np.nan 
                   for k, d in zip(k_values, d_values)]
        
        return {
            'k': k_values,
            'd': d_values,
            'j': j_values
        }
    
    @staticmethod
    def calculate_all_indicators(ohlc_data: List[Dict]) -> Dict[str, List[float]]:
        """
        计算所有技术指标
        
        Args:
            ohlc_data: OHLC数据列表，每个元素包含open, high, low, close, volume
            
        Returns:
            包含所有指标的字典
        """
        if not ohlc_data:
            return {}
        
        # 提取价格数据
        opens = [item['open'] for item in ohlc_data]
        highs = [item['high'] for item in ohlc_data]
        lows = [item['low'] for item in ohlc_data]
        closes = [item['close'] for item in ohlc_data]
        volumes = [item['volume'] for item in ohlc_data]
        
        # 计算各种指标
        indicators = {}
        
        # 移动平均线
        indicators['ma5'] = TechnicalIndicators.moving_average(closes, 5)
        indicators['ma10'] = TechnicalIndicators.moving_average(closes, 10)
        indicators['ma20'] = TechnicalIndicators.moving_average(closes, 20)
        indicators['ma60'] = TechnicalIndicators.moving_average(closes, 60)
        
        # EMA
        indicators['ema12'] = TechnicalIndicators.exponential_moving_average(closes, 12)
        indicators['ema26'] = TechnicalIndicators.exponential_moving_average(closes, 26)
        
        # MACD
        macd_result = TechnicalIndicators.macd(closes)
        indicators.update(macd_result)
        
        # RSI
        indicators['rsi'] = TechnicalIndicators.rsi(closes)
        
        # 布林带
        boll_result = TechnicalIndicators.bollinger_bands(closes)
        indicators['boll_upper'] = boll_result['upper']
        indicators['boll_middle'] = boll_result['middle']
        indicators['boll_lower'] = boll_result['lower']
        
        # KDJ
        kdj_result = TechnicalIndicators.kdj(highs, lows, closes)
        indicators.update(kdj_result)
        
        return indicators

    @staticmethod
    def get_latest_indicators(stock_code: str, ohlc_data: List[Dict]) -> Dict[str, float]:
        """
        获取最新的技术指标值

        Args:
            stock_code: 股票代码
            ohlc_data: OHLC数据

        Returns:
            最新指标值字典
        """
        if not ohlc_data:
            return {}

        indicators = TechnicalIndicators.calculate_all_indicators(ohlc_data)
        latest_indicators = {}

        # 获取最新值（非NaN）
        for key, values in indicators.items():
            if values:
                # 从后往前找第一个非NaN值
                for i in range(len(values) - 1, -1, -1):
                    if not np.isnan(values[i]):
                        latest_indicators[key] = round(values[i], 4)
                        break

                if key not in latest_indicators:
                    latest_indicators[key] = None

        return latest_indicators

# 全局技术指标计算器实例
technical_indicators = TechnicalIndicators()
