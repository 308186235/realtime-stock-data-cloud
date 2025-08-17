import pandas as pd
import numpy as np
from backend.strategies.base_strategy import BaseStrategy
from backend.strategies.rising_obstacle_detector import RisingObstacleDetector
import logging

logger = logging.getLogger(__name__)

class RisingObstacleStrategy(BaseStrategy):
    """
    下降受阻策略
    
    基于"下降受阻"形态的交易策略,识别股价在下跌趋势中遇到支撑位时的潜在反弹机会。
    该形态的核心特征是:下跌趋势中接近支撑位时,出现缩量,长下影线或阳包阴等信号,
    表明空方力量减弱,多方开始抵抗,可能形成短期止跌或反弹。
    
    该策略生成以下信号:
    - 1 (买入信号): 在关键支撑位确认下降受阻形态,且有多种反转信号指示
    - 0 (观望): 无明显信号或形态不完整
    """
    
    def __init__(self, parameters=None):
        """
        初始化下降受阻策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "下降受阻策略"
        self.description = "基于下降受阻形态的交易策略,识别下跌趋势中的潜在反弹机会"
        self.detector = RisingObstacleDetector()
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            # 趋势识别参数
            'downtrend_lookback': 15,        # 检查下跌趋势的回溯天数
            'downtrend_threshold': -0.05,    # 定义下跌趋势的阈值(-5%)
            
            # 支撑位识别参数
            'support_lookback': 60,          # 寻找历史支撑位的回溯天数
            'support_tolerance': 0.02,       # 支撑位容差范围(2%)
            'min_touches': 2,                # 确认支撑位的最小触及次数
            
            # 形态识别参数
            'volume_shrink_threshold': 0.8,  # 缩量阈值(低于80%为缩量)
            'hammer_ratio': 1.5,             # 锤子线下影/实体比例
            'doji_threshold': 0.1,           # 十字星实体/振幅比例阈值
            'bullish_engulf_required': False, # 是否必须出现阳包阴形态
            
            # 信号强度和确认参数
            'confirmation_days': 2,          # 确认信号所需天数
            'min_pattern_quality': 0.5,      # 最低形态质量要求(0.5)
            'high_quality_threshold': 0.7,   # 高质量形态阈值(0.7)
            
            # 风险控制参数
            'stop_loss_pct': 0.03,           # 止损比例(3%)
            'target_rebound_pct': 0.05,      # 目标反弹幅度(5%)
            'initial_position': 0.2,         # 初始仓位(20%)
            'max_position': 0.5,             # 最大仓位(50%)
            
            # 信号过滤参数
            'filter_by_market': True,        # 是否根据大盘走势过滤信号
            'market_uptrend_required': False # 是否要求大盘处于上升趋势
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'downtrend_threshold': {'min': -0.1, 'max': -0.03, 'step': 0.01},
            'support_tolerance': {'min': 0.01, 'max': 0.04, 'step': 0.005},
            'volume_shrink_threshold': {'min': 0.7, 'max': 0.9, 'step': 0.05},
            'min_pattern_quality': {'min': 0.4, 'max': 0.6, 'step': 0.05},
            'high_quality_threshold': {'min': 0.6, 'max': 0.8, 'step': 0.05},
            'stop_loss_pct': {'min': 0.02, 'max': 0.05, 'step': 0.005},
            'initial_position': {'min': 0.1, 'max': 0.3, 'step': 0.05}
        }
    
    def generate_signals(self, data, market_data=None):
        """
        生成交易信号
        
        Args:
            data (pd.DataFrame): 包含OHLCV的历史市场数据
            market_data (pd.DataFrame, optional): 大盘数据,用于市场过滤
            
        Returns:
            pd.Series: 交易信号序列 (1:买入, 0:持有/观望)
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
        
        # 使用检测器识别下降受阻形态
        signals, pattern_details = self.detector.detect_rising_obstacle(df)
        
        # 记录检测到的形态
        if len(pattern_details) > 0:
            logger.info(f"检测到 {len(pattern_details)} 个下降受阻形态")
            for date, details in pattern_details.items():
                logger.info(f"日期: {date}, 强度: {details['strength']:.2f}, 行动: {details['action']}")
        
        # 应用市场过滤(如果有大盘数据且启用过滤)
        if market_data is not None and self.parameters['filter_by_market']:
            signals = self._apply_market_filter(signals, market_data)
        
        # 应用确认规则
        if self.parameters['confirmation_days'] > 0:
            signals = self._apply_confirmation_rules(df, signals, pattern_details)
        
        return signals
    
    def _apply_market_filter(self, signals, market_data):
        """
        根据大盘走势过滤信号
        
        Args:
            signals (pd.Series): 原始信号
            market_data (pd.DataFrame): 大盘数据
            
        Returns:
            pd.Series: 过滤后的信号
        """
        # 复制信号数据
        filtered_signals = signals.copy()
        
        # 计算大盘短期趋势(简单用5日均线判断)
        if 'close' in market_data.columns:
            market_data['ma5'] = market_data['close'].rolling(window=5).mean()
            market_data['ma10'] = market_data['close'].rolling(window=10).mean()
            market_data['uptrend'] = market_data['close'] > market_data['ma5']
        
            # 对所有信号日期进行检查
            for date in signals[signals != 0].index:
                if date in market_data.index:
                    # 如果要求大盘必须上涨,但大盘处于下跌,则过滤信号
                    if (self.parameters['market_uptrend_required'] and 
                        not market_data.loc[date, 'uptrend']):
                        filtered_signals[date] = 0
                        logger.info(f"{date}: 因大盘下跌过滤信号")
        
        return filtered_signals
    
    def _apply_confirmation_rules(self, df, signals, pattern_details):
        """
        应用信号确认规则
        
        Args:
            df (pd.DataFrame): 价格数据
            signals (pd.Series): 信号序列
            pattern_details (dict): 形态详情
            
        Returns:
            pd.Series: 确认后的信号序列
        """
        # 复制信号数据
        confirmed_signals = signals.copy()
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
            
            # 买入信号确认
            if signal > 0:
                # 检查后续是否有效突破支撑位
                if any(row['close'] < df.loc[date, 'low'] * (1 - self.parameters['stop_loss_pct']) 
                      for _, row in confirmation_window.iterrows()):
                    # 如果后续K线跌破止损位,可能是假信号
                    confirmed_signals[date] = 0
                    logger.info(f"{date}: 取消买入信号 - 后续K线跌破止损位")
                    
                # 检查后续是否有上涨确认
                elif not any(row['close'] > df.loc[date, 'close'] * (1 + 0.01)  # 至少上涨1%
                           for _, row in confirmation_window.iterrows()):
                    # 如果后续没有上涨确认,降低信号强度
                    if date in pattern_details and pattern_details[date]['strength'] < self.parameters['high_quality_threshold']:
                        confirmed_signals[date] = 0
                        logger.info(f"{date}: 取消买入信号 - 后续无上涨确认且信号强度不足")
        
        return confirmed_signals
    
    def generate_trading_decisions(self, data, current_position=0, market_data=None):
        """
        生成交易决策,包括仓位管理建议
        
        Args:
            data (pd.DataFrame): 价格数据
            current_position (float): 当前仓位,0-1之间,0表示空仓,1表示满仓
            market_data (pd.DataFrame, optional): 大盘数据
            
        Returns:
            dict: 交易决策,包括方向,目标仓位,止损价等
        """
        # 生成信号
        signals = self.generate_signals(data, market_data)
        
        # 最新日期
        latest_date = data.index[-1]
        
        # 默认决策
        decision = {
            'date': latest_date,
            'signal': 0,
            'action': '持有观望',
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
                    
                    if signal > 0:  # 买入信号
                        # 获取形态详情
                        _, pattern_details = self.detector.detect_rising_obstacle(data)
                        if signal_date in pattern_details:
                            strength = pattern_details[signal_date]['strength']
                            decision['pattern_strength'] = strength
                            
                            # 根据强度决定买入仓位
                            if strength >= self.parameters['high_quality_threshold']:
                                # 高质量信号,可以使用较大仓位
                                target_position = min(current_position + self.parameters['initial_position'] * 1.5, 
                                                    self.parameters['max_position'])
                                decision['action'] = f"强烈买入信号,建议买入至{int(target_position*100)}%仓位"
                            else:
                                # 一般信号,使用标准仓位
                                target_position = min(current_position + self.parameters['initial_position'],
                                                    self.parameters['max_position'])
                                decision['action'] = f"买入信号,建议买入至{int(target_position*100)}%仓位"
                            
                            decision['target_position'] = target_position
                            
                            # 设置止损价
                            if 'support_info' in pattern_details[signal_date]:
                                support_price = pattern_details[signal_date]['support_info']['price']
                                decision['stop_loss'] = support_price * (1 - self.parameters['stop_loss_pct'])
                            else:
                                decision['stop_loss'] = data.loc[signal_date, 'low'] * (1 - self.parameters['stop_loss_pct'])
                            
                            # 添加支撑位信息
                            if 'support_info' in pattern_details[signal_date]:
                                support_info = pattern_details[signal_date]['support_info']
                                decision['notes'] = f"支撑位: {support_info['price']:.2f} ({support_info['type']})"
                            
                            # 添加目标价格
                            current_price = data.loc[signal_date, 'close']
                            decision['target_price'] = current_price * (1 + self.parameters['target_rebound_pct'])
                    
                    break
        
        # 如果没有明确信号,但市场可能存在风险,提供防御性建议
        if decision['signal'] == 0 and current_position > 0:
            # 检查是否跌破重要支撑
            if 'ma20' in data.columns and data['close'].iloc[-1] < data['ma20'].iloc[-1]:
                if 'ma60' in data.columns and data['close'].iloc[-1] < data['ma60'].iloc[-1]:
                    # 跌破长期支撑,建议减仓
                    decision['action'] = f"跌破重要均线支撑,建议减仓"
                    decision['target_position'] = current_position * 0.7
                    decision['notes'] = "价格跌破20日线和60日线,趋势转弱"
        
        return decision


def test_rising_obstacle_strategy():
    """测试下降受阻策略"""
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    
    # 生成模拟数据
    dates = pd.date_range(start='2023-01-01', periods=120, freq='D')
    
    # 初始价格
    np.random.seed(42)
    close = 100 + np.random.randn(120).cumsum()
    
    # 创建下跌趋势
    for i in range(30, 80):
        close[i] = close[i-1] * (1 - np.random.uniform(0.003, 0.01))
    
    # 创建下降受阻形态
    obstacle_idx = 80
    
    # 在支撑位附近出现止跌信号
    close[obstacle_idx] = close[obstacle_idx-1] * 0.98  # 最后一次下跌
    
    # 支撑后的小幅反弹
    for i in range(obstacle_idx + 1, obstacle_idx + 5):
        close[i] = close[i-1] * (1 + np.random.uniform(0.003, 0.01))
    
    # 生成OHLCV数据
    high = np.zeros(len(close))
    low = np.zeros(len(close))
    open_prices = np.zeros(len(close))
    
    # 一般K线
    for i in range(len(close)):
        if i != obstacle_idx:
            daily_range = close[i] * np.random.uniform(0.01, 0.03)
            high[i] = close[i] + daily_range/2
            low[i] = close[i] - daily_range/2
            if i > 0:
                open_prices[i] = close[i-1] + np.random.uniform(-daily_range/4, daily_range/4)
            else:
                open_prices[i] = close[i] - daily_range/4
    
    # 下降受阻K线 - 带长下影线
    open_prices[obstacle_idx] = close[obstacle_idx-1] * 0.99  # 略低开
    high[obstacle_idx] = open_prices[obstacle_idx] * 1.01     # 小幅反弹
    low[obstacle_idx] = open_prices[obstacle_idx] * 0.95      # 长下影线,尝试下破支撑后回升
    
    # 成交量
    volume = np.random.uniform(1000, 2000, size=len(close))
    volume[obstacle_idx-3:obstacle_idx] = volume[obstacle_idx-4] * 1.3  # 下跌时放量
    volume[obstacle_idx] = volume[obstacle_idx-1] * 0.7                # 止跌时缩量
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    # 计算均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    # 创建策略
    strategy = RisingObstacleStrategy()
    
    # 生成信号
    signals = strategy.generate_signals(df)
    
    # 打印检测结果
    print(f"生成信号数量: {(signals != 0).sum()}")
    if (signals != 0).sum() > 0:
        for date, signal in signals[signals != 0].items():
            print(f"日期: {date}, 信号: {signal}")
    
    # 生成交易决策
    decision = strategy.generate_trading_decisions(df, current_position=0.2)
    print("\n交易决策:")
    for key, value in decision.items():
        print(f"{key}: {value}")
    
    # 用检测器可视化形态
    detector = RisingObstacleDetector()
    detector.params.update(strategy.parameters)
    _, pattern_details = detector.detect_rising_obstacle(df)
    detector.visualize_pattern(df, signals, pattern_details, "下降受阻策略测试")
    
    return df, signals, decision

if __name__ == "__main__":
    test_rising_obstacle_strategy() 
