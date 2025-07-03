#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据流管理器
管理从茶股帮数据接收到Agent决策再到本地执行的完整数据流
"""

import asyncio
import json
import logging
import socket
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """股票数据结构"""
    symbol: str
    name: str
    price: float
    volume: int
    amount: float
    change_percent: float
    timestamp: str

@dataclass
class AgentDecision:
    """Agent决策结构"""
    action: str  # buy/sell/hold
    stock_code: str
    stock_name: str
    quantity: int
    price: Optional[float]
    confidence: float
    reason: str
    timestamp: str

class ChaguBangClient:
    """茶股帮数据客户端"""
    
    def __init__(self, host: str, port: int, token: str):
        self.host = host
        self.port = port
        self.token = token
        self.socket = None
        self.connected = False
        
    async def connect(self):
        """连接茶股帮服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # 发送token认证
            self.socket.send(self.token.encode('utf-8'))
            
            self.connected = True
            logger.info(f"✅ 茶股帮连接成功: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ 茶股帮连接失败: {e}")
            self.connected = False
            raise
    
    async def stream_data(self):
        """流式接收股票数据"""
        if not self.connected:
            await self.connect()
        
        buffer = ""
        
        while self.connected:
            try:
                # 接收数据
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # 处理完整的JSON消息
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            stock_data = json.loads(line.strip())
                            yield self._parse_stock_data(stock_data)
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.error(f"❌ 接收数据失败: {e}")
                self.connected = False
                break
    
    def _parse_stock_data(self, raw_data: Dict) -> StockData:
        """解析股票数据"""
        return StockData(
            symbol=raw_data.get('symbol', ''),
            name=raw_data.get('name', ''),
            price=float(raw_data.get('price', 0)),
            volume=int(raw_data.get('volume', 0)),
            amount=float(raw_data.get('amount', 0)),
            change_percent=float(raw_data.get('change_percent', 0)),
            timestamp=raw_data.get('timestamp', datetime.now().isoformat())
        )
    
    def disconnect(self):
        """断开连接"""
        if self.socket:
            self.socket.close()
        self.connected = False

class AgentAnalyzer:
    """Agent分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.decision_history = []
        
    async def analyze(self, stock_data: StockData) -> List[AgentDecision]:
        """分析股票数据并生成决策"""
        decisions = []
        
        try:
            # 检查北交所权限
            if stock_data.symbol.startswith('BJ') and not self.config.get('enable_beijing_exchange', False):
                logger.debug(f"跳过北交所股票: {stock_data.symbol} (权限未开启)")
                return decisions
            
            # 简单的决策逻辑示例
            if stock_data.change_percent > 5.0 and stock_data.volume > 1000000:
                # 涨幅超过5%且成交量大，考虑买入
                decision = AgentDecision(
                    action="buy",
                    stock_code=stock_data.symbol,
                    stock_name=stock_data.name,
                    quantity=100,  # 固定100股
                    price=stock_data.price,
                    confidence=0.7,
                    reason=f"涨幅{stock_data.change_percent}%，成交量{stock_data.volume}",
                    timestamp=datetime.now().isoformat()
                )
                decisions.append(decision)
                
            elif stock_data.change_percent < -3.0:
                # 跌幅超过3%，考虑卖出
                decision = AgentDecision(
                    action="sell",
                    stock_code=stock_data.symbol,
                    stock_name=stock_data.name,
                    quantity=100,
                    price=stock_data.price,
                    confidence=0.6,
                    reason=f"跌幅{stock_data.change_percent}%，止损",
                    timestamp=datetime.now().isoformat()
                )
                decisions.append(decision)
            
            # 记录决策历史
            self.decision_history.extend(decisions)
            
            # 限制历史记录长度
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-1000:]
            
        except Exception as e:
            logger.error(f"❌ 分析股票数据失败: {e}")
        
        return decisions

class DecisionExecutor:
    """决策执行器"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.execution_history = []
        
    async def execute_decision(self, decision: AgentDecision) -> Dict[str, Any]:
        """执行Agent决策"""
        try:
            logger.info(f"🤖 执行Agent决策: {decision.action} {decision.stock_code} {decision.quantity}股")
            
            # 构造交易命令
            command = {
                "type": "trade",
                "id": f"decision_{int(time.time())}",
                "data": {
                    "action": decision.action,
                    "stock_code": decision.stock_code,
                    "quantity": decision.quantity,
                    "price": decision.price
                },
                "metadata": {
                    "source": "agent_decision",
                    "confidence": decision.confidence,
                    "reason": decision.reason,
                    "timestamp": decision.timestamp
                }
            }
            
            # 发送到本地Agent执行
            result = await self.websocket_manager.send_to_local_agent(command)
            
            # 记录执行结果
            execution_record = {
                "decision": decision,
                "command": command,
                "result": result,
                "executed_at": datetime.now().isoformat()
            }
            
            self.execution_history.append(execution_record)
            
            # 限制历史记录长度
            if len(self.execution_history) > 500:
                self.execution_history = self.execution_history[-500:]
            
            logger.info(f"{'✅' if result.get('success') else '❌'} 决策执行结果: {result.get('message', '未知')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 执行决策失败: {e}")
            return {
                "success": False,
                "message": f"执行失败: {e}",
                "timestamp": datetime.now().isoformat()
            }

