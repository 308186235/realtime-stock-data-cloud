import logging
import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# PTRADE SDK import attempt
try:
    # 尝试导入PTRADE SDK
    sys.path.append(os.environ.get('PTRADE_PATH', 'C:/Program Files/PTRADE'))
    import ptrade_api as pa
except ImportError:
    logging.error("无法导入PTRADE SDK,请确保PTRADE已正确安装并设置PTRADE_PATH环境变量")

logger = logging.getLogger(__name__)

class PTradeDongwuBroker:
    """
    东吴证券秀才PTRADE接口
    """
    def __init__(self, account_id: str, account_pwd: str, broker_id: str = "DONGWU_PTRADE", 
                 server_ip: str = None, server_port: int = None):
        """
        初始化东吴证券秀才PTRADE接口
        
        Args:
            account_id: 证券账号
            account_pwd: 账号密码
            broker_id: 券商ID标识
            server_ip: 服务器IP地址,默认为None表示使用配置文件中的默认地址
            server_port: 服务器端口,默认为None表示使用配置文件中的默认端口
        """
        self.account_id = account_id
        self.account_pwd = account_pwd
        self.broker_id = broker_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected = False
        self.session_id = None
        self.ptrade_instance = None
        
        # 交易权限标志
        self.can_trade = False
        
        # 行情访问权限
        self.can_access_market = False
        
        # 初始化连接
        self._init_connection()
    
    def _init_connection(self) -> bool:
        """初始化连接到东吴秀才PTRADE"""
        try:
            # 创建PTRADE实例
            if self.server_ip and self.server_port:
                self.ptrade_instance = pa.PTrade(
                    server_ip=self.server_ip,
                    server_port=self.server_port
                )
            else:
                self.ptrade_instance = pa.PTrade()  # 使用默认配置
            
            # 登录东吴秀才账户
            login_result = self.ptrade_instance.login(
                username=self.account_id,
                password=self.account_pwd,
                broker_type="DONGWU"  # 东吴证券标识
            )
            
            if login_result["success"]:
                self.connected = True
                self.session_id = login_result.get("session_id")
                self.can_trade = True
                self.can_access_market = True
                logger.info(f"已成功连接东吴秀才PTRADE接口,账户:{self.account_id}")
                return True
            else:
                logger.error(f"连接东吴秀才PTRADE接口失败: {login_result.get('message', '未知错误')}")
                return False
        except Exception as e:
            logger.error(f"初始化东吴秀才PTRADE接口异常: {str(e)}")
            return False
    
    def reconnect(self) -> bool:
        """重新连接到东吴秀才PTRADE"""
        self.disconnect()
        time.sleep(1)
        return self._init_connection()
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.ptrade_instance and self.connected:
            try:
                self.ptrade_instance.logout()
                logger.info(f"已断开东吴秀才PTRADE接口连接,账户:{self.account_id}")
            except Exception as e:
                logger.error(f"断开东吴秀才PTRADE接口连接异常: {str(e)}")
        
        self.connected = False
        self.session_id = None
        self.can_trade = False
        self.can_access_market = False
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        try:
            account_info = self.ptrade_instance.get_account_info()
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
                    "risk_level": account_info.get("risk_level", ""),
                    "update_time": account_info.get("update_time", "")
                }
            }
        except Exception as e:
            logger.error(f"获取账户信息异常: {str(e)}")
            return {"success": False, "message": f"获取账户信息异常: {str(e)}"}
    
    def get_positions(self) -> Dict:
        """获取持仓信息"""
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        try:
            positions = self.ptrade_instance.get_positions()
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
                    "holding_days": pos.get("holding_days", 0),
                    "exchange": pos.get("exchange", "")
                })
            
            return {
                "success": True,
                "data": position_list
            }
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
            order_type: 订单类型,'LIMIT'(限价)或'MARKET'(市价)
        
        Returns:
            dict: 下单结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        if not self.can_trade:
            return {"success": False, "message": "当前账户无交易权限"}
        
        try:
            # 转换交易方向
            ptrade_direction = "buy" if direction.upper() == "BUY" else "sell"
            
            # 转换订单类型
            ptrade_order_type = "limit" if order_type.upper() == "LIMIT" else "market"
            
            # 构建下单参数
            order_params = {
                "symbol": symbol,
                "price": price if ptrade_order_type == "limit" else 0,
                "volume": volume,
                "direction": ptrade_direction,
                "order_type": ptrade_order_type
            }
            
            # 执行下单
            order_result = self.ptrade_instance.place_order(**order_params)
            
            if order_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "order_id": order_result.get("order_id", ""),
                        "symbol": symbol,
                        "price": price,
                        "volume": volume,
                        "direction": direction,
                        "order_type": order_type,
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
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        try:
            # 执行撤单
            cancel_result = self.ptrade_instance.cancel_order(order_id=order_id)
            
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
    
    def get_orders(self, start_date: str = None, end_date: str = None, status: str = None) -> Dict:
        """
        获取委托列表
        
        Args:
            start_date: 开始日期,格式'YYYY-MM-DD'
            end_date: 结束日期,格式'YYYY-MM-DD'
            status: 委托状态,None表示全部
        
        Returns:
            dict: 委托列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        try:
            # 获取委托列表
            orders = self.ptrade_instance.get_orders(
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            
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
                    "order_type": order.get("order_type", "LIMIT").upper(),
                    "status": order.get("status", ""),
                    "submit_time": order.get("submit_time", ""),
                    "update_time": order.get("update_time", ""),
                    "message": order.get("message", "")
                })
            
            return {
                "success": True,
                "data": order_list
            }
        except Exception as e:
            logger.error(f"获取委托列表异常: {str(e)}")
            return {"success": False, "message": f"获取委托列表异常: {str(e)}"}
    
    def get_trades(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        获取成交列表
        
        Args:
            start_date: 开始日期,格式'YYYY-MM-DD'
            end_date: 结束日期,格式'YYYY-MM-DD'
        
        Returns:
            dict: 成交列表
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        try:
            # 获取成交列表
            trades = self.ptrade_instance.get_trades(
                start_date=start_date,
                end_date=end_date
            )
            
            trade_list = []
            for trade in trades:
                trade_list.append({
                    "trade_id": trade.get("trade_id", ""),
                    "order_id": trade.get("order_id", ""),
                    "symbol": trade.get("symbol", ""),
                    "name": trade.get("name", ""),
                    "price": trade.get("price", 0),
                    "volume": trade.get("volume", 0),
                    "amount": trade.get("amount", 0),
                    "direction": "BUY" if trade.get("direction") == "buy" else "SELL",
                    "trade_time": trade.get("trade_time", ""),
                    "commission": trade.get("commission", 0),
                    "tax": trade.get("tax", 0),
                    "exchange": trade.get("exchange", "")
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
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        if not self.can_access_market:
            return {"success": False, "message": "当前账户无行情访问权限"}
        
        try:
            # 获取实时行情
            quotes = self.ptrade_instance.get_realtime_quotes(symbols=symbols)
            
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
                    "bid_prices": [
                        quote.get("bid1", 0),
                        quote.get("bid2", 0),
                        quote.get("bid3", 0),
                        quote.get("bid4", 0),
                        quote.get("bid5", 0),
                    ],
                    "bid_volumes": [
                        quote.get("bid1_volume", 0),
                        quote.get("bid2_volume", 0),
                        quote.get("bid3_volume", 0),
                        quote.get("bid4_volume", 0),
                        quote.get("bid5_volume", 0),
                    ],
                    "ask_prices": [
                        quote.get("ask1", 0),
                        quote.get("ask2", 0),
                        quote.get("ask3", 0),
                        quote.get("ask4", 0),
                        quote.get("ask5", 0),
                    ],
                    "ask_volumes": [
                        quote.get("ask1_volume", 0),
                        quote.get("ask2_volume", 0),
                        quote.get("ask3_volume", 0),
                        quote.get("ask4_volume", 0),
                        quote.get("ask5_volume", 0),
                    ],
                    "update_time": quote.get("update_time", ""),
                    "exchange": quote.get("exchange", ""),
                    "status": quote.get("status", "")
                })
            
            return {
                "success": True,
                "data": quote_list
            }
        except Exception as e:
            logger.error(f"获取实时行情异常: {str(e)}")
            return {"success": False, "message": f"获取实时行情异常: {str(e)}"}
    
    def get_klines(self, symbol: str, period: str = "1d", 
                 start_date: str = None, end_date: str = None, count: int = 100) -> Dict:
        """
        获取K线数据
        
        Args:
            symbol: 证券代码
            period: K线周期,如 '1m', '5m', '15m', '30m', '1h', '1d', '1w', '1M'
            start_date: 开始日期,格式'YYYY-MM-DD'
            end_date: 结束日期,格式'YYYY-MM-DD'
            count: 返回K线数量,默认100
        
        Returns:
            dict: K线数据
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        if not self.can_access_market:
            return {"success": False, "message": "当前账户无行情访问权限"}
        
        try:
            # 获取K线数据
            klines = self.ptrade_instance.get_klines(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                count=count
            )
            
            kline_list = []
            for kline in klines:
                kline_list.append({
                    "time": kline.get("time", ""),
                    "open": kline.get("open", 0),
                    "high": kline.get("high", 0),
                    "low": kline.get("low", 0),
                    "close": kline.get("close", 0),
                    "volume": kline.get("volume", 0),
                    "amount": kline.get("amount", 0),
                })
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "period": period,
                    "klines": kline_list
                }
            }
        except Exception as e:
            logger.error(f"获取K线数据异常: {str(e)}")
            return {"success": False, "message": f"获取K线数据异常: {str(e)}"}
    
    def transfer(self, amount: float, transfer_type: str) -> Dict:
        """
        银证转账
        
        Args:
            amount: 转账金额
            transfer_type: 转账类型,'BANK_TO_SECURITY'(银行转证券)或'SECURITY_TO_BANK'(证券转银行)
        
        Returns:
            dict: 转账结果
        """
        if not self._check_connection():
            return {"success": False, "message": "未连接到东吴秀才PTRADE"}
        
        if not self.can_trade:
            return {"success": False, "message": "当前账户无交易权限"}
        
        try:
            # 转换转账类型
            ptrade_transfer_type = "in" if transfer_type == "BANK_TO_SECURITY" else "out"
            
            # 执行转账
            transfer_result = self.ptrade_instance.transfer(
                amount=amount,
                transfer_type=ptrade_transfer_type
            )
            
            if transfer_result.get("success"):
                return {
                    "success": True,
                    "data": {
                        "transfer_id": transfer_result.get("transfer_id", ""),
                        "amount": amount,
                        "transfer_type": transfer_type,
                        "status": "SUBMITTED",
                        "message": "转账请求已提交"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": transfer_result.get("message", "转账失败,未知错误")
                }
        except Exception as e:
            logger.error(f"银证转账异常: {str(e)}")
            return {"success": False, "message": f"银证转账异常: {str(e)}"}
    
    def _check_connection(self) -> bool:
        """检查连接状态,如果未连接则尝试重连"""
        if not self.connected:
            logger.warning("未连接到东吴秀才PTRADE,尝试重新连接...")
            return self.reconnect()
        return True 
