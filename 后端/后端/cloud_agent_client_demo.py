#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端Agent客户端演示
展示如何远程调用交易API
"""

import requests
import json
import time
from datetime import datetime

class CloudAgentClient:
    """云端Agent客户端"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CloudAgentClient/1.0'
        })
    
    def get_api_status(self):
        """获取API状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def get_account_balance(self):
        """获取账户余额"""
        try:
            response = self.session.get(f"{self.base_url}/api/balance")
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def export_data(self, data_type):
        """导出数据"""
        try:
            response = self.session.post(f"{self.base_url}/api/export/{data_type}")
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def place_buy_order(self, stock_code, price, quantity, confirm=False):
        """下买单"""
        try:
            data = {
                "stock_code": stock_code,
                "price": price,
                "quantity": quantity,
                "confirm": confirm
            }
            response = self.session.post(f"{self.base_url}/api/trading/buy", json=data)
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def place_sell_order(self, stock_code, price, quantity, confirm=False):
        """下卖单"""
        try:
            data = {
                "stock_code": stock_code,
                "price": price,
                "quantity": quantity,
                "confirm": confirm
            }
            response = self.session.post(f"{self.base_url}/api/trading/sell", json=data)
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def cancel_order(self, order_id):
        """撤单"""
        try:
            data = {"order_id": order_id}
            response = self.session.post(f"{self.base_url}/api/trading/cancel", json=data)
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def start_monitoring(self):
        """启动监控"""
        try:
            response = self.session.post(f"{self.base_url}/api/monitoring/start")
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def stop_monitoring(self):
        """停止监控"""
        try:
            response = self.session.post(f"{self.base_url}/api/monitoring/stop")
            return response.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

def demo_cloud_agent_client():
    """演示云端Agent客户端"""
    print("🌐 云端Agent客户端演示")
    print("=" * 60)
    
    # 创建客户端
    client = CloudAgentClient()
    
    # 1. 检查API状态
    print("1️⃣ 检查API状态...")
    status = client.get_api_status()
    if "error" not in status:
        print(f"✅ API状态正常,版本: {status.get('api_status', {}).get('version', 'Unknown')}")
        connection_status = status.get('trading_system', {}).get('connection_status', {}).get('connection', {}).get('status', 'Unknown')
        print(f"📊 交易系统连接状态: {connection_status}")
    else:
        print(f"❌ API状态检查失败: {status['error']}")
        return
    
    # 2. 获取账户余额
    print("\n2️⃣ 获取账户余额...")
    balance = client.get_account_balance()
    if "error" not in balance and balance.get('success'):
        cash = balance['data']['available_cash']
        total = balance['data']['total_assets']
        print(f"✅ 余额获取成功:")
        print(f"   💰 可用资金: {cash:,.2f}元")
        print(f"   📈 总资产: {total:,.2f}元")
        
        reconnected = balance.get('connection_info', {}).get('reconnected', False)
        if reconnected:
            print("   🔄 过程中执行了自动重连")
    else:
        print(f"❌ 余额获取失败: {balance.get('message', balance.get('error'))}")
    
    # 3. 导出持仓数据
    print("\n3️⃣ 导出持仓数据...")
    holdings = client.export_data('holdings')
    if "error" not in holdings and holdings.get('success'):
        filename = holdings.get('filename', 'Unknown')
        print(f"✅ 持仓数据导出成功: {filename}")
        
        reconnected = holdings.get('connection_info', {}).get('reconnected', False)
        if reconnected:
            print("   🔄 过程中执行了自动重连")
    else:
        print(f"❌ 持仓数据导出失败: {holdings.get('message', holdings.get('error'))}")
    
    # 4. 演示买入操作(不确认提交)
    print("\n4️⃣ 演示买入操作(模拟,不提交)...")
    buy_result = client.place_buy_order("000001", 10.50, 100, confirm=False)
    if "error" not in buy_result and buy_result.get('success'):
        order_data = buy_result['data']
        print(f"✅ 买入信息已填入:")
        print(f"   📋 订单ID: {order_data['order_id']}")
        print(f"   🏷️ 股票代码: {order_data['stock_code']}")
        print(f"   💰 价格: {order_data['price']}元")
        print(f"   📊 数量: {order_data['quantity']}股")
        print(f"   💵 总金额: {order_data['total_amount']}元")
        print(f"   📈 状态: {order_data['status']}")
        print(f"   💬 消息: {order_data['message']}")
    else:
        print(f"❌ 买入操作失败: {buy_result.get('message', buy_result.get('error'))}")
    
    # 5. 演示卖出操作(不确认提交)
    print("\n5️⃣ 演示卖出操作(模拟,不提交)...")
    sell_result = client.place_sell_order("000001", 10.80, 100, confirm=False)
    if "error" not in sell_result and sell_result.get('success'):
        order_data = sell_result['data']
        print(f"✅ 卖出信息已填入:")
        print(f"   📋 订单ID: {order_data['order_id']}")
        print(f"   🏷️ 股票代码: {order_data['stock_code']}")
        print(f"   💰 价格: {order_data['price']}元")
        print(f"   📊 数量: {order_data['quantity']}股")
        print(f"   💵 总金额: {order_data['total_amount']}元")
        print(f"   📈 状态: {order_data['status']}")
        print(f"   💬 消息: {order_data['message']}")
    else:
        print(f"❌ 卖出操作失败: {sell_result.get('message', sell_result.get('error'))}")
    
    # 6. 演示撤单操作
    print("\n6️⃣ 演示撤单操作...")
    cancel_result = client.cancel_order("TEST_ORDER_123")
    if "error" not in cancel_result and cancel_result.get('success'):
        order_data = cancel_result['data']
        print(f"✅ 撤单操作成功:")
        print(f"   📋 订单ID: {order_data['order_id']}")
        print(f"   📈 状态: {order_data['status']}")
        print(f"   💬 消息: {order_data['message']}")
    else:
        print(f"❌ 撤单操作失败: {cancel_result.get('message', cancel_result.get('error'))}")
    
    print("\n🎉 云端Agent客户端演示完成!")

def demo_trading_workflow():
    """演示完整的交易流程"""
    print("🚀 演示完整的云端交易流程")
    print("=" * 60)
    
    client = CloudAgentClient()
    
    # 交易流程
    workflow_steps = [
        ("检查系统状态", lambda: client.get_api_status()),
        ("获取账户余额", lambda: client.get_account_balance()),
        ("导出持仓数据", lambda: client.export_data('holdings')),
        ("导出委托数据", lambda: client.export_data('orders')),
        ("导出成交数据", lambda: client.export_data('transactions')),
    ]
    
    print("📋 执行交易流程:")
    for i, (step_name, step_func) in enumerate(workflow_steps, 1):
        print(f"\n{i}️⃣ {step_name}...")
        
        try:
            result = step_func()
            if "error" not in result:
                if result.get('success', True):
                    print(f"   ✅ {step_name}成功")
                else:
                    print(f"   ❌ {step_name}失败: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ {step_name}失败: {result['error']}")
        except Exception as e:
            print(f"   ❌ {step_name}异常: {str(e)}")
        
        time.sleep(1)  # 避免请求过快
    
    print("\n🎯 交易流程演示完成!")

def interactive_trading_demo():
    """交互式交易演示"""
    print("🎮 交互式云端交易演示")
    print("=" * 60)
    
    client = CloudAgentClient()
    
    while True:
        print("\n📋 可用操作:")
        print("1. 检查API状态")
        print("2. 获取账户余额")
        print("3. 导出持仓数据")
        print("4. 导出委托数据")
        print("5. 导出成交数据")
        print("6. 买入股票(模拟)")
        print("7. 卖出股票(模拟)")
        print("8. 撤单")
        print("9. 启动监控")
        print("10. 停止监控")
        print("0. 退出")
        
        try:
            choice = input("\n请选择操作 (0-10): ").strip()
            
            if choice == "0":
                print("👋 退出演示")
                break
            elif choice == "1":
                result = client.get_api_status()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "2":
                result = client.get_account_balance()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "3":
                result = client.export_data('holdings')
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "4":
                result = client.export_data('orders')
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "5":
                result = client.export_data('transactions')
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "6":
                stock_code = input("股票代码: ").strip()
                price = float(input("买入价格: ").strip())
                quantity = int(input("买入数量: ").strip())
                result = client.place_buy_order(stock_code, price, quantity, confirm=False)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "7":
                stock_code = input("股票代码: ").strip()
                price = float(input("卖出价格: ").strip())
                quantity = int(input("卖出数量: ").strip())
                result = client.place_sell_order(stock_code, price, quantity, confirm=False)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "8":
                order_id = input("订单ID: ").strip()
                result = client.cancel_order(order_id)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "9":
                result = client.start_monitoring()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "10":
                result = client.stop_monitoring()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("❌ 无效选择,请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断")
            break
        except Exception as e:
            print(f"❌ 操作异常: {str(e)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'workflow':
            demo_trading_workflow()
        elif sys.argv[1] == 'interactive':
            interactive_trading_demo()
        else:
            demo_cloud_agent_client()
    else:
        demo_cloud_agent_client()
