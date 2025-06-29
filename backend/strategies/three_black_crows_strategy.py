import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class ThreeBlackCrowsStrategy(BaseStrategy):
    """
    顶部三鸦形(Three Black Crows)策略
    
    "顶部三鸦形"是一种强烈的顶部反转信号,通常出现在上涨趋势末端,预示着空方力量强势归来。
    
    核心特征:
    1. 连续三根中小阴线,依次排列,每根K线的收盘价低于前一日收盘价
    2. 每根K线的开盘价在前一日阴线实体范围内(无跳空),形成"逐级下跌"态势
    3. 阴线实体长度相近,上下影线较短,表明空方主导,多方无有效抵抗
    4. 成交量可温和放大(抛压递增)或缩量(阴跌式见顶),但放量下跌时信号更强
    
    根据出现的位置,信号强度和操作建议不同:
    
    1. 高位三鸦:
       - 出现在大幅上涨后的高位区域,重要压力位下方,或上升趋势线破位后
       - 信号最强,通常是明确的顶部反转信号,应及时减仓或清仓
       
    2. 中继位置的三鸦:
       - 出现在下跌趋势中的反弹后,表示下跌趋势将继续
       - 适合持币观望或加大空头仓位
       
    3. 低位三鸦:
       - 罕见情况,出现在长期下跌后的底部区域
       - 信号较弱,可能是洗盘行为,需结合其他指标综合判断
       
    该策略生成以下信号:
    - 1 (买入信号):罕见,只在低位缩量三鸦形后出现止跌信号时产生
    - -1 (卖出信号):高位或中继位置的三鸦形,明确的卖出信号
    - 0 (观望):无明显信号或确认条件不足
    """
    
    def __init__(self, parameters=None):
        """
        初始化顶部三鸦形策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "顶部三鸦形策略"
        self.description = "基于三根连续阴线组成的顶部反转形态的交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'min_body_size_ratio': 0.5,        # 实体占整个K线的最小比例(50%)
            'max_shadow_ratio': 0.3,           # 上下影线占实体的最大比例(30%)
            'max_open_close_gap': 0.02,        # 开盘价与前一日收盘价的最大偏离(2%)
            'min_price_decrease': 0.01,        # 每根K线最小跌幅(1%)
            'body_similarity_threshold': 0.7,  # 实体长度相似度阈值(70%)
            'up_trend_bars': 5,                # 上涨趋势确认K线数量
            'up_trend_threshold': 0.05,        # 上涨趋势确认阈值(5%)
            'volume_increase_threshold': 0.1,  # 放量阈值(10%)
            'volume_decrease_threshold': 0.1,  # 缩量阈值(10%)
            'look_back_period': 60,            # 历史回溯判断位置的周期
            'high_position_threshold': 0.9,    # 高位判断阈值(90%)
            'low_position_threshold': 0.2,     # 低位判断阈值(20%)
            'use_ma_confirmation': True,       # 是否使用均线确认
            'ma5_period': 5,                   # 5日均线周期
            'ma20_period': 20,                 # 20日均线周期
            'ma60_period': 60,                 # 60日均线周期
            'stop_loss_pct': 0.07,             # 止损百分比(7%)
            'high_position_target_r': 2.0,     # 高位目标风险收益比
            'low_position_target_r': 0.5,      # 低位目标风险收益比
            'use_macd_confirmation': True,     # 是否使用MACD确认
            'use_rsi_confirmation': True,      # 是否使用RSI确认
            'rsi_overbought': 70,              # RSI超买阈值
            'confirmation_days': 1             # 形态确认的观察天数
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'min_body_size_ratio': {'min': 0.4, 'max': 0.7, 'step': 0.05},
            'max_shadow_ratio': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'max_open_close_gap': {'min': 0.01, 'max': 0.05, 'step': 0.01},
            'min_price_decrease': {'min': 0.005, 'max': 0.02, 'step': 0.005},
            'body_similarity_threshold': {'min': 0.6, 'max': 0.9, 'step': 0.05},
            'up_trend_bars': {'min': 3, 'max': 10, 'step': 1},
            'up_trend_threshold': {'min': 0.03, 'max': 0.1, 'step': 0.01},
            'volume_increase_threshold': {'min': 0.05, 'max': 0.3, 'step': 0.05},
            'volume_decrease_threshold': {'min': 0.05, 'max': 0.3, 'step': 0.05},
            'high_position_threshold': {'min': 0.8, 'max': 0.95, 'step': 0.05},
            'low_position_threshold': {'min': 0.1, 'max': 0.3, 'step': 0.05},
            'stop_loss_pct': {'min': 0.05, 'max': 0.1, 'step': 0.01},
            'rsi_overbought': {'min': 60, 'max': 80, 'step': 5}
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
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['shadow_ratio'] = (df['upper_shadow'] + df['lower_shadow']) / df[['close', 'open']].apply(
            lambda x: abs(x[0] - x[1]) if abs(x[0] - x[1]) > 0 else 0.001, axis=1)
        
        # 计算移动平均线
        if self.parameters['use_ma_confirmation']:
            df['ma5'] = df['close'].rolling(window=self.parameters['ma5_period']).mean()
            df['ma20'] = df['close'].rolling(window=self.parameters['ma20_period']).mean()
            df['ma60'] = df['close'].rolling(window=self.parameters['ma60_period']).mean()
        
        # 计算技术指标
        self._calculate_technical_indicators(df)
        
        # 初始化信号列
        df['signal'] = 0
        df['tbc_detected'] = False  # Three Black Crows detected flag
        
        # 设置回溯周期
        look_back = self.parameters['look_back_period']
        prior_bars = self.parameters['up_trend_bars']
        
        # 需要足够的数据才能开始分析
        min_required_bars = max(look_back, prior_bars, self.parameters['ma60_period'] if self.parameters['use_ma_confirmation'] else 0) + 3
        if len(df) < min_required_bars:
            logger.warning(f"数据不足,无法完整分析顶部三鸦形态,需要至少{min_required_bars}根K线")
            return pd.Series(0, index=data.index)
        
        # 检测顶部三鸦形态
        for i in range(prior_bars + 3, len(df)):
            # 跳过已经检测到形态的区域
            if i >= 3 and df['tbc_detected'].iloc[i-1]:
                continue
                
            # 提取用于模式识别的K线
            window3 = df.iloc[i-3:i]  # 最近三根K线
            
            # 检查三根K线是否均为阴线
            bearish_candles = window3['is_bearish'].all()
            if not bearish_candles:
                continue
            
            # 检查每根K线收盘价是否低于前一日收盘价
            closes = window3['close'].values
            if not (closes[1] < closes[0] and closes[2] < closes[1]):
                continue
            
            # 检查开盘价是否在前一根K线实体内或接近收盘价
            opens = window3['open'].values
            prev_closes = [window3['close'].iloc[0], window3['close'].iloc[1]]
            prev_opens = [window3['open'].iloc[0], window3['open'].iloc[1]]
            
            open_in_range = []
            for j in range(1, 3):
                prev_high = max(prev_opens[j-1], prev_closes[j-1])
                prev_low = min(prev_opens[j-1], prev_closes[j-1])
                
                # 开盘价在前一根K线实体范围内,或偏离不超过设定阈值
                in_range = (opens[j] >= prev_low and opens[j] <= prev_high) or \
                          (abs(opens[j] - prev_closes[j-1]) / prev_closes[j-1] <= self.parameters['max_open_close_gap'])
                open_in_range.append(in_range)
            
            if not all(open_in_range):
                continue
            
            # 检查K线实体是否足够长
            if not (window3['body_size'] >= self.parameters['min_body_size_ratio']).all():
                continue
            
            # 检查影线是否足够短
            if not (window3['shadow_ratio'] <= self.parameters['max_shadow_ratio']).all():
                continue
            
            # 检查价格是否持续下降(每根K线都有一定幅度的下跌)
            price_decreases = []
            for j in range(3):
                decrease = (window3['open'].iloc[j] - window3['close'].iloc[j]) / window3['open'].iloc[j]
                price_decreases.append(decrease >= self.parameters['min_price_decrease'])
            
            if not all(price_decreases):
                continue
            
            # 检查K线实体长度是否相似
            body_lengths = [abs(window3['open'].iloc[j] - window3['close'].iloc[j]) for j in range(3)]
            body_ratios = [min(body_lengths[i], body_lengths[j]) / max(body_lengths[i], body_lengths[j]) 
                          for i, j in [(0, 1), (1, 2), (0, 2)]]
            
            if not all(ratio >= self.parameters['body_similarity_threshold'] for ratio in body_ratios):
                continue
            
            # 分析成交量特征
            volumes = window3['volume'].values
            volume_increased = (volumes[1] > volumes[0] * (1 + self.parameters['volume_increase_threshold']) and 
                               volumes[2] > volumes[1] * (1 + self.parameters['volume_increase_threshold']))
            volume_decreased = (volumes[1] < volumes[0] * (1 - self.parameters['volume_decrease_threshold']) and 
                               volumes[2] < volumes[1] * (1 - self.parameters['volume_decrease_threshold']))
            
            # 确定成交量特征
            if volume_increased:
                volume_feature = 'increasing'
            elif volume_decreased:
                volume_feature = 'decreasing'
            else:
                volume_feature = 'neutral'
            
            # 分析前期趋势
            trend_window = df.iloc[i-prior_bars-3:i-3]
            is_uptrend = self._check_uptrend(trend_window, self.parameters['up_trend_threshold'])
            
            # 判断位置类型(高位,中继位置,低位)
            position_type = self._determine_position_type(df, i, is_uptrend)
            
            # 均线检测
            ma5_broken = False
            ma20_broken = False
            ma60_broken = False
            
            if self.parameters['use_ma_confirmation'] and i >= self.parameters['ma60_period']:
                ma5_broken = (df['close'].iloc[i-1] < df['ma5'].iloc[i-1])
                ma20_broken = (df['close'].iloc[i-1] < df['ma20'].iloc[i-1])
                ma60_broken = (df['close'].iloc[i-1] < df['ma60'].iloc[i-1] and 
                              df['close'].iloc[i-2] >= df['ma60'].iloc[i-2])
            
            # 技术指标确认
            macd_confirmation = False
            rsi_confirmation = False
            
            if self.parameters['use_macd_confirmation'] and 'macd_hist' in df.columns:
                # MACD直方图顶背离确认
                macd_confirmation = (df['macd_hist'].iloc[i-1] < df['macd_hist'].iloc[i-3] and 
                                    df['close'].iloc[i-1] < df['close'].iloc[i-3])
            
            if self.parameters['use_rsi_confirmation'] and 'rsi' in df.columns:
                # RSI超买区死叉确认
                rsi_confirmation = (df['rsi'].iloc[i-3] > self.parameters['rsi_overbought'] and 
                                   df['rsi'].iloc[i-1] < df['rsi'].iloc[i-3])
            
            # 标记已检测到形态
            df.loc[df.index[i-1], 'tbc_detected'] = True
            
            # 生成信号
            signal = self._generate_signal(
                position_type, 
                volume_feature, 
                ma5_broken,
                ma20_broken,
                ma60_broken,
                macd_confirmation,
                rsi_confirmation
            )
            
            # 应用确认规则(如果需要)
            if self.parameters['confirmation_days'] > 0 and i + self.parameters['confirmation_days'] <= len(df):
                confirmation_window = df.iloc[i:i+self.parameters['confirmation_days']]
                signal = self._apply_confirmation_rules(confirmation_window, signal, position_type, volume_feature)
            
            df.loc[df.index[i-1], 'signal'] = signal
        
        return df['signal']
    
    def _calculate_technical_indicators(self, df):
        """
        计算技术指标
        
        Args:
            df (pd.DataFrame): 数据帧
        """
        # 计算RSI
        if self.parameters['use_rsi_confirmation']:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        if self.parameters['use_macd_confirmation']:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['signal_line']
    
    def _check_uptrend(self, window, threshold):
        """
        检查是否为上涨趋势
        
        Args:
            window (pd.DataFrame): 数据窗口
            threshold (float): 上涨阈值
            
        Returns:
            bool: 是否为上涨趋势
        """
        if len(window) == 0:
            return False
            
        start_price = window['close'].iloc[0]
        end_price = window['close'].iloc[-1]
        
        # 计算价格变动幅度
        price_change = (end_price - start_price) / start_price
        
        # 判断是否为上涨趋势
        return price_change >= threshold
    
    def _determine_position_type(self, df, current_index, is_uptrend):
        """
        判断当前K线位置类型
        
        Args:
            df (pd.DataFrame): 数据帧
            current_index (int): 当前K线索引
            is_uptrend (bool): 是否处于上涨趋势
            
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
    
    def _generate_signal(self, position_type, volume_feature, ma5_broken, ma20_broken, ma60_broken, 
                        macd_confirmation, rsi_confirmation):
        """
        根据形态特征生成交易信号
        
        Args:
            position_type (str): 位置类型
            volume_feature (str): 成交量特征
            ma5_broken (bool): 是否跌破MA5
            ma20_broken (bool): 是否跌破MA20
            ma60_broken (bool): 是否跌破MA60
            macd_confirmation (bool): MACD是否确认
            rsi_confirmation (bool): RSI是否确认
            
        Returns:
            int: 交易信号 (1:买入, -1:卖出, 0:持有)
        """
        # 初始信号强度
        signal_strength = 0
        
        # 根据位置类型调整信号
        if position_type == 'high':
            # 高位三鸦形态,强卖出信号
            signal_strength -= 1
            
            # 放量下跌信号更强
            if volume_feature == 'increasing':
                signal_strength -= 0.5
                
            # 均线突破增强信号
            if ma5_broken:
                signal_strength -= 0.2
            if ma20_broken:
                signal_strength -= 0.3
            if ma60_broken:
                signal_strength -= 0.5
                
            # 指标确认增强信号
            if macd_confirmation:
                signal_strength -= 0.3
            if rsi_confirmation:
                signal_strength -= 0.3
                
        elif position_type == 'middle':
            # 中继位置,较弱卖出信号
            signal_strength -= 0.7
            
            # 放量下跌确认中继
            if volume_feature == 'increasing':
                signal_strength -= 0.3
                
            # 均线突破增强信号
            if ma20_broken:
                signal_strength -= 0.3
                
            # 指标确认
            if macd_confirmation:
                signal_strength -= 0.2
                
        elif position_type == 'low':
            # 低位三鸦形态,通常是洗盘,信号较弱
            if volume_feature == 'decreasing':
                # 低位缩量可能是探底信号
                signal_strength += 0.5
                
                # 不跌破重要均线,可能是洗盘
                if not ma20_broken and not ma60_broken:
                    signal_strength += 0.5
        
        # 确定最终信号
        if signal_strength <= -1:
            return -1  # 强卖出信号
        elif signal_strength >= 1:
            return 1   # 买入信号(罕见)
        else:
            return 0   # 中性信号
    
    def _apply_confirmation_rules(self, confirmation_window, initial_signal, position_type, volume_feature):
        """
        应用确认规则来验证信号
        
        Args:
            confirmation_window (pd.DataFrame): 确认窗口数据
            initial_signal (int): 初始信号
            position_type (str): 位置类型
            volume_feature (str): 成交量特征
            
        Returns:
            int: 最终交易信号
        """
        # 如果初始信号为0,直接返回
        if initial_signal == 0:
            return 0
            
        # 获取确认窗口的第一根K线
        confirm_candle = confirmation_window.iloc[0]
        
        # 高位卖出信号确认
        if initial_signal == -1 and position_type == 'high':
            # 如果确认K线继续下跌,增强卖出信号
            if confirm_candle['is_bearish'] and confirm_candle['close'] < confirmation_window.iloc[-1]['close']:
                return -1
                
            # 如果出现大阳线包含前一天阴线,可能是假突破,减弱信号
            elif (not confirm_candle['is_bearish'] and 
                  confirm_candle['high'] > confirmation_window.iloc[-1]['high'] and
                  confirm_candle['low'] < confirmation_window.iloc[-1]['low']):
                return 0
        
        # 低位买入信号确认
        elif initial_signal == 1 and position_type == 'low':
            # 如果确认K线为阳线且成交量放大,增强买入信号
            if (not confirm_candle['is_bearish'] and 
                confirm_candle['volume'] > confirmation_window.iloc[-1]['volume'] * 1.5):
                return 1
            else:
                # 不满足确认条件,降级为中性信号
                return 0
                
        # 其他情况保持原信号
        return initial_signal 
