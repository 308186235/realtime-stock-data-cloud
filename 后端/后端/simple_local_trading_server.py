#!/usr/bin/env python3
"""
简化版本地交易服务器
直接使用已模块化的working-trader-FIXED TraderAPI
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入已模块化的working-trader-FIXED
try:
    from trader_api import TraderAPI, api  # 使用已经模块化的API
    TRADER_API_AVAILABLE = True
    logger.info("✅ 已模块化的working-trader-FIXED加载成功")
    logger.info(f"✅ TraderAPI版本: {api.version}")
except ImportError as e:
    logger.error(f"❌ working-trader-FIXED模块加载失败: {e}")
    TRADER_API_AVAILABLE = False
    api = None

class SimpleLocalTradingServer:
    """简化版本地交易服务器"""
    
    def __init__(self):
        self.cloud_api_url = "https://api.aigupiao.me"
        self.trader_api = api if TRADER_API_AVAILABLE else None
        self.running = False
        
        if self.trader_api:
            logger.info(f"✅ TraderAPI初始化成功 (v{self.trader_api.version})")
            self._test_api()
        else:
            logger.warning("⚠️ TraderAPI不可用")
    
    def _test_api(self):
        """测试API功能"""
        try:
            status = self.trader_api.get_status()
            logger.info(f"✅ API状态: 当前窗口 '{status.get('current_window', 'N/A')}'")
            logger.info(f"✅ 交易软件激活: {status.get('trading_software_active', False)}")
            logger.info(f"✅ 导出文件数: {status.get('export_files', 0)}")
        except Exception as e:
            logger.warning(f"⚠️ API状态检查失败: {e}")
    
    def execute_trade(self, action: str, stock_code: str, quantity: int, price: float = None) -> Dict[str, Any]:
        """执行交易"""
        if not TRADER_API_AVAILABLE:
            return {"success": False, "message": "TraderAPI不可用"}
        
        logger.info(f"💰 执行交易: {action} {stock_code} {quantity}股 @{price or '市价'}")
        
        try:
            if action.lower() == "buy":
                success = self.trader_api.buy(stock_code, quantity, price or "市价")
                action_name = "买入"
            elif action.lower() == "sell":
                success = self.trader_api.sell(stock_code, quantity, price or "市价")
                action_name = "卖出"
            else:
                return {"success": False, "message": f"不支持的交易类型: {action}"}
            
            result_message = f"{action_name}操作{'成功' if success else '失败'}"
            logger.info(f"{'✅' if success else '❌'} {result_message}")
            
            return {
                "success": success,
                "message": result_message,
                "trade_details": {
                    "action": action,
                    "stock_code": stock_code,
                    "quantity": quantity,
                    "price": price or "市价",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            error_msg = f"交易执行异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def export_data(self, data_type: str = "all") -> Dict[str, Any]:
        """导出数据"""
        if not TRADER_API_AVAILABLE:
            return {"success": False, "message": "TraderAPI不可用"}
        
        logger.info(f"📊 执行数据导出: {data_type}")
        
        try:
            if data_type == "all":
                # 使用export_all方法导出所有数据
                results = self.trader_api.export_all()
                logger.info(f"✅ 导出所有数据完成: {results}")
            else:
                results = {}
                if data_type == "holdings":
                    results["holdings"] = self.trader_api.export_positions()
                elif data_type == "transactions":
                    results["transactions"] = self.trader_api.export_trades()
                elif data_type == "orders":
                    results["orders"] = self.trader_api.export_orders()
                else:
                    return {"success": False, "message": f"不支持的导出类型: {data_type}"}
                
                logger.info(f"✅ 导出{data_type}数据完成: {results}")
            
            # 获取导出文件列表
            export_files = self.trader_api.get_files()
            
            return {
                "success": True,
                "message": "数据导出完成",
                "results": results,
                "export_files": export_files,
                "export_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"数据导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        try:
            if TRADER_API_AVAILABLE:
                api_status = self.trader_api.get_status()
                
                return {
                    "success": True,
                    "local_trading_available": True,
                    "trading_software_active": api_status.get("trading_software_active", False),
                    "current_window": api_status.get("current_window", "N/A"),
                    "export_files": api_status.get("export_files", 0),
                    "api_version": self.trader_api.version,
                    "timestamp": datetime.now().isoformat(),
                    "api_status": api_status
                }
            else:
                return {
                    "success": False,
                    "local_trading_available": False,
                    "message": "TraderAPI不可用",
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            error_msg = f"状态检查失败: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg, "timestamp": datetime.now().isoformat()}
    
    def cleanup_files(self):
        """清理过期文件"""
        if not TRADER_API_AVAILABLE:
            return {"success": False, "message": "TraderAPI不可用"}
        
        try:
            self.trader_api.cleanup_files()
            return {"success": True, "message": "文件清理完成"}
        except Exception as e:
            return {"success": False, "message": f"文件清理失败: {e}"}
    
    def handle_cloud_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """处理云端命令"""
        command_type = command.get("type")
        data = command.get("data", {})
        
        logger.info(f"📨 处理云端命令: {command_type}")
        
        try:
            if command_type == "trade":
                return self.execute_trade(
                    action=data.get("action"),
                    stock_code=data.get("stock_code"),
                    quantity=data.get("quantity"),
                    price=data.get("price")
                )
            
            elif command_type == "export":
                return self.export_data(data.get("data_type", "all"))
            
            elif command_type == "status":
                return self.get_status()
            
            elif command_type == "cleanup":
                return self.cleanup_files()
            
            else:
                return {"success": False, "message": f"未知命令类型: {command_type}"}
        
        except Exception as e:
            error_msg = f"命令处理异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def notify_cloud(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """通知云端"""
        try:
            import requests
            
            response = requests.post(
                f"{self.cloud_api_url}/api/cloud-local-trading/notify",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {"success": False, "message": f"HTTP {response.status_code}"}
            
        except Exception as e:
            return {"success": False, "message": f"通知云端失败: {e}"}

# 创建全局服务器实例
local_server = SimpleLocalTradingServer()

def test_local_server():
    """测试本地服务器"""
    print("🧪 测试简化版本地交易服务器")
    print("=" * 50)
    
    # 测试状态
    print("\n📊 测试状态获取...")
    status = local_server.get_status()
    print(f"状态: {status}")
    
    # 测试导出
    print("\n📊 测试数据导出...")
    export_result = local_server.export_data("holdings")
    print(f"导出结果: {export_result}")
    
    # 测试交易(模拟)
    print("\n💰 测试交易执行...")
    trade_result = local_server.execute_trade("buy", "000001", 100, 10.50)
    print(f"交易结果: {trade_result}")
    
    # 测试云端命令处理
    print("\n📨 测试云端命令处理...")
    test_command = {
        "type": "status",
        "data": {}
    }
    command_result = local_server.handle_cloud_command(test_command)
    print(f"命令处理结果: {command_result}")
    
    print("\n✅ 测试完成")

def main():
    """主函数"""
    print("🖥️ 简化版本地交易服务器")
    print("=" * 40)
    print("基于已模块化的working-trader-FIXED TraderAPI")
    print()
    
    if not TRADER_API_AVAILABLE:
        print("❌ TraderAPI不可用,请确保以下文件存在:")
        print("  - trader_api.py")
        print("  - trader_buy_sell.py")
        print("  - trader_export.py")
        print("  - trader_core.py")
        return
    
    print(f"✅ TraderAPI版本: {api.version}")
    print()
    
    # 选择操作
    while True:
        print("\n请选择操作:")
        print("1. 测试服务器功能")
        print("2. 查看状态")
        print("3. 导出数据")
        print("4. 模拟交易")
        print("5. 清理文件")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-5): ").strip()
        
        if choice == "0":
            print("👋 退出程序")
            break
        elif choice == "1":
            test_local_server()
        elif choice == "2":
            status = local_server.get_status()
            print(f"\n📊 当前状态:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
        elif choice == "3":
            data_type = input("导出类型 (all/holdings/transactions/orders) [all]: ").strip() or "all"
            result = local_server.export_data(data_type)
            print(f"\n📊 导出结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            action = input("交易类型 (buy/sell) [buy]: ").strip() or "buy"
            code = input("股票代码 [000001]: ").strip() or "000001"
            quantity = int(input("交易数量 [100]: ").strip() or "100")
            price_input = input("交易价格 (回车为市价): ").strip()
            price = float(price_input) if price_input else None
            
            result = local_server.execute_trade(action, code, quantity, price)
            print(f"\n💰 交易结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            result = local_server.cleanup_files()
            print(f"\n🧹 清理结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ 无效选择,请重新输入")

if __name__ == "__main__":
    main()
