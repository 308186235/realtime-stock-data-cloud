#!/usr/bin/env python3
"""
混合股票数据管理器
整合茶股帮TCP + 腾讯API的完整解决方案
"""

import asyncio
import socket
import requests
import json
import time
import threading
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """数据源枚举"""
    CHAGUBANG_TCP = "chagubang_tcp"
    TENCENT_API = "tencent_api"
    CACHE = "cache"

@dataclass
class StockData:
    """股票数据结构"""
    code: str
    name: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    close_price: float = 0.0
    timestamp: str = ""
    source: DataSource = DataSource.CACHE
    raw_data: str = ""

class TradingTimeChecker:
    """交易时间检查器"""
    
    @staticmethod
    def is_trading_time() -> bool:
        """检查当前是否为交易时间"""
        now = datetime.now()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        current_time = now.time()
        
        # 检查是否为交易日 (周一到周五)
        if weekday >= 5:  # 周六、周日
            return False
        
        # 检查是否在交易时段
        morning_start = dt_time(9, 10)
        morning_end = dt_time(11, 30)
        afternoon_start = dt_time(13, 0)
        afternoon_end = dt_time(15, 0)
        
        is_morning = morning_start <= current_time <= morning_end
        is_afternoon = afternoon_start <= current_time <= afternoon_end
        
        return is_morning or is_afternoon
    
    @staticmethod
    def get_trading_status() -> Dict:
        """获取详细的交易状态"""
        now = datetime.now()
        is_trading = TradingTimeChecker.is_trading_time()
        
        return {
            'is_trading': is_trading,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'weekday': now.strftime('%A'),
            'next_trading_session': TradingTimeChecker._get_next_trading_session(now)
        }
    
    @staticmethod
    def _get_next_trading_session(now: datetime) -> str:
        """获取下一个交易时段"""
        current_time = now.time()
        weekday = now.weekday()
        
        if weekday < 5:  # 工作日
            if current_time < dt_time(9, 10):
                return "今日 09:10 (上午开盘)"
            elif dt_time(11, 30) < current_time < dt_time(13, 0):
                return "今日 13:00 (下午开盘)"
            elif current_time > dt_time(15, 0):
                return "明日 09:10 (上午开盘)"
            else:
                return "交易中"
        else:
            return "下周一 09:10 (上午开盘)"

