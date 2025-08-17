#!/usr/bin/env python3
"""
完整系统最终测试
测试前端-Worker-本地API的完整通信链路
"""

import requests
import json
import time
import asyncio
import websockets

class CompleteSystemTester:
    """完整系统测试器"""
    
    def __init__(self):
        self.worker_url = "https://trading-api.308186235.workers.dev"
        self.local_api_url = "http://localhost:8888"
        self.test_results = {}
        
    def run_complete_test(self):
        """运行完整测试"""
        print("🧪 完整系统最终测试")
        print("=" * 60)
        
        # 1. 测试Worker API
        self._test_worker_api()
        
        # 2. 测试本地API
        self._test_local_api()
        
        # 3. 测试Agent分析功能
        self._test_agent_analysis()
        
        # 4. 测试交易功能
        self._test_trading_functions()
        
        # 5. 测试数据导出
        self._test_data_export()
        
        # 6. 生成测试报告
        self._generate_test_report()
        
    def _test_worker_api(self):
        """测试Worker API"""
        print("\n🔧 测试Worker API...")
        
        tests = [
            ("根路径", "/"),
            ("Agent分析", "/api/agent-analysis"),
            ("账户余额", "/api/account-balance")
        ]
        
        for test_name, endpoint in tests:
            try:
                response = requests.get(f"{self.worker_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {test_name}: 正常")
                    self.test_results[f"worker_{test_name}"] = True
                else:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    self.test_results[f"worker_{test_name}"] = False
            except Exception as e:
                print(f"❌ {test_name}: 连接失败 - {e}")
                self.test_results[f"worker_{test_name}"] = False
    
    def _test_local_api(self):
        """测试本地API"""
        print("\n💰 测试本地API...")
        
        tests = [
            ("健康检查", "/health"),
            ("系统状态", "/status"),
            ("交易状态", "/trading-status")
        ]
        
        for test_name, endpoint in tests:
            try:
                response = requests.get(f"{self.local_api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name}: 正常")
                    self.test_results[f"local_{test_name}"] = True
                else:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    self.test_results[f"local_{test_name}"] = False
            except Exception as e:
                print(f"❌ {test_name}: 连接失败 - {e}")
                self.test_results[f"local_{test_name}"] = False
    
    def _test_agent_analysis(self):
        """测试Agent分析功能"""
        print("\n🤖 测试Agent分析功能...")
        
        try:
            response = requests.get(f"{self.worker_url}/api/agent-analysis", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # 检查数据结构
                if "success" in data and data["success"]:
                    if "data" in data and "recommendations" in data["data"]:
                        print("✅ Agent分析数据结构正确")
                        print(f"   - 推荐数量: {len(data['data']['recommendations'])}")
                        print(f"   - 市场情绪: {data['data'].get('market_sentiment', 'N/A')}")
                        print(f"   - 置信度: {data['data'].get('confidence_score', 'N/A')}")
                        self.test_results["agent_analysis"] = True
                    else:
                        print("❌ Agent分析数据结构不完整")
                        self.test_results["agent_analysis"] = False
                else:
                    print("❌ Agent分析返回失败状态")
                    self.test_results["agent_analysis"] = False
            else:
                print(f"❌ Agent分析HTTP错误: {response.status_code}")
                self.test_results["agent_analysis"] = False
                
        except Exception as e:
            print(f"❌ Agent分析测试失败: {e}")
            self.test_results["agent_analysis"] = False
    
    def _test_trading_functions(self):
        """测试交易功能"""
        print("\n💼 测试交易功能...")
        
        # 测试本地交易API
        try:
            # 测试买入接口
            buy_data = {
                "code": "000001",
                "quantity": 100,
                "price": "10.50"
            }
            response = requests.post(f"{self.local_api_url}/buy", 
                                   json=buy_data, timeout=5)
            if response.status_code == 200:
                print("✅ 买入接口: 正常")
                self.test_results["trading_buy"] = True
            else:
                print(f"❌ 买入接口: HTTP {response.status_code}")
                self.test_results["trading_buy"] = False
                
        except Exception as e:
            print(f"❌ 买入接口测试失败: {e}")
            self.test_results["trading_buy"] = False
        
        # 测试卖出接口
        try:
            sell_data = {
                "code": "000001",
                "quantity": 100,
                "price": "10.60"
            }
            response = requests.post(f"{self.local_api_url}/sell", 
                                   json=sell_data, timeout=5)
            if response.status_code == 200:
                print("✅ 卖出接口: 正常")
                self.test_results["trading_sell"] = True
            else:
                print(f"❌ 卖出接口: HTTP {response.status_code}")
                self.test_results["trading_sell"] = False
                
        except Exception as e:
            print(f"❌ 卖出接口测试失败: {e}")
            self.test_results["trading_sell"] = False
    
    def _test_data_export(self):
        """测试数据导出"""
        print("\n📊 测试数据导出...")
        
        export_types = ["holdings", "transactions", "orders"]
        
        for export_type in export_types:
            try:
                response = requests.post(f"{self.local_api_url}/export", 
                                       json={"type": export_type}, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {export_type}导出: 正常")
                    self.test_results[f"export_{export_type}"] = True
                else:
                    print(f"❌ {export_type}导出: HTTP {response.status_code}")
                    self.test_results[f"export_{export_type}"] = False
                    
            except Exception as e:
                print(f"❌ {export_type}导出测试失败: {e}")
                self.test_results[f"export_{export_type}"] = False
    
    def _generate_test_report(self):
        """生成测试报告"""
        print("\n📋 测试报告")
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
        
        # 系统状态评估
        print(f"\n🎯 系统状态评估:")
        
        worker_tests = [k for k in self.test_results.keys() if k.startswith("worker_")]
        worker_passed = sum(self.test_results[k] for k in worker_tests)
        
        local_tests = [k for k in self.test_results.keys() if k.startswith("local_")]
        local_passed = sum(self.test_results[k] for k in local_tests)
        
        if worker_passed == len(worker_tests):
            print("   🔧 Worker API: ✅ 完全正常")
        elif worker_passed > 0:
            print("   🔧 Worker API: ⚠️ 部分正常")
        else:
            print("   🔧 Worker API: ❌ 完全异常")
        
        if local_passed == len(local_tests):
            print("   💰 本地API: ✅ 完全正常")
        elif local_passed > 0:
            print("   💰 本地API: ⚠️ 部分正常")
        else:
            print("   💰 本地API: ❌ 完全异常")
        
        if self.test_results.get("agent_analysis", False):
            print("   🤖 Agent分析: ✅ 正常")
        else:
            print("   🤖 Agent分析: ❌ 异常")
        
        # 整体评估
        if passed_tests >= total_tests * 0.8:
            print(f"\n🎉 系统整体状态: ✅ 良好")
            print("   系统基本功能正常,可以开始使用")
        elif passed_tests >= total_tests * 0.5:
            print(f"\n⚠️ 系统整体状态: ⚠️ 一般")
            print("   部分功能正常,需要修复失败的组件")
        else:
            print(f"\n❌ 系统整体状态: ❌ 异常")
            print("   系统存在严重问题,需要全面检查")

if __name__ == "__main__":
    tester = CompleteSystemTester()
    tester.run_complete_test()
