import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class DoubleGreenParallelStrategy(BaseStrategy):
    """
    双绿并行形(Double Green Parallel)策略
    
    双绿并行形是一种常见的K线组合,由两根连续的阴线组成,两根阴线的实体长度相近,开盘价与收盘价区间基本平行。
    根据出现的位置和成交量特征,可分为三种信号:
    
    1. 高位双绿并行形:
       - 出现在上涨趋势末端,通常是顶部反转信号
       - 高位放量时,下跌信号更明显
       - 适宜减仓或清仓操作
    
    2. 中继位置的双绿并行形:
       - 出现在下跌趋势中,表示下跌趋势仍在延续
       - 伴随均线突破(如MA5,MA60)时信号更强
       - 适合持币观望或做空操作
    
    3. 低位双绿并行形:
       - 出现在历史底部区域
       - 如果成交量缩小,可能是探底信号
       - 需要配合其他指标确认,不宜盲目抄底
    
    该策略生成以下信号:
    - 1 (买入信号):低位缩量双绿并行形态,可能是探底信号
    - -1 (卖出信号):高位放量双绿并行形态,顶部反转信号
    - 0 (观望):位置不明确或中继位置的双绿并行形
    """
    
    def __init__(self, parameters=None):
        """
        初始化双绿并行形策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "双绿并行形策略"
        self.description = "基于双绿并行形K线组合的交易策略,根据位置和量能判断反转或中继信号"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'parallel_threshold': 0.03,        # 开盘价与收盘价平行度阈值(3%)
            'body_length_ratio': 0.7,          # 两根K线实体长度比例的最小值(70%)
            'min_body_size_ratio': 0.4,        # 阴线实体占K线的最小比例(40%)
            'volume_increase_threshold': 0.3,   # 放量阈值(30%)
            'volume_decrease_threshold': 0.3,   # 缩量阈值(30%)
            'prior_bars_to_check': 10,         # 检查前期趋势的K线数量
            'uptrend_threshold': 0.05,         # 上涨趋势确认阈值(5%)
            'downtrend_threshold': 0.05,       # 下跌趋势确认阈值(5%)
            'look_back_period': 60,            # 历史回溯判断低位的周期
            'low_position_threshold': 0.05,    # 低位判断阈值(5%)
            'use_ma_confirmation': True,       # 是否使用均线确认
            'ma5_period': 5,                   # 5日均线周期
            'ma60_period': 60,                 # 60日均线周期
            'stop_loss_pct': 0.03,             # 止损百分比(3%)
            'high_position_target_r': 2.0,     # 高位目标风险收益比
            'low_position_target_r': 1.5,      # 低位目标风险收益比
            'position_size_high': 0.0,         # 高位信号仓位比例(0%,即清仓)
            'position_size_middle': 0.0,       # 中继信号仓位比例(0%)
            'position_size_low': 0.2,          # 低位信号仓位比例(20%)
            'confirmation_days': 2             # 形态确认的观察天数
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'parallel_threshold': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'body_length_ratio': {'min': 0.6, 'max': 0.9, 'step': 0.05},
            'min_body_size_ratio': {'min': 0.3, 'max': 0.6, 'step': 0.05},
            'volume_increase_threshold': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'volume_decrease_threshold': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'prior_bars_to_check': {'min': 5, 'max': 20, 'step': 1},
            'uptrend_threshold': {'min': 0.03, 'max': 0.1, 'step': 0.01},
            'downtrend_threshold': {'min': 0.03, 'max': 0.1, 'step': 0.01},
            'look_back_period': {'min': 30, 'max': 120, 'step': 10},
            'low_position_threshold': {'min': 0.03, 'max': 0.1, 'step': 0.01},
            'stop_loss_pct': {'min': 0.02, 'max': 0.05, 'step': 0.005}
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
        df['is_bearish'] = df['close'] < df['open']
        
        # 计算移动平均线
        if self.parameters['use_ma_confirmation']:
            df['ma5'] = df['close'].rolling(window=self.parameters['ma5_period']).mean()
            df['ma60'] = df['close'].rolling(window=self.parameters['ma60_period']).mean()
        
        # 初始化信号列
        df['signal'] = 0
        df['dgp_detected'] = False  # Double Green Parallel detected flag
        
        # 设置回溯周期
        look_back = self.parameters['look_back_period']
        prior_bars = self.parameters['prior_bars_to_check']
        
        # 需要足够的数据才能开始分析
        if len(df) < max(look_back, prior_bars) + 2:
            logger.warning("数据不足,无法完整分析双绿并行形态")
            return pd.Series(0, index=data.index)
        
        # 检测双绿并行形态
        for i in range(prior_bars + 2, len(df)):
            # 跳过已经检测到形态的区域
            if i >= 2 and df['dgp_detected'].iloc[i-1]:
                continue
                
            # 提取用于模式识别的K线
            window2 = df.iloc[i-2:i]  # 最近两根K线
            
            # 检查两根K线是否均为阴线
            bearish_candles = window2['is_bearish'].all()
            if not bearish_candles:
                continue
            
            # 计算两根K线的实体长度
            first_body_length = abs(window2['open'].iloc[0] - window2['close'].iloc[0])
            second_body_length = abs(window2['open'].iloc[1] - window2['close'].iloc[1])
            
            # 检查两根K线的实体长度是否相近
            body_length_similarity = min(first_body_length, second_body_length) / max(first_body_length, second_body_length)
            
            if body_length_similarity < self.parameters['body_length_ratio']:
                continue
            
            # 检查实体占比是否足够大
            if (window2['body_size'] < self.parameters['min_body_size_ratio']).any():
                continue
            
            # 检查开盘价和收盘价是否平行
            open_price_diff = abs(window2['open'].iloc[0] - window2['open'].iloc[1]) / window2['open'].iloc[0]
            close_price_diff = abs(window2['close'].iloc[0] - window2['close'].iloc[1]) / window2['close'].iloc[0]
            
            is_price_parallel = (open_price_diff <= self.parameters['parallel_threshold'] and 
                                close_price_diff <= self.parameters['parallel_threshold'])
            
            if not is_price_parallel:
                continue
            
            # 分析成交量特征
            volume_increased = window2['volume'].iloc[1] > window2['volume'].iloc[0] * (1 + self.parameters['volume_increase_threshold'])
            volume_decreased = window2['volume'].iloc[1] < window2['volume'].iloc[0] * (1 - self.parameters['volume_decrease_threshold'])
            
            # 确定成交量特征
            if volume_increased:
                volume_feature = 'increasing'
            elif volume_decreased:
                volume_feature = 'decreasing'
            else:
                volume_feature = 'neutral'
            
            # 分析前期趋势
            trend_window = df.iloc[i-prior_bars-2:i-2]
            is_uptrend = self._check_uptrend(trend_window, self.parameters['uptrend_threshold'])
            is_downtrend = self._check_downtrend(trend_window, self.parameters['downtrend_threshold'])
            
            # 均线检测
            ma5_broken = False
            ma60_broken = False
            
            if self.parameters['use_ma_confirmation'] and i >= self.parameters['ma60_period']:
                ma5_broken = (df['close'].iloc[i-1] < df['ma5'].iloc[i-1] and 
                             df['close'].iloc[i-2] < df['ma5'].iloc[i-2])
                ma60_broken = (df['close'].iloc[i-1] < df['ma60'].iloc[i-1] and 
                              df['close'].iloc[i-2] < df['ma60'].iloc[i-2])
            
            # 判断位置类型
            position_type = self._determine_position_type(df, i, is_uptrend, is_downtrend)
            
            # 标记已检测到双绿并行形
            df.loc[df.index[i-1], 'dgp_detected'] = True
            
            # 生成交易信号
            signal, confidence = self._generate_signal(position_type, volume_feature, 
                                                      ma5_broken, ma60_broken, body_length_similarity)
            
            df.loc[df.index[i-1], 'signal'] = signal
            
            # 应用确认规则
            if i + self.parameters['confirmation_days'] < len(df):
                confirmation_window = df.iloc[i:i+self.parameters['confirmation_days']]
                df.loc[df.index[i-1], 'signal'] = self._apply_confirmation_rules(
                    confirmation_window, signal, position_type, volume_feature)
        
        return df['signal']
    
    def _check_uptrend(self, window, threshold):
        """
        检查是否处于上涨趋势
        
        Args:
            window (pd.DataFrame): K线窗口
            threshold (float): 上涨趋势阈值
            
        Returns:
            bool: 是否处于上涨趋势
        """
        if len(window) < 2:
            return False
            
        start_price = window['close'].iloc[0]
        end_price = window['close'].iloc[-1]
        price_change = (end_price - start_price) / start_price
        
        return price_change >= threshold
    
    def _check_downtrend(self, window, threshold):
        """
        检查是否处于下跌趋势
        
        Args:
            window (pd.DataFrame): K线窗口
            threshold (float): 下跌趋势阈值
            
        Returns:
            bool: 是否处于下跌趋势
        """
        if len(window) < 2:
            return False
            
        start_price = window['close'].iloc[0]
        end_price = window['close'].iloc[-1]
        price_change = (start_price - end_price) / start_price
        
        return price_change >= threshold
    
    def _determine_position_type(self, df, current_index, is_uptrend, is_downtrend):
        """
        确定K线组合位置类型
        
        Args:
            df (pd.DataFrame): 数据
            current_index (int): 当前索引
            is_uptrend (bool): 是否处于上涨趋势
            is_downtrend (bool): 是否处于下跌趋势
            
        Returns:
            str: 位置类型 ('high', 'middle', 'low', 'neutral')
        """
        if is_uptrend:
            return 'high'  # 高位见顶
        elif is_downtrend:
            return 'middle'  # 下跌中继
        else:
            # 检查是否处于历史低位
            look_back = min(self.parameters['look_back_period'], current_index)
            historical_lows = df['low'].iloc[current_index-look_back:current_index-2]
            current_low = min(df['low'].iloc[current_index-2], df['low'].iloc[current_index-1])
            
            if len(historical_lows) > 0:
                min_low = historical_lows.min()
                if abs(current_low - min_low) / min_low <= self.parameters['low_position_threshold']:
                    return 'low'  # 低位探底
            
            return 'neutral'  # 中性位置
    
    def _generate_signal(self, position_type, volume_feature, ma5_broken, ma60_broken, body_similarity):
        """
        生成交易信号
        
        Args:
            position_type (str): 位置类型
            volume_feature (str): 成交量特征
            ma5_broken (bool): 是否跌破5日均线
            ma60_broken (bool): 是否跌破60日均线
            body_similarity (float): 实体相似度
            
        Returns:
            tuple: (信号值, 可信度)
        """
        # 基础可信度
        confidence = 0.5
        
        # 基于各种因素调整可信度
        # 1. 实体长度相似度(最多+0.1)
        confidence += min((body_similarity - self.parameters['body_length_ratio']) / 
                          (1 - self.parameters['body_length_ratio']), 1) * 0.1
        
        # 2. 位置特征和成交量配合(最多+0.2)
        if position_type == 'high' and volume_feature == 'increasing':
            confidence += 0.2  # 高位放量,见顶信号更强
        elif position_type == 'middle' and volume_feature == 'increasing':
            confidence += 0.15  # 中继位置放量,下跌延续信号更强
        elif position_type == 'low' and volume_feature == 'decreasing':
            confidence += 0.15  # 低位缩量,探底信号更强
        
        # 3. 均线突破确认(最多+0.1)
        if ma5_broken:
            confidence += 0.05  # 跌破5日均线增强信号
        if ma60_broken:
            confidence += 0.05  # 跌破60日均线增强信号
        
        # 限制最大可信度为1.0
        confidence = min(confidence, 1.0)
        
        # 生成信号
        signal = 0  # 默认为观望信号
        
        if position_type == 'high' and confidence > 0.6:
            signal = -1  # 高位形态,生成卖出信号
        elif position_type == 'middle' and confidence > 0.7:
            signal = -1  # 中继下跌形态,生成卖出信号
        elif position_type == 'low' and volume_feature == 'decreasing' and confidence > 0.7:
            signal = 1   # 低位缩量形态,生成买入信号
        
        return signal, confidence
    
    def _apply_confirmation_rules(self, confirmation_window, initial_signal, position_type, volume_feature):
        """
        应用确认规则
        
        Args:
            confirmation_window (pd.DataFrame): 确认窗口
            initial_signal (int): 初始信号
            position_type (str): 位置类型
            volume_feature (str): 成交量特征
            
        Returns:
            int: 最终信号
        """
        if len(confirmation_window) == 0:
            return initial_signal
            
        # 如果初始信号为卖出或观望
        if initial_signal <= 0:
            # 高位信号确认:如果后续出现下跌,增强卖出信号
            if position_type == 'high':
                first_close = confirmation_window['close'].iloc[0]
                last_close = confirmation_window['close'].iloc[-1]
                
                # 如果后续下跌超过1%,确认卖出信号
                if (first_close - last_close) / first_close > 0.01:
                    return -1
            
            # 中继信号确认:如果后续继续下跌并伴随放量
            if position_type == 'middle':
                first_close = confirmation_window['close'].iloc[0]
                last_close = confirmation_window['close'].iloc[-1]
                volume_increased = confirmation_window['volume'].iloc[-1] > confirmation_window['volume'].iloc[0] * 1.1
                
                if (first_close - last_close) / first_close > 0.02 and volume_increased:
                    return -1
        
        # 如果初始信号为买入
        if initial_signal > 0:
            # 低位信号确认:如果后续出现企稳或反弹,增强买入信号
            if position_type == 'low' and volume_feature == 'decreasing':
                first_close = confirmation_window['close'].iloc[0]
                last_close = confirmation_window['close'].iloc[-1]
                
                # 如果后续企稳或反弹,确认买入信号
                if last_close >= first_close * 0.995:  # 允许-0.5%的波动
                    return 1
                else:
                    return 0  # 如果继续下跌,取消买入信号
        
        return initial_signal 