class DataFlowManager:
    """数据流管理器"""
    
    def __init__(self, config: Dict[str, Any], websocket_manager):
        self.config = config
        self.websocket_manager = websocket_manager
        
        # 初始化组件
        self.chagubang_client = ChaguBangClient(
            host=config.get('chagubang_host', 'l1.chagubang.com'),
            port=config.get('chagubang_port', 6380),
            token=config.get('chagubang_token', 'QT_wat5QfcJ6N9pDZM5')
        )
        
        self.agent_analyzer = AgentAnalyzer(config)
        self.decision_executor = DecisionExecutor(websocket_manager)
        
        # 运行状态
        self.running = False
        self.stats = {
            "data_received": 0,
            "decisions_made": 0,
            "trades_executed": 0,
            "start_time": None,
            "last_data_time": None
        }
    
    async def start_data_flow(self):
        """启动数据流"""
        logger.info("🚀 启动数据流管理器")
        self.running = True
        self.stats["start_time"] = datetime.now().isoformat()
        
        try:
            # 连接茶股帮
            await self.chagubang_client.connect()
            
            # 开始数据流处理
            async for stock_data in self.chagubang_client.stream_data():
                if not self.running:
                    break
                
                # 更新统计
                self.stats["data_received"] += 1
                self.stats["last_data_time"] = datetime.now().isoformat()
                
                # Agent分析
                decisions = await self.agent_analyzer.analyze(stock_data)
                
                if decisions:
                    self.stats["decisions_made"] += len(decisions)
                    logger.info(f"📊 生成{len(decisions)}个决策: {stock_data.symbol}")
                    
                    # 执行决策
                    for decision in decisions:
                        result = await self.decision_executor.execute_decision(decision)
                        if result.get("success"):
                            self.stats["trades_executed"] += 1
                
                # 广播实时数据到前端
                await self._broadcast_real_time_data(stock_data, decisions)
                
        except Exception as e:
            logger.error(f"❌ 数据流处理失败: {e}")
        finally:
            self.chagubang_client.disconnect()
            logger.info("🛑 数据流管理器已停止")
    
    async def _broadcast_real_time_data(self, stock_data: StockData, decisions: List[AgentDecision]):
        """广播实时数据到前端"""
        try:
            message = {
                "type": "real_time_data",
                "stock_data": {
                    "symbol": stock_data.symbol,
                    "name": stock_data.name,
                    "price": stock_data.price,
                    "volume": stock_data.volume,
                    "change_percent": stock_data.change_percent,
                    "timestamp": stock_data.timestamp
                },
                "decisions": [
                    {
                        "action": d.action,
                        "stock_code": d.stock_code,
                        "quantity": d.quantity,
                        "confidence": d.confidence,
                        "reason": d.reason
                    } for d in decisions
                ],
                "stats": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            # 广播到所有连接的前端客户端
            await self.websocket_manager.broadcast_to_clients(message)
            
        except Exception as e:
            logger.error(f"❌ 广播实时数据失败: {e}")
    
    def stop_data_flow(self):
        """停止数据流"""
        logger.info("🛑 停止数据流管理器")
        self.running = False
        self.chagubang_client.disconnect()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "running": self.running,
            "decision_history_count": len(self.agent_analyzer.decision_history),
            "execution_history_count": len(self.decision_executor.execution_history)
        }
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的决策"""
        recent = self.agent_analyzer.decision_history[-limit:]
        return [
            {
                "action": d.action,
                "stock_code": d.stock_code,
                "stock_name": d.stock_name,
                "quantity": d.quantity,
                "price": d.price,
                "confidence": d.confidence,
                "reason": d.reason,
                "timestamp": d.timestamp
            } for d in recent
        ]
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的执行记录"""
        recent = self.decision_executor.execution_history[-limit:]
        return [
            {
                "decision": {
                    "action": record["decision"].action,
                    "stock_code": record["decision"].stock_code,
                    "quantity": record["decision"].quantity,
                    "confidence": record["decision"].confidence
                },
                "result": record["result"],
                "executed_at": record["executed_at"]
            } for record in recent
        ]
