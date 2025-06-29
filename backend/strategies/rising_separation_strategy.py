import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class RisingSeparationStrategy(BaseStrategy):
    """
    上涨分离形(Rising Separation)策略
    
    "上涨分离形"是股价在上涨趋势中出现的中继或反转信号,由两根K线组合而成,表示多空在关键价位博弈的结果。
    
    核心特征:
    1. 第一根为阴线(调整信号),第二根为阳线(反攻信号)
    2. 两根K线的开盘价几乎相同(或相差≤1%),但收盘价方向相反
    3. 阳线收盘价需高于阴线收盘价,且最好收复阴线实体的1/2以上
    4. 第二根阳线成交量需较阴线放大30%以上(验证多方发力)
    5. 出现在上涨趋势中途(如回踩5日均线后)或短期调整末端
    
    信号意义:
    - 中继信号:若出现在上涨初期或中期,且阳线力度强,多为洗盘结束,股价继续上行
    - 反转信号:若在高位出现,且阳线未能覆盖阴线实体,可能是滞涨信号,需警惕
    
    该策略生成以下信号:
    - 1 (买入信号):低位或中位有效分离形,多方重新占据主动,趋势可能继续
    - -1 (卖出信号):高位无效分离形,表现为阳线覆盖不足或缩量,可能是滞涨信号
    - 0 (观望):不满足分离形条件或信号不明确
    """
    
    def __init__(self, parameters=None):
        """
        初始化上涨分离形策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "上涨分离形策略"
        self.description = "基于上涨分离形K线组合的趋势中继或反转信号交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'open_price_diff_threshold': 0.01,    # 两根K线开盘价差阈值(1%)
            'min_recovery_ratio': 0.5,            # 阳线收复阴线实体最小比例(50%)
            'volume_increase_threshold': 0.3,     # 阳线成交量增幅最小阈值(30%)
            'trend_bars': 5,                      # 检查趋势的K线数量
            'uptrend_threshold': 0.03,            # 上涨趋势确认阈值(3%)
            'look_back_period': 60,               # 回溯周期(历史高低点判断)
            'high_position_threshold': 0.8,       # 高位判断阈值(80%)
            'low_position_threshold': 0.2,        # 低位判断阈值(20%)
            'use_ma_confirmation': True,          # 是否使用均线确认
            'ma5_period': 5,                      # 5日均线周期
            'ma10_period': 10,                    # 10日均线周期
            'ma20_period': 20,                    # 20日均线周期
            'ma60_period': 60,                    # 60日均线周期
            'stop_loss_pct': 0.05,                # 止损百分比(5%)
            'enable_macd_confirmation': True,     # 是否启用MACD确认
            'enable_rsi_confirmation': True,      # 是否启用RSI确认
            'rsi_threshold': 50,                  # RSI强势区域阈值
            'min_body_size_ratio': 0.3,           # 阳线实体最小比例(占K线的30%)
            'confirmation_days': 1                # 形态确认的观察天数
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'open_price_diff_threshold': {'min': 0.005, 'max': 0.02, 'step': 0.005},
            'min_recovery_ratio': {'min': 0.3, 'max': 0.7, 'step': 0.1},
            'volume_increase_threshold': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'trend_bars': {'min': 3, 'max': 10, 'step': 1},
            'uptrend_threshold': {'min': 0.01, 'max': 0.05, 'step': 0.01},
            'high_position_threshold': {'min': 0.7, 'max': 0.9, 'step': 0.05},
            'low_position_threshold': {'min': 0.1, 'max': 0.3, 'step': 0.05},
            'min_body_size_ratio': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'rsi_threshold': {'min': 40, 'max': 60, 'step': 5}
        }
    
    def generate_signals(self, data):
        """
        生成交易信号
        
        Args:
            data (pd.DataFrame): 包含OHLCV的历史市场数据
            
        Returns:
            pd.Series: 交易信号序列 (1:买入, -1:卖出, 0:持有)
        """
        # 确保数据完整性
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error("缺少所需的数据列,至少需要 OHLCV 数据")
            return pd.Series(0, index=data.index)
        
        # 创建数据副本并进行预处理
        df = data.copy()
        
        # 计算K线特征
        df['body_size'] = abs(df['close'] - df['open']) / (df['high'] - df['low'])
        df['is_bullish'] = df['close'] > df['open']
        df['is_bearish'] = df['close'] < df['open']
        
        # 计算移动平均线
        if self.parameters['use_ma_confirmation']:
            df['ma5'] = df['close'].rolling(window=self.parameters['ma5_period']).mean()
            df['ma10'] = df['close'].rolling(window=self.parameters['ma10_period']).mean()
            df['ma20'] = df['close'].rolling(window=self.parameters['ma20_period']).mean()
            df['ma60'] = df['close'].rolling(window=self.parameters['ma60_period']).mean()
        
        # 计算技术指标
        self._calculate_technical_indicators(df)
        
        # 初始化信号列
        df['signal'] = 0
        df['separation_detected'] = False  # 分离形检测标记
        
        # 设置回溯周期
        look_back = self.parameters['look_back_period']
        trend_bars = self.parameters['trend_bars']
        
        # 需要足够的数据才能开始分析
        min_required_bars = max(look_back, trend_bars, self.parameters['ma60_period'] if self.parameters['use_ma_confirmation'] else 0) + 2
        if len(df) < min_required_bars:
            logger.warning(f"数据不足,无法完整分析上涨分离形,需要至少{min_required_bars}根K线")
            return pd.Series(0, index=data.index)
        
        # 检测上涨分离形
        for i in range(trend_bars + 2, len(df)):
            # 跳过已经检测到的形态区域
            if i >= 2 and df['separation_detected'].iloc[i-1]:
                continue
                
            # 提取用于模式识别的K线
            window2 = df.iloc[i-2:i]  # 最近两根K线
            
            # 检查第一根是否为阴线,第二根是否为阳线
            if not (window2['is_bearish'].iloc[0] and window2['is_bullish'].iloc[1]):
                continue
            
            # 检查两根K线的开盘价是否相近
            open_diff = abs(window2['open'].iloc[0] - window2['open'].iloc[1]) / window2['open'].iloc[0]
            if open_diff > self.parameters['open_price_diff_threshold']:
                continue
            
            # 检查阳线收盘价是否高于阴线收盘价
            if window2['close'].iloc[1] <= window2['close'].iloc[0]:
                continue
            
            # 计算阳线收复阴线实体的比例
            bearish_body = abs(window2['open'].iloc[0] - window2['close'].iloc[0])
            recovery = window2['close'].iloc[1] - window2['close'].iloc[0]
            recovery_ratio = recovery / bearish_body if bearish_body > 0 else 0
            
            # 检查阳线是否至少收复阴线实体的一定比例
            if recovery_ratio < self.parameters['min_recovery_ratio']:
                continue
            
            # 检查阳线成交量是否放大
            volume_increase = (window2['volume'].iloc[1] / window2['volume'].iloc[0]) - 1
            volume_increase_enough = volume_increase >= self.parameters['volume_increase_threshold']
            
            # 检查阳线实体是否足够大
            bullish_body_ratio = window2['body_size'].iloc[1]
            large_body = bullish_body_ratio >= self.parameters['min_body_size_ratio']
            
            # 分析前期趋势
            trend_window = df.iloc[i-trend_bars-2:i-2]
            is_uptrend = self._check_uptrend(trend_window)
            
            # 如果不在上涨趋势中,可能是误信号
            if not is_uptrend:
                continue
            
            # 判断价格位置(高位,中位,低位)
            position_type = self._determine_position_type(df, i)
            
            # 均线确认
            ma_confirmation = False
            if self.parameters['use_ma_confirmation'] and i >= self.parameters['ma60_period']:
                # 上涨分离形后是否站上关键均线
                ma_confirmation = (
                    (df['close'].iloc[i-1] > df['ma5'].iloc[i-1]) or
                    (df['close'].iloc[i-1] > df['ma10'].iloc[i-1] and df['close'].iloc[i-2] <= df['ma10'].iloc[i-2])
                )
            
            # 技术指标确认
            macd_confirmation = False
            rsi_confirmation = False
            
            if self.parameters['enable_macd_confirmation'] and 'macd_hist' in df.columns:
                # MACD柱状图放大确认
                macd_confirmation = (df['macd_hist'].iloc[i-1] > df['macd_hist'].iloc[i-2] and
                                    df['macd_hist'].iloc[i-1] > 0)
            
            if self.parameters['enable_rsi_confirmation'] and 'rsi' in df.columns:
                # RSI是否处于强势区域
                rsi_confirmation = df['rsi'].iloc[i-1] > self.parameters['rsi_threshold']
            
            # 标记检测到分离形
            df.loc[df.index[i-1], 'separation_detected'] = True
            
            # 生成信号
            signal = self._generate_signal(
                position_type,
                recovery_ratio,
                volume_increase_enough,
                large_body,
                ma_confirmation,
                macd_confirmation,
                rsi_confirmation
            )
            
            # 应用确认规则(如果需要)
            if self.parameters['confirmation_days'] > 0 and i + self.parameters['confirmation_days'] <= len(df):
                confirmation_window = df.iloc[i:i+self.parameters['confirmation_days']]
                signal = self._apply_confirmation_rules(confirmation_window, signal, position_type)
            
            df.loc[df.index[i-1], 'signal'] = signal
        
        return df['signal']
    
    def _calculate_technical_indicators(self, df):
        """
        计算技术指标
        
        Args:
            df (pd.DataFrame): 数据帧
        """
        # 计算RSI
        if self.parameters['enable_rsi_confirmation']:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        if self.parameters['enable_macd_confirmation']:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['signal_line']
    
    def _check_uptrend(self, window):
        """
        检查是否为上涨趋势
        
        Args:
            window (pd.DataFrame): 数据窗口
            
        Returns:
            bool: 是否为上涨趋势
        """
        if len(window) < 3:
            return False
            
        start_price = window['close'].iloc[0]
        end_price = window['close'].iloc[-1]
        
        # 计算价格变动幅度
        price_change = (end_price - start_price) / start_price
        
        # 判断是否为上涨趋势
        return price_change >= self.parameters['uptrend_threshold']
    
    def _determine_position_type(self, df, current_index):
        """
        判断当前K线位置类型
        
        Args:
            df (pd.DataFrame): 数据帧
            current_index (int): 当前K线索引
            
        Returns:
            str: 位置类型 ('high', 'middle', 'low')
        """
        # 获取回溯周期
        look_back = min(self.parameters['look_back_period'], current_index)
        
        # 获取历史数据
        historical_data = df.iloc[current_index-look_back:current_index]
        current_price = df['close'].iloc[current_index-1]
        
        # 计算历史最高,最低价
        historical_high = historical_data['high'].max()
        historical_low = historical_data['low'].min()
        
        # 计算当前价格在历史范围中的相对位置
        range_size = historical_high - historical_low
        
        if range_size == 0:  # 避免除零错误
            return 'middle'
            
        relative_position = (current_price - historical_low) / range_size
        
        # 判断位置类型
        if relative_position >= self.parameters['high_position_threshold']:
            return 'high'
        elif relative_position <= self.parameters['low_position_threshold']:
            return 'low'
        else:
            return 'middle'
    
    def _generate_signal(self, position_type, recovery_ratio, volume_increase, large_body,
                        ma_confirmation, macd_confirmation, rsi_confirmation):
        """
        根据形态特征生成交易信号
        
        Args:
            position_type (str): 位置类型
            recovery_ratio (float): 阳线收复阴线实体比例
            volume_increase (bool): 成交量是否放大
            large_body (bool): 阳线实体是否足够大
            ma_confirmation (bool): 均线确认
            macd_confirmation (bool): MACD确认
            rsi_confirmation (bool): RSI确认
            
        Returns:
            int: 交易信号 (1:买入, -1:卖出, 0:持有)
        """
        # 初始信号
        signal = 0
        
        # 高位分离形
        if position_type == 'high':
            # 高位出现分离形且信号不够强,可能是滞涨信号
            if not volume_increase or recovery_ratio < 0.7 or not large_body:
                signal = -1  # 卖出信号
            else:
                # 放量突破且各项指标确认,仍可能是上涨中继
                confirmations = sum([volume_increase, large_body, ma_confirmation, 
                                    macd_confirmation, rsi_confirmation])
                if confirmations >= 4:  # 至少满足4项确认条件
                    signal = 1  # 买入信号
        
        # 中位分离形
        elif position_type == 'middle':
            # 中位分离形通常是上涨中继信号
            if volume_increase and recovery_ratio >= 0.5:
                signal = 1  # 买入信号
                
                # 加强确认条件
                confirmations = sum([large_body, ma_confirmation, macd_confirmation, rsi_confirmation])
                if confirmations <= 1:  # 确认条件不足
                    signal = 0  # 观望信号
        
        # 低位分离形
        elif position_type == 'low':
            # 低位分离形可能是反转信号
            if volume_increase and recovery_ratio >= 0.5 and large_body:
                signal = 1  # 买入信号
                
                # 技术指标确认
                if ma_confirmation or macd_confirmation or rsi_confirmation:
                    signal = 1  # 增强买入信号的确信度
        
        return signal
    
    def _apply_confirmation_rules(self, confirmation_window, initial_signal, position_type):
        """
        应用确认规则来验证信号
        
        Args:
            confirmation_window (pd.DataFrame): 确认窗口数据
            initial_signal (int): 初始信号
            position_type (str): 位置类型
            
        Returns:
            int: 最终交易信号
        """
        # 如果初始信号为0,直接返回
        if initial_signal == 0 or len(confirmation_window) == 0:
            return initial_signal
            
        # 获取确认K线
        confirm_candle = confirmation_window.iloc[0]
        
        # 买入信号确认
        if initial_signal == 1:
            # 如果确认K线继续上涨,增强买入信号
            if confirm_candle['is_bullish'] and confirm_candle['close'] > confirmation_window.index[-1]:
                return 1
            
            # 如果确认K线为大阴线,可能是假突破,减弱信号
            elif confirm_candle['is_bearish'] and confirm_candle['body_size'] > 0.6:
                return 0
        
        # 卖出信号确认(高位分离形)
        elif initial_signal == -1 and position_type == 'high':
            # 如果确认K线继续下跌,确认卖出信号
            if confirm_candle['is_bearish']:
                return -1
            
            # 如果确认K线为大阳线且成交量放大,可能是错误信号
            elif confirm_candle['is_bullish'] and confirm_candle['body_size'] > 0.6:
                return 0
                
        # 其他情况保持原信号
        return initial_signal 
