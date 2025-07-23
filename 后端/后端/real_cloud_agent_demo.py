#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实云端Agent演示
展示云端Agent调用本地电脑进行真实交易
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class RealCloudAgent:
    """真实云端Agent"""
    
    def __init__(self, name: str, local_api_url: str = "http://localhost:8889"):
        self.name = name
        self.local_api_url = local_api_url
        self.agent_id = f"real_agent_{int(time.time())}"
        self.trade_history = []
        
    def check_local_connection(self) -> bool:
        """检查本地连接"""
        try:
            response = requests.get(f"{self.local_api_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 本地连接正常")
                print(f"   - 服务状态: {data.get('service_running')}")
                print(f"   - 交易API: {data.get('trader_api_available')}")
                print(f"   - 交易软件: {data.get('trading_software_active')}")
                print(f"   - 运行模式: {data.get('mode')}")
                
                if not data.get('trading_software_active'):
                    print("⚠️ 警告: 交易软件未激活,请启动东吴证券软件并登录")
                    return False
                
                return True
            else:
                print(f"❌ 本地连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 本地连接异常: {e}")
            return False
    
    def execute_real_trade(self, action: str, stock_code: str, quantity: int, price: str = "市价") -> Dict[str, Any]:
        """执行真实交易"""
        print(f"\n🤖 {self.name} 执行真实交易:")
        print(f"   - 操作: {action}")
        print(f"   - 股票: {stock_code}")
        print(f"   - 数量: {quantity}")
        print(f"   - 价格: {price}")
        print(f"   ⚠️ 注意: 这是真实交易,会影响实际账户!")
        
        try:
            trade_data = {
                "action": action,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price
            }
            
            print(f"📤 发送真实交易指令到本地电脑...")
            response = requests.post(f"{self.local_api_url}/trade", json=trade_data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 交易执行完成!")
                print(f"   - 结果: {result.get('message')}")
                print(f"   - 交易ID: {result.get('trade_id')}")
                print(f"   - 时间: {result.get('trade_details', {}).get('timestamp')}")
                
                # 记录交易历史
                self.trade_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": action,
                    "stock_code": stock_code,
                    "quantity": quantity,
                    "price": price,
                    "result": result
                })
                
                return result
            else:
                error_msg = f"交易失败: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"交易异常: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def get_real_portfolio(self) -> Dict[str, Any]:
        """获取真实投资组合"""
        print(f"\n📊 {self.name} 获取真实投资组合...")
        
        try:
            export_data = {"data_type": "holdings"}
            
            response = requests.post(f"{self.local_api_url}/export", json=export_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 投资组合获取成功!")
                
                data = result.get('data', [])
                if isinstance(data, list) and data:
                    print(f"   - 持仓股票: {len(data)}只")
                    
                    for i, holding in enumerate(data[:5]):  # 显示前5只
                        if isinstance(holding, dict):
                            code = holding.get('股票代码', holding.get('code', ''))
                            name = holding.get('股票名称', holding.get('name', ''))
                            quantity = holding.get('股票余额', holding.get('quantity', 0))
                            print(f"     {i+1}. {code} {name}: {quantity}股")
                        else:
                            print(f"     {i+1}. {holding}")
                else:
                    print("   - 暂无持仓数据")
                
                return result
            else:
                error_msg = f"获取投资组合失败: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"获取投资组合异常: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def get_real_transactions(self) -> Dict[str, Any]:
        """获取真实成交记录"""
        print(f"\n📋 {self.name} 获取真实成交记录...")
        
        try:
            export_data = {"data_type": "transactions"}
            
            response = requests.post(f"{self.local_api_url}/export", json=export_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成交记录获取成功!")
                
                data = result.get('data', [])
                if isinstance(data, list) and data:
                    print(f"   - 成交记录: {len(data)}笔")
                    
                    for i, transaction in enumerate(data[-5:]):  # 显示最近5笔
                        if isinstance(transaction, dict):
                            code = transaction.get('证券代码', transaction.get('code', ''))
                            name = transaction.get('证券名称', transaction.get('name', ''))
                            action = transaction.get('买卖标志', transaction.get('action', ''))
                            quantity = transaction.get('成交数量', transaction.get('quantity', 0))
                            price = transaction.get('成交价格', transaction.get('price', 0))
                            print(f"     {i+1}. {action} {code} {name}: {quantity}股 @{price}")
                        else:
                            print(f"     {i+1}. {transaction}")
                else:
                    print("   - 暂无成交记录")
                
                return result
            else:
                error_msg = f"获取成交记录失败: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"获取成交记录异常: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def show_trade_summary(self):
        """显示交易总结"""
        print(f"\n📋 {self.name} 交易总结:")
        print("=" * 50)
        
        if not self.trade_history:
            print("📝 本次会话暂无交易记录")
            return
        
        buy_count = sum(1 for trade in self.trade_history if trade['action'] == 'buy')
        sell_count = sum(1 for trade in self.trade_history if trade['action'] == 'sell')
        
        print(f"📊 本次会话交易统计:")
        print(f"   - 总交易次数: {len(self.trade_history)}")
        print(f"   - 买入次数: {buy_count}")
        print(f"   - 卖出次数: {sell_count}")
        
        print(f"\n📝 交易明细:")
        for i, trade in enumerate(self.trade_history, 1):
            result = trade['result']
            success = "✅" if result.get('success') else "❌"
            print(f"   {i}. {success} {trade['action'].upper()} {trade['stock_code']} {trade['quantity']}股 @{trade['price']}")

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
    
    # 创建真实云端Agent
    agent = RealCloudAgent("真实交易Agent-001")
    
    # 1. 检查本地连接
    print("\n🔍 步骤1: 检查本地连接")
    if not agent.check_local_connection():
        print("\n❌ 本地连接失败,请先启动真实交易系统:")
        print("💡 启动命令: python real_cloud_local_trading_system.py")
        return
    
    # 2. 获取当前真实投资组合
    print("\n📊 步骤2: 获取当前真实投资组合")
    agent.get_real_portfolio()
    
    # 3. 获取真实成交记录
    print("\n📋 步骤3: 获取真实成交记录")
    agent.get_real_transactions()
    
    # 4. 演示真实交易(收盘时间,不会实际成交)
    print("\n💰 步骤4: 演示真实交易指令")
    print("注意: 收盘时间发送的指令不会实际成交")
    
    # 演示买入指令
    print("\n🔵 演示买入指令:")
    agent.execute_real_trade("buy", "000001", 100, "10.50")
    
    time.sleep(2)
    
    # 演示卖出指令
    print("\n🔴 演示卖出指令:")
    agent.execute_real_trade("sell", "000002", 100, "18.60")
    
    # 5. 显示交易总结
    print("\n📋 步骤5: 交易总结")
    agent.show_trade_summary()
    
    print("\n🎉 真实交易演示完成!")
    print("💡 提示: 这个演示展示了云端Agent如何调用本地电脑进行真实交易")
    print("⚠️ 在交易时间内,这些指令会实际执行并影响您的账户")

def test_real_api_endpoints():
    """测试真实API端点"""
    print("🧪 测试真实交易API端点")
    print("=" * 50)
    
    local_api_url = "http://localhost:8889"
    
    # 测试端点列表
    tests = [
        ("GET", "/", "根路径"),
        ("GET", "/status", "状态检查"),
        ("GET", "/health", "健康检查"),
    ]
    
    for method, endpoint, description in tests:
        try:
            print(f"\n📡 测试 {method} {endpoint} ({description})")
            
            if method == "GET":
                response = requests.get(f"{local_api_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功")
                if endpoint == "/status":
                    print(f"   - 交易软件: {data.get('trading_software_active')}")
                    print(f"   - 运行模式: {data.get('mode')}")
                elif endpoint == "/":
                    print(f"   - 服务: {data.get('service')}")
                    print(f"   - 模式: {data.get('mode')}")
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试API端点
        test_real_api_endpoints()
    else:
        # 运行完整演示
        demo_real_cloud_agent_trading()

if __name__ == "__main__":
    main()
