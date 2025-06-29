"""
增强版决策引擎
集成多种AI算法和决策模型，提供更准确和智能的交易决策
"""

import numpy as np
import pandas as pd
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union, Optional, Tuple
import traceback
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("EnhancedDecisionEngine")

class MarketRegime(Enum):
    """市场状态枚举"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    CRISIS = "crisis"

class DecisionType(Enum):
    """决策类型枚举"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REDUCE = "reduce"
    INCREASE = "increase"

@dataclass
class DecisionSignal:
    """决策信号数据类"""
    signal_type: DecisionType
    confidence: float
    strength: float
    source: str
    reasoning: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class TradingDecision:
    """交易决策数据类"""
    action: DecisionType
    symbol: str
    quantity: int
    price: float
    confidence: float
    reasoning: str
    risk_score: float
    expected_return: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    signals: List[DecisionSignal]
    metadata: Dict[str, Any] = None

class EnhancedDecisionEngine:
    """
    增强版决策引擎
    集成多种AI算法和决策模型
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化增强版决策引擎
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 决策模型权重
        self.model_weights = {
            "technical_analysis": 0.25,    # 技术分析
            "fundamental_analysis": 0.20,  # 基本面分析
            "sentiment_analysis": 0.15,    # 情绪分析
            "momentum_model": 0.15,        # 动量模型
            "mean_reversion": 0.10,        # 均值回归
            "volatility_model": 0.10,      # 波动率模型
            "risk_model": 0.05             # 风险模型
        }
        
        # 市场状态检测器
        self.market_regime_detector = MarketRegimeDetector()
        
        # 信号聚合器
        self.signal_aggregator = SignalAggregator()
        
        # 风险调整器
        self.risk_adjuster = RiskAdjuster()
        
        # 决策历史
        self.decision_history = []
        
        # 性能指标
        self.performance_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "accuracy": 0.0,
            "avg_confidence": 0.0,
            "avg_return": 0.0,
            "sharpe_ratio": 0.0
        }
        
        logger.info("Enhanced Decision Engine initialized")
    
    async def make_decision(self, 
                          market_data: Dict[str, Any],
                          portfolio_state: Dict[str, Any],
                          context: Dict[str, Any] = None) -> TradingDecision:
        """
        生成增强版交易决策
        
        Args:
            market_data: 市场数据
            portfolio_state: 投资组合状态
            context: 额外上下文信息
            
        Returns:
            交易决策
        """
        try:
            logger.info("Generating enhanced trading decision...")
            
            # 1. 检测市场状态
            market_regime = await self.market_regime_detector.detect_regime(market_data)
            
            # 2. 生成多模型信号
            signals = await self._generate_multi_model_signals(market_data, market_regime)
            
            # 3. 聚合信号
            aggregated_signal = self.signal_aggregator.aggregate(signals, market_regime)
            
            # 4. 风险调整
            risk_adjusted_decision = self.risk_adjuster.adjust_decision(
                aggregated_signal, portfolio_state, market_data
            )
            
            # 5. 生成最终决策
            final_decision = self._generate_final_decision(
                risk_adjusted_decision, signals, market_data, portfolio_state
            )
            
            # 6. 记录决策
            self._record_decision(final_decision)
            
            logger.info(f"Decision generated: {final_decision.action.value} with confidence {final_decision.confidence:.2f}")
            return final_decision
            
        except Exception as e:
            logger.error(f"Error generating decision: {e}")
            logger.error(traceback.format_exc())
            return self._generate_error_decision(str(e))
    
    async def _generate_multi_model_signals(self, 
                                          market_data: Dict[str, Any], 
                                          market_regime: MarketRegime) -> List[DecisionSignal]:
        """
        生成多模型信号
        
        Args:
            market_data: 市场数据
            market_regime: 市场状态
            
        Returns:
            决策信号列表
        """
        signals = []
        
        try:
            # 技术分析信号
            tech_signal = await self._generate_technical_signal(market_data, market_regime)
            if tech_signal:
                signals.append(tech_signal)
            
            # 基本面分析信号
            fundamental_signal = await self._generate_fundamental_signal(market_data, market_regime)
            if fundamental_signal:
                signals.append(fundamental_signal)
            
            # 情绪分析信号
            sentiment_signal = await self._generate_sentiment_signal(market_data, market_regime)
            if sentiment_signal:
                signals.append(sentiment_signal)
            
            # 动量模型信号
            momentum_signal = await self._generate_momentum_signal(market_data, market_regime)
            if momentum_signal:
                signals.append(momentum_signal)
            
            # 均值回归信号
            mean_reversion_signal = await self._generate_mean_reversion_signal(market_data, market_regime)
            if mean_reversion_signal:
                signals.append(mean_reversion_signal)
            
            # 波动率模型信号
            volatility_signal = await self._generate_volatility_signal(market_data, market_regime)
            if volatility_signal:
                signals.append(volatility_signal)
            
        except Exception as e:
            logger.error(f"Error generating multi-model signals: {e}")
        
        return signals
    
    async def _generate_technical_signal(self, 
                                       market_data: Dict[str, Any], 
                                       market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成技术分析信号"""
        try:
            # 获取价格数据
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return None
            
            df = pd.DataFrame(prices)
            
            # 计算技术指标
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else sma_20
            current_price = df['close'].iloc[-1]
            
            rsi = self._calculate_rsi(df['close'])
            macd_signal = self._calculate_macd_signal(df['close'])
            
            # 生成信号
            signal_strength = 0.0
            reasoning = []
            
            # 移动平均线信号
            if current_price > sma_20 > sma_50:
                signal_strength += 0.3
                reasoning.append("价格突破短期和长期均线")
            elif current_price < sma_20 < sma_50:
                signal_strength -= 0.3
                reasoning.append("价格跌破短期和长期均线")
            
            # RSI信号
            if rsi < 30:
                signal_strength += 0.2
                reasoning.append(f"RSI超卖({rsi:.1f})")
            elif rsi > 70:
                signal_strength -= 0.2
                reasoning.append(f"RSI超买({rsi:.1f})")
            
            # MACD信号
            if macd_signal > 0:
                signal_strength += 0.2
                reasoning.append("MACD金叉")
            elif macd_signal < 0:
                signal_strength -= 0.2
                reasoning.append("MACD死叉")
            
            # 根据市场状态调整信号
            if market_regime == MarketRegime.BULL:
                signal_strength *= 1.2
            elif market_regime == MarketRegime.BEAR:
                signal_strength *= 0.8
            
            # 确定信号类型
            if signal_strength > 0.3:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.3:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD
            
            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="technical_analysis",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                metadata={
                    "rsi": rsi,
                    "sma_20": sma_20,
                    "sma_50": sma_50,
                    "macd_signal": macd_signal
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating technical signal: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """计算RSI指标"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def _calculate_macd_signal(self, prices: pd.Series) -> float:
        """计算MACD信号"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            return (macd - signal).iloc[-1]
        except:
            return 0.0

class MarketRegimeDetector:
    """市场状态检测器"""
    
    async def detect_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """检测当前市场状态"""
        try:
            # 简化的市场状态检测逻辑
            volatility = market_data.get('volatility', 0.2)
            trend = market_data.get('trend', 0.0)
            
            if volatility > 0.4:
                return MarketRegime.VOLATILE
            elif trend > 0.1:
                return MarketRegime.BULL
            elif trend < -0.1:
                return MarketRegime.BEAR
            else:
                return MarketRegime.SIDEWAYS
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return MarketRegime.SIDEWAYS

class SignalAggregator:
    """信号聚合器"""
    
    def aggregate(self, signals: List[DecisionSignal], market_regime: MarketRegime) -> DecisionSignal:
        """聚合多个信号"""
        if not signals:
            return DecisionSignal(
                signal_type=DecisionType.HOLD,
                confidence=0.0,
                strength=0.0,
                source="aggregator",
                reasoning="No signals available",
                timestamp=datetime.now()
            )
        
        # 计算加权平均
        total_weight = 0.0
        weighted_strength = 0.0
        
        for signal in signals:
            weight = signal.confidence
            total_weight += weight
            weighted_strength += signal.strength * weight
        
        if total_weight > 0:
            avg_strength = weighted_strength / total_weight
        else:
            avg_strength = 0.0
        
        # 确定聚合信号类型
        if avg_strength > 0.3:
            signal_type = DecisionType.BUY
        elif avg_strength < -0.3:
            signal_type = DecisionType.SELL
        else:
            signal_type = DecisionType.HOLD
        
        return DecisionSignal(
            signal_type=signal_type,
            confidence=min(abs(avg_strength), 1.0),
            strength=avg_strength,
            source="aggregated",
            reasoning=f"Aggregated from {len(signals)} signals",
            timestamp=datetime.now(),
            metadata={"source_signals": len(signals)}
        )

class RiskAdjuster:
    """风险调整器"""
    
    def adjust_decision(self, 
                       signal: DecisionSignal, 
                       portfolio_state: Dict[str, Any], 
                       market_data: Dict[str, Any]) -> DecisionSignal:
        """根据风险调整决策"""
        try:
            # 获取风险指标
            portfolio_risk = portfolio_state.get('risk_score', 0.5)
            market_volatility = market_data.get('volatility', 0.2)
            
            # 计算风险调整因子
            risk_factor = 1.0 - (portfolio_risk * 0.5 + market_volatility * 0.3)
            risk_factor = max(0.1, min(1.0, risk_factor))
            
            # 调整信号强度
            adjusted_strength = signal.strength * risk_factor
            adjusted_confidence = signal.confidence * risk_factor
            
            return DecisionSignal(
                signal_type=signal.signal_type,
                confidence=adjusted_confidence,
                strength=adjusted_strength,
                source=f"risk_adjusted_{signal.source}",
                reasoning=f"Risk adjusted: {signal.reasoning}",
                timestamp=datetime.now(),
                metadata={
                    "original_signal": signal,
                    "risk_factor": risk_factor,
                    "portfolio_risk": portfolio_risk,
                    "market_volatility": market_volatility
                }
            )
            
        except Exception as e:
            logger.error(f"Error adjusting decision for risk: {e}")
            return signal

    async def _generate_fundamental_signal(self,
                                         market_data: Dict[str, Any],
                                         market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成基本面分析信号"""
        try:
            fundamental_data = market_data.get('fundamental', {})
            if not fundamental_data:
                return None

            pe_ratio = fundamental_data.get('pe_ratio', 15.0)
            pb_ratio = fundamental_data.get('pb_ratio', 1.5)
            roe = fundamental_data.get('roe', 0.1)
            debt_ratio = fundamental_data.get('debt_ratio', 0.3)

            signal_strength = 0.0
            reasoning = []

            # PE估值分析
            if pe_ratio < 10:
                signal_strength += 0.3
                reasoning.append(f"PE低估值({pe_ratio:.1f})")
            elif pe_ratio > 30:
                signal_strength -= 0.2
                reasoning.append(f"PE高估值({pe_ratio:.1f})")

            # PB估值分析
            if pb_ratio < 1.0:
                signal_strength += 0.2
                reasoning.append(f"PB破净({pb_ratio:.1f})")
            elif pb_ratio > 3.0:
                signal_strength -= 0.1
                reasoning.append(f"PB过高({pb_ratio:.1f})")

            # ROE盈利能力
            if roe > 0.15:
                signal_strength += 0.2
                reasoning.append(f"ROE优秀({roe:.1%})")
            elif roe < 0.05:
                signal_strength -= 0.2
                reasoning.append(f"ROE较低({roe:.1%})")

            # 债务比率
            if debt_ratio > 0.6:
                signal_strength -= 0.2
                reasoning.append(f"债务比率过高({debt_ratio:.1%})")

            # 确定信号类型
            if signal_strength > 0.2:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.2:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD

            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="fundamental_analysis",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                metadata=fundamental_data
            )

        except Exception as e:
            logger.error(f"Error generating fundamental signal: {e}")
            return None

    async def _generate_sentiment_signal(self,
                                       market_data: Dict[str, Any],
                                       market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成情绪分析信号"""
        try:
            sentiment_data = market_data.get('sentiment', {})
            if not sentiment_data:
                return None

            news_sentiment = sentiment_data.get('news_sentiment', 0.0)
            social_sentiment = sentiment_data.get('social_sentiment', 0.0)
            analyst_rating = sentiment_data.get('analyst_rating', 0.0)

            # 综合情绪分数
            sentiment_score = (news_sentiment * 0.4 + social_sentiment * 0.3 + analyst_rating * 0.3)

            signal_strength = sentiment_score * 0.5  # 情绪信号权重较低

            reasoning = f"综合情绪分数: {sentiment_score:.2f}"

            # 确定信号类型
            if signal_strength > 0.2:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.2:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD

            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="sentiment_analysis",
                reasoning=reasoning,
                timestamp=datetime.now(),
                metadata=sentiment_data
            )

        except Exception as e:
            logger.error(f"Error generating sentiment signal: {e}")
            return None

    async def _generate_momentum_signal(self,
                                      market_data: Dict[str, Any],
                                      market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成动量模型信号"""
        try:
            prices = market_data.get('prices', [])
            if len(prices) < 10:
                return None

            df = pd.DataFrame(prices)

            # 计算动量指标
            returns_5d = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) if len(df) >= 6 else 0
            returns_20d = (df['close'].iloc[-1] / df['close'].iloc[-21] - 1) if len(df) >= 21 else 0

            volume_ratio = df['volume'].iloc[-5:].mean() / df['volume'].iloc[-20:-5].mean() if len(df) >= 20 else 1.0

            signal_strength = 0.0
            reasoning = []

            # 短期动量
            if returns_5d > 0.05:
                signal_strength += 0.3
                reasoning.append(f"5日涨幅{returns_5d:.1%}")
            elif returns_5d < -0.05:
                signal_strength -= 0.3
                reasoning.append(f"5日跌幅{abs(returns_5d):.1%}")

            # 中期动量
            if returns_20d > 0.1:
                signal_strength += 0.2
                reasoning.append(f"20日涨幅{returns_20d:.1%}")
            elif returns_20d < -0.1:
                signal_strength -= 0.2
                reasoning.append(f"20日跌幅{abs(returns_20d):.1%}")

            # 成交量确认
            if volume_ratio > 1.5:
                signal_strength *= 1.2
                reasoning.append(f"成交量放大{volume_ratio:.1f}倍")

            # 确定信号类型
            if signal_strength > 0.2:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.2:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD

            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="momentum_model",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                metadata={
                    "returns_5d": returns_5d,
                    "returns_20d": returns_20d,
                    "volume_ratio": volume_ratio
                }
            )

        except Exception as e:
            logger.error(f"Error generating momentum signal: {e}")
            return None

    async def _generate_mean_reversion_signal(self,
                                            market_data: Dict[str, Any],
                                            market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成均值回归信号"""
        try:
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return None

            df = pd.DataFrame(prices)

            # 计算均值回归指标
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            std_20 = df['close'].rolling(20).std().iloc[-1]

            # 计算偏离度
            deviation = (current_price - sma_20) / std_20 if std_20 > 0 else 0

            signal_strength = 0.0
            reasoning = []

            # 均值回归信号（与动量相反）
            if deviation > 2:  # 价格过度偏离均值上方
                signal_strength -= 0.3
                reasoning.append(f"价格过度偏离均值上方({deviation:.1f}σ)")
            elif deviation < -2:  # 价格过度偏离均值下方
                signal_strength += 0.3
                reasoning.append(f"价格过度偏离均值下方({abs(deviation):.1f}σ)")

            # 在震荡市场中增强均值回归信号
            if market_regime == MarketRegime.SIDEWAYS:
                signal_strength *= 1.5

            # 确定信号类型
            if signal_strength > 0.2:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.2:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD

            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="mean_reversion",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                metadata={
                    "deviation": deviation,
                    "sma_20": sma_20,
                    "std_20": std_20
                }
            )

        except Exception as e:
            logger.error(f"Error generating mean reversion signal: {e}")
            return None

    async def _generate_volatility_signal(self,
                                        market_data: Dict[str, Any],
                                        market_regime: MarketRegime) -> Optional[DecisionSignal]:
        """生成波动率模型信号"""
        try:
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return None

            df = pd.DataFrame(prices)

            # 计算波动率指标
            returns = df['close'].pct_change().dropna()
            current_vol = returns.rolling(20).std().iloc[-1] * np.sqrt(252)  # 年化波动率
            long_term_vol = returns.rolling(60).std().iloc[-1] * np.sqrt(252) if len(returns) >= 60 else current_vol

            vol_ratio = current_vol / long_term_vol if long_term_vol > 0 else 1.0

            signal_strength = 0.0
            reasoning = []

            # 波动率信号
            if vol_ratio > 1.5:  # 波动率显著上升
                signal_strength -= 0.2
                reasoning.append(f"波动率上升{vol_ratio:.1f}倍")
            elif vol_ratio < 0.7:  # 波动率显著下降
                signal_strength += 0.1
                reasoning.append(f"波动率下降至{vol_ratio:.1f}倍")

            # 在高波动市场中降低信号强度
            if market_regime == MarketRegime.VOLATILE:
                signal_strength *= 0.5

            # 确定信号类型
            if signal_strength > 0.1:
                signal_type = DecisionType.BUY
            elif signal_strength < -0.1:
                signal_type = DecisionType.SELL
            else:
                signal_type = DecisionType.HOLD

            return DecisionSignal(
                signal_type=signal_type,
                confidence=min(abs(signal_strength), 1.0),
                strength=signal_strength,
                source="volatility_model",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                metadata={
                    "current_vol": current_vol,
                    "long_term_vol": long_term_vol,
                    "vol_ratio": vol_ratio
                }
            )

        except Exception as e:
            logger.error(f"Error generating volatility signal: {e}")
            return None

    def _generate_final_decision(self,
                               risk_adjusted_signal: DecisionSignal,
                               signals: List[DecisionSignal],
                               market_data: Dict[str, Any],
                               portfolio_state: Dict[str, Any]) -> TradingDecision:
        """生成最终交易决策"""
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            current_price = market_data.get('current_price', 0.0)

            # 计算仓位大小
            portfolio_value = portfolio_state.get('total_value', 100000)
            risk_per_trade = portfolio_state.get('risk_per_trade', 0.02)

            # 基础仓位计算
            base_position_size = int(portfolio_value * risk_per_trade / current_price) if current_price > 0 else 0

            # 根据信号强度调整仓位
            position_multiplier = min(abs(risk_adjusted_signal.strength) * 2, 1.0)
            quantity = int(base_position_size * position_multiplier)

            # 计算止损和止盈
            volatility = market_data.get('volatility', 0.02)

            if risk_adjusted_signal.signal_type == DecisionType.BUY:
                stop_loss = current_price * (1 - volatility * 2)
                take_profit = current_price * (1 + volatility * 3)
            elif risk_adjusted_signal.signal_type == DecisionType.SELL:
                stop_loss = current_price * (1 + volatility * 2)
                take_profit = current_price * (1 - volatility * 3)
            else:
                stop_loss = current_price
                take_profit = current_price

            # 计算预期收益
            if risk_adjusted_signal.signal_type == DecisionType.BUY:
                expected_return = (take_profit - current_price) / current_price
            elif risk_adjusted_signal.signal_type == DecisionType.SELL:
                expected_return = (current_price - take_profit) / current_price
            else:
                expected_return = 0.0

            # 计算风险分数
            risk_score = 1.0 - risk_adjusted_signal.confidence

            # 生成推理说明
            reasoning_parts = [risk_adjusted_signal.reasoning]
            reasoning_parts.append(f"基于{len(signals)}个信号的综合分析")
            reasoning_parts.append(f"预期收益: {expected_return:.2%}")

            return TradingDecision(
                action=risk_adjusted_signal.signal_type,
                symbol=symbol,
                quantity=quantity,
                price=current_price,
                confidence=risk_adjusted_signal.confidence,
                reasoning="; ".join(reasoning_parts),
                risk_score=risk_score,
                expected_return=expected_return,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now(),
                signals=signals,
                metadata={
                    "portfolio_value": portfolio_value,
                    "risk_per_trade": risk_per_trade,
                    "position_multiplier": position_multiplier,
                    "volatility": volatility
                }
            )

        except Exception as e:
            logger.error(f"Error generating final decision: {e}")
            return self._generate_error_decision(str(e))

    def _generate_error_decision(self, error_message: str) -> TradingDecision:
        """生成错误决策"""
        return TradingDecision(
            action=DecisionType.HOLD,
            symbol="ERROR",
            quantity=0,
            price=0.0,
            confidence=0.0,
            reasoning=f"Error in decision making: {error_message}",
            risk_score=1.0,
            expected_return=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            timestamp=datetime.now(),
            signals=[],
            metadata={"error": error_message}
        )

    def _record_decision(self, decision: TradingDecision):
        """记录决策"""
        try:
            self.decision_history.append(decision)

            # 限制历史记录长度
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-500:]

            # 更新性能指标
            self.performance_metrics["total_decisions"] += 1

            # 计算平均置信度
            total_confidence = sum(d.confidence for d in self.decision_history[-100:])
            self.performance_metrics["avg_confidence"] = total_confidence / min(len(self.decision_history), 100)

            logger.info(f"Decision recorded: {decision.action.value} for {decision.symbol}")

        except Exception as e:
            logger.error(f"Error recording decision: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.performance_metrics.copy()

    def get_recent_decisions(self, limit: int = 10) -> List[TradingDecision]:
        """获取最近的决策"""
        return self.decision_history[-limit:] if self.decision_history else []

    def update_model_weights(self, new_weights: Dict[str, float]):
        """更新模型权重"""
        try:
            for model, weight in new_weights.items():
                if model in self.model_weights:
                    self.model_weights[model] = max(0.0, min(1.0, weight))

            # 归一化权重
            total_weight = sum(self.model_weights.values())
            if total_weight > 0:
                for model in self.model_weights:
                    self.model_weights[model] /= total_weight

            logger.info(f"Model weights updated: {self.model_weights}")

        except Exception as e:
            logger.error(f"Error updating model weights: {e}")

    async def evaluate_decision_performance(self,
                                          decision: TradingDecision,
                                          actual_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """评估决策性能"""
        try:
            actual_return = actual_outcome.get('return', 0.0)
            actual_risk = actual_outcome.get('risk', 0.0)

            # 计算预测准确性
            prediction_accuracy = 1.0 - abs(decision.expected_return - actual_return)

            # 计算风险预测准确性
            risk_accuracy = 1.0 - abs(decision.risk_score - actual_risk)

            # 更新成功决策计数
            if actual_return > 0 and decision.action in [DecisionType.BUY, DecisionType.INCREASE]:
                self.performance_metrics["successful_decisions"] += 1
            elif actual_return < 0 and decision.action in [DecisionType.SELL, DecisionType.REDUCE]:
                self.performance_metrics["successful_decisions"] += 1

            # 计算准确率
            if self.performance_metrics["total_decisions"] > 0:
                self.performance_metrics["accuracy"] = (
                    self.performance_metrics["successful_decisions"] /
                    self.performance_metrics["total_decisions"]
                )

            evaluation_result = {
                "decision_id": id(decision),
                "prediction_accuracy": prediction_accuracy,
                "risk_accuracy": risk_accuracy,
                "actual_return": actual_return,
                "expected_return": decision.expected_return,
                "performance_impact": actual_return * decision.confidence
            }

            logger.info(f"Decision performance evaluated: accuracy={prediction_accuracy:.2f}")
            return evaluation_result

        except Exception as e:
            logger.error(f"Error evaluating decision performance: {e}")
            return {"error": str(e)}
