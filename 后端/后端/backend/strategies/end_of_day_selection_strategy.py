import pandas as pd
import numpy as np
from datetime import datetime, time
from .base_strategy import BaseStrategy

class EndOfDaySelectionStrategy(BaseStrategy):
    """
    尾盘选股策略 (End-of-Day Stock Selection Strategy)
    
    专为中国A股市场设计的尾盘选股策略,主要关注收盘前30分钟(14:30-15:00)
    的市场行为,通过分析量价关系,技术指标共振和市场趋势,筛选适合T+0交易
    或次日交易的潜力股。
    
    支持多种策略方法:
    1. 基础尾盘策略:基于量价关系和技术指标
    2. 国诚投顾策略:尾盘资金动向和技术指标共振
    3. 指南针策略:红锦鲤摆尾指标
    4. 尾盘选股王策略:资金流,技术指标和新闻事件
    5. 经传短线策略:捕捞季节和主力追踪指标共振
    6. 乾坤六道策略:六大技术指标共振
    7. 九方智投策略:尾盘K线形态与量价关系
    """
    
    def __init__(self, parameters=None):
        """
        初始化尾盘选股策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters)
        self.name = "尾盘选股策略"
        self.description = "基于量价关系和技术指标的尾盘选股策略,适用于A股T+0或次日交易"
        
        # 设置默认参数
        default_params = self.get_default_parameters()
        for key, value in default_params.items():
            if key not in self.parameters:
                self.parameters[key] = value
        
        # 设置策略方法映射
        self.strategy_methods = {
            'base': self._base_strategy,
            'guocheng': self._guocheng_strategy,
            'zhinanzhen': self._zhinanzhen_strategy,
            'tn6': self._tn6_strategy,
            'jingchuan': self._jingchuan_strategy,
            'qiankun': self._qiankun_strategy,
            'jiufang': self._jiufang_strategy,
        }
    
    def get_default_parameters(self):
        """
        获取策略默认参数
        
        Returns:
            dict: 默认参数
        """
        return {
            # 策略选择
            'active_strategies': ['base', 'guocheng', 'zhinanzhen', 'tn6', 'jingchuan', 'qiankun', 'jiufang'],
            'strategy_weights': {
                'base': 0.15,
                'guocheng': 0.15,
                'zhinanzhen': 0.15,
                'tn6': 0.15,
                'jingchuan': 0.15, 
                'qiankun': 0.15,
                'jiufang': 0.10
            },
            
            # 基础策略参数
            'volume_ratio_threshold': 1.5,        # 尾盘量比阈值
            'turnover_rate_small_cap': 0.05,      # 小盘股换手率阈值 (5%)
            'turnover_rate_mid_large_cap': 0.03,  # 中大盘股换手率阈值 (3%)
            'volume_spike_factor': 1.5,           # 尾盘量能突增因子
            
            # 价格指标参数
            'bias_lower_bound': -0.02,            # 乖离率下限 (-2%)
            'bias_upper_bound': 0.03,             # 乖离率上限 (3%)
            'price_ma_confirm': True,             # 是否需要均价线确认
            
            # 技术指标参数
            'macd_zero_line_filter': True,        # 是否过滤MACD 0轴以下的股票
            'kdj_lower_bound': 50,                # KDJ低位阈值
            'kdj_upper_bound': 80,                # KDJ高位阈值
            'rsi_lower_bound': 50,                # RSI低位阈值
            'rsi_upper_bound': 70,                # RSI高位阈值
            
            # 市值和涨幅过滤
            'min_market_cap': 2e9,                # 最小市值(20亿)
            'max_market_cap': 2e10,               # 最大市值(200亿)
            'min_price_change': 0.02,             # 最小涨幅(2%)
            'max_price_change': 0.05,             # 最大涨幅(5%)
            
            # 尾盘时间设置
            'eod_start_time': '14:30',            # 尾盘开始时间
            'eod_end_time': '15:00',              # 尾盘结束时间
            
            # 国诚投顾策略参数
            'guocheng_rsi_lower': 50,             # RSI下限
            'guocheng_rsi_upper': 70,             # RSI上限
            'guocheng_volume_ratio': 1.5,         # 量比阈值
            
            # 指南针策略参数
            'zhinanzhen_volume_ratio': 2.0,       # 红锦鲤量比阈值
            'zhinanzhen_market_cap_min': 2e9,     # 流通市值下限(20亿)
            'zhinanzhen_market_cap_max': 2e10,    # 流通市值上限(200亿)
            
            # 尾盘选股王(tn6)策略参数
            'tn6_super_fund_inflow': 0.01,        # 超大单净流入占比阈值(1%)
            'tn6_volume_ratio': 1.5,              # 量比阈值
            
            # 经传短线策略参数
            'jingchuan_volume_ratio': 1.5,        # 尾盘成交量放大阈值
            
            # 乾坤六道策略参数
            'qiankun_all_indicators_golden': True, # 是否要求六道指标同时金叉
            
            # 九方智投策略参数
            'jiufang_low_shadow_length': 0.01,    # 长下影线长度阈值(相对于收盘价)
            
            # 组合策略权重
            'volume_weight': 0.35,                # 成交量指标权重
            'trend_weight': 0.30,                 # 趋势指标权重
            'technical_weight': 0.35              # 技术指标权重
        }
    
    def get_parameter_ranges(self):
        """
        获取参数优化范围
        
        Returns:
            dict: 参数范围配置
        """
        return {
            'volume_ratio_threshold': {'min': 1.2, 'max': 3.0, 'step': 0.1},
            'turnover_rate_small_cap': {'min': 0.03, 'max': 0.15, 'step': 0.01},
            'turnover_rate_mid_large_cap': {'min': 0.02, 'max': 0.08, 'step': 0.005},
            'volume_spike_factor': {'min': 1.2, 'max': 2.0, 'step': 0.1},
            'bias_lower_bound': {'min': -0.05, 'max': -0.01, 'step': 0.005},
            'bias_upper_bound': {'min': 0.01, 'max': 0.05, 'step': 0.005},
            'kdj_lower_bound': {'min': 40, 'max': 60, 'step': 5},
            'kdj_upper_bound': {'min': 70, 'max': 90, 'step': 5},
            'rsi_lower_bound': {'min': 40, 'max': 60, 'step': 5},
            'rsi_upper_bound': {'min': 60, 'max': 80, 'step': 5},
            'guocheng_volume_ratio': {'min': 1.2, 'max': 2.5, 'step': 0.1},
            'zhinanzhen_volume_ratio': {'min': 1.5, 'max': 3.0, 'step': 0.1},
            'tn6_super_fund_inflow': {'min': 0.005, 'max': 0.02, 'step': 0.001},
            'jingchuan_volume_ratio': {'min': 1.3, 'max': 2.0, 'step': 0.1}
        }
    
    def generate_signals(self, data, market_data=None):
        """
        生成尾盘选股信号
        
        Args:
            data (pd.DataFrame): 个股历史数据,包括OHLCV
            market_data (pd.DataFrame, optional): 市场数据,包含指数和板块信息
            
        Returns:
            pd.DataFrame: 评分结果,包含综合得分和各维度得分
        """
        # 确保数据包含必要的列
        required_columns = ['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'turnover_rate', 'market_cap']
        for col in required_columns:
            if col not in data.columns and col not in ['turnover_rate', 'market_cap']:
                raise ValueError(f"输入数据缺少必要列: {col}")
        
        # 添加市值和换手率列(如果不存在)
        if 'market_cap' not in data.columns and 'total_shares' in data.columns and 'close' in data.columns:
            data['market_cap'] = data['total_shares'] * data['close']
        
        if 'turnover_rate' not in data.columns and 'volume' in data.columns and 'float_shares' in data.columns:
            data['turnover_rate'] = data['volume'] / data['float_shares']
        
        # 1. 筛选尾盘时段数据
        eod_start = datetime.strptime(self.parameters['eod_start_time'], '%H:%M').time()
        eod_end = datetime.strptime(self.parameters['eod_end_time'], '%H:%M').time()
        
        # 检查时间列格式
        if isinstance(data['time'].iloc[0], str):
            data['time'] = pd.to_datetime(data['time']).dt.time
        
        # 提取尾盘数据
        eod_mask = (data['time'] >= eod_start) & (data['time'] <= eod_end)
        eod_data = data[eod_mask].copy()
        
        if len(eod_data) == 0:
            return pd.DataFrame()  # 无尾盘数据
        
        # 2. 计算技术指标
        self._calculate_indicators(data)
        
        # 3. 应用多种策略方法并获取评分
        strategy_scores = {}
        strategy_signals = {}
        strategy_reasons = {}
        
        # 根据active_strategies参数选择要运行的策略
        active_strategies = self.parameters['active_strategies']
        
        # 遍历激活的策略并运行
        for strategy_name in active_strategies:
            if strategy_name in self.strategy_methods:
                score, signal, reason = self.strategy_methods[strategy_name](data, eod_data)
                strategy_scores[strategy_name] = score
                strategy_signals[strategy_name] = signal
                strategy_reasons[strategy_name] = reason
        
        # 计算综合得分(根据策略权重)
        composite_score = 0
        total_weight = 0
        
        for strategy_name, score in strategy_scores.items():
            weight = self.parameters['strategy_weights'].get(strategy_name, 0)
            composite_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            composite_score /= total_weight
        
        # 确定最终信号和原因(根据得分最高的策略)
        max_score_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        final_signal = strategy_signals[max_score_strategy]
        final_reason = strategy_reasons[max_score_strategy]
        
        # 4. 生成评分结果
        last_price = data['close'].iloc[-1]
        last_change_pct = (last_price / data['open'].iloc[0] - 1) * 100
        market_cap = data['market_cap'].iloc[-1] if 'market_cap' in data.columns else None
        
        # 构建返回结果
        result = {
            'date': data['date'].iloc[-1],
            'code': data.get('code', ['Unknown'])[0] if 'code' in data.columns else 'Unknown',
            'name': data.get('name', ['Unknown'])[0] if 'name' in data.columns else 'Unknown',
            'price': last_price,
            'change_percent': last_change_pct,
            'market_cap': market_cap,
            'strategy_scores': strategy_scores,
            'composite_score': composite_score,
            't0_signal': final_signal,
            't0_reason': final_reason
        }
        
        return pd.DataFrame([result])
    
    def _calculate_indicators(self, data):
        """
        计算技术指标
        
        Args:
            data (pd.DataFrame): 价格数据
        """
        # 1. 计算移动平均线
        data['ma5'] = data['close'].rolling(5).mean()
        data['ma10'] = data['close'].rolling(10).mean()
        data['ma20'] = data['close'].rolling(20).mean()
        
        # 2. 计算MACD
        ema12 = data['close'].ewm(span=12, adjust=False).mean()
        ema26 = data['close'].ewm(span=26, adjust=False).mean()
        data['macd_dif'] = ema12 - ema26
        data['macd_dea'] = data['macd_dif'].ewm(span=9, adjust=False).mean()
        data['macd_hist'] = data['macd_dif'] - data['macd_dea']
        
        # 3. 计算KDJ
        low_9 = data['low'].rolling(9).min()
        high_9 = data['high'].rolling(9).max()
        rsv = 100 * ((data['close'] - low_9) / (high_9 - low_9))
        data['kdj_k'] = rsv.ewm(alpha=1/3, adjust=False).mean()
        data['kdj_d'] = data['kdj_k'].ewm(alpha=1/3, adjust=False).mean()
        data['kdj_j'] = 3 * data['kdj_k'] - 2 * data['kdj_d']
        
        # 4. 计算RSI
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # 5. 计算布林带
        data['boll_mid'] = data['close'].rolling(20).mean()
        std = data['close'].rolling(20).std()
        data['boll_upper'] = data['boll_mid'] + 2 * std
        data['boll_lower'] = data['boll_mid'] - 2 * std
        
        # 6. 计算乖离率
        data['bias_5'] = (data['close'] - data['ma5']) / data['ma5']
        data['bias_10'] = (data['close'] - data['ma10']) / data['ma10']
        
        # 7. 计算量比
        data['volume_5_avg'] = data['volume'].rolling(5).mean()
        data['volume_ratio'] = data['volume'] / data['volume_5_avg']
        
        # 8. 计算均价线(日内)
        data['amount'] = data['close'] * data['volume']
        data['cum_amount'] = data.groupby(data['date'])['amount'].cumsum()
        data['cum_volume'] = data.groupby(data['date'])['volume'].cumsum()
        data['avg_price'] = data['cum_amount'] / data['cum_volume']
    
    def _evaluate_volume(self, data, eod_data):
        """
        评估成交量指标
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
        
        Returns:
            float: 成交量评分 (0-1)
        """
        # 1. 获取尾盘量比
        eod_volume_ratio = eod_data['volume_ratio'].mean()
        
        # 2. 尾盘换手率
        if 'turnover_rate' in eod_data.columns:
            eod_turnover = eod_data['turnover_rate'].sum()
            
            # 根据市值判断换手率标准
            if 'market_cap' in data.columns:
                market_cap = data['market_cap'].iloc[-1]
                if market_cap < 5e9:  # 小盘股,<50亿
                    turnover_threshold = self.parameters['turnover_rate_small_cap']
                else:  # 中大盘股
                    turnover_threshold = self.parameters['turnover_rate_mid_large_cap']
                
                turnover_score = min(eod_turnover / turnover_threshold, 1.5) / 1.5
            else:
                # 市值未知,使用中等标准
                turnover_score = min(eod_turnover / self.parameters['turnover_rate_mid_large_cap'], 1.5) / 1.5
        else:
            # 无换手率数据,仅依赖量比
            turnover_score = 0.5
        
        # 3. 尾盘量能突增
        if len(eod_data) >= 3:
            last_15min_volume = eod_data.iloc[-3:]['volume'].sum()
            prev_15min_volume = eod_data.iloc[-6:-3]['volume'].sum() if len(eod_data) >= 6 else last_15min_volume
            
            if prev_15min_volume > 0:
                volume_increase = last_15min_volume / prev_15min_volume
                volume_spike_score = min(volume_increase / self.parameters['volume_spike_factor'], 1.5) / 1.5
            else:
                volume_spike_score = 0.5
        else:
            volume_spike_score = 0.5
        
        # 4. 量比与价格协同性
        price_volume_aligned = (eod_data['close'].diff() > 0) == (eod_data['volume_ratio'] > 1)
        alignment_score = price_volume_aligned.mean()
        
        # 5. 综合评分
        volume_score = (
            0.3 * min(eod_volume_ratio / self.parameters['volume_ratio_threshold'], 2) / 2 +
            0.3 * turnover_score +
            0.2 * volume_spike_score +
            0.2 * alignment_score
        )
        
        return min(max(volume_score, 0), 1)
    
    def _evaluate_trend(self, data, eod_data):
        """
        评估价格趋势指标
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
        
        Returns:
            float: 趋势评分 (0-1)
        """
        # 1. 均线多头排列
        ma_trend = (data['ma5'] > data['ma10']) & (data['ma10'] > data['ma20'])
        ma_trend_score = ma_trend.iloc[-1] * 1.0
        
        # 2. 乖离率适中
        bias_5 = data['bias_5'].iloc[-1]
        bias_optimal = (bias_5 >= self.parameters['bias_lower_bound']) & (bias_5 <= self.parameters['bias_upper_bound'])
        bias_score = 1.0 if bias_optimal else 0.5 if bias_5 > 0 else 0.3
        
        # 3. 尾盘站稳均价线
        if self.parameters['price_ma_confirm']:
            price_above_avg = (eod_data['close'] > eod_data['avg_price']).mean()
            avg_line_score = min(price_above_avg * 1.5, 1.0)
        else:
            avg_line_score = 0.5
        
        # 4. 尾盘上涨动能
        eod_price_trend = eod_data['close'].pct_change()
        eod_momentum = eod_price_trend.mean() * 100  # 转为百分比
        momentum_score = min(max((eod_momentum + 1) / 2, 0), 1)  # 归一化到0-1
        
        # 5. 突破前期高点
        if len(data) > 20:
            prev_high = data['high'].iloc[-20:-1].max()
            breakout = data['close'].iloc[-1] > prev_high
            breakout_score = 1.0 if breakout else 0.5
        else:
            breakout_score = 0.5
        
        # 6. 综合评分
        trend_score = (
            0.3 * ma_trend_score +
            0.2 * bias_score +
            0.2 * avg_line_score +
            0.2 * momentum_score +
            0.1 * breakout_score
        )
        
        return min(max(trend_score, 0), 1)
    
    def _evaluate_technical(self, data, eod_data):
        """
        评估技术指标
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
        
        Returns:
            float: 技术指标评分 (0-1)
        """
        # 1. MACD指标
        if self.parameters['macd_zero_line_filter'] and data['macd_dif'].iloc[-1] < 0:
            # MACD DIF在0轴以下,降低评分
            macd_score = 0.3
        else:
            # 检查是否金叉或红柱放大
            macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) & (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
            hist_growing = (data['macd_hist'].iloc[-1] > 0) & (data['macd_hist'].iloc[-1] > data['macd_hist'].iloc[-2])
            
            if macd_cross:
                macd_score = 1.0
            elif hist_growing:
                macd_score = 0.8
            else:
                macd_score = 0.5
        
        # 2. KDJ指标
        kdj_k = data['kdj_k'].iloc[-1]
        kdj_j = data['kdj_j'].iloc[-1]
        
        # 检查KDJ金叉和位置
        kdj_cross = (data['kdj_k'].iloc[-2] < data['kdj_d'].iloc[-2]) & (data['kdj_k'].iloc[-1] > data['kdj_d'].iloc[-1])
        kdj_optimal_zone = (kdj_k > self.parameters['kdj_lower_bound']) & (kdj_k < self.parameters['kdj_upper_bound']) & (kdj_j < 100)
        
        if kdj_cross and kdj_optimal_zone:
            kdj_score = 1.0
        elif kdj_optimal_zone:
            kdj_score = 0.8
        elif kdj_cross:
            kdj_score = 0.7
        else:
            kdj_score = 0.4
        
        # 3. RSI指标
        rsi = data['rsi'].iloc[-1]
        rsi_optimal_zone = (rsi > self.parameters['rsi_lower_bound']) & (rsi < self.parameters['rsi_upper_bound'])
        rsi_rising = data['rsi'].iloc[-1] > data['rsi'].iloc[-2]
        
        if rsi_optimal_zone and rsi_rising:
            rsi_score = 1.0
        elif rsi_optimal_zone:
            rsi_score = 0.8
        elif rsi_rising:
            rsi_score = 0.6
        else:
            rsi_score = 0.4
        
        # 4. 布林带位置
        boll_pos = (data['close'].iloc[-1] - data['boll_lower'].iloc[-1]) / (data['boll_upper'].iloc[-1] - data['boll_lower'].iloc[-1])
        
        if boll_pos > 0.4 and boll_pos < 0.6:
            # 中轨附近
            boll_score = 1.0
        elif boll_pos >= 0.6 and boll_pos < 0.8:
            # 中轨上方,但未过度接近上轨
            boll_score = 0.8
        elif boll_pos >= 0.2 and boll_pos <= 0.4:
            # 中轨下方,但未过度接近下轨
            boll_score = 0.7
        else:
            # 极端位置
            boll_score = 0.4
        
        # 5. 综合评分
        technical_score = (
            0.3 * macd_score +
            0.3 * kdj_score +
            0.2 * rsi_score +
            0.2 * boll_score
        )
        
        return min(max(technical_score, 0), 1)
    
    def _generate_trading_signal(self, composite_score, volume_score, trend_score, technical_score, change_pct):
        """
        生成交易信号和原因
        
        Args:
            composite_score (float): 综合评分
            volume_score (float): 成交量评分
            trend_score (float): 趋势评分
            technical_score (float): 技术指标评分
            change_pct (float): 当日涨跌幅
        
        Returns:
            tuple: (信号, 原因)
        """
        # 根据综合评分决定信号
        if composite_score >= 0.8:
            signal = "强烈买入"
            
            # 生成原因
            if volume_score > 0.8 and trend_score > 0.7:
                reason = "尾盘量价齐升,多头控盘明显,短线上涨概率高"
            elif technical_score > 0.8:
                reason = "尾盘技术指标共振强烈,次日延续概率大"
            else:
                reason = "尾盘综合表现强势,建议积极参与"
                
        elif composite_score >= 0.7:
            signal = "买入"
            
            if volume_score > 0.7:
                reason = "尾盘资金流入明显,短线活跃度高"
            elif trend_score > 0.7:
                reason = "尾盘突破关键阻力位,趋势向好"
            else:
                reason = "尾盘表现良好,可适量建仓"
                
        elif composite_score >= 0.6:
            signal = "观望"
            
            if change_pct > 2:
                reason = "短期涨幅已有,宜等待回调后介入"
            else:
                reason = "盘面表现尚可,建议观望,待信号明确"
                
        else:
            signal = "回避"
            reason = "尾盘表现不佳,不具备短线机会"
        
        return signal, reason

    def _base_strategy(self, data, eod_data):
        """
        基础尾盘选股策略
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 评估各维度得分
        volume_score = self._evaluate_volume(data, eod_data)
        trend_score = self._evaluate_trend(data, eod_data)
        technical_score = self._evaluate_technical(data, eod_data)
        
        # 计算综合得分
        score = (
            volume_score * self.parameters['volume_weight'] +
            trend_score * self.parameters['trend_weight'] +
            technical_score * self.parameters['technical_weight']
        )
        
        # 生成信号和原因
        last_change_pct = (data['close'].iloc[-1] / data['open'].iloc[0] - 1) * 100
        signal, reason = self._generate_trading_signal(score, volume_score, trend_score, technical_score, last_change_pct)
        
        return score, signal, reason

    def _guocheng_strategy(self, data, eod_data):
        """
        国诚投顾尾盘选股策略
        
        特点:
        - 利用尾盘资金动向和技术指标共振捕捉短期机会
        - 筛选尾盘30分钟内量比＞1.5,换手率适中的个股
        - 股价需在均线上方且均线呈多头排列,RSI在指定区间
        - 尾盘最后15分钟出现"二次翻红"(MACD红柱缩短后放大)或金叉信号
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 量比检查
        eod_volume_ratio = eod_data['volume_ratio'].mean()
        volume_condition = eod_volume_ratio >= self.parameters['guocheng_volume_ratio']
        
        # 2. 换手率检查
        if 'turnover_rate' in eod_data.columns:
            eod_turnover = eod_data['turnover_rate'].sum()
            
            # 根据市值判断换手率标准
            if 'market_cap' in data.columns:
                market_cap = data['market_cap'].iloc[-1]
                if market_cap < 5e9:  # 小盘股,<50亿
                    turnover_min = self.parameters['turnover_rate_small_cap']
                    turnover_max = 0.15  # 小盘股换手率5%-15%
                    turnover_condition = turnover_min <= eod_turnover <= turnover_max
                else:  # 中大盘股
                    turnover_min = self.parameters['turnover_rate_mid_large_cap']
                    turnover_max = 0.08  # 中大盘股换手率3%-8%
                    turnover_condition = turnover_min <= eod_turnover <= turnover_max
            else:
                # 市值未知,使用中等标准
                turnover_condition = True
        else:
            # 无换手率数据,不做此项检查
            turnover_condition = True
        
        # 3. 均线多头排列检查
        ma_condition = (data['ma5'].iloc[-1] > data['ma10'].iloc[-1]) and \
                       (data['ma10'].iloc[-1] > data['ma20'].iloc[-1])
        
        # 4. 股价在均线上方检查
        price_above_ma = data['close'].iloc[-1] > data['ma5'].iloc[-1]
        
        # 5. RSI在50-70区间
        rsi = data['rsi'].iloc[-1]
        rsi_condition = self.parameters['guocheng_rsi_lower'] <= rsi <= self.parameters['guocheng_rsi_upper']
        
        # 6. 检查尾盘最后15分钟MACD二次翻红或金叉
        if len(eod_data) >= 15:  # 确保有足够的尾盘数据
            last_15min = eod_data.iloc[-15:].copy()
            
            # MACD金叉
            macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) and \
                         (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
            
            # 检查红柱缩短后放大(二次翻红)
            if len(last_15min) >= 3:
                hist_values = last_15min['macd_hist'].values
                hist_diff = np.diff(hist_values)
                # 红柱先缩短后放大
                red_rebound = False
                for i in range(1, len(hist_diff)):
                    if hist_diff[i-1] < 0 and hist_diff[i] > 0 and hist_values[i+1] > 0:
                        red_rebound = True
                        break
            else:
                red_rebound = False
            
            macd_condition = macd_cross or red_rebound
        else:
            macd_condition = False
        
        # 计算总分
        score = 0.0
        if volume_condition: score += 0.25
        if turnover_condition: score += 0.15
        if ma_condition: score += 0.2
        if price_above_ma: score += 0.1
        if rsi_condition: score += 0.1
        if macd_condition: score += 0.2
        
        # 生成信号和原因
        if score >= 0.8:
            signal = "买入"
            reason = "国诚尾盘策略:量价齐升,技术指标共振,短期看涨"
        elif score >= 0.6:
            signal = "观望"
            reason = "国诚尾盘策略:部分指标满足,可设置盘中提醒"
        else:
            signal = "回避"
            reason = "国诚尾盘策略:关键指标不满足,不符合操作条件"
        
        return score, signal, reason
        
    def _zhinanzhen_strategy(self, data, eod_data):
        """
        指南针尾盘选股策略(红锦鲤摆尾)
        
        特点:
        - 主打"尾盘选股+今买明卖"的短线操作
        - 核心是红锦鲤摆尾:尾盘回踩均线后快速拉升,同时MACD金叉
        - 尾盘量比大,且以主动性买盘为主
        - 优先选择流通市值20-200亿,当日涨幅2%-5%的标的
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 检查尾盘量比
        eod_volume_ratio = eod_data['volume_ratio'].mean()
        volume_condition = eod_volume_ratio >= self.parameters['zhinanzhen_volume_ratio']
        
        # 2. 检查市值是否在目标范围内
        if 'market_cap' in data.columns:
            market_cap = data['market_cap'].iloc[-1]
            cap_condition = self.parameters['zhinanzhen_market_cap_min'] <= market_cap <= self.parameters['zhinanzhen_market_cap_max']
        else:
            cap_condition = True
        
        # 3. 检查涨幅是否在目标范围内
        price_change = (data['close'].iloc[-1] / data['open'].iloc[0] - 1) * 100
        change_condition = self.parameters['min_price_change'] <= price_change <= self.parameters['max_price_change']
        
        # 4. 红锦鲤摆尾模式检查:尾盘回踩均线后快速拉升
        if len(eod_data) >= 10:
            # 检查是否有回踩均线
            price_touched_ma = False
            for i in range(-10, -3):
                if eod_data['close'].iloc[i] <= eod_data['ma5'].iloc[i]:
                    price_touched_ma = True
                    break
            
            # 检查尾盘是否拉升
            if price_touched_ma:
                last_prices = eod_data['close'].iloc[-3:].values
                price_rising = (last_prices[-1] > last_prices[0]) and (last_prices[-1] > last_prices[1])
            else:
                price_rising = False
            
            koi_pattern = price_touched_ma and price_rising
        else:
            koi_pattern = False
        
        # 5. 检查MACD金叉
        macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) and \
                     (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
        
        # 6. 主动买盘检查 (通过价格上涨同时成交量放大简单估计)
        if len(eod_data) >= 5:
            price_volume_corr = eod_data['close'].diff().corr(eod_data['volume'])
            active_buying = price_volume_corr > 0.3
        else:
            active_buying = False
        
        # 计算总分
        score = 0.0
        if volume_condition: score += 0.2
        if cap_condition: score += 0.1
        if change_condition: score += 0.1
        if koi_pattern: score += 0.3
        if macd_cross: score += 0.2
        if active_buying: score += 0.1
        
        # 生成信号和原因
        if score >= 0.7 and koi_pattern:
            signal = "买入"
            if macd_cross:
                reason = "指南针红锦鲤:尾盘回踩均线后拉升,MACD金叉,短线看涨"
            else:
                reason = "指南针红锦鲤:尾盘回踩均线后拉升,主力资金流入明显"
        elif score >= 0.5:
            signal = "观望"
            reason = "指南针红锦鲤:部分特征符合,但不够明确,建议观望"
        else:
            signal = "回避"
            reason = "指南针红锦鲤:未出现摆尾特征,不符合短线操作条件"
        
        return score, signal, reason
        
    def _tn6_strategy(self, data, eod_data):
        """
        尾盘选股王(tn6)策略
        
        特点:
        - 结合资金流,技术指标和新闻事件
        - 关键指标:尾盘30分钟超大单净流入占比＞1%
        - 技术信号:KDJ在50-80金叉,RSI＞50,布林带开口向上
        - 尾盘14:45后,筛选量比＞1.5且股价突破日内高点的个股
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 检查尾盘量比
        eod_volume_ratio = eod_data['volume_ratio'].mean()
        volume_condition = eod_volume_ratio >= self.parameters['tn6_volume_ratio']
        
        # 2. 检查股价是否突破日内高点 (简化为接近日内高点)
        day_high = data['high'].max()
        last_price = data['close'].iloc[-1]
        price_near_high = last_price >= day_high * 0.995
        
        # 3. KDJ检查
        kdj_k = data['kdj_k'].iloc[-1]
        kdj_d = data['kdj_d'].iloc[-1]
        kdj_condition = (50 <= kdj_k <= 80) and kdj_k > kdj_d
        
        # 4. RSI检查
        rsi_condition = data['rsi'].iloc[-1] > 50
        
        # 5. 布林带开口向上检查
        if len(data) >= 30:
            boll_width_now = data['boll_upper'].iloc[-1] - data['boll_lower'].iloc[-1]
            boll_width_prev = data['boll_upper'].iloc[-10] - data['boll_lower'].iloc[-10]
            boll_opening_up = boll_width_now > boll_width_prev and data['boll_mid'].iloc[-1] > data['boll_mid'].iloc[-5]
        else:
            boll_opening_up = False
        
        # 6. 超大单净流入检查 (由于没有实际超大单数据,简化估计)
        # 实际应用中应通过超大单数据计算
        super_fund_inflow = True  # 假设满足条件
        
        # 7. MACD金叉或红柱放大检查
        macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) and \
                     (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
        
        macd_hist_growing = (data['macd_hist'].iloc[-1] > 0) and \
                            (data['macd_hist'].iloc[-1] > data['macd_hist'].iloc[-2])
        
        macd_condition = macd_cross or macd_hist_growing
        
        # 计算总分
        score = 0.0
        if volume_condition: score += 0.15
        if price_near_high: score += 0.15
        if kdj_condition: score += 0.15
        if rsi_condition: score += 0.1
        if boll_opening_up: score += 0.1
        if super_fund_inflow: score += 0.2
        if macd_condition: score += 0.15
        
        # 生成信号和原因
        if score >= 0.7 and volume_condition and (price_near_high or macd_condition):
            signal = "买入"
            if macd_condition and price_near_high:
                reason = "尾盘选股王:放量突破日内高点,MACD指标共振,主力资金介入"
            else:
                reason = "尾盘选股王:尾盘资金流动活跃,技术指标向好,可短线介入"
        elif score >= 0.5:
            signal = "观望"
            reason = "尾盘选股王:部分指标满足,但动能不足,建议观望"
        else:
            signal = "回避"
            reason = "尾盘选股王:关键指标不满足,不具备短线机会"
        
        return score, signal, reason

    def _jingchuan_strategy(self, data, eod_data):
        """
        经传短线尾盘策略
        
        特点:
        - 核心方法:"捕捞季节"+"主力追踪"指标共振
        - 尾盘出现金叉信号,且红柱放大
        - 主力资金持续流入,股价在智能辅助线上方
        - 尾盘成交量较前5日均值放大1.5倍以上
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 尾盘成交量放大检查
        if len(data) >= 5*240:  # 假设有5天的分钟数据
            # 计算前5日同时段均值
            prev_days = 5
            mins_per_day = 240
            eod_start_idx = len(eod_data)
            
            # 计算前几天同一时段的成交量均值
            prev_volume_sum = 0
            count = 0
            
            for i in range(1, prev_days+1):
                start_idx = len(data) - (i * mins_per_day + eod_start_idx)
                end_idx = len(data) - (i * mins_per_day)
                
                if start_idx >= 0:
                    prev_volume_sum += data['volume'].iloc[start_idx:end_idx].sum()
                    count += 1
            
            if count > 0:
                prev_avg_volume = prev_volume_sum / count
                current_volume = eod_data['volume'].sum()
                volume_expansion = current_volume / prev_avg_volume
                volume_condition = volume_expansion >= self.parameters['jingchuan_volume_ratio']
            else:
                volume_condition = False
        else:
            # 如果没有足够的历史数据,简化检查为当前成交量是否高于均值
            volume_condition = eod_data['volume_ratio'].mean() >= self.parameters['jingchuan_volume_ratio']
        
        # 2. "捕捞季节"金叉信号 (使用MACD金叉作为简化估计)
        macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) and \
                     (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
        
        # 3. 红柱放大检查
        macd_hist_growing = (data['macd_hist'].iloc[-1] > 0) and \
                            (data['macd_hist'].iloc[-1] > data['macd_hist'].iloc[-2])
        
        # 4. 主力资金流入检查(使用价格与量的关系简化估计)
        if len(eod_data) >= 5:
            price_rising = eod_data['close'].iloc[-1] > eod_data['close'].iloc[-5]
            volume_rising = eod_data['volume'].iloc[-5:].mean() > eod_data['volume'].iloc[-10:-5].mean()
            fund_inflow = price_rising and volume_rising
        else:
            fund_inflow = False
        
        # 5. 股价在智能辅助线上方(使用10日均线作为简化估计)
        price_above_line = data['close'].iloc[-1] > data['ma10'].iloc[-1]
        
        # 计算总分
        score = 0.0
        if volume_condition: score += 0.25
        if macd_cross: score += 0.25
        if macd_hist_growing: score += 0.15
        if fund_inflow: score += 0.2
        if price_above_line: score += 0.15
        
        # 生成信号和原因
        if score >= 0.75 and macd_cross and volume_condition:
            signal = "买入"
            reason = "经传短线策略:捕捞季节金叉,尾盘量能明显放大,主力资金持续流入"
        elif score >= 0.5:
            signal = "观望"
            reason = "经传短线策略:部分信号出现,但未形成完美共振,建议观望"
        else:
            signal = "回避"
            reason = "经传短线策略:关键指标未满足,不符合操作条件"
        
        return score, signal, reason
        
    def _qiankun_strategy(self, data, eod_data):
        """
        乾坤六道尾盘选股法
        
        特点:
        - 结合MACD,KDJ,RSI,威廉指标等六大道指标共振
        - 六道指标同时金叉,且股价在20日均线上方
        - 尾盘出现"长下影阳线"或"启明星"形态
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 检查股价是否在20日均线上方
        price_above_ma20 = data['close'].iloc[-1] > data['ma20'].iloc[-1]
        
        # 2. 检查六大技术指标
        # 2.1 MACD金叉
        macd_cross = (data['macd_dif'].iloc[-2] < data['macd_dea'].iloc[-2]) and \
                     (data['macd_dif'].iloc[-1] > data['macd_dea'].iloc[-1])
        
        # 2.2 KDJ金叉
        kdj_cross = (data['kdj_k'].iloc[-2] < data['kdj_d'].iloc[-2]) and \
                    (data['kdj_k'].iloc[-1] > data['kdj_d'].iloc[-1])
        
        # 2.3 RSI金叉(简化为RSI上穿50)
        rsi_cross = (data['rsi'].iloc[-2] < 50) and (data['rsi'].iloc[-1] > 50)
        
        # 2.4 布林带金叉(简化为价格上穿中轨)
        boll_cross = (data['close'].iloc[-2] < data['boll_mid'].iloc[-2]) and \
                     (data['close'].iloc[-1] > data['boll_mid'].iloc[-1])
        
        # 2.5 均线金叉(简化为5日均线上穿10日均线)
        ma_cross = (data['ma5'].iloc[-2] < data['ma10'].iloc[-2]) and \
                   (data['ma5'].iloc[-1] > data['ma10'].iloc[-1])
        
        # 2.6 成交量金叉(简化为成交量突破5日均量)
        vol_cross = (data['volume'].iloc[-2] < data['volume_5_avg'].iloc[-2]) and \
                    (data['volume'].iloc[-1] > data['volume_5_avg'].iloc[-1])
        
        # 六道指标共振检测
        if self.parameters['qiankun_all_indicators_golden']:
            # 要求全部指标金叉
            indicators_all_golden = macd_cross and kdj_cross and rsi_cross and boll_cross and ma_cross and vol_cross
        else:
            # 至少4个指标金叉
            golden_count = sum([macd_cross, kdj_cross, rsi_cross, boll_cross, ma_cross, vol_cross])
            indicators_all_golden = golden_count >= 4
        
        # 3. 检查尾盘K线形态
        if len(eod_data) >= 2:
            # 检查长下影阳线
            last_k = eod_data.iloc[-1]
            body_length = abs(last_k['close'] - last_k['open'])
            
            if last_k['close'] > last_k['open']:  # 阳线
                lower_shadow = last_k['open'] - last_k['low']
                long_lower_shadow = lower_shadow > 2 * body_length
            else:
                long_lower_shadow = False
            
            # 检查启明星形态(简化)
            if len(eod_data) >= 3:
                k1 = eod_data.iloc[-3]
                k2 = eod_data.iloc[-2]
                k3 = eod_data.iloc[-1]
                
                morning_star = (k1['close'] < k1['open']) and \
                              (abs(k2['close'] - k2['open']) < abs(k1['close'] - k1['open']) * 0.3) and \
                              (k3['close'] > k3['open']) and \
                              (k3['close'] > (k1['open'] + k1['close']) / 2)
            else:
                morning_star = False
                
            special_pattern = long_lower_shadow or morning_star
        else:
            special_pattern = False
        
        # 计算总分
        score = 0.0
        if price_above_ma20: score += 0.1
        
        # 指标加分
        indicator_score = 0
        if macd_cross: indicator_score += 1
        if kdj_cross: indicator_score += 1
        if rsi_cross: indicator_score += 1
        if boll_cross: indicator_score += 1
        if ma_cross: indicator_score += 1
        if vol_cross: indicator_score += 1
        score += (indicator_score / 6) * 0.6  # 指标最高占60%权重
        
        if special_pattern: score += 0.3
        
        # 生成信号和原因
        if score >= 0.7 and indicators_all_golden:
            signal = "买入"
            if special_pattern:
                reason = "乾坤六道:六大指标共振金叉,尾盘K线形态良好,短线强势"
            else:
                reason = "乾坤六道:技术指标多重共振,强势特征明显"
        elif score >= 0.5:
            signal = "观望"
            reason = "乾坤六道:部分指标共振,但未达到最佳标准,建议观望"
        else:
            signal = "回避"
            reason = "乾坤六道:指标共振不足,不符合操作条件"
        
        return score, signal, reason
        
    def _jiufang_strategy(self, data, eod_data):
        """
        九方智投尾盘策略
        
        特点:
        - 关注尾盘K线形态与量价关系
        - 长下影阳线:尾盘探底回升,表明支撑强劲,次日高开概率大
        - 尾盘放巨量但收红:结合股价位置判断
        
        Args:
            data (pd.DataFrame): 完整数据
            eod_data (pd.DataFrame): 尾盘数据
            
        Returns:
            tuple: (得分, 信号, 原因)
        """
        # 1. 检查尾盘是否形成长下影阳线
        if len(eod_data) >= 2:
            last_k = eod_data.iloc[-1]
            if last_k['close'] > last_k['open']:  # 阳线
                body_length = last_k['close'] - last_k['open']
                shadow_length = last_k['open'] - last_k['low']
                
                # 长下影线定义:下影线长度超过收盘价的一定比例
                shadow_threshold = last_k['close'] * self.parameters['jiufang_low_shadow_length']
                long_lower_shadow = shadow_length > shadow_threshold and shadow_length > body_length
            else:
                long_lower_shadow = False
        else:
            long_lower_shadow = False
        
        # 2. 检查尾盘是否放量
        volume_spike = eod_data['volume_ratio'].mean() > 1.5
        
        # 3. 检查尾盘收红
        if len(eod_data) >= 5:
            eod_open = eod_data['open'].iloc[0]
            eod_close = eod_data['close'].iloc[-1]
            eod_red = eod_close > eod_open
        else:
            eod_red = False
        
        # 4. 股价位置判断(低位/高位)
        # 使用20日均线作为参考
        if 'ma20' in data.columns:
            price_position = data['close'].iloc[-1] / data['ma20'].iloc[-1] - 1
            low_position = price_position < -0.05  # 股价低于20日均线5%以上视为低位
            high_position = price_position > 0.1   # 股价高于20日均线10%以上视为高位
        else:
            low_position = False
            high_position = False
        
        # 5. 检查股价是否在均线上方企稳
        if len(eod_data) >= 5:
            price_above_ma = (eod_data['close'] > eod_data['ma5']).mean() > 0.6  # 60%时间在均线上方
        else:
            price_above_ma = False
        
        # 6. 尾盘回踩不破低点
        if len(eod_data) >= 10:
            early_low = eod_data['low'].iloc[:5].min()
            late_low = eod_data['low'].iloc[-5:].min()
            no_break_low = late_low >= early_low
        else:
            no_break_low = False
        
        # 计算总分
        score = 0.0
        
        # 长下影阳线是重要特征
        if long_lower_shadow: score += 0.3
        
        # 量价配合
        if volume_spike and eod_red:
            if low_position:  # 低位放量收红,可能是建仓
                score += 0.3
            elif high_position:  # 高位放量收红,警惕出货
                score += 0.1
            else:  # 中位放量收红
                score += 0.2
        elif volume_spike:
            score += 0.1
        
        if price_above_ma: score += 0.2
        if no_break_low: score += 0.2
        
        # 生成信号和原因
        if score >= 0.7:
            if long_lower_shadow:
                signal = "买入"
                reason = "九方智投:尾盘形成长下影阳线,探底回升支撑明显,次日看涨"
            elif volume_spike and eod_red and low_position:
                signal = "买入"
                reason = "九方智投:低位尾盘放量收红,主力资金可能介入,次日看涨"
            else:
                signal = "买入"
                reason = "九方智投:尾盘走势强势,技术形态良好,可短线参与"
        elif score >= 0.5:
            signal = "观望"
            reason = "九方智投:尾盘表现一般,形态不够明确,建议观望"
        else:
            signal = "回避"
            reason = "九方智投:未见明显买点,不符合操作条件"
        
        return score, signal, reason

# 在策略初始化文件中注册此策略
# 需要在__init__.py中添加相应的导入和注册代码 
 
