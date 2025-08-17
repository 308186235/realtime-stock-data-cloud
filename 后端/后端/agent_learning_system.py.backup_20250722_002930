#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent智能学习系统 - 基于历史数据的机器学习
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import talib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'agent_trading',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        df = df.copy()
        
        # 移动平均线
        df['ma5'] = talib.SMA(df['close_price'], timeperiod=5)
        df['ma10'] = talib.SMA(df['close_price'], timeperiod=10)
        df['ma20'] = talib.SMA(df['close_price'], timeperiod=20)
        df['ma60'] = talib.SMA(df['close_price'], timeperiod=60)
        
        # MACD
        df['macd_dif'], df['macd_dea'], df['macd_histogram'] = talib.MACD(df['close_price'])
        
        # RSI
        df['rsi'] = talib.RSI(df['close_price'], timeperiod=14)
        
        # KDJ
        df['kdj_k'], df['kdj_d'] = talib.STOCH(df['high_price'], df['low_price'], df['close_price'])
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        # 布林带
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close_price'])
        
        # 成交量指标
        df['volume_ma5'] = talib.SMA(df['volume'], timeperiod=5)
        df['volume_ratio'] = df['volume'] / df['volume_ma5']
        
        # 价格位置
        df['price_position'] = (df['close_price'] - df['low_price']) / (df['high_price'] - df['low_price'])
        
        # 涨跌幅
        df['change_1d'] = df['close_price'].pct_change()
        df['change_3d'] = df['close_price'].pct_change(periods=3)
        df['change_5d'] = df['close_price'].pct_change(periods=5)
        
        return df

