import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity
from tensorflow.keras import layers, models

class MarketPatternRecognizer:
    """
    市场模式识别核心模块
    功能:
    1. 实时K线模式识别
    2. 量价关系模式挖掘
    3. 多周期共振模式检测
    4. 主力资金行为模式分析
    """
    
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.pattern_models = {
            'kmeans': KMeans(n_clusters=n_clusters),
            'kde': KernelDensity(bandwidth=0.5)
        }
        self.autoencoder = self._build_autoencoder()

    def _build_autoencoder(self):
        """构建深度特征提取自编码器"""
        input_dim = 10  # 输入特征维度
        encoder = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu')
        ])
        decoder = models.Sequential([
            layers.Dense(32, activation='relu', input_shape=(16,)),
            layers.Dense(64, activation='relu'),
            layers.Dense(input_dim, activation='linear')
        ])
        autoencoder = models.Sequential([encoder, decoder])
        autoencoder.compile(optimizer='adam', loss='mse')
        return autoencoder

    def detect_candlestick_patterns(self, ohlc_data):
        """实时K线模式识别"""
        # 添加多维度特征
        features = self._extract_features(ohlc_data)
        
        # 深度特征提取
        encoded_features = self.autoencoder.predict(features)
        
        # 模式聚类
        clusters = self.pattern_models['kmeans'].fit_predict(encoded_features)
        
        # 模式概率计算
        self.pattern_models['kde'].fit(encoded_features)
        log_prob = self.pattern_models['kde'].score_samples(encoded_features)
        
        return {
            'cluster_labels': clusters,
            'pattern_probability': np.exp(log_prob)
        }

    def _extract_features(self, ohlc_data):
        """提取多维量价特征"""
        df = pd.DataFrame(ohlc_data)
        features = pd.DataFrame()
        
        # 基础特征
        features['body_ratio'] = (df['close'] - df['open']) / (df['high'] - df['low'] + 1e-5)
        features['upper_shadow'] = (df['high'] - np.maximum(df['close'], df['open']))
        features['lower_shadow'] = (np.minimum(df['close'], df['open']) - df['low'])
        
        # 动量特征
        features['momentum_5'] = df['close'].pct_change(5)
        features['momentum_20'] = df['close'].pct_change(20)
        
        # 波动率特征
        features['volatility_10'] = df['close'].rolling(10).std()
        
        # 量能特征
        features['volume_ma_5'] = df['volume'].rolling(5).mean()
        features['volume_ma_20'] = df['volume'].rolling(20).mean()
        
        return features.dropna().values

    def analyze_cross_market_patterns(self, market_data):
        """跨市场关联模式分析"""
        aligned_data = self._align_market_data(market_data)  # 多市场数据时空对齐
        corr_matrix = aligned_data.corr()  # 动态相关性矩阵
        return self._detect_dominant_patterns(corr_matrix)  # SVD模式提取

    def _align_market_data(self, market_data):
        """多市场数据时空对齐"""
        # 实现多市场数据的时间对齐和标准化
        return pd.DataFrame(market_data).dropna().apply(lambda x: (x - x.mean())/x.std())

    def _detect_dominant_patterns(self, corr_matrix):
        """主导模式检测"""
        # 使用奇异值分解进行模式提取
        U, s, Vt = np.linalg.svd(corr_matrix)
        return U[:, :self.n_clusters]
