import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class MorningStarStrategy(BaseStrategy):
    """
    曙光初现(Morning Star)策略
    
    曙光初现是股价在下跌趋势中出现的底部反转信号,通常由两根K线组合而成。
    
    核心特征:
    1. 第一根K线:为大阴线或中阴线,延续前期下跌趋势,市场情绪悲观。
    2. 第二根K线:次日股价低开,但随后大幅反弹,收出大阳线或中阳线,且阳线收盘价深入第一根阴线实体的1/2以上。
    3. 量能配合:第二根阳线的成交量较前一日放大,显示买盘积极介入。
    
    该策略生成以下信号:
    - 1 (买入信号):检测到曙光初现形态
    - -1 (卖出信号):罕见,主要在反弹后期出现见顶信号时
    - 0 (观望):无明显信号
    """
    
    def __init__(self, parameters=None):
        """
        初始化曙光初现策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "曙光初现策略"
        self.description = "基于曙光初现形态的底部反转交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'downtrend_window': 5,          # 下跌趋势确认窗口大小
            'downtrend_threshold': 0.03,    # 下跌趋势确认阈值(例如3%的下跌)
            'penetration_ratio': 0.5,       # 阳线对阴线的穿透比例(默认50%)
            'ideal_penetration': 0.6,       # 理想穿透比例(60%)
            'volume_increase': 0.3,         # 成交量增加比例(例如30%)
            'min_body_size_ratio': 0.5,     # 最小实体比例(实体占整个K线的比例)
            'confirmation_days': 2,         # 形态确认的观察天数
            'stop_loss_pct': 0.03,          # 止损百分比
            'take_profit_atr_multiple': 2,  # 获利目标(ATR的倍数)
            'risk_reward_ratio': 2.0,       # 风险收益比,确定是否执行交易
            'position_initial': 0.2,        # 初始仓位比例(如20%)
            'position_add': 0.3,            # 加仓仓位比例(如30%)
            'use_macd_confirm': True,       # 是否使用MACD底背离确认
            'use_rsi_confirm': True         # 是否使用RSI超卖确认
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'downtrend_window': {'min': 3, 'max': 10, 'step': 1},
            'downtrend_threshold': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'penetration_ratio': {'min': 0.3, 'max': 0.7, 'step': 0.05},
            'volume_increase': {'min': 0.1, 'max': 0.5, 'step': 0.05},
            'min_body_size_ratio': {'min': 0.4, 'max': 0.8, 'step': 0.05},
            'confirmation_days': {'min': 1, 'max': 3, 'step': 1},
            'stop_loss_pct': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'take_profit_atr_multiple': {'min': 1, 'max': 4, 'step': 0.5},
            'risk_reward_ratio': {'min': 1.0, 'max': 3.0, 'step': 0.25},
            'position_initial': {'min': 0.1, 'max': 0.5, 'step': 0.05}
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
        
        # 计算实体大小比例 (实体/整个K线的比例)
        df['body_size'] = abs(df['close'] - df['open']) / (df['high'] - df['low'])
        
        # 计算ATR,用于设置止损和止盈位置
        df['tr'] = self._calculate_true_range(df)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # 检查是否为阳线/阴线
        df['is_bullish'] = df['close'] > df['open']
        df['is_bearish'] = df['close'] < df['open']
        
        # 检查下跌趋势
        df['downtrend'] = self._detect_downtrend(df)
        
        # 计算技术指标(用于确认)
        if self.parameters['use_macd_confirm'] or self.parameters['use_rsi_confirm']:
            self._calculate_technical_indicators(df)
        
        # 初始化信号列
        df['signal'] = 0
        
        # 寻找曙光初现形态
        for i in range(self.parameters['downtrend_window'] + 1, len(df)):
            # 只在下跌趋势中寻找曙光初现
            if not df['downtrend'].iloc[i-1]:
                continue
                
            # 获取前两根K线
            first_day = df.iloc[i-1]  # 阴线
            current_day = df.iloc[i]  # 阳线
            
            # 检查第一天是否为阴线且实体较大
            if not first_day['is_bearish'] or first_day['body_size'] < self.parameters['min_body_size_ratio']:
                continue
                
            # 检查第二天是否为阳线
            if not current_day['is_bullish']:
                continue
                
            # 检查第二天是否低开
            if current_day['open'] >= first_day['close']:
                continue
                
            # 计算第一天的实体中点
            first_day_midpoint = (first_day['open'] + first_day['close']) / 2
            
            # 检查阳线是否深入阴线实体50%以上
            if current_day['close'] <= first_day_midpoint:
                continue
                
            # 计算阳线的穿透比例
            penetration = (current_day['close'] - first_day['close']) / (first_day['open'] - first_day['close'])
            
            # 检查穿透比例是否满足要求
            if penetration < self.parameters['penetration_ratio']:
                continue
                
            # 检查成交量是否增加
            volume_change = current_day['volume'] / first_day['volume'] - 1
            volume_increased = volume_change >= self.parameters['volume_increase']
            
            # 是否为阳包阴形态(更强的反转信号)
            is_engulfing = current_day['close'] >= first_day['open']
            
            # 计算形态可信度
            confidence = self._calculate_pattern_confidence(
                penetration, 
                volume_change, 
                first_day['body_size'], 
                current_day['body_size'],
                is_engulfing
            )
            
            # 检查技术指标确认
            if self.parameters['use_macd_confirm'] or self.parameters['use_rsi_confirm']:
                technical_confirmed = self._check_technical_confirmation(df, i)
                # 如果需要技术指标确认但未确认,降低置信度
                if not technical_confirmed:
                    confidence *= 0.7
            
            # 如果找到形态且置信度足够高,生成买入信号
            if confidence > 0.5:  # 仅当可信度足够高时
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'pattern_confidence'] = confidence
                df.loc[df.index[i], 'stop_loss'] = min(current_day['low'], first_day['low'])
                df.loc[df.index[i], 'take_profit'] = current_day['close'] + (current_day['atr'] * self.parameters['take_profit_atr_multiple'])
                df.loc[df.index[i], 'is_engulfing'] = is_engulfing
        
        # 添加形态后的确认或否定(检查后续几天是否继续上涨或反转)
        if self.parameters['confirmation_days'] > 0:
            self._apply_confirmation_rules(df)
            
        # 添加止损和获利目标
        self._apply_stop_loss_take_profit(df)
        
        return df['signal']
    
    def _detect_downtrend(self, df):
        """
        检测下跌趋势
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            pd.Series: 布尔序列,表示每个时间点是否处于下跌趋势
        """
        window = self.parameters['downtrend_window']
        threshold = self.parameters['downtrend_threshold']
        
        # 计算滚动窗口内的价格变化
        rolling_return = df['close'].pct_change(window)
        
        # 确定下跌趋势(价格变化低于负阈值)
        downtrend = rolling_return < -threshold
        
        # 至少有3根连续下跌的K线也视为下跌趋势
        consecutive_falls = pd.Series(0, index=df.index)
        for i in range(1, len(df)):
            if df['close'].iloc[i] < df['close'].iloc[i-1]:
                consecutive_falls.iloc[i] = consecutive_falls.iloc[i-1] + 1
            else:
                consecutive_falls.iloc[i] = 0
        
        downtrend = downtrend | (consecutive_falls >= 3)
        
        return downtrend
    
    def _calculate_true_range(self, df):
        """
        计算真实波动范围(True Range)
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            pd.Series: 真实波动范围序列
        """
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['close'].shift(1))
        low_close_prev = abs(df['low'] - df['close'].shift(1))
        
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        return tr
    
    def _calculate_technical_indicators(self, df):
        """
        计算用于确认的技术指标(MACD和RSI)
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            None (直接修改df)
        """
        # 计算MACD
        if self.parameters['use_macd_confirm']:
            # 计算EMA
            df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # 计算MACD线和信号线
            df['macd_line'] = df['ema12'] - df['ema26']
            df['signal_line'] = df['macd_line'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd_line'] - df['signal_line']
            
            # 检测MACD底背离
            df['macd_divergence'] = self._detect_macd_divergence(df)
        
        # 计算RSI
        if self.parameters['use_rsi_confirm']:
            window = 14
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            
            rs = avg_gain / avg_loss.replace(0, 0.001)  # 避免除以零
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # RSI超卖区(低于30)
            df['rsi_oversold'] = df['rsi'] < 30
    
    def _detect_macd_divergence(self, df):
        """
        检测MACD底背离
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            pd.Series: 表示是否出现底背离的布尔序列
        """
        divergence = pd.Series(False, index=df.index)
        window = 20  # 寻找背离的窗口大小
        
        for i in range(window, len(df)):
            # 提取窗口内的数据
            window_df = df.iloc[i-window:i+1]
            
            # 找到价格的低点
            price_lows = window_df[window_df['close'] == window_df['close'].min()]
            
            if len(price_lows) < 1:
                continue
                
            price_low_idx = price_lows.index[-1]
            price_low_val = window_df.loc[price_low_idx, 'close']
            
            # 找到MACD的低点
            macd_lows = window_df[window_df['macd_line'] == window_df['macd_line'].min()]
            
            if len(macd_lows) < 1:
                continue
                
            macd_low_idx = macd_lows.index[-1]
            macd_low_val = window_df.loc[macd_low_idx, 'macd_line']
            
            # 检查是否有新的价格低点
            if i > 0 and df['close'].iloc[i] < price_low_val:
                # 检查MACD是否没有创新低 -> 底背离
                if df['macd_line'].iloc[i] > macd_low_val:
                    divergence.iloc[i] = True
        
        return divergence
    
    def _calculate_pattern_confidence(self, penetration, volume_change, first_day_body, second_day_body, is_engulfing):
        """
        计算曙光初现形态的可信度
        
        Args:
            penetration (float): 阳线对阴线的穿透比例
            volume_change (float): 成交量变化比例
            first_day_body (float): 第一天K线实体比例
            second_day_body (float): 第二天K线实体比例
            is_engulfing (bool): 是否为阳包阴形态
            
        Returns:
            float: 可信度评分 [0,1]
        """
        # 计算穿透深度得分 (最大贡献50%)
        # 如果是阳包阴形态,直接给满分
        penetration_score = 0.5 if is_engulfing else min(penetration / self.parameters['penetration_ratio'], 1.5) * 0.5
        
        # 计算成交量得分 (最大贡献30%)
        volume_score = min(volume_change / self.parameters['volume_increase'], 1.5) * 0.3 if volume_change > 0 else 0
        
        # 计算K线形态得分 (最大贡献20%)
        body_score = (first_day_body + second_day_body) / 2 * 0.2
        
        # 计算总体可信度
        confidence = min(penetration_score + volume_score + body_score, 1.0)
        
        return confidence
    
    def _check_technical_confirmation(self, df, index):
        """
        检查技术指标是否确认形态
        
        Args:
            df (pd.DataFrame): 市场数据
            index (int): 当前检查的索引
            
        Returns:
            bool: 是否有技术确认
        """
        macd_confirmed = True
        rsi_confirmed = True
        
        if self.parameters['use_macd_confirm']:
            # MACD底背离或直方图转正
            macd_confirmed = df['macd_divergence'].iloc[index] or df['macd_histogram'].iloc[index] > 0
        
        if self.parameters['use_rsi_confirm']:
            # RSI超卖或从超卖区回升
            rsi_confirmed = df['rsi_oversold'].iloc[index] or (
                df['rsi_oversold'].iloc[index-1] and df['rsi'].iloc[index] > df['rsi'].iloc[index-1]
            )
        
        # 如果两个都设置了,至少一个要确认;如果只设置了一个,那个必须确认
        if self.parameters['use_macd_confirm'] and self.parameters['use_rsi_confirm']:
            return macd_confirmed or rsi_confirmed
        elif self.parameters['use_macd_confirm']:
            return macd_confirmed
        elif self.parameters['use_rsi_confirm']:
            return rsi_confirmed
        else:
            return True  # 如果没有设置技术确认,返回True
    
    def _apply_confirmation_rules(self, df):
        """
        应用形态确认规则,检查后续几天的走势是否确认或否定形态
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            None (直接修改df)
        """
        # 临时保存原始信号
        df['original_signal'] = df['signal'].copy()
        
        # 记录止损位和获利目标
        df['pattern_stop_loss'] = np.nan
        df['pattern_take_profit'] = np.nan
        
        for i in range(len(df) - 1, self.parameters['confirmation_days'], -1):
            if df['original_signal'].iloc[i] == 1:  # 找到买入信号
                # 保存形态对应的止损位和获利目标
                stop_loss = min(df['low'].iloc[i], df['low'].iloc[i-1])  # 形态最低点
                take_profit = df['close'].iloc[i] + (df['close'].iloc[i] - df['close'].iloc[i-1])  # 1:1目标
                
                df.loc[df.index[i], 'pattern_stop_loss'] = stop_loss
                df.loc[df.index[i], 'pattern_take_profit'] = take_profit
                
                # 检查后续几天是否确认形态
                confirmed = True
                for j in range(1, min(self.parameters['confirmation_days'] + 1, len(df) - i)):
                    next_day = df.iloc[i + j]
                    
                    # 如果后续价格跌破止损位,取消信号(可能是假突破)
                    if next_day['low'] < stop_loss:
                        confirmed = False
                        break
                    
                    # 如果后续有阴线且收盘价低于曙光初现阳线的收盘价,形态可能失效
                    if next_day['is_bearish'] and next_day['close'] < df['close'].iloc[i]:
                        # 如果跌破阳线开盘价,形态失效
                        if next_day['close'] < df['open'].iloc[i]:
                            confirmed = False
                            break
                    
                    # 如果后续连续上涨,增强信号
                    if next_day['is_bullish'] and j == 1:
                        # 提高首个确认日的信号强度
                        df.loc[df.index[i + j], 'signal'] = 0.5  # 半强度信号
                
                # 调整当前信号
                if not confirmed:
                    df.loc[df.index[i], 'signal'] = 0  # 取消假信号
    
    def _apply_stop_loss_take_profit(self, df):
        """
        应用止损和获利目标规则
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            None (直接修改df)
        """
        # 初始化持仓状态(1表示多仓,-1表示空仓,0表示无持仓)
        df['position'] = 0
        
        current_position = 0
        entry_price = 0
        stop_loss = 0
        take_profit = 0
        
        for i in range(1, len(df)):
            # 更新前一个交易日的持仓状态
            df.loc[df.index[i-1], 'position'] = current_position
            
            # 根据信号开仓
            if current_position == 0:
                if df['signal'].iloc[i] == 1:  # 买入信号
                    current_position = 1  # 建立多头
                    entry_price = df['close'].iloc[i]
                    stop_loss = df['pattern_stop_loss'].iloc[i] if not np.isnan(df['pattern_stop_loss'].iloc[i]) else df['low'].iloc[i] * (1 - self.parameters['stop_loss_pct'])
                    take_profit = df['pattern_take_profit'].iloc[i] if not np.isnan(df['pattern_take_profit'].iloc[i]) else df['close'].iloc[i] + df['atr'].iloc[i] * self.parameters['take_profit_atr_multiple']
            
            # 根据止损和获利目标平仓
            elif current_position == 1:  # 多头持仓
                # 检查是否触发止损
                if df['low'].iloc[i] <= stop_loss:
                    current_position = 0  # 平仓
                    df.loc[df.index[i], 'signal'] = -1  # 发出止损信号
                
                # 检查是否触发获利目标
                elif df['high'].iloc[i] >= take_profit:
                    current_position = 0  # 平仓
                    df.loc[df.index[i], 'signal'] = -1  # 发出获利信号
            
            # 更新当前交易日的持仓状态
            df.loc[df.index[i], 'position'] = current_position 
