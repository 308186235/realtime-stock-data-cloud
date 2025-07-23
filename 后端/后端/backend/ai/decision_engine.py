import numpy as np
import pandas as pd
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union, Optional, Tuple
import traceback

logger = logging.getLogger("DecisionEngine")

class DecisionEngine:
    """
    决策引擎 - 负责整合市场分析,风险评估和策略信号,生成最终交易决策
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化决策引擎
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 决策因素权重
        self.factor_weights = {
            "market_regime": 0.25,      # 市场状态
            "trend": 0.20,              # 趋势分析
            "sentiment": 0.10,          # 市场情绪
            "fundamental": 0.15,        # 基本面
            "technical": 0.20,          # 技术指标
            "risk": 0.10                # 风险评估
        }
        
        # 决策历史
        self.decision_history = []
        
        # 置信度阈值
        self.confidence_thresholds = {
            "execute": 0.65,            # 执行交易的最低置信度
            "alert": 0.50               # 发出提醒的最低置信度
        }
        
        # 决策偏好
        self.decision_preferences = {
            "max_open_positions": 5,    # 最大持仓数量
            "min_position_spacing": 2,  # 最小开仓间隔(天)
            "profit_target": 0.15,      # 目标利润
            "adaptive_sizing": True     # 是否启用自适应仓位
        }
        
        logger.info("Decision Engine initialized")
    
    async def make_decision(self, 
                          market_analysis: Dict[str, Any], 
                          risk_assessment: Dict[str, Any], 
                          strategy_signals: Dict[str, Any],
                          portfolio_state: Dict[str, Any] = None,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成交易决策
        
        Args:
            market_analysis: 市场分析结果
            risk_assessment: 风险评估结果
            strategy_signals: 策略信号
            portfolio_state: 当前投资组合状态
            context: 额外上下文信息
            
        Returns:
            决策结果
        """
        try:
            logger.info("Generating trading decision...")
            
            # 创建决策上下文
            decision_context = self._build_decision_context(
                market_analysis, risk_assessment, strategy_signals, 
                portfolio_state, context
            )
            
            # 评估各策略信号
            evaluated_signals = self._evaluate_strategy_signals(
                strategy_signals, market_analysis, risk_assessment
            )
            
            # 检查决策约束条件
            constraints_check = self._check_decision_constraints(
                evaluated_signals, portfolio_state, decision_context
            )
            
            # 如果违反约束,可能调整决策
            if not constraints_check["passed"]:
                logger.info(f"Decision constraints not met: {constraints_check['reason']}")
                if constraints_check.get("alternative_action"):
                    decision = constraints_check["alternative_action"]
                else:
                    decision = self._generate_hold_decision(
                        "Constraints not met: " + constraints_check["reason"],
                        evaluated_signals
                    )
                    
            else:
                # 生成最终决策
                decision = self._generate_final_decision(
                    evaluated_signals, 
                    market_analysis, 
                    risk_assessment,
                    portfolio_state,
                    decision_context
                )
            
            # 记录决策
            self._record_decision(decision)
            
            logger.info(f"Decision generated: {decision['action']} with confidence {decision['confidence']:.2f}")
            return decision
            
        except Exception as e:
            error_msg = f"Error generating decision: {str(e)}"
            logger.error(error_msg)
            traceback.print_exc()
            
            # 出错时返回持有决策
            return {
                "action": "hold",
                "confidence": 0.0,
                "reason": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": True
            }
    
    def _build_decision_context(self, 
                              market_analysis: Dict[str, Any],
                              risk_assessment: Dict[str, Any],
                              strategy_signals: Dict[str, Any],
                              portfolio_state: Dict[str, Any] = None,
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """构建决策上下文"""
        # 合并所有上下文信息
        decision_context = {
            "timestamp": datetime.now().isoformat(),
            "market_regime": market_analysis.get("market_regime", "unknown"),
            "trend": market_analysis.get("trend", {}),
            "risk_level": risk_assessment.get("risk_level", "medium"),
            "strategy_consensus": self._calculate_strategy_consensus(strategy_signals),
            "recent_decisions": self._get_recent_decisions(5)
        }
        
        # 添加投资组合状态
        if portfolio_state:
            decision_context["portfolio"] = {
                "open_positions": portfolio_state.get("open_positions", 0),
                "cash_available": portfolio_state.get("cash_available", 0),
                "total_value": portfolio_state.get("total_value", 0),
                "current_allocation": portfolio_state.get("allocation", {})
            }
        
        # 添加额外上下文
        if context:
            for key, value in context.items():
                if key not in decision_context:
                    decision_context[key] = value
        
        return decision_context
    
    def _evaluate_strategy_signals(self,
                                 strategy_signals: Dict[str, Any],
                                 market_analysis: Dict[str, Any],
                                 risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """评估策略信号"""
        # 提取策略信号
        signals = strategy_signals.get("signals", {})
        
        # 评估结果
        evaluated_signals = {
            "buy_signals": [],
            "sell_signals": [],
            "hold_signals": [],
            "strongest_buy": None,
            "strongest_sell": None,
            "consensus": "hold",
            "consensus_strength": 0.0
        }
        
        # 市场状态和风险调整因子
        market_regime = market_analysis.get("market_regime", "unknown")
        risk_level = risk_assessment.get("risk_level", "medium")
        
        # 基于市场状态的信号调整因子
        regime_factors = {
            "bull_trending": {"buy": 1.2, "sell": 0.8},
            "bull_volatile": {"buy": 1.0, "sell": 1.0},
            "bear_trending": {"buy": 0.7, "sell": 1.3},
            "bear_volatile": {"buy": 0.6, "sell": 1.2},
            "neutral_low_vol": {"buy": 1.0, "sell": 1.0},
            "neutral_high_vol": {"buy": 0.8, "sell": 0.8},
            "transition_bullish": {"buy": 1.1, "sell": 0.9},
            "transition_bearish": {"buy": 0.8, "sell": 1.1}
        }
        
        # 基于风险级别的信号调整因子
        risk_factors = {
            "low": {"buy": 1.2, "sell": 0.9},
            "medium": {"buy": 1.0, "sell": 1.0},
            "high": {"buy": 0.7, "sell": 1.2},
            "extreme": {"buy": 0.4, "sell": 1.4}
        }
        
        # 获取调整因子
        market_factor = regime_factors.get(market_regime, {"buy": 1.0, "sell": 1.0})
        risk_factor = risk_factors.get(risk_level, {"buy": 1.0, "sell": 1.0})
        
        # 处理各个策略信号
        buy_scores = []
        sell_scores = []
        
        for strategy_name, signal in signals.items():
            signal_type = signal.get("type", "hold").lower()
            signal_strength = signal.get("strength", 0.5)
            
            # 根据市场状态和风险调整信号强度
            if signal_type == "buy":
                adjusted_strength = signal_strength * market_factor["buy"] * risk_factor["buy"]
                adjusted_strength = min(1.0, adjusted_strength)  # 上限为1.0
                
                buy_scores.append({
                    "strategy": strategy_name,
                    "original_strength": signal_strength,
                    "adjusted_strength": adjusted_strength,
                    "reason": signal.get("reason", "")
                })
                
            elif signal_type == "sell":
                adjusted_strength = signal_strength * market_factor["sell"] * risk_factor["sell"]
                adjusted_strength = min(1.0, adjusted_strength)  # 上限为1.0
                
                sell_scores.append({
                    "strategy": strategy_name,
                    "original_strength": signal_strength,
                    "adjusted_strength": adjusted_strength,
                    "reason": signal.get("reason", "")
                })
        
        # 排序并找出最强信号
        if buy_scores:
            buy_scores.sort(key=lambda x: x["adjusted_strength"], reverse=True)
            evaluated_signals["buy_signals"] = buy_scores
            evaluated_signals["strongest_buy"] = buy_scores[0]
        
        if sell_scores:
            sell_scores.sort(key=lambda x: x["adjusted_strength"], reverse=True)
            evaluated_signals["sell_signals"] = sell_scores
            evaluated_signals["strongest_sell"] = sell_scores[0]
        
        # 计算买卖共识
        avg_buy_strength = np.mean([s["adjusted_strength"] for s in buy_scores]) if buy_scores else 0
        avg_sell_strength = np.mean([s["adjusted_strength"] for s in sell_scores]) if sell_scores else 0
        
        # 共识方向
        if avg_buy_strength > 0.6 and avg_buy_strength > avg_sell_strength * 1.5:
            evaluated_signals["consensus"] = "buy"
            evaluated_signals["consensus_strength"] = avg_buy_strength
        elif avg_sell_strength > 0.6 and avg_sell_strength > avg_buy_strength * 1.5:
            evaluated_signals["consensus"] = "sell"
            evaluated_signals["consensus_strength"] = avg_sell_strength
        else:
            evaluated_signals["consensus"] = "hold"
            evaluated_signals["consensus_strength"] = 0.5
        
        return evaluated_signals
    
    def _check_decision_constraints(self,
                                  evaluated_signals: Dict[str, Any],
                                  portfolio_state: Dict[str, Any],
                                  decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """检查决策约束条件"""
        constraints = {
            "passed": True,
            "reason": "",
            "alternative_action": None
        }
        
        # 如果没有投资组合状态信息,无法进行约束检查
        if not portfolio_state:
            return constraints
        
        # 检查最大持仓数量约束
        open_positions = portfolio_state.get("open_positions", 0)
        max_positions = self.decision_preferences["max_open_positions"]
        
        if evaluated_signals["consensus"] == "buy" and open_positions >= max_positions:
            constraints["passed"] = False
            constraints["reason"] = f"Maximum open positions limit reached ({max_positions})"
            
        # 检查最小开仓间隔约束
        recent_decisions = decision_context.get("recent_decisions", [])
        min_spacing = self.decision_preferences["min_position_spacing"]
        
        if evaluated_signals["consensus"] == "buy" and recent_decisions:
            last_buy = None
            for decision in recent_decisions:
                if decision["action"] == "buy" and decision.get("executed", False):
                    last_buy = datetime.fromisoformat(decision["timestamp"])
                    break
            
            if last_buy:
                days_since_last_buy = (datetime.now() - last_buy).days
                if days_since_last_buy < min_spacing:
                    constraints["passed"] = False
                    constraints["reason"] = f"Minimum position spacing not met ({days_since_last_buy}/{min_spacing} days)"
        
        # 检查可用资金约束
        cash_available = portfolio_state.get("cash_available", 0)
        if evaluated_signals["consensus"] == "buy" and cash_available <= 0:
            constraints["passed"] = False
            constraints["reason"] = "Insufficient funds available"
        
        # 检查持仓时间约束 (如果需要强制持有一段时间)
        # 这里可以添加更多约束...
        
        return constraints
    
    def _generate_final_decision(self,
                               evaluated_signals: Dict[str, Any],
                               market_analysis: Dict[str, Any],
                               risk_assessment: Dict[str, Any],
                               portfolio_state: Dict[str, Any],
                               decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终决策"""
        # 默认为持有决策
        decision = {
            "action": "hold",
            "confidence": 0.5,
            "timestamp": datetime.now().isoformat(),
            "factors": {},
            "explanation": [],
            "position_size": 0.0,
            "execute": False
        }
        
        # 获取共识和最强信号
        consensus = evaluated_signals["consensus"]
        consensus_strength = evaluated_signals["consensus_strength"]
        strongest_buy = evaluated_signals.get("strongest_buy")
        strongest_sell = evaluated_signals.get("strongest_sell")
        
        # 基于共识方向确定初步决策
        if consensus == "buy" and strongest_buy:
            decision["action"] = "buy"
            decision["confidence"] = strongest_buy["adjusted_strength"]
            decision["strategy"] = strongest_buy["strategy"]
            decision["factors"]["strategy_signal"] = strongest_buy
            decision["explanation"].append(f"Strong buy signal from {strongest_buy['strategy']} strategy")
            
        elif consensus == "sell" and strongest_sell:
            decision["action"] = "sell"
            decision["confidence"] = strongest_sell["adjusted_strength"]
            decision["strategy"] = strongest_sell["strategy"]
            decision["factors"]["strategy_signal"] = strongest_sell
            decision["explanation"].append(f"Strong sell signal from {strongest_sell['strategy']} strategy")
        
        # 整合市场状态影响
        market_regime = market_analysis.get("market_regime", "unknown")
        trend = market_analysis.get("trend", {})
        
        # 记录市场因素
        decision["factors"]["market_regime"] = market_regime
        decision["factors"]["trend"] = trend
        
        # 调整置信度基于市场状态
        if market_regime in ["bull_trending", "transition_bullish"] and decision["action"] == "buy":
            decision["confidence"] = min(1.0, decision["confidence"] * 1.1)
            decision["explanation"].append(f"Confidence boosted by favorable market regime ({market_regime})")
            
        elif market_regime in ["bear_trending", "transition_bearish"] and decision["action"] == "sell":
            decision["confidence"] = min(1.0, decision["confidence"] * 1.1)
            decision["explanation"].append(f"Confidence boosted by favorable market regime ({market_regime})")
            
        elif market_regime in ["neutral_high_vol", "bull_volatile", "bear_volatile"]:
            decision["confidence"] *= 0.9
            decision["explanation"].append(f"Confidence reduced due to high volatility regime ({market_regime})")
        
        # 整合风险评估
        risk_level = risk_assessment.get("risk_level", "medium")
        decision["factors"]["risk_level"] = risk_level
        
        # 基于风险调整决策
        if risk_level in ["high", "extreme"] and decision["action"] == "buy":
            decision["confidence"] *= 0.8
            decision["explanation"].append(f"Confidence reduced due to high risk level ({risk_level})")
            
        elif risk_level == "low" and decision["action"] == "buy":
            decision["confidence"] = min(1.0, decision["confidence"] * 1.1)
            decision["explanation"].append("Confidence boosted by low risk environment")
        
        # 确定执行标志
        if decision["confidence"] >= self.confidence_thresholds["execute"]:
            decision["execute"] = True
            
            # 确定仓位大小
            if decision["action"] == "buy":
                position_size = self._calculate_position_size(
                    decision["confidence"], 
                    risk_assessment, 
                    portfolio_state
                )
                decision["position_size"] = position_size
        
        # 确定是否需要提醒
        if not decision["execute"] and decision["confidence"] >= self.confidence_thresholds["alert"]:
            decision["alert"] = True
        
        return decision
    
    def _generate_hold_decision(self, reason: str, evaluated_signals: Dict[str, Any]) -> Dict[str, Any]:
        """生成持有决策"""
        return {
            "action": "hold",
            "confidence": 0.5,
            "timestamp": datetime.now().isoformat(),
            "factors": {
                "evaluated_signals": evaluated_signals
            },
            "explanation": [reason],
            "position_size": 0.0,
            "execute": False
        }
    
    def _calculate_strategy_consensus(self, strategy_signals: Dict[str, Any]) -> Dict[str, Any]:
        """计算策略共识"""
        signals = strategy_signals.get("signals", {})
        
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        # 统计各类信号数量
        for signal in signals.values():
            signal_type = signal.get("type", "hold").lower()
            
            if signal_type == "buy":
                buy_count += 1
            elif signal_type == "sell":
                sell_count += 1
            else:
                hold_count += 1
        
        total_signals = buy_count + sell_count + hold_count
        
        if total_signals == 0:
            return {
                "direction": "hold",
                "strength": 0.0,
                "buy_ratio": 0.0,
                "sell_ratio": 0.0,
                "hold_ratio": 0.0
            }
        
        # 计算比例
        buy_ratio = buy_count / total_signals
        sell_ratio = sell_count / total_signals
        hold_ratio = hold_count / total_signals
        
        # 确定共识方向
        if buy_ratio > 0.5 and buy_ratio > sell_ratio:
            direction = "buy"
            strength = buy_ratio
        elif sell_ratio > 0.5 and sell_ratio > buy_ratio:
            direction = "sell"
            strength = sell_ratio
        else:
            direction = "hold"
            strength = hold_ratio
        
        return {
            "direction": direction,
            "strength": strength,
            "buy_ratio": buy_ratio,
            "sell_ratio": sell_ratio,
            "hold_ratio": hold_ratio
        }
    
    def _get_recent_decisions(self, count: int = 5) -> List[Dict[str, Any]]:
        """获取最近的决策历史"""
        return self.decision_history[-count:] if len(self.decision_history) >= count else self.decision_history.copy()
    
    def _calculate_position_size(self, 
                               confidence: float, 
                               risk_assessment: Dict[str, Any], 
                               portfolio_state: Dict[str, Any]) -> float:
        """计算仓位大小"""
        # 默认仓位比例
        base_position = 0.1  # 10%仓位
        
        # 如果启用自适应仓位
        if self.decision_preferences["adaptive_sizing"]:
            # 基于置信度调整
            confidence_factor = (confidence - 0.5) * 2  # 映射到0-1区间
            confidence_factor = max(0, confidence_factor)  # 确保非负
            
            # 基于风险调整
            risk_level = risk_assessment.get("risk_level", "medium")
            risk_factor = {
                "low": 1.5,
                "medium": 1.0,
                "high": 0.7,
                "extreme": 0.4
            }.get(risk_level, 1.0)
            
            # 计算调整后的仓位
            adjusted_position = base_position * (1 + confidence_factor) * risk_factor
            
            # 设置上限
            max_position = 0.25  # 最大25%仓位
            position_size = min(adjusted_position, max_position)
        else:
            position_size = base_position
        
        # 计算绝对金额
        if portfolio_state:
            cash_available = portfolio_state.get("cash_available", 0)
            position_amount = cash_available * position_size
        else:
            position_amount = 0
        
        return position_size
    
    def _record_decision(self, decision: Dict[str, Any]):
        """记录决策历史"""
        # 添加到历史记录
        self.decision_history.append(decision)
        
        # 限制历史记录长度
        max_history = 100
        if len(self.decision_history) > max_history:
            self.decision_history = self.decision_history[-max_history:] 