class AgentLearningSystem:
    """Agent学习系统"""
    
    def __init__(self):
        self.db_config = DB_CONFIG
        self.technical_calculator = TechnicalIndicators()
        self.models = {}
        
    def get_db_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(**self.db_config)
    
    def fetch_historical_data(self, symbol: str, days: int = 252) -> pd.DataFrame:
        """获取历史数据"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = """
        SELECT trade_date, open_price, high_price, low_price, close_price, 
               volume, amount, change_percent
        FROM daily_klines 
        WHERE symbol = %s AND trade_date BETWEEN %s AND %s
        ORDER BY trade_date
        """
        
        with self.get_db_connection() as conn:
            df = pd.read_sql(query, conn, params=(symbol, start_date, end_date))
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        # 计算技术指标
        df = self.technical_calculator.calculate_all_indicators(df)
        
        # 特征工程
        features = []
        
        # 价格特征
        features.extend([
            'close_price', 'open_price', 'high_price', 'low_price',
            'change_percent', 'price_position'
        ])
        
        # 均线特征
        features.extend(['ma5', 'ma10', 'ma20', 'ma60'])
        df['ma5_slope'] = df['ma5'].diff()
        df['ma10_slope'] = df['ma10'].diff()
        df['price_vs_ma5'] = df['close_price'] / df['ma5'] - 1
        df['price_vs_ma20'] = df['close_price'] / df['ma20'] - 1
        features.extend(['ma5_slope', 'ma10_slope', 'price_vs_ma5', 'price_vs_ma20'])
        
        # MACD特征
        features.extend(['macd_dif', 'macd_dea', 'macd_histogram'])
        df['macd_signal'] = np.where(df['macd_dif'] > df['macd_dea'], 1, 0)
        features.append('macd_signal')
        
        # RSI特征
        features.append('rsi')
        df['rsi_oversold'] = np.where(df['rsi'] < 30, 1, 0)
        df['rsi_overbought'] = np.where(df['rsi'] > 70, 1, 0)
        features.extend(['rsi_oversold', 'rsi_overbought'])
        
        # KDJ特征
        features.extend(['kdj_k', 'kdj_d', 'kdj_j'])
        
        # 成交量特征
        features.extend(['volume', 'volume_ratio'])
        df['volume_surge'] = np.where(df['volume_ratio'] > 2, 1, 0)
        features.append('volume_surge')
        
        # 波动率特征
        df['volatility_5d'] = df['change_percent'].rolling(5).std()
        df['volatility_20d'] = df['change_percent'].rolling(20).std()
        features.extend(['volatility_5d', 'volatility_20d'])
        
        return df[features].fillna(0)
    
    def create_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建标签数据"""
        labels = pd.DataFrame(index=df.index)
        
        # 未来收益率标签
        for days in [1, 3, 5, 10]:
            future_return = df['close_price'].shift(-days) / df['close_price'] - 1
            labels[f'return_{days}d'] = future_return
            
            # 分类标签
            labels[f'trend_{days}d'] = pd.cut(
                future_return, 
                bins=[-np.inf, -0.03, 0.03, np.inf], 
                labels=['DOWN', 'FLAT', 'UP']
            )
        
        return labels
    
    def train_models(self, symbol: str):
        """训练模型"""
        logger.info(f"开始训练 {symbol} 的模型...")
        
        # 获取历史数据
        df = self.fetch_historical_data(symbol, days=500)
        if len(df) < 100:
            logger.warning(f"{symbol} 历史数据不足，跳过训练")
            return
        
        # 准备特征和标签
        features_df = self.prepare_features(df)
        labels_df = self.create_labels(df)
        
        # 合并数据并去除缺失值
        data = pd.concat([features_df, labels_df], axis=1).dropna()
        
        if len(data) < 50:
            logger.warning(f"{symbol} 有效数据不足，跳过训练")
            return
        
        # 分离特征和标签
        feature_columns = features_df.columns
        X = data[feature_columns]
        
        # 训练多个预测模型
        models = {}
        
        # 1天趋势分类模型
        y_trend_1d = data['trend_1d']
        if len(y_trend_1d.dropna()) > 30:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_trend_1d, test_size=0.2, random_state=42
            )
            
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)
            
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            models['trend_1d'] = {
                'model': clf,
                'accuracy': accuracy,
                'feature_importance': dict(zip(feature_columns, clf.feature_importances_))
            }
            
            logger.info(f"{symbol} 1天趋势模型准确率: {accuracy:.3f}")
        
        # 3天收益率回归模型
        y_return_3d = data['return_3d']
        if len(y_return_3d.dropna()) > 30:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_return_3d, test_size=0.2, random_state=42
            )
            
            reg = RandomForestRegressor(n_estimators=100, random_state=42)
            reg.fit(X_train, y_train)
            
            score = reg.score(X_test, y_test)
            
            models['return_3d'] = {
                'model': reg,
                'r2_score': score,
                'feature_importance': dict(zip(feature_columns, reg.feature_importances_))
            }
            
            logger.info(f"{symbol} 3天收益率模型R²: {score:.3f}")
        
        # 保存模型
        self.models[symbol] = models
        
        # 保存到文件
        model_file = f"models/agent_model_{symbol}.joblib"
        joblib.dump(models, model_file)
        logger.info(f"{symbol} 模型已保存到 {model_file}")
    
    def predict(self, symbol: str, current_data: Dict) -> Dict:
        """使用模型进行预测"""
        if symbol not in self.models:
            # 尝试加载模型
            try:
                model_file = f"models/agent_model_{symbol}.joblib"
                self.models[symbol] = joblib.load(model_file)
            except:
                logger.warning(f"未找到 {symbol} 的训练模型")
                return {}
        
        models = self.models[symbol]
        predictions = {}
        
        # 准备特征数据
        features = self._prepare_prediction_features(current_data)
        
        # 趋势预测
        if 'trend_1d' in models:
            trend_pred = models['trend_1d']['model'].predict([features])[0]
            trend_proba = models['trend_1d']['model'].predict_proba([features])[0]
            
            predictions['trend_1d'] = {
                'prediction': trend_pred,
                'confidence': max(trend_proba),
                'probabilities': dict(zip(['DOWN', 'FLAT', 'UP'], trend_proba))
            }
        
        # 收益率预测
        if 'return_3d' in models:
            return_pred = models['return_3d']['model'].predict([features])[0]
            predictions['return_3d'] = {
                'prediction': return_pred,
                'confidence': models['return_3d']['r2_score']
            }
        
        return predictions
    
    def _prepare_prediction_features(self, data: Dict) -> List:
        """准备预测用的特征数据"""
        # 这里需要根据训练时的特征顺序来准备数据
        # 简化版本，实际需要完整的特征工程
        features = [
            data.get('close_price', 0),
            data.get('open_price', 0),
            data.get('high_price', 0),
            data.get('low_price', 0),
            data.get('change_percent', 0),
            data.get('volume', 0),
            # ... 其他特征
        ]
        return features
    
    def batch_train_all_stocks(self):
        """批量训练所有股票的模型"""
        query = "SELECT DISTINCT symbol FROM daily_klines WHERE trade_date >= %s"
        cutoff_date = datetime.now().date() - timedelta(days=30)
        
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (cutoff_date,))
                symbols = [row[0] for row in cur.fetchall()]
        
        logger.info(f"开始训练 {len(symbols)} 只股票的模型...")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"[{i}/{len(symbols)}] 训练 {symbol}")
                self.train_models(symbol)
            except Exception as e:
                logger.error(f"训练 {symbol} 失败: {e}")
        
        logger.info("批量训练完成！")

