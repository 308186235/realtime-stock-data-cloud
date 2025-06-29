import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .base_strategy import BaseStrategy

class TTradingStrategy(BaseStrategy):
    """
    T交易策略 (T Trading Strategy)
    
    在中国A股T+1制度下进行做T操作,通过日内交易降低持仓成本。
    策略支持两种模式:
    1. 正T (先买后卖): 当天股价下跌时买入,待股价回升后卖出同等数量
    2. 反T (先卖后买): 当天股价高位时先卖出部分底仓,待股价下跌后再买回
    
    关键前提:必须有底仓(已持有的股票),且当日买卖数量不超过底仓数量
    """
    
    def __init__(self, parameters=None):
        """
        初始化T交易策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters)
        self.name = "T交易策略"
        self.description = "在T+1制度下通过日内波动降低持仓成本的策略"
        
        # 设置默认参数
        default_params = self.get_default_parameters()
        for key, value in default_params.items():
            if key not in self.parameters:
                self.parameters[key] = value
        
        # 持仓底仓数量(初始值,实际使用时应从账户信息获取)
        self.base_position = self.parameters.get('base_position', 100)
        
        # 交易记录
        self.today_bought = 0  # 当天已买入数量
        self.today_sold = 0    # 当天已卖出数量
        self.last_signal_time = None  # 上次产生信号的时间
        self.last_action = None  # 上次执行的操作

    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'mode': 'auto',  # 'positive'(正T), 'negative'(反T), 'auto'(自动选择)
            'base_position': 100,  # 底仓数量
            'max_daily_t_percentage': 0.5,  # 最大日内T交易比例(相对于底仓)
            'positive_t_buy_threshold': -0.02,  # 正T买入阈值(相对开盘价跌幅)
            'positive_t_sell_threshold': 0.01,  # 正T卖出阈值(相对买入价涨幅)
            'negative_t_sell_threshold': 0.03,  # 反T卖出阈值(相对开盘价涨幅)
            'negative_t_buy_threshold': -0.01,  # 反T买入阈值(相对卖出价跌幅)
            'min_price_move': 0.01,  # 最小价格波动(元)
            'time_interval': 15,  # 信号生成时间间隔(分钟)
            'enable_volume_check': True,  # 是否启用成交量检查
            'volume_threshold': 2.0,  # 成交量阈值(相对于平均成交量)
        }
    
    def get_parameter_ranges(self):
        """
        获取策略参数的优化范围
        
        Returns:
            dict: 参数优化范围
        """
        return {
            'positive_t_buy_threshold': {'min': -0.05, 'max': -0.01, 'step': 0.005},
            'positive_t_sell_threshold': {'min': 0.005, 'max': 0.03, 'step': 0.005},
            'negative_t_sell_threshold': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'negative_t_buy_threshold': {'min': -0.03, 'max': -0.005, 'step': 0.005},
            'max_daily_t_percentage': {'min': 0.1, 'max': 0.8, 'step': 0.1}
        }
    
    def generate_signals(self, data):
        """
        根据市场数据生成T交易信号
        
        Args:
            data (pd.DataFrame): 市场数据,包括OHLCV和实时数据
                                必须包含: date, time, open, high, low, close, volume列
            
        Returns:
            pd.Series: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        # 确保数据包含所有必要列
        required_columns = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"输入数据缺少必要列: {col}")
        
        # 创建结果信号Series
        signals = pd.Series(0, index=data.index)
        
        # 检查是否有足够的底仓进行T交易
        if self.base_position <= 0:
            print("警告: 没有底仓,无法进行T交易")
            return signals
        
        # 计算可用于T交易的最大数量
        max_t_shares = int(self.base_position * self.parameters['max_daily_t_percentage'])
        
        # 检查今日交易是否已达上限
        available_for_buy = max_t_shares - self.today_bought
        available_for_sell = max_t_shares - self.today_sold
        
        if available_for_buy <= 0 and available_for_sell <= 0:
            return signals  # 今日交易已达上限
            
        # 如果数据是日线级别,转换为分钟级别进行处理
        is_daily = len(data) > 0 and data['time'].iloc[0] == data['time'].iloc[-1]
        if is_daily:
            print("警告: T交易策略需要分钟级数据,日线数据将直接返回0信号")
            return signals
            
        # 获取当前价格和开盘价
        current_price = data['close'].iloc[-1]
        open_price = data['open'].iloc[0]  # 当日开盘价
        
        # 计算交易量指标
        avg_volume = data['volume'].iloc[:-1].mean()
        current_volume = data['volume'].iloc[-1]
        
        # 当前时间
        if 'datetime' in data.columns:
            current_time = data['datetime'].iloc[-1]
        else:
            # 从date和time列构造datetime
            date_str = str(data['date'].iloc[-1])
            time_str = str(data['time'].iloc[-1])
            try:
                current_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
            except:
                current_time = datetime.now()  # 如果无法解析,使用当前时间
        
        # 时间间隔控制,避免频繁信号
        if self.last_signal_time is not None:
            time_diff = (current_time - self.last_signal_time).total_seconds() / 60.0
            if time_diff < self.parameters['time_interval']:
                return signals
        
        # 检查成交量条件
        volume_condition = True
        if self.parameters['enable_volume_check']:
            volume_condition = current_volume > avg_volume * self.parameters['volume_threshold']
        
        # 交易模式选择
        mode = self.parameters['mode']
        
        # 自动模式根据开盘后的价格走势决定使用正T还是反T
        if mode == 'auto':
            # 如果当前价格高于开盘价,优先使用反T模式
            if current_price > open_price * (1 + self.parameters['negative_t_sell_threshold']):
                mode = 'negative'
            # 如果当前价格低于开盘价,优先使用正T模式
            elif current_price < open_price * (1 + self.parameters['positive_t_buy_threshold']):
                mode = 'positive'
            else:
                # 价格在阈值范围内,不产生信号
                return signals
        
        # 正T模式: 先买后卖
        if mode == 'positive' and available_for_buy > 0:
            # 价格下跌到买入阈值,产生买入信号
            if current_price < open_price * (1 + self.parameters['positive_t_buy_threshold']) and volume_condition:
                if self.last_action != 'buy': # 避免连续买入
                    signals.iloc[-1] = 1  # 买入信号
                    self.today_bought += available_for_buy
                    self.last_action = 'buy'
                    self.last_signal_time = current_time
                    print(f"产生正T买入信号: 价格={current_price}, 数量={available_for_buy}")
            
            # 如果之前已买入,且价格回升到卖出阈值,产生卖出信号
            elif self.last_action == 'buy' and \
                current_price > open_price * (1 + self.parameters['positive_t_sell_threshold']):
                signals.iloc[-1] = -1  # 卖出信号
                self.today_sold += available_for_sell
                self.last_action = 'sell'
                self.last_signal_time = current_time
                print(f"产生正T卖出信号: 价格={current_price}, 数量={available_for_sell}")
                
        # 反T模式: 先卖后买
        elif mode == 'negative' and available_for_sell > 0:
            # 价格上涨到卖出阈值,产生卖出信号
            if current_price > open_price * (1 + self.parameters['negative_t_sell_threshold']) and volume_condition:
                if self.last_action != 'sell': # 避免连续卖出
                    signals.iloc[-1] = -1  # 卖出信号
                    self.today_sold += available_for_sell
                    self.last_action = 'sell'
                    self.last_signal_time = current_time
                    print(f"产生反T卖出信号: 价格={current_price}, 数量={available_for_sell}")
            
            # 如果之前已卖出,且价格回落到买入阈值,产生买入信号
            elif self.last_action == 'sell' and \
                current_price < current_price * (1 + self.parameters['negative_t_buy_threshold']):
                signals.iloc[-1] = 1  # 买入信号
                self.today_bought += available_for_buy
                self.last_action = 'buy'
                self.last_signal_time = current_time
                print(f"产生反T买入信号: 价格={current_price}, 数量={available_for_buy}")
                
        return signals
    
    def reset_daily_counters(self):
        """重置每日交易计数器,应在每个交易日开始时调用"""
        self.today_bought = 0
        self.today_sold = 0
        self.last_signal_time = None
        self.last_action = None
    
    def update_base_position(self, new_position):
        """更新底仓数量"""
        self.base_position = new_position
        print(f"底仓更新为: {new_position}股") 
