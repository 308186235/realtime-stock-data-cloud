"""
增强版风险管理器
提供更全面和智能的风险控制功能，包括动态风险调整、多层风险预警和智能止损
"""

import numpy as np
import pandas as pd
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union, Optional, Tuple
import traceback
from dataclasses import dataclass, asdict
from enum import Enum
import math

logger = logging.getLogger("EnhancedRiskManager")

class RiskLevel(Enum):
    """风险等级枚举"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

class RiskType(Enum):
    """风险类型枚举"""
    MARKET = "market"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    OPERATIONAL = "operational"
    CONCENTRATION = "concentration"
    VOLATILITY = "volatility"

@dataclass
class RiskAlert:
    """风险预警数据类"""
    risk_type: RiskType
    risk_level: RiskLevel
    message: str
    current_value: float
    threshold: float
    recommendation: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class PositionRisk:
    """仓位风险数据类"""
    symbol: str
    position_size: float
    market_value: float
    var_1d: float
    var_5d: float
    max_drawdown: float
    beta: float
    correlation_risk: float
    liquidity_score: float
    risk_score: float

class EnhancedRiskManager:
    """
    增强版风险管理器
    提供全面的风险评估和控制功能
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化增强版风险管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 风险阈值配置
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: 0.05,
            RiskLevel.LOW: 0.10,
            RiskLevel.MEDIUM: 0.20,
            RiskLevel.HIGH: 0.35,
            RiskLevel.VERY_HIGH: 0.50,
            RiskLevel.CRITICAL: 0.70
        }
        
        # 风险限制
        self.risk_limits = {
            "max_portfolio_var": 0.15,        # 最大投资组合VaR
            "max_position_weight": 0.20,      # 最大单一仓位权重
            "max_sector_exposure": 0.40,      # 最大行业敞口
            "max_correlation": 0.80,          # 最大相关性
            "min_liquidity_score": 0.30,     # 最小流动性分数
            "max_leverage": 2.0,              # 最大杠杆率
            "max_drawdown": 0.15              # 最大回撤
        }
        
        # 动态风险调整参数
        self.dynamic_params = {
            "volatility_lookback": 20,        # 波动率回看期
            "correlation_lookback": 60,       # 相关性回看期
            "var_confidence": 0.95,           # VaR置信度
            "stress_test_scenarios": 5,       # 压力测试场景数
            "risk_decay_factor": 0.94         # 风险衰减因子
        }
        
        # 止损策略
        self.stop_loss_strategies = {
            "fixed": {"enabled": True, "percentage": 0.05},
            "trailing": {"enabled": True, "distance": 0.03, "step": 0.01},
            "volatility_based": {"enabled": True, "multiplier": 2.0},
            "support_resistance": {"enabled": True, "buffer": 0.02}
        }
        
        # 风险状态
        self.risk_state = {
            "current_alerts": [],
            "risk_budget_used": 0.0,
            "portfolio_var": 0.0,
            "max_drawdown": 0.0,
            "stress_test_results": {},
            "last_assessment_time": None
        }
        
        # 历史风险数据
        self.risk_history = []
        
        logger.info("Enhanced Risk Manager initialized")
    
    async def assess_comprehensive_risk(self, 
                                      market_data: Dict[str, Any],
                                      portfolio_data: Dict[str, Any],
                                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        综合风险评估
        
        Args:
            market_data: 市场数据
            portfolio_data: 投资组合数据
            context: 额外上下文
            
        Returns:
            综合风险评估结果
        """
        try:
            logger.info("Performing comprehensive risk assessment...")
            
            # 1. 市场风险评估
            market_risk = await self._assess_market_risk(market_data)
            
            # 2. 投资组合风险评估
            portfolio_risk = await self._assess_portfolio_risk(portfolio_data, market_data)
            
            # 3. 流动性风险评估
            liquidity_risk = await self._assess_liquidity_risk(market_data, portfolio_data)
            
            # 4. 集中度风险评估
            concentration_risk = await self._assess_concentration_risk(portfolio_data)
            
            # 5. 压力测试
            stress_test_results = await self._perform_stress_test(portfolio_data, market_data)
            
            # 6. 动态VaR计算
            var_results = await self._calculate_dynamic_var(portfolio_data, market_data)
            
            # 7. 风险预警检查
            risk_alerts = await self._check_risk_alerts(
                market_risk, portfolio_risk, liquidity_risk, concentration_risk
            )
            
            # 8. 生成风险控制建议
            risk_controls = await self._generate_risk_controls(
                market_risk, portfolio_risk, liquidity_risk, concentration_risk, var_results
            )
            
            # 9. 计算综合风险分数
            overall_risk_score = self._calculate_overall_risk_score(
                market_risk, portfolio_risk, liquidity_risk, concentration_risk
            )
            
            # 构建评估结果
            assessment_result = {
                "overall_risk_score": overall_risk_score,
                "risk_level": self._get_risk_level(overall_risk_score),
                "market_risk": market_risk,
                "portfolio_risk": portfolio_risk,
                "liquidity_risk": liquidity_risk,
                "concentration_risk": concentration_risk,
                "var_results": var_results,
                "stress_test_results": stress_test_results,
                "risk_alerts": [asdict(alert) for alert in risk_alerts],
                "risk_controls": risk_controls,
                "assessment_time": datetime.now().isoformat(),
                "metadata": {
                    "risk_budget_used": self.risk_state["risk_budget_used"],
                    "max_drawdown": self.risk_state["max_drawdown"]
                }
            }
            
            # 更新风险状态
            self._update_risk_state(assessment_result)
            
            logger.info(f"Risk assessment completed. Overall risk: {overall_risk_score:.2f}")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk assessment: {e}")
            logger.error(traceback.format_exc())
            return self._generate_error_assessment(str(e))
    
    async def _assess_market_risk(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估市场风险"""
        try:
            # 获取市场数据
            volatility = market_data.get('volatility', 0.20)
            beta = market_data.get('beta', 1.0)
            correlation_with_market = market_data.get('market_correlation', 0.70)
            
            # 计算市场风险指标
            market_var = volatility * beta * 2.33  # 99%置信度VaR
            systematic_risk = abs(correlation_with_market) * volatility
            
            # 市场状态评估
            market_regime = market_data.get('market_regime', 'normal')
            regime_risk_multiplier = {
                'bull': 0.8,
                'bear': 1.5,
                'volatile': 1.3,
                'crisis': 2.0,
                'normal': 1.0
            }.get(market_regime, 1.0)
            
            adjusted_market_risk = market_var * regime_risk_multiplier
            
            return {
                "market_var": market_var,
                "systematic_risk": systematic_risk,
                "adjusted_risk": adjusted_market_risk,
                "volatility": volatility,
                "beta": beta,
                "market_correlation": correlation_with_market,
                "market_regime": market_regime,
                "regime_multiplier": regime_risk_multiplier,
                "risk_score": min(adjusted_market_risk / 0.30, 1.0)  # 标准化到0-1
            }
            
        except Exception as e:
            logger.error(f"Error assessing market risk: {e}")
            return {"risk_score": 0.5, "error": str(e)}
    
    async def _assess_portfolio_risk(self, 
                                   portfolio_data: Dict[str, Any], 
                                   market_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估投资组合风险"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 100000)
            
            if not positions:
                return {"risk_score": 0.0, "message": "No positions"}
            
            # 计算各仓位风险
            position_risks = []
            total_var = 0.0
            
            for position in positions:
                symbol = position.get('symbol', '')
                quantity = position.get('quantity', 0)
                price = position.get('current_price', 0)
                market_value = quantity * price
                weight = market_value / total_value if total_value > 0 else 0
                
                # 计算仓位VaR
                volatility = position.get('volatility', 0.20)
                position_var = market_value * volatility * 2.33  # 99%置信度
                
                # 计算Beta和相关性风险
                beta = position.get('beta', 1.0)
                correlation = position.get('correlation', 0.0)
                
                position_risk = PositionRisk(
                    symbol=symbol,
                    position_size=weight,
                    market_value=market_value,
                    var_1d=position_var,
                    var_5d=position_var * math.sqrt(5),
                    max_drawdown=position.get('max_drawdown', 0.0),
                    beta=beta,
                    correlation_risk=abs(correlation),
                    liquidity_score=position.get('liquidity_score', 0.5),
                    risk_score=min(weight * volatility * 5, 1.0)
                )
                
                position_risks.append(position_risk)
                total_var += position_var
            
            # 计算投资组合多样化效应
            diversification_ratio = self._calculate_diversification_ratio(positions)
            adjusted_portfolio_var = total_var * diversification_ratio
            
            # 计算集中度风险
            weights = [pos.position_size for pos in position_risks]
            concentration_index = sum(w**2 for w in weights)  # Herfindahl指数
            
            return {
                "portfolio_var": adjusted_portfolio_var,
                "portfolio_var_percentage": adjusted_portfolio_var / total_value,
                "diversification_ratio": diversification_ratio,
                "concentration_index": concentration_index,
                "position_count": len(positions),
                "largest_position_weight": max(weights) if weights else 0,
                "position_risks": [asdict(risk) for risk in position_risks],
                "risk_score": min(adjusted_portfolio_var / (total_value * 0.20), 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
            return {"risk_score": 0.5, "error": str(e)}
    
    def _calculate_diversification_ratio(self, positions: List[Dict]) -> float:
        """计算多样化比率"""
        try:
            if len(positions) <= 1:
                return 1.0
            
            # 简化的多样化计算
            n = len(positions)
            avg_correlation = 0.3  # 假设平均相关性
            
            # 多样化比率公式
            diversification_ratio = math.sqrt(
                (1 + (n - 1) * avg_correlation) / n
            )
            
            return max(0.5, min(1.0, diversification_ratio))
            
        except Exception as e:
            logger.error(f"Error calculating diversification ratio: {e}")
            return 0.8

    async def _assess_liquidity_risk(self,
                                   market_data: Dict[str, Any],
                                   portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估流动性风险"""
        try:
            positions = portfolio_data.get('positions', [])

            if not positions:
                return {"risk_score": 0.0, "message": "No positions"}

            total_liquidity_score = 0.0
            illiquid_positions = []

            for position in positions:
                symbol = position.get('symbol', '')
                volume = position.get('avg_volume', 0)
                market_cap = position.get('market_cap', 0)
                bid_ask_spread = position.get('bid_ask_spread', 0.01)

                # 计算流动性分数
                volume_score = min(volume / 1000000, 1.0)  # 标准化成交量
                market_cap_score = min(market_cap / 1000000000, 1.0)  # 标准化市值
                spread_score = max(0, 1.0 - bid_ask_spread * 100)  # 买卖价差分数

                liquidity_score = (volume_score * 0.4 + market_cap_score * 0.4 + spread_score * 0.2)

                total_liquidity_score += liquidity_score

                if liquidity_score < self.risk_limits["min_liquidity_score"]:
                    illiquid_positions.append({
                        "symbol": symbol,
                        "liquidity_score": liquidity_score,
                        "volume": volume,
                        "market_cap": market_cap,
                        "bid_ask_spread": bid_ask_spread
                    })

            avg_liquidity_score = total_liquidity_score / len(positions) if positions else 0
            liquidity_risk_score = 1.0 - avg_liquidity_score

            return {
                "avg_liquidity_score": avg_liquidity_score,
                "illiquid_positions_count": len(illiquid_positions),
                "illiquid_positions": illiquid_positions,
                "liquidity_risk_score": liquidity_risk_score,
                "risk_score": liquidity_risk_score
            }

        except Exception as e:
            logger.error(f"Error assessing liquidity risk: {e}")
            return {"risk_score": 0.5, "error": str(e)}

    async def _assess_concentration_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估集中度风险"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 100000)

            if not positions:
                return {"risk_score": 0.0, "message": "No positions"}

            # 按行业分组
            sector_exposure = {}
            # 按地区分组
            region_exposure = {}
            # 按资产类型分组
            asset_type_exposure = {}

            for position in positions:
                market_value = position.get('quantity', 0) * position.get('current_price', 0)
                weight = market_value / total_value if total_value > 0 else 0

                # 行业集中度
                sector = position.get('sector', 'Unknown')
                sector_exposure[sector] = sector_exposure.get(sector, 0) + weight

                # 地区集中度
                region = position.get('region', 'Unknown')
                region_exposure[region] = region_exposure.get(region, 0) + weight

                # 资产类型集中度
                asset_type = position.get('asset_type', 'Stock')
                asset_type_exposure[asset_type] = asset_type_exposure.get(asset_type, 0) + weight

            # 计算集中度指标
            sector_hhi = sum(w**2 for w in sector_exposure.values())
            region_hhi = sum(w**2 for w in region_exposure.values())
            asset_type_hhi = sum(w**2 for w in asset_type_exposure.values())

            # 检查是否超过限制
            max_sector_exposure = max(sector_exposure.values()) if sector_exposure else 0
            concentration_violations = []

            if max_sector_exposure > self.risk_limits["max_sector_exposure"]:
                concentration_violations.append({
                    "type": "sector",
                    "value": max_sector_exposure,
                    "limit": self.risk_limits["max_sector_exposure"]
                })

            # 计算总体集中度风险分数
            concentration_risk_score = (sector_hhi + region_hhi + asset_type_hhi) / 3

            return {
                "sector_exposure": sector_exposure,
                "region_exposure": region_exposure,
                "asset_type_exposure": asset_type_exposure,
                "sector_hhi": sector_hhi,
                "region_hhi": region_hhi,
                "asset_type_hhi": asset_type_hhi,
                "max_sector_exposure": max_sector_exposure,
                "concentration_violations": concentration_violations,
                "risk_score": concentration_risk_score
            }

        except Exception as e:
            logger.error(f"Error assessing concentration risk: {e}")
            return {"risk_score": 0.5, "error": str(e)}

    async def _perform_stress_test(self,
                                 portfolio_data: Dict[str, Any],
                                 market_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行压力测试"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 100000)

            if not positions:
                return {"message": "No positions for stress test"}

            # 定义压力测试场景
            stress_scenarios = {
                "market_crash": {"market_shock": -0.20, "volatility_spike": 2.0},
                "sector_rotation": {"sector_shock": -0.15, "correlation_increase": 0.3},
                "liquidity_crisis": {"liquidity_shock": 0.5, "spread_widening": 3.0},
                "interest_rate_shock": {"rate_shock": 0.02, "duration_impact": -0.10},
                "currency_crisis": {"fx_shock": -0.15, "emerging_market_impact": -0.25}
            }

            stress_results = {}

            for scenario_name, scenario_params in stress_scenarios.items():
                scenario_loss = 0.0

                for position in positions:
                    market_value = position.get('quantity', 0) * position.get('current_price', 0)
                    beta = position.get('beta', 1.0)
                    sector = position.get('sector', 'Unknown')

                    # 计算场景下的损失
                    if scenario_name == "market_crash":
                        position_loss = market_value * scenario_params["market_shock"] * beta
                    elif scenario_name == "sector_rotation":
                        sector_impact = scenario_params["sector_shock"] if sector in ["Technology", "Finance"] else -0.05
                        position_loss = market_value * sector_impact
                    elif scenario_name == "liquidity_crisis":
                        liquidity_score = position.get('liquidity_score', 0.5)
                        position_loss = market_value * scenario_params["liquidity_shock"] * (1 - liquidity_score)
                    else:
                        # 默认市场冲击
                        position_loss = market_value * -0.10 * beta

                    scenario_loss += position_loss

                stress_results[scenario_name] = {
                    "total_loss": scenario_loss,
                    "loss_percentage": scenario_loss / total_value if total_value > 0 else 0,
                    "scenario_params": scenario_params
                }

            # 计算最坏情况
            worst_case_loss = min(result["total_loss"] for result in stress_results.values())
            worst_case_percentage = worst_case_loss / total_value if total_value > 0 else 0

            return {
                "scenarios": stress_results,
                "worst_case_loss": worst_case_loss,
                "worst_case_percentage": worst_case_percentage,
                "stress_test_passed": worst_case_percentage > -0.25,  # 25%损失阈值
                "test_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error performing stress test: {e}")
            return {"error": str(e)}

    async def _calculate_dynamic_var(self,
                                   portfolio_data: Dict[str, Any],
                                   market_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算动态VaR"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 100000)

            if not positions:
                return {"var_1d": 0.0, "var_5d": 0.0, "var_10d": 0.0}

            # 计算投资组合VaR
            portfolio_volatility = 0.0
            total_weight_squared = 0.0

            for position in positions:
                market_value = position.get('quantity', 0) * position.get('current_price', 0)
                weight = market_value / total_value if total_value > 0 else 0
                volatility = position.get('volatility', 0.20)

                portfolio_volatility += (weight * volatility) ** 2
                total_weight_squared += weight ** 2

            # 考虑相关性的简化计算
            avg_correlation = 0.3
            portfolio_volatility = math.sqrt(
                portfolio_volatility +
                2 * avg_correlation * math.sqrt(portfolio_volatility) * (1 - total_weight_squared)
            )

            # 计算不同时间范围的VaR
            confidence_level = self.dynamic_params["var_confidence"]
            z_score = 2.33 if confidence_level == 0.99 else 1.96 if confidence_level == 0.95 else 1.65

            var_1d = total_value * portfolio_volatility * z_score
            var_5d = var_1d * math.sqrt(5)
            var_10d = var_1d * math.sqrt(10)

            return {
                "var_1d": var_1d,
                "var_5d": var_5d,
                "var_10d": var_10d,
                "var_1d_percentage": var_1d / total_value,
                "var_5d_percentage": var_5d / total_value,
                "var_10d_percentage": var_10d / total_value,
                "portfolio_volatility": portfolio_volatility,
                "confidence_level": confidence_level,
                "calculation_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating dynamic VaR: {e}")
            return {"error": str(e)}

    async def _check_risk_alerts(self,
                               market_risk: Dict[str, Any],
                               portfolio_risk: Dict[str, Any],
                               liquidity_risk: Dict[str, Any],
                               concentration_risk: Dict[str, Any]) -> List[RiskAlert]:
        """检查风险预警"""
        alerts = []

        try:
            # 市场风险预警
            if market_risk.get("risk_score", 0) > 0.7:
                alerts.append(RiskAlert(
                    risk_type=RiskType.MARKET,
                    risk_level=RiskLevel.HIGH,
                    message="市场风险过高",
                    current_value=market_risk.get("risk_score", 0),
                    threshold=0.7,
                    recommendation="考虑减少市场敞口或增加对冲",
                    timestamp=datetime.now()
                ))

            # 投资组合风险预警
            portfolio_var_pct = portfolio_risk.get("portfolio_var_percentage", 0)
            if portfolio_var_pct > self.risk_limits["max_portfolio_var"]:
                alerts.append(RiskAlert(
                    risk_type=RiskType.MARKET,
                    risk_level=RiskLevel.HIGH,
                    message="投资组合VaR超限",
                    current_value=portfolio_var_pct,
                    threshold=self.risk_limits["max_portfolio_var"],
                    recommendation="减少高风险仓位或增加多样化",
                    timestamp=datetime.now()
                ))

            # 集中度风险预警
            max_sector_exposure = concentration_risk.get("max_sector_exposure", 0)
            if max_sector_exposure > self.risk_limits["max_sector_exposure"]:
                alerts.append(RiskAlert(
                    risk_type=RiskType.CONCENTRATION,
                    risk_level=RiskLevel.MEDIUM,
                    message="行业集中度过高",
                    current_value=max_sector_exposure,
                    threshold=self.risk_limits["max_sector_exposure"],
                    recommendation="分散投资到其他行业",
                    timestamp=datetime.now()
                ))

            # 流动性风险预警
            if liquidity_risk.get("risk_score", 0) > 0.6:
                alerts.append(RiskAlert(
                    risk_type=RiskType.LIQUIDITY,
                    risk_level=RiskLevel.MEDIUM,
                    message="流动性风险较高",
                    current_value=liquidity_risk.get("risk_score", 0),
                    threshold=0.6,
                    recommendation="增加流动性较好的资产配置",
                    timestamp=datetime.now()
                ))

        except Exception as e:
            logger.error(f"Error checking risk alerts: {e}")

        return alerts

    async def _generate_risk_controls(self,
                                    market_risk: Dict[str, Any],
                                    portfolio_risk: Dict[str, Any],
                                    liquidity_risk: Dict[str, Any],
                                    concentration_risk: Dict[str, Any],
                                    var_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成风险控制建议"""
        try:
            controls = {
                "position_sizing": {},
                "stop_loss": {},
                "hedging": {},
                "rebalancing": {},
                "liquidity_management": {}
            }

            # 仓位控制建议
            portfolio_var_pct = portfolio_risk.get("portfolio_var_percentage", 0)
            if portfolio_var_pct > 0.10:
                controls["position_sizing"] = {
                    "action": "reduce_positions",
                    "target_reduction": min(0.3, (portfolio_var_pct - 0.10) / 0.10),
                    "priority": "high_risk_positions",
                    "reasoning": "投资组合风险过高，需要减少仓位"
                }

            # 止损建议
            market_volatility = market_risk.get("volatility", 0.20)
            if market_volatility > 0.30:
                controls["stop_loss"] = {
                    "strategy": "volatility_based",
                    "stop_distance": market_volatility * 1.5,
                    "trailing_enabled": True,
                    "reasoning": "市场波动率高，建议使用动态止损"
                }
            else:
                controls["stop_loss"] = {
                    "strategy": "fixed",
                    "stop_distance": 0.05,
                    "trailing_enabled": False,
                    "reasoning": "市场相对稳定，使用固定止损"
                }

            # 对冲建议
            if market_risk.get("risk_score", 0) > 0.6:
                controls["hedging"] = {
                    "recommended": True,
                    "hedge_ratio": min(0.5, market_risk.get("risk_score", 0)),
                    "instruments": ["index_futures", "options"],
                    "reasoning": "市场风险较高，建议进行对冲"
                }

            # 再平衡建议
            concentration_violations = concentration_risk.get("concentration_violations", [])
            if concentration_violations:
                controls["rebalancing"] = {
                    "required": True,
                    "target_weights": self._calculate_target_weights(concentration_risk),
                    "priority": "high",
                    "reasoning": "存在集中度风险，需要再平衡"
                }

            # 流动性管理建议
            illiquid_count = liquidity_risk.get("illiquid_positions_count", 0)
            if illiquid_count > 0:
                controls["liquidity_management"] = {
                    "action": "improve_liquidity",
                    "target_liquidity_ratio": 0.20,
                    "illiquid_positions": illiquid_count,
                    "reasoning": "存在流动性不足的仓位，建议优化"
                }

            return controls

        except Exception as e:
            logger.error(f"Error generating risk controls: {e}")
            return {"error": str(e)}

    def _calculate_target_weights(self, concentration_risk: Dict[str, Any]) -> Dict[str, float]:
        """计算目标权重"""
        try:
            sector_exposure = concentration_risk.get("sector_exposure", {})
            max_sector_limit = self.risk_limits["max_sector_exposure"]

            target_weights = {}
            total_excess = 0.0

            # 计算超限部分
            for sector, weight in sector_exposure.items():
                if weight > max_sector_limit:
                    target_weights[sector] = max_sector_limit
                    total_excess += weight - max_sector_limit
                else:
                    target_weights[sector] = weight

            # 重新分配超限部分
            if total_excess > 0:
                sectors_under_limit = [s for s, w in target_weights.items() if w < max_sector_limit]
                if sectors_under_limit:
                    redistribution_per_sector = total_excess / len(sectors_under_limit)
                    for sector in sectors_under_limit:
                        target_weights[sector] = min(
                            max_sector_limit,
                            target_weights[sector] + redistribution_per_sector
                        )

            return target_weights

        except Exception as e:
            logger.error(f"Error calculating target weights: {e}")
            return {}

    def _calculate_overall_risk_score(self,
                                    market_risk: Dict[str, Any],
                                    portfolio_risk: Dict[str, Any],
                                    liquidity_risk: Dict[str, Any],
                                    concentration_risk: Dict[str, Any]) -> float:
        """计算综合风险分数"""
        try:
            # 风险权重
            weights = {
                "market": 0.30,
                "portfolio": 0.35,
                "liquidity": 0.20,
                "concentration": 0.15
            }

            # 获取各项风险分数
            market_score = market_risk.get("risk_score", 0.0)
            portfolio_score = portfolio_risk.get("risk_score", 0.0)
            liquidity_score = liquidity_risk.get("risk_score", 0.0)
            concentration_score = concentration_risk.get("risk_score", 0.0)

            # 计算加权平均
            overall_score = (
                market_score * weights["market"] +
                portfolio_score * weights["portfolio"] +
                liquidity_score * weights["liquidity"] +
                concentration_score * weights["concentration"]
            )

            return min(1.0, max(0.0, overall_score))

        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 0.5

    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """根据风险分数获取风险等级"""
        for level, threshold in self.risk_thresholds.items():
            if risk_score <= threshold:
                return level
        return RiskLevel.CRITICAL

    def _update_risk_state(self, assessment_result: Dict[str, Any]):
        """更新风险状态"""
        try:
            self.risk_state["current_alerts"] = assessment_result.get("risk_alerts", [])
            self.risk_state["portfolio_var"] = assessment_result.get("var_results", {}).get("var_1d_percentage", 0)
            self.risk_state["last_assessment_time"] = datetime.now()

            # 更新历史记录
            self.risk_history.append({
                "timestamp": datetime.now().isoformat(),
                "overall_risk_score": assessment_result.get("overall_risk_score", 0),
                "risk_level": assessment_result.get("risk_level", RiskLevel.MEDIUM).value,
                "alert_count": len(assessment_result.get("risk_alerts", []))
            })

            # 限制历史长度
            if len(self.risk_history) > 1000:
                self.risk_history = self.risk_history[-500:]

        except Exception as e:
            logger.error(f"Error updating risk state: {e}")

    def _generate_error_assessment(self, error_message: str) -> Dict[str, Any]:
        """生成错误评估结果"""
        return {
            "overall_risk_score": 0.5,
            "risk_level": RiskLevel.MEDIUM.value,
            "error": error_message,
            "assessment_time": datetime.now().isoformat(),
            "market_risk": {"risk_score": 0.5, "error": error_message},
            "portfolio_risk": {"risk_score": 0.5, "error": error_message},
            "liquidity_risk": {"risk_score": 0.5, "error": error_message},
            "concentration_risk": {"risk_score": 0.5, "error": error_message},
            "risk_alerts": [],
            "risk_controls": {}
        }

    async def get_risk_summary(self) -> Dict[str, Any]:
        """获取风险摘要"""
        try:
            return {
                "current_risk_state": self.risk_state,
                "risk_limits": self.risk_limits,
                "recent_alerts": self.risk_state["current_alerts"][-5:],
                "risk_history_summary": {
                    "total_assessments": len(self.risk_history),
                    "avg_risk_score": np.mean([h["overall_risk_score"] for h in self.risk_history[-30:]]) if self.risk_history else 0,
                    "recent_trend": "increasing" if len(self.risk_history) >= 2 and self.risk_history[-1]["overall_risk_score"] > self.risk_history[-2]["overall_risk_score"] else "stable"
                }
            }
        except Exception as e:
            logger.error(f"Error getting risk summary: {e}")
            return {"error": str(e)}
