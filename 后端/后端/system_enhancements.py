"""
交易系统增强包 - 错误处理,性能监控,安全机制
"""

import asyncio
import time
import psutil
import logging
import json
from datetime import datetime
from functools import wraps
import threading
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingSystemException(Exception):
    """交易系统专用异常"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now()

class NetworkRetryHandler:
    """网络重试处理器"""
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def retry_with_backoff(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                logger.info(f"尝试执行 {func.__name__} (第{attempt + 1}次)")
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"{func.__name__} 重试成功")
                return result
            except Exception as e:
                logger.warning(f"{func.__name__} 第{attempt + 1}次尝试失败: {e}")
                if attempt == self.max_retries - 1:
                    raise TradingSystemException(f"重试失败: {func.__name__}", "RETRY_FAILED")
                await asyncio.sleep(self.backoff_factor ** attempt)

class DataValidator:
    """数据校验器"""
    
    @staticmethod
    def validate_stock_data(data):
        """验证股票数据完整性"""
        required_fields = ['stock_code', 'last_price', 'timestamp']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"缺少必需字段: {field}")
        
        if float(data['last_price']) <= 0:
            raise ValueError("无效的价格数据")
        
        logger.debug(f"股票数据验证通过: {data['stock_code']}")
        return True
    
    @staticmethod
    def validate_trade_params(code, quantity, price):
        """验证交易参数"""
        if not code or len(code.strip()) < 6:
            raise ValueError(f"无效的股票代码: {code}")
        
        if quantity <= 0 or quantity % 100 != 0:
            raise ValueError(f"无效的交易数量: {quantity}")
        
        if price <= 0:
            raise ValueError(f"无效的交易价格: {price}")
        
        return True

def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 1.0:
                logger.warning(f" {func.__name__} 执行时间过长: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f" {func.__name__} 执行失败 ({execution_time:.2f}秒): {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 1.0:
                logger.warning(f" {func.__name__} 执行时间过长: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f" {func.__name__} 执行失败 ({execution_time:.2f}秒): {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

class ResourceManager:
    """资源管理器"""
    def __init__(self):
        self.max_memory_usage = 500 * 1024 * 1024  # 500MB
        self.data_cache_limit = 1000
        
    def check_memory_usage(self):
        """检查内存使用情况"""
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss
            
            if memory_usage > self.max_memory_usage:
                logger.warning(f"内存使用过高: {memory_usage / 1024 / 1024:.2f}MB")
                return False
            return True
        except Exception as e:
            logger.error(f"内存检查失败: {e}")
            return True
    
    def check_disk_space(self):
        """检查磁盘空间"""
        try:
            disk_usage = psutil.disk_usage('.')
            free_space_gb = disk_usage.free / (1024**3)
            
            if free_space_gb < 1.0:  # 少于1GB
                logger.warning(f"磁盘空间不足: {free_space_gb:.2f}GB")
                return False
            return True
        except Exception as e:
            logger.error(f"磁盘空间检查失败: {e}")
            return True

class SystemHealthChecker:
    """系统健康检查器"""
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.last_check_time = None
        self.health_status = {}
    
    def check_trading_software_connection(self):
        """检查交易软件连接"""
        try:
            import win32gui
            def enum_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "网上股票交易系统" in title:
                        windows.append(title)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_callback, windows)
            return len(windows) > 0
        except Exception as e:
            logger.error(f"交易软件连接检查失败: {e}")
            return False
    
    def check_system_health(self):
        """全面系统健康检查"""
        checks = {
            "memory": self.resource_manager.check_memory_usage(),
            "disk_space": self.resource_manager.check_disk_space(),
            "trading_software": self.check_trading_software_connection(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.health_status = checks
        self.last_check_time = datetime.now()
        
        all_healthy = all([checks["memory"], checks["disk_space"], checks["trading_software"]])
        
        if not all_healthy:
            logger.warning(f"系统健康检查发现问题: {checks}")
        else:
            logger.info("系统健康检查通过")
        
        return checks

class SecurityManager:
    """安全管理器"""
    def __init__(self):
        self.trade_limits = {
            "max_daily_trades": 50,
            "max_single_trade_amount": 100000,
            "max_total_position": 500000
        }
        self.daily_trade_count = 0
        self.daily_trade_amount = 0
        self.last_reset_date = datetime.now().date()
    
    def check_trade_limits(self, amount):
        """检查交易限额"""
        # 重置日计数器
        if datetime.now().date() != self.last_reset_date:
            self.daily_trade_count = 0
            self.daily_trade_amount = 0
            self.last_reset_date = datetime.now().date()
        
        # 检查单笔交易限额
        if amount > self.trade_limits["max_single_trade_amount"]:
            raise TradingSystemException(
                f"单笔交易金额超限: {amount} > {self.trade_limits['max_single_trade_amount']}",
                "TRADE_AMOUNT_EXCEEDED"
            )
        
        # 检查日交易次数
        if self.daily_trade_count >= self.trade_limits["max_daily_trades"]:
            raise TradingSystemException(
                f"日交易次数超限: {self.daily_trade_count}",
                "DAILY_TRADES_EXCEEDED"
            )
        
        # 检查日交易总额
        if self.daily_trade_amount + amount > self.trade_limits["max_total_position"]:
            raise TradingSystemException(
                f"日交易总额超限: {self.daily_trade_amount + amount}",
                "DAILY_AMOUNT_EXCEEDED"
            )
        
        return True
    
    def record_trade(self, amount):
        """记录交易"""
        self.daily_trade_count += 1
        self.daily_trade_amount += amount
        logger.info(f"记录交易: 第{self.daily_trade_count}笔, 金额{amount:,.2f}")

# 全局实例
retry_handler = NetworkRetryHandler()
data_validator = DataValidator()
resource_manager = ResourceManager()
health_checker = SystemHealthChecker()
security_manager = SecurityManager()

# 导出主要组件
__all__ = [
    'TradingSystemException',
    'NetworkRetryHandler', 
    'DataValidator',
    'performance_monitor',
    'ResourceManager',
    'SystemHealthChecker',
    'SecurityManager',
    'retry_handler',
    'data_validator', 
    'resource_manager',
    'health_checker',
    'security_manager'
]

if __name__ == "__main__":
    print(" 测试系统增强包")
    
    # 测试健康检查
    health_status = health_checker.check_system_health()
    print(f"系统健康状态: {health_status}")
    
    # 测试数据验证
    test_data = {
        "stock_code": "000001",
        "last_price": 10.50,
        "timestamp": time.time()
    }
    
    try:
        data_validator.validate_stock_data(test_data)
        print(" 数据验证通过")
    except Exception as e:
        print(f" 数据验证失败: {e}")
    
    print(" 系统增强包测试完成")
