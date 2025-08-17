import numpy as np
import pandas as pd
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union, Optional, Tuple
import traceback

logger = logging.getLogger("StrategyFusion")

class StrategyFusion:
    """
    策略融合器 - 负责整合多个交易策略的信号,生成统一的交易建议
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化策略融合器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 策略权重配置
        self.strategy_weights = {
            "momentum": 0.20,
            "mean_reversion": 0.20,
            "trend_following": 0.20,
            "breakout": 0.15,
            "volatility": 0.10,
            "fundamental": 0.10,
            "sentiment": 0.05
        }
        
        # 动态权重调整参数
        self.adaptive_weights = self.config.get("adaptive_weights", True)
        self.max_weight_adjustment = 0.10  # 最大权重调整幅度
        
        # 策略性能跟踪
        self.strategy_performance = {}
        
        # 融合方法
        self.fusion_method = self.config.get("fusion_method", "weighted_average")
        
        # 信号阈值
        self.signal_thresholds = {
            "strong_buy": 0.7,
            "buy": 0.55,
            "neutral": 0.45,
            "sell": 0.35,
            "strong_sell": 0.2
        }
        
        logger.info("Strategy Fusion initialized")
    
    async def fuse_strategies(self, 
                           strategy_signals: Dict[str, List[Dict[str, Any]]],
                           market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        融合多个交易策略的信号
        
        Args:
            strategy_signals: 各策略生成的信号
            market_context: 市场上下文信息
            
        Returns:
            融合后的信号
        """
        try:
            logger.info("Fusing strategy signals...")
            
            # 规范化策略信号
            normalized_signals = self._normalize_signals(strategy_signals)
            
            # 调整策略权重
            if self.adaptive_weights and market_context:
                adjusted_weights = self._adjust_strategy_weights(market_context)
            else:
                adjusted_weights = self.strategy_weights.copy()
            
            # 应用融合方法
            if self.fusion_method == "weighted_average":
                fused_signal = self._weighted_average_fusion(normalized_signals, adjusted_weights)
            elif self.fusion_method == "majority_vote":
                fused_signal = self._majority_vote_fusion(normalized_signals, adjusted_weights)
            elif self.fusion_method == "machine_learning":
                fused_signal = self._ml_based_fusion(normalized_signals, market_context)
            elif self.fusion_method == "hierarchical":
                fused_signal = self._hierarchical_fusion(normalized_signals, market_context)
            else:
                # 默认使用加权平均
                fused_signal = self._weighted_average_fusion(normalized_signals, adjusted_weights)
            
            # 计算信号一致性
            signal_consistency = self._calculate_signal_consistency(normalized_signals)
            
            # 添加元数据
            fused_signal["meta"] = {
                "timestamp": datetime.now().isoformat(),
                "fusion_method": self.fusion_method,
                "strategy_count": len(normalized_signals),
                "adjusted_weights": adjusted_weights,
                "signal_consistency": signal_consistency
            }
            
            logger.info(f"Signal fusion completed: {fused_signal['action']} with strength {fused_signal['strength']:.2f}")
            return fused_signal
            
        except Exception as e:
            error_msg = f"Error in strategy fusion: {str(e)}"
            logger.error(error_msg)
            traceback.print_exc()
            
            # 出错时返回中性信号
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            }
    
    def _normalize_signals(self, strategy_signals: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        将各种策略信号标准化为统一格式
        
        Args:
            strategy_signals: 各策略生成的原始信号
            
        Returns:
            标准化后的信号字典
        """
        normalized = {}
        
        # 处理每个策略类别的信号
        for strategy_type, signals in strategy_signals.items():
            # 跳过不在权重配置中的策略
            if strategy_type not in self.strategy_weights:
                logger.warning(f"Strategy type '{strategy_type}' not in weights configuration, skipping")
                continue
                
            # 如果策略没有产生信号,跳过
            if not signals:
                continue
                
            # 取最新的信号
            latest_signal = signals[-1] if isinstance(signals, list) else signals
            
            # 转换信号到标准格式
            action = latest_signal.get("action", "").lower()
            if not action:
                action = latest_signal.get("signal", "").lower()
            if not action:
                action = latest_signal.get("type", "").lower()
            
            # 如果仍然没有动作,使用默认值
            if not action or action not in ["buy", "sell", "hold"]:
                action = "hold"
            
            # 获取信号强度
            strength = latest_signal.get("strength", 0.5)
            if not isinstance(strength, (int, float)):
                strength = 0.5
            
            # 确保强度在[0,1]范围内
            strength = max(0.0, min(1.0, strength))
            
            # 信号时间戳
            timestamp = latest_signal.get("timestamp", datetime.now().isoformat())
            
            # 标准化信号
            normalized[strategy_type] = {
                "action": action,
                "strength": strength,
                "timestamp": timestamp,
                "details": latest_signal.get("details", {}),
                "symbols": latest_signal.get("symbols", [])
            }
        
        return normalized
    
    def _adjust_strategy_weights(self, market_context: Dict[str, Any]) -> Dict[str, float]:
        """
        根据市场状态调整策略权重
        
        Args:
            market_context: 市场上下文信息
            
        Returns:
            调整后的策略权重
        """
        adjusted_weights = self.strategy_weights.copy()
        
        # 获取市场状态
        market_regime = market_context.get("market_regime", "unknown")
        volatility = market_context.get("volatility", 0.2)
        trend = market_context.get("trend", {})
        trend_strength = trend.get("strength", 0.5) if isinstance(trend, dict) else 0.5
        
        # 根据市场状态调整权重
        if market_regime in ["bull_trending", "transition_bullish"]:
            # 牛市或转向牛市,增加趋势策略权重
            adjusted_weights["momentum"] += self.max_weight_adjustment * 0.5
            adjusted_weights["trend_following"] += self.max_weight_adjustment * 0.5
            adjusted_weights["mean_reversion"] -= self.max_weight_adjustment * 0.5
            adjusted_weights["volatility"] -= self.max_weight_adjustment * 0.5
            
        elif market_regime in ["bear_trending", "transition_bearish"]:
            # 熊市或转向熊市,增加反转和波动率策略权重
            adjusted_weights["mean_reversion"] += self.max_weight_adjustment * 0.5
            adjusted_weights["volatility"] += self.max_weight_adjustment * 0.5
            adjusted_weights["momentum"] -= self.max_weight_adjustment * 0.5
            adjusted_weights["breakout"] -= self.max_weight_adjustment * 0.5
            
        elif market_regime in ["neutral_low_vol"]:
            # 低波动中性市场,增加基本面策略权重
            adjusted_weights["fundamental"] += self.max_weight_adjustment
            adjusted_weights["momentum"] -= self.max_weight_adjustment * 0.5
            adjusted_weights["volatility"] -= self.max_weight_adjustment * 0.5
            
        elif market_regime in ["neutral_high_vol", "bull_volatile", "bear_volatile"]:
            # 高波动市场,增加波动率和反转策略权重
            adjusted_weights["volatility"] += self.max_weight_adjustment
            adjusted_weights["mean_reversion"] += self.max_weight_adjustment * 0.5
            adjusted_weights["trend_following"] -= self.max_weight_adjustment
            adjusted_weights["breakout"] -= self.max_weight_adjustment * 0.5
        
        # 根据趋势强度调整
        if trend_strength > 0.7:
            # 强趋势,增加趋势跟踪权重
            adjusted_weights["trend_following"] += self.max_weight_adjustment * 0.5
            adjusted_weights["mean_reversion"] -= self.max_weight_adjustment * 0.5
        elif trend_strength < 0.3:
            # 弱趋势,增加反转和震荡策略权重
            adjusted_weights["mean_reversion"] += self.max_weight_adjustment * 0.5
            adjusted_weights["trend_following"] -= self.max_weight_adjustment * 0.5
        
        # 标准化权重,确保总和为1
        weight_sum = sum(adjusted_weights.values())
        if weight_sum > 0:
            for strategy in adjusted_weights:
                adjusted_weights[strategy] /= weight_sum
        
        return adjusted_weights
    
    def _weighted_average_fusion(self, 
                              normalized_signals: Dict[str, Dict[str, Any]], 
                              weights: Dict[str, float]) -> Dict[str, Any]:
        """
        使用加权平均方法融合信号
        
        Args:
            normalized_signals: 标准化的策略信号
            weights: 策略权重
            
        Returns:
            融合后的信号
        """
        if not normalized_signals:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "contributing_strategies": []
            }
        
        # 初始化买入和卖出分数
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        
        # 统计每种策略的贡献
        contributing_strategies = []
        
        # 计算加权分数
        for strategy_type, signal in normalized_signals.items():
            # 获取该策略的权重
            weight = weights.get(strategy_type, 0.0)
            if weight <= 0:
                continue
                
            # 累计权重
            total_weight += weight
            
            # 获取动作和强度
            action = signal["action"]
            strength = signal["strength"]
            
            # 累积分数
            if action == "buy":
                buy_score += weight * strength
                contributing_strategies.append({
                    "strategy": strategy_type,
                    "action": action,
                    "strength": strength,
                    "weight": weight,
                    "contribution": weight * strength
                })
            elif action == "sell":
                sell_score += weight * strength
                contributing_strategies.append({
                    "strategy": strategy_type,
                    "action": action,
                    "strength": strength,
                    "weight": weight,
                    "contribution": weight * strength
                })
            else:  # hold
                # 中性信号对买卖双方影响较小
                buy_score += weight * 0.5
                sell_score += weight * 0.5
                contributing_strategies.append({
                    "strategy": strategy_type,
                    "action": action,
                    "strength": strength,
                    "weight": weight,
                    "contribution": weight * 0.5
                })
        
        # 如果没有累积权重,返回中性信号
        if total_weight <= 0:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "contributing_strategies": []
            }
        
        # 标准化分数
        buy_score /= total_weight
        sell_score /= total_weight
        
        # 确定最终动作
        if buy_score > sell_score and buy_score > self.signal_thresholds["buy"]:
            action = "buy"
            strength = buy_score
        elif sell_score > buy_score and sell_score > self.signal_thresholds["buy"]:  # 使用相同阈值
            action = "sell"
            strength = sell_score
        else:
            action = "hold"
            strength = 0.5
        
        # 确定信号强度级别
        signal_level = self._determine_signal_level(action, strength)
        
        return {
            "action": action,
            "strength": strength,
            "level": signal_level,
            "timestamp": datetime.now().isoformat(),
            "contributing_strategies": contributing_strategies,
            "buy_score": buy_score,
            "sell_score": sell_score
        }
    
    def _majority_vote_fusion(self, 
                           normalized_signals: Dict[str, Dict[str, Any]], 
                           weights: Dict[str, float]) -> Dict[str, Any]:
        """
        使用多数投票方法融合信号
        
        Args:
            normalized_signals: 标准化的策略信号
            weights: 策略权重
            
        Returns:
            融合后的信号
        """
        if not normalized_signals:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "votes": {}
            }
        
        # 统计各类动作的权重和
        votes = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        
        # 计算每个策略的投票
        for strategy_type, signal in normalized_signals.items():
            # 获取该策略的权重
            weight = weights.get(strategy_type, 0.0)
            if weight <= 0:
                continue
                
            # 获取动作
            action = signal["action"]
            
            # 累积投票
            if action in votes:
                votes[action] += weight
        
        # 找出得票最多的动作
        max_vote_action = max(votes, key=votes.get)
        max_vote_count = votes[max_vote_action]
        
        # 计算总投票数
        total_votes = sum(votes.values())
        
        # 如果没有投票,返回中性信号
        if total_votes <= 0:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "votes": votes
            }
        
        # 计算强度(支持率)
        strength = max_vote_count / total_votes
        
        # 如果最高票是持有或支持率不够高,返回持有
        if max_vote_action == "hold" or strength < self.signal_thresholds["buy"]:
            action = "hold"
            strength = 0.5
        else:
            action = max_vote_action
        
        # 确定信号强度级别
        signal_level = self._determine_signal_level(action, strength)
        
        return {
            "action": action,
            "strength": strength,
            "level": signal_level,
            "timestamp": datetime.now().isoformat(),
            "votes": votes,
            "vote_ratio": strength
        }
    
    def _ml_based_fusion(self, 
                       normalized_signals: Dict[str, Dict[str, Any]], 
                       market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用机器学习方法融合信号(简化版本)
        
        Args:
            normalized_signals: 标准化的策略信号
            market_context: 市场上下文信息
            
        Returns:
            融合后的信号
        """
        # 由于ML融合需要训练模型,这里提供一个简化版本
        # 实际实现中,可以使用预训练的模型或在线学习方法
        
        # 在没有ML模型的情况下,退化为加权平均方法
        logger.info("ML-based fusion not fully implemented, falling back to weighted average")
        return self._weighted_average_fusion(normalized_signals, self.strategy_weights)
    
    def _hierarchical_fusion(self, 
                          normalized_signals: Dict[str, Dict[str, Any]], 
                          market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用分层融合方法融合信号
        
        Args:
            normalized_signals: 标准化的策略信号
            market_context: 市场上下文信息
            
        Returns:
            融合后的信号
        """
        if not normalized_signals:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "layers": {}
            }
        
        # 策略分组
        strategy_groups = {
            "technical": ["momentum", "mean_reversion", "trend_following", "breakout"],
            "fundamental": ["fundamental"],
            "market_condition": ["volatility", "sentiment"]
        }
        
        # 第一层:在每个组内融合
        group_signals = {}
        
        for group_name, strategies in strategy_groups.items():
            # 提取该组中的策略信号
            group_normalized_signals = {
                strategy: signal for strategy, signal in normalized_signals.items() 
                if strategy in strategies
            }
            
            # 如果组内没有信号,跳过
            if not group_normalized_signals:
                continue
                
            # 提取组内策略权重并标准化
            group_weights = {
                strategy: self.strategy_weights.get(strategy, 0.0) 
                for strategy in group_normalized_signals
            }
            weight_sum = sum(group_weights.values())
            if weight_sum > 0:
                group_weights = {s: w / weight_sum for s, w in group_weights.items()}
            
            # 在组内融合
            group_signal = self._weighted_average_fusion(group_normalized_signals, group_weights)
            group_signals[group_name] = group_signal
        
        # 第二层:融合组信号
        # 组权重
        group_weights = {
            "technical": 0.6,
            "fundamental": 0.25,
            "market_condition": 0.15
        }
        
        # 最终融合结果
        final_buy_score = 0.0
        final_sell_score = 0.0
        total_weight = 0.0
        
        for group_name, signal in group_signals.items():
            weight = group_weights.get(group_name, 0.0)
            if weight <= 0:
                continue
                
            total_weight += weight
            
            if signal["action"] == "buy":
                final_buy_score += weight * signal["strength"]
            elif signal["action"] == "sell":
                final_sell_score += weight * signal["strength"]
            else:  # hold
                final_buy_score += weight * 0.5
                final_sell_score += weight * 0.5
        
        # 如果没有组信号,返回中性信号
        if total_weight <= 0:
            return {
                "action": "hold",
                "strength": 0.5,
                "timestamp": datetime.now().isoformat(),
                "layers": {"groups": group_signals}
            }
        
        # 标准化分数
        final_buy_score /= total_weight
        final_sell_score /= total_weight
        
        # 确定最终动作
        if final_buy_score > final_sell_score and final_buy_score > self.signal_thresholds["buy"]:
            action = "buy"
            strength = final_buy_score
        elif final_sell_score > final_buy_score and final_sell_score > self.signal_thresholds["buy"]:
            action = "sell"
            strength = final_sell_score
        else:
            action = "hold"
            strength = 0.5
        
        # 确定信号强度级别
        signal_level = self._determine_signal_level(action, strength)
        
        return {
            "action": action,
            "strength": strength,
            "level": signal_level,
            "timestamp": datetime.now().isoformat(),
            "layers": {
                "groups": group_signals
            },
            "buy_score": final_buy_score,
            "sell_score": final_sell_score
        }
    
    def _calculate_signal_consistency(self, normalized_signals: Dict[str, Dict[str, Any]]) -> float:
        """
        计算信号一致性程度
        
        Args:
            normalized_signals: 标准化的策略信号
            
        Returns:
            一致性得分 (0-1)
        """
        if not normalized_signals:
            return 1.0  # 空信号集默认一致
            
        # 统计各类动作的数量
        action_counts = {"buy": 0, "sell": 0, "hold": 0}
        
        for signal in normalized_signals.values():
            action = signal["action"]
            if action in action_counts:
                action_counts[action] += 1
        
        # 计算总信号数
        total_signals = sum(action_counts.values())
        
        if total_signals == 0:
            return 1.0
        
        # 计算最大动作比例
        max_action_ratio = max(action_counts.values()) / total_signals
        
        return max_action_ratio
    
    def _determine_signal_level(self, action: str, strength: float) -> str:
        """
        根据动作和强度确定信号级别
        
        Args:
            action: 信号动作
            strength: 信号强度
            
        Returns:
            信号级别
        """
        if action == "buy":
            if strength >= self.signal_thresholds["strong_buy"]:
                return "strong_buy"
            else:
                return "buy"
        elif action == "sell":
            if strength <= self.signal_thresholds["strong_sell"]:
                return "strong_sell"
            else:
                return "sell"
        else:  # hold
            if strength > self.signal_thresholds["neutral"]:
                return "weak_buy"
            elif strength < (1 - self.signal_thresholds["neutral"]):
                return "weak_sell"
            else:
                return "neutral"
    
    def update_strategy_performance(self, performance_data: Dict[str, Any]):
        """
        更新策略性能数据
        
        Args:
            performance_data: 包含各策略性能指标的数据
        """
        # 更新性能跟踪
        for strategy, metrics in performance_data.items():
            if strategy in self.strategy_weights:
                self.strategy_performance[strategy] = metrics
        
        # 如果启用自适应权重,可以根据性能自动调整权重
        if self.adaptive_weights and self.strategy_performance:
            self._adjust_weights_by_performance()
    
    def _adjust_weights_by_performance(self):
        """根据策略性能调整权重"""
        # 这是一个简化的方法,实际实现可能更复杂
        
        # 提取策略夏普比率或其他绩效指标
        performance_scores = {}
        
        for strategy, metrics in self.strategy_performance.items():
            # 使用夏普比率作为性能指标
            sharpe = metrics.get("sharpe_ratio", 0)
            
            # 避免负夏普比率导致权重倒置
            performance_scores[strategy] = max(0.1, sharpe)
        
        # 如果没有足够的性能数据,不调整
        if len(performance_scores) < 2:
            return
        
        # 计算总分
        total_score = sum(performance_scores.values())
        
        if total_score <= 0:
            return
        
        # 计算新权重
        new_weights = {}
        for strategy, score in performance_scores.items():
            new_weight = score / total_score
            
            # 限制单个策略权重变化
            old_weight = self.strategy_weights.get(strategy, 0)
            max_change = self.max_weight_adjustment
            
            # 确保权重变化在允许范围内
            if new_weight > old_weight:
                new_weights[strategy] = min(new_weight, old_weight + max_change)
            else:
                new_weights[strategy] = max(new_weight, old_weight - max_change)
        
        # 对于没有性能数据的策略,保持原权重
        for strategy in self.strategy_weights:
            if strategy not in new_weights:
                new_weights[strategy] = self.strategy_weights[strategy]
        
        # 标准化权重确保总和为1
        weight_sum = sum(new_weights.values())
        if weight_sum > 0:
            self.strategy_weights = {s: w / weight_sum for s, w in new_weights.items()}
            
        logger.info(f"Strategy weights adjusted based on performance: {self.strategy_weights}") 
