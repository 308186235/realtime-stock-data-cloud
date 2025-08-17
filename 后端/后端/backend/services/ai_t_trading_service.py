import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import os
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义交易环境类型
class TradingEnvironment:
    BACKTEST = "backtest"  # 回测环境
    LIVE = "live"          # 实盘环境

class AITTradingService:
    """
    AI服务用于交易决策和执行
    作为交易系统的中央组件,负责所有交易决策的生成和执行
    集成T交易和其他交易策略,提供统一的决策引擎
    """
    
    def __init__(self, model_dir="models/t_trading", environment=TradingEnvironment.LIVE):
        """
        初始化AI交易服务
        
        Args:
            model_dir (str): 模型存储目录
            environment (str): 交易环境,可选值:'backtest'或'live'
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # 设置交易环境
        self.environment = environment
        logger.info(f"AI交易服务初始化,环境:{self.environment}")
        
        # 模型
        self.opportunity_classifier = None  # 判断是否存在T交易机会的分类器
        self.mode_classifier = None  # 判断应该使用正T还是反T的分类器
        self.price_predictor = None  # 价格走势预测器
        self.quantity_optimizer = None  # 交易数量优化器
        
        # 特征标准化器
        self.feature_scaler = None
        
        # 模型训练参数
        self.min_training_samples = 100  # 训练所需的最小样本数
        self.retrain_interval = 7  # 重新训练的时间间隔(天)
        self.last_trained = None  # 上次训练时间
        
        # 系统状态
        self.auto_execute = False  # 是否自动执行交易决策
        self.max_trade_amount = 10000  # 单笔交易金额上限
        
        # 加载模型(如果存在)
        self._load_models()
        
        # 回测环境特定属性
        self.backtest_data = None
        self.backtest_trades = []
        self.backtest_performance = {
            'total_return': 0,
            'win_rate': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0
        }
        
        # 实盘环境特定属性
        self.risk_control_level = "medium"  # 风险控制级别:low, medium, high
        self.max_position_per_stock = 0.2   # 单只股票最大仓位比例
        self.daily_loss_limit = 0.02        # 日亏损限制比例
        self.position_sizing_method = "confidence"  # 仓位确定方法:fixed, confidence, kelly
        
        # 添加风险控制映射表
        self.risk_thresholds = {
            # 风险控制阈值映射表 - 不同风险级别对应不同的交易阈值
            "low": {
                "confidence_threshold": 0.75,        # 交易触发的最低置信度
                "volatility_limit": 0.03,           # 最大可接受波动率
                "position_factor": 0.5,             # 仓位系数(基础建议仓位的倍数)
                "profit_target_multiplier": 1.5,    # 止盈目标倍数
                "stop_loss_multiplier": 0.7,        # 止损距离倍数
                "volume_requirement": 1.2,          # 最低成交量比率要求
                "max_trades_per_day": 2,            # 每日最大交易次数
                "price_reversal_threshold": 0.02    # 价格反转阈值
            },
            "medium": {
                "confidence_threshold": 0.65,
                "volatility_limit": 0.05,
                "position_factor": 0.75,
                "profit_target_multiplier": 1.2,
                "stop_loss_multiplier": 0.8,
                "volume_requirement": 1.0,
                "max_trades_per_day": 5,
                "price_reversal_threshold": 0.015
            },
            "high": {
                "confidence_threshold": 0.55,
                "volatility_limit": 0.08,
                "position_factor": 1.0,
                "profit_target_multiplier": 1.0,
                "stop_loss_multiplier": 1.0,
                "volume_requirement": 0.8,
                "max_trades_per_day": 10,
                "price_reversal_threshold": 0.01
            }
        }
        
        # 风险参数学习数据
        self.risk_parameter_history = []    # 历史风险参数及其表现记录
        self.successful_trades_parameters = []  # 成功交易使用的风险参数记录
        self.risk_learning_enabled = True   # 是否启用风险参数学习
        
    def set_environment(self, environment):
        """
        设置交易环境
        
        Args:
            environment (str): 交易环境,可选值:TradingEnvironment.BACKTEST或TradingEnvironment.LIVE
            
        Returns:
            bool: 设置是否成功
        """
        if environment not in [TradingEnvironment.BACKTEST, TradingEnvironment.LIVE]:
            logger.error(f"无效的交易环境设置: {environment}")
            return False
            
        prev_env = self.environment
        self.environment = environment
        logger.info(f"交易环境已从 {prev_env} 切换到 {environment}")
        
        # 根据环境调整相关参数
        if environment == TradingEnvironment.BACKTEST:
            # 回测环境下,放宽交易限制,允许更频繁的交易
            self.max_trade_amount = 1000000  # 提高回测环境的单笔交易限额
            logger.info("切换到回测环境,已调整交易参数")
        else:
            # 实盘环境下,采用更保守的交易策略
            self.max_trade_amount = 10000   # 恢复实盘环境的单笔交易限额
            logger.info("切换到实盘环境,已恢复保守交易参数")
            
        return True
        
    def _load_models(self):
        """加载已保存的模型"""
        try:
            if os.path.exists(f"{self.model_dir}/opportunity_classifier.joblib"):
                self.opportunity_classifier = joblib.load(f"{self.model_dir}/opportunity_classifier.joblib")
                logger.info("成功加载T交易机会分类器")
                
            if os.path.exists(f"{self.model_dir}/mode_classifier.joblib"):
                self.mode_classifier = joblib.load(f"{self.model_dir}/mode_classifier.joblib")
                logger.info("成功加载T交易模式分类器")
                
            if os.path.exists(f"{self.model_dir}/price_predictor.joblib"):
                self.price_predictor = joblib.load(f"{self.model_dir}/price_predictor.joblib")
                logger.info("成功加载价格预测器")
                
            if os.path.exists(f"{self.model_dir}/quantity_optimizer.joblib"):
                self.quantity_optimizer = joblib.load(f"{self.model_dir}/quantity_optimizer.joblib")
                logger.info("成功加载数量优化器")
                
            if os.path.exists(f"{self.model_dir}/feature_scaler.joblib"):
                self.feature_scaler = joblib.load(f"{self.model_dir}/feature_scaler.joblib")
                logger.info("成功加载特征标准化器")
                
            # 读取上次训练时间
            if os.path.exists(f"{self.model_dir}/last_trained.txt"):
                with open(f"{self.model_dir}/last_trained.txt", "r") as f:
                    self.last_trained = datetime.strptime(f.read().strip(), "%Y-%m-%d")
                    
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            
    def _save_models(self):
        """保存模型到磁盘"""
        try:
            if self.opportunity_classifier:
                joblib.dump(self.opportunity_classifier, f"{self.model_dir}/opportunity_classifier.joblib")
                
            if self.mode_classifier:
                joblib.dump(self.mode_classifier, f"{self.model_dir}/mode_classifier.joblib")
                
            if self.price_predictor:
                joblib.dump(self.price_predictor, f"{self.model_dir}/price_predictor.joblib")
                
            if self.quantity_optimizer:
                joblib.dump(self.quantity_optimizer, f"{self.model_dir}/quantity_optimizer.joblib")
                
            if self.feature_scaler:
                joblib.dump(self.feature_scaler, f"{self.model_dir}/feature_scaler.joblib")
                
            # 保存训练时间
            with open(f"{self.model_dir}/last_trained.txt", "w") as f:
                f.write(datetime.now().strftime("%Y-%m-%d"))
                
            self.last_trained = datetime.now()
            logger.info(f"模型已保存到 {self.model_dir}")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    def _extract_features(self, market_data):
        """
        从市场数据中提取特征
        
        Args:
            market_data (pd.DataFrame): 市场数据
            
        Returns:
            np.array: 特征数组
        """
        # 基本价格特征
        price_features = np.array([
            market_data['current_price'],
            market_data['open_price'],
            market_data['intraday_high'],
            market_data['intraday_low'],
            market_data['current_price'] / market_data['open_price'] - 1,  # 相对开盘价涨跌幅
            market_data['current_price'] / market_data['intraday_high'] - 1,  # 相对高点回落幅度
            market_data['current_price'] / market_data['intraday_low'] - 1,  # 相对低点涨幅
            (market_data['intraday_high'] - market_data['intraday_low']) / market_data['open_price'],  # 日内波动率
            (market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5,  # 价格位置
        ]).reshape(1, -1)
        
        # 成交量特征
        volume_features = np.array([
            market_data['current_volume'],
            market_data['current_volume'] / market_data['avg_volume'] if market_data['avg_volume'] > 0 else 1.0,  # 相对成交量
        ]).reshape(1, -1)
        
        # 合并特征
        features = np.hstack([price_features, volume_features])
        
        # 使用标准化器(如果已训练)
        if self.feature_scaler:
            features = self.feature_scaler.transform(features)
        
        return features
    
    async def train_models(self, historical_data, trade_results):
        """
        训练AI模型
        
        Args:
            historical_data (List[Dict]): 历史市场数据
            trade_results (List[Dict]): 历史T交易结果
            
        Returns:
            bool: 训练是否成功
        """
        if len(historical_data) < self.min_training_samples:
            logger.warning(f"训练数据不足,需要至少 {self.min_training_samples} 条数据")
            return False
            
        # 检查是否需要重新训练
        if self.last_trained and (datetime.now() - self.last_trained).days < self.retrain_interval:
            logger.info(f"模型最近已训练,{self.retrain_interval}天后再训练")
            return False
            
        logger.info(f"开始训练T交易AI模型,数据量: {len(historical_data)}")
        
        try:
            # 准备数据集
            df = pd.DataFrame(historical_data)
            
            # 标记成功的交易结果
            successful_trades = set((t['date'], t['stock_code']) for t in trade_results if t['status'] == 'success')
            
            # 创建标签
            df['has_opportunity'] = df.apply(lambda row: 1 if (row['date'], row['stock_code']) in successful_trades else 0, axis=1)
            
            # 提取特征
            features = []
            for _, row in df.iterrows():
                # 将行数据转换为字典
                market_data = row.to_dict()
                # 处理可能的NaN值
                for k, v in market_data.items():
                    if pd.isna(v):
                        market_data[k] = 0
                
                feature = np.array([
                    market_data['current_price'],
                    market_data['open_price'],
                    market_data['intraday_high'],
                    market_data['intraday_low'],
                    market_data['current_price'] / market_data['open_price'] - 1,
                    market_data['current_price'] / market_data['intraday_high'] - 1,
                    market_data['current_price'] / market_data['intraday_low'] - 1,
                    (market_data['intraday_high'] - market_data['intraday_low']) / market_data['open_price'],
                    (market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5,
                    market_data['current_volume'],
                    market_data['current_volume'] / market_data['avg_volume'] if market_data['avg_volume'] > 0 else 1.0,
                ])
                features.append(feature)
                
            X = np.array(features)
            y_opportunity = df['has_opportunity'].values
            
            # 创建交易模式标签(1: 正T, 0: 反T)
            df_successful = df[df['has_opportunity'] == 1]
            successful_modes = {(t['date'], t['stock_code']): 1 if t['mode'] == 'positive' else 0 
                              for t in trade_results if t['status'] == 'success'}
            
            df_successful['mode'] = df_successful.apply(
                lambda row: successful_modes.get((row['date'], row['stock_code']), 1), axis=1)
            
            # 模型训练数据集划分
            X_train, X_test, y_opp_train, y_opp_test = train_test_split(X, y_opportunity, test_size=0.2, random_state=42)
            
            # 标准化特征
            self.feature_scaler = StandardScaler()
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)
            
            # 训练机会分类器
            self.opportunity_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.opportunity_classifier.fit(X_train_scaled, y_opp_train)
            
            # 评估机会分类器
            y_opp_pred = self.opportunity_classifier.predict(X_test_scaled)
            opp_accuracy = accuracy_score(y_opp_test, y_opp_pred)
            logger.info(f"T交易机会分类器准确率: {opp_accuracy:.4f}")
            
            # 如果成功样本充足,训练模式分类器
            if df_successful.shape[0] > 20:
                X_mode = X[df['has_opportunity'] == 1]
                y_mode = df_successful['mode'].values
                
                if len(np.unique(y_mode)) > 1:  # 确保有正T和反T两种模式
                    X_mode_train, X_mode_test, y_mode_train, y_mode_test = train_test_split(
                        X_mode, y_mode, test_size=0.2, random_state=42)
                    
                    # 标准化
                    X_mode_train_scaled = self.feature_scaler.transform(X_mode_train)
                    X_mode_test_scaled = self.feature_scaler.transform(X_mode_test)
                    
                    # 训练模式分类器
                    self.mode_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
                    self.mode_classifier.fit(X_mode_train_scaled, y_mode_train)
                    
                    # 评估模式分类器
                    y_mode_pred = self.mode_classifier.predict(X_mode_test_scaled)
                    mode_accuracy = accuracy_score(y_mode_test, y_mode_pred)
                    logger.info(f"T交易模式分类器准确率: {mode_accuracy:.4f}")
            
            # 训练价格预测器(预测未来价格走势)
            if 'future_price' in df.columns:
                y_price = df['future_price'].values
                
                # 训练价格预测模型
                self.price_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
                self.price_predictor.fit(X_train_scaled, y_price[df.index.isin(y_opp_train.index)])
                
                # 评估价格预测模型
                y_price_pred = self.price_predictor.predict(X_test_scaled)
                price_mse = mean_squared_error(y_price[df.index.isin(y_opp_test.index)], y_price_pred)
                logger.info(f"价格预测器均方误差: {price_mse:.4f}")
            
            # 训练交易数量优化器
            if 'optimal_quantity' in df.columns:
                y_quantity = df['optimal_quantity'].values
                
                # 训练数量优化模型
                self.quantity_optimizer = GradientBoostingRegressor(n_estimators=100, random_state=42)
                self.quantity_optimizer.fit(X_train_scaled, y_quantity[df.index.isin(y_opp_train.index)])
                
                # 评估数量优化模型
                y_quantity_pred = self.quantity_optimizer.predict(X_test_scaled)
                quantity_mse = mean_squared_error(y_quantity[df.index.isin(y_opp_test.index)], y_quantity_pred)
                logger.info(f"数量优化器均方误差: {quantity_mse:.4f}")
            
            # 保存模型
            self._save_models()
            return True
            
        except Exception as e:
            logger.error(f"训练模型失败: {e}")
            return False
    
    async def evaluate_opportunity(self, market_data):
        """
        评估是否存在T交易机会
        
        Args:
            market_data (dict): 市场数据
            
        Returns:
            dict: 评估结果
        """
        if not self.opportunity_classifier:
            logger.warning("机会分类器未训练,使用规则引擎评估")
            return self._rule_based_evaluation(market_data)
        
        try:
            # 提取特征
            features = self._extract_features(market_data)
            
            # 预测是否有交易机会
            has_opportunity = bool(self.opportunity_classifier.predict(features)[0])
            
            if not has_opportunity:
                return {
                    'has_opportunity': False,
                    'message': 'AI分析:当前不适合进行T交易',
                    'ai_confidence': float(self.opportunity_classifier.predict_proba(features)[0][0]),
                    'evaluation_method': 'ai'
                }
                
            # 预测交易模式(正T或反T)
            if self.mode_classifier:
                mode_prediction = self.mode_classifier.predict(features)[0]
                mode = 'positive' if mode_prediction == 1 else 'negative'
                mode_confidence = float(self.mode_classifier.predict_proba(features)[0][mode_prediction])
            else:
                # 没有模式分类器时使用规则
                price_position = (market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5
                mode = 'positive' if price_position < 0.4 else 'negative'
                mode_confidence = 0.7
            
            # 计算推荐交易数量
            if self.quantity_optimizer:
                suggested_quantity = int(self.quantity_optimizer.predict(features)[0])
                # 确保数量合理
                max_quantity = int(market_data['base_position'] * 0.3)  # 最多使用30%的底仓
                suggested_quantity = min(max_quantity, max(100, suggested_quantity))
            else:
                # 默认使用20%底仓
                suggested_quantity = int(market_data['base_position'] * 0.2)
            
            # 预测价格走势
            price_trend = None
            if self.price_predictor:
                future_price = self.price_predictor.predict(features)[0]
                current_price = market_data['current_price']
                price_change = (future_price / current_price - 1) * 100
                price_trend = {
                    'predicted_price': float(future_price),
                    'predicted_change': float(price_change),
                    'direction': 'up' if price_change > 0 else 'down'
                }
            
            # 构建结果
            result = {
                'has_opportunity': True,
                'mode': mode,
                'message': f'AI推荐:适合进行{"正T(先买后卖)" if mode == "positive" else "反T(先卖后买)"}',
                'suggested_quantity': suggested_quantity,
                'ai_confidence': float(mode_confidence),
                'evaluation_method': 'ai',
                'volatility': float((market_data['intraday_high'] - market_data['intraday_low']) / market_data['open_price']),
                'current_position': float((market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5)
            }
            
            if price_trend:
                result['price_trend'] = price_trend
                
            # 计算预期成本影响
            if mode == 'positive':
                # 正T:假设以当前价买入,未来以predicted_price卖出
                if price_trend:
                    buy_price = market_data['current_price']
                    sell_price = price_trend['predicted_price']
                    expected_profit = (sell_price - buy_price) * suggested_quantity
                    
                    result['expected_profit'] = float(expected_profit)
                    
                    # 计算对持仓成本的影响
                    original_cost = market_data['base_cost']
                    new_cost = (original_cost * market_data['base_position'] - expected_profit) / market_data['base_position']
                    
                    result['expected_cost_impact'] = {
                        'original_cost': float(original_cost),
                        'new_cost': float(new_cost),
                        'cost_reduction': float(original_cost - new_cost),
                        'reduction_percentage': float((original_cost - new_cost) / original_cost * 100)
                    }
            else:
                # 反T:假设以当前价卖出,未来以predicted_price买入
                if price_trend:
                    sell_price = market_data['current_price']
                    buy_price = price_trend['predicted_price']
                    expected_profit = (sell_price - buy_price) * suggested_quantity
                    
                    result['expected_profit'] = float(expected_profit)
                    
                    # 计算对持仓成本的影响
                    original_cost = market_data['base_cost']
                    new_cost = (original_cost * market_data['base_position'] - expected_profit) / market_data['base_position']
                    
                    result['expected_cost_impact'] = {
                        'original_cost': float(original_cost),
                        'new_cost': float(new_cost),
                        'cost_reduction': float(original_cost - new_cost),
                        'reduction_percentage': float((original_cost - new_cost) / original_cost * 100)
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"AI评估T交易机会失败: {e}")
            # 出错时回退到规则引擎
            return self._rule_based_evaluation(market_data)
    
    def _rule_based_evaluation(self, market_data):
        """
        使用规则引擎评估T交易机会(当AI模型不可用时的备选方案)
        
        Args:
            market_data (dict): 市场数据
            
        Returns:
            dict: 评估结果
        """
        # 计算日内波动率和价格位置
        intraday_volatility = (market_data['intraday_high'] - market_data['intraday_low']) / market_data['open_price']
        
        current_position = (market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5
        
        # 计算成交量活跃度
        volume_activity = market_data['current_volume'] / market_data['avg_volume'] if market_data['avg_volume'] > 0 else 1.0
        
        # 检查是否有足够的底仓
        if market_data['base_position'] <= 0:
            return {
                'has_opportunity': False,
                'message': '无底仓,不可进行T交易',
                'evaluation_method': 'rule'
            }
            
        # 波动率太小不适合做T
        if intraday_volatility < 0.01:
            return {
                'has_opportunity': False,
                'message': '日内波动太小,不适合做T',
                'volatility': float(intraday_volatility),
                'evaluation_method': 'rule'
            }
            
        # 正T机会:当前价格接近日内低点,且成交量放大
        if current_position < 0.3 and volume_activity > 1.2:
            suggested_quantity = int(market_data['base_position'] * 0.2)
            
            # 计算预期成本影响(假设0.5%的获利空间)
            expected_profit_rate = 0.005
            expected_profit = suggested_quantity * market_data['current_price'] * expected_profit_rate
            
            original_cost = market_data['base_cost']
            new_cost = (original_cost * market_data['base_position'] - expected_profit) / market_data['base_position']
            
            return {
                'has_opportunity': True,
                'mode': 'positive',
                'message': '接近日内低点,可考虑正T(先买)',
                'suggested_quantity': suggested_quantity,
                'volatility': float(intraday_volatility),
                'current_position': float(current_position),
                'evaluation_method': 'rule',
                'expected_cost_impact': {
                    'original_cost': float(original_cost),
                    'new_cost': float(new_cost),
                    'cost_reduction': float(original_cost - new_cost),
                    'reduction_percentage': float((original_cost - new_cost) / original_cost * 100)
                }
            }
            
        # 反T机会:当前价格接近日内高点,且有一定上涨幅度
        if current_position > 0.7 and (market_data['current_price'] / market_data['open_price']) > 1.01:
            suggested_quantity = int(market_data['base_position'] * 0.2)
            
            # 计算预期成本影响(假设0.5%的获利空间)
            expected_profit_rate = 0.005
            expected_profit = suggested_quantity * market_data['current_price'] * expected_profit_rate
            
            original_cost = market_data['base_cost']
            new_cost = (original_cost * market_data['base_position'] - expected_profit) / market_data['base_position']
            
            return {
                'has_opportunity': True,
                'mode': 'negative',
                'message': '接近日内高点,可考虑反T(先卖)',
                'suggested_quantity': suggested_quantity,
                'volatility': float(intraday_volatility),
                'current_position': float(current_position),
                'evaluation_method': 'rule',
                'expected_cost_impact': {
                    'original_cost': float(original_cost),
                    'new_cost': float(new_cost),
                    'cost_reduction': float(original_cost - new_cost),
                    'reduction_percentage': float((original_cost - new_cost) / original_cost * 100)
                }
            }
            
        # 无明确机会
        return {
            'has_opportunity': False,
            'message': '当前没有明确的T交易机会',
            'volatility': float(intraday_volatility),
            'current_position': float(current_position),
            'evaluation_method': 'rule'
        }
        
    async def recommend_trade_action(self, stock_info, historical_prices=None):
        """
        推荐交易行动
        
        Args:
            stock_info (dict): 股票信息
            historical_prices (pd.DataFrame, optional): 历史价格数据
            
        Returns:
            dict: 推荐的交易行动
        """
        # 根据环境调整决策行为
        if self.environment == TradingEnvironment.BACKTEST:
            # 回测环境下,可以使用完整的历史数据进行决策
            return await self._backtest_recommend_action(stock_info, historical_prices)
        else:
            # 实盘环境下,需要更加谨慎,加强风险控制
            return await self._live_recommend_action(stock_info, historical_prices)
    
    async def _backtest_recommend_action(self, stock_info, historical_prices):
        """回测环境下的交易推荐,可以使用完整历史数据"""
        # 评估交易机会
        market_data = {
            'current_price': stock_info['current_price'],
            'open_price': stock_info['open_price'],
            'intraday_high': stock_info['intraday_high'],
            'intraday_low': stock_info['intraday_low'],
            'avg_volume': stock_info['avg_volume'],
            'current_volume': stock_info['current_volume'],
            'base_position': stock_info['base_position'],
            'base_cost': stock_info['base_cost']
        }
        
        opportunity = await self.evaluate_opportunity(market_data)
        
        # 在回测模式下,我们可以更激进地交易,降低机会阈值
        if not opportunity['has_opportunity']:
            # 重新检查,使用更宽松的标准
            if opportunity.get('evaluation_method') == 'ai' and opportunity.get('ai_confidence', 0) > 0.4:
                # 在回测中,较低置信度也可以尝试
                return {
                    'action': 'buy' if opportunity.get('current_position', 0.5) < 0.4 else 'sell',
                    'price': market_data['current_price'],
                    'quantity': int(market_data['base_position'] * 0.1),  # 使用较小仓位测试策略
                    'message': "回测环境:低置信度交易测试",
                    'confidence': opportunity.get('ai_confidence', 0.4),
                    'opportunity': opportunity,
                    'environment': 'backtest'
                }
            return {
                'action': 'hold',
                'message': opportunity['message'],
                'opportunity': opportunity,
                'environment': 'backtest'
            }
            
        # 根据交易模式推荐操作
        if opportunity['mode'] == 'positive':
            return {
                'action': 'buy',
                'price': market_data['current_price'],
                'quantity': opportunity['suggested_quantity'],
                'message': f"回测推荐:正T买入 {opportunity['suggested_quantity']}股 @ ¥{market_data['current_price']:.2f}",
                'reason': opportunity['message'],
                'confidence': opportunity.get('ai_confidence', 0.7),
                'opportunity': opportunity,
                'environment': 'backtest'
            }
        else:
            return {
                'action': 'sell',
                'price': market_data['current_price'],
                'quantity': opportunity['suggested_quantity'],
                'message': f"回测推荐:反T卖出 {opportunity['suggested_quantity']}股 @ ¥{market_data['current_price']:.2f}",
                'reason': opportunity['message'],
                'confidence': opportunity.get('ai_confidence', 0.7),
                'opportunity': opportunity,
                'environment': 'backtest'
            }
    
    async def _live_recommend_action(self, stock_info, historical_prices):
        """实盘环境下的交易推荐,更注重风险控制"""
        market_data = {
            'current_price': stock_info['current_price'],
            'open_price': stock_info['open_price'],
            'intraday_high': stock_info['intraday_high'],
            'intraday_low': stock_info['intraday_low'],
            'avg_volume': stock_info['avg_volume'],
            'current_volume': stock_info['current_volume'],
            'base_position': stock_info['base_position'],
            'base_cost': stock_info['base_cost']
        }
        
        # 使用统一AI决策模型,整合多维度分析
        decision = await self.unified_decision_model(market_data, historical_prices)
        
        # 实盘环境下,对决策进行额外的风险评估
        risk_assessment = self._assess_trade_risk(decision, stock_info)
        
        # 根据风险评估调整决策
        if risk_assessment['risk_level'] == 'high':
            logger.warning(f"实盘高风险交易被拒绝: {risk_assessment['reason']}")
            return {
                'action': 'hold',
                'message': f"风险过高,不推荐交易: {risk_assessment['reason']}",
                'risk_assessment': risk_assessment,
                'original_decision': decision,
                'environment': 'live'
            }
        
        # 调整仓位大小,实盘环境下更保守
        if decision['action'] != 'hold':
            # 根据风险评估调整数量
            adjusted_quantity = self._adjust_position_size(
                decision.get('suggested_quantity', 0),
                decision.get('confidence', 0.5),
                risk_assessment
            )
            
            decision['suggested_quantity'] = adjusted_quantity
            decision['message'] = f"实盘{'买入' if decision['action']=='buy' else '卖出'} {adjusted_quantity}股 @ ¥{market_data['current_price']:.2f} (风险:{risk_assessment['risk_level']})"
            decision['environment'] = 'live'
            decision['risk_assessment'] = risk_assessment
        
        return decision
    
    def _assess_trade_risk(self, decision, stock_info):
        """
        评估交易风险
        
        Args:
            decision (dict): 交易决策
            stock_info (dict): 股票信息
            
        Returns:
            dict: 风险评估结果
        """
        # 获取当前风险级别的阈值配置
        risk_thresholds = self.risk_thresholds[self.risk_control_level]
        
        risk_assessment = {
            'risk_level': 'low',  # 默认风险级别:low, medium, high
            'risk_factors': [],
            'reason': '',
            'thresholds_used': risk_thresholds  # 记录使用的阈值,用于后续学习
        }
        
        # 检查市场波动性
        market_volatility = stock_info.get('volatility', 0)
        if market_volatility > risk_thresholds["volatility_limit"]:
            risk_assessment['risk_level'] = 'high'
            risk_assessment['risk_factors'].append({
                'factor': 'high_volatility',
                'value': market_volatility,
                'threshold': risk_thresholds["volatility_limit"]
            })
            risk_assessment['reason'] = '市场波动性过高'
            
        # 检查交易量
        volume_ratio = stock_info.get('current_volume', 0) / stock_info.get('avg_volume', 1) if stock_info.get('avg_volume', 0) > 0 else 1
        if volume_ratio < risk_thresholds["volume_requirement"]:
            if risk_assessment['risk_level'] != 'high':
                risk_assessment['risk_level'] = 'medium'
            risk_assessment['risk_factors'].append({
                'factor': 'low_volume',
                'value': volume_ratio,
                'threshold': risk_thresholds["volume_requirement"]
            })
            risk_assessment['reason'] += '成交量不足 '
            
        # 检查决策置信度
        if decision.get('confidence', 0) < risk_thresholds["confidence_threshold"]:
            if risk_assessment['risk_level'] != 'high':
                risk_assessment['risk_level'] = 'medium'
            risk_assessment['risk_factors'].append({
                'factor': 'low_confidence',
                'value': decision.get('confidence', 0),
                'threshold': risk_thresholds["confidence_threshold"]
            })
            risk_assessment['reason'] += '决策置信度不足 '
            
        # 检查风险收益比
        if decision.get('risk_reward') and decision['risk_reward'].get('risk_reward_ratio', 0) < risk_thresholds["profit_target_multiplier"]:
            if risk_assessment['risk_level'] != 'high':
                risk_assessment['risk_level'] = 'medium'
            risk_assessment['risk_factors'].append({
                'factor': 'poor_risk_reward',
                'value': decision['risk_reward'].get('risk_reward_ratio', 0),
                'threshold': risk_thresholds["profit_target_multiplier"]
            })
            risk_assessment['reason'] += '风险收益比不佳 '
            
        # 检查价格是否处于极端位置
        price_position = (stock_info.get('current_price', 0) - stock_info.get('intraday_low', 0)) / (stock_info.get('intraday_high', 0) - stock_info.get('intraday_low', 0)) if (stock_info.get('intraday_high', 0) - stock_info.get('intraday_low', 0)) > 0 else 0.5
        if (decision.get('action') == 'buy' and price_position > 0.8) or (decision.get('action') == 'sell' and price_position < 0.2):
            risk_assessment['risk_factors'].append({
                'factor': 'extreme_price_position',
                'value': price_position,
                'threshold': 0.8 if decision.get('action') == 'buy' else 0.2
            })
            risk_assessment['reason'] += '价格位置极端 '
            
        # 如果没有具体风险因素,设置默认原因
        if not risk_assessment['reason']:
            risk_assessment['reason'] = '正常风险水平'
            
        # 记录风险评估参数,用于学习优化
        self._record_risk_assessment(risk_assessment, decision)
            
        return risk_assessment
    
    def _adjust_position_size(self, suggested_quantity, confidence, risk_assessment):
        """
        根据风险评估调整仓位大小
        
        Args:
            suggested_quantity (int): 建议的交易数量
            confidence (float): 决策置信度
            risk_assessment (dict): 风险评估结果
            
        Returns:
            int: 调整后的交易数量
        """
        # 获取风险级别对应的阈值配置
        risk_thresholds = self.risk_thresholds[self.risk_control_level]
        
        # 基础调整系数,使用风险级别对应的仓位系数
        adjustment_factor = risk_thresholds["position_factor"]
        
        # 根据风险级别调整
        if risk_assessment['risk_level'] == 'high':
            adjustment_factor *= 0.5  # 高风险减半
        elif risk_assessment['risk_level'] == 'medium':
            adjustment_factor *= 0.75  # 中等风险减少25%
            
        # 根据置信度调整
        confidence_threshold = risk_thresholds["confidence_threshold"]
        if confidence < confidence_threshold + 0.05:  # 略高于阈值
            # 低置信度时更加保守
            confidence_factor = (confidence - confidence_threshold) / 0.05
            confidence_factor = max(0.1, min(1.0, confidence_factor))
            adjustment_factor *= confidence_factor
            
        # 根据仓位确定方法调整
        if self.position_sizing_method == "confidence":
            # 根据置信度确定仓位
            adjustment_factor *= confidence
        elif self.position_sizing_method == "kelly":
            # 使用简化的kelly公式计算仓位
            # f* = (bp - q) / b = (edge×odds - 1) / odds
            # 其中p为胜率(使用confidence), q=1-p, b为赔率(假设为1)
            kelly_fraction = max(0, 2 * confidence - 1)
            adjustment_factor *= kelly_fraction
        elif self.position_sizing_method == "adaptive":
            # 自适应仓位,根据历史绩效动态调整
            historical_success_rate = self._get_historical_success_rate()
            if historical_success_rate:  # 如果有历史数据
                adjustment_factor *= (0.5 + historical_success_rate * 0.5)
            
        # 应用单只股票最大仓位限制
        max_quantity_by_position_limit = int(stock_info.get('base_position', 0) * self.max_position_per_stock)
        suggested_quantity = min(suggested_quantity, max_quantity_by_position_limit)
        
        # 确保最小交易单位,四舍五入到100股的倍数
        adjusted_quantity = max(100, round(suggested_quantity * adjustment_factor / 100) * 100)
        
        return adjusted_quantity
    
    def _record_risk_assessment(self, risk_assessment, decision):
        """
        记录风险评估参数,用于学习优化
        
        Args:
            risk_assessment (dict): 风险评估结果
            decision (dict): 交易决策
        """
        if not self.risk_learning_enabled:
            return
            
        # 记录评估数据
        assessment_record = {
            'timestamp': datetime.now().isoformat(),
            'risk_level': self.risk_control_level,
            'thresholds_used': risk_assessment.get('thresholds_used', {}),
            'decision_confidence': decision.get('confidence', 0),
            'action': decision.get('action', 'hold'),
            'risk_assessment_result': risk_assessment.get('risk_level', 'low'),
            'risk_factors': risk_assessment.get('risk_factors', []),
            'position_sizing_method': self.position_sizing_method,
            'trade_id': f"trade_{len(self.risk_parameter_history)}",
            'trade_result': None  # 将在交易完成后更新
        }
        
        self.risk_parameter_history.append(assessment_record)
        
        # 限制历史记录数量,防止内存占用过多
        if len(self.risk_parameter_history) > 1000:
            self.risk_parameter_history = self.risk_parameter_history[-1000:]
    
    def record_trade_result(self, trade_id, result, profit_loss=0):
        """
        记录交易结果,用于风险参数学习
        
        Args:
            trade_id (str): 交易ID
            result (str): 交易结果,'success', 'failure', 'neutral'
            profit_loss (float): 盈亏金额
            
        Returns:
            bool: 是否成功记录
        """
        if not self.risk_learning_enabled:
            return False
            
        # 查找对应的风险评估记录
        for record in self.risk_parameter_history:
            if record['trade_id'] == trade_id:
                record['trade_result'] = result
                record['profit_loss'] = profit_loss
                
                # 如果交易成功,加入成功记录集合
                if result == 'success':
                    self.successful_trades_parameters.append(record)
                    
                    # 定期优化风险参数
                    if len(self.successful_trades_parameters) % 10 == 0:
                        self._optimize_risk_parameters()
                        
                return True
                
        return False
    
    def _get_historical_success_rate(self):
        """
        获取历史交易成功率
        
        Returns:
            float: 成功率,如果没有足够数据则返回None
        """
        # 获取有结果的交易记录
        completed_trades = [record for record in self.risk_parameter_history 
                          if record['trade_result'] is not None]
                          
        if len(completed_trades) < 5:  # 至少需要5笔交易才有意义
            return None
            
        successful_trades = [trade for trade in completed_trades 
                           if trade['trade_result'] == 'success']
                           
        return len(successful_trades) / len(completed_trades)
    
    def _optimize_risk_parameters(self):
        """
        根据历史表现优化风险参数
        """
        if not self.risk_learning_enabled or len(self.successful_trades_parameters) < 10:
            return
            
        logger.info("开始优化风险控制参数...")
        
        # 分析成功交易的风险参数
        confidence_values = [trade['decision_confidence'] for trade in self.successful_trades_parameters]
        position_methods = [trade['position_sizing_method'] for trade in self.successful_trades_parameters]
        risk_levels = [trade['risk_level'] for trade in self.successful_trades_parameters]
        
        # 计算平均值和分布
        avg_confidence = sum(confidence_values) / len(confidence_values)
        most_common_method = max(set(position_methods), key=position_methods.count)
        most_common_risk_level = max(set(risk_levels), key=risk_levels.count)
        
        # 根据历史表现调整风险参数
        # 这里使用简单的调整策略,实际应用中可以使用更复杂的机器学习方法
        
        # 调整置信度阈值 - 向历史成功交易的平均置信度靠拢
        for level in self.risk_thresholds:
            current_threshold = self.risk_thresholds[level]['confidence_threshold']
            # 每次微调,避免过度调整
            if avg_confidence > current_threshold:
                # 如果成功交易的平均置信度高于当前阈值,稍微提高阈值
                self.risk_thresholds[level]['confidence_threshold'] = min(
                    0.9,  # 最高不超过0.9
                    current_threshold + 0.01  # 每次增加0.01
                )
            elif avg_confidence < current_threshold - 0.1:  # 给一些余量
                # 如果成功交易的平均置信度明显低于当前阈值,稍微降低阈值
                self.risk_thresholds[level]['confidence_threshold'] = max(
                    0.5,  # 最低不低于0.5
                    current_threshold - 0.01  # 每次减少0.01
                )
        
        # 调整仓位策略 - 如果某种策略效果更好,增加其权重
        if most_common_method != self.position_sizing_method:
            logger.info(f"发现更有效的仓位确定方法: {most_common_method}, 当前方法: {self.position_sizing_method}")
            # 不立即切换,但记录这一发现
            # 在实际应用中,可以逐渐增加新方法的使用频率
        
        logger.info(f"风险参数优化完成。当前使用: {self.risk_control_level}级别, 置信度阈值: {self.risk_thresholds[self.risk_control_level]['confidence_threshold']}")
    
    def get_risk_parameter_stats(self):
        """
        获取风险参数统计和学习情况
        
        Returns:
            dict: 风险参数统计数据
        """
        if not self.risk_learning_enabled:
            return {
                "learning_enabled": False,
                "message": "风险参数学习功能未启用"
            }
            
        # 计算成功率统计
        success_rate = self._get_historical_success_rate()
        
        # 获取当前风险参数
        current_thresholds = self.risk_thresholds[self.risk_control_level]
        
        # 构建统计结果
        return {
            "learning_enabled": True,
            "records_count": len(self.risk_parameter_history),
            "successful_trades_count": len(self.successful_trades_parameters),
            "overall_success_rate": success_rate,
            "current_risk_level": self.risk_control_level,
            "current_thresholds": current_thresholds,
            "historical_thresholds": [
                record['thresholds_used'] for record in self.risk_parameter_history[-5:]
            ] if len(self.risk_parameter_history) > 0 else [],
            "position_sizing_method": self.position_sizing_method,
            "last_optimization_time": datetime.now().isoformat()
        }
    
    def configure_risk_control(self, risk_level="medium", max_position_per_stock=0.2, 
                             daily_loss_limit=0.02, position_sizing_method="confidence",
                             enable_learning=True):
        """
        配置实盘环境下的风险控制参数
        
        Args:
            risk_level (str): 风险控制级别,可选值:'low', 'medium', 'high'
            max_position_per_stock (float): 单只股票最大仓位比例
            daily_loss_limit (float): 日亏损限制比例
            position_sizing_method (str): 仓位确定方法,可选值:'fixed', 'confidence', 'kelly', 'adaptive'
            enable_learning (bool): 是否启用风险参数学习
            
        Returns:
            dict: 更新结果
        """
        try:
            # 验证参数
            if risk_level not in ['low', 'medium', 'high']:
                return {"success": False, "message": "无效的风险级别"}
                
            if not (0 < max_position_per_stock <= 1):
                return {"success": False, "message": "单只股票最大仓位比例必须在0-1之间"}
                
            if not (0 < daily_loss_limit <= 0.1):
                return {"success": False, "message": "日亏损限制比例必须在0-0.1之间"}
                
            valid_position_methods = ['fixed', 'confidence', 'kelly', 'adaptive']
            if position_sizing_method not in valid_position_methods:
                return {"success": False, "message": f"无效的仓位确定方法, 有效值: {', '.join(valid_position_methods)}"}
                
            # 更新风险控制参数
            self.risk_control_level = risk_level
            self.max_position_per_stock = max_position_per_stock
            self.daily_loss_limit = daily_loss_limit
            self.position_sizing_method = position_sizing_method
            self.risk_learning_enabled = enable_learning
            
            # 根据风险级别调整其他参数
            if risk_level == 'low':
                # 低风险:更保守的设置
                self.max_position_per_stock = min(0.15, max_position_per_stock)
                self.daily_loss_limit = min(0.01, daily_loss_limit)
            elif risk_level == 'high':
                # 高风险:更激进的设置
                self.max_position_per_stock = max(0.25, max_position_per_stock)
                self.daily_loss_limit = max(0.03, daily_loss_limit)
                
            logger.info(f"风险控制参数已更新: 级别={risk_level}, 单股最大仓位={self.max_position_per_stock}, " +
                      f"日亏损限制={self.daily_loss_limit}, 仓位方法={position_sizing_method}, " +
                      f"参数学习={enable_learning}")
                      
            # 如果启用学习但当前没有参数历史,则初始化
            if enable_learning and not self.risk_parameter_history:
                self.risk_parameter_history = []
                logger.info("已初始化风险参数历史记录")
                      
            return {
                "success": True,
                "message": "风险控制参数已更新",
                "settings": {
                    "risk_level": self.risk_control_level,
                    "max_position_per_stock": self.max_position_per_stock,
                    "daily_loss_limit": self.daily_loss_limit,
                    "position_sizing_method": self.position_sizing_method,
                    "risk_learning_enabled": self.risk_learning_enabled,
                    "active_thresholds": self.risk_thresholds[self.risk_control_level]
                }
            }
            
        except Exception as e:
            logger.error(f"更新风险控制参数失败: {e}")
            return {"success": False, "message": f"更新失败: {str(e)}"}
    
    # ... 其他代码保持不变 ...

    # 添加一个综合决策方法,整合所有分析因素
    async def unified_decision_model(self, market_data, historical_data=None):
        """
        AI统一决策模型 - 整合多种策略和分析方法
        
        Args:
            market_data (dict): 市场数据
            historical_data (list, optional): 历史数据
            
        Returns:
            dict: 综合决策结果
        """
        decision_factors = {}
        weights = {}
        final_decision = {
            'action': 'hold',  # 默认持有
            'confidence': 0.0,
            'reasons': [],
            'source': 'unified_ai_model'
        }
        
        # 1. 技术分析因子 (40%)
        weights['technical'] = 0.4
        try:
            # 获取T交易机会评估
            t_opportunity = await self.evaluate_opportunity(market_data)
            
            decision_factors['t_trading'] = {
                'has_opportunity': t_opportunity.get('has_opportunity', False),
                'mode': t_opportunity.get('mode'),
                'confidence': t_opportunity.get('ai_confidence', 0.5),
                'suggested_action': 'buy' if t_opportunity.get('mode') == 'positive' else 'sell' if t_opportunity.get('mode') == 'negative' else 'hold'
            }
            
            # 价格趋势分析
            price_trend = self._analyze_price_trend(market_data) if self.price_predictor else None
            if price_trend:
                decision_factors['price_trend'] = price_trend
            
            # 添加技术指标分析结果
            tech_indicators = self._calculate_technical_indicators(market_data, historical_data)
            if tech_indicators:
                decision_factors['technical_indicators'] = tech_indicators
        except Exception as e:
            logger.error(f"技术分析计算错误: {str(e)}")
        
        # 2. 量价分析因子 (30%)
        weights['volume_price'] = 0.3
        try:
            volume_analysis = self._analyze_volume_price_relationship(market_data, historical_data)
            if volume_analysis:
                decision_factors['volume_price'] = volume_analysis
        except Exception as e:
            logger.error(f"量价分析计算错误: {str(e)}")
        
        # 3. 市场情绪因子 (15%)
        weights['market_sentiment'] = 0.15
        try:
            market_sentiment = self._analyze_market_sentiment(market_data)
            if market_sentiment:
                decision_factors['market_sentiment'] = market_sentiment
        except Exception as e:
            logger.error(f"市场情绪分析错误: {str(e)}")
        
        # 4. 历史绩效因子 (15%)
        weights['historical_performance'] = 0.15
        try:
            if historical_data:
                hist_performance = self._analyze_historical_performance(market_data, historical_data)
                if hist_performance:
                    decision_factors['historical_performance'] = hist_performance
        except Exception as e:
            logger.error(f"历史绩效分析错误: {str(e)}")
        
        # 综合所有因素,计算最终决策
        logger.info("AI正在整合各项分析因素,生成最终决策...")
        
        # 有T交易机会时,优先考虑T交易策略
        if 't_trading' in decision_factors and decision_factors['t_trading']['has_opportunity']:
            t_factor = decision_factors['t_trading']
            final_decision['action'] = t_factor['suggested_action']
            final_decision['confidence'] = t_factor['confidence']
            final_decision['reasons'].append(f"T交易策略({t_factor['mode']}模式)建议{t_factor['suggested_action']}")
            
            # 检查是否有其他因素支持该决策
            supporting_factors = 0
            
            if 'price_trend' in decision_factors:
                price_trend = decision_factors['price_trend']
                if (final_decision['action'] == 'buy' and price_trend['direction'] == 'up') or \
                   (final_decision['action'] == 'sell' and price_trend['direction'] == 'down'):
                    supporting_factors += 1
                    final_decision['reasons'].append(f"价格趋势({price_trend['direction']})支持该决策")
            
            if 'volume_price' in decision_factors:
                volume_price = decision_factors['volume_price']
                if (final_decision['action'] == 'buy' and volume_price['signal'] == 'bullish') or \
                   (final_decision['action'] == 'sell' and volume_price['signal'] == 'bearish'):
                    supporting_factors += 1
                    final_decision['reasons'].append(f"量价关系({volume_price['signal']})支持该决策")
            
            # 根据支持因素调整置信度
            if supporting_factors > 0:
                # 每个支持因素增加10%的置信度,最高不超过95%
                final_decision['confidence'] = min(0.95, final_decision['confidence'] * (1 + 0.1 * supporting_factors))
            
        else:
            # 没有T交易机会时,综合其他因素
            buy_signals = 0
            sell_signals = 0
            hold_signals = 0
            total_signals = 0
            
            # 计算各类信号数量
            for factor_type, factor_data in decision_factors.items():
                if factor_type == 't_trading':
                    continue  # T交易已单独处理
                
                signal = factor_data.get('signal')
                if signal == 'bullish':
                    buy_signals += 1
                elif signal == 'bearish':
                    sell_signals += 1
                else:
                    hold_signals += 1
                total_signals += 1
            
            # 如果总信号数量不足,建议持有
            if total_signals < 2:
                final_decision['action'] = 'hold'
                final_decision['confidence'] = 0.5
                final_decision['reasons'].append("分析因素不足,建议持有观望")
            else:
                # 根据信号多数决定行动
                if buy_signals > sell_signals and buy_signals > hold_signals:
                    final_decision['action'] = 'buy'
                    final_decision['confidence'] = 0.5 + (buy_signals / total_signals) * 0.4
                    final_decision['reasons'].append(f"{buy_signals}个看涨信号支持买入决策")
                elif sell_signals > buy_signals and sell_signals > hold_signals:
                    final_decision['action'] = 'sell'
                    final_decision['confidence'] = 0.5 + (sell_signals / total_signals) * 0.4
                    final_decision['reasons'].append(f"{sell_signals}个看跌信号支持卖出决策")
                else:
                    final_decision['action'] = 'hold'
                    final_decision['confidence'] = 0.6
                    final_decision['reasons'].append("信号不明确,建议持有观望")
        
        # 添加相关建议数据
        if final_decision['action'] != 'hold':
            final_decision['suggested_quantity'] = self._calculate_optimal_quantity(market_data, final_decision['confidence'])
            final_decision['price'] = market_data['current_price']
            
            # 添加预期收益和风险
            risk_reward = self._calculate_risk_reward(market_data, final_decision)
            if risk_reward:
                final_decision['risk_reward'] = risk_reward
        
        # 记录最终决策
        logger.info(f"AI最终决策: {final_decision['action']}, 置信度: {final_decision['confidence']:.2f}")
        logger.info(f"决策理由: {', '.join(final_decision['reasons'])}")
        
        return final_decision
    
    def _analyze_price_trend(self, market_data):
        """
        分析价格趋势
        
        Args:
            market_data (dict): 市场数据
            
        Returns:
            dict: 价格趋势分析结果
        """
        try:
            current_price = market_data['current_price']
            open_price = market_data['open_price']
            intraday_high = market_data['intraday_high']
            intraday_low = market_data['intraday_low']
            
            # 计算价格位置
            price_position = (current_price - intraday_low) / (intraday_high - intraday_low) if (intraday_high - intraday_low) > 0 else 0.5
            
            # 日内涨跌幅
            intraday_change = (current_price / open_price - 1) * 100
            
            # 判断趋势
            if self.price_predictor:
                features = self._extract_features(market_data)
                predicted_price = self.price_predictor.predict(features)[0]
                predicted_change = (predicted_price / current_price - 1) * 100
                
                direction = 'up' if predicted_change > 0.5 else 'down' if predicted_change < -0.5 else 'sideways'
                
                return {
                    'direction': direction,
                    'current_position': price_position,
                    'intraday_change': intraday_change,
                    'predicted_price': float(predicted_price),
                    'predicted_change': float(predicted_change),
                    'signal': 'bullish' if direction == 'up' else 'bearish' if direction == 'down' else 'neutral'
                }
            else:
                # 简单趋势判断
                if intraday_change > 1.0 and price_position > 0.7:
                    direction = 'up'
                    signal = 'bearish'  # 高位,可能反转向下
                elif intraday_change < -1.0 and price_position < 0.3:
                    direction = 'down'
                    signal = 'bullish'  # 低位,可能反转向上
                elif intraday_change > 0:
                    direction = 'up'
                    signal = 'neutral'
                elif intraday_change < 0:
                    direction = 'down'
                    signal = 'neutral'
                else:
                    direction = 'sideways'
                    signal = 'neutral'
                
                return {
                    'direction': direction,
                    'current_position': price_position,
                    'intraday_change': intraday_change,
                    'signal': signal
                }
        except Exception as e:
            logger.error(f"价格趋势分析错误: {str(e)}")
            return {
                'direction': 'unknown',
                'signal': 'neutral',
                'error': str(e)
            }
    
    def _calculate_technical_indicators(self, market_data, historical_data=None):
        """
        计算技术指标
        
        Args:
            market_data (dict): 市场数据
            historical_data (list, optional): 历史数据
            
        Returns:
            dict: 技术指标分析结果
        """
        # 如果没有历史数据,则无法计算大部分技术指标
        if not historical_data:
            return None
        
        try:
            indicators = {}
            bullish_count = 0
            bearish_count = 0
            
            # 模拟简单的MACD指标计算
            if len(historical_data) >= 26:
                ema12 = sum([d['close'] for d in historical_data[-12:]]) / 12
                ema26 = sum([d['close'] for d in historical_data[-26:]]) / 26
                macd = ema12 - ema26
                
                indicators['macd'] = {
                    'value': macd,
                    'signal': 'bullish' if macd > 0 else 'bearish'
                }
                
                if macd > 0:
                    bullish_count += 1
                else:
                    bearish_count += 1
            
            # 模拟RSI指标计算 (简化版)
            if len(historical_data) >= 14:
                gains = []
                losses = []
                
                for i in range(1, 15):
                    change = historical_data[-i]['close'] - historical_data[-(i+1)]['close']
                    if change >= 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))
                
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                indicators['rsi'] = {
                    'value': rsi,
                    'signal': 'bullish' if rsi < 30 else 'bearish' if rsi > 70 else 'neutral'
                }
                
                if rsi < 30:
                    bullish_count += 1
                elif rsi > 70:
                    bearish_count += 1
            
            # 计算布林带
            if len(historical_data) >= 20:
                closes = [d['close'] for d in historical_data[-20:]]
                sma20 = sum(closes) / 20
                std = (sum([(x - sma20) ** 2 for x in closes]) / 20) ** 0.5
                
                upper_band = sma20 + (2 * std)
                lower_band = sma20 - (2 * std)
                
                indicators['bollinger_bands'] = {
                    'middle': sma20,
                    'upper': upper_band,
                    'lower': lower_band
                }
                
                current_price = market_data['current_price']
                
                if current_price > upper_band:
                    indicators['bollinger_bands']['signal'] = 'bearish'
                    bearish_count += 1
                elif current_price < lower_band:
                    indicators['bollinger_bands']['signal'] = 'bullish'
                    bullish_count += 1
                else:
                    indicators['bollinger_bands']['signal'] = 'neutral'
            
            # 汇总技术指标信号
            overall_signal = 'neutral'
            if bullish_count > bearish_count:
                overall_signal = 'bullish'
            elif bearish_count > bullish_count:
                overall_signal = 'bearish'
            
            return {
                'indicators': indicators,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'signal': overall_signal
            }
            
        except Exception as e:
            logger.error(f"技术指标计算错误: {str(e)}")
            return None
    
    def _analyze_volume_price_relationship(self, market_data, historical_data=None):
        """
        分析量价关系
        
        Args:
            market_data (dict): 市场数据
            historical_data (list, optional): 历史数据
            
        Returns:
            dict: 量价分析结果
        """
        try:
            current_price = market_data['current_price']
            current_volume = market_data['current_volume']
            avg_volume = market_data['avg_volume']
            intraday_high = market_data['intraday_high']
            intraday_low = market_data['intraday_low']
            open_price = market_data['open_price']
            
            # 成交量比
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # 价格变动百分比
            price_change_percent = (current_price / open_price - 1) * 100
            
            # 简单量价分析
            if volume_ratio > 2.0:
                if price_change_percent > 2.0:
                    pattern = "放量上涨"
                    signal = "bullish"
                elif price_change_percent < -2.0:
                    pattern = "放量下跌"
                    signal = "bearish"
                else:
                    pattern = "量增价稳"
                    signal = "neutral"
            elif volume_ratio < 0.7:
                if price_change_percent > 1.0:
                    pattern = "缩量上涨"
                    signal = "bearish"  # 持续性存疑
                elif price_change_percent < -1.0:
                    pattern = "缩量下跌"
                    signal = "bullish"  # 可能见底
                else:
                    pattern = "量减价稳"
                    signal = "neutral"
            else:
                pattern = "量价平稳"
                signal = "neutral"
            
            # 如果有历史数据,进行更复杂的量价分析
            if historical_data and len(historical_data) >= 5:
                # 检查是否存在量价背离
                price_trend_up = current_price > historical_data[-2]['close'] > historical_data[-3]['close']
                volume_trend_up = current_volume > historical_data[-2]['volume'] > historical_data[-3]['volume']
                
                if price_trend_up and not volume_trend_up:
                    pattern = "量价背离(价升量缩)"
                    signal = "bearish"
                elif not price_trend_up and volume_trend_up:
                    pattern = "量价背离(价跌量增)"
                    signal = "bullish"
            
            return {
                'volume_ratio': volume_ratio,
                'price_change_percent': price_change_percent,
                'pattern': pattern,
                'signal': signal
            }
            
        except Exception as e:
            logger.error(f"量价分析错误: {str(e)}")
            return {
                'signal': 'neutral',
                'error': str(e)
            }
    
    def _analyze_market_sentiment(self, market_data):
        """
        分析市场情绪
        
        Args:
            market_data (dict): 市场数据
            
        Returns:
            dict: 市场情绪分析结果
        """
        try:
            # 实际项目中可以接入市场情绪API或新闻情感分析
            # 这里使用随机模拟,实际应用中应当使用真实数据
            
            # 模拟市场情绪分数 (0-100)
            import random
            sentiment_score = random.randint(30, 70)
            
            if sentiment_score > 60:
                sentiment = "乐观"
                signal = "bullish"
            elif sentiment_score < 40:
                sentiment = "悲观"
                signal = "bearish"
            else:
                sentiment = "中性"
                signal = "neutral"
            
            return {
                'score': sentiment_score,
                'sentiment': sentiment,
                'signal': signal
            }
        
        except Exception as e:
            logger.error(f"市场情绪分析错误: {str(e)}")
            return {
                'signal': 'neutral',
                'error': str(e)
            }
    
    def _analyze_historical_performance(self, market_data, historical_data):
        """
        分析历史绩效,评估策略在类似情况下的表现
        
        Args:
            market_data (dict): 市场数据
            historical_data (list): 历史数据
            
        Returns:
            dict: 历史绩效分析结果
        """
        try:
            if not historical_data or len(historical_data) < 10:
                return None
            
            # 模拟在类似市场条件下的历史绩效
            similar_cases = 0
            successful_cases = 0
            
            # 当前价格位置
            current_position = (market_data['current_price'] - market_data['intraday_low']) / (market_data['intraday_high'] - market_data['intraday_low']) if (market_data['intraday_high'] - market_data['intraday_low']) > 0 else 0.5
            
            # 当前成交量比
            current_volume_ratio = market_data['current_volume'] / market_data['avg_volume'] if market_data['avg_volume'] > 0 else 1.0
            
            # 查找历史上类似的情况
            for case in historical_data:
                if 'position' not in case or 'volume_ratio' not in case:
                    continue
                
                position_diff = abs(case['position'] - current_position)
                volume_diff = abs(case['volume_ratio'] - current_volume_ratio)
                
                # 如果位置和成交量都相似
                if position_diff < 0.2 and volume_diff < 0.5:
                    similar_cases += 1
                    if case.get('result') == 'success':
                        successful_cases += 1
            
            if similar_cases == 0:
                return None
            
            success_rate = successful_cases / similar_cases
            
            if success_rate > 0.7:
                signal = "bullish"
                assessment = "历史表现优异"
            elif success_rate > 0.5:
                signal = "neutral"
                assessment = "历史表现一般"
            else:
                signal = "bearish"
                assessment = "历史表现不佳"
            
            return {
                'similar_cases': similar_cases,
                'success_rate': success_rate,
                'assessment': assessment,
                'signal': signal
            }
            
        except Exception as e:
            logger.error(f"历史绩效分析错误: {str(e)}")
            return None
    
    def _calculate_optimal_quantity(self, market_data, confidence):
        """
        计算最优交易数量
        
        Args:
            market_data (dict): 市场数据
            confidence (float): 决策置信度
            
        Returns:
            int: 建议交易数量
        """
        try:
            base_position = market_data['base_position']
            
            # 根据置信度调整交易比例
            if confidence > 0.85:
                ratio = 0.3  # 高置信度,使用30%的底仓
            elif confidence > 0.7:
                ratio = 0.2  # 中等置信度,使用20%的底仓
            else:
                ratio = 0.1  # 低置信度,使用10%的底仓
            
            # 确保数量为整数且不少于100股(A股最小交易单位)
            quantity = max(100, int(base_position * ratio))
            
            # 确保不超过底仓
            return min(quantity, base_position)
            
        except Exception as e:
            logger.error(f"计算最优交易数量错误: {str(e)}")
            return int(market_data['base_position'] * 0.1)  # 默认使用10%底仓
    
    def _calculate_risk_reward(self, market_data, decision):
        """
        计算风险收益比
        
        Args:
            market_data (dict): 市场数据
            decision (dict): 交易决策
            
        Returns:
            dict: 风险收益分析
        """
        try:
            current_price = market_data['current_price']
            
            # 根据决策类型和置信度设置目标价和止损价
            if decision['action'] == 'buy':
                # 买入情况下的目标收益和止损
                target_gain_pct = 0.01 + (decision['confidence'] - 0.5) * 0.02  # 1-3%
                stop_loss_pct = 0.005 + (1 - decision['confidence']) * 0.01  # 0.5-1.5%
                
                target_price = current_price * (1 + target_gain_pct)
                stop_loss = current_price * (1 - stop_loss_pct)
                
            elif decision['action'] == 'sell':
                # 卖出情况下的目标收益和止损
                target_drop_pct = 0.01 + (decision['confidence'] - 0.5) * 0.02  # 1-3%
                stop_loss_pct = 0.005 + (1 - decision['confidence']) * 0.01  # 0.5-1.5%
                
                target_price = current_price * (1 - target_drop_pct)
                stop_loss = current_price * (1 + stop_loss_pct)
                
            else:
                return None
            
            # 计算风险收益比
            potential_gain = abs(target_price - current_price) * decision['suggested_quantity']
            potential_loss = abs(stop_loss - current_price) * decision['suggested_quantity']
            
            risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else float('inf')
            
            return {
                'target_price': float(target_price),
                'stop_loss': float(stop_loss),
                'potential_gain': float(potential_gain),
                'potential_loss': float(potential_loss),
                'risk_reward_ratio': float(risk_reward_ratio)
            }
            
        except Exception as e:
            logger.error(f"计算风险收益比错误: {str(e)}")
            return None 