class ChaguBangConnector:
    """茶股帮TCP连接器"""
    
    def __init__(self, token: str, host: str = "l1.chagubang.com", port: int = 6380):
        self.token = token
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.data_callbacks: List[Callable] = []
        self.running = False
        
    def add_data_callback(self, callback: Callable):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)
    
    async def connect(self) -> bool:
        """连接到茶股帮服务器"""
        try:
            logger.info(f"连接茶股帮服务器: {self.host}:{self.port}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # 发送Token认证
            logger.info("发送Token认证...")
            self.socket.send(self.token.encode('utf-8'))
            
            # 等待认证响应
            response = self.socket.recv(1024)
            if response:
                logger.info(f"认证响应: {response.decode('utf-8', errors='ignore')}")
                self.connected = True
                return True
            
        except Exception as e:
            logger.error(f"茶股帮连接失败: {e}")
            self.connected = False
            
        return False
    
    async def start_listening(self):
        """开始监听数据"""
        if not self.connected:
            return
        
        self.running = True
        logger.info("开始监听茶股帮数据...")
        
        try:
            self.socket.settimeout(1)
            while self.running:
                try:
                    data = self.socket.recv(4096)
                    if data:
                        data_text = data.decode('utf-8', errors='ignore')
                        await self._process_chagubang_data(data_text)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"数据接收错误: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"监听过程出错: {e}")
        finally:
            self.disconnect()
    
    async def _process_chagubang_data(self, data: str):
        """处理茶股帮数据"""
        try:
            # 茶股帮数据格式通常是用$分隔的字段
            if '$' in data:
                fields = data.strip().split('$')
                if len(fields) >= 10:
                    stock_data = StockData(
                        code=fields[0] if len(fields) > 0 else "",
                        name=fields[1] if len(fields) > 1 else "",
                        current_price=float(fields[2]) if len(fields) > 2 and fields[2] else 0.0,
                        change=float(fields[3]) if len(fields) > 3 and fields[3] else 0.0,
                        change_percent=float(fields[4]) if len(fields) > 4 and fields[4] else 0.0,
                        volume=int(fields[5]) if len(fields) > 5 and fields[5] else 0,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        source=DataSource.CHAGUBANG_TCP,
                        raw_data=data[:200]
                    )
                    
                    # 调用所有回调函数
                    for callback in self.data_callbacks:
                        await callback(stock_data)
                        
        except Exception as e:
            logger.error(f"茶股帮数据处理失败: {e}")
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        logger.info("茶股帮连接已断开")

class TencentAPIConnector:
    """腾讯API连接器"""
    
    def __init__(self):
        self.base_url = "https://qt.gtimg.cn/q="
        self.cache = {}
        self.cache_timeout = 30  # 缓存30秒
    
    async def get_stock_data(self, stock_codes: List[str]) -> Dict[str, StockData]:
        """获取股票数据"""
        try:
            # 检查缓存
            cached_data = self._get_cached_data(stock_codes)
            if cached_data:
                return cached_data
            
            # 批量请求
            codes_str = ",".join(stock_codes)
            url = f"{self.base_url}{codes_str}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.text.strip()
                parsed_data = self._parse_tencent_data(data, stock_codes)
                
                # 更新缓存
                self._update_cache(parsed_data)
                
                return parsed_data
            
        except Exception as e:
            logger.error(f"腾讯API请求失败: {e}")
        
        return {}
    
    def _parse_tencent_data(self, data: str, stock_codes: List[str]) -> Dict[str, StockData]:
        """解析腾讯数据"""
        results = {}
        
        try:
            lines = data.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for code in stock_codes:
                    if f"v_{code}" in line:
                        parsed = self._parse_single_stock(line, code)
                        if parsed:
                            results[code] = parsed
                        break
        except Exception as e:
            logger.error(f"腾讯数据解析失败: {e}")
        
        return results
    
    def _parse_single_stock(self, data: str, stock_code: str) -> Optional[StockData]:
        """解析单个股票数据"""
        try:
            if '="' in data and '~' in data:
                start = data.find('="') + 2
                end = data.find('";', start)
                if end == -1:
                    end = len(data)
                
                stock_data = data[start:end]
                fields = stock_data.split('~')
                
                if len(fields) >= 10:
                    return StockData(
                        code=stock_code,
                        name=fields[1] if len(fields) > 1 else 'N/A',
                        current_price=float(fields[3]) if len(fields) > 3 and fields[3] else 0,
                        change=float(fields[31]) if len(fields) > 31 and fields[31] else 0,
                        change_percent=float(fields[32]) if len(fields) > 32 and fields[32] else 0,
                        volume=int(fields[6]) if len(fields) > 6 and fields[6] else 0,
                        high=float(fields[41]) if len(fields) > 41 and fields[41] else 0,
                        low=float(fields[42]) if len(fields) > 42 and fields[42] else 0,
                        open_price=float(fields[5]) if len(fields) > 5 and fields[5] else 0,
                        close_price=float(fields[4]) if len(fields) > 4 and fields[4] else 0,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        source=DataSource.TENCENT_API,
                        raw_data=data[:200]
                    )
        except Exception as e:
            logger.error(f"解析股票 {stock_code} 失败: {e}")
        
        return None
    
    def _get_cached_data(self, stock_codes: List[str]) -> Optional[Dict[str, StockData]]:
        """获取缓存数据"""
        now = time.time()
        cached_data = {}
        
        for code in stock_codes:
            if code in self.cache:
                cache_time, data = self.cache[code]
                if now - cache_time < self.cache_timeout:
                    cached_data[code] = data
        
        return cached_data if len(cached_data) == len(stock_codes) else None
    
    def _update_cache(self, data: Dict[str, StockData]):
        """更新缓存"""
        now = time.time()
        for code, stock_data in data.items():
            self.cache[code] = (now, stock_data)

class HybridStockDataManager:
    """混合股票数据管理器"""
    
    def __init__(self):
        self.token = os.getenv("CHAGUBANG_TOKEN", "QT_wat5QfcJ6N9pDZM5")
        self.chagubang = ChaguBangConnector(self.token)
        self.tencent = TencentAPIConnector()
        self.data_callbacks: List[Callable] = []
        self.current_data: Dict[str, StockData] = {}
        self.running = False
        
        # 添加数据回调
        self.chagubang.add_data_callback(self._on_data_received)
    
    def add_data_callback(self, callback: Callable):
        """添加数据回调"""
        self.data_callbacks.append(callback)
    
    async def _on_data_received(self, stock_data: StockData):
        """数据接收回调"""
        self.current_data[stock_data.code] = stock_data
        
        # 通知所有回调
        for callback in self.data_callbacks:
            await callback(stock_data)
    
    async def start(self):
        """启动混合数据管理器"""
        self.running = True
        logger.info("启动混合股票数据管理器...")
        
        # 检查交易时间
        trading_status = TradingTimeChecker.get_trading_status()
        logger.info(f"交易状态: {trading_status}")
        
        if trading_status['is_trading']:
            # 交易时间：尝试连接茶股帮
            logger.info("交易时间内，尝试连接茶股帮...")
            if await self.chagubang.connect():
                logger.info("茶股帮连接成功，开始实时数据监听")
                await self.chagubang.start_listening()
            else:
                logger.warning("茶股帮连接失败，使用腾讯API作为备用")
        else:
            logger.info("非交易时间，使用腾讯API获取数据")
    
    async def get_stock_data(self, stock_codes: List[str]) -> Dict[str, StockData]:
        """获取股票数据"""
        trading_status = TradingTimeChecker.get_trading_status()
        
        if trading_status['is_trading'] and self.chagubang.connected:
            # 交易时间且茶股帮已连接：返回实时数据
            logger.info("使用茶股帮实时数据")
            return {code: data for code, data in self.current_data.items() if code in stock_codes}
        else:
            # 非交易时间或茶股帮未连接：使用腾讯API
            logger.info("使用腾讯API获取数据")
            return await self.tencent.get_stock_data(stock_codes)
    
    async def get_single_stock(self, stock_code: str) -> Optional[StockData]:
        """获取单个股票数据"""
        data = await self.get_stock_data([stock_code])
        return data.get(stock_code)
    
    def stop(self):
        """停止管理器"""
        self.running = False
        self.chagubang.disconnect()
        logger.info("混合股票数据管理器已停止")

# 使用示例
async def demo_usage():
    """使用演示"""
    manager = HybridStockDataManager()
    
    # 添加数据回调
    async def on_stock_data(stock_data: StockData):
        print(f"📊 {stock_data.name} ({stock_data.code}): ¥{stock_data.current_price:.2f} "
              f"({stock_data.change_percent:+.2f}%) [{stock_data.source.value}]")
    
    manager.add_data_callback(on_stock_data)
    
    # 测试股票代码
    test_stocks = ["sh000001", "sh600519", "sz000001", "sh601318"]
    
    print("🚀 启动混合股票数据管理器...")
    
    # 获取股票数据
    stock_data = await manager.get_stock_data(test_stocks)
    
    print(f"\n📊 获取到 {len(stock_data)} 只股票数据:")
    for code, data in stock_data.items():
        print(f"  {data.name} ({code}): ¥{data.current_price:.2f} "
              f"({data.change_percent:+.2f}%) [{data.source.value}]")
    
    # 如果在交易时间，启动实时监听
    if TradingTimeChecker.is_trading_time():
        print("\n🔄 交易时间内，启动实时数据监听...")
        await manager.start()
    
    manager.stop()

if __name__ == "__main__":
    asyncio.run(demo_usage())
