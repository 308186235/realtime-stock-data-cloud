#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端Agent调用本地电脑交易演示
展示云端Agent如何通过API调用本地电脑进行交易
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class CloudAgent:
    """云端Agent"""
    
    def __init__(self, name: str, local_api_url: str = "http://localhost:8888"):
        self.name = name
        self.local_api_url = local_api_url
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
                print(f"   - 运行模式: {data.get('mode')}")
                return True
            else:
                print(f"❌ 本地连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 本地连接异常: {e}")
            return False
    
    def execute_local_trade(self, action: str, stock_code: str, quantity: int, price: float = None) -> Dict[str, Any]:
        """执行本地交易"""
        print(f"\n🤖 {self.name} 执行交易决策:")
        print(f"   - 操作: {action}")
        print(f"   - 股票: {stock_code}")
        print(f"   - 数量: {quantity}")
        print(f"   - 价格: {price or '市价'}")
        
        try:
            trade_data = {
                "action": action,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price
            }
            
            print(f"📤 发送交易指令到本地电脑...")
            response = requests.post(f"{self.local_api_url}/trade", json=trade_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 交易执行成功!")
                print(f"   - 消息: {result.get('message')}")
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
    
    def get_local_portfolio(self) -> Dict[str, Any]:
        """获取本地投资组合"""
        print(f"\n📊 {self.name} 获取投资组合...")
        
        try:
            export_data = {"data_type": "holdings"}
            
            response = requests.post(f"{self.local_api_url}/export", json=export_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 投资组合获取成功!")
                
                data = result.get('data', {})
                holdings = data.get('holdings', [])
                balance = data.get('balance', 0)
                
                print(f"   - 现金余额: ¥{balance:,.2f}")
                print(f"   - 持仓股票: {len(holdings)}只")
                
                for holding in holdings:
                    print(f"     * {holding.get('stock_code')} {holding.get('stock_name')}: {holding.get('quantity')}股 @¥{holding.get('cost_price')}")
                
                return result
            else:
                error_msg = f"获取投资组合失败: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"获取投资组合异常: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def analyze_and_trade(self, market_data: List[Dict[str, Any]]):
        """分析市场数据并执行交易"""
        print(f"\n🧠 {self.name} 开始分析市场数据...")
        
        for stock in market_data:
            stock_code = stock.get('code')
            price = stock.get('price')
            change_percent = stock.get('change_percent')
            volume = stock.get('volume')
            
            print(f"📈 分析 {stock_code}: 价格¥{price}, 涨跌{change_percent:+.2f}%, 成交量{volume:,}")
            
            # 简单的交易策略
            if change_percent > 3.0 and volume > 1000000:
                # 涨幅超过3%且成交量大，买入
                print(f"💡 策略触发: 涨幅{change_percent:.2f}%，成交量{volume:,}，执行买入")
                self.execute_local_trade("buy", stock_code, 100, price)
                
            elif change_percent < -2.0:
                # 跌幅超过2%，卖出
                print(f"💡 策略触发: 跌幅{change_percent:.2f}%，执行卖出")
                self.execute_local_trade("sell", stock_code, 100, price)
                
            else:
                print(f"💤 策略判断: 持有观望")
            
            # 模拟分析间隔
            time.sleep(1)
    
    def show_trade_summary(self):
        """显示交易总结"""
        print(f"\n📋 {self.name} 交易总结:")
        print("=" * 50)
        
        if not self.trade_history:
            print("📝 暂无交易记录")
            return
        
        buy_count = sum(1 for trade in self.trade_history if trade['action'] == 'buy')
        sell_count = sum(1 for trade in self.trade_history if trade['action'] == 'sell')
        
        print(f"📊 交易统计:")
        print(f"   - 总交易次数: {len(self.trade_history)}")
        print(f"   - 买入次数: {buy_count}")
        print(f"   - 卖出次数: {sell_count}")
        
        print(f"\n📝 交易明细:")
        for i, trade in enumerate(self.trade_history, 1):
            result = trade['result']
            success = "✅" if result.get('success') else "❌"
            print(f"   {i}. {success} {trade['action'].upper()} {trade['stock_code']} {trade['quantity']}股 @¥{trade['price'] or '市价'}")

def demo_cloud_agent_trading():
    """演示云端Agent交易"""
    print("🎯 云端Agent调用本地电脑交易演示")
    print("=" * 80)
    
    # 创建云端Agent
    agent = CloudAgent("智能交易Agent-001")
    
    # 1. 检查本地连接
    print("\n🔍 步骤1: 检查本地连接")
    if not agent.check_local_connection():
        print("\n❌ 本地连接失败，请先启动本地API服务器:")
        print("💡 启动命令: python simple_cloud_to_local_solution.py")
        return
    
    # 2. 获取当前投资组合
    print("\n📊 步骤2: 获取当前投资组合")
    agent.get_local_portfolio()
    
    # 3. 模拟市场数据分析和交易
    print("\n🧠 步骤3: 市场数据分析和交易决策")
    
    # 模拟市场数据
    market_data = [
        {"code": "000001", "name": "平安银行", "price": 12.85, "change_percent": 4.2, "volume": 2500000},
        {"code": "000002", "name": "万科A", "price": 18.76, "change_percent": -2.8, "volume": 1800000},
        {"code": "000858", "name": "五粮液", "price": 168.50, "change_percent": 1.5, "volume": 800000},
        {"code": "BJ430001", "name": "北交所测试", "price": 15.20, "change_percent": 5.8, "volume": 1200000}
    ]
    
    # 执行分析和交易
    agent.analyze_and_trade(market_data)
    
    # 4. 获取更新后的投资组合
    print("\n📊 步骤4: 获取更新后的投资组合")
    agent.get_local_portfolio()
    
    # 5. 显示交易总结
    print("\n📋 步骤5: 交易总结")
    agent.show_trade_summary()
    
    print("\n🎉 演示完成!")
    print("💡 提示: 这个演示展示了云端Agent如何通过API调用本地电脑进行交易")

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试本地API端点")
    print("=" * 50)
    
    local_api_url = "http://localhost:8888"
    
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
                print(f"✅ 成功: {data}")
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试API端点
        test_api_endpoints()
    else:
        # 运行完整演示
        demo_cloud_agent_trading()

if __name__ == "__main__":
    main()
