"""
增强版学习管理器
提供更先进的AI学习机制，包括深度强化学习、模型评估和性能监控
"""

import numpy as np
import pandas as pd
import logging
import json
import asyncio
import os
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union, Optional, Tuple
import traceback
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

logger = logging.getLogger("EnhancedLearningManager")

class LearningPhase(Enum):
    """学习阶段枚举"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    FINE_TUNING = "fine_tuning"
    EVALUATION = "evaluation"

@dataclass
class Experience:
    """经验数据类"""
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    done: bool
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class ModelPerformance:
    """模型性能数据类"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    timestamp: datetime

class EnhancedLearningManager:
    """
    增强版学习管理器
    提供先进的AI学习和优化功能
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化增强版学习管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 学习配置
        self.learning_config = {
            "experience_buffer_size": self.config.get("experience_buffer_size", 50000),
            "batch_size": self.config.get("batch_size", 64),
            "learning_rate": self.config.get("learning_rate", 0.001),
            "discount_factor": self.config.get("discount_factor", 0.95),
            "exploration_rate": self.config.get("exploration_rate", 0.3),
            "min_exploration_rate": self.config.get("min_exploration_rate", 0.01),
            "exploration_decay": self.config.get("exploration_decay", 0.995),
            "target_update_frequency": self.config.get("target_update_frequency", 100),
            "save_frequency": self.config.get("save_frequency", 1000)
        }
        
        # 数据存储
        self.models_dir = self.config.get("models_dir", "models")
        self.data_dir = self.config.get("data_dir", "data")
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 经验回放缓冲区
        self.experience_buffer = deque(maxlen=self.learning_config["experience_buffer_size"])
        
        # 学习状态
        self.learning_state = {
            "phase": LearningPhase.EXPLORATION,
            "total_experiences": 0,
            "total_updates": 0,
            "episodes": 0,
            "current_episode_reward": 0.0,
            "best_episode_reward": float('-inf'),
            "exploration_rate": self.learning_config["exploration_rate"],
            "last_update_time": None,
            "last_save_time": None
        }
        
        # 性能监控
        self.performance_history = []
        self.current_performance = ModelPerformance(
            accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
            sharpe_ratio=0.0, max_drawdown=0.0, win_rate=0.0,
            profit_factor=0.0, total_trades=0, timestamp=datetime.now()
        )
        
        # 模型管理
        self.models = {}
        self.model_versions = defaultdict(int)
        
        # 数据库连接
        self.db_path = os.path.join(self.data_dir, "learning_data.db")
        self._init_database()
        
        # 学习线程
        self.learning_thread = None
        self.learning_active = False
        
        logger.info("Enhanced Learning Manager initialized")
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建经验表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reward REAL NOT NULL,
                    next_state TEXT NOT NULL,
                    done BOOLEAN NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # 创建性能表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    profit_factor REAL,
                    total_trades INTEGER,
                    timestamp DATETIME NOT NULL
                )
            ''')
            
            # 创建模型版本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    performance_score REAL,
                    file_path TEXT,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    async def add_experience(self, experience: Experience):
        """
        添加学习经验
        
        Args:
            experience: 经验数据
        """
        try:
            # 添加到内存缓冲区
            self.experience_buffer.append(experience)
            self.learning_state["total_experiences"] += 1
            
            # 保存到数据库
            await self._save_experience_to_db(experience)
            
            # 检查是否需要学习更新
            if len(self.experience_buffer) >= self.learning_config["batch_size"]:
                await self._trigger_learning_update()
            
            logger.debug(f"Experience added. Buffer size: {len(self.experience_buffer)}")
            
        except Exception as e:
            logger.error(f"Error adding experience: {e}")
    
    async def _save_experience_to_db(self, experience: Experience):
        """保存经验到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO experiences (state, action, reward, next_state, done, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                json.dumps(experience.state),
                json.dumps(experience.action),
                experience.reward,
                json.dumps(experience.next_state),
                experience.done,
                experience.timestamp.isoformat(),
                json.dumps(experience.metadata) if experience.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving experience to database: {e}")
    
    async def _trigger_learning_update(self):
        """触发学习更新"""
        try:
            if not self.learning_active:
                self.learning_active = True
                
                # 在后台线程中执行学习
                if self.learning_thread is None or not self.learning_thread.is_alive():
                    self.learning_thread = threading.Thread(target=self._learning_worker)
                    self.learning_thread.daemon = True
                    self.learning_thread.start()
            
        except Exception as e:
            logger.error(f"Error triggering learning update: {e}")
    
    def _learning_worker(self):
        """学习工作线程"""
        try:
            while self.learning_active and len(self.experience_buffer) >= self.learning_config["batch_size"]:
                # 执行学习更新
                self._perform_learning_update()
                
                # 更新学习状态
                self.learning_state["total_updates"] += 1
                self.learning_state["last_update_time"] = datetime.now()
                
                # 检查是否需要保存模型
                if (self.learning_state["total_updates"] % 
                    self.learning_config["save_frequency"] == 0):
                    self._save_models()
                
                # 短暂休息
                time.sleep(0.1)
            
            self.learning_active = False
            
        except Exception as e:
            logger.error(f"Error in learning worker: {e}")
            self.learning_active = False
    
    def _perform_learning_update(self):
        """执行学习更新"""
        try:
            # 从经验缓冲区采样批次数据
            batch = self._sample_batch()
            
            if not batch:
                return
            
            # 执行Q学习更新
            self._update_q_learning(batch)
            
            # 更新探索率
            self._update_exploration_rate()
            
            # 评估当前性能
            self._evaluate_performance()
            
            logger.debug(f"Learning update completed. Updates: {self.learning_state['total_updates']}")
            
        except Exception as e:
            logger.error(f"Error performing learning update: {e}")
    
    def _sample_batch(self) -> List[Experience]:
        """从经验缓冲区采样批次数据"""
        try:
            batch_size = min(self.learning_config["batch_size"], len(self.experience_buffer))
            return list(np.random.choice(self.experience_buffer, batch_size, replace=False))
        except Exception as e:
            logger.error(f"Error sampling batch: {e}")
            return []
    
    def _update_q_learning(self, batch: List[Experience]):
        """更新Q学习模型"""
        try:
            # 简化的Q学习更新
            learning_rate = self.learning_config["learning_rate"]
            discount_factor = self.learning_config["discount_factor"]
            
            for experience in batch:
                # 将状态转换为可哈希的键
                state_key = self._state_to_key(experience.state)
                action_key = self._action_to_key(experience.action)
                next_state_key = self._state_to_key(experience.next_state)
                
                # 初始化Q值
                if state_key not in self.models:
                    self.models[state_key] = {}
                if action_key not in self.models[state_key]:
                    self.models[state_key][action_key] = 0.0
                
                # 计算目标Q值
                if experience.done:
                    target_q = experience.reward
                else:
                    next_q_values = self.models.get(next_state_key, {})
                    max_next_q = max(next_q_values.values()) if next_q_values else 0.0
                    target_q = experience.reward + discount_factor * max_next_q
                
                # 更新Q值
                current_q = self.models[state_key][action_key]
                self.models[state_key][action_key] = (
                    current_q + learning_rate * (target_q - current_q)
                )
            
        except Exception as e:
            logger.error(f"Error updating Q-learning: {e}")
    
    def _state_to_key(self, state: Dict[str, Any]) -> str:
        """将状态转换为可哈希的键"""
        try:
            # 简化状态表示
            key_parts = []
            for key in sorted(state.keys()):
                value = state[key]
                if isinstance(value, (int, float)):
                    # 量化数值
                    quantized = round(value, 2)
                    key_parts.append(f"{key}:{quantized}")
                elif isinstance(value, str):
                    key_parts.append(f"{key}:{value}")
            
            return "|".join(key_parts)
        except Exception as e:
            logger.error(f"Error converting state to key: {e}")
            return "unknown_state"
    
    def _action_to_key(self, action: Dict[str, Any]) -> str:
        """将动作转换为可哈希的键"""
        try:
            action_type = action.get('action', 'hold')
            return action_type
        except Exception as e:
            logger.error(f"Error converting action to key: {e}")
            return "unknown_action"

    def _update_exploration_rate(self):
        """更新探索率"""
        try:
            current_rate = self.learning_state["exploration_rate"]
            min_rate = self.learning_config["min_exploration_rate"]
            decay = self.learning_config["exploration_decay"]

            new_rate = max(min_rate, current_rate * decay)
            self.learning_state["exploration_rate"] = new_rate

            # 根据性能调整学习阶段
            if new_rate <= min_rate * 2:
                self.learning_state["phase"] = LearningPhase.EXPLOITATION
            elif self.current_performance.accuracy > 0.7:
                self.learning_state["phase"] = LearningPhase.FINE_TUNING

        except Exception as e:
            logger.error(f"Error updating exploration rate: {e}")

    def _evaluate_performance(self):
        """评估当前性能"""
        try:
            # 获取最近的交易结果
            recent_experiences = list(self.experience_buffer)[-100:] if len(self.experience_buffer) >= 100 else list(self.experience_buffer)

            if not recent_experiences:
                return

            # 计算性能指标
            total_trades = len(recent_experiences)
            profitable_trades = sum(1 for exp in recent_experiences if exp.reward > 0)
            total_reward = sum(exp.reward for exp in recent_experiences)

            win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0
            avg_reward = total_reward / total_trades if total_trades > 0 else 0.0

            # 计算夏普比率（简化版）
            rewards = [exp.reward for exp in recent_experiences]
            if len(rewards) > 1:
                reward_std = np.std(rewards)
                sharpe_ratio = avg_reward / reward_std if reward_std > 0 else 0.0
            else:
                sharpe_ratio = 0.0

            # 计算最大回撤
            cumulative_rewards = np.cumsum(rewards)
            running_max = np.maximum.accumulate(cumulative_rewards)
            drawdowns = (running_max - cumulative_rewards) / np.maximum(running_max, 1)
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0

            # 更新当前性能
            self.current_performance = ModelPerformance(
                accuracy=win_rate,
                precision=win_rate,  # 简化
                recall=win_rate,     # 简化
                f1_score=win_rate,   # 简化
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=abs(avg_reward) if avg_reward != 0 else 1.0,
                total_trades=total_trades,
                timestamp=datetime.now()
            )

            # 保存性能历史
            self.performance_history.append(self.current_performance)

            # 限制历史长度
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-500:]

            logger.debug(f"Performance evaluated: win_rate={win_rate:.2f}, sharpe={sharpe_ratio:.2f}")

        except Exception as e:
            logger.error(f"Error evaluating performance: {e}")

    def _save_models(self):
        """保存模型"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 保存Q学习模型
            q_model_path = os.path.join(self.models_dir, f"q_model_{timestamp}.pkl")
            with open(q_model_path, 'wb') as f:
                pickle.dump(self.models, f)

            # 保存学习状态
            state_path = os.path.join(self.models_dir, f"learning_state_{timestamp}.json")
            with open(state_path, 'w') as f:
                # 转换枚举为字符串
                state_copy = self.learning_state.copy()
                state_copy["phase"] = state_copy["phase"].value
                if state_copy["last_update_time"]:
                    state_copy["last_update_time"] = state_copy["last_update_time"].isoformat()
                json.dump(state_copy, f, indent=2)

            # 保存性能数据到数据库
            self._save_performance_to_db()

            self.learning_state["last_save_time"] = datetime.now()

            logger.info(f"Models saved: {q_model_path}")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def _save_performance_to_db(self):
        """保存性能数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            perf = self.current_performance
            cursor.execute('''
                INSERT INTO performance_history
                (accuracy, precision, recall, f1_score, sharpe_ratio, max_drawdown,
                 win_rate, profit_factor, total_trades, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                perf.accuracy, perf.precision, perf.recall, perf.f1_score,
                perf.sharpe_ratio, perf.max_drawdown, perf.win_rate,
                perf.profit_factor, perf.total_trades, perf.timestamp.isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving performance to database: {e}")

    async def get_learning_progress(self) -> Dict[str, Any]:
        """获取学习进度"""
        try:
            progress = {
                "learning_state": {
                    "phase": self.learning_state["phase"].value,
                    "total_experiences": self.learning_state["total_experiences"],
                    "total_updates": self.learning_state["total_updates"],
                    "episodes": self.learning_state["episodes"],
                    "exploration_rate": self.learning_state["exploration_rate"],
                    "last_update_time": self.learning_state["last_update_time"].isoformat() if self.learning_state["last_update_time"] else None
                },
                "current_performance": asdict(self.current_performance),
                "buffer_status": {
                    "size": len(self.experience_buffer),
                    "capacity": self.learning_config["experience_buffer_size"],
                    "utilization": len(self.experience_buffer) / self.learning_config["experience_buffer_size"]
                },
                "model_status": {
                    "q_table_size": len(self.models),
                    "learning_active": self.learning_active,
                    "last_save_time": self.learning_state["last_save_time"].isoformat() if self.learning_state["last_save_time"] else None
                }
            }

            return progress

        except Exception as e:
            logger.error(f"Error getting learning progress: {e}")
            return {"error": str(e)}

    async def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取性能历史"""
        try:
            recent_history = self.performance_history[-limit:] if self.performance_history else []
            return [asdict(perf) for perf in recent_history]

        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []

    async def optimize_hyperparameters(self, target_metric: str = "sharpe_ratio") -> Dict[str, Any]:
        """优化超参数"""
        try:
            if len(self.performance_history) < 10:
                return {"status": "insufficient_data", "message": "需要更多性能数据"}

            # 简化的超参数优化
            best_performance = max(self.performance_history,
                                 key=lambda x: getattr(x, target_metric))

            # 基于最佳性能调整学习率
            if best_performance.sharpe_ratio > 1.0:
                # 性能良好，降低学习率以稳定
                self.learning_config["learning_rate"] *= 0.9
            elif best_performance.sharpe_ratio < 0.5:
                # 性能较差，提高学习率以加快学习
                self.learning_config["learning_rate"] *= 1.1

            # 限制学习率范围
            self.learning_config["learning_rate"] = max(0.0001, min(0.01, self.learning_config["learning_rate"]))

            optimization_result = {
                "status": "completed",
                "target_metric": target_metric,
                "best_value": getattr(best_performance, target_metric),
                "new_learning_rate": self.learning_config["learning_rate"],
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Hyperparameters optimized: {optimization_result}")
            return optimization_result

        except Exception as e:
            logger.error(f"Error optimizing hyperparameters: {e}")
            return {"status": "error", "message": str(e)}

    async def reset_learning(self):
        """重置学习状态"""
        try:
            # 清空经验缓冲区
            self.experience_buffer.clear()

            # 重置学习状态
            self.learning_state = {
                "phase": LearningPhase.EXPLORATION,
                "total_experiences": 0,
                "total_updates": 0,
                "episodes": 0,
                "current_episode_reward": 0.0,
                "best_episode_reward": float('-inf'),
                "exploration_rate": self.learning_config["exploration_rate"],
                "last_update_time": None,
                "last_save_time": None
            }

            # 清空模型
            self.models.clear()

            # 清空性能历史
            self.performance_history.clear()

            logger.info("Learning state reset successfully")

        except Exception as e:
            logger.error(f"Error resetting learning: {e}")

    def shutdown(self):
        """关闭学习管理器"""
        try:
            self.learning_active = False

            # 等待学习线程结束
            if self.learning_thread and self.learning_thread.is_alive():
                self.learning_thread.join(timeout=5)

            # 保存最终状态
            self._save_models()

            logger.info("Enhanced Learning Manager shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
