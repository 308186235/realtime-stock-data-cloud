"""
增强版Agent系统集成器
整合所有AI组件，提供统一的智能交易服务
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

from .enhanced_decision_engine import EnhancedDecisionEngine, TradingDecision
from .enhanced_learning_manager import EnhancedLearningManager, Experience
from .enhanced_risk_manager import EnhancedRiskManager, RiskAlert
from .realtime_data_integrator import RealtimeDataIntegrator, MarketData

logger = logging.getLogger("EnhancedAgentSystem")

class EnhancedAgentSystem:
    """
    增强版Agent系统
    集成决策引擎、学习管理、风险控制和实时数据
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化增强版Agent系统
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 初始化各个组件
        self.decision_engine = EnhancedDecisionEngine(
            self.config.get("decision_engine", {})
        )
        
        self.learning_manager = EnhancedLearningManager(
            self.config.get("learning_manager", {})
        )
        
        self.risk_manager = EnhancedRiskManager(
            self.config.get("risk_manager", {})
        )
        
        self.data_integrator = RealtimeDataIntegrator(
            self.config.get("data_integrator", {})
        )
        
        # 系统状态
        self.system_state = {
            "active": False,
            "last_decision_time": None,
            "total_decisions": 0,
            "successful_decisions": 0,
            "system_performance": {
                "accuracy": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
        }
        
        # 决策历史
        self.decision_history = []
        
        logger.info("Enhanced Agent System initialized")
    
    async def start(self):
        """启动增强版Agent系统"""
        try:
            logger.info("Starting Enhanced Agent System...")
            
            # 启动数据集成器
            await self.data_integrator.start()
            
            # 设置系统为活跃状态
            self.system_state["active"] = True
            
            logger.info("Enhanced Agent System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting Enhanced Agent System: {e}")
            raise
    
    async def stop(self):
        """停止增强版Agent系统"""
        try:
            logger.info("Stopping Enhanced Agent System...")
            
            # 停止数据集成器
            await self.data_integrator.stop()
            
            # 关闭学习管理器
            self.learning_manager.shutdown()
            
            # 设置系统为非活跃状态
            self.system_state["active"] = False
            
            logger.info("Enhanced Agent System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Enhanced Agent System: {e}")
    
    async def make_trading_decision(self, 
                                  symbol: str, 
                                  portfolio_data: Dict[str, Any] = None,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成交易决策
        
        Args:
            symbol: 股票代码
            portfolio_data: 投资组合数据
            context: 额外上下文
            
        Returns:
            交易决策结果
        """
        try:
            if not self.system_state["active"]:
                return {"error": "System not active"}
            
            logger.info(f"Making trading decision for {symbol}...")
            
            # 1. 获取实时市场数据
            market_data = await self._get_market_data(symbol)
            if not market_data:
                return {"error": f"Failed to get market data for {symbol}"}
            
            # 2. 进行风险评估
            risk_assessment = await self.risk_manager.assess_comprehensive_risk(
                market_data=self._format_market_data_for_risk(market_data),
                portfolio_data=portfolio_data or {},
                context=context
            )
            
            # 3. 检查风险预警
            risk_alerts = risk_assessment.get("risk_alerts", [])
            if any(alert.get("risk_level") == "critical" for alert in risk_alerts):
                return {
                    "action": "hold",
                    "reason": "Critical risk detected",
                    "risk_alerts": risk_alerts,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 4. 生成交易决策
            decision = await self.decision_engine.make_decision(
                market_data=self._format_market_data_for_decision(market_data),
                portfolio_state=portfolio_data or {},
                context=context
            )
            
            # 5. 应用风险控制
            final_decision = await self._apply_risk_controls(decision, risk_assessment)
            
            # 6. 记录决策
            await self._record_decision(final_decision, market_data, risk_assessment)
            
            # 7. 更新系统状态
            self._update_system_state(final_decision)
            
            logger.info(f"Trading decision completed for {symbol}: {final_decision.action.value}")
            
            return {
                "symbol": symbol,
                "action": final_decision.action.value,
                "quantity": final_decision.quantity,
                "price": final_decision.price,
                "confidence": final_decision.confidence,
                "reasoning": final_decision.reasoning,
                "risk_score": final_decision.risk_score,
                "expected_return": final_decision.expected_return,
                "stop_loss": final_decision.stop_loss,
                "take_profit": final_decision.take_profit,
                "timestamp": final_decision.timestamp.isoformat(),
                "risk_assessment": risk_assessment,
                "metadata": final_decision.metadata
            }
            
        except Exception as e:
            logger.error(f"Error making trading decision for {symbol}: {e}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_market_data(self, symbol: str) -> Optional[MarketData]:
        """获取市场数据"""
        try:
            return await self.data_integrator.get_market_data(symbol)
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    def _format_market_data_for_risk(self, market_data: MarketData) -> Dict[str, Any]:
        """为风险评估格式化市场数据"""
        return {
            "symbol": market_data.symbol,
            "current_price": market_data.price,
            "volatility": 0.20,  # 默认波动率，实际应从历史数据计算
            "volume": market_data.volume,
            "market_cap": market_data.market_cap,
            "beta": 1.0,  # 默认Beta，实际应从数据源获取
            "market_correlation": 0.7,  # 默认市场相关性
            "market_regime": "normal"  # 默认市场状态
        }
    
    def _format_market_data_for_decision(self, market_data: MarketData) -> Dict[str, Any]:
        """为决策引擎格式化市场数据"""
        return {
            "symbol": market_data.symbol,
            "current_price": market_data.price,
            "volume": market_data.volume,
            "volatility": 0.20,  # 默认波动率
            "prices": [  # 模拟价格历史
                {
                    "close": market_data.price,
                    "high": market_data.high or market_data.price * 1.02,
                    "low": market_data.low or market_data.price * 0.98,
                    "open": market_data.open or market_data.price,
                    "volume": market_data.volume
                }
            ],
            "fundamental": {
                "pe_ratio": market_data.pe_ratio or 15.0,
                "pb_ratio": 1.5,
                "roe": 0.12,
                "debt_ratio": 0.3
            },
            "sentiment": {
                "news_sentiment": 0.0,
                "social_sentiment": 0.0,
                "analyst_rating": 0.0
            }
        }
    
    async def _apply_risk_controls(self, 
                                 decision: TradingDecision, 
                                 risk_assessment: Dict[str, Any]) -> TradingDecision:
        """应用风险控制"""
        try:
            # 获取风险控制建议
            risk_controls = risk_assessment.get("risk_controls", {})
            
            # 调整仓位大小
            position_sizing = risk_controls.get("position_sizing", {})
            if position_sizing.get("action") == "reduce_positions":
                reduction_factor = 1.0 - position_sizing.get("target_reduction", 0.0)
                decision.quantity = int(decision.quantity * reduction_factor)
            
            # 调整止损
            stop_loss_control = risk_controls.get("stop_loss", {})
            if stop_loss_control.get("strategy") == "volatility_based":
                stop_distance = stop_loss_control.get("stop_distance", 0.05)
                if decision.action.value == "buy":
                    decision.stop_loss = decision.price * (1 - stop_distance)
                elif decision.action.value == "sell":
                    decision.stop_loss = decision.price * (1 + stop_distance)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error applying risk controls: {e}")
            return decision
    
    async def _record_decision(self, 
                             decision: TradingDecision, 
                             market_data: MarketData,
                             risk_assessment: Dict[str, Any]):
        """记录决策"""
        try:
            # 记录到决策历史
            decision_record = {
                "decision": decision,
                "market_data": market_data,
                "risk_assessment": risk_assessment,
                "timestamp": datetime.now()
            }
            
            self.decision_history.append(decision_record)
            
            # 限制历史长度
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-500:]
            
            # 创建学习经验
            experience = Experience(
                state={
                    "market_data": self._format_market_data_for_decision(market_data),
                    "risk_score": risk_assessment.get("overall_risk_score", 0.5)
                },
                action={
                    "action": decision.action.value,
                    "quantity": decision.quantity,
                    "confidence": decision.confidence
                },
                reward=0.0,  # 将在交易结果确定后更新
                next_state={},  # 将在下次决策时更新
                done=False,
                timestamp=datetime.now(),
                metadata={
                    "symbol": decision.symbol,
                    "price": decision.price,
                    "risk_score": decision.risk_score
                }
            )
            
            # 添加到学习管理器
            await self.learning_manager.add_experience(experience)
            
        except Exception as e:
            logger.error(f"Error recording decision: {e}")
    
    def _update_system_state(self, decision: TradingDecision):
        """更新系统状态"""
        try:
            self.system_state["last_decision_time"] = datetime.now()
            self.system_state["total_decisions"] += 1
            
            # 更新性能指标（简化版）
            if decision.confidence > 0.7:
                self.system_state["successful_decisions"] += 1
            
            # 计算准确率
            if self.system_state["total_decisions"] > 0:
                accuracy = (self.system_state["successful_decisions"] / 
                          self.system_state["total_decisions"])
                self.system_state["system_performance"]["accuracy"] = accuracy
            
        except Exception as e:
            logger.error(f"Error updating system state: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 获取各组件状态
            learning_progress = await self.learning_manager.get_learning_progress()
            risk_summary = await self.risk_manager.get_risk_summary()
            data_stats = self.data_integrator.get_stats()
            
            return {
                "system_state": self.system_state,
                "learning_progress": learning_progress,
                "risk_summary": risk_summary,
                "data_stats": data_stats,
                "decision_engine_performance": self.decision_engine.get_performance_metrics(),
                "recent_decisions": len(self.decision_history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def optimize_system(self) -> Dict[str, Any]:
        """优化系统性能"""
        try:
            logger.info("Starting system optimization...")
            
            # 优化学习管理器超参数
            learning_optimization = await self.learning_manager.optimize_hyperparameters()
            
            # 更新决策引擎模型权重
            if self.system_state["total_decisions"] > 100:
                # 基于历史性能调整权重
                performance = self.system_state["system_performance"]
                if performance["accuracy"] > 0.7:
                    # 性能良好，增加技术分析权重
                    new_weights = {
                        "technical_analysis": 0.30,
                        "fundamental_analysis": 0.20,
                        "sentiment_analysis": 0.15,
                        "momentum_model": 0.15,
                        "mean_reversion": 0.10,
                        "volatility_model": 0.10
                    }
                    self.decision_engine.update_model_weights(new_weights)
            
            optimization_result = {
                "status": "completed",
                "learning_optimization": learning_optimization,
                "model_weights_updated": True,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("System optimization completed")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing system: {e}")
            return {"status": "error", "message": str(e)}
