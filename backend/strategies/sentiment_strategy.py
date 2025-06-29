from typing import Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest
from .base_strategy import BaseStrategy

class SentimentStrategy(BaseStrategy):
    """
    基于市场情绪分析的择时策略
    整合新闻情感分析,社交媒体情绪和订单流分析
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.anomaly_detector = IsolationForest(n_estimators=100)
        
    def calculate_features(self, market_data: Dict) -> Dict:
        """综合市场情绪特征工程"""
        features = {
            'news_sentiment': market_data.get('news_sentiment', 0.5),
            'social_media_volatility': self._calc_social_volatility(market_data),
            'order_flow_imbalance': market_data['bid_volume'] / (market_data['ask_volume'] + 1e-6),
            'vwap_deviation': (market_data['price'] - market_data['vwap']) / market_data['vwap']
        }
        return features

    def _calc_social_volatility(self, data: Dict) -> float:
        """计算社交媒体情绪波动率"""
        posts = data.get('social_posts', [])
        sentiments = [p['sentiment'] for p in posts[-100:]]
        return np.std(sentiments) if len(sentiments) > 10 else 0

    def execute(self, market_data: Dict) -> Dict:
        """
        执行策略逻辑:
        1. 特征工程
        2. 异常检测
        3. 生成交易信号
        """
        features = self.calculate_features(market_data)
        feature_vector = list(features.values())
        
        # 异常检测
        anomaly_score = self.anomaly_detector.decision_function([feature_vector])[0]
        
        # 生成信号
        signal_strength = self._calculate_signal_strength(anomaly_score)
        
        return {
            'timestamp': market_data['timestamp'],
            'signal': signal_strength,
            'features': features,
            'anomaly_score': anomaly_score
        }

    def _calculate_signal_strength(self, score: float) -> float:
        """将异常分数转换为交易信号"""
        if score < -0.6:
            return -1.0  # 强烈卖出
        elif score < -0.3:
            return -0.5  # 适度卖出
        elif score > 0.6:
            return 1.0   # 强烈买入
        elif score > 0.3:
            return 0.5   # 适度买入
        return 0.0       # 中性
