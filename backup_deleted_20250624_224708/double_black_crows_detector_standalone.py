import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class DoubleBlackCrowsDetector:
    """
    双飞乌鸦（Double Black Crows）检测器
    
    双飞乌鸦是一种经典的看跌K线组合，通常出现在上涨趋势末端或盘整区间的高位，预示着股价可能见顶回落。
    
    核心特征：
    1. 第一根K线：通常是一根高开低走的阴线（或阳线，但实体较短），留有上影线
    2. 第二根K线：再次跳高开盘，但收盘价低于第一根阴线的收盘价，形成第二根阴线
    3. 两根阴线呈"乌鸦"状并列，实体部分有重叠或向下倾斜
    
    该形态的核心是"高位连续两根阴线，空头力量增强"，反映多空博弈中空方开始占据主动。
    
    验证信号有效性需要考虑：
    1. 出现位置（高位出现更可靠）
    2. 成交量特征（放量更可靠）
    3. 后续验证（第三根K线继续收阴更确认）
    """
    
    def __init__(self):
        self.name = "双飞乌鸦检测器"
        self.description = "检测双飞乌鸦K线形态，评估其有效性和强度"
        
        # 默认参数
        self.params = {
            # 形态识别参数
            'trend_lookback': 10,            # 检查趋势的回溯天数
            'uptrend_threshold': 0.05,       # 定义上涨趋势的阈值(5%)
            'first_candle_body_ratio': 0.4,  # 第一根K线实体/影线比例最小值
            'second_open_ratio': 0.0,        # 第二根K线开盘价需高于第一根多少(0%表示高开即可)
            'overlap_threshold': 0.3,        # 第二根K线与第一根实体重叠占比
            
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
            'false_signal_threshold': 0.01,   # 突破前高多少视为假信号(1%)
            
            # 风险控制参数
            'stop_loss_pct': 0.03,            # 止损比例(3%)
            'first_reduce_pct': 0.5,          # 首次减仓比例(50%)
            'ma5_ma10_cross_weight': 0.4,     # 5日均线与10日均线交叉的权重
            
            # 其他参数
            'high_vol_threshold': 0.8,        # 成交量位于高位的阈值
            'top_shadow_ratio': 0.5,          # 上影线/实体比例阈值
            'macd_weight': 0.3                # MACD指标的权重
        }
    
    def detect_double_crows(self, data):
        """
        检测双飞乌鸦形态
        
        Args:
            data (pd.DataFrame): OHLCV数据
            
        Returns:
            tuple: (信号列表, 形态强度和特征)
        """
        # 创建数据副本
        df = data.copy()
        
        # 确保数据完整性
        if len(df) < max(self.params['trend_lookback'], self.params['position_lookback']) + 3:
            return pd.Series(0, index=df.index), {}
        
        # 计算必要指标
        self._calculate_indicators(df)
        
        # 初始化结果
        signals = pd.Series(0, index=df.index)
        pattern_details = {}
        
        # 遍历K线寻找双飞乌鸦形态
        for i in range(2, len(df)):
            # 获取最近三根K线
            current = df.iloc[i]
            prev1 = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # 1. 检查是否处于上涨趋势
            uptrend = self._check_uptrend(df, i)
            
            # 2. 检查第一根K线（阴线或带长上影线的小阳线）
            first_candle_valid = (
                (not prev1['is_bullish'] or  # 阴线
                 (prev1['is_bullish'] and prev1['upper_shadow_ratio'] > self.params['top_shadow_ratio']))  # 带长上影线的阳线
            )
            
            # 3. 检查第二根K线（阴线，且开盘高于第一根，收盘低于第一根）
            second_candle_valid = (
                not current['is_bullish'] and  # 阴线
                current['open'] >= prev1['open'] * (1 + self.params['second_open_ratio']) and  # 高开
                current['close'] < prev1['close']  # 收盘低于前一根
            )
            
            # 4. 检查两根K线形成的双飞乌鸦形态
            if uptrend and first_candle_valid and second_candle_valid:
                # 计算形态强度
                strength, pattern_features = self._evaluate_pattern_strength(df, i)
                
                # 如果形态强度超过阈值，生成信号
                if strength >= self.params['min_pattern_quality']:
                    signals.iloc[i] = -1  # 生成卖出信号
                    pattern_details[df.index[i]] = {
                        'strength': strength,
                        'features': pattern_features,
                        'action': self._generate_action_suggestion(strength, pattern_features)
                    }
        
        return signals, pattern_details
    
    def _calculate_indicators(self, df):
        """
        计算分析所需的技术指标
        
        Args:
            df (pd.DataFrame): 价格数据
        """
        # 计算K线基本特征
        df['body_size'] = abs(df['close'] - df['open'])
        df['candle_range'] = df['high'] - df['low']
        df['is_bullish'] = df['close'] > df['open']
        
        # 计算影线比例
        df['upper_shadow'] = df.apply(
            lambda x: x['high'] - max(x['open'], x['close']), axis=1)
        df['lower_shadow'] = df.apply(
            lambda x: min(x['open'], x['close']) - x['low'], axis=1)
        
        # 计算影线比例
        df['upper_shadow_ratio'] = df.apply(
            lambda x: 0 if x['body_size'] == 0 else x['upper_shadow'] / x['body_size'], axis=1)
        df['lower_shadow_ratio'] = df.apply(
            lambda x: 0 if x['body_size'] == 0 else x['lower_shadow'] / x['body_size'], axis=1)
        
        # 计算成交量比例
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(
            window=self.params['volume_lookback']).mean()
        
        # 计算均线
        for period in self.params['ma_periods']:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 计算MACD
        self._calculate_macd(df)
        
        # 计算RSI
        self._calculate_rsi(df)
        
        # 计算位置指标
        self._calculate_position_indicators(df)
    
    def _calculate_macd(self, df, fast=12, slow=26, signal=9):
        """
        计算MACD指标
        
        Args:
            df (pd.DataFrame): 价格数据
            fast (int): 快线周期
            slow (int): 慢线周期
            signal (int): 信号线周期
        """
        # 计算EMA
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        
        # 计算MACD线和信号线
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 判断MACD死叉
        df['macd_death_cross'] = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        # 判断MACD顶背离
        df['macd_divergence'] = False
        for i in range(20, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-10:i].max() and df['macd'].iloc[i] < df['macd'].iloc[i-10:i].max():
                df['macd_divergence'].iloc[i] = True
    
    def _calculate_rsi(self, df, period=14):
        """
        计算RSI指标
        
        Args:
            df (pd.DataFrame): 价格数据
            period (int): 计算周期
        """
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
    
    def _calculate_position_indicators(self, df):
        """
        计算位置指标
        
        Args:
            df (pd.DataFrame): 价格数据
        """
        lookback = self.params['position_lookback']
        
        # 计算当前价格相对区间位置
        df['high_lookback'] = df['high'].rolling(window=lookback).max()
        df['low_lookback'] = df['low'].rolling(window=lookback).min()
        df['position_in_range'] = (df['close'] - df['low_lookback']) / (df['high_lookback'] - df['low_lookback'])
        
        # 计算价格相对均线位置
        for period in self.params['ma_periods']:
            ma_col = f'ma{period}'
            if ma_col in df.columns:
                df[f'above_{ma_col}'] = df['close'] > df[ma_col]
        
        # 计算均线交叉
        df['ma5_cross_below_ma10'] = (df['ma5'] < df['ma10']) & (df['ma5'].shift(1) >= df['ma10'].shift(1))
        
        # 计算量能位置
        df['volume_high'] = df['volume'] > df['volume'].rolling(window=lookback).mean() * self.params['high_vol_threshold']
    
    def _check_uptrend(self, df, index):
        """
        检查是否处于上涨趋势
        
        Args:
            df (pd.DataFrame): 价格数据
            index (int): 当前K线索引
            
        Returns:
            bool: 是否处于上涨趋势
        """
        if index < self.params['trend_lookback']:
            return False
        
        # 检查是否相比回溯期的起点有明显上涨
        start_price = df['close'].iloc[index - self.params['trend_lookback']]
        current_price = df['close'].iloc[index]
        price_change = (current_price - start_price) / start_price
        
        # 检查均线多头排列
        ma_uptrend = all(
            df[f'ma{self.params["ma_periods"][i]}'].iloc[index] > 
            df[f'ma{self.params["ma_periods"][i+1]}'].iloc[index]
            for i in range(len(self.params['ma_periods'])-1)
        )
        
        # 检查位置是否处于高位
        high_position = df['position_in_range'].iloc[index] > self.params['high_position_threshold']
        
        # 综合判断上涨趋势
        return (price_change > self.params['uptrend_threshold'] or ma_uptrend) and high_position
    
    def _evaluate_pattern_strength(self, df, index):
        """
        评估双飞乌鸦形态的强度
        
        Args:
            df (pd.DataFrame): 价格数据
            index (int): 当前K线索引
            
        Returns:
            tuple: (强度得分, 形态特征)
        """
        current = df.iloc[index]
        prev1 = df.iloc[index-1]
        
        features = {}
        score = 0.0
        max_score = 0.0
        
        # 1. 位置评分 (30分)
        max_score += 30
        position_score = 0
        
        # 高位出现双飞乌鸦更可靠
        if current['position_in_range'] > 0.9:
            position_score += 30
            features['position'] = 'extreme_high'
        elif current['position_in_range'] > 0.8:
            position_score += 25
            features['position'] = 'very_high'
        elif current['position_in_range'] > 0.7:
            position_score += 20
            features['position'] = 'high'
        elif current['position_in_range'] > 0.5:
            position_score += 10
            features['position'] = 'medium'
        else:
            features['position'] = 'low'
        
        score += position_score
        
        # 2. K线形态评分 (30分)
        max_score += 30
        candle_score = 0
        
        # 第一根K线带长上影线
        if prev1['upper_shadow_ratio'] > 1.0:
            candle_score += 10
            features['first_candle'] = 'long_upper_shadow'
        elif not prev1['is_bullish']:
            candle_score += 8
            features['first_candle'] = 'bearish'
        else:
            features['first_candle'] = 'small_bullish'
        
        # 第二根K线为大阴线
        body_ratio = current['body_size'] / current['candle_range']
        if not current['is_bullish'] and body_ratio > 0.7:
            candle_score += 10
            features['second_candle'] = 'strong_bearish'
        elif not current['is_bullish'] and body_ratio > 0.5:
            candle_score += 8
            features['second_candle'] = 'medium_bearish'
        else:
            candle_score += 5
            features['second_candle'] = 'weak_bearish'
        
        # 两根K线的排列关系
        if current['open'] > prev1['open'] and current['close'] < prev1['close']:
            candle_score += 10
            features['arrangement'] = 'perfect'
        elif current['open'] > prev1['close'] and current['close'] < prev1['close']:
            candle_score += 8
            features['arrangement'] = 'strong'
        elif current['close'] < prev1['close']:
            candle_score += 5
            features['arrangement'] = 'acceptable'
        
        score += candle_score
        
        # 3. 成交量特征评分 (20分)
        max_score += 20
        volume_score = 0
        
        # 第二根K线放量
        if current['volume_ratio'] > 2.0:
            volume_score += 20
            features['volume'] = 'heavy_surge'
        elif current['volume_ratio'] > 1.5:
            volume_score += 15
            features['volume'] = 'surge'
        elif current['volume_ratio'] > 1.2:
            volume_score += 10
            features['volume'] = 'increased'
        elif current['volume_ratio'] < 0.8:
            volume_score += 5
            features['volume'] = 'shrinking'
        else:
            features['volume'] = 'normal'
        
        score += volume_score
        
        # 4. 技术指标确认 (20分)
        max_score += 20
        indicator_score = 0
        
        # MACD死叉或顶背离
        if 'macd_death_cross' in current and current['macd_death_cross']:
            indicator_score += 10
            features['macd'] = 'death_cross'
        elif 'macd_divergence' in current and current['macd_divergence']:
            indicator_score += 8
            features['macd'] = 'divergence'
        
        # RSI超买
        if 'rsi' in current and current['rsi'] > 70:
            indicator_score += 10
            features['rsi'] = 'overbought'
        elif 'rsi' in current and current['rsi'] > 60:
            indicator_score += 5
            features['rsi'] = 'high'
        
        score += indicator_score
        
        # 计算总分百分比
        strength = score / max_score if max_score > 0 else 0
        
        # 记录关键特征
        features['overall_strength'] = strength
        features['position_score'] = position_score
        features['candle_score'] = candle_score
        features['volume_score'] = volume_score
        features['indicator_score'] = indicator_score
        
        return strength, features
    
    def _generate_action_suggestion(self, strength, features):
        """
        根据形态强度和特征生成行动建议
        
        Args:
            strength (float): 形态强度得分
            features (dict): 形态特征
            
        Returns:
            str: 行动建议
        """
        if strength >= 0.8:
            return f"强烈减仓信号：减仓{int(self.params['first_reduce_pct']*100)}%，止损位设置在最低点下方{int(self.params['stop_loss_pct']*100)}%"
        elif strength >= 0.6:
            return f"明确减仓信号：建议减仓{int(self.params['first_reduce_pct']*75)}%，严格设置止损"
        elif strength >= 0.4:
            return "谨慎看待：在第三根K线确认前减仓一部分，等待进一步确认"
        else:
            return "弱信号：保持关注，但暂不行动，可能是短期洗盘"
    
    def visualize_pattern(self, data, signals, pattern_details, title="双飞乌鸦形态分析"):
        """
        可视化双飞乌鸦形态
        
        Args:
            data (pd.DataFrame): 价格数据
            signals (pd.Series): 信号列表
            pattern_details (dict): 形态详情
            title (str): 图表标题
        """
        # 确保有检测到形态
        if signals.sum() == 0:
            print("未检测到双飞乌鸦形态")
            return
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制K线图
        for i in range(len(data)):
            date = data.index[i]
            op, hi, lo, cl = data.iloc[i][['open', 'high', 'low', 'close']]
            
            # K线颜色
            color = 'red' if cl >= op else 'green'
            
            # K线实体
            ax1.plot([date, date], [op, cl], color=color, linewidth=3)
            
            # 上下影线
            ax1.plot([date, date], [lo, min(op, cl)], color=color, linewidth=1)
            ax1.plot([date, date], [max(op, cl), hi], color=color, linewidth=1)
        
        # 绘制均线
        for period in self.params['ma_periods']:
            ma_col = f'ma{period}'
            if ma_col in data.columns:
                ax1.plot(data.index, data[ma_col], 
                         label=f"{period}日均线", 
                         alpha=0.7, 
                         linewidth=1)
        
        # 标记双飞乌鸦形态
        pattern_dates = [date for date in pattern_details.keys()]
        
        for date in pattern_dates:
            if date in data.index:
                idx = data.index.get_loc(date)
                if idx >= 2:
                    # 找到形态的三根K线
                    crow1_date = data.index[idx-1]
                    crow2_date = date
                    
                    # 绘制标记
                    ax1.plot([crow1_date, crow2_date], 
                             [data.loc[crow1_date, 'high'], data.loc[crow2_date, 'high']], 
                             'ro-', markersize=8, linewidth=2)
                    
                    # 添加文本说明
                    strength = pattern_details[date]['strength']
                    strength_text = "强" if strength >= 0.8 else "中" if strength >= 0.5 else "弱"
                    
                    ax1.annotate(f"双飞乌鸦({strength_text})",
                                xy=(crow2_date, data.loc[crow2_date, 'high']),
                                xytext=(10, 20),
                                textcoords='offset points',
                                arrowprops=dict(arrowstyle='->', color='red'),
                                color='red',
                                fontweight='bold')
                    
                    # 添加行动建议
                    if 'action' in pattern_details[date]:
                        action = pattern_details[date]['action']
                        ax1.annotate(action,
                                    xy=(crow2_date, data.loc[crow2_date, 'low']),
                                    xytext=(10, -30),
                                    textcoords='offset points',
                                    color='blue',
                                    fontsize=8,
                                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))
        
        # 绘制成交量
        ax2.bar(data.index, data['volume'], color='skyblue', alpha=0.7)
        ax2.set_ylabel('成交量')
        
        # 设置标题和标签
        ax1.set_title(title)
        ax1.set_ylabel('价格')
        ax1.grid(True, alpha=0.3)
        ax2.grid(True, alpha=0.3)
        
        # 添加图例
        ax1.legend(loc='best')
        
        # 格式化日期
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 旋转日期标签
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.savefig('double_black_crows_analysis.png')
        print("分析图表已保存为 'double_black_crows_analysis.png'")
        
        # 输出形态详情
        print("\n双飞乌鸦形态分析:")
        for date, details in pattern_details.items():
            print(f"\n日期: {date}")
            print(f"信号强度: {details['strength']:.2f}")
            print("特征详情:")
            for key, value in details['features'].items():
                if key not in ['overall_strength', 'position_score', 'candle_score', 'volume_score', 'indicator_score']:
                    print(f"  - {key}: {value}")
            print(f"行动建议: {details['action']}")
        
        return fig 