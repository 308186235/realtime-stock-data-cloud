import logging
import threading
from typing import Dict, List, Optional, Union, Any

from ..config import settings
from .brokers import BrokerFactory

logger = logging.getLogger(__name__)

class TradingService:
    """
    交易服务,提供统一的交易接口,内部根据配置使用不同的券商接口
    """
    
    def __init__(self):
        """初始化交易服务"""
        self.broker = None
        self.broker_type = settings.DONGWU_DEFAULT_BROKER
        self.lock = threading.Lock()
        self.connected = False
        
        # 自动初始化
        self._init_broker()
    
    def _init_broker(self) -> bool:
        """初始化券商接口"""
        with self.lock:
            try:
                # 根据默认券商类型创建券商接口
                if self.broker_type.upper() == "THS_DONGWU":
                    self.broker = BrokerFactory.create_broker(
                        broker_type=self.broker_type,
                        account_id=settings.DONGWU_ACCOUNT_ID,
                        account_pwd=settings.DONGWU_ACCOUNT_PWD,
                        verification_code=settings.DONGWU_VERIFICATION_CODE if hasattr(settings, 'DONGWU_VERIFICATION_CODE') else None,
                        ths_path=settings.THS_PATH if hasattr(settings, 'THS_PATH') else None
                    )
                else:
                    logger.error(f"不支持的券商类型: {self.broker_type}")
                    return False
                
                self.connected = True
                logger.info(f"已初始化交易服务,使用券商接口: {self.broker_type}")
                return True
            except Exception as e:
                logger.error(f"初始化交易服务失败: {str(e)}")
                self.broker = None
                self.connected = False
                return False
    
    def connect(self, broker_type: str = None, **kwargs) -> Dict:
        """
        连接到交易服务
        
        Args:
            broker_type: 券商类型,如果不指定则使用默认券商类型
            **kwargs: 连接参数
        
        Returns:
            dict: 连接结果
        """
        with self.lock:
            try:
                # 如果指定了券商类型且与当前不同,先断开当前连接
                if broker_type and broker_type.upper() != self.broker_type.upper():
                    self.disconnect()
                    self.broker_type = broker_type.upper()
                
                # 如果已经连接,则返回已连接信息
                if self.connected and self.broker:
                    return {
                        "success": True,
                        "message": f"已连接到交易服务,券商类型: {self.broker_type}",
                        "broker_type": self.broker_type
                    }
                
                # 重新初始化券商接口
                if self._init_broker():
                    return {
                        "success": True,
                        "message": f"成功连接到交易服务,券商类型: {self.broker_type}",
                        "broker_type": self.broker_type
                    }
                else:
                    return {
                        "success": False,
                        "message": "连接交易服务失败,请检查配置",
                        "broker_type": self.broker_type
                    }
            except Exception as e:
                logger.error(f"连接交易服务异常: {str(e)}")
                return {
                    "success": False,
                    "message": f"连接交易服务异常: {str(e)}",
                    "broker_type": self.broker_type
                }
    
    def disconnect(self) -> Dict:
        """
        断开交易服务连接
        
        Returns:
            dict: 断开连接结果
        """
        with self.lock:
            try:
                if self.broker:
                    self.broker.disconnect()
                    logger.info(f"已断开交易服务连接,券商类型: {self.broker_type}")
                
                self.broker = None
                self.connected = False
                
                return {
                    "success": True,
                    "message": "已断开交易服务连接"
                }
            except Exception as e:
                logger.error(f"断开交易服务连接异常: {str(e)}")
                return {
                    "success": False,
                    "message": f"断开交易服务连接异常: {str(e)}"
                }
    
    def get_account_info(self) -> Dict:
        """
        获取账户信息
        
        Returns:
            dict: 账户信息
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.get_account_info()
        except Exception as e:
            logger.error(f"获取账户信息异常: {str(e)}")
            return {"success": False, "message": f"获取账户信息异常: {str(e)}"}
    
    def get_positions(self) -> Dict:
        """
        获取持仓信息
        
        Returns:
            dict: 持仓信息
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.get_positions()
        except Exception as e:
            logger.error(f"获取持仓信息异常: {str(e)}")
            return {"success": False, "message": f"获取持仓信息异常: {str(e)}"}
    
    def place_order(self, symbol: str, price: float, volume: int, direction: str, **kwargs) -> Dict:
        """
        下单
        
        Args:
            symbol: 证券代码
            price: 委托价格
            volume: 委托数量
            direction: 方向,'BUY'或'SELL'
            **kwargs: 其他参数,如订单类型等
        
        Returns:
            dict: 下单结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.place_order(
                symbol=symbol,
                price=price,
                volume=volume,
                direction=direction,
                **kwargs
            )
        except Exception as e:
            logger.error(f"下单异常: {str(e)}")
            return {"success": False, "message": f"下单异常: {str(e)}"}
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        撤单
        
        Args:
            order_id: 委托编号
        
        Returns:
            dict: 撤单结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.cancel_order(order_id=order_id)
        except Exception as e:
            logger.error(f"撤单异常: {str(e)}")
            return {"success": False, "message": f"撤单异常: {str(e)}"}
    
    def get_orders(self, **kwargs) -> Dict:
        """
        获取委托列表
        
        Args:
            **kwargs: 查询参数,如状态,日期范围等
        
        Returns:
            dict: 委托列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.get_orders(**kwargs)
        except Exception as e:
            logger.error(f"获取委托列表异常: {str(e)}")
            return {"success": False, "message": f"获取委托列表异常: {str(e)}"}
    
    def get_trades(self, **kwargs) -> Dict:
        """
        获取成交列表
        
        Args:
            **kwargs: 查询参数,如日期范围等
        
        Returns:
            dict: 成交列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.get_trades(**kwargs)
        except Exception as e:
            logger.error(f"获取成交列表异常: {str(e)}")
            return {"success": False, "message": f"获取成交列表异常: {str(e)}"}
    
    def get_realtime_quotes(self, symbols: List[str]) -> Dict:
        """
        获取实时行情
        
        Args:
            symbols: 证券代码列表
        
        Returns:
            dict: 实时行情
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到交易服务"}
        
        try:
            return self.broker.get_realtime_quotes(symbols=symbols)
        except Exception as e:
            logger.error(f"获取实时行情异常: {str(e)}")
            return {"success": False, "message": f"获取实时行情异常: {str(e)}"}
    
    def get_supported_brokers(self) -> List[Dict]:
        """
        获取所有支持的券商类型
        
        Returns:
            List[Dict]: 券商类型列表
        """
        try:
            return BrokerFactory.get_supported_brokers()
        except Exception as e:
            logger.error(f"获取支持的券商类型异常: {str(e)}")
            return []
    
    def _check_connection(self) -> bool:
        """检查连接状态,如果未连接则尝试重连"""
        if not self.connected or not self.broker:
            logger.warning("未连接到交易服务,尝试重新连接...")
            result = self.connect()
            return result.get("success", False)
        return True


# 创建全局交易服务实例
trading_service = TradingService() 
