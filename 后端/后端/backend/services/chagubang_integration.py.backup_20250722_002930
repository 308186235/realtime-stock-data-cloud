"""
茶股帮数据源集成服务
将茶股帮实时数据集成到现有的股票交易系统后端
"""

import os
import sys
import asyncio
import threading
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 添加项目根路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chagubang_receiver import ChaguBangReceiver, start_chagubang_service
from chagubang_token_manager import TokenManager

logger = logging.getLogger(__name__)

class ChaguBangIntegrationService:
    """茶股帮集成服务"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.receiver: Optional[ChaguBangReceiver] = None
        self.running = False
        self.data_cache: Dict[str, Dict] = {}
        self.subscribers: List[callable] = []
        
        # 统计信息
        self.stats = {
            'start_time': None,
            'total_received': 0,
            'unique_stocks': 0,
            'last_update': None,
            'connection_status': 'disconnected',
            'error_count': 0
        }
        
        # 配置
        self.config = {
            'max_cache_size': 10000,
            'data_retention_hours': 24,
            'reconnect_interval': 30,
            'health_check_interval': 60
        }
    
    async def initialize(self) -> bool:
        """初始化服务"""
        try:
            logger.info("初始化茶股帮集成服务...")
            
            # 获取最佳token
            best_token = self.token_manager.get_best_token()
            if not best_token:
                logger.warning("没有可用的茶股帮Token，请先配置")
                return False
            
            # 创建接收器
            self.receiver = ChaguBangReceiver(token=best_token)
            self.receiver.add_data_callback(self._on_stock_data_received)
            
            # 启动接收线程
            self.thread = threading.Thread(target=self.receiver.start_receiving, daemon=True)
            self.thread.start()
            
            # 启动健康检查
            asyncio.create_task(self._health_check_loop())
            
            self.running = True
            self.stats['start_time'] = datetime.now().isoformat()
            
            logger.info("茶股帮集成服务初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化茶股帮集成服务失败: {e}")
            return False
    
    def _on_stock_data_received(self, stock_data: Dict[str, Any]):
        """处理接收到的股票数据"""
        try:
            code = stock_data['stock_code']
            
            # 更新缓存
            self.data_cache[code] = {
                **stock_data,
                'received_time': datetime.now().isoformat(),
                'source': 'chagubang'
            }
            
            # 限制缓存大小
            if len(self.data_cache) > self.config['max_cache_size']:
                oldest_code = min(self.data_cache.keys(), 
                                key=lambda k: self.data_cache[k].get('received_time', ''))
                del self.data_cache[oldest_code]
            
            # 更新统计
            self.stats['total_received'] += 1
            self.stats['unique_stocks'] = len(self.data_cache)
            self.stats['last_update'] = datetime.now().isoformat()
            self.stats['connection_status'] = 'connected'
            
            # 通知订阅者
            for subscriber in self.subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        asyncio.create_task(subscriber(stock_data))
                    else:
                        subscriber(stock_data)
                except Exception as e:
                    logger.error(f"通知订阅者失败: {e}")
                    
        except Exception as e:
            logger.error(f"处理股票数据失败: {e}")
            self.stats['error_count'] += 1
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                await asyncio.sleep(self.config['health_check_interval'])
                
                if self.receiver:
                    receiver_stats = self.receiver.get_stats()
                    self.stats['connection_status'] = receiver_stats.get('connection_status', 'unknown')
                    
                    # 如果连接断开，尝试重连
                    if self.stats['connection_status'] != 'connected':
                        logger.warning("检测到连接断开，尝试重连...")
                        await self._attempt_reconnect()
                
            except Exception as e:
                logger.error(f"健康检查异常: {e}")
    
    async def _attempt_reconnect(self):
        """尝试重连"""
        try:
            if self.receiver:
                self.receiver.stop_receiving()
            
            # 等待一段时间后重连
            await asyncio.sleep(self.config['reconnect_interval'])
            
            # 重新初始化
            await self.initialize()
            
        except Exception as e:
            logger.error(f"重连失败: {e}")
    
    def subscribe_to_data(self, callback: callable):
        """订阅数据更新"""
        self.subscribers.append(callback)
    
    def unsubscribe_from_data(self, callback: callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_stock_data(self, stock_code: str = None) -> Dict:
        """获取股票数据"""
        if stock_code:
            return self.data_cache.get(stock_code, {})
        return self.data_cache.copy()
    
    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        if not self.data_cache:
            return {}
        
        # 计算市场统计
        prices = [data['last_price'] for data in self.data_cache.values() if data.get('last_price')]
        changes = [data['change_pct'] for data in self.data_cache.values() if data.get('change_pct')]
        
        if not prices or not changes:
            return {}
        
        return {
            'total_stocks': len(self.data_cache),
            'avg_price': sum(prices) / len(prices),
            'avg_change': sum(changes) / len(changes),
            'rising_stocks': len([c for c in changes if c > 0]),
            'falling_stocks': len([c for c in changes if c < 0]),
            'flat_stocks': len([c for c in changes if c == 0]),
            'last_update': self.stats['last_update']
        }
    
    def get_hot_stocks(self, limit: int = 10) -> List[Dict]:
        """获取热门股票（按涨跌幅排序）"""
        stocks = list(self.data_cache.values())
        
        # 按涨跌幅排序
        hot_stocks = sorted(stocks, 
                           key=lambda x: abs(x.get('change_pct', 0)), 
                           reverse=True)
        
        return hot_stocks[:limit]
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计"""
        stats = self.stats.copy()
        
        if self.receiver:
            receiver_stats = self.receiver.get_stats()
            stats.update({
                'receiver_errors': receiver_stats.get('error_count', 0),
                'queue_size': receiver_stats.get('queue_size', 0)
            })
        
        return stats
    
    async def stop(self):
        """停止服务"""
        logger.info("停止茶股帮集成服务...")
        
        self.running = False
        
        if self.receiver:
            self.receiver.stop_receiving()
        
        logger.info("茶股帮集成服务已停止")


# 全局服务实例
_chagubang_service: Optional[ChaguBangIntegrationService] = None

async def get_chagubang_service() -> ChaguBangIntegrationService:
    """获取茶股帮服务实例"""
    global _chagubang_service
    
    if _chagubang_service is None:
        _chagubang_service = ChaguBangIntegrationService()
        await _chagubang_service.initialize()
    
    return _chagubang_service

async def initialize_chagubang_service() -> bool:
    """初始化茶股帮服务"""
    try:
        service = await get_chagubang_service()
        return service.running
    except Exception as e:
        logger.error(f"初始化茶股帮服务失败: {e}")
        return False

# API辅助函数
async def get_realtime_stock_data(stock_code: str = None) -> Dict:
    """获取实时股票数据（API接口）"""
    service = await get_chagubang_service()
    return service.get_stock_data(stock_code)

async def get_market_overview_data() -> Dict[str, Any]:
    """获取市场概览数据（API接口）"""
    service = await get_chagubang_service()
    return service.get_market_overview()

async def get_hot_stocks_data(limit: int = 10) -> List[Dict]:
    """获取热门股票数据（API接口）"""
    service = await get_chagubang_service()
    return service.get_hot_stocks(limit)

async def get_chagubang_stats() -> Dict[str, Any]:
    """获取茶股帮服务统计（API接口）"""
    service = await get_chagubang_service()
    return service.get_service_stats()

# 数据订阅装饰器
def subscribe_to_stock_data(callback: callable):
    """数据订阅装饰器"""
    async def wrapper():
        service = await get_chagubang_service()
        service.subscribe_to_data(callback)
    
    asyncio.create_task(wrapper())
    return callback
