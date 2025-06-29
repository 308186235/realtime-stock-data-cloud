import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class TripleCrashStrategy(BaseStrategy):
    """
    暴跌三杰形(Triple Crash Pattern)策略
    
    暴跌三杰形是一种强烈的下跌趋势延续或加速信号,通常由三根连续的大阴线或中阴线组成。
    
    核心特征:
    1. 三根阴线依次排列,每日收盘价均低于前一日收盘价,呈现"节节败退"的态势。
    2. 至少两根阴线为大阴线(跌幅≥3%),甚至伴随跳空低开缺口。
    3. 成交量可放大(恐慌抛售)或缩量(阴跌无承接)。
    4. 多方毫无抵抗,空方占据绝对主导,市场情绪极度悲观。
    
    该策略生成以下信号:
    - 1 (买入信号):罕见,仅在暴跌后出现明确的超跌反弹信号时
    - -1 (卖出信号):检测到暴跌三杰形后,表明下跌趋势强烈
    - 0 (观望):无明显信号
    """
    
    def __init__(self, parameters=None):
        """
        初始化暴跌三杰形策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "暴跌三杰形策略"
        self.description = "基于暴跌三杰形态的下跌趋势交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'min_big_down_pct': 0.03,        # 大阴线的最小跌幅(3%)
            'min_big_down_bars': 2,          # 至少需要的大阴线数量
            'min_total_down_pct': 0.06,      # 三日累计最小跌幅(6%)
            'volume_increase_pct': 0.3,      # 成交量放大确认阈值(30%)
            'prior_bars': 5,                 # 之前的K线考察数量
            'confirmation_days': 2,          # 形态确认的观察天数
            'stop_loss_pct': 0.03,           # 止损百分比
            'bounce_threshold': 0.02,        # 反弹确认阈值(2%)
            'oversold_rsi': 30,              # 超卖RSI阈值
            'use_rsi_filter': True,          # 是否使用RSI超卖确认
            'use_macd_filter': True,         # 是否使用MACD确认
            'position_size': 0.2,            # 轻仓反弹的仓位比例
            'bounce_target_ratio': 0.5       # 反弹目标为下跌幅度的比例(如50%)
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'min_big_down_pct': {'min': 0.02, 'max': 0.05, 'step': 0.005},
            'min_big_down_bars': {'min': 1, 'max': 3, 'step': 1},
            'min_total_down_pct': {'min': 0.04, 'max': 0.1, 'step': 0.01},
            'volume_increase_pct': {'min': 0.2, 'max': 0.5, 'step': 0.05},
            'prior_bars': {'min': 3, 'max': 10, 'step': 1},
            'confirmation_days': {'min': 1, 'max': 3, 'step': 1},
            'stop_loss_pct': {'min': 0.02, 'max': 0.05, 'step': 0.005},
            'bounce_threshold': {'min': 0.01, 'max': 0.04, 'step': 0.005},
            'oversold_rsi': {'min': 20, 'max': 40, 'step': 5},
            'position_size': {'min': 0.1, 'max': 0.3, 'step': 0.05},
            'bounce_target_ratio': {'min': 0.3, 'max': 0.7, 'step': 0.1}
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
        
        # 计算每日跌幅百分比
        df['down_pct'] = (df['open'] - df['close']) / df['open']
        df['down_pct'] = df['down_pct'].where(df['close'] < df['open'], 0)
        
        # 检查K线是否为阴线
        df['is_negative'] = df['close'] < df['open']
        
        # 检查是否为大阴线(跌幅≥3%)
        df['is_big_down'] = df['down_pct'] >= self.parameters['min_big_down_pct']
        
        # 计算收盘价变化
        df['close_change'] = df['close'].pct_change()
        
        # 计算技术指标(用于确认或反弹判断)
        self._calculate_technical_indicators(df)
        
        # 初始化信号列
        df['signal'] = 0
        
        # 标记跳空缺口
        df['gap_down'] = (df['high'] < df['low'].shift(1)) & df['is_negative']
        
        # 检测暴跌三杰形
        for i in range(self.parameters['prior_bars'] + 3, len(df)):
            # 提取最近三根K线
            window = df.iloc[i-3:i]
            
            # 检查三根K线是否均为阴线
            if not all(window['is_negative']):
                continue
                
            # 检查每日收盘价是否均低于前一日收盘价
            closes = window['close'].values
            if not (closes[1] < closes[0] and closes[2] < closes[1]):
                continue
                
            # 计算大阴线数量
            big_down_count = window['is_big_down'].sum()
            if big_down_count < self.parameters['min_big_down_bars']:
                continue
                
            # 计算三日累计跌幅
            total_down_pct = (window['open'].iloc[0] - window['close'].iloc[2]) / window['open'].iloc[0]
            if total_down_pct < self.parameters['min_total_down_pct']:
                continue
                
            # 检查是否存在跳空缺口
            has_gap_down = window['gap_down'].any()
            
            # 成交量分析
            volume_data = window['volume'].values
            volume_change1 = volume_data[1] / volume_data[0] - 1
            volume_change2 = volume_data[2] / volume_data[1] - 1
            
            # 成交量放大(恐慌抛售)
            volume_increasing = (volume_change1 > self.parameters['volume_increase_pct']) or \
                                (volume_change2 > self.parameters['volume_increase_pct'])
            
            # 成交量萎缩(阴跌无承接)
            avg_volume = (volume_data[0] + volume_data[1]) / 2
            volume_shrinking = volume_data[2] < avg_volume * 0.8
            
            # 计算暴跌三杰形态的可信度
            confidence = self._calculate_pattern_confidence(
                big_down_count, 
                total_down_pct,
                has_gap_down,
                volume_increasing,
                volume_shrinking,
                df, 
                i
            )
            
            # 计算关键价格水平
            support_level = window[['low']].min().iloc[0]
            bounce_target_1 = window['close'].iloc[2] + total_down_pct * window['open'].iloc[0] * 0.382  # 38.2%回抽目标
            bounce_target_2 = window['close'].iloc[2] + total_down_pct * window['open'].iloc[0] * 0.5    # 50%回抽目标
            stop_loss = window['low'].iloc[2] * (1 - self.parameters['stop_loss_pct'])
            breakdown_target = window['close'].iloc[2] * (1 - total_down_pct)  # 延续目标
            
            # 检查是否为超跌区域(跌幅超过15%)
            is_oversold = total_down_pct >= 0.15
            
            # 如果是超跌区域且RSI超卖,可能有反弹机会(信号为弱买入)
            if is_oversold and df['rsi'].iloc[i] < self.parameters['oversold_rsi']:
                # 观察前边的5根K线是否已经有过类似的暴跌模式
                prior_pattern_window = df.iloc[i-8:i-3]
                prior_pattern = (prior_pattern_window['is_negative'].sum() >= 3) and \
                                (prior_pattern_window['is_big_down'].sum() >= 2)
                                
                # 如果之前已经有过类似暴跌,当前又处于超跌状态,可能是反弹机会
                if prior_pattern:
                    df.loc[df.index[i], 'signal'] = 0.5  # 弱买入信号(反弹机会)
                    df.loc[df.index[i], 'pattern_type'] = 'triple_crash_oversold'
                    df.loc[df.index[i], 'pattern_confidence'] = confidence * 0.7  # 降低可信度
                    df.loc[df.index[i], 'stop_loss'] = stop_loss
                    df.loc[df.index[i], 'bounce_target'] = bounce_target_1
                else:
                    df.loc[df.index[i], 'signal'] = -1  # 卖出信号
                    df.loc[df.index[i], 'pattern_type'] = 'triple_crash'
                    df.loc[df.index[i], 'pattern_confidence'] = confidence
                    df.loc[df.index[i], 'stop_loss'] = None
                    df.loc[df.index[i], 'breakdown_target'] = breakdown_target
            else:
                # 正常情况下暴跌三杰形为强烈卖出信号
                df.loc[df.index[i], 'signal'] = -1
                df.loc[df.index[i], 'pattern_type'] = 'triple_crash'
                df.loc[df.index[i], 'pattern_confidence'] = confidence
                df.loc[df.index[i], 'stop_loss'] = None
                df.loc[df.index[i], 'breakdown_target'] = breakdown_target
            
            # 记录形态特征
            df.loc[df.index[i], 'triple_crash_detected'] = True
            df.loc[df.index[i], 'big_down_count'] = big_down_count
            df.loc[df.index[i], 'total_down_pct'] = total_down_pct
            df.loc[df.index[i], 'has_gap_down'] = has_gap_down
            df.loc[df.index[i], 'volume_pattern'] = 'increasing' if volume_increasing else ('shrinking' if volume_shrinking else 'neutral')
            
            # 记录关键价格水平
            df.loc[df.index[i], 'support_level'] = support_level
            df.loc[df.index[i], 'bounce_target_1'] = bounce_target_1
            df.loc[df.index[i], 'bounce_target_2'] = bounce_target_2
        
        # 检测反弹信号(第四天出现止跌信号)
        self._detect_bounce_signals(df)
        
        # 应用形态确认规则
        if self.parameters['confirmation_days'] > 0:
            self._apply_confirmation_rules(df)
        
        return df['signal']
    
    def _calculate_technical_indicators(self, df):
        """
        计算用于确认的技术指标(RSI和MACD)
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            None (直接修改df)
        """
        # 计算RSI
        window = 14
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss.replace(0, 0.001)  # 避免除以零
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI超卖区(低于30)
        df['rsi_oversold'] = df['rsi'] < self.parameters['oversold_rsi']
        
        # 计算MACD
        if self.parameters['use_macd_filter']:
            # 计算EMA
            df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # 计算MACD线和信号线
            df['macd_line'] = df['ema12'] - df['ema26']
            df['signal_line'] = df['macd_line'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd_line'] - df['signal_line']
            
            # MACD柱状图变化率(用于判断动能减弱)
            df['macd_hist_chg'] = df['macd_histogram'].pct_change()
            
            # 检测MACD底背离
            df['macd_divergence'] = self._detect_macd_divergence(df)
    
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
    
    def _calculate_pattern_confidence(self, big_down_count, total_down_pct, has_gap_down, 
                                    volume_increasing, volume_shrinking, df, index):
        """
        计算暴跌三杰形态的可信度
        
        Args:
            big_down_count (int): 大阴线数量
            total_down_pct (float): 总跌幅
            has_gap_down (bool): 是否存在跳空缺口
            volume_increasing (bool): 成交量是否放大
            volume_shrinking (bool): 成交量是否萎缩
            df (pd.DataFrame): 市场数据
            index (int): 当前检查的索引
            
        Returns:
            float: 可信度评分 [0,1]
        """
        # 基础可信度为0.5
        confidence = 0.5
        
        # 1. 大阴线数量(最多+0.15)
        confidence += (big_down_count / 3) * 0.15
        
        # 2. 总跌幅(最多+0.15)
        min_total_pct = self.parameters['min_total_down_pct']
        confidence += min(total_down_pct / min_total_pct, 2) * 0.075
        
        # 3. 存在跳空缺口(最多+0.1)
        confidence += has_gap_down * 0.1
        
        # 4. 成交量特征(最多+0.1)
        if volume_increasing:
            confidence += 0.1  # 成交量放大,恐慌抛售
        elif volume_shrinking:
            confidence += 0.05  # 成交量萎缩,阴跌无承接
        
        # 5. 技术指标确认
        if self.parameters['use_rsi_filter'] and df['rsi_oversold'].iloc[index]:
            confidence += 0.05  # RSI超卖
        
        if self.parameters['use_macd_filter'] and 'macd_histogram' in df.columns:
            # MACD柱状图连续两日为负,且下跌动能加大
            hist_vals = df['macd_histogram'].iloc[index-2:index+1]
            if all(val < 0 for val in hist_vals) and hist_vals.iloc[-1] < hist_vals.iloc[-2]:
                confidence += 0.05
        
        # 限制最大可信度为1.0
        confidence = min(confidence, 1.0)
        
        return confidence
    
    def _detect_bounce_signals(self, df):
        """
        检测暴跌三杰形态后的反弹信号
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            None (直接修改df)
        """
        for i in range(4, len(df)):
            # 检查前一天是否为暴跌三杰形
            if i-1 >= 0 and df['triple_crash_detected'].iloc[i-1] == True:
                current_day = df.iloc[i]
                
                # 检查是否出现止跌信号:
                # 1. 长下影线 - 下影线长度超过实体的2倍
                has_long_lower_shadow = False
                if current_day['close'] > current_day['open']:  # 阳线
                    body_size = current_day['close'] - current_day['open']
                    lower_shadow = current_day['open'] - current_day['low']
                    has_long_lower_shadow = lower_shadow > body_size * 2
                else:  # 阴线
                    body_size = current_day['open'] - current_day['close']
                    lower_shadow = current_day['close'] - current_day['low']
                    has_long_lower_shadow = lower_shadow > body_size * 2
                
                # 2. 是否为十字星形态(开盘价和收盘价接近)
                is_doji = abs(current_day['close'] - current_day['open']) / (current_day['high'] - current_day['low']) < 0.1
                
                # 3. 明显的阳线反弹(大于2%)
                is_strong_bounce = (current_day['close'] > current_day['open']) and \
                                  ((current_day['close'] - current_day['open']) / current_day['open'] > self.parameters['bounce_threshold'])
                
                # 4. 成交量特征 - 成交量放大但价格企稳
                vol_increased = current_day['volume'] > df['volume'].iloc[i-1] * 1.3
                price_stabilized = current_day['close'] >= df['close'].iloc[i-1] * 0.99
                volume_confirmation = vol_increased and price_stabilized
                
                # 5. 技术指标确认
                rsi_confirmation = current_day['rsi'] < 30 and current_day['rsi'] > df['rsi'].iloc[i-1]
                
                # 汇总反弹信号
                has_bounce_signal = (has_long_lower_shadow or is_doji or is_strong_bounce) and \
                                   (volume_confirmation or rsi_confirmation)
                
                if has_bounce_signal:
                    # 检查当前价格是否在支撑位附近(5%以内)
                    near_support = abs(current_day['low'] - df['support_level'].iloc[i-1]) / df['support_level'].iloc[i-1] <= 0.05
                    
                    # 检查是否为超跌区域
                    is_oversold = df['total_down_pct'].iloc[i-1] >= 0.15
                    
                    # 生成反弹信号(弱买入)
                    if near_support and is_oversold:
                        df.loc[df.index[i], 'signal'] = 1  # 买入信号(反弹)
                        df.loc[df.index[i], 'pattern_type'] = 'triple_crash_bounce'
                        # 设置止损和目标价
                        df.loc[df.index[i], 'stop_loss'] = current_day['low'] * 0.98
                        df.loc[df.index[i], 'bounce_target'] = current_day['close'] + \
                                                             (df['bounce_target_1'].iloc[i-1] - current_day['close']) * \
                                                             self.parameters['bounce_target_ratio']
    
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
        
        # 记录止损位和目标价
        df['confirmed_stop_loss'] = np.nan
        df['confirmed_target'] = np.nan
        
        for i in range(len(df) - 1, self.parameters['confirmation_days'], -1):
            # 卖出信号 (Triple Crash Pattern)
            if df['original_signal'].iloc[i] == -1:
                # 检查后续几天是否确认形态
                confirmed = True
                for j in range(1, min(self.parameters['confirmation_days'] + 1, len(df) - i)):
                    next_day = df.iloc[i + j]
                    
                    # 如果后续几天价格持续上涨,形态可能失效
                    if next_day['close'] > next_day['open'] and next_day['close'] > df['close'].iloc[i]:
                        # 如果突破前一天的高点,形态可能失效
                        if next_day['close'] > df['high'].iloc[i]:
                            confirmed = False
                            break
                
                # 调整当前信号
                if not confirmed:
                    df.loc[df.index[i], 'signal'] = 0  # 取消假信号
                
            # 买入信号 (Bounce after Triple Crash)
            elif df['original_signal'].iloc[i] == 1:
                # 检查后续几天是否确认形态
                confirmed = True
                for j in range(1, min(self.parameters['confirmation_days'] + 1, len(df) - i)):
                    next_day = df.iloc[i + j]
                    
                    # 如果后续几天价格破位下跌,超过止损线,反弹信号失效
                    if 'stop_loss' in df.columns and not pd.isna(df['stop_loss'].iloc[i]):
                        if next_day['low'] < df['stop_loss'].iloc[i]:
                            confirmed = False
                            break
                
                # 调整当前信号
                if not confirmed:
                    df.loc[df.index[i], 'signal'] = 0  # 取消假信号 
