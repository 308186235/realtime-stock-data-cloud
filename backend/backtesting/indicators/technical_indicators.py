import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple

class TechnicalIndicators:
    """技术指标计算类,提供常用技术指标的计算功能"""
    
    @staticmethod
    def add_moving_average(df: pd.DataFrame, price_col: str = 'close', periods: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """
        添加移动平均线
        
        参数:
        - df: 数据DataFrame
        - price_col: 价格列名
        - periods: 均线周期列表
        
        返回:
        - 添加了均线的DataFrame
        """
        result_df = df.copy()
        
        for period in periods:
            result_df[f'ma_{period}'] = result_df[price_col].rolling(window=period).mean()
        
        return result_df
    
    @staticmethod
    def add_exponential_moving_average(df: pd.DataFrame, price_col: str = 'close', periods: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """
        添加指数移动平均线
        
        参数:
        - df: 数据DataFrame
        - price_col: 价格列名
        - periods: EMA周期列表
        
        返回:
        - 添加了EMA的DataFrame
        """
        result_df = df.copy()
        
        for period in periods:
            result_df[f'ema_{period}'] = result_df[price_col].ewm(span=period, adjust=False).mean()
        
        return result_df
    
    @staticmethod
    def add_macd(df: pd.DataFrame, price_col: str = 'close', fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """
        添加MACD指标
        
        参数:
        - df: 数据DataFrame
        - price_col: 价格列名
        - fast_period: 快线周期
        - slow_period: 慢线周期
        - signal_period: 信号线周期
        
        返回:
        - 添加了MACD的DataFrame
        """
        result_df = df.copy()
        
        # 计算快线和慢线
        ema_fast = result_df[price_col].ewm(span=fast_period, adjust=False).mean()
        ema_slow = result_df[price_col].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线和信号线
        result_df['macd'] = ema_fast - ema_slow
        result_df['macd_signal'] = result_df['macd'].ewm(span=signal_period, adjust=False).mean()
        result_df['macd_histogram'] = result_df['macd'] - result_df['macd_signal']
        
        return result_df
    
    @staticmethod
    def add_rsi(df: pd.DataFrame, price_col: str = 'close', period: int = 14) -> pd.DataFrame:
        """
        添加RSI指标
        
        参数:
        - df: 数据DataFrame
        - price_col: 价格列名
        - period: RSI周期
        
        返回:
        - 添加了RSI的DataFrame
        """
        result_df = df.copy()
        
        # 计算价格变化
        delta = result_df[price_col].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均上涨和下跌
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 后续数据使用wilder平滑
        for i in range(period, len(delta)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
        
        # 计算相对强度和RSI
        rs = avg_gain / avg_loss
        result_df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        return result_df
    
    @staticmethod
    def add_stochastic_oscillator(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', close_col: str = 'close', k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        添加随机指标(KD)
        
        参数:
        - df: 数据DataFrame
        - high_col: 最高价列名
        - low_col: 最低价列名
        - close_col: 收盘价列名
        - k_period: K线周期
        - d_period: D线周期
        
        返回:
        - 添加了KD指标的DataFrame
        """
        result_df = df.copy()
        
        # 计算K值(快速随机指标)
        lowest_low = result_df[low_col].rolling(window=k_period).min()
        highest_high = result_df[high_col].rolling(window=k_period).max()
        result_df['stoch_k'] = 100 * ((result_df[close_col] - lowest_low) / (highest_high - lowest_low))
        
        # 计算D值(慢速随机指标 - K值的移动平均)
        result_df['stoch_d'] = result_df['stoch_k'].rolling(window=d_period).mean()
        
        return result_df
    
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, price_col: str = 'close', period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        添加布林带指标
        
        参数:
        - df: 数据DataFrame
        - price_col: 价格列名
        - period: 周期
        - std_dev: 标准差倍数
        
        返回:
        - 添加了布林带的DataFrame
        """
        result_df = df.copy()
        
        # 计算移动平均线
        result_df['bb_middle'] = result_df[price_col].rolling(window=period).mean()
        
        # 计算标准差
        rolling_std = result_df[price_col].rolling(window=period).std()
        
        # 计算上下轨
        result_df['bb_upper'] = result_df['bb_middle'] + (rolling_std * std_dev)
        result_df['bb_lower'] = result_df['bb_middle'] - (rolling_std * std_dev)
        
        # 计算带宽和百分比B
        result_df['bb_width'] = (result_df['bb_upper'] - result_df['bb_lower']) / result_df['bb_middle']
        result_df['bb_b'] = (result_df[price_col] - result_df['bb_lower']) / (result_df['bb_upper'] - result_df['bb_lower'])
        
        return result_df
    
    @staticmethod
    def add_atr(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', close_col: str = 'close', period: int = 14) -> pd.DataFrame:
        """
        添加平均真实范围(ATR)指标
        
        参数:
        - df: 数据DataFrame
        - high_col: 最高价列名
        - low_col: 最低价列名
        - close_col: 收盘价列名
        - period: ATR周期
        
        返回:
        - 添加了ATR的DataFrame
        """
        result_df = df.copy()
        
        # 计算真实范围
        result_df['tr1'] = abs(result_df[high_col] - result_df[low_col])
        result_df['tr2'] = abs(result_df[high_col] - result_df[close_col].shift())
        result_df['tr3'] = abs(result_df[low_col] - result_df[close_col].shift())
        result_df['tr'] = result_df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        # 计算ATR
        result_df[f'atr_{period}'] = result_df['tr'].rolling(window=period).mean()
        
        # 删除临时列
        result_df = result_df.drop(['tr1', 'tr2', 'tr3', 'tr'], axis=1)
        
        return result_df
    
    @staticmethod
    def add_obv(df: pd.DataFrame, close_col: str = 'close', volume_col: str = 'volume') -> pd.DataFrame:
        """
        添加能量潮(OBV)指标
        
        参数:
        - df: 数据DataFrame
        - close_col: 收盘价列名
        - volume_col: 成交量列名
        
        返回:
        - 添加了OBV的DataFrame
        """
        result_df = df.copy()
        
        # 计算价格变化方向
        price_change = result_df[close_col].diff()
        
        # 初始化OBV列
        result_df['obv'] = 0
        
        # 填充第一行OBV
        if len(result_df) > 0:
            result_df.loc[result_df.index[0], 'obv'] = result_df.loc[result_df.index[0], volume_col]
        
        # 根据价格变化累计OBV
        for i in range(1, len(result_df)):
            if price_change.iloc[i] > 0:
                result_df.loc[result_df.index[i], 'obv'] = result_df.loc[result_df.index[i-1], 'obv'] + result_df.loc[result_df.index[i], volume_col]
            elif price_change.iloc[i] < 0:
                result_df.loc[result_df.index[i], 'obv'] = result_df.loc[result_df.index[i-1], 'obv'] - result_df.loc[result_df.index[i], volume_col]
            else:
                result_df.loc[result_df.index[i], 'obv'] = result_df.loc[result_df.index[i-1], 'obv']
        
        return result_df
    
    @staticmethod
    def add_money_flow_index(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', close_col: str = 'close', volume_col: str = 'volume', period: int = 14) -> pd.DataFrame:
        """
        添加资金流量指标(MFI)
        
        参数:
        - df: 数据DataFrame
        - high_col: 最高价列名
        - low_col: 最低价列名
        - close_col: 收盘价列名
        - volume_col: 成交量列名
        - period: MFI周期
        
        返回:
        - 添加了MFI的DataFrame
        """
        result_df = df.copy()
        
        # 计算典型价格
        result_df['typical_price'] = (result_df[high_col] + result_df[low_col] + result_df[close_col]) / 3
        
        # 计算原始资金流
        result_df['raw_money_flow'] = result_df['typical_price'] * result_df[volume_col]
        
        # 计算正/负资金流
        result_df['price_change'] = result_df['typical_price'].diff()
        result_df['positive_flow'] = np.where(result_df['price_change'] > 0, result_df['raw_money_flow'], 0)
        result_df['negative_flow'] = np.where(result_df['price_change'] < 0, result_df['raw_money_flow'], 0)
        
        # 计算周期内的正/负流量和
        result_df['positive_flow_sum'] = result_df['positive_flow'].rolling(window=period).sum()
        result_df['negative_flow_sum'] = result_df['negative_flow'].rolling(window=period).sum()
        
        # 计算资金比率和MFI
        result_df['money_ratio'] = result_df['positive_flow_sum'] / result_df['negative_flow_sum']
        result_df['mfi'] = 100 - (100 / (1 + result_df['money_ratio']))
        
        # 删除临时列
        result_df = result_df.drop(['typical_price', 'raw_money_flow', 'price_change', 'positive_flow', 'negative_flow', 'positive_flow_sum', 'negative_flow_sum', 'money_ratio'], axis=1)
        
        return result_df
    
    @staticmethod
    def add_ichimoku_cloud(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                           tenkan_period: int = 9, kijun_period: int = 26, 
                           senkou_b_period: int = 52, displacement: int = 26) -> pd.DataFrame:
        """
        添加一目均衡表(Ichimoku Cloud)指标
        
        参数:
        - df: 数据DataFrame
        - high_col: 最高价列名
        - low_col: 最低价列名
        - tenkan_period: 转换线周期
        - kijun_period: 基准线周期
        - senkou_b_period: 先行带B周期
        - displacement: 延迟周期
        
        返回:
        - 添加了一目均衡表指标的DataFrame
        """
        result_df = df.copy()
        
        # 计算转换线 (Tenkan-sen): (最高价(n天) + 最低价(n天))/2
        high_tenkan = result_df[high_col].rolling(window=tenkan_period).max()
        low_tenkan = result_df[low_col].rolling(window=tenkan_period).min()
        result_df['ichimoku_tenkan'] = (high_tenkan + low_tenkan) / 2
        
        # 计算基准线 (Kijun-sen): (最高价(n天) + 最低价(n天))/2
        high_kijun = result_df[high_col].rolling(window=kijun_period).max()
        low_kijun = result_df[low_col].rolling(window=kijun_period).min()
        result_df['ichimoku_kijun'] = (high_kijun + low_kijun) / 2
        
        # 计算先行带A (Senkou Span A): (转换线 + 基准线)/2,向前位移n天
        result_df['ichimoku_senkou_a'] = ((result_df['ichimoku_tenkan'] + result_df['ichimoku_kijun']) / 2).shift(displacement)
        
        # 计算先行带B (Senkou Span B): (最高价(n天) + 最低价(n天))/2,向前位移n天
        high_senkou_b = result_df[high_col].rolling(window=senkou_b_period).max()
        low_senkou_b = result_df[low_col].rolling(window=senkou_b_period).min()
        result_df['ichimoku_senkou_b'] = ((high_senkou_b + low_senkou_b) / 2).shift(displacement)
        
        # 计算滞后带 (Chikou Span): 当日收盘价向后位移n天
        result_df['ichimoku_chikou'] = result_df['close'].shift(-displacement)
        
        return result_df
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        添加所有常用技术指标
        
        参数:
        - df: 数据DataFrame
        
        返回:
        - 添加了所有指标的DataFrame
        """
        result_df = df.copy()
        
        # 添加移动平均线
        result_df = TechnicalIndicators.add_moving_average(result_df)
        
        # 添加指数移动平均线
        result_df = TechnicalIndicators.add_exponential_moving_average(result_df)
        
        # 添加MACD
        result_df = TechnicalIndicators.add_macd(result_df)
        
        # 添加RSI
        result_df = TechnicalIndicators.add_rsi(result_df)
        
        # 添加随机指标
        result_df = TechnicalIndicators.add_stochastic_oscillator(result_df)
        
        # 添加布林带
        result_df = TechnicalIndicators.add_bollinger_bands(result_df)
        
        # 添加ATR
        result_df = TechnicalIndicators.add_atr(result_df)
        
        # 添加OBV
        result_df = TechnicalIndicators.add_obv(result_df)
        
        # 添加MFI
        result_df = TechnicalIndicators.add_money_flow_index(result_df)
        
        return result_df
    
    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        生成技术指标信号
        
        参数:
        - df: 包含技术指标的DataFrame
        
        返回:
        - 添加了信号的DataFrame
        """
        result_df = df.copy()
        
        # MACD交叉信号
        if 'macd' in result_df.columns and 'macd_signal' in result_df.columns:
            result_df['macd_cross_signal'] = 0
            # 金叉信号 (MACD从下方穿过信号线)
            result_df.loc[(result_df['macd'] > result_df['macd_signal']) & 
                         (result_df['macd'].shift() <= result_df['macd_signal'].shift()), 'macd_cross_signal'] = 1
            # 死叉信号 (MACD从上方穿过信号线)
            result_df.loc[(result_df['macd'] < result_df['macd_signal']) & 
                         (result_df['macd'].shift() >= result_df['macd_signal'].shift()), 'macd_cross_signal'] = -1
        
        # RSI信号
        if 'rsi_14' in result_df.columns:
            result_df['rsi_signal'] = 0
            # 超买信号
            result_df.loc[result_df['rsi_14'] > 70, 'rsi_signal'] = -1
            # 超卖信号
            result_df.loc[result_df['rsi_14'] < 30, 'rsi_signal'] = 1
        
        # 均线交叉信号
        if 'ma_5' in result_df.columns and 'ma_20' in result_df.columns:
            result_df['ma_cross_signal'] = 0
            # 短期均线上穿长期均线
            result_df.loc[(result_df['ma_5'] > result_df['ma_20']) & 
                         (result_df['ma_5'].shift() <= result_df['ma_20'].shift()), 'ma_cross_signal'] = 1
            # 短期均线下穿长期均线
            result_df.loc[(result_df['ma_5'] < result_df['ma_20']) & 
                         (result_df['ma_5'].shift() >= result_df['ma_20'].shift()), 'ma_cross_signal'] = -1
        
        # 布林带信号
        if 'bb_upper' in result_df.columns and 'bb_lower' in result_df.columns:
            result_df['bb_signal'] = 0
            # 价格突破上轨
            result_df.loc[(result_df['close'] > result_df['bb_upper']) & 
                         (result_df['close'].shift() <= result_df['bb_upper'].shift()), 'bb_signal'] = 1
            # 价格突破下轨
            result_df.loc[(result_df['close'] < result_df['bb_lower']) & 
                         (result_df['close'].shift() >= result_df['bb_lower'].shift()), 'bb_signal'] = -1
        
        # KD随机指标信号
        if 'stoch_k' in result_df.columns and 'stoch_d' in result_df.columns:
            result_df['stoch_signal'] = 0
            # K线上穿D线
            result_df.loc[(result_df['stoch_k'] > result_df['stoch_d']) & 
                         (result_df['stoch_k'].shift() <= result_df['stoch_d'].shift()), 'stoch_signal'] = 1
            # K线下穿D线
            result_df.loc[(result_df['stoch_k'] < result_df['stoch_d']) & 
                         (result_df['stoch_k'].shift() >= result_df['stoch_d'].shift()), 'stoch_signal'] = -1
        
        # 综合信号(简单加权)
        signal_columns = [col for col in result_df.columns if col.endswith('_signal')]
        if signal_columns:
            result_df['combined_signal'] = result_df[signal_columns].sum(axis=1)
        
        return result_df 
