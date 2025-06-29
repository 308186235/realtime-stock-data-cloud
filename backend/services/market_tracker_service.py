import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import asyncio

from services.ai_service import AIService
from services.auto_trader_service import AutoTraderService

logger = logging.getLogger(__name__)

# ******************************************************************************
# NOTE: This service is essential for the AI trading system and is actively used
# even though the dedicated "市场追踪" frontend UI has been removed. This service 
# provides market data analysis, trend recognition and decision support that is
# consumed by the AI trading system in the AI Analysis module.
# ******************************************************************************

class MarketTrackerService:
    """
    Service for tracking real-time market movements and comparing them with AI predictions.
    """
    
    def __init__(self, ai_service=None, auto_trader_service=None):
        """
        Initialize the market tracker service.
        
        Args:
            ai_service (AIService): AI service instance for predictions
            auto_trader_service (AutoTraderService): Auto trader service for automated trading
        """
        self.ai_service = ai_service or AIService()
        self.auto_trader_service = auto_trader_service or AutoTraderService()
        self.data_path = 'data/market_tracking'
        self.active_trackers = {}
        self.alert_subscribers = {}  # 储存警报订阅者
        self.alert_thresholds = {
            "price_change": 0.02,  # 价格变化阈值,默认2%
            "divergence": 0.7,     # 背离度阈值,超过该值则触发警报
            "accuracy_drop": 0.15  # 准确度下降阈值
        }
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        logger.info("Market Tracker Service initialized")
    
    async def start_tracking(self, stock_code, prediction_days=10):
        """
        Start tracking a stock and its comparison with AI predictions.
        
        Args:
            stock_code (str): Stock code to track
            prediction_days (int): Number of days for AI prediction
            
        Returns:
            dict: Tracking initialization result
        """
        try:
            # Get current market data
            current_data = await self._get_market_data(stock_code)
            
            if not current_data or current_data.empty:
                return {"error": f"Could not get market data for {stock_code}"}
            
            # Get AI prediction
            prediction_result = await self.ai_service.predict_stock_price(stock_code, prediction_days)
            
            if "error" in prediction_result:
                return {"error": f"Failed to get AI prediction: {prediction_result['error']}"}
            
            # Initialize tracking record
            tracker_id = f"{stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Extract current price and predicted trend
            current_price = current_data['close'].iloc[-1]
            predictions = prediction_result['predictions']
            
            # Calculate predicted direction and magnitude
            last_predicted_price = predictions[-1]['predicted_price']
            predicted_change = (last_predicted_price - current_price) / current_price
            predicted_direction = "up" if predicted_change > 0 else "down"
            
            # Create tracker record
            tracker = {
                "id": tracker_id,
                "stock_code": stock_code,
                "start_date": datetime.now().isoformat(),
                "start_price": float(current_price),
                "predicted_direction": predicted_direction,
                "predicted_change": float(predicted_change),
                "predictions": predictions,
                "actual_prices": [{"date": datetime.now().isoformat(), "price": float(current_price)}],
                "comparison_metrics": self._calculate_initial_metrics(current_price, predictions),
                "status": "active"
            }
            
            # Save to active trackers
            self.active_trackers[tracker_id] = tracker
            
            # Save to disk
            self._save_tracker(tracker)
            
            return {
                "tracker_id": tracker_id,
                "stock_code": stock_code,
                "start_price": float(current_price),
                "predicted_direction": predicted_direction,
                "predicted_change": float(predicted_change),
                "predictions": predictions
            }
            
        except Exception as e:
            logger.error(f"Error starting market tracking: {e}")
            return {"error": str(e)}
    
    async def update_tracker(self, tracker_id):
        """
        更新追踪器并检查是否需要发送警报。
        
        Args:
            tracker_id (str): 追踪器ID
            
        Returns:
            dict: 更新后的追踪器数据
        """
        try:
            # 获取追踪器数据
            tracker = self.active_trackers.get(tracker_id)
            
            if not tracker:
                # 尝试从磁盘加载
                tracker = self._load_tracker(tracker_id)
                
            if not tracker:
                return {"error": f"Tracker {tracker_id} not found"}
            
            if tracker["status"] != "active":
                return {"error": f"Tracker {tracker_id} is not active"}
            
            # 保存旧指标用于比较
            old_metrics = tracker["comparison_metrics"].copy() if "comparison_metrics" in tracker else {}
            old_actual_prices = tracker.get("actual_prices", [])
            last_price = old_actual_prices[-1]["price"] if old_actual_prices else tracker["start_price"]
            
            # 获取当前市场数据
            current_data = await self._get_market_data(tracker["stock_code"])
            
            if not current_data or current_data.empty:
                return {"error": f"Could not get market data for {tracker['stock_code']}"}
            
            # 提取当前价格
            current_price = current_data['close'].iloc[-1]
            
            # 添加到实际价格列表
            tracker["actual_prices"].append({
                "date": datetime.now().isoformat(),
                "price": float(current_price)
            })
            
            # 计算基于比较的指标
            metrics = self._calculate_comparison_metrics(tracker, current_price)
            tracker["comparison_metrics"] = metrics
            
            # 更新内存和磁盘
            self.active_trackers[tracker_id] = tracker
            self._save_tracker(tracker)
            
            # 生成交易信号
            trading_signal = self._generate_trading_signal(metrics)
            
            # 检查是否需要触发警报
            alerts = await self._check_alerts(
                tracker_id, 
                current_price, 
                last_price, 
                old_metrics, 
                metrics, 
                trading_signal
            )
            
            result = {
                "tracker_id": tracker_id,
                "stock_code": tracker["stock_code"],
                "current_price": float(current_price),
                "change_since_start": metrics["actual_change"],
                "prediction_accuracy": metrics["prediction_accuracy"],
                "alignment_status": metrics["alignment_status"],
                "trading_signal": trading_signal
            }
            
            # 如果有警报,添加到结果中
            if alerts:
                result["alerts"] = alerts
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating market tracker: {e}")
            return {"error": str(e)}
    
    async def get_tracker_details(self, tracker_id):
        """
        Get detailed information about a tracker.
        
        Args:
            tracker_id (str): Tracker ID
            
        Returns:
            dict: Detailed tracker information
        """
        try:
            # Get tracker data
            tracker = self.active_trackers.get(tracker_id)
            
            if not tracker:
                # Try to load from disk
                tracker = self._load_tracker(tracker_id)
                
            if not tracker:
                return {"error": f"Tracker {tracker_id} not found"}
            
            return tracker
            
        except Exception as e:
            logger.error(f"Error getting tracker details: {e}")
            return {"error": str(e)}
    
    async def get_active_trackers(self):
        """
        Get list of all active trackers.
        
        Returns:
            list: Active trackers
        """
        try:
            # Get all trackers from disk
            trackers = []
            
            for filename in os.listdir(self.data_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.data_path, filename), 'r') as f:
                            tracker = json.load(f)
                            
                            if tracker["status"] == "active":
                                trackers.append({
                                    "tracker_id": tracker["id"],
                                    "stock_code": tracker["stock_code"],
                                    "start_date": tracker["start_date"],
                                    "start_price": tracker["start_price"],
                                    "predicted_direction": tracker["predicted_direction"],
                                    "comparison_metrics": tracker["comparison_metrics"]
                                })
                    except Exception as e:
                        logger.error(f"Error loading tracker from file {filename}: {e}")
            
            return trackers
            
        except Exception as e:
            logger.error(f"Error getting active trackers: {e}")
            return []
    
    async def update_all_active_trackers(self):
        """
        Update all active trackers with latest market data.
        This method is meant to be called by a scheduler.
        """
        try:
            # Get all active trackers
            active_trackers = []
            
            for filename in os.listdir(self.data_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.data_path, filename), 'r') as f:
                            tracker = json.load(f)
                            
                            if tracker["status"] == "active":
                                active_trackers.append(tracker["id"])
                    except Exception as e:
                        logger.error(f"Error loading tracker from file {filename}: {e}")
            
            logger.info(f"Updating {len(active_trackers)} active trackers")
            
            # Update each tracker
            for tracker_id in active_trackers:
                try:
                    await self.update_tracker(tracker_id)
                except Exception as e:
                    logger.error(f"Error updating tracker {tracker_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in update_all_active_trackers: {e}")
    
    async def update_high_priority_trackers(self):
        """
        快速更新高优先级追踪器,用于实时响应。
        此方法会更频繁地调用,只处理需要密切监控的追踪器。
        """
        try:
            # 获取所有活跃追踪器
            high_priority_trackers = []
            
            for filename in os.listdir(self.data_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.data_path, filename), 'r') as f:
                            tracker = json.load(f)
                            
                            # 只处理活跃且满足高优先级条件的追踪器
                            if tracker["status"] == "active":
                                # 高优先级条件:
                                # 1. 最近添加的追踪器
                                # 2. 有警报触发的追踪器
                                # 3. 市场波动较大的追踪器
                                
                                is_high_priority = False
                                
                                # 检查是否是最近添加的追踪器
                                if "start_date" in tracker:
                                    start_date = datetime.fromisoformat(tracker["start_date"].replace('Z', '+00:00'))
                                    if (datetime.now() - start_date).total_seconds() < 3600:  # 1小时内添加的
                                        is_high_priority = True
                                
                                # 检查是否有价格大幅波动
                                if "actual_prices" in tracker and len(tracker["actual_prices"]) >= 2:
                                    latest_price = tracker["actual_prices"][-1]["price"]
                                    previous_price = tracker["actual_prices"][-2]["price"]
                                    price_change = abs(latest_price - previous_price) / previous_price
                                    
                                    if price_change > 0.01:  # 价格变化超过1%
                                        is_high_priority = True
                                
                                # 检查是否对齐状态变化
                                if "comparison_metrics" in tracker and "alignment_status" in tracker["comparison_metrics"]:
                                    alignment = tracker["comparison_metrics"]["alignment_status"]
                                    if alignment == "divergent":  # 与AI预测背离
                                        is_high_priority = True
                                
                                if is_high_priority:
                                    high_priority_trackers.append(tracker["id"])
                    except Exception as e:
                        logger.error(f"Error loading tracker from file {filename}: {e}")
            
            if high_priority_trackers:
                logger.info(f"Rapid updating {len(high_priority_trackers)} high priority trackers")
                
                # 使用asyncio.gather并行更新所有高优先级追踪器
                update_tasks = [self.update_tracker(tracker_id) for tracker_id in high_priority_trackers]
                results = await asyncio.gather(*update_tasks, return_exceptions=True)
                
                # 处理结果和错误
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error rapid updating tracker {high_priority_trackers[i]}: {result}")
            
        except Exception as e:
            logger.error(f"Error in update_high_priority_trackers: {e}")
    
    async def stop_tracking(self, tracker_id):
        """
        Stop tracking a stock.
        
        Args:
            tracker_id (str): Tracker ID to stop
            
        Returns:
            dict: Result of operation
        """
        try:
            # Get tracker data
            tracker = self.active_trackers.get(tracker_id)
            
            if not tracker:
                # Try to load from disk
                tracker = self._load_tracker(tracker_id)
                
            if not tracker:
                return {"error": f"Tracker {tracker_id} not found"}
            
            # Update status
            tracker["status"] = "stopped"
            tracker["end_date"] = datetime.now().isoformat()
            
            # Save to disk
            self._save_tracker(tracker)
            
            # Remove from active trackers
            if tracker_id in self.active_trackers:
                del self.active_trackers[tracker_id]
            
            return {
                "tracker_id": tracker_id,
                "status": "stopped",
                "message": f"Stopped tracking {tracker['stock_code']}"
            }
            
        except Exception as e:
            logger.error(f"Error stopping market tracker: {e}")
            return {"error": str(e)}
    
    def _calculate_initial_metrics(self, current_price, predictions):
        """
        Calculate initial comparison metrics.
        
        Args:
            current_price (float): Current stock price
            predictions (list): Predicted prices
            
        Returns:
            dict: Initial metrics
        """
        # Calculate predicted direction and magnitude
        last_predicted_price = predictions[-1]['predicted_price']
        predicted_change = (last_predicted_price - current_price) / current_price
        
        return {
            "predicted_change": float(predicted_change),
            "actual_change": 0.0,
            "prediction_accuracy": 100.0,  # Initial accuracy is 100%
            "alignment_status": "aligned",  # Initially aligned by definition
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_comparison_metrics(self, tracker, current_price):
        """
        Calculate comparison metrics between actual and predicted prices.
        
        Args:
            tracker (dict): Tracker data
            current_price (float): Current stock price
            
        Returns:
            dict: Comparison metrics
        """
        # Calculate actual change
        start_price = tracker["start_price"]
        actual_change = (current_price - start_price) / start_price
        
        # Get predicted change
        predicted_change = tracker["comparison_metrics"]["predicted_change"]
        
        # Calculate prediction accuracy
        # This is a simple measure of how close the actual movement is to the predicted movement
        if abs(predicted_change) < 0.0001:  # Avoid division by zero if prediction is flat
            prediction_accuracy = 100.0 if abs(actual_change) < 0.0001 else 0.0
        else:
            # Calculate accuracy as percentage of similarity between actual and predicted change
            if (predicted_change > 0 and actual_change > 0) or (predicted_change < 0 and actual_change < 0):
                # Same direction - calculate how close the magnitude is
                ratio = min(abs(actual_change), abs(predicted_change)) / max(abs(actual_change), abs(predicted_change))
                prediction_accuracy = ratio * 100.0
            else:
                # Opposite direction - zero accuracy
                prediction_accuracy = 0.0
        
        # Determine alignment status
        if (predicted_change > 0 and actual_change > 0) or (predicted_change < 0 and actual_change < 0):
            alignment_status = "aligned"
        else:
            alignment_status = "divergent"
        
        return {
            "predicted_change": float(predicted_change),
            "actual_change": float(actual_change),
            "prediction_accuracy": float(prediction_accuracy),
            "alignment_status": alignment_status,
            "last_updated": datetime.now().isoformat()
        }
    
    def _generate_trading_signal(self, metrics):
        """
        Generate trading signal based on prediction and actual market alignment.
        
        Args:
            metrics (dict): Comparison metrics
            
        Returns:
            dict: Trading signal
        """
        alignment_status = metrics["alignment_status"]
        actual_change = metrics["actual_change"]
        prediction_accuracy = metrics["prediction_accuracy"]
        
        if alignment_status == "aligned" and actual_change > 0 and prediction_accuracy > 70:
            # Aligned upward movement with good accuracy - consider increasing position
            signal = "INCREASE_POSITION"
            confidence = min(100, prediction_accuracy + 10)
            message = "市场走势与AI预测一致,且方向向上,考虑加仓"
        elif alignment_status == "aligned" and actual_change < 0 and prediction_accuracy > 70:
            # Aligned downward movement with good accuracy - consider reducing position
            signal = "REDUCE_POSITION"
            confidence = min(100, prediction_accuracy + 10)
            message = "市场走势与AI预测一致,且方向向下,考虑减仓"
        elif alignment_status == "divergent" and actual_change < 0:
            # Divergent with downward actual movement - consider exiting
            signal = "EXIT_POSITION"
            confidence = max(50, 100 - prediction_accuracy)
            message = "市场走势与AI预测不一致,且实际走势向下,考虑离场观望"
        elif alignment_status == "divergent" and actual_change > 0:
            # Divergent with upward actual movement - monitor closely
            signal = "MONITOR"
            confidence = 50
            message = "市场走势与AI预测不一致,但实际走势向上,密切关注"
        else:
            # Default - hold
            signal = "HOLD"
            confidence = 50
            message = "维持当前仓位,继续观察"
        
        return {
            "signal": signal,
            "confidence": float(confidence),
            "message": message
        }
    
    async def _get_market_data(self, stock_code, days=1):
        """
        Get recent market data for a stock.
        
        Args:
            stock_code (str): Stock code
            days (int): Number of days of data
            
        Returns:
            pd.DataFrame: Market data
        """
        # In a real implementation, this would fetch real-time data from market data service
        # For demonstration, we'll create mock data
        
        try:
            # Create mock data for demonstration
            dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
            
            # Generate some realistic looking price data
            n = len(dates)
            seed = sum(ord(c) for c in stock_code)  # Use stock code to seed the random generator
            np.random.seed(seed + int(datetime.now().timestamp()) // 3600)  # Change seed each hour
            
            # Start with a base price
            base_price = 50 + (seed % 100)
            
            # Generate a price trend with some randomness
            trend = np.linspace(0, 0.01, n) * base_price
            random_walk = np.random.normal(0, 0.005, n).cumsum() * base_price
            
            close = base_price + trend + random_walk
            
            # Create other price columns
            open_price = close * np.random.normal(1, 0.002, n)
            high = np.maximum(close, open_price) * np.random.normal(1.005, 0.002, n)
            low = np.minimum(close, open_price) * np.random.normal(0.995, 0.002, n)
            
            # Generate volume
            volume = np.abs(np.diff(np.concatenate([[0], close]))) * 100000 + np.random.normal(500000, 100000, n)
            volume = np.maximum(volume, 10000).astype(int)
            
            # Create DataFrame
            data = pd.DataFrame({
                'date': dates,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return pd.DataFrame()
    
    def _save_tracker(self, tracker):
        """
        Save tracker data to disk.
        
        Args:
            tracker (dict): Tracker data
        """
        try:
            filename = f"{tracker['id']}.json"
            filepath = os.path.join(self.data_path, filename)
            
            with open(filepath, 'w') as f:
                json.dump(tracker, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving tracker: {e}")
    
    def _load_tracker(self, tracker_id):
        """
        Load tracker data from disk.
        
        Args:
            tracker_id (str): Tracker ID
            
        Returns:
            dict: Tracker data or None if not found
        """
        try:
            filename = f"{tracker_id}.json"
            filepath = os.path.join(self.data_path, filename)
            
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r') as f:
                tracker = json.load(f)
                
            # Add to active trackers if active
            if tracker["status"] == "active":
                self.active_trackers[tracker_id] = tracker
                
            return tracker
            
        except Exception as e:
            logger.error(f"Error loading tracker: {e}")
            return None
    
    async def set_alert_thresholds(self, thresholds):
        """
        设置警报阈值。
        
        Args:
            thresholds (dict): 警报阈值字典
            
        Returns:
            dict: 更新后的阈值设置
        """
        for key, value in thresholds.items():
            if key in self.alert_thresholds and isinstance(value, (int, float)):
                self.alert_thresholds[key] = value
                
        return self.alert_thresholds
    
    async def subscribe_alerts(self, tracker_id, subscriber_id, alert_types=None):
        """
        订阅特定追踪器的警报。
        
        Args:
            tracker_id (str): 追踪器ID
            subscriber_id (str): 订阅者ID(用于通知发送)
            alert_types (list): 警报类型列表,None代表全部
            
        Returns:
            dict: 订阅结果
        """
        if not alert_types:
            alert_types = ["price_change", "direction_change", "accuracy_drop", "trading_signal"]
            
        if tracker_id not in self.alert_subscribers:
            self.alert_subscribers[tracker_id] = {}
            
        self.alert_subscribers[tracker_id][subscriber_id] = {
            "alert_types": alert_types,
            "last_alert": datetime.now().isoformat(),
            "enabled": True
        }
        
        return {
            "tracker_id": tracker_id,
            "subscriber_id": subscriber_id,
            "alert_types": alert_types,
            "status": "subscribed"
        }
    
    async def unsubscribe_alerts(self, tracker_id, subscriber_id):
        """
        取消订阅警报。
        
        Args:
            tracker_id (str): 追踪器ID
            subscriber_id (str): 订阅者ID
            
        Returns:
            dict: 操作结果
        """
        if tracker_id in self.alert_subscribers and subscriber_id in self.alert_subscribers[tracker_id]:
            del self.alert_subscribers[tracker_id][subscriber_id]
            
            if not self.alert_subscribers[tracker_id]:
                del self.alert_subscribers[tracker_id]
                
            return {
                "status": "unsubscribed",
                "message": f"已取消 {tracker_id} 的警报订阅"
            }
        
        return {
            "status": "error",
            "message": "未找到订阅记录"
        }
    
    async def _check_alerts(self, tracker_id, current_price, last_price, old_metrics, new_metrics, trading_signal):
        """
        检查是否需要触发警报。
        
        Args:
            tracker_id (str): 追踪器ID
            current_price (float): 当前价格
            last_price (float): 上次价格
            old_metrics (dict): 旧指标
            new_metrics (dict): 新指标
            trading_signal (dict): 交易信号
            
        Returns:
            list: 触发的警报列表
        """
        # 没有订阅者则不检查警报
        if tracker_id not in self.alert_subscribers:
            return []
            
        alerts = []
        
        # 检查价格变化警报
        price_change = (current_price - last_price) / last_price
        if abs(price_change) >= self.alert_thresholds["price_change"]:
            price_alert = {
                "type": "price_change",
                "price_change": float(price_change),
                "price_change_pct": float(price_change * 100),
                "last_price": float(last_price),
                "current_price": float(current_price),
                "direction": "up" if price_change > 0 else "down",
                "timestamp": datetime.now().isoformat(),
                "message": f"价格{'上涨' if price_change > 0 else '下跌'}{abs(price_change * 100):.2f}%,当前价格: {current_price:.2f}"
            }
            alerts.append(price_alert)
            
            # 将价格变化信号发送到自动交易服务
            try:
                asyncio.create_task(self.auto_trader_service.handle_market_signal(
                    tracker_id,
                    price_alert
                ))
            except Exception as e:
                logger.error(f"发送价格变化信号到自动交易服务失败: {e}")
        
        # 检查方向变化警报(从上涨变为下跌或反之)
        if "alignment_status" in old_metrics and old_metrics["alignment_status"] != new_metrics["alignment_status"]:
            direction_alert = {
                "type": "direction_change",
                "old_status": old_metrics["alignment_status"],
                "new_status": new_metrics["alignment_status"],
                "timestamp": datetime.now().isoformat(),
                "message": f"市场走势与AI预测的关系从 {self._get_alignment_text(old_metrics['alignment_status'])} 变为 {self._get_alignment_text(new_metrics['alignment_status'])}"
            }
            alerts.append(direction_alert)
            
            # 将方向变化信号发送到自动交易服务
            try:
                asyncio.create_task(self.auto_trader_service.handle_market_signal(
                    tracker_id,
                    direction_alert
                ))
            except Exception as e:
                logger.error(f"发送方向变化信号到自动交易服务失败: {e}")
        
        # 检查准确度下降警报
        if "prediction_accuracy" in old_metrics and old_metrics["prediction_accuracy"] - new_metrics["prediction_accuracy"] >= self.alert_thresholds["accuracy_drop"] * 100:
            accuracy_alert = {
                "type": "accuracy_drop",
                "old_accuracy": float(old_metrics["prediction_accuracy"]),
                "new_accuracy": float(new_metrics["prediction_accuracy"]),
                "drop": float(old_metrics["prediction_accuracy"] - new_metrics["prediction_accuracy"]),
                "timestamp": datetime.now().isoformat(),
                "message": f"AI预测准确度下降 {old_metrics['prediction_accuracy'] - new_metrics['prediction_accuracy']:.2f}%,当前准确度: {new_metrics['prediction_accuracy']:.2f}%"
            }
            alerts.append(accuracy_alert)
            
            # 将准确度下降信号发送到自动交易服务
            try:
                asyncio.create_task(self.auto_trader_service.handle_market_signal(
                    tracker_id,
                    accuracy_alert
                ))
            except Exception as e:
                logger.error(f"发送准确度下降信号到自动交易服务失败: {e}")
        
        # 检查交易信号警报(仅当信号为增加仓位,减少仓位或退出时)
        important_signals = ["INCREASE_POSITION", "REDUCE_POSITION", "EXIT_POSITION"]
        if trading_signal["signal"] in important_signals:
            signal_alert = {
                "type": "trading_signal",
                "signal": trading_signal["signal"],
                "confidence": float(trading_signal["confidence"]),
                "current_price": float(current_price),
                "message": trading_signal["message"],
                "timestamp": datetime.now().isoformat(),
                "action_required": True  # 标记为需要采取行动
            }
            alerts.append(signal_alert)
            
            # 将交易信号发送到自动交易服务
            try:
                asyncio.create_task(self.auto_trader_service.handle_market_signal(
                    tracker_id,
                    signal_alert
                ))
            except Exception as e:
                logger.error(f"发送交易信号到自动交易服务失败: {e}")
        
        # 对于每个警报,向所有订阅者发送通知
        if alerts:
            await self._notify_subscribers(tracker_id, alerts)
            
        return alerts
    
    async def _notify_subscribers(self, tracker_id, alerts):
        """
        向订阅者发送警报通知。
        
        Args:
            tracker_id (str): 追踪器ID
            alerts (list): 警报列表
        """
        if tracker_id not in self.alert_subscribers:
            return
            
        # 获取当前时间
        now = datetime.now()
        
        for subscriber_id, subscription in self.alert_subscribers[tracker_id].items():
            if not subscription["enabled"]:
                continue
                
            # 筛选该订阅者关注的警报类型
            relevant_alerts = [
                alert for alert in alerts 
                if alert["type"] in subscription["alert_types"]
            ]
            
            if not relevant_alerts:
                continue
                
            # 在实际应用中,这里会调用通知服务向订阅者发送通知
            # 例如WebSocket推送,短信通知等
            
            # 记录最后一次警报时间
            subscription["last_alert"] = now.isoformat()
            
            logger.info(f"Sent {len(relevant_alerts)} alerts to subscriber {subscriber_id} for tracker {tracker_id}")
    
    def _get_alignment_text(self, alignment_status):
        """
        获取对齐状态的中文描述。
        
        Args:
            alignment_status (str): 对齐状态
            
        Returns:
            str: 中文描述
        """
        return "一致" if alignment_status == "aligned" else "背离" 
