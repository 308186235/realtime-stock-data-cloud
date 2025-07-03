#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整交易系统演示
展示云端Agent调用本地电脑交易的完整流程
"""

import asyncio
import subprocess
import time
import requests
import json
import websockets
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteTradingDemo:
    """完整交易系统演示"""
    
    def __init__(self):
        self.local_api_url = "http://localhost:8888"
        self.websocket_url = "ws://localhost:8888/ws"
        self.local_process = None
        
    async def run_complete_demo(self):
        """运行完整演示"""
        print("🎯 完整云端Agent调用本地电脑交易演示")
        print("=" * 80)
        
        try:
            # 1. 启动本地交易系统
            await self.start_local_system()
            
            # 2. 等待系统启动
            await self.wait_for_system_ready()
            
            # 3. 验证系统连接
            await self.verify_system_connections()
            
            # 4. 演示基础功能
            await self.demo_basic_functions()
            
            # 5. 演示Agent决策
            await self.demo_agent_decisions()
            
            # 6. 演示WebSocket实时通信
            await self.demo_websocket_communication()
            
            # 7. 演示云端Agent自动交易
            await self.demo_cloud_agent_trading()
            
            # 8. 显示系统统计
            await self.show_system_statistics()
            
            print("\n🎉 完整演示成功！")
            
        except Exception as e:
            print(f"❌ 演示失败: {e}")
        finally:
            await self.cleanup()
    
    async def start_local_system(self):
        """启动本地交易系统"""
        print("\n🚀 步骤1: 启动本地交易系统")
        print("-" * 40)
        
        try:
            # 启动本地交易系统
            self.local_process = subprocess.Popen(
                ["python", "complete_cloud_local_trading_system.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("✅ 本地交易系统启动中...")
            
        except Exception as e:
            print(f"❌ 启动本地系统失败: {e}")
            raise
    
    async def wait_for_system_ready(self):
        """等待系统准备就绪"""
        print("\n⏳ 步骤2: 等待系统准备就绪")
        print("-" * 40)
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.local_api_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ 本地交易系统已就绪")
                    return
            except:
                pass
            
            print(f"   等待中... ({attempt + 1}/{max_attempts})")
            await asyncio.sleep(2)
        
        raise Exception("系统启动超时")
    
    async def verify_system_connections(self):
        """验证系统连接"""
        print("\n🔍 步骤3: 验证系统连接")
        print("-" * 40)
        
        # 检查HTTP API
        try:
            response = requests.get(f"{self.local_api_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ HTTP API连接正常")
                print(f"   - 服务运行: {data.get('service_running')}")
                print(f"   - 交易API: {data.get('trader_api_available')}")
                print(f"   - 运行模式: {data.get('mode')}")
            else:
                print(f"❌ HTTP API连接失败: {response.status_code}")
        except Exception as e:
            print(f"❌ HTTP API连接异常: {e}")
        
        # 检查根路径
        try:
            response = requests.get(f"{self.local_api_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ 系统信息获取成功")
                print(f"   - 服务: {data.get('service')}")
                print(f"   - 版本: {data.get('version')}")
                print(f"   - 统计: {data.get('stats')}")
        except Exception as e:
            print(f"❌ 系统信息获取失败: {e}")
    
    async def demo_basic_functions(self):
        """演示基础功能"""
        print("\n💰 步骤4: 演示基础交易功能")
        print("-" * 40)
        
        # 演示交易
        trade_requests = [
            {"action": "buy", "stock_code": "000001", "quantity": 100, "price": 12.5},
            {"action": "sell", "stock_code": "000002", "quantity": 50, "price": 18.6},
            {"action": "buy", "stock_code": "BJ430001", "quantity": 100, "price": 15.2}
        ]
        
        for i, trade in enumerate(trade_requests, 1):
            try:
                print(f"\n📈 交易 {i}: {trade['action'].upper()} {trade['stock_code']} {trade['quantity']}股")
                
                response = requests.post(f"{self.local_api_url}/trade", json=trade, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 交易成功: {result['message']}")
                    print(f"   - 交易ID: {result['trade_id']}")
                else:
                    print(f"❌ 交易失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 交易异常: {e}")
            
            await asyncio.sleep(1)
        
        # 演示数据导出
        print(f"\n📊 数据导出演示:")
        try:
            response = requests.post(f"{self.local_api_url}/export", json={"data_type": "all"}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print("✅ 数据导出成功")
                data = result.get('data', {})
                if 'holdings' in data:
                    print(f"   - 持仓股票: {len(data['holdings'])}只")
                if 'balance' in data:
                    print(f"   - 账户余额: ¥{data['balance']:,.2f}")
            else:
                print(f"❌ 数据导出失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 数据导出异常: {e}")
    
    async def demo_agent_decisions(self):
        """演示Agent决策"""
        print("\n🤖 步骤5: 演示Agent决策处理")
        print("-" * 40)
        
        decisions = [
            {
                "action": "buy",
                "stock_code": "000001",
                "stock_name": "平安银行",
                "quantity": 100,
                "price": 12.8,
                "confidence": 0.85,
                "reason": "技术指标看涨，成交量放大",
                "timestamp": datetime.now().isoformat()
            },
            {
                "action": "sell",
                "stock_code": "000002",
                "stock_name": "万科A",
                "quantity": 50,
                "price": 18.5,
                "confidence": 0.6,
                "reason": "获利了结，风险控制",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        for i, decision in enumerate(decisions, 1):
            try:
                print(f"\n🎯 决策 {i}: {decision['action'].upper()} {decision['stock_code']} (置信度: {decision['confidence']})")
                print(f"   理由: {decision['reason']}")
                
                response = requests.post(f"{self.local_api_url}/agent-decision", json=decision, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 决策处理成功: {result['message']}")
                    if result.get('auto_executed'):
                        print("   🚀 已自动执行交易")
                    else:
                        print("   ⏸️ 需要手动确认")
                else:
                    print(f"❌ 决策处理失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 决策处理异常: {e}")
            
            await asyncio.sleep(1)
    
    async def demo_websocket_communication(self):
        """演示WebSocket实时通信"""
        print("\n🔗 步骤6: 演示WebSocket实时通信")
        print("-" * 40)
        
        try:
            print("📡 连接WebSocket...")
            
            async with websockets.connect(self.websocket_url) as websocket:
                print("✅ WebSocket连接成功")
                
                # 接收几条实时消息
                for i in range(3):
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        
                        print(f"📨 收到实时消息 {i+1}:")
                        print(f"   - 类型: {data.get('type')}")
                        print(f"   - 时间: {data.get('timestamp')}")
                        if 'stats' in data:
                            stats = data['stats']
                            print(f"   - 交易次数: {stats.get('trades_executed')}")
                            print(f"   - 决策次数: {stats.get('decisions_made')}")
                        
                    except asyncio.TimeoutError:
                        print("⏰ WebSocket消息接收超时")
                        break
                    except Exception as e:
                        print(f"❌ WebSocket消息处理失败: {e}")
                        break
                
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
    
    async def demo_cloud_agent_trading(self):
        """演示云端Agent自动交易"""
        print("\n☁️ 步骤7: 演示云端Agent自动交易")
        print("-" * 40)
        
        try:
            print("🤖 启动云端Agent...")
            
            # 启动云端Agent
            agent_process = subprocess.Popen(
                ["python", "complete_cloud_local_trading_system.py", "agent"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("✅ 云端Agent已启动")
            print("⏳ 等待Agent执行决策...")
            
            # 等待Agent执行
            await asyncio.sleep(10)
            
            # 检查Agent执行结果
            try:
                response = requests.get(f"{self.local_api_url}/decisions", timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    decisions = result.get('decisions', [])
                    print(f"📊 Agent执行了 {len(decisions)} 个决策")
                    
                    for decision in decisions[-3:]:  # 显示最近3个决策
                        print(f"   - {decision.get('action', '').upper()} {decision.get('stock_code')} (置信度: {decision.get('confidence')})")
            except Exception as e:
                print(f"⚠️ 获取Agent决策失败: {e}")
            
            # 停止Agent
            agent_process.terminate()
            print("🛑 云端Agent已停止")
            
        except Exception as e:
            print(f"❌ 云端Agent演示失败: {e}")
    
    async def show_system_statistics(self):
        """显示系统统计"""
        print("\n📊 步骤8: 系统统计信息")
        print("-" * 40)
        
        try:
            # 获取交易历史
            response = requests.get(f"{self.local_api_url}/history", timeout=5)
            if response.status_code == 200:
                result = response.json()
                trades = result.get('trades', [])
                print(f"📈 总交易次数: {len(trades)}")
                
                buy_count = sum(1 for trade in trades if trade.get('action') == 'buy')
                sell_count = sum(1 for trade in trades if trade.get('action') == 'sell')
                print(f"   - 买入: {buy_count} 次")
                print(f"   - 卖出: {sell_count} 次")
            
            # 获取决策历史
            response = requests.get(f"{self.local_api_url}/decisions", timeout=5)
            if response.status_code == 200:
                result = response.json()
                decisions = result.get('decisions', [])
                print(f"🤖 总决策次数: {len(decisions)}")
                
                auto_executed = sum(1 for decision in decisions if decision.get('auto_executed'))
                print(f"   - 自动执行: {auto_executed} 次")
                print(f"   - 需要确认: {len(decisions) - auto_executed} 次")
            
            # 获取系统状态
            response = requests.get(f"{self.local_api_url}/", timeout=5)
            if response.status_code == 200:
                result = response.json()
                stats = result.get('stats', {})
                print(f"⚙️ 系统统计:")
                print(f"   - 启动时间: {stats.get('start_time')}")
                print(f"   - 错误次数: {stats.get('errors_count', 0)}")
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        
        if self.local_process:
            self.local_process.terminate()
            print("✅ 本地交易系统已停止")

async def main():
    """主函数"""
    demo = CompleteTradingDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
