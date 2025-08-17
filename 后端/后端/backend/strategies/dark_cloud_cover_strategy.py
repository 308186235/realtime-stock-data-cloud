import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class DarkCloudCoverStrategy(BaseStrategy):
    """
    乌云盖顶(Dark Cloud Cover)策略
    
    乌云盖顶是一种经典的顶部反转K线组合形态,出现在上涨趋势末端,预示股价可能见顶回落。
    
    核心特征:
    1. 第一根K线:上涨趋势中的一根阳线(实体较长,代表多方主导)
    2. 第二根K线:次日股价高开,但随后被空方打压,收出一根阴线,且阴线实体深入第一根阳线实体的1/2以上
    3. 通常伴随成交量放大
    
    该策略生成以下信号:
    - 1 (卖出信号):检测到乌云盖顶形态
    - -1(买入信号):非常罕见,乌云盖顶为看跌信号,买入信号主要在后续观察到反包或止跌时产生
    - 0 (观望):无明显信号
    """
    
    def __init__(self, parameters=None):
        """
        初始化乌云盖顶策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "乌云盖顶策略"
        self.description = "基于乌云盖顶形态的反转交易策略"
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'uptrend_window': 5,            # 上涨趋势确认窗口大小
            'uptrend_threshold': 0.02,      # 上涨趋势确认阈值(例如2%的上涨)
            'penetration_ratio': 0.5,       # 阴线对阳线的穿透比例(默认50%)
            'volume_increase': 0.3,         # 成交量增加比例(例如30%)
            'min_body_size_ratio': 0.6,     # 最小实体比例(实体占整个K线的比例)
            'confirmation_days': 2,         # 形态确认的观察天数
            'stop_loss_pct': 0.02,          # 止损百分比
            'take_profit_atr_multiple': 2,  # 获利目标(ATR的倍数)
            'risk_reward_ratio': 2.0,       # 风险收益比,确定是否执行交易
            'recovery_threshold': 0.7       # 反转阴线的"收复"阈值
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'uptrend_window': {'min': 3, 'max': 10, 'step': 1},
            'uptrend_threshold': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'penetration_ratio': {'min': 0.3, 'max': 0.7, 'step': 0.05},
            'volume_increase': {'min': 0.1, 'max': 0.5, 'step': 0.05},
            'min_body_size_ratio': {'min': 0.4, 'max': 0.8, 'step': 0.05},
            'confirmation_days': {'min': 1, 'max': 3, 'step': 1},
            'stop_loss_pct': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'take_profit_atr_multiple': {'min': 1, 'max': 4, 'step': 0.5},
            'risk_reward_ratio': {'min': 1.0, 'max': 3.0, 'step': 0.25},
            'recovery_threshold': {'min': 0.5, 'max': 0.9, 'step': 0.05}
        }
    
    def generate_signals(self, data):
        """
        生成交易信号
        
        Args:
            data (pd.DataFrame): 包含OHLCV的历史市场数据
            
        Returns:
            pd.Series: 交易信号序列 (1:卖出, -1:买入, 0:持有)
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
        
        # 检查上涨趋势
        df['uptrend'] = self._detect_uptrend(df)
        
        # 初始化信号列
        df['signal'] = 0
        
        # 寻找乌云盖顶形态
        for i in range(self.parameters['uptrend_window'] + 1, len(df)):
            # 只在上涨趋势中寻找乌云盖顶
            if not df['uptrend'].iloc[i-1]:
                continue
                
            # 获取前两根K线
            first_day = df.iloc[i-1]
            current_day = df.iloc[i]
            
            # 检查第一天是否为阳线且实体较大
            if not first_day['is_bullish'] or first_day['body_size'] < self.parameters['min_body_size_ratio']:
                continue
                
            # 检查第二天是否为阴线
            if not current_day['is_bearish']:
                continue
                
            # 检查第二天是否高开
            if current_day['open'] <= first_day['close']:
                continue
                
            # 计算第一天的实体中点
            first_day_midpoint = (first_day['open'] + first_day['close']) / 2
            
            # 检查阴线是否深入阳线实体50%以上
            if current_day['close'] >= first_day_midpoint:
                continue
                
            # 计算阴线的穿透比例
            penetration = (first_day['close'] - current_day['close']) / (first_day['close'] - first_day['open'])
            
            # 检查穿透比例是否满足要求
            if penetration < self.parameters['penetration_ratio']:
                continue
                
            # 检查成交量是否增加
            volume_change = current_day['volume'] / first_day['volume'] - 1
            volume_increased = volume_change >= self.parameters['volume_increase']
            
            # 计算形态可信度
            confidence = self._calculate_pattern_confidence(
                penetration, 
                volume_change, 
                first_day['body_size'], 
                current_day['body_size']
            )
            
            # 如果找到形态,生成卖出信号
            if confidence > 0.5:  # 仅当可信度足够高时
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'pattern_confidence'] = confidence
                df.loc[df.index[i], 'stop_loss'] = current_day['high']
                df.loc[df.index[i], 'take_profit'] = current_day['close'] - (current_day['atr'] * self.parameters['take_profit_atr_multiple'])
        
        # 添加形态后的确认或否定(检查后续几天是否继续下跌或反转)
        if self.parameters['confirmation_days'] > 0:
            self._apply_confirmation_rules(df)
            
        # 添加止损和获利目标
        self._apply_stop_loss_take_profit(df)
        
        return df['signal']
    
    def _detect_uptrend(self, df):
        """
        检测上涨趋势
        
        Args:
            df (pd.DataFrame): 市场数据
            
        Returns:
            pd.Series: 布尔序列,表示每个时间点是否处于上涨趋势
        """
        window = self.parameters['uptrend_window']
        threshold = self.parameters['uptrend_threshold']
        
        # 计算滚动窗口内的价格变化
        rolling_return = df['close'].pct_change(window)
        
        # 确定上涨趋势(价格变化超过阈值)
        uptrend = rolling_return > threshold
        
        # 至少有3根连续上涨的K线也视为上涨趋势
        consecutive_rises = pd.Series(0, index=df.index)
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                consecutive_rises.iloc[i] = consecutive_rises.iloc[i-1] + 1
            else:
                consecutive_rises.iloc[i] = 0
        
        uptrend = uptrend | (consecutive_rises >= 3)
        
        return uptrend
    
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
    
    def _calculate_pattern_confidence(self, penetration, volume_change, first_day_body, second_day_body):
        """
        计算乌云盖顶形态的可信度
        
        Args:
            penetration (float): 阴线对阳线的穿透比例
            volume_change (float): 成交量变化比例
            first_day_body (float): 第一天K线实体比例
            second_day_body (float): 第二天K线实体比例
            
        Returns:
            float: 可信度评分 [0,1]
        """
        # 计算穿透深度得分 (最大贡献50%)
        penetration_score = min(penetration / self.parameters['penetration_ratio'], 1.5) * 0.5
        
        # 计算成交量得分 (最大贡献30%)
        volume_score = min(volume_change / self.parameters['volume_increase'], 1.5) * 0.3 if volume_change > 0 else 0
        
        # 计算K线形态得分 (最大贡献20%)
        body_score = (first_day_body + second_day_body) / 2 * 0.2
        
        # 计算总体可信度
        confidence = min(penetration_score + volume_score + body_score, 1.0)
        
        return confidence
    
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
            if df['original_signal'].iloc[i] == 1:  # 找到卖出信号
                # 保存形态对应的止损位和获利目标
                stop_loss = df['high'].iloc[i]  # 形态第二根K线的高点
                take_profit = df['close'].iloc[i] - (df['close'].iloc[i-1] - df['open'].iloc[i-1])  # 1:1目标
                
                df.loc[df.index[i], 'pattern_stop_loss'] = stop_loss
                df.loc[df.index[i], 'pattern_take_profit'] = take_profit
                
                # 检查后续几天是否确认形态
                confirmed = True
                for j in range(1, min(self.parameters['confirmation_days'] + 1, len(df) - i)):
                    next_day = df.iloc[i + j]
                    
                    # 如果后续价格突破止损位,取消信号(可能是假突破)
                    if next_day['high'] > stop_loss:
                        confirmed = False
                        break
                    
                    # 如果后续有阳线且收盘价高于乌云盖顶阴线的开盘价,形态失效
                    if next_day['is_bullish'] and next_day['close'] > df['open'].iloc[i]:
                        confirmed = False
                        break
                        
                    # 如果后续连续下跌,增强信号
                    if next_day['is_bearish'] and j == 1:
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
        # 初始化持仓状态(1表示空仓,-1表示多仓,0表示无持仓)
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
                if df['signal'].iloc[i] == 1:  # 卖出信号
                    current_position = 1  # 建立空头
                    entry_price = df['close'].iloc[i]
                    stop_loss = df['pattern_stop_loss'].iloc[i] if not np.isnan(df['pattern_stop_loss'].iloc[i]) else df['high'].iloc[i]
                    take_profit = df['pattern_take_profit'].iloc[i] if not np.isnan(df['pattern_take_profit'].iloc[i]) else df['close'].iloc[i] - df['atr'].iloc[i] * 2
            
            # 根据止损和获利目标平仓
            elif current_position == 1:  # 空头持仓
                # 检查是否触发止损
                if df['high'].iloc[i] >= stop_loss:
                    current_position = 0  # 平仓
                    df.loc[df.index[i], 'signal'] = -1  # 发出止损信号
                
                # 检查是否触发获利目标
                elif df['low'].iloc[i] <= take_profit:
                    current_position = 0  # 平仓
                    df.loc[df.index[i], 'signal'] = -1  # 发出获利信号
            
            # 更新当前交易日的持仓状态
            df.loc[df.index[i], 'position'] = current_position 
