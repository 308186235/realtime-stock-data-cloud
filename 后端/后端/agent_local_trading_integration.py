#!/usr/bin/env python3
"""
Agent本地交易软件集成系统
基于working-trader-FIXED的模块化实现,为Agent提供完整的本地交易接口
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import threading
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TradeRequest:
    """交易请求"""
    action: str  # "buy" or "sell"
    stock_code: str
    quantity: int
    price: Optional[float] = None  # None表示市价
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class TradeResult:
    """交易结果"""
    success: bool
    message: str
    trade_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class LocalTradingInterface:
    """本地交易软件接口"""
    
    def __init__(self):
        self.is_initialized = False
        self.trading_api = None
        self.last_export_time = None
        
        # 导入本地交易模块
        self._import_trading_modules()
    
    def _import_trading_modules(self):
        """导入本地交易模块"""
        try:
            # 导入模块化的交易API
            from trader_api import TraderAPI
            self.trading_api = TraderAPI()
            
            # 导入核心功能
            from trader_core import get_current_focus, cleanup_old_export_files
            from trader_buy_sell import buy_stock, sell_stock
            from trader_export import export_holdings, export_transactions, export_orders
            
            self.get_current_focus = get_current_focus
            self.cleanup_old_export_files = cleanup_old_export_files
            self.buy_stock = buy_stock
            self.sell_stock = sell_stock
            self.export_holdings = export_holdings
            self.export_transactions = export_transactions
            self.export_orders = export_orders
            
            self.is_initialized = True
            logger.info("✅ 本地交易模块加载成功")
            
        except ImportError as e:
            logger.error(f"❌ 本地交易模块加载失败: {e}")
            logger.info("💡 请确保working-trader-FIXED相关模块存在")
            self.is_initialized = False
    
    def check_trading_software_status(self) -> Dict[str, Any]:
        """检查交易软件状态"""
        if not self.is_initialized:
            return {
                "status": "error",
                "message": "本地交易模块未初始化",
                "trading_software_active": False
            }
        
        try:
            hwnd, current_title = self.get_current_focus()
            trading_software_active = "交易" in current_title or "股票" in current_title
            
            return {
                "status": "success",
                "current_window": current_title,
                "trading_software_active": trading_software_active,
                "window_handle": hwnd
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查状态失败: {e}",
                "trading_software_active": False
            }
    
    def execute_trade(self, trade_request: TradeRequest) -> TradeResult:
        """执行交易"""
        if not self.is_initialized:
            return TradeResult(
                success=False,
                message="本地交易模块未初始化"
            )
        
        logger.info(f"🔄 执行交易: {trade_request.action} {trade_request.stock_code} {trade_request.quantity}股")
        
        try:
            # 检查交易软件状态
            status = self.check_trading_software_status()
            if not status.get("trading_software_active", False):
                logger.warning("⚠️ 交易软件未激活,尝试继续执行")
            
            # 执行交易
            if trade_request.action.lower() == "buy":
                success = self._execute_buy(trade_request)
            elif trade_request.action.lower() == "sell":
                success = self._execute_sell(trade_request)
            else:
                return TradeResult(
                    success=False,
                    message=f"不支持的交易类型: {trade_request.action}"
                )
            
            if success:
                return TradeResult(
                    success=True,
                    message=f"{trade_request.action}操作执行成功",
                    trade_id=f"{trade_request.action}_{trade_request.stock_code}_{int(time.time())}"
                )
            else:
                return TradeResult(
                    success=False,
                    message=f"{trade_request.action}操作执行失败"
                )
                
        except Exception as e:
            logger.error(f"❌ 交易执行异常: {e}")
            return TradeResult(
                success=False,
                message=f"交易执行异常: {e}"
            )
    
    def _execute_buy(self, trade_request: TradeRequest) -> bool:
        """执行买入操作"""
        price_str = str(trade_request.price) if trade_request.price else "市价"
        
        return self.buy_stock(
            code=trade_request.stock_code,
            price=price_str,
            quantity=str(trade_request.quantity)
        )
    
    def _execute_sell(self, trade_request: TradeRequest) -> bool:
        """执行卖出操作"""
        price_str = str(trade_request.price) if trade_request.price else "市价"
        
        return self.sell_stock(
            code=trade_request.stock_code,
            price=price_str,
            quantity=str(trade_request.quantity)
        )
    
    def export_data(self, data_type: str = "all") -> Dict[str, Any]:
        """导出数据"""
        if not self.is_initialized:
            return {
                "success": False,
                "message": "本地交易模块未初始化"
            }
        
        logger.info(f"📊 导出数据: {data_type}")
        
        try:
            # 清理过期文件
            self.cleanup_old_export_files()
            
            results = {}
            
            if data_type == "all" or data_type == "holdings":
                results["holdings"] = self.export_holdings()
            
            if data_type == "all" or data_type == "transactions":
                results["transactions"] = self.export_transactions()
            
            if data_type == "all" or data_type == "orders":
                results["orders"] = self.export_orders()
            
            self.last_export_time = datetime.now()
            
            return {
                "success": True,
                "message": "数据导出完成",
                "results": results,
                "export_time": self.last_export_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 数据导出异常: {e}")
            return {
                "success": False,
                "message": f"数据导出异常: {e}"
            }

class AgentTradingController:
    """Agent交易控制器"""
    
    def __init__(self):
        self.local_interface = LocalTradingInterface()
        self.trade_history = []
        self.is_running = False
        
    def start(self):
        """启动交易控制器"""
        if not self.local_interface.is_initialized:
            logger.error("❌ 本地交易接口未初始化,无法启动")
            return False
        
        self.is_running = True
        logger.info("🚀 Agent交易控制器已启动")
        return True
    
    def stop(self):
        """停止交易控制器"""
        self.is_running = False
        logger.info("⏹️ Agent交易控制器已停止")
    
    def execute_agent_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent决策"""
        if not self.is_running:
            return {
                "success": False,
                "message": "交易控制器未运行"
            }
        
        logger.info(f"🤖 执行Agent决策: {decision}")
        
        try:
            # 解析决策
            action = decision.get("action", "").lower()
            stock_code = decision.get("stock_code", "")
            quantity = decision.get("quantity", 0)
            price = decision.get("price")  # 可选
            
            # 验证参数
            if not action or action not in ["buy", "sell"]:
                return {
                    "success": False,
                    "message": f"无效的交易动作: {action}"
                }
            
            if not stock_code:
                return {
                    "success": False,
                    "message": "股票代码不能为空"
                }
            
            if quantity <= 0:
                return {
                    "success": False,
                    "message": f"无效的交易数量: {quantity}"
                }
            
            # 创建交易请求
            trade_request = TradeRequest(
                action=action,
                stock_code=stock_code,
                quantity=quantity,
                price=price
            )
            
            # 执行交易
            result = self.local_interface.execute_trade(trade_request)
            
            # 记录交易历史
            self.trade_history.append({
                "request": trade_request,
                "result": result,
                "timestamp": datetime.now()
            })
            
            return {
                "success": result.success,
                "message": result.message,
                "trade_id": result.trade_id,
                "timestamp": result.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 执行Agent决策异常: {e}")
            return {
                "success": False,
                "message": f"执行异常: {e}"
            }
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """获取投资组合数据"""
        logger.info("📊 获取投资组合数据")
        
        # 导出最新数据
        export_result = self.local_interface.export_data("all")
        
        if not export_result["success"]:
            return {
                "success": False,
                "message": export_result["message"]
            }
        
        # 这里可以添加数据解析逻辑
        # 读取导出的CSV文件并解析为结构化数据
        
        return {
            "success": True,
            "message": "投资组合数据获取成功",
            "export_result": export_result,
            "data_files": self._get_latest_export_files()
        }
    
    def _get_latest_export_files(self) -> List[str]:
        """获取最新的导出文件列表"""
        try:
            import glob
            patterns = [
                "持仓数据_*.csv",
                "成交数据_*.csv",
                "委托数据_*.csv"
            ]
            
            files = []
            for pattern in patterns:
                files.extend(glob.glob(pattern))
            
            # 按修改时间排序
            files.sort(key=os.path.getmtime, reverse=True)
            return files[:10]  # 返回最新的10个文件
            
        except Exception as e:
            logger.error(f"❌ 获取导出文件列表失败: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """获取控制器状态"""
        software_status = self.local_interface.check_trading_software_status()
        
        return {
            "controller_running": self.is_running,
            "local_interface_initialized": self.local_interface.is_initialized,
            "trading_software_status": software_status,
            "trade_history_count": len(self.trade_history),
            "last_export_time": self.local_interface.last_export_time.isoformat() if self.local_interface.last_export_time else None
        }

# 全局实例
agent_trading_controller = AgentTradingController()

def create_api_endpoints():
    """创建API端点函数"""
    
    def api_execute_trade(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API端点: 执行交易"""
        return agent_trading_controller.execute_agent_decision(request_data)
    
    def api_export_data(data_type: str = "all") -> Dict[str, Any]:
        """API端点: 导出数据"""
        return agent_trading_controller.local_interface.export_data(data_type)
    
    def api_get_portfolio() -> Dict[str, Any]:
        """API端点: 获取投资组合"""
        return agent_trading_controller.get_portfolio_data()
    
    def api_get_status() -> Dict[str, Any]:
        """API端点: 获取状态"""
        return agent_trading_controller.get_status()
    
    def api_start_controller() -> Dict[str, Any]:
        """API端点: 启动控制器"""
        success = agent_trading_controller.start()
        return {
            "success": success,
            "message": "控制器启动成功" if success else "控制器启动失败"
        }
    
    def api_stop_controller() -> Dict[str, Any]:
        """API端点: 停止控制器"""
        agent_trading_controller.stop()
        return {
            "success": True,
            "message": "控制器已停止"
        }
    
    return {
        "execute_trade": api_execute_trade,
        "export_data": api_export_data,
        "get_portfolio": api_get_portfolio,
        "get_status": api_get_status,
        "start_controller": api_start_controller,
        "stop_controller": api_stop_controller
    }

# 测试函数
def test_integration():
    """测试集成功能"""
    print("🧪 测试Agent本地交易集成")
    print("=" * 50)
    
    # 启动控制器
    controller = AgentTradingController()
    if not controller.start():
        print("❌ 控制器启动失败")
        return
    
    # 测试状态检查
    print("\n📊 检查状态...")
    status = controller.get_status()
    print(f"控制器运行: {status['controller_running']}")
    print(f"本地接口初始化: {status['local_interface_initialized']}")
    print(f"交易软件激活: {status['trading_software_status'].get('trading_software_active', False)}")
    
    # 测试数据导出
    print("\n📊 测试数据导出...")
    export_result = controller.local_interface.export_data("holdings")
    print(f"导出结果: {export_result['success']}")
    print(f"导出消息: {export_result['message']}")
    
    # 测试交易决策执行(模拟)
    print("\n🤖 测试交易决策执行...")
    test_decision = {
        "action": "buy",
        "stock_code": "000001",
        "quantity": 100,
        "price": 10.50
    }
    
    trade_result = controller.execute_agent_decision(test_decision)
    print(f"交易结果: {trade_result['success']}")
    print(f"交易消息: {trade_result['message']}")
    
    # 停止控制器
    controller.stop()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_integration()
