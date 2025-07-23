import logging
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# QMT SDK import
try:
    # 尝试导入QMT SDK
    sys.path.append(os.environ.get('QMT_PATH', 'C:/Program Files/QMT'))
    import qmt_core as qc
except ImportError:
    logging.error("无法导入QMT SDK,请确保QMT已正确安装并设置QMT_PATH环境变量")

logger = logging.getLogger(__name__)

class QMTDongwuBroker:
    """
    东吴证券秀才QMT接口
    """
    def __init__(self, account_id: str, account_pwd: str, broker_id: str = "DONGWU_QMT"):
        """
        初始化东吴证券秀才QMT接口
        
        Args:
            account_id: 证券账号
            account_pwd: 账号密码
            broker_id: 券商ID标识
        """
        self.account_id = account_id
        self.account_pwd = account_pwd
        self.broker_id = broker_id
        self.connected = False
        self.session_id = None
        self.qmt_instance = None
        
        # 交易权限标志
        self.can_trade = False
        
        # 初始化连接
        self._init_connection()
    
    def _init_connection(self) -> bool:
        """初始化连接到东吴秀才QMT"""
        try:
            # 创建QMT实例
            self.qmt_instance = qc.QMT()
            
            # 登录东吴秀才账户
            login_result = self.qmt_instance.login(
                account=self.account_id,
                password=self.account_pwd,
                broker_type="DONGWU"  # 东吴证券标识
            )
            
            if login_result["success"]:
                self.connected = True
                self.session_id = login_result.get("session_id")
                self.can_trade = True
                logger.info(f"已成功连接东吴秀才QMT接口,账户:{self.account_id}")
                return True
            else:
                logger.error(f"连接东吴秀才QMT接口失败: {login_result.get('message', '未知错误')}")
                return False
        except Exception as e:
            logger.error(f"初始化东吴秀才QMT接口异常: {str(e)}")
            return False
    
    def reconnect(self) -> bool:
        """重新连接到东吴秀才QMT"""
        self.disconnect()
        time.sleep(1)
        return self._init_connection()
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.qmt_instance and self.connected:
            try:
                self.qmt_instance.logout()
                logger.info(f"已断开东吴秀才QMT接口连接,账户:{self.account_id}")
            except Exception as e:
                logger.error(f"断开东吴秀才QMT接口连接异常: {str(e)}")
        
        self.connected = False
        self.session_id = None
        self.can_trade = False
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            account_info = self.qmt_instance.get_account_info()
            return {
                "success": True,
                "data": {
                    "account_id": self.account_id,
                    "broker_id": self.broker_id,
                    "balance": account_info.get("balance", 0),
                    "available": account_info.get("available", 0),
                    "market_value": account_info.get("market_value", 0),
                    "total_assets": account_info.get("total_assets", 0),
                    "frozen": account_info.get("frozen", 0),
                }
            }
        except Exception as e:
            logger.error(f"获取账户信息异常: {str(e)}")
            return {"success": False, "message": f"获取账户信息异常: {str(e)}"}
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            positions = self.qmt_instance.get_positions()
            position_list = []
            
            for pos in positions:
                position_list.append({
                    "symbol": pos.get("symbol", ""),
                    "name": pos.get("name", ""),
                    "volume": pos.get("volume", 0),
                    "available_volume": pos.get("available", 0),
                    "cost_price": pos.get("cost_price", 0),
                    "current_price": pos.get("current_price", 0),
                    "market_value": pos.get("market_value", 0),
                    "profit_loss": pos.get("profit_loss", 0),
                    "profit_loss_ratio": pos.get("profit_loss_ratio", 0),
                })
            
            return {
                "success": True,
                "data": position_list
            }
        except Exception as e:
            logger.error(f"获取持仓信息异常: {str(e)}")
            return {"success": False, "message": f"获取持仓信息异常: {str(e)}"}
    
    def place_order(self, symbol: str, price: float, volume: int, direction: str) -> Dict:
        """
        下单
        
        Args:
            symbol: 证券代码
            price: 委托价格
            volume: 委托数量
            direction: 方向,'BUY'或'SELL'
        
        Returns:
            dict: 下单结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        if not self.can_trade:
            return {"success": False, "message": "当前账户无交易权限"}
        
        try:
            # 转换交易方向
            qmt_direction = "buy" if direction.upper() == "BUY" else "sell"
            
            # 构建下单参数
            order_params = {
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "direction": qmt_direction,
                "order_type": "limit"  # 限价单
            }
            
            # 执行下单
            order_result = self.qmt_instance.place_order(**order_params)
            
            if order_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "order_id": order_result.get("order_id", ""),
                        "symbol": symbol,
                        "price": price,
                        "volume": volume,
                        "direction": direction,
                        "status": "SUBMITTED",
                        "message": "委托已提交"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": order_result.get("message", "下单失败,未知错误")
                }
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
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            # 执行撤单
            cancel_result = self.qmt_instance.cancel_order(order_id=order_id)
            
            if cancel_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "order_id": order_id,
                        "message": "撤单请求已提交"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": cancel_result.get("message", "撤单失败,未知错误")
                }
        except Exception as e:
            logger.error(f"撤单异常: {str(e)}")
            return {"success": False, "message": f"撤单异常: {str(e)}"}
    
    def get_orders(self, status: str = None) -> Dict:
        """
        获取委托列表
        
        Args:
            status: 委托状态,None表示全部
        
        Returns:
            dict: 委托列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            # 获取委托列表
            orders = self.qmt_instance.get_orders(status=status)
            
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": order.get("order_id", ""),
                    "symbol": order.get("symbol", ""),
                    "name": order.get("name", ""),
                    "price": order.get("price", 0),
                    "volume": order.get("volume", 0),
                    "traded_volume": order.get("traded_volume", 0),
                    "direction": "BUY" if order.get("direction") == "buy" else "SELL",
                    "status": order.get("status", ""),
                    "submit_time": order.get("submit_time", ""),
                    "message": order.get("message", "")
                })
            
            return {
                "success": True,
                "data": order_list
            }
        except Exception as e:
            logger.error(f"获取委托列表异常: {str(e)}")
            return {"success": False, "message": f"获取委托列表异常: {str(e)}"}
    
    def get_trades(self) -> Dict:
        """
        获取成交列表
        
        Returns:
            dict: 成交列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            # 获取成交列表
            trades = self.qmt_instance.get_trades()
            
            trade_list = []
            for trade in trades:
                trade_list.append({
                    "trade_id": trade.get("trade_id", ""),
                    "order_id": trade.get("order_id", ""),
                    "symbol": trade.get("symbol", ""),
                    "name": trade.get("name", ""),
                    "price": trade.get("price", 0),
                    "volume": trade.get("volume", 0),
                    "direction": "BUY" if trade.get("direction") == "buy" else "SELL",
                    "trade_time": trade.get("trade_time", ""),
                    "commission": trade.get("commission", 0)
                })
            
            return {
                "success": True,
                "data": trade_list
            }
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
            return {"success": False, "message": "未连接到东吴秀才QMT"}
        
        try:
            # 获取实时行情
            quotes = self.qmt_instance.get_realtime_quotes(symbols=symbols)
            
            quote_list = []
            for symbol, quote in quotes.items():
                quote_list.append({
                    "symbol": symbol,
                    "name": quote.get("name", ""),
                    "last_price": quote.get("last_price", 0),
                    "open": quote.get("open", 0),
                    "high": quote.get("high", 0),
                    "low": quote.get("low", 0),
                    "close": quote.get("pre_close", 0),
                    "volume": quote.get("volume", 0),
                    "amount": quote.get("amount", 0),
                    "bid1": quote.get("bid1", 0),
                    "bid1_volume": quote.get("bid1_volume", 0),
                    "ask1": quote.get("ask1", 0),
                    "ask1_volume": quote.get("ask1_volume", 0),
                    "update_time": quote.get("update_time", "")
                })
            
            return {
                "success": True,
                "data": quote_list
            }
        except Exception as e:
            logger.error(f"获取实时行情异常: {str(e)}")
            return {"success": False, "message": f"获取实时行情异常: {str(e)}"}
    
    def _check_connection(self) -> bool:
        """检查连接状态,如果未连接则尝试重连"""
        if not self.connected:
            logger.warning("未连接到东吴秀才QMT,尝试重新连接...")
            return self.reconnect()
        return True 