class EnhancedAgentSystem:
    """增强版Agent系统 - 集成实时数据和历史学习"""

    def __init__(self):
        self.learning_system = AgentLearningSystem()
        self.stock_data = {}

    def analyze_with_history(self, symbol: str, current_data: Dict) -> Dict:
        """基于历史数据学习的智能分析"""
        # 获取模型预测
        predictions = self.learning_system.predict(symbol, current_data)

        # 综合分析
        analysis = {
            'symbol': symbol,
            'current_price': current_data.get('price', 0),
            'change_percent': current_data.get('change_percent', 0),
            'timestamp': datetime.now().isoformat()
        }

        if predictions:
            # 趋势预测
            if 'trend_1d' in predictions:
                trend = predictions['trend_1d']
                analysis['trend_prediction'] = trend['prediction']
                analysis['trend_confidence'] = trend['confidence']

            # 收益率预测
            if 'return_3d' in predictions:
                ret = predictions['return_3d']
                analysis['expected_return_3d'] = ret['prediction']
                analysis['return_confidence'] = ret['confidence']

            # 生成交易建议
            analysis['recommendation'] = self._generate_recommendation(predictions, current_data)
        else:
            # 回退到基础分析
            analysis['recommendation'] = self._basic_analysis(current_data)

        return analysis

    def _generate_recommendation(self, predictions: Dict, current_data: Dict) -> Dict:
        """基于预测生成交易建议"""
        recommendation = {
            'action': 'HOLD',
            'confidence': 50,
            'reason': '数据不足'
        }

        if 'trend_1d' in predictions:
            trend = predictions['trend_1d']

            if trend['prediction'] == 'UP' and trend['confidence'] > 0.7:
                recommendation = {
                    'action': 'BUY',
                    'confidence': int(trend['confidence'] * 100),
                    'reason': f"模型预测上涨，置信度{trend['confidence']:.2f}"
                }
            elif trend['prediction'] == 'DOWN' and trend['confidence'] > 0.7:
                recommendation = {
                    'action': 'SELL',
                    'confidence': int(trend['confidence'] * 100),
                    'reason': f"模型预测下跌，置信度{trend['confidence']:.2f}"
                }

        return recommendation

    def _basic_analysis(self, current_data: Dict) -> Dict:
        """基础技术分析"""
        change_pct = current_data.get('change_percent', 0)

        if change_pct > 5:
            return {
                'action': 'BUY',
                'confidence': 70,
                'reason': f"强势上涨{change_pct:.2f}%"
            }
        elif change_pct < -5:
            return {
                'action': 'SELL',
                'confidence': 70,
                'reason': f"大幅下跌{change_pct:.2f}%"
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 60,
                'reason': '震荡整理'
            }

def main():
    """主函数"""
    print("🤖 Agent智能学习系统")
    print("=" * 50)

    learning_system = AgentLearningSystem()

    # 选择操作
    print("请选择操作:")
    print("1. 训练单个股票模型")
    print("2. 批量训练所有股票")
    print("3. 测试预测功能")

    choice = input("请输入选择 (1-3): ").strip()

    if choice == '1':
        symbol = input("请输入股票代码 (如 SH600519): ").strip()
        learning_system.train_models(symbol)

    elif choice == '2':
        confirm = input("批量训练需要较长时间，确认继续? (y/N): ").strip().lower()
        if confirm == 'y':
            learning_system.batch_train_all_stocks()
        else:
            print("已取消")

    elif choice == '3':
        symbol = input("请输入股票代码: ").strip()
        current_data = {
            'price': float(input("当前价格: ")),
            'change_percent': float(input("涨跌幅(%): ")),
            'volume': int(input("成交量: ") or "0")
        }

        enhanced_agent = EnhancedAgentSystem()
        analysis = enhanced_agent.analyze_with_history(symbol, current_data)

        print(f"\n📊 {symbol} 智能分析结果:")
        print(f"当前价格: ¥{analysis['current_price']:.2f}")
        print(f"涨跌幅: {analysis['change_percent']:+.2f}%")

        if 'trend_prediction' in analysis:
            print(f"趋势预测: {analysis['trend_prediction']}")
            print(f"预测置信度: {analysis['trend_confidence']:.2f}")

        if 'expected_return_3d' in analysis:
            print(f"3天预期收益: {analysis['expected_return_3d']:+.2f}%")

        rec = analysis['recommendation']
        print(f"\n🎯 交易建议: {rec['action']}")
        print(f"信心度: {rec['confidence']}%")
        print(f"理由: {rec['reason']}")

    else:
        print("无效选择")

if __name__ == "__main__":
    main()
