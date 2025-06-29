import pandas as pd
import numpy as np
from backend.strategies.base_strategy import BaseStrategy
from backend.strategies.double_black_crows_detector import DoubleBlackCrowsDetector
import logging

logger = logging.getLogger(__name__)

class DoubleBlackCrowsStrategy(BaseStrategy):
    """
    双飞乌鸦(Double Black Crows)策略
    
    双飞乌鸦是一种经典的看跌K线组合,通常出现在上涨趋势末端或盘整区间的高位,
    预示着股价可能见顶回落。其形态特征为:
    
    1. 第一根K线:通常是一根高开低走的阴线(或阳线,但实体较短),留有上影线
    2. 第二根K线:再次跳高开盘,但收盘价低于第一根阴线的收盘价,形成第二根阴线
       且两根阴线呈"乌鸦"状并列,实体部分有重叠或向下倾斜
    
    该策略生成以下信号:
    - -1 (卖出/减仓信号): 在高位确认双飞乌鸦形态,且伴随放量或指标确认
    - 0 (观望): 无明显信号或形态不完整
    """
    
    def __init__(self, parameters=None):
        """
        初始化双飞乌鸦策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "双飞乌鸦策略"
        self.description = "基于双飞乌鸦K线形态的交易策略,识别高位可能回落的形态"
        self.detector = DoubleBlackCrowsDetector()
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            # 形态识别参数
            'trend_lookback': 10,             # 检查趋势的回溯天数
            'uptrend_threshold': 0.05,        # 定义上涨趋势的阈值(5%)
            'first_candle_body_ratio': 0.4,   # 第一根K线实体/影线比例最小值
            'second_open_ratio': 0.0,         # 第二根K线开盘价需高于第一根多少(0%表示高开即可)
            'overlap_threshold': 0.3,         # 第二根K线与第一根实体重叠占比
            
            # 位置判断参数
            'high_position_threshold': 0.7,   # 股价位于近期高点70%以上视为高位
            'position_lookback': 20,          # 判断位置的回溯周期
            'ma_periods': [5, 10, 20, 60],    # 用于判断位置的均线周期
            
            # 成交量判断参数
            'volume_surge_threshold': 1.5,    # 量能放大阈值(1.5倍)
            'volume_lookback': 5,             # 成交量比较回溯天数
            
            # 信号强度和确认参数
            'confirmation_days': 1,           # 确认信号所需天数
            'min_pattern_quality': 0.5,       # 最低形态质量要求(0.5)
            'high_quality_threshold': 0.75,   # 高质量形态阈值(0.75)
            'false_signal_threshold': 0.01,   # 突破前高多少视为假信号(1%)
            
            # 风险控制参数
            'stop_loss_pct': 0.03,            # 止损比例(3%)
            'initial_reduce_pct': 0.5,        # 初始减仓比例(50%)
            'ma5_ma10_cross_weight': 0.4,     # 5日均线与10日均线交叉的权重
            
            # 其他参数
            'high_vol_threshold': 0.8,        # 成交量位于高位的阈值
            'top_shadow_ratio': 0.5,          # 上影线/实体比例阈值
            'macd_weight': 0.3                # MACD指标的权重
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'uptrend_threshold': {'min': 0.03, 'max': 0.08, 'step': 0.01},
            'high_position_threshold': {'min': 0.6, 'max': 0.8, 'step': 0.05},
            'volume_surge_threshold': {'min': 1.2, 'max': 1.8, 'step': 0.1},
            'min_pattern_quality': {'min': 0.4, 'max': 0.6, 'step': 0.05},
            'high_quality_threshold': {'min': 0.65, 'max': 0.85, 'step': 0.05},
            'stop_loss_pct': {'min': 0.02, 'max': 0.05, 'step': 0.005},
            'initial_reduce_pct': {'min': 0.4, 'max': 0.6, 'step': 0.05},
            'top_shadow_ratio': {'min': 0.3, 'max': 0.7, 'step': 0.1}
        }
    
    def generate_signals(self, data):
        """
        生成交易信号
        
        Args:
            data (pd.DataFrame): 包含OHLCV的历史市场数据
            
        Returns:
            pd.Series: 交易信号序列 (-1:卖出, 0:持有)
        """
        # 确保数据完整性
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error("缺少所需的数据列,至少需要 OHLCV 数据")
            return pd.Series(0, index=data.index)
        
        # 创建数据副本
        df = data.copy()
        
        # 更新检测器参数
        self.detector.params.update(self.parameters)
        
        # 使用检测器识别双飞乌鸦形态
        signals, pattern_details = self.detector.detect_double_crows(df)
        
        # 记录检测到的形态
        if len(pattern_details) > 0:
            logger.info(f"检测到 {len(pattern_details)} 个双飞乌鸦形态")
            for date, details in pattern_details.items():
                logger.info(f"日期: {date}, 强度: {details['strength']:.2f}, 行动: {details['action']}")
        
        # 应用确认规则
        if self.parameters['confirmation_days'] > 0:
            self._apply_confirmation_rules(df, signals, pattern_details)
        
        return signals
    
    def _apply_confirmation_rules(self, df, signals, pattern_details):
        """
        应用信号确认规则
        
        Args:
            df (pd.DataFrame): 价格数据
            signals (pd.Series): 信号序列
            pattern_details (dict): 形态详情
            
        Returns:
            None: 直接修改signals
        """
        confirmation_days = self.parameters['confirmation_days']
        
        # 获取信号日期
        signal_dates = signals[signals != 0].index
        
        for date in signal_dates:
            idx = df.index.get_loc(date)
            
            # 确保有足够的确认日期数据
            if idx + confirmation_days >= len(df):
                continue
                
            signal = signals[date]
            
            # 获取确认窗口
            confirmation_window = df.iloc[idx+1:idx+confirmation_days+1]
            
            # 卖出信号确认
            if signal < 0:
                # 检查后续是否继续下跌或横盘整理
                if all(row['high'] > df.loc[date, 'high'] * (1 + self.parameters['false_signal_threshold']) 
                      for _, row in confirmation_window.iterrows()):
                    # 如果后续K线高点突破了双飞乌鸦的高点,可能是假信号
                    signals[date] = 0
                    logger.info(f"{date}: 取消卖出信号 - 后续K线突破了形态高点")
                
                # 检查是否有"阳包阴"反转信号
                for i, (confirm_date, row) in enumerate(confirmation_window.iterrows()):
                    if (row['is_bullish'] if 'is_bullish' in row else row['close'] > row['open']) and \
                       row['close'] > df.loc[date, 'open'] and \
                       row['open'] < df.loc[date, 'close']:
                        signals[date] = 0
                        logger.info(f"{date}: 取消卖出信号 - 第{i+1}天出现阳包阴反转信号")
                        break
        
        return signals

    def generate_trading_decisions(self, data, current_position=0):
        """
        生成交易决策,包括仓位管理建议
        
        Args:
            data (pd.DataFrame): 价格数据
            current_position (float): 当前仓位,0-1之间,0表示空仓,1表示满仓
            
        Returns:
            dict: 交易决策,包括方向,目标仓位,止损价等
        """
        # 生成信号
        signals = self.generate_signals(data)
        
        # 最新日期
        latest_date = data.index[-1]
        
        # 默认决策
        decision = {
            'date': latest_date,
            'signal': 0,
            'action': '持有',
            'target_position': current_position,
            'stop_loss': None,
            'pattern_strength': 0,
            'notes': ''
        }
        
        # 检查是否有信号
        recent_signals = signals.iloc[-5:]  # 最近5个交易日的信号
        if (recent_signals != 0).any():
            # 找到最近的非零信号
            for i in range(len(recent_signals)-1, -1, -1):
                if recent_signals.iloc[i] != 0:
                    signal_date = recent_signals.index[i]
                    signal = recent_signals.iloc[i]
                    
                    # 更新决策
                    decision['date'] = signal_date
                    decision['signal'] = signal
                    
                    if signal < 0:  # 卖出信号
                        # 计算减仓比例,根据信号强度调整
                        _, pattern_details = self.detector.detect_double_crows(data)
                        if signal_date in pattern_details:
                            strength = pattern_details[signal_date]['strength']
                            decision['pattern_strength'] = strength
                            
                            # 根据强度决定减仓比例
                            if strength >= self.parameters['high_quality_threshold']:
                                reduce_pct = self.parameters['initial_reduce_pct']
                                decision['action'] = f"强烈减仓信号,建议减仓{int(reduce_pct*100)}%"
                                decision['target_position'] = max(0, current_position * (1 - reduce_pct))
                            else:
                                reduce_pct = self.parameters['initial_reduce_pct'] * 0.7
                                decision['action'] = f"减仓信号,建议减仓{int(reduce_pct*100)}%"
                                decision['target_position'] = max(0, current_position * (1 - reduce_pct))
                            
                            # 设置止损价
                            if 'action' in pattern_details[signal_date]:
                                decision['notes'] = pattern_details[signal_date]['action']
                            
                            # 设置止损价格
                            low_price = data.loc[signal_date, 'low']
                            decision['stop_loss'] = low_price * (1 - self.parameters['stop_loss_pct'])
                    
                    break
        
        # 添加跟踪止损
        if current_position > 0 and decision['target_position'] > 0:
            if 'ma20' in data.columns:
                ma20_value = data['ma20'].iloc[-1]
                decision['trailing_stop'] = ma20_value * 0.98  # MA20下方2%
            else:
                # 使用近期低点作为跟踪止损
                recent_low = data['low'].iloc[-10:].min()
                decision['trailing_stop'] = recent_low * 0.98
        
        return decision


def test_double_black_crows_strategy():
    """测试双飞乌鸦策略"""
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    
    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=120, freq='D')
    
    # 初始价格和波动
    np.random.seed(42)
    close = 100 + np.random.randn(120).cumsum()
    
    # 创建上涨趋势
    for i in range(40, 80):
        close[i] = close[i-1] * (1 + np.random.uniform(0.003, 0.012))
    
    # 创建双飞乌鸦形态
    crow_idx1 = 80
    crow_idx2 = 81
    
    # 第一根K线 - 阴线或带上影线的小阳线
    close[crow_idx1] = close[crow_idx1-1] * 0.99
    
    # 第二根K线 - 高开低走的阴线
    close[crow_idx2] = close[crow_idx1] * 0.97
    
    # 生成OHLCV数据
    high = np.zeros(len(close))
    low = np.zeros(len(close))
    open_prices = np.zeros(len(close))
    
    # 一般K线
    for i in range(len(close)):
        if i not in [crow_idx1, crow_idx2]:
            daily_range = close[i] * np.random.uniform(0.005, 0.02)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/2, daily_range/2)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 第一根K线 - 设置为阴线带上影线
    open_prices[crow_idx1] = close[crow_idx1-1] * 1.01  # 高开
    high[crow_idx1] = open_prices[crow_idx1] * 1.02     # 长上影线
    low[crow_idx1] = min(open_prices[crow_idx1], close[crow_idx1]) * 0.99
    
    # 第二根K线 - 高开低走
    open_prices[crow_idx2] = close[crow_idx1] * 1.005   # 高开
    high[crow_idx2] = open_prices[crow_idx2] * 1.01     # 上影线
    low[crow_idx2] = close[crow_idx2] * 0.99            # 下影线
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=len(close))
    volume[crow_idx1] = volume[crow_idx1-1] * 1.2       # 第一根K线小幅放量
    volume[crow_idx2] = volume[crow_idx1] * 1.5         # 第二根K线明显放量
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    # 创建策略
    strategy = DoubleBlackCrowsStrategy()
    
    # 生成信号
    signals = strategy.generate_signals(df)
    
    # 打印检测结果
    print(f"生成信号数量: {(signals != 0).sum()}")
    if (signals != 0).sum() > 0:
        for date, signal in signals[signals != 0].items():
            print(f"日期: {date}, 信号: {signal}")
    
    # 生成交易决策
    decision = strategy.generate_trading_decisions(df, current_position=0.8)
    print("\n交易决策:")
    for key, value in decision.items():
        print(f"{key}: {value}")
    
    # 用检测器可视化形态
    detector = DoubleBlackCrowsDetector()
    detector.params.update(strategy.parameters)
    _, pattern_details = detector.detect_double_crows(df)
    detector.visualize_pattern(df, signals, pattern_details, "双飞乌鸦策略测试")
    
    return df, signals, decision

if __name__ == "__main__":
    test_double_black_crows_strategy() 
