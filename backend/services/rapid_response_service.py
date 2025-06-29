import logging
import time
import asyncio
import json
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
import threading
import queue

logger = logging.getLogger(__name__)

class RapidResponseService:
    """
    快速响应服务,用于处理高优先级的市场信号和提供快速反馈。
    该服务通过内存缓存,优先级队列和异步处理提高响应速度。
    """
    
    # 在__init__方法中增加LRU缓存结构
    def __init__(self):
        self.cache = OrderedDict()  # 替换原有字典
        self.cache_capacity = 1000  # 最大缓存条目数
    
    # 新增缓存淘汰方法
    def _evict_cache(self):
        while len(self.cache) > self.cache_capacity:
            self.cache.popitem(last=False)
    
    # 修改get_cached_data方法
    async def get_cached_data(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache.pop(key)
            if time.time() - entry["timestamp"] < self.cache_ttl:
                self.cache[key] = entry  # 更新访问顺序
                return entry["data"]
        return None
    
    async def clear_cache(self, key: str = None):
        """清除缓存"""
        if key:
            if key in self.cache:
                del self.cache[key]
        else:
            self.cache.clear()
    
    async def enqueue_signal(self, signal_type: str, data: Dict, priority: int = None):
        """
        将市场信号加入队列处理
        
        Args:
            signal_type: 信号类型
            data: 信号数据
            priority: 优先级(若未指定则根据信号类型确定)
        """
        # 确定优先级
        if priority is None:
            priority = self.signal_priorities.get(signal_type, 5)
            
            # 特殊处理:价格变化
            if signal_type == "price_change":
                # 价格变化较大,提高优先级
                if data.get("price_change_pct", 0) > 2.0:  # 大于2%的价格变化视为较大
                    priority = self.signal_priorities.get("price_change_major", 2)
                else:
                    priority = self.signal_priorities.get("price_change_minor", 4)
        
        # 构建信号对象
        signal = {
            "type": signal_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        # 放入优先级队列
        await self.signal_queue.put((priority, signal))
        
        # 同时放入后台处理队列
        self.background_queue.put((priority, signal))
        
        logger.debug(f"信号已加入队列:{signal_type},优先级:{priority}")
        
        # 对于高优先级信号(优先级1-2),直接发送给所有WebSocket连接
        if priority <= 2:
            await self._broadcast_signal(signal)
            
        return {
            "status": "enqueued",
            "signal_type": signal_type,
            "priority": priority,
            "timestamp": signal["timestamp"]
        }
    
    async def process_trading_signal(self, trading_signal: Dict) -> Dict:
        """
        处理交易信号(高优先级)
        
        Args:
            trading_signal: 交易信号数据
            
        Returns:
            处理结果
        """
        signal_type = trading_signal.get("signal", "UNKNOWN")
        
        # 记录信号
        signal_id = f"{signal_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.recent_signals[signal_id] = {
            "type": "trading_signal",
            "data": trading_signal,
            "timestamp": datetime.now().isoformat(),
            "processed": True
        }
        
        # 加入队列以便可能的后续处理
        await self.enqueue_signal("trading_signal", trading_signal, priority=1)
        
        # 立即通知所有WebSocket连接
        await self._broadcast_signal({
            "type": "trading_signal",
            "data": trading_signal,
            "timestamp": datetime.now().isoformat(),
            "id": signal_id
        })
        
        return {
            "status": "processed",
            "signal_id": signal_id,
            "signal_type": signal_type,
            "action_required": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_price_alert(self, price_data: Dict) -> Dict:
        """
        处理价格警报
        
        Args:
            price_data: 价格数据
            
        Returns:
            处理结果
        """
        price_change = price_data.get("price_change", 0)
        price_change_pct = price_data.get("price_change_pct", 0)
        
        # 确定优先级
        priority = 4  # 默认中等优先级
        if abs(price_change_pct) >= 5.0:
            priority = 1  # 大幅变动,最高优先级
        elif abs(price_change_pct) >= 2.0:
            priority = 2  # 明显变动,高优先级
        
        # 构建警报数据
        alert_data = {
            "type": "price_change",
            "price_change": float(price_change),
            "price_change_pct": float(price_change_pct),
            "current_price": float(price_data.get("current_price", 0)),
            "direction": "up" if price_change > 0 else "down",
            "timestamp": datetime.now().isoformat(),
            "message": f"价格{'上涨' if price_change > 0 else '下跌'}{abs(price_change_pct):.2f}%,当前价格: {price_data.get('current_price', 0):.2f}"
        }
        
        # 加入队列处理
        await self.enqueue_signal("price_change", alert_data, priority=priority)
        
        return {
            "status": "processing",
            "alert_type": "price_change",
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """
        获取最近处理的信号
        
        Args:
            limit: 返回的最大数量
            
        Returns:
            最近信号列表
        """
        # 将字典转换为列表,按时间戳排序
        signals = list(self.recent_signals.values())
        signals.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 返回限制数量的信号
        return signals[:limit]
    
    async def _process_signal_queue(self):
        """处理信号队列(异步)"""
        while self.processing:
            try:
                # 非阻塞方式尝试获取队列项目
                try:
                    priority, signal = await asyncio.wait_for(
                        self.signal_queue.get(), 
                        timeout=0.5
                    )
                except asyncio.TimeoutError:
                    continue
                
                # 处理信号
                logger.debug(f"处理信号:{signal['type']},优先级:{priority}")
                
                # 标记为已处理
                signal["processed"] = True
                
                # 对于需要广播的信号,发送给所有WebSocket连接
                # 优先级3以下的信号已在enqueue_signal时发送
                if priority <= 3:
                    await self._broadcast_signal(signal)
                
                # 保存到最近信号中
                signal_id = f"{signal['type']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.recent_signals[signal_id] = signal
                
                # 限制最近信号的数量
                if len(self.recent_signals) > 100:
                    # 删除最旧的信号
                    oldest_key = min(self.recent_signals.keys(), key=lambda k: self.recent_signals[k]["timestamp"])
                    del self.recent_signals[oldest_key]
                
                # 完成队列任务
                self.signal_queue.task_done()
                
            except Exception as e:
                logger.error(f"处理信号队列时出错:{e}")
                await asyncio.sleep(1)  # 出错时稍作延迟
    
    def _background_worker(self):
        """后台工作线程,处理非关键任务"""
        while self.processing:
            try:
                # 非阻塞方式尝试获取队列项目
                try:
                    priority, signal = self.background_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # 在后台处理非关键信号
                # 例如:记录到文件,发送通知邮件等
                
                # 这里可以添加其他后台处理逻辑
                
                # 完成队列任务
                self.background_queue.task_done()
                
            except Exception as e:
                logger.error(f"后台处理线程出错:{e}")
                time.sleep(1)  # 出错时稍作延迟
    
    async def _broadcast_signal(self, signal):
        """向所有WebSocket连接广播信号"""
        disconnected_clients = []
        
        for client_id, websocket in self.websocket_connections.items():
            try:
                await websocket.send_json({
                    "type": "alert",
                    "alert": signal
                })
            except Exception as e:
                logger.error(f"向客户端 {client_id} 发送信号时出错:{e}")
                disconnected_clients.append(client_id)
        
        # 移除断开的连接
        for client_id in disconnected_clients:
            await self.unregister_websocket(client_id)
