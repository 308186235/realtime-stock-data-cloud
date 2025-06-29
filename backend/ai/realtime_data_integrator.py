"""
实时数据集成器
集成多种数据源，为AI决策提供实时、准确的市场数据
"""

import asyncio
import aiohttp
import websockets
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import redis
import sqlite3
import os

logger = logging.getLogger("RealtimeDataIntegrator")

class DataSource(Enum):
    """数据源枚举"""
    STOCK_API = "stock_api"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"

class DataType(Enum):
    """数据类型枚举"""
    PRICE = "price"
    VOLUME = "volume"
    ORDER_BOOK = "order_book"
    NEWS = "news"
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"

@dataclass
class MarketData:
    """市场数据类"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float = 0.0
    ask: float = 0.0
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    market_cap: float = 0.0
    pe_ratio: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class DataQuality:
    """数据质量指标"""
    completeness: float
    timeliness: float
    accuracy: float
    consistency: float
    overall_score: float
    last_updated: datetime

class RealtimeDataIntegrator:
    """
    实时数据集成器
    负责从多个数据源获取、处理和分发实时市场数据
    """
    
    def __init__(self, config: Dict = None):
        """
        初始化实时数据集成器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 数据源配置
        self.data_sources = {
            "primary_api": {
                "url": self.config.get("primary_api_url", "https://api.example.com"),
                "api_key": self.config.get("primary_api_key", ""),
                "rate_limit": self.config.get("primary_rate_limit", 100),
                "enabled": True
            },
            "backup_api": {
                "url": self.config.get("backup_api_url", "https://backup-api.example.com"),
                "api_key": self.config.get("backup_api_key", ""),
                "rate_limit": self.config.get("backup_rate_limit", 50),
                "enabled": True
            },
            "websocket": {
                "url": self.config.get("websocket_url", "wss://stream.example.com"),
                "enabled": True
            }
        }
        
        # 缓存配置
        self.cache_config = {
            "redis_host": self.config.get("redis_host", "localhost"),
            "redis_port": self.config.get("redis_port", 6379),
            "redis_db": self.config.get("redis_db", 0),
            "cache_ttl": self.config.get("cache_ttl", 300),  # 5分钟
            "use_redis": self.config.get("use_redis", True)
        }
        
        # 数据库配置
        self.db_config = {
            "db_path": self.config.get("db_path", "data/market_data.db"),
            "batch_size": self.config.get("batch_size", 1000),
            "retention_days": self.config.get("retention_days", 30)
        }
        
        # 数据质量配置
        self.quality_config = {
            "max_delay_seconds": self.config.get("max_delay_seconds", 10),
            "min_completeness": self.config.get("min_completeness", 0.95),
            "outlier_threshold": self.config.get("outlier_threshold", 3.0)
        }
        
        # 运行状态
        self.running = False
        self.data_cache = {}
        self.subscribers = {}
        self.data_quality = {}
        
        # 连接池
        self.redis_client = None
        self.db_connection = None
        self.websocket_connections = {}
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "data_points_processed": 0,
            "last_update_time": None
        }
        
        logger.info("Realtime Data Integrator initialized")
    
    async def start(self):
        """启动数据集成器"""
        try:
            logger.info("Starting Realtime Data Integrator...")
            
            # 初始化连接
            await self._init_connections()
            
            # 初始化数据库
            await self._init_database()
            
            # 启动数据收集任务
            self.running = True
            
            # 启动各种数据收集任务
            tasks = [
                self._start_api_data_collection(),
                self._start_websocket_data_collection(),
                self._start_data_quality_monitoring(),
                self._start_cache_cleanup(),
                self._start_database_maintenance()
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("Realtime Data Integrator started successfully")
            
        except Exception as e:
            logger.error(f"Error starting data integrator: {e}")
            raise
    
    async def stop(self):
        """停止数据集成器"""
        try:
            logger.info("Stopping Realtime Data Integrator...")
            
            self.running = False
            
            # 关闭连接
            await self._close_connections()
            
            # 关闭线程池
            self.executor.shutdown(wait=True)
            
            logger.info("Realtime Data Integrator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping data integrator: {e}")
    
    async def _init_connections(self):
        """初始化连接"""
        try:
            # 初始化Redis连接
            if self.cache_config["use_redis"]:
                try:
                    self.redis_client = redis.Redis(
                        host=self.cache_config["redis_host"],
                        port=self.cache_config["redis_port"],
                        db=self.cache_config["redis_db"],
                        decode_responses=True
                    )
                    # 测试连接
                    self.redis_client.ping()
                    logger.info("Redis connection established")
                except Exception as e:
                    logger.warning(f"Redis connection failed: {e}")
                    self.redis_client = None
            
        except Exception as e:
            logger.error(f"Error initializing connections: {e}")
    
    async def _init_database(self):
        """初始化数据库"""
        try:
            db_dir = os.path.dirname(self.db_config["db_path"])
            os.makedirs(db_dir, exist_ok=True)
            
            self.db_connection = sqlite3.connect(self.db_config["db_path"], check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # 创建市场数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER,
                    timestamp DATETIME NOT NULL,
                    bid REAL,
                    ask REAL,
                    high REAL,
                    low REAL,
                    open REAL,
                    change_percent REAL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON market_data(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON market_data(timestamp)')
            
            self.db_connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    async def _start_api_data_collection(self):
        """启动API数据收集"""
        try:
            while self.running:
                # 获取需要更新的股票列表
                symbols = await self._get_symbols_to_update()
                
                # 批量获取数据
                for symbol_batch in self._batch_symbols(symbols, 50):
                    try:
                        data = await self._fetch_api_data(symbol_batch)
                        await self._process_market_data(data)
                    except Exception as e:
                        logger.error(f"Error fetching API data for batch: {e}")
                
                # 等待下一次更新
                await asyncio.sleep(3)  # 3秒更新间隔
                
        except Exception as e:
            logger.error(f"Error in API data collection: {e}")
    
    async def _start_websocket_data_collection(self):
        """启动WebSocket数据收集"""
        try:
            if not self.data_sources["websocket"]["enabled"]:
                return
            
            websocket_url = self.data_sources["websocket"]["url"]
            
            while self.running:
                try:
                    async with websockets.connect(websocket_url) as websocket:
                        logger.info("WebSocket connection established")
                        
                        # 订阅数据流
                        subscribe_message = {
                            "action": "subscribe",
                            "symbols": await self._get_symbols_to_update()
                        }
                        await websocket.send(json.dumps(subscribe_message))
                        
                        # 接收数据
                        async for message in websocket:
                            try:
                                data = json.loads(message)
                                await self._process_websocket_data(data)
                            except Exception as e:
                                logger.error(f"Error processing WebSocket message: {e}")
                                
                except Exception as e:
                    logger.error(f"WebSocket connection error: {e}")
                    await asyncio.sleep(5)  # 重连延迟
                    
        except Exception as e:
            logger.error(f"Error in WebSocket data collection: {e}")
    
    async def _fetch_api_data(self, symbols: List[str]) -> List[MarketData]:
        """从API获取数据"""
        try:
            self.stats["total_requests"] += 1
            
            # 尝试主要API
            primary_source = self.data_sources["primary_api"]
            if primary_source["enabled"]:
                try:
                    data = await self._fetch_from_source(primary_source, symbols)
                    self.stats["successful_requests"] += 1
                    return data
                except Exception as e:
                    logger.warning(f"Primary API failed: {e}")
            
            # 尝试备用API
            backup_source = self.data_sources["backup_api"]
            if backup_source["enabled"]:
                try:
                    data = await self._fetch_from_source(backup_source, symbols)
                    self.stats["successful_requests"] += 1
                    return data
                except Exception as e:
                    logger.warning(f"Backup API failed: {e}")
            
            self.stats["failed_requests"] += 1
            return []
            
        except Exception as e:
            logger.error(f"Error fetching API data: {e}")
            self.stats["failed_requests"] += 1
            return []
    
    async def _fetch_from_source(self, source: Dict, symbols: List[str]) -> List[MarketData]:
        """从指定数据源获取数据"""
        try:
            url = source["url"]
            api_key = source["api_key"]
            
            # 构建请求参数
            params = {
                "symbols": ",".join(symbols),
                "apikey": api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_api_response(data)
                    else:
                        raise Exception(f"API request failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error fetching from source: {e}")
            raise
    
    def _parse_api_response(self, response_data: Dict) -> List[MarketData]:
        """解析API响应数据"""
        try:
            market_data_list = []
            
            # 假设API返回格式
            if "data" in response_data:
                for item in response_data["data"]:
                    market_data = MarketData(
                        symbol=item.get("symbol", ""),
                        price=float(item.get("price", 0)),
                        volume=int(item.get("volume", 0)),
                        timestamp=datetime.now(),
                        bid=float(item.get("bid", 0)),
                        ask=float(item.get("ask", 0)),
                        high=float(item.get("high", 0)),
                        low=float(item.get("low", 0)),
                        open=float(item.get("open", 0)),
                        change=float(item.get("change", 0)),
                        change_percent=float(item.get("change_percent", 0)),
                        metadata=item.get("metadata", {})
                    )
                    market_data_list.append(market_data)
            
            return market_data_list
            
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            return []

    async def _process_market_data(self, market_data_list: List[MarketData]):
        """处理市场数据"""
        try:
            for market_data in market_data_list:
                # 数据质量检查
                if await self._validate_data_quality(market_data):
                    # 更新缓存
                    await self._update_cache(market_data)

                    # 保存到数据库
                    await self._save_to_database(market_data)

                    # 通知订阅者
                    await self._notify_subscribers(market_data)

                    self.stats["data_points_processed"] += 1

            self.stats["last_update_time"] = datetime.now()

        except Exception as e:
            logger.error(f"Error processing market data: {e}")

    async def _validate_data_quality(self, market_data: MarketData) -> bool:
        """验证数据质量"""
        try:
            # 检查必要字段
            if not market_data.symbol or market_data.price <= 0:
                return False

            # 检查时效性
            time_diff = (datetime.now() - market_data.timestamp).total_seconds()
            if time_diff > self.quality_config["max_delay_seconds"]:
                return False

            # 检查异常值
            if market_data.symbol in self.data_cache:
                cached_data = self.data_cache[market_data.symbol]
                if cached_data and cached_data.price > 0:
                    price_change = abs(market_data.price - cached_data.price) / cached_data.price
                    if price_change > 0.20:  # 20%的价格变动阈值
                        logger.warning(f"Unusual price change for {market_data.symbol}: {price_change:.2%}")

            return True

        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return False

    async def _update_cache(self, market_data: MarketData):
        """更新缓存"""
        try:
            # 更新内存缓存
            self.data_cache[market_data.symbol] = market_data

            # 更新Redis缓存
            if self.redis_client:
                try:
                    cache_key = f"market_data:{market_data.symbol}"
                    cache_value = json.dumps(asdict(market_data), default=str)
                    self.redis_client.setex(
                        cache_key,
                        self.cache_config["cache_ttl"],
                        cache_value
                    )
                    self.stats["cache_hits"] += 1
                except Exception as e:
                    logger.error(f"Error updating Redis cache: {e}")

        except Exception as e:
            logger.error(f"Error updating cache: {e}")

    async def _save_to_database(self, market_data: MarketData):
        """保存到数据库"""
        try:
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO market_data
                    (symbol, price, volume, timestamp, bid, ask, high, low, open, change_percent, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    market_data.symbol,
                    market_data.price,
                    market_data.volume,
                    market_data.timestamp.isoformat(),
                    market_data.bid,
                    market_data.ask,
                    market_data.high,
                    market_data.low,
                    market_data.open,
                    market_data.change_percent,
                    json.dumps(market_data.metadata) if market_data.metadata else None
                ))
                self.db_connection.commit()

        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    async def _notify_subscribers(self, market_data: MarketData):
        """通知订阅者"""
        try:
            symbol = market_data.symbol
            if symbol in self.subscribers:
                for callback in self.subscribers[symbol]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(market_data)
                        else:
                            callback(market_data)
                    except Exception as e:
                        logger.error(f"Error notifying subscriber: {e}")

        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")

    async def get_market_data(self, symbol: str, use_cache: bool = True) -> Optional[MarketData]:
        """获取市场数据"""
        try:
            # 首先检查缓存
            if use_cache and symbol in self.data_cache:
                cached_data = self.data_cache[symbol]
                # 检查缓存是否过期
                if (datetime.now() - cached_data.timestamp).total_seconds() < 60:
                    self.stats["cache_hits"] += 1
                    return cached_data

            # 检查Redis缓存
            if self.redis_client and use_cache:
                try:
                    cache_key = f"market_data:{symbol}"
                    cached_value = self.redis_client.get(cache_key)
                    if cached_value:
                        data_dict = json.loads(cached_value)
                        data_dict["timestamp"] = datetime.fromisoformat(data_dict["timestamp"])
                        self.stats["cache_hits"] += 1
                        return MarketData(**data_dict)
                except Exception as e:
                    logger.error(f"Error reading from Redis cache: {e}")

            # 缓存未命中，从API获取
            self.stats["cache_misses"] += 1
            data_list = await self._fetch_api_data([symbol])
            if data_list:
                return data_list[0]

            return None

        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None

    async def get_batch_market_data(self, symbols: List[str], use_cache: bool = True) -> Dict[str, MarketData]:
        """批量获取市场数据"""
        try:
            result = {}
            cache_misses = []

            # 检查缓存
            if use_cache:
                for symbol in symbols:
                    cached_data = await self.get_market_data(symbol, use_cache=True)
                    if cached_data:
                        result[symbol] = cached_data
                    else:
                        cache_misses.append(symbol)
            else:
                cache_misses = symbols

            # 获取缓存未命中的数据
            if cache_misses:
                fresh_data = await self._fetch_api_data(cache_misses)
                for data in fresh_data:
                    result[data.symbol] = data
                    # 更新缓存
                    await self._update_cache(data)

            return result

        except Exception as e:
            logger.error(f"Error getting batch market data: {e}")
            return {}

    def subscribe(self, symbol: str, callback: Callable[[MarketData], None]):
        """订阅市场数据更新"""
        try:
            if symbol not in self.subscribers:
                self.subscribers[symbol] = []
            self.subscribers[symbol].append(callback)
            logger.info(f"Subscribed to {symbol}")

        except Exception as e:
            logger.error(f"Error subscribing to {symbol}: {e}")

    def unsubscribe(self, symbol: str, callback: Callable[[MarketData], None]):
        """取消订阅"""
        try:
            if symbol in self.subscribers and callback in self.subscribers[symbol]:
                self.subscribers[symbol].remove(callback)
                if not self.subscribers[symbol]:
                    del self.subscribers[symbol]
                logger.info(f"Unsubscribed from {symbol}")

        except Exception as e:
            logger.error(f"Error unsubscribing from {symbol}: {e}")

    async def _get_symbols_to_update(self) -> List[str]:
        """获取需要更新的股票代码列表"""
        # 这里应该从配置或数据库中获取需要监控的股票列表
        # 暂时返回一些示例股票
        return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "000001", "000002", "600000", "600036"]

    def _batch_symbols(self, symbols: List[str], batch_size: int) -> List[List[str]]:
        """将股票代码分批"""
        for i in range(0, len(symbols), batch_size):
            yield symbols[i:i + batch_size]

    async def _start_data_quality_monitoring(self):
        """启动数据质量监控"""
        try:
            while self.running:
                await self._update_data_quality_metrics()
                await asyncio.sleep(60)  # 每分钟检查一次

        except Exception as e:
            logger.error(f"Error in data quality monitoring: {e}")

    async def _update_data_quality_metrics(self):
        """更新数据质量指标"""
        try:
            for symbol in self.data_cache:
                data = self.data_cache[symbol]

                # 计算时效性
                time_diff = (datetime.now() - data.timestamp).total_seconds()
                timeliness = max(0, 1 - time_diff / 300)  # 5分钟内为满分

                # 计算完整性（简化版）
                completeness = 1.0 if all([data.price, data.volume, data.symbol]) else 0.5

                # 计算准确性（基于历史数据的一致性）
                accuracy = 0.9  # 简化为固定值

                # 计算一致性
                consistency = 0.9  # 简化为固定值

                # 计算总体分数
                overall_score = (timeliness * 0.3 + completeness * 0.3 +
                               accuracy * 0.2 + consistency * 0.2)

                self.data_quality[symbol] = DataQuality(
                    completeness=completeness,
                    timeliness=timeliness,
                    accuracy=accuracy,
                    consistency=consistency,
                    overall_score=overall_score,
                    last_updated=datetime.now()
                )

        except Exception as e:
            logger.error(f"Error updating data quality metrics: {e}")

    async def _start_cache_cleanup(self):
        """启动缓存清理"""
        try:
            while self.running:
                await self._cleanup_expired_cache()
                await asyncio.sleep(300)  # 每5分钟清理一次

        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}")

    async def _cleanup_expired_cache(self):
        """清理过期缓存"""
        try:
            current_time = datetime.now()
            expired_symbols = []

            for symbol, data in self.data_cache.items():
                if (current_time - data.timestamp).total_seconds() > 600:  # 10分钟过期
                    expired_symbols.append(symbol)

            for symbol in expired_symbols:
                del self.data_cache[symbol]

            if expired_symbols:
                logger.info(f"Cleaned up {len(expired_symbols)} expired cache entries")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")

    async def _start_database_maintenance(self):
        """启动数据库维护"""
        try:
            while self.running:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # 每小时执行一次

        except Exception as e:
            logger.error(f"Error in database maintenance: {e}")

    async def _cleanup_old_data(self):
        """清理旧数据"""
        try:
            if self.db_connection:
                cutoff_date = datetime.now() - timedelta(days=self.db_config["retention_days"])
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "DELETE FROM market_data WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                deleted_rows = cursor.rowcount
                self.db_connection.commit()

                if deleted_rows > 0:
                    logger.info(f"Cleaned up {deleted_rows} old data records")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    async def _close_connections(self):
        """关闭连接"""
        try:
            if self.redis_client:
                self.redis_client.close()

            if self.db_connection:
                self.db_connection.close()

            for ws in self.websocket_connections.values():
                if not ws.closed:
                    await ws.close()

        except Exception as e:
            logger.error(f"Error closing connections: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "cache_size": len(self.data_cache),
            "subscribers_count": sum(len(subs) for subs in self.subscribers.values()),
            "data_quality_average": np.mean([dq.overall_score for dq in self.data_quality.values()]) if self.data_quality else 0
        }
