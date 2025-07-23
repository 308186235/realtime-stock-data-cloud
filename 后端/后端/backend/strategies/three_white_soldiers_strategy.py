import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class ThreeWhiteSoldiersStrategy(BaseStrategy):
    """
    三个白武士(Three White Soldiers)策略
    
    "三个白武士"是强势看涨信号,由三根连续的中阳线或大阳线组成,常见于下跌趋势末端或上涨初期。
    
    核心特征:
    1. 三根阳线实体较长(单日涨幅3%-6%),收盘价逐日创新高,且上影线极短或无(表明多方占据绝对优势)
    2. 后一根阳线的开盘价不低于前一根阳线的收盘价(允许小幅低开但迅速高走)
    3. 成交量逐次温和放大(较前5日均值增加30%以上),显示买盘持续强劲
    4. 多出现在历史低位,重要支撑位或上涨中继调整后
    
    该策略生成以下信号:
    - 1 (买入信号):低位或中位反转三个白武士,表示强势多方进入信号,适合大幅加仓或入场
    - -1 (卖出信号):高位出现三个白武士但量能异常或乖离率过高,为潜在滞涨信号,需减仓或离场
    - 0 (观望):无明显形态或形态不完整
    """
    
    def __init__(self, parameters=None):
        """
        初始化三个白武士策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "三个白武士策略"
        self.description = "基于三个白武士K线组合的强势反转交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'min_body_size_ratio': 0.7,      # 实体占整根K线最小比例(70%)
            'max_upper_shadow_ratio': 0.1,   # 上影线占实体最大比例(10%),比红三兵更严格
            'min_price_increase': 0.03,      # 最小单日涨幅(3%),比红三兵更高
            'max_price_increase': 0.06,      # 最大单日涨幅(6%),避免过大波动
            'volume_increase_threshold': 0.3, # 量能增长阈值(较前5日均值增加30%以上)
            'max_volume_surge': 3.0,         # 单日最大放量倍数(避免天量见顶)
            'high_position_threshold': 0.8,   # 高位判断阈值(相对近期波动区间80%)
            'low_position_threshold': 0.2,    # 低位判断阈值(相对近期波动区间20%)
            'trend_bars': 10,                 # 检查趋势的K线数量
            'downtrend_threshold': 0.08,      # 下跌趋势确认阈值(下跌8%),比红三兵更严格
            'look_back_period': 60,           # 回溯周期(历史高低点判断)
            'ma_deviation_threshold': 0.15,   # 股价偏离均线阈值(15%)
            'stop_loss_pct': 0.05,            # 止损百分比(5%)
            'use_ma_confirmation': True,      # 是否使用均线确认信号
            'ma_periods': [5, 10, 20, 60],    # 均线周期设置
            'use_macd_confirmation': True,    # 是否使用MACD确认信号
            'use_rsi_confirmation': True,     # 是否使用RSI确认信号
            'rsi_oversold': 30,               # RSI超卖阈值
            'rsi_overbought': 70,             # RSI超买阈值
            'min_pattern_length': 3,          # 要求的最小连续阳线数
            'confirmation_days': 1,           # 形态确认的观察天数
            'min_total_increase': 0.09,       # 三根K线最小累计涨幅(9%),比红三兵更高
            'max_candle_gap_pct': 0.015,      # 允许的K线间最大跳空比例(1.5%)
            'gap_recovery_required': True,    # 若低开是否要求收盘价高于前收盘
            'low_position_add': 0.5,          # 低位加仓比例(50%),比红三兵更激进
            'mid_position_add': 0.3,          # 中位加仓比例(30%)
            'high_position_reduction': 0.5    # 高位减仓比例(50%)
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'min_body_size_ratio': {'min': 0.6, 'max': 0.8, 'step': 0.05},
            'max_upper_shadow_ratio': {'min': 0.05, 'max': 0.2, 'step': 0.05},
            'min_price_increase': {'min': 0.02, 'max': 0.04, 'step': 0.005},
            'volume_increase_threshold': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'high_position_threshold': {'min': 0.7, 'max': 0.9, 'step': 0.05},
            'low_position_threshold': {'min': 0.1, 'max': 0.3, 'step': 0.05},
            'downtrend_threshold': {'min': 0.05, 'max': 0.1, 'step': 0.01},
            'ma_deviation_threshold': {'min': 0.1, 'max': 0.2, 'step': 0.01},
            'rsi_oversold': {'min': 20, 'max': 40, 'step': 5},
            'rsi_overbought': {'min': 60, 'max': 80, 'step': 5},
            'min_total_increase': {'min': 0.07, 'max': 0.12, 'step': 0.01}
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
        df['body_size'] = abs(df['close'] - df['open'])
        df['total_range'] = df['high'] - df['low']
        df['body_size_ratio'] = df['body_size'] / df['total_range'].where(df['total_range'] != 0, 0.01)
        df['is_bullish'] = df['close'] > df['open']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['upper_shadow_ratio'] = df.apply(
            lambda x: x['upper_shadow'] / x['body_size'] if x['body_size'] > 0 and x['is_bullish'] else 10, 
            axis=1
        )
        df['daily_return'] = df['close'].pct_change()
        
        # 计算量能变化
        df['volume_5d_avg'] = df['volume'].rolling(window=5).mean()
        df['volume_ratio'] = df['volume'] / df['volume_5d_avg'].shift(1)
        
        # 计算移动平均线
        self._calculate_moving_averages(df)
        
        # 计算技术指标
        self._calculate_technical_indicators(df)
        
        # 初始化信号列
        df['signal'] = 0
        df['pattern_detected'] = False
        
        # 设置回溯周期
        look_back = self.parameters['look_back_period']
        trend_bars = self.parameters['trend_bars']
        
        # 需要足够的数据才能开始分析
        min_required_bars = max(look_back, trend_bars, 
                               self.parameters['ma_periods'][-1] if self.parameters['use_ma_confirmation'] else 0)
        min_required_bars = max(min_required_bars, 
                                self.parameters['min_pattern_length'] + self.parameters['confirmation_days']) + 2
                                
        if len(df) < min_required_bars:
            logger.warning(f"数据不足,无法完整分析三个白武士形态,需要至少{min_required_bars}根K线")
            return pd.Series(0, index=data.index)
        
        # 检测三个白武士形态
        min_pattern_length = self.parameters['min_pattern_length']
        for i in range(trend_bars + min_pattern_length, len(df)):
            # 跳过已经检测到的形态区域
            if i >= min_pattern_length and df['pattern_detected'].iloc[i-1]:
                continue
                
            # 提取用于模式识别的K线
            window = df.iloc[i-min_pattern_length:i]  # 最近三根K线(或指定的根数)
            
            # 检查是否连续三根阳线
            if not window['is_bullish'].all():
                continue
            
            # 检查收盘价是否逐日抬高
            closes = window['close'].values
            if not all(closes[j] > closes[j-1] for j in range(1, min_pattern_length)):
                continue
            
            # 检查单日涨幅是否符合要求(3%-6%)
            daily_returns = window['daily_return'].values[1:]  # 跳过第一个(无法计算涨跌幅)
            if not all(self.parameters['min_price_increase'] <= ret <= self.parameters['max_price_increase'] for ret in daily_returns):
                continue
            
            # 检查实体占比是否足够大(至少70%)
            if not all(window['body_size_ratio'] >= self.parameters['min_body_size_ratio']):
                continue
            
            # 检查上影线是否足够短(不超过实体的10%)
            if not all(window['upper_shadow_ratio'] <= self.parameters['max_upper_shadow_ratio']):
                continue
            
            # 检查开盘价是否符合要求(不低于前收盘或低开高走)
            valid_opens = True
            for j in range(1, min_pattern_length):
                curr_open = window['open'].iloc[j]
                prev_close = window['close'].iloc[j-1]
                
                # 如果开盘价低于前收盘价
                if curr_open < prev_close:
                    # 检查是否要求收盘价高于前收盘(低开高走)
                    if self.parameters['gap_recovery_required'] and window['close'].iloc[j] <= prev_close:
                        valid_opens = False
                        break
                    
                    # 检查低开幅度是否在允许范围内
                    gap_pct = (prev_close - curr_open) / prev_close
                    if gap_pct > self.parameters['max_candle_gap_pct']:
                        valid_opens = False
                        break
            
            if not valid_opens:
                continue
            
            # 检查累计涨幅是否满足最低要求(9%)
            total_increase = (window['close'].iloc[-1] - window['open'].iloc[0]) / window['open'].iloc[0]
            if total_increase < self.parameters['min_total_increase']:
                continue
            
            # 分析成交量特征
            volumes = window['volume'].values
            volume_ratios = window['volume_ratio'].values[-min_pattern_length:]
            
            # 检查成交量是否逐步增加(至少有两天量能明显增加)
            increased_volume_days = sum(ratio >= 1 + self.parameters['volume_increase_threshold'] for ratio in volume_ratios)
            if increased_volume_days < 2:  # 比红三兵更严格,要求至少两天放量
                continue
            
            # 检查是否有异常天量(可能是诱多陷阱)
            if any(ratio > self.parameters['max_volume_surge'] for ratio in volume_ratios):
                volume_warning = True
            else:
                volume_warning = False
            
            # 分析前期趋势
            trend_window = df.iloc[i-trend_bars-min_pattern_length:i-min_pattern_length]
            is_downtrend = self._check_downtrend(trend_window)
            
            # 判断价格位置(高位,中位,低位)
            position_type = self._determine_position_type(df, i)
            
            # 判断均线配合状态
            ma_aligned = False
            if self.parameters['use_ma_confirmation']:
                if 'ma5' in df.columns and 'ma10' in df.columns and 'ma20' in df.columns:
                    current_price = df['close'].iloc[i-1]
                    ma5 = df['ma5'].iloc[i-1]
                    ma10 = df['ma10'].iloc[i-1]
                    ma20 = df['ma20'].iloc[i-1]
                    ma60 = df['ma60'].iloc[i-1] if 'ma60' in df.columns else 0
                    
                    # 检查均线多头排列(短期均线在长期均线上方)
                    if current_price > ma5 > ma10 > ma20:
                        ma_aligned = True
                    # 或者检查是否突破关键均线(如60日线)
                    elif ma60 > 0 and current_price > ma60 and (current_price / ma60 - 1) < 0.05:
                        ma_aligned = True
            
            # 判断MACD状态
            macd_bullish = False
            if self.parameters['use_macd_confirmation'] and 'macd_hist' in df.columns:
                # MACD金叉或柱状图由负转正
                macd_hist = df['macd_hist'].iloc[i-1]
                prev_macd_hist = df['macd_hist'].iloc[i-2]
                macd = df['macd'].iloc[i-1] if 'macd' in df.columns else 0
                signal_line = df['signal_line'].iloc[i-1] if 'signal_line' in df.columns else 0
                
                macd_bullish = (macd_hist > 0 and prev_macd_hist <= 0) or \
                               (macd > signal_line and macd_hist > 0 and macd_hist > prev_macd_hist)
            
            # 判断RSI状态
            rsi_status = "neutral"
            if self.parameters['use_rsi_confirmation'] and 'rsi' in df.columns:
                rsi = df['rsi'].iloc[i-1]
                if rsi < self.parameters['rsi_oversold']:
                    rsi_status = "oversold"
                elif rsi > self.parameters['rsi_overbought']:
                    rsi_status = "overbought"
            
            # 计算乖离率(用于判断是否过度偏离均线)
            deviation = 0
            if 'ma20' in df.columns:
                current_price = df['close'].iloc[i-1]
                ma20 = df['ma20'].iloc[i-1]
                deviation = (current_price - ma20) / ma20
            
            # 根据形态特征,位置和技术指标生成信号
            signal = self._generate_signal(
                position_type=position_type,
                is_downtrend=is_downtrend,
                volume_warning=volume_warning,
                ma_aligned=ma_aligned,
                macd_bullish=macd_bullish,
                rsi_status=rsi_status,
                deviation=deviation,
                total_increase=total_increase
            )
            
            # 标记检测到形态
            df.loc[df.index[i-1], 'pattern_detected'] = True
            df.loc[df.index[i-1], 'signal'] = signal
            
            # 应用确认规则(如果需要)
            if self.parameters['confirmation_days'] > 0 and i < len(df) - self.parameters['confirmation_days']:
                confirmation_window = df.iloc[i:i+self.parameters['confirmation_days']]
                confirmed_signal = self._apply_confirmation_rules(confirmation_window, signal, position_type)
                df.loc[df.index[i+self.parameters['confirmation_days']-1], 'signal'] = confirmed_signal
        
        return df['signal']
    
    def _calculate_moving_averages(self, df):
        """
        计算移动平均线
        
        Args:
            df (pd.DataFrame): 数据帧
        """
        if self.parameters['use_ma_confirmation']:
            for period in self.parameters['ma_periods']:
                df[f'ma{period}'] = df['close'].rolling(window=period).mean()
    
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
    
    def _check_downtrend(self, window):
        """
        检查是否为下跌趋势
        
        Args:
            window (pd.DataFrame): 数据窗口
            
        Returns:
            bool: 是否为下跌趋势
        """
        if len(window) < 3:
            return False
            
        start_price = window['close'].iloc[0]
        end_price = window['close'].iloc[-1]
        
        # 计算价格变动幅度
        price_change = (start_price - end_price) / start_price
        
        # 判断是否为下跌趋势
        return price_change >= self.parameters['downtrend_threshold']
    
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
    
    def _generate_signal(self, position_type, is_downtrend, volume_warning, ma_aligned, 
                         macd_bullish, rsi_status, deviation, total_increase):
        """
        根据形态特征生成交易信号
        
        Args:
            position_type (str): 位置类型 ('high', 'middle', 'low')
            is_downtrend (bool): 是否处于下跌趋势
            volume_warning (bool): 是否有成交量警示信号
            ma_aligned (bool): 均线是否有利
            macd_bullish (bool): MACD是否看涨
            rsi_status (str): RSI状态 ('oversold', 'overbought', 'neutral')
            deviation (float): 价格与均线的偏离程度
            total_increase (float): 总涨幅
            
        Returns:
            int: 交易信号 (1:买入, -1:卖出, 0:持有)
        """
        # 默认信号为0(观望)
        signal = 0
        
        # 低位三个白武士(通常是强烈的买入信号)
        if position_type == 'low':
            # 低位出现三个白武士,且处于前期下跌趋势末端,是典型的反转信号
            if is_downtrend:
                # 强化信号:RSI超卖+MACD金叉+均线看涨
                signal_strength = 0
                if rsi_status == "oversold":
                    signal_strength += 1
                if macd_bullish:
                    signal_strength += 1
                if ma_aligned:
                    signal_strength += 1
                
                # 即使没有所有指标共振,低位三个白武士也是强信号
                signal = 1  # 强烈买入信号
            else:
                # 非下跌趋势末端的低位三个白武士,可能是底部区域的突破
                if ma_aligned or macd_bullish:
                    signal = 1  # 买入信号
        
        # 中位三个白武士(通常是上涨中继信号)
        elif position_type == 'middle':
            # 上涨中继信号,结合其他指标判断
            if ma_aligned and not volume_warning:
                # 如果均线配合良好且没有异常量能,考虑加仓
                signal = 1  # 买入信号
            elif macd_bullish and not (rsi_status == "overbought"):
                # MACD看涨且未超买
                signal = 1  # 买入信号
            else:
                # 仅靠形态不足以确认信号
                signal = 0  # 观望信号
        
        # 高位三个白武士(需谨慎,可能是加速上涨也可能是滞涨信号)
        elif position_type == 'high':
            # 判断是否过度偏离均线(乖离率过高)
            excessive_deviation = deviation > self.parameters['ma_deviation_threshold']
            
            if volume_warning or rsi_status == "overbought" or excessive_deviation:
                # 如果有放量警示,RSI超买或乖离率过高,考虑减仓
                signal = -1  # 卖出信号
            elif total_increase > 0.15:  # 累计涨幅过大(超过15%)
                # 可能是短期加速拉升,存在回调风险
                signal = -1  # 轻微卖出信号
            else:
                # 没有明显风险特征的高位三个白武士,可能仍有上涨空间
                signal = 0  # 观望信号(减仓或持有)
        
        return signal
    
    def _apply_confirmation_rules(self, confirmation_window, initial_signal, position_type):
        """
        应用确认规则验证信号
        
        Args:
            confirmation_window (pd.DataFrame): 确认窗口数据
            initial_signal (int): 初始信号
            position_type (str): 位置类型
            
        Returns:
            int: 最终交易信号
        """
        # 如果初始信号为0或没有足够的确认数据,直接返回
        if initial_signal == 0 or len(confirmation_window) == 0:
            return initial_signal
        
        # 获取确认K线
        confirm_candle = confirmation_window.iloc[0]
        
        # 买入信号确认
        if initial_signal == 1:
            # 如果确认K线为阴线且跌幅超过2%,可能是假突破
            if not confirm_candle['is_bullish'] and abs(confirm_candle['daily_return']) > 0.02:
                return 0  # 取消买入信号
            
            # 如果确认K线为阳线且放量,增强买入信号
            elif confirm_candle['is_bullish'] and confirm_candle['volume_ratio'] > 1.3:
                return 1  # 确认买入信号
        
        # 卖出信号确认(高位三个白武士)
        elif initial_signal == -1 and position_type == 'high':
            # 如果确认K线为阴线,确认卖出信号
            if not confirm_candle['is_bullish']:
                return -1  # 确认卖出信号
            
            # 如果确认K线为大阳线且突破前高,可能不是真正顶部
            elif confirm_candle['is_bullish'] and confirm_candle['daily_return'] > 0.03:
                return 0  # 取消卖出信号
        
        # 默认保持原信号
        return initial_signal 
