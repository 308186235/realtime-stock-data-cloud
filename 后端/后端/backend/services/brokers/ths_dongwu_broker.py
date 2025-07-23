import logging
import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

class THSDongwuBroker:
    """
    东吴证券同花顺接口
    """
    def __init__(self, account_id: str, account_pwd: str, broker_id: str = "DONGWU_THS", 
                 verification_code: str = None, ths_path: str = None):
        """
        初始化东吴证券同花顺接口
        
        Args:
            account_id: 证券账号
            account_pwd: 账号密码
            broker_id: 券商ID标识
            verification_code: 验证码(如果需要)
            ths_path: 同花顺安装路径(可选)
        """
        self.account_id = account_id
        self.account_pwd = account_pwd
        self.broker_id = broker_id
        self.verification_code = verification_code
        self.ths_path = ths_path or os.environ.get('THS_PATH', 'C:/同花顺')
        self.connected = False
        self.session_id = None
        
        # 同花顺API基础URL,实际应用中可能需要从配置中获取
        self.base_url = "http://localhost:8000/ths"
        
        # 交易权限标志
        self.can_trade = False
        
        # 会话对象
        self.session = requests.Session()
        
        # 初始化连接
        self._init_connection()
    
    def _init_connection(self) -> bool:
        """初始化连接到东吴证券同花顺"""
        try:
            # 构建登录参数
            login_params = {
                "account": self.account_id,
                "password": self.account_pwd,
                "broker_type": "东吴证券",
                "verification_code": self.verification_code
            }
            
            # 发送登录请求
            response = self.session.post(f"{self.base_url}/login", json=login_params)
            login_result = response.json()
            
            if login_result.get("success"):
                self.connected = True
                self.session_id = login_result.get("session_id")
                self.can_trade = True
                logger.info(f"已成功连接东吴证券同花顺接口,账户:{self.account_id}")
                return True
            else:
                logger.error(f"连接东吴证券同花顺接口失败: {login_result.get('message', '未知错误')}")
                return False
        except Exception as e:
            logger.error(f"初始化东吴证券同花顺接口异常: {str(e)}")
            return False
    
    def reconnect(self) -> bool:
        """重新连接到东吴证券同花顺"""
        self.disconnect()
        time.sleep(1)
        return self._init_connection()
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.connected:
            try:
                self.session.post(f"{self.base_url}/logout", json={"session_id": self.session_id})
                logger.info(f"已断开东吴证券同花顺接口连接,账户:{self.account_id}")
            except Exception as e:
                logger.error(f"断开东吴证券同花顺接口连接异常: {str(e)}")
        
        self.connected = False
        self.session_id = None
        self.can_trade = False
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        try:
            response = self.session.get(f"{self.base_url}/account_info", 
                                       params={"session_id": self.session_id})
            account_info = response.json()
            
            if account_info.get("success"):
                return {
                    "success": True,
                    "data": {
                        "account_id": self.account_id,
                        "broker_id": self.broker_id,
                        "balance": account_info.get("data", {}).get("balance", 0),
                        "available": account_info.get("data", {}).get("available", 0),
                        "market_value": account_info.get("data", {}).get("market_value", 0),
                        "total_assets": account_info.get("data", {}).get("total_assets", 0),
                        "frozen": account_info.get("data", {}).get("frozen", 0),
                    }
                }
            else:
                return {"success": False, "message": account_info.get("message", "获取账户信息失败")}
        except Exception as e:
            logger.error(f"获取账户信息异常: {str(e)}")
            return {"success": False, "message": f"获取账户信息异常: {str(e)}"}
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        try:
            response = self.session.get(f"{self.base_url}/positions", 
                                       params={"session_id": self.session_id})
            positions_info = response.json()
            
            if positions_info.get("success"):
                position_list = []
                
                for pos in positions_info.get("data", []):
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
            else:
                return {"success": False, "message": positions_info.get("message", "获取持仓信息失败")}
        except Exception as e:
            logger.error(f"获取持仓信息异常: {str(e)}")
            return {"success": False, "message": f"获取持仓信息异常: {str(e)}"}
    
    def place_order(self, symbol: str, price: float, volume: int, direction: str, 
                   order_type: str = "LIMIT") -> Dict:
        """
        下单
        
        Args:
            symbol: 证券代码
            price: 委托价格
            volume: 委托数量
            direction: 方向,'BUY'或'SELL'
            order_type: 订单类型,'LIMIT'或'MARKET'
        
        Returns:
            dict: 下单结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        if not self.can_trade:
            return {"success": False, "message": "当前账户无交易权限"}
        
        try:
            # 构建下单参数
            order_params = {
                "session_id": self.session_id,
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "direction": direction.lower(),
                "order_type": order_type.lower()
            }
            
            # 执行下单
            response = self.session.post(f"{self.base_url}/place_order", json=order_params)
            order_result = response.json()
            
            if order_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "order_id": order_result.get("data", {}).get("order_id", ""),
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
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        if not self.can_trade:
            return {"success": False, "message": "当前账户无交易权限"}
        
        try:
            # 构建撤单参数
            cancel_params = {
                "session_id": self.session_id,
                "order_id": order_id
            }
            
            # 执行撤单
            response = self.session.post(f"{self.base_url}/cancel_order", json=cancel_params)
            cancel_result = response.json()
            
            if cancel_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "order_id": order_id,
                        "status": "CANCELLED",
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
    
    def get_orders(self, status: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """
        获取委托列表
        
        Args:
            status: 委托状态筛选
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 委托列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        try:
            # 构建查询参数
            query_params = {"session_id": self.session_id}
            if status:
                query_params["status"] = status
            if start_date:
                query_params["start_date"] = start_date
            if end_date:
                query_params["end_date"] = end_date
            
            # 执行查询
            response = self.session.get(f"{self.base_url}/orders", params=query_params)
            orders_result = response.json()
            
            if orders_result.get("success"):
                return {
                    "success": True,
                    "data": orders_result.get("data", [])
                }
            else:
                return {
                    "success": False,
                    "message": orders_result.get("message", "获取委托列表失败")
                }
        except Exception as e:
            logger.error(f"获取委托列表异常: {str(e)}")
            return {"success": False, "message": f"获取委托列表异常: {str(e)}"}
    
    def get_trades(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        获取成交列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 成交列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        try:
            # 构建查询参数
            query_params = {"session_id": self.session_id}
            if start_date:
                query_params["start_date"] = start_date
            if end_date:
                query_params["end_date"] = end_date
            
            # 执行查询
            response = self.session.get(f"{self.base_url}/trades", params=query_params)
            trades_result = response.json()
            
            if trades_result.get("success"):
                return {
                    "success": True,
                    "data": trades_result.get("data", [])
                }
            else:
                return {
                    "success": False,
                    "message": trades_result.get("message", "获取成交列表失败")
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
            dict: 行情数据
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴证券同花顺"}
        
        try:
            # 构建查询参数
            query_params = {
                "session_id": self.session_id,
                "symbols": ",".join(symbols)
            }
            
            # 执行查询
            response = self.session.get(f"{self.base_url}/quotes", params=query_params)
            quotes_result = response.json()
            
            if quotes_result.get("success"):
                return {
                    "success": True,
                    "data": quotes_result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "message": quotes_result.get("message", "获取实时行情失败")
                }
        except Exception as e:
            logger.error(f"获取实时行情异常: {str(e)}")
            return {"success": False, "message": f"获取实时行情异常: {str(e)}"}
    
    def _check_connection(self) -> bool:
        """检查连接状态"""
        if not self.connected or not self.session_id:
            logger.warning("未连接到东吴证券同花顺,尝试重新连接")
            return self.reconnect()
        return True 
