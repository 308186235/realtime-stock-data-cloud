#!/usr/bin/env python3
"""
最终完整系统测试
测试本地Agent后端 + 本地交易API的完整解决方案
"""

import requests
import json
import time

class FinalSystemTester:
    """最终系统测试器"""
    
    def __init__(self):
        self.agent_backend_url = "http://localhost:9999"
        self.trading_api_url = "http://localhost:8888"
        self.test_results = {}
        
    def run_final_test(self):
        """运行最终测试"""
        print("🎯 最终完整系统测试")
        print("=" * 60)
        print("🤖 Agent后端: http://localhost:9999")
        print("💰 交易API: http://localhost:8888")
        print("=" * 60)
        
        # 1. 测试本地Agent后端
        self._test_agent_backend()
        
        # 2. 测试本地交易API
        self._test_trading_api()
        
        # 3. 测试完整工作流
        self._test_complete_workflow()
        
        # 4. 生成最终报告
        self._generate_final_report()
        
    def _test_agent_backend(self):
        """测试本地Agent后端"""
        print("\n🤖 测试本地Agent后端...")
        
        tests = [
            ("根路径", "/"),
            ("健康检查", "/health"),
            ("Agent分析", "/api/agent-analysis"),
            ("账户余额", "/api/account-balance"),
            ("市场数据", "/api/market-data")
        ]
        
        for test_name, endpoint in tests:
            try:
                response = requests.get(f"{self.agent_backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {test_name}: 正常")
                    if "success" in data and data["success"]:
                        print(f"   📊 数据完整性: ✅")
                    self.test_results[f"agent_{test_name}"] = True
                else:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    self.test_results[f"agent_{test_name}"] = False
            except Exception as e:
                print(f"❌ {test_name}: 连接失败 - {e}")
                self.test_results[f"agent_{test_name}"] = False
    
    def _test_trading_api(self):
        """测试本地交易API"""
        print("\n💰 测试本地交易API...")
        
        # 基础测试
        basic_tests = [
            ("健康检查", "/health"),
            ("系统状态", "/status"),
            ("交易状态", "/trading-status")
        ]
        
        for test_name, endpoint in basic_tests:
            try:
                response = requests.get(f"{self.trading_api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name}: 正常")
                    self.test_results[f"trading_{test_name}"] = True
                else:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    self.test_results[f"trading_{test_name}"] = False
            except Exception as e:
                print(f"❌ {test_name}: 连接失败 - {e}")
                self.test_results[f"trading_{test_name}"] = False
        
        # 交易功能测试
        print("\n   💼 测试交易功能...")
        
        # 测试买入
        try:
            buy_data = {"code": "000001", "quantity": 100, "price": "10.50"}
            response = requests.post(f"{self.trading_api_url}/buy", 
                                   json=buy_data, timeout=5)
            if response.status_code == 200:
                print("   ✅ 买入接口: 正常")
                self.test_results["trading_buy"] = True
            else:
                print(f"   ❌ 买入接口: HTTP {response.status_code}")
                self.test_results["trading_buy"] = False
        except Exception as e:
            print(f"   ❌ 买入接口: {e}")
            self.test_results["trading_buy"] = False
        
        # 测试卖出
        try:
            sell_data = {"code": "000001", "quantity": 100, "price": "10.60"}
            response = requests.post(f"{self.trading_api_url}/sell", 
                                   json=sell_data, timeout=5)
            if response.status_code == 200:
                print("   ✅ 卖出接口: 正常")
                self.test_results["trading_sell"] = True
            else:
                print(f"   ❌ 卖出接口: HTTP {response.status_code}")
                self.test_results["trading_sell"] = False
        except Exception as e:
            print(f"   ❌ 卖出接口: {e}")
            self.test_results["trading_sell"] = False
    
    def _test_complete_workflow(self):
        """测试完整工作流"""
        print("\n🔄 测试完整工作流...")
        
        try:
            # 1. 获取Agent分析
            print("   1️⃣ 获取Agent分析...")
            response = requests.get(f"{self.agent_backend_url}/api/agent-analysis", timeout=5)
            if response.status_code == 200:
                analysis_data = response.json()
                if analysis_data.get("success") and "recommendations" in analysis_data.get("data", {}):
                    recommendations = analysis_data["data"]["recommendations"]
                    print(f"   ✅ 获取到 {len(recommendations)} 个推荐")
                    
                    # 2. 根据推荐执行交易
                    print("   2️⃣ 根据推荐执行模拟交易...")
                    for rec in recommendations[:1]:  # 只测试第一个推荐
                        if rec["action"] == "buy":
                            trade_data = {
                                "code": rec["stock_code"],
                                "quantity": 100,
                                "price": str(rec["current_price"])
                            }
                            trade_response = requests.post(f"{self.trading_api_url}/buy", 
                                                         json=trade_data, timeout=5)
                            if trade_response.status_code == 200:
                                print(f"   ✅ 执行买入 {rec['stock_code']}: 成功")
                            else:
                                print(f"   ❌ 执行买入 {rec['stock_code']}: 失败")
                    
                    self.test_results["workflow_complete"] = True
                else:
                    print("   ❌ Agent分析数据格式错误")
                    self.test_results["workflow_complete"] = False
            else:
                print("   ❌ 获取Agent分析失败")
                self.test_results["workflow_complete"] = False
                
        except Exception as e:
            print(f"   ❌ 完整工作流测试失败: {e}")
            self.test_results["workflow_complete"] = False
    
    def _generate_final_report(self):
        """生成最终报告"""
        print("\n📋 最终测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数: {passed_tests}")
        print(f"   失败数: {total_tests - passed_tests}")
        print(f"   通过率: {passed_tests/total_tests*100:.1f}%")
        
        print(f"\n📝 详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        # 系统组件状态
        print(f"\n🎯 系统组件状态:")
        
        agent_tests = [k for k in self.test_results.keys() if k.startswith("agent_")]
        agent_passed = sum(self.test_results[k] for k in agent_tests)
        
        trading_tests = [k for k in self.test_results.keys() if k.startswith("trading_")]
        trading_passed = sum(self.test_results[k] for k in trading_tests)
        
        if agent_passed == len(agent_tests):
            print("   🤖 Agent后端: ✅ 完全正常")
        elif agent_passed > 0:
            print("   🤖 Agent后端: ⚠️ 部分正常")
        else:
            print("   🤖 Agent后端: ❌ 完全异常")
        
        if trading_passed == len(trading_tests):
            print("   💰 交易API: ✅ 完全正常")
        elif trading_passed > 0:
            print("   💰 交易API: ⚠️ 部分正常")
        else:
            print("   💰 交易API: ❌ 完全异常")
        
        if self.test_results.get("workflow_complete", False):
            print("   🔄 完整工作流: ✅ 正常")
        else:
            print("   🔄 完整工作流: ❌ 异常")
        
        # 最终评估
        if passed_tests >= total_tests * 0.9:
            print(f"\n🎉 系统状态: ✅ 优秀")
            print("   所有核心功能正常,系统可以投入使用!")
        elif passed_tests >= total_tests * 0.7:
            print(f"\n👍 系统状态: ✅ 良好")
            print("   主要功能正常,可以开始使用")
        elif passed_tests >= total_tests * 0.5:
            print(f"\n⚠️ 系统状态: ⚠️ 一般")
            print("   部分功能正常,需要修复失败的组件")
        else:
            print(f"\n❌ 系统状态: ❌ 异常")
            print("   系统存在严重问题,需要全面检查")
        
        print(f"\n🚀 下一步操作:")
        print("   1. 打开前端页面测试Agent分析控制台")
        print("   2. 验证前端与后端的通信")
        print("   3. 测试完整的交易工作流")
        print("   4. 根据需要调整Agent分析算法")

if __name__ == "__main__":
    tester = FinalSystemTester()
    tester.run_final_test()
