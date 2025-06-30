"""
实时股票服务 - 集成所有组件的主服务
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
import time
from dataclasses import asdict

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.realtime_stock_receiver import RealtimeStockReceiver, create_receiver
from services.stock_data_parser import parse_stock_batch, StockData
from services.redis_stock_storage import redis_stock_storage
from services.stock_data_consumer import stock_data_consumer

logger = logging.getLogger(__name__)

class RealtimeStockService:
    """实时股票服务 - 主服务类"""
    
    def __init__(self):
        # 组件实例
        self.receiver: Optional[RealtimeStockReceiver] = None
        self.storage = redis_stock_storage
        self.consumer = stock_data_consumer
        
        # 配置
        self.config = {
            'api_key': 'QT_wat5QfcJ6N9pDZM5',
            'host': '',  # 需要配置实际服务器地址
            'port': 0,   # 需要配置实际端口
            'token': '', # 需要配置实际token
        }
        
        # 运行状态
        self.running = False
        self.components_started = {
            'receiver': False,
            'storage': False,
            'consumer': False
        }
        
        # 统计信息
        self.stats = {
            'service_start_time': 0,
            'total_received': 0,
            'total_parsed': 0,
            'total_stored': 0,
            'total_consumed': 0,
            'error_count': 0,
            'uptime_seconds': 0
        }
        
        # 回调函数
        self.data_callbacks: List[Callable] = []
        
    def configure(self, host: str, port: int, token: str):
        """配置连接参数"""
        self.config.update({
            'host': host,
            'port': port,
            'token': token
        })
        logger.info(f"配置更新: {host}:{port}")
    
    async def start(self):
        """启动实时股票服务"""
        try:
            logger.info("启动实时股票服务...")
            
            if not self.config['host'] or not self.config['port'] or not self.config['token']:
                raise ValueError("请先配置连接参数 (host, port, token)")
            
            self.running = True
            self.stats['service_start_time'] = time.time()
            
            # 1. 启动Redis存储服务
            await self._start_storage()
            
            # 2. 启动数据消费者
            await self._start_consumer()
            
            # 3. 启动数据接收器
            await self._start_receiver()
            
            # 4. 设置数据流
            self._setup_data_flow()
            
            logger.info("实时股票服务启动成功")
            
        except Exception as e:
            logger.error(f"启动实时股票服务失败: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """停止实时股票服务"""
        logger.info("停止实时股票服务...")
        
        self.running = False
        
        # 停止各个组件
        if self.receiver and self.components_started['receiver']:
            try:
                self.receiver.stop()
                self.components_started['receiver'] = False
            except Exception as e:
                logger.error(f"停止接收器失败: {str(e)}")
        
        if self.components_started['consumer']:
            try:
                await self.consumer.stop()
                self.components_started['consumer'] = False
            except Exception as e:
                logger.error(f"停止消费者失败: {str(e)}")
        
        if self.components_started['storage']:
            try:
                self.storage.stop()
                self.components_started['storage'] = False
            except Exception as e:
                logger.error(f"停止存储服务失败: {str(e)}")
        
        logger.info("实时股票服务已停止")
    
    async def _start_storage(self):
        """启动存储服务"""
        try:
            self.storage.start()
            self.components_started['storage'] = True
            logger.info("Redis存储服务启动成功")
        except Exception as e:
            logger.error(f"启动存储服务失败: {str(e)}")
            raise
    
    async def _start_consumer(self):
        """启动消费者"""
        try:
            await self.consumer.start()
            self.components_started['consumer'] = True
            logger.info("数据消费者启动成功")
        except Exception as e:
            logger.error(f"启动消费者失败: {str(e)}")
            raise
    
    async def _start_receiver(self):
        """启动接收器"""
        try:
            # 创建接收器实例
            self.receiver = create_receiver(
                host=self.config['host'],
                port=self.config['port'],
                token=self.config['token']
            )
            
            # 启动接收器
            self.receiver.start()
            self.components_started['receiver'] = True
            logger.info("数据接收器启动成功")
            
        except Exception as e:
            logger.error(f"启动接收器失败: {str(e)}")
            raise
    
    def _setup_data_flow(self):
        """设置数据流"""
        try:
            # 设置接收器的数据回调
            def on_data_received(batch_data):
                """接收器数据回调"""
                try:
                    # 解析数据
                    parsed_stocks = parse_stock_batch(batch_data)
                    
                    if parsed_stocks:
                        # 存储到Redis
                        self.storage.store_stock_batch(parsed_stocks)
                        
                        # 调用用户回调
                        for callback in self.data_callbacks:
                            try:
                                callback(parsed_stocks)
                            except Exception as e:
                                logger.error(f"用户回调执行失败: {str(e)}")
                        
                        # 更新统计
                        self.stats['total_parsed'] += len(parsed_stocks)
                
                except Exception as e:
                    logger.error(f"数据流处理失败: {str(e)}")
                    self.stats['error_count'] += 1
            
            # 添加回调到接收器
            if self.receiver:
                self.receiver.add_data_callback(on_data_received)
            
            logger.info("数据流设置完成")
            
        except Exception as e:
            logger.error(f"设置数据流失败: {str(e)}")
            raise
    
    def add_data_callback(self, callback: Callable):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)
        logger.debug("添加数据回调函数")
    
    def remove_data_callback(self, callback: Callable):
        """移除数据回调函数"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
            logger.debug("移除数据回调函数")
    
    # ==================== 订阅接口 ====================
    
    def subscribe_stock(self, stock_code: str, callback: Callable):
        """订阅单只股票"""
        self.consumer.subscribe_stock(stock_code, callback)
    
    def unsubscribe_stock(self, stock_code: str, callback: Callable):
        """取消订阅单只股票"""
        self.consumer.unsubscribe_stock(stock_code, callback)
    
    def subscribe_market(self, market: str, callback: Callable):
        """订阅整个市场"""
        self.consumer.subscribe_market(market, callback)
    
    def unsubscribe_market(self, market: str, callback: Callable):
        """取消订阅市场"""
        self.consumer.unsubscribe_market(market, callback)
    
    def subscribe_all(self, callback: Callable):
        """订阅所有股票"""
        self.consumer.subscribe_all(callback)
    
    def unsubscribe_all(self, callback: Callable):
        """取消订阅所有股票"""
        self.consumer.unsubscribe_all(callback)
    
    # ==================== 数据查询接口 ====================
    
    async def get_realtime_data(self, stock_code: str) -> Optional[Dict]:
        """获取实时数据"""
        return await self.consumer.get_latest_data(stock_code)
    
    async def get_stock_stream(self, stock_code: str, count: int = 100) -> List[Dict]:
        """获取股票时间序列数据"""
        return self.storage.get_stock_stream(stock_code, count)
    
    async def get_market_summary(self, market: str) -> Dict:
        """获取市场概况"""
        return await self.consumer.get_market_summary(market)
    
    async def get_market_top_stocks(self, market: str, metric: str = 'volume', count: int = 50) -> List[Dict]:
        """获取市场热门股票"""
        return self.storage.get_market_top_stocks(market, metric, count)
    
    # ==================== 状态和统计 ====================
    
    def is_running(self) -> bool:
        """检查服务是否运行中"""
        return self.running and all(self.components_started.values())
    
    def is_connected(self) -> bool:
        """检查是否连接到数据源"""
        return self.receiver and self.receiver.is_connected() if self.receiver else False
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计"""
        # 更新运行时间
        if self.stats['service_start_time'] > 0:
            self.stats['uptime_seconds'] = time.time() - self.stats['service_start_time']
        
        # 收集各组件统计
        component_stats = {}
        
        if self.receiver:
            component_stats['receiver'] = self.receiver.get_stats()
        
        component_stats['storage'] = self.storage.get_stats()
        component_stats['consumer'] = self.consumer.get_stats()
        
        return {
            'service': self.stats,
            'components': component_stats,
            'status': {
                'running': self.running,
                'connected': self.is_connected(),
                'components_started': self.components_started
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'timestamp': time.time(),
            'components': {}
        }
        
        try:
            # 检查各组件状态
            if self.receiver:
                health['components']['receiver'] = {
                    'status': 'connected' if self.receiver.is_connected() else 'disconnected',
                    'stats': self.receiver.get_stats()
                }
            
            # 检查Redis连接
            try:
                self.storage.redis_client.ping()
                health['components']['storage'] = {
                    'status': 'connected',
                    'stats': self.storage.get_stats()
                }
            except Exception:
                health['components']['storage'] = {
                    'status': 'disconnected',
                    'error': 'Redis连接失败'
                }
                health['status'] = 'unhealthy'
            
            # 检查消费者
            health['components']['consumer'] = {
                'status': 'running' if self.consumer.running else 'stopped',
                'stats': self.consumer.get_stats()
            }
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    # ==================== 配置管理 ====================
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        config = self.config.copy()
        # 隐藏敏感信息
        if config.get('token'):
            config['token'] = '***'
        return config
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"配置更新: {key} = {value if key != 'token' else '***'}")

# 全局服务实例
realtime_stock_service = RealtimeStockService()

# 便捷函数
async def start_realtime_service(host: str, port: int, token: str):
    """启动实时股票服务"""
    realtime_stock_service.configure(host, port, token)
    await realtime_stock_service.start()
    return realtime_stock_service

async def stop_realtime_service():
    """停止实时股票服务"""
    await realtime_stock_service.stop()

def get_realtime_service() -> RealtimeStockService:
    """获取实时股票服务实例"""
    return realtime_stock_service
