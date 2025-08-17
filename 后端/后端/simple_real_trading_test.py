#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的真实交易测试
直接测试云端Agent调用本地电脑交易功能,不使用模拟数据
"""

import time
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTradingTest:
    """真实交易测试"""
    
    def __init__(self):
        self.trade_history = []
        self.init_trading_modules()
    
    def init_trading_modules(self):
        """初始化交易模块"""
        try:
            # 导入真实的交易模块
            import trader_buy_sell
            import trader_export
            import trader_core
            
            self.trader_buy_sell = trader_buy_sell
            self.trader_export = trader_export
            self.trader_core = trader_core
            
            logger.info("✅ 真实交易模块导入成功")
            
            # 检查交易软件状态
            status = self.check_trading_software()
            if status:
                logger.info("✅ 交易软件状态正常")
            else:
                logger.warning("⚠️ 交易软件未激活,请确保东吴证券软件正在运行")
                
        except ImportError as e:
            logger.error(f"❌ 无法导入交易模块: {e}")
            logger.error("请确保trader_buy_sell.py, trader_export.py, trader_core.py等文件存在")
            raise Exception("交易模块导入失败")
        except Exception as e:
            logger.error(f"❌ 交易模块初始化失败: {e}")
            raise Exception(f"交易模块初始化失败: {e}")
    
    def check_trading_software(self):
        """检查交易软件状态"""
        try:
            import win32gui

            def enum_windows_proc(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    # 更精确的匹配您的交易软件
                    trading_keywords = [
                        "网上股票交易系统5.0", "网上股票交易系统", "东吴证券",
                        "网上交易", "股票交易", "证券交易"
                    ]

                    for keyword in trading_keywords:
                        if keyword in window_text:
                            windows.append((hwnd, window_text))
                            break
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_proc, windows)

            if windows:
                logger.info(f"✅ 找到交易软件窗口: {windows[0][1]} (句柄: {windows[0][0]})")
                return True
            else:
                logger.warning("❌ 未找到交易软件窗口")
                logger.warning("请确保东吴证券软件正在运行且窗口可见")
                return False

        except Exception as e:
            logger.error(f"检查交易软件失败: {e}")
            return False
    
    def execute_real_buy(self, stock_code: str, quantity: int, price: str = "市价"):
        """执行真实买入"""
        logger.info(f"💰 执行真实买入: {stock_code} {quantity}股 @{price}")
        
        try:
            # 检查交易软件状态
            if not self.check_trading_software():
                return {"success": False, "message": "交易软件未激活"}
            
            # 执行买入 - 正确的参数顺序:(code, price, quantity)
            success = self.trader_buy_sell.buy_stock(stock_code, price, quantity)
            
            # 记录交易
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "buy",
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "success": success,
                "mode": "REAL_TRADING"
            }
            
            self.trade_history.append(trade_record)
            
            if success:
                logger.info(f"✅ 买入成功: {stock_code}")
                return {"success": True, "message": f"买入{stock_code}成功", "trade": trade_record}
            else:
                logger.error(f"❌ 买入失败: {stock_code}")
                return {"success": False, "message": f"买入{stock_code}失败", "trade": trade_record}
                
        except Exception as e:
            error_msg = f"买入异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def execute_real_sell(self, stock_code: str, quantity: int, price: str = "市价"):
        """执行真实卖出"""
        logger.info(f"💰 执行真实卖出: {stock_code} {quantity}股 @{price}")
        
        try:
            # 检查交易软件状态
            if not self.check_trading_software():
                return {"success": False, "message": "交易软件未激活"}
            
            # 执行卖出 - 正确的参数顺序:(code, price, quantity)
            success = self.trader_buy_sell.sell_stock(stock_code, price, quantity)
            
            # 记录交易
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "sell",
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "success": success,
                "mode": "REAL_TRADING"
            }
            
            self.trade_history.append(trade_record)
            
            if success:
                logger.info(f"✅ 卖出成功: {stock_code}")
                return {"success": True, "message": f"卖出{stock_code}成功", "trade": trade_record}
            else:
                logger.error(f"❌ 卖出失败: {stock_code}")
                return {"success": False, "message": f"卖出{stock_code}失败", "trade": trade_record}
                
        except Exception as e:
            error_msg = f"卖出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def export_real_holdings(self):
        """导出真实持仓"""
        logger.info("📊 导出真实持仓数据")
        
        try:
            # 检查交易软件状态
            if not self.check_trading_software():
                return {"success": False, "message": "交易软件未激活"}
            
            # 执行导出
            success = self.trader_export.export_holdings()
            
            if success:
                # 读取导出的文件
                latest_file = self.trader_export.get_latest_export_file("holdings")
                if latest_file:
                    holdings = self.trader_export.read_csv_file(latest_file)
                    if holdings:
                        logger.info(f"✅ 持仓导出成功,共{len(holdings)}条记录")
                        return {
                            "success": True,
                            "message": f"持仓导出成功,共{len(holdings)}条记录",
                            "data": holdings
                        }
                    else:
                        logger.warning("⚠️ 持仓导出成功但无法读取文件")
                        return {"success": True, "message": "持仓导出成功但无法读取文件", "data": []}
                else:
                    logger.warning("⚠️ 持仓导出成功但未找到文件")
                    return {"success": True, "message": "持仓导出成功但未找到文件", "data": []}
            else:
                logger.error("❌ 持仓导出失败")
                return {"success": False, "message": "持仓导出失败"}
                
        except Exception as e:
            error_msg = f"持仓导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def export_real_transactions(self):
        """导出真实成交记录"""
        logger.info("📋 导出真实成交记录")
        
        try:
            # 检查交易软件状态
            if not self.check_trading_software():
                return {"success": False, "message": "交易软件未激活"}
            
            # 执行导出
            success = self.trader_export.export_transactions()
            
            if success:
                # 读取导出的文件
                latest_file = self.trader_export.get_latest_export_file("transactions")
                if latest_file:
                    transactions = self.trader_export.read_csv_file(latest_file)
                    if transactions:
                        logger.info(f"✅ 成交记录导出成功,共{len(transactions)}条记录")
                        return {
                            "success": True,
                            "message": f"成交记录导出成功,共{len(transactions)}条记录",
                            "data": transactions
                        }
                    else:
                        logger.warning("⚠️ 成交记录导出成功但无法读取文件")
                        return {"success": True, "message": "成交记录导出成功但无法读取文件", "data": []}
                else:
                    logger.warning("⚠️ 成交记录导出成功但未找到文件")
                    return {"success": True, "message": "成交记录导出成功但未找到文件", "data": []}
            else:
                logger.error("❌ 成交记录导出失败")
                return {"success": False, "message": "成交记录导出失败"}
                
        except Exception as e:
            error_msg = f"成交记录导出异常: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def show_trade_summary(self):
        """显示交易总结"""
        print(f"\n📋 真实交易总结:")
        print("=" * 50)
        
        if not self.trade_history:
            print("📝 暂无交易记录")
            return
        
        buy_count = sum(1 for trade in self.trade_history if trade['action'] == 'buy')
        sell_count = sum(1 for trade in self.trade_history if trade['action'] == 'sell')
        success_count = sum(1 for trade in self.trade_history if trade['success'])
        
        print(f"📊 交易统计:")
        print(f"   - 总交易次数: {len(self.trade_history)}")
        print(f"   - 买入次数: {buy_count}")
        print(f"   - 卖出次数: {sell_count}")
        print(f"   - 成功次数: {success_count}")
        print(f"   - 成功率: {success_count/len(self.trade_history)*100:.1f}%")
        
        print(f"\n📝 交易明细:")
        for i, trade in enumerate(self.trade_history, 1):
            success = "✅" if trade['success'] else "❌"
            print(f"   {i}. {success} {trade['action'].upper()} {trade['stock_code']} {trade['quantity']}股 @{trade['price']} [{trade['timestamp'][:19]}]")

def demo_real_cloud_agent_trading():
    """演示真实云端Agent交易"""
    print("🎯 真实云端Agent调用本地电脑交易演示")
    print("=" * 80)
    print("⚠️ 警告: 这是真实交易演示,所有操作都会影响实际账户!")
    print("请确保:")
    print("1. 现在是收盘时间,不会实际成交")
    print("2. 东吴证券软件已启动并登录")
    print("3. 您了解交易风险")
    print("=" * 80)
    
    confirm = input("确认继续演示? (输入 'YES' 继续): ")
    if confirm != "YES":
        print("已取消演示")
        return
    
    # 创建真实交易测试实例
    try:
        trading_test = RealTradingTest()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 1. 获取真实持仓数据
    print("\n📊 步骤1: 获取真实持仓数据")
    holdings_result = trading_test.export_real_holdings()
    if holdings_result["success"]:
        print(f"✅ {holdings_result['message']}")
        if holdings_result.get("data"):
            print("   持仓详情:")
            for i, holding in enumerate(holdings_result["data"][:5], 1):
                if isinstance(holding, dict):
                    code = holding.get('股票代码', holding.get('code', ''))
                    name = holding.get('股票名称', holding.get('name', ''))
                    quantity = holding.get('股票余额', holding.get('quantity', 0))
                    print(f"     {i}. {code} {name}: {quantity}股")
    else:
        print(f"❌ {holdings_result['message']}")
    
    # 2. 获取真实成交记录
    print("\n📋 步骤2: 获取真实成交记录")
    transactions_result = trading_test.export_real_transactions()
    if transactions_result["success"]:
        print(f"✅ {transactions_result['message']}")
        if transactions_result.get("data"):
            print("   最近成交:")
            for i, transaction in enumerate(transactions_result["data"][-3:], 1):
                if isinstance(transaction, dict):
                    code = transaction.get('证券代码', transaction.get('code', ''))
                    name = transaction.get('证券名称', transaction.get('name', ''))
                    action = transaction.get('买卖标志', transaction.get('action', ''))
                    quantity = transaction.get('成交数量', transaction.get('quantity', 0))
                    price = transaction.get('成交价格', transaction.get('price', 0))
                    print(f"     {i}. {action} {code} {name}: {quantity}股 @{price}")
    else:
        print(f"❌ {transactions_result['message']}")
    
    # 3. 演示真实交易(收盘时间,不会实际成交)
    print("\n💰 步骤3: 演示真实交易指令")
    print("注意: 收盘时间发送的指令不会实际成交")
    
    # 演示买入
    print("\n🔵 演示买入指令:")
    buy_result = trading_test.execute_real_buy("000001", 100, "10.50")
    print(f"结果: {buy_result['message']}")
    
    time.sleep(2)
    
    # 演示卖出
    print("\n🔴 演示卖出指令:")
    sell_result = trading_test.execute_real_sell("000002", 100, "18.60")
    print(f"结果: {sell_result['message']}")
    
    # 4. 显示交易总结
    print("\n📋 步骤4: 交易总结")
    trading_test.show_trade_summary()
    
    print("\n🎉 真实交易演示完成!")
    print("💡 提示: 这个演示展示了云端Agent如何调用本地电脑进行真实交易")
    print("⚠️ 在交易时间内,这些指令会实际执行并影响您的账户")

def main():
    """主函数"""
    try:
        demo_real_cloud_agent_trading()
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"❌ 演示失败: {e}")

if __name__ == "__main__":
    main()
