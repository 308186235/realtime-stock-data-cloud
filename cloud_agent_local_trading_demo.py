#!/usr/bin/env python3
"""
云端Agent调用本地交易演示
展示云端Agent如何通过API调用本地working-trader-FIXED模块
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

class CloudAgent:
    """云端Agent演示类"""
    
    def __init__(self, name="CloudTradingAgent"):
        self.name = name
        self.cloud_api_url = "https://api.aigupiao.me/api/cloud-local-trading"
        self.local_api_url = "http://localhost:8888"  # 本地服务器地址
        self.decision_history = []
        
    def analyze_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场数据 - 只接受真实数据"""
        print(f"🤖 {self.name} 正在分析真实市场数据...")

        # 验证输入数据真实性
        if not market_data:
            raise ValueError("❌ 市场数据为空，需要真实数据")

        # 检查必要字段
        required_fields = ['code', 'price', 'change_pct', 'volume', 'timestamp']
        for field in required_fields:
            if field not in market_data:
                raise ValueError(f"❌ 缺少必要字段: {field}，需要完整的真实市场数据")

        # 检查数据源
        if market_data.get('data_source') == 'mock':
            raise ValueError("❌ 检测到模拟数据，Agent拒绝分析")

        # 提取真实数据
        stock_code = market_data["code"]
        current_price = float(market_data["price"])
        change_pct = float(market_data["change_pct"])
        volume = int(market_data["volume"])
        
        # 简单的交易策略
        decision = {
            "should_trade": False,
            "action": None,
            "stock_code": stock_code,
            "quantity": 100,
            "price": None,
            "reason": "无交易信号"
        }
        
        # 策略1: 跌超5%买入
        if change_pct < -5:
            decision.update({
                "should_trade": True,
                "action": "buy",
                "price": current_price * 0.99,  # 稍低于当前价格
                "reason": f"跌幅{change_pct:.2f}%，触发买入信号"
            })
        
        # 策略2: 涨超10%卖出
        elif change_pct > 10:
            decision.update({
                "should_trade": True,
                "action": "sell",
                "price": current_price * 1.01,  # 稍高于当前价格
                "reason": f"涨幅{change_pct:.2f}%，触发卖出信号"
            })
        
        # 策略3: 成交量异常
        elif volume > 5000000:  # 成交量超过500万
            decision.update({
                "should_trade": True,
                "action": "buy",
                "quantity": 200,  # 增加数量
                "price": current_price,
                "reason": f"成交量异常({volume:,})，可能有利好消息"
            })
        
        print(f"📊 分析结果: {decision['reason']}")
        return decision
    
    def execute_local_trade_via_cloud_api(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """通过云端API执行本地交易"""
        try:
            print(f"☁️ 通过云端API发送交易指令...")
            
            trade_data = {
                "action": decision["action"],
                "stock_code": decision["stock_code"],
                "quantity": decision["quantity"],
                "price": decision["price"],
                "agent_id": self.name
            }
            
            response = requests.post(
                f"{self.cloud_api_url}/execute-trade",
                json=trade_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 云端API响应: {result.get('message', '成功')}")
                return result
            else:
                error_msg = f"云端API错误: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"云端API调用失败: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def execute_local_trade_direct(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """直接调用本地API执行交易"""
        try:
            print(f"🖥️ 直接调用本地API执行交易...")
            
            trade_data = {
                "action": decision["action"],
                "stock_code": decision["stock_code"],
                "quantity": decision["quantity"],
                "price": decision["price"]
            }
            
            response = requests.post(
                f"{self.local_api_url}/trade",
                json=trade_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 本地API响应: {result.get('message', '成功')}")
                return result
            else:
                error_msg = f"本地API错误: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"本地API调用失败: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def export_local_data(self, data_type: str = "all") -> Dict[str, Any]:
        """导出本地数据"""
        try:
            print(f"📊 导出本地数据: {data_type}")
            
            # 优先使用云端API
            try:
                export_data = {
                    "data_type": data_type,
                    "agent_id": self.name
                }
                
                response = requests.post(
                    f"{self.cloud_api_url}/export-data",
                    json=export_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 云端API导出成功")
                    return result
                else:
                    print(f"⚠️ 云端API导出失败，尝试本地API...")
                    raise Exception("云端API失败")
                    
            except:
                # 备用：直接调用本地API
                export_data = {"data_type": data_type}
                
                response = requests.post(
                    f"{self.local_api_url}/export",
                    json=export_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 本地API导出成功")
                    return result
                else:
                    raise Exception(f"本地API错误: HTTP {response.status_code}")
                    
        except Exception as e:
            error_msg = f"数据导出失败: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def get_local_status(self) -> Dict[str, Any]:
        """获取本地状态"""
        try:
            # 优先使用云端API
            try:
                response = requests.get(f"{self.cloud_api_url}/local-status", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 通过云端API获取本地状态成功")
                    return result
                else:
                    raise Exception("云端API失败")
            except:
                # 备用：直接调用本地API
                response = requests.get(f"{self.local_api_url}/status", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 直接获取本地状态成功")
                    return result
                else:
                    raise Exception(f"本地API错误: HTTP {response.status_code}")
                    
        except Exception as e:
            error_msg = f"获取本地状态失败: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    def make_trading_decision_and_execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """制定交易决策并执行"""
        print(f"\n🤖 {self.name} 开始决策流程...")
        print("=" * 50)
        
        # 1. 分析市场数据
        decision = self.analyze_market_data(market_data)
        
        # 2. 记录决策
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "market_data": market_data,
            "decision": decision,
            "execution_result": None
        }
        
        # 3. 如果需要交易，执行交易
        if decision.get("should_trade", False):
            print(f"\n💰 执行交易决策...")
            
            # 优先使用云端API，备用本地API
            execution_result = self.execute_local_trade_via_cloud_api(decision)
            
            if not execution_result.get("success", False):
                print(f"⚠️ 云端API失败，尝试本地API...")
                execution_result = self.execute_local_trade_direct(decision)
            
            decision_record["execution_result"] = execution_result
            
            if execution_result.get("success", False):
                print(f"✅ 交易执行成功: {decision['action']} {decision['stock_code']}")
            else:
                print(f"❌ 交易执行失败: {execution_result.get('message', '未知错误')}")
        else:
            print(f"📊 无交易信号，继续观察")
        
        # 4. 记录决策历史
        self.decision_history.append(decision_record)
        
        return decision_record

def demo_cloud_agent_trading():
    """演示云端Agent交易"""
    print("🎭 云端Agent本地交易演示")
    print("=" * 60)
    
    # 创建Agent
    agent = CloudAgent("DemoTradingAgent")
    
    # 检查本地状态
    print("\n📊 检查本地交易系统状态...")
    status = agent.get_local_status()
    if status.get("success", False):
        local_status = status.get("local_status", {})
        print(f"✅ 本地系统状态:")
        print(f"   交易软件激活: {local_status.get('trading_software_active', False)}")
        print(f"   当前窗口: {local_status.get('current_window', 'N/A')}")
    else:
        print(f"❌ 本地系统状态检查失败: {status.get('message', '未知错误')}")
    
    # ❌ 演示已禁用 - 不允许使用模拟市场数据
    print("❌ 演示功能已禁用")
    print("原因: 系统禁止使用任何模拟市场数据")
    print()
    print("请配置真实数据源后重新运行:")
    print("1. 淘宝股票数据推送服务 (API_KEY: QT_wat5QfcJ6N9pDZM5)")
    print("2. 同花顺实时数据API")
    print("3. 通达信数据接口")
    print()
    print("系统只接受真实市场数据进行Agent决策！")
    return

if __name__ == "__main__":
    demo_cloud_agent_trading()
