"""
股票数据解析器 - 解析沪深和北交所两种数据格式
沪深：33个字段，$分隔
北交所：JSON格式
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """标准化股票数据结构"""
    stock_code: str
    stock_name: str
    timestamp: float
    
    # 价格信息
    open_price: float
    high_price: float
    low_price: float
    current_price: float
    last_close: float
    
    # 交易信息
    volume: int  # 成交量
    amount: float  # 成交额
    turnover_rate: float  # 换手率
    
    # 五档行情
    ask_prices: List[float]  # 卖一到卖五价格
    bid_prices: List[float]  # 买一到买五价格
    ask_volumes: List[int]   # 卖一到卖五数量
    bid_volumes: List[int]   # 买一到买五数量
    
    # 涨跌停价格
    limit_up: Optional[float] = None    # 涨停价
    limit_down: Optional[float] = None  # 跌停价
    
    # 市场标识
    market: str = "SZ"  # SZ/SH/BJ
    
    # 原始数据（用于调试）
    raw_data: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'timestamp': self.timestamp,
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'current_price': self.current_price,
            'last_close': self.last_close,
            'volume': self.volume,
            'amount': self.amount,
            'turnover_rate': self.turnover_rate,
            'ask_prices': self.ask_prices,
            'bid_prices': self.bid_prices,
            'ask_volumes': self.ask_volumes,
            'bid_volumes': self.bid_volumes,
            'limit_up': self.limit_up,
            'limit_down': self.limit_down,
            'market': self.market,
            'change': self.current_price - self.last_close if self.last_close > 0 else 0,
            'change_percent': ((self.current_price - self.last_close) / self.last_close * 100) if self.last_close > 0 else 0
        }

class StockDataParser:
    """股票数据解析器"""
    
    def __init__(self):
        self.stats = {
            'parsed_count': 0,
            'error_count': 0,
            'sz_sh_count': 0,  # 沪深数据计数
            'bj_count': 0,     # 北交所数据计数
            'last_parse_time': 0
        }
    
    def parse_message(self, raw_data: bytes) -> List[StockData]:
        """解析原始消息数据"""
        try:
            # 尝试解码为UTF-8
            try:
                decoded_data = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                logger.debug("数据不是UTF-8格式，跳过解析")
                return []
            
            # 判断数据格式并解析
            parsed_stocks = []
            
            # 检查是否为JSON格式（北交所）
            if decoded_data.strip().startswith('{') and decoded_data.strip().endswith('}'):
                stock_data = self._parse_beijing_data(decoded_data)
                if stock_data:
                    parsed_stocks.append(stock_data)
                    self.stats['bj_count'] += 1
            
            # 检查是否为$分隔格式（沪深）
            elif '$' in decoded_data:
                stock_data = self._parse_sz_sh_data(decoded_data)
                if stock_data:
                    parsed_stocks.append(stock_data)
                    self.stats['sz_sh_count'] += 1
            
            # 可能是批量数据，按行分割
            else:
                lines = decoded_data.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # JSON格式
                    if line.startswith('{') and line.endswith('}'):
                        stock_data = self._parse_beijing_data(line)
                        if stock_data:
                            parsed_stocks.append(stock_data)
                            self.stats['bj_count'] += 1
                    
                    # $分隔格式
                    elif '$' in line:
                        stock_data = self._parse_sz_sh_data(line)
                        if stock_data:
                            parsed_stocks.append(stock_data)
                            self.stats['sz_sh_count'] += 1
            
            self.stats['parsed_count'] += len(parsed_stocks)
            self.stats['last_parse_time'] = time.time()
            
            return parsed_stocks
            
        except Exception as e:
            logger.error(f"解析消息失败: {str(e)}")
            self.stats['error_count'] += 1
            return []
    
    def _parse_sz_sh_data(self, data: str) -> Optional[StockData]:
        """解析沪深数据格式"""
        try:
            # 按$分割数据
            fields = data.strip().split('$')
            
            # 检查字段数量（应该有33个字段）
            if len(fields) < 33:
                logger.debug(f"沪深数据字段不足: {len(fields)} < 33")
                return None
            
            # 解析各个字段
            stock_code = fields[0].strip()
            stock_name = fields[1].strip()
            timestamp = float(fields[2]) if fields[2] else time.time()
            
            # 价格信息
            open_price = float(fields[3]) if fields[3] else 0.0
            high_price = float(fields[4]) if fields[4] else 0.0
            low_price = float(fields[5]) if fields[5] else 0.0
            current_price = float(fields[6]) if fields[6] else 0.0
            
            # 交易信息
            volume = int(fields[7]) if fields[7] else 0  # 成交量(手)
            amount = float(fields[8]) if fields[8] else 0.0  # 成交额
            
            # 五档卖价 (10-14)
            ask_prices = []
            for i in range(9, 14):  # 卖一到卖五价
                price = float(fields[i]) if fields[i] else 0.0
                ask_prices.append(price)
            
            # 五档卖量 (15-19)
            ask_volumes = []
            for i in range(14, 19):  # 卖一到卖五量
                vol = int(fields[i]) if fields[i] else 0
                ask_volumes.append(vol)
            
            # 五档买价 (20-24)
            bid_prices = []
            for i in range(19, 24):  # 买一到买五价
                price = float(fields[i]) if fields[i] else 0.0
                bid_prices.append(price)
            
            # 五档买量 (25-29)
            bid_volumes = []
            for i in range(24, 29):  # 买一到买五量
                vol = int(fields[i]) if fields[i] else 0
                bid_volumes.append(vol)
            
            # 其他信息
            turnover_rate = float(fields[29]) if fields[29] else 0.0  # 换手率
            last_close = float(fields[30]) if fields[30] else 0.0     # 昨收盘价
            limit_up = float(fields[31]) if fields[31] else None      # 涨停价
            limit_down = float(fields[32]) if fields[32] else None    # 跌停价
            
            # 判断市场
            market = "SZ"
            if stock_code.startswith("6"):
                market = "SH"
            elif stock_code.startswith("0") or stock_code.startswith("3"):
                market = "SZ"
            
            return StockData(
                stock_code=stock_code,
                stock_name=stock_name,
                timestamp=timestamp,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                current_price=current_price,
                last_close=last_close,
                volume=volume,
                amount=amount,
                turnover_rate=turnover_rate,
                ask_prices=ask_prices,
                bid_prices=bid_prices,
                ask_volumes=ask_volumes,
                bid_volumes=bid_volumes,
                limit_up=limit_up,
                limit_down=limit_down,
                market=market,
                raw_data=data
            )
            
        except Exception as e:
            logger.error(f"解析沪深数据失败: {str(e)}, 数据: {data[:100]}...")
            return None
    
    def _parse_beijing_data(self, data: str) -> Optional[StockData]:
        """解析北交所数据格式"""
        try:
            # 解析JSON数据
            json_data = json.loads(data)
            
            # 提取字段
            stock_code = json_data.get('stock_code', '')
            timestamp = json_data.get('time', time.time() * 1000) / 1000  # 转换为秒
            
            # 价格信息
            current_price = float(json_data.get('lastPrice', 0))
            open_price = float(json_data.get('open', 0))
            high_price = float(json_data.get('high', 0))
            low_price = float(json_data.get('low', 0))
            last_close = float(json_data.get('lastClose', 0))
            
            # 交易信息
            volume = int(json_data.get('volume', 0))
            amount = float(json_data.get('amount', 0))
            
            # 五档行情
            ask_prices = json_data.get('askPrice', [0, 0, 0, 0, 0])
            bid_prices = json_data.get('bidPrice', [0, 0, 0, 0, 0])
            ask_volumes = json_data.get('askVol', [0, 0, 0, 0, 0])
            bid_volumes = json_data.get('bidVol', [0, 0, 0, 0, 0])
            
            # 确保列表长度为5
            ask_prices = (ask_prices + [0] * 5)[:5]
            bid_prices = (bid_prices + [0] * 5)[:5]
            ask_volumes = (ask_volumes + [0] * 5)[:5]
            bid_volumes = (bid_volumes + [0] * 5)[:5]
            
            # 转换数据类型
            ask_prices = [float(p) for p in ask_prices]
            bid_prices = [float(p) for p in bid_prices]
            ask_volumes = [int(v) for v in ask_volumes]
            bid_volumes = [int(v) for v in bid_volumes]
            
            # 股票名称（北交所数据中可能没有，从股票代码推断）
            stock_name = self._get_stock_name_from_code(stock_code)
            
            return StockData(
                stock_code=stock_code,
                stock_name=stock_name,
                timestamp=timestamp,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                current_price=current_price,
                last_close=last_close,
                volume=volume,
                amount=amount,
                turnover_rate=0.0,  # 北交所数据中没有换手率
                ask_prices=ask_prices,
                bid_prices=bid_prices,
                ask_volumes=ask_volumes,
                bid_volumes=bid_volumes,
                limit_up=None,  # 北交所数据中没有涨跌停价
                limit_down=None,
                market="BJ",
                raw_data=data
            )
            
        except Exception as e:
            logger.error(f"解析北交所数据失败: {str(e)}, 数据: {data[:100]}...")
            return None
    
    def _get_stock_name_from_code(self, stock_code: str) -> str:
        """从股票代码推断股票名称"""
        # 这里可以维护一个股票代码到名称的映射
        # 或者从数据库查询，暂时返回代码本身
        return stock_code.replace('.BJ', '')
    
    def get_stats(self) -> Dict[str, Any]:
        """获取解析统计"""
        return self.stats.copy()

class BatchStockDataParser:
    """批量股票数据解析器"""
    
    def __init__(self, batch_size: int = 1000):
        self.parser = StockDataParser()
        self.batch_size = batch_size
        
    def parse_batch(self, raw_data_list: List[Dict[str, Any]]) -> List[StockData]:
        """批量解析数据"""
        all_stocks = []
        
        for data_item in raw_data_list:
            raw_data = data_item.get('data', b'')
            if isinstance(raw_data, bytes):
                stocks = self.parser.parse_message(raw_data)
                all_stocks.extend(stocks)
        
        return all_stocks
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.parser.get_stats()

# 全局解析器实例
stock_data_parser = StockDataParser()
batch_stock_data_parser = BatchStockDataParser()

def parse_stock_message(raw_data: bytes) -> List[StockData]:
    """解析单条股票消息"""
    return stock_data_parser.parse_message(raw_data)

def parse_stock_batch(raw_data_list: List[Dict[str, Any]]) -> List[StockData]:
    """批量解析股票消息"""
    return batch_stock_data_parser.parse_batch(raw_data_list)
