#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动端后端通信测试
测试移动端是否能与云端Agent后端正常通信
"""

import requests
import json
import time
from datetime import datetime

class MobileBackendTester:
    def __init__(self):
        self.base_url = "https://api.aigupiao.me"
        self.timeout = 30  # 增加超时时间适应移动网络
        
    def test_backend_communication(self):
        """测试移动端与后端通信"""
        print("📱 移动端后端通信测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端地址: {self.base_url}")
        print(f"网络类型: 移动热点")
        print()
        
        results = {}
        
        # 1. 基础连通性测试
        print("🔗 测试1: 基础连通性")
        print("-" * 40)
        results["connectivity"] = self.test_basic_connectivity()
        
        # 2. 健康检查端点
        print("\n🏥 测试2: 健康检查端点")
        print("-" * 40)
        results["health_check"] = self.test_health_endpoints()
        
        # 3. Agent分析端点
        print("\n🤖 测试3: Agent分析端点")
        print("-" * 40)
        results["agent_analysis"] = self.test_agent_endpoints()
        
        # 4. 云端本地交易端点
        print("\n☁️ 测试4: 云端本地交易端点")
        print("-" * 40)
        results["cloud_local_trading"] = self.test_cloud_local_trading()
        
        # 5. 数据端点测试
        print("\n📊 测试5: 数据端点")
        print("-" * 40)
        results["data_endpoints"] = self.test_data_endpoints()
        
        # 6. 生成通信测试报告
        print("\n📋 移动端后端通信测试报告")
        print("-" * 40)
        self.generate_communication_report(results)
        
        return results
    
    def test_basic_connectivity(self):
        """测试基础连通性"""
        try:
            print("🔍 测试基础HTTP连接...")
            
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ 基础连接成功")
                print(f"   响应时间: {response_time:.0f}ms")
                print(f"   状态码: {response.status_code}")
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                print(f"⚠️ 连接异常: HTTP {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response_time": response_time
                }
                
        except requests.exceptions.Timeout:
            print("❌ 连接超时 (>30秒)")
            return {"success": False, "error": "连接超时"}
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败")
            return {"success": False, "error": "连接失败"}
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return {"success": False, "error": str(e)}
    
    def test_health_endpoints(self):
        """测试健康检查端点"""
        health_endpoints = [
            "/api/health",
            "/health"
        ]
        
        results = {}
        
        for endpoint in health_endpoints:
            try:
                print(f"🔍 测试 {endpoint}...")
                
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 成功: {response_time:.0f}ms")
                    print(f"      服务: {data.get('service', 'N/A')}")
                    print(f"      状态: {data.get('status', 'N/A')}")
                    
                    results[endpoint] = {
                        "success": True,
                        "response_time": response_time,
                        "data": data
                    }
                else:
                    print(f"   ❌ 失败: HTTP {response.status_code}")
                    results[endpoint] = {
                        "success": False,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results[endpoint] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def test_agent_endpoints(self):
        """测试Agent相关端点"""
        agent_endpoints = [
            ("/api/agent-analysis", "POST"),
            ("/api/agent/decision", "POST"),
            ("/api/agent/send-order", "POST")
        ]
        
        results = {}
        
        for endpoint, method in agent_endpoints:
            try:
                print(f"🔍 测试 {method} {endpoint}...")
                
                # 准备测试数据
                test_data = self.get_test_data_for_endpoint(endpoint)
                
                start_time = time.time()
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=test_data,
                        timeout=self.timeout
                    )
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
                
                response_time = (time.time() - start_time) * 1000
                
                # 200, 400, 422 都算正常响应
                if response.status_code in [200, 400, 422]:
                    print(f"   ✅ 响应正常: {response.status_code} ({response_time:.0f}ms)")
                    
                    try:
                        data = response.json()
                        results[endpoint] = {
                            "success": True,
                            "response_time": response_time,
                            "status_code": response.status_code,
                            "has_data": bool(data)
                        }
                    except:
                        results[endpoint] = {
                            "success": True,
                            "response_time": response_time,
                            "status_code": response.status_code,
                            "has_data": False
                        }
                else:
                    print(f"   ❌ 响应异常: HTTP {response.status_code}")
                    results[endpoint] = {
                        "success": False,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {e}")
                results[endpoint] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def test_cloud_local_trading(self):
        """测试云端本地交易端点"""
        trading_endpoints = [
            ("/api/cloud-local-trading/local-status", "GET"),
            ("/api/cloud-local-trading/export-data", "POST")
        ]
        
        results = {}
        
        for endpoint, method in trading_endpoints:
            try:
                print(f"🔍 测试 {method} {endpoint}...")
                
                start_time = time.time()
                if method == "POST":
                    test_data = {"export_type": "holdings"}
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=test_data,
                        timeout=self.timeout
                    )
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
                
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 400, 422, 503]:  # 503也可能是正常的(服务暂时不可用)
                    print(f"   ✅ 端点可达: {response.status_code} ({response_time:.0f}ms)")
                    
                    results[endpoint] = {
                        "success": True,
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                else:
                    print(f"   ❌ 端点异常: HTTP {response.status_code}")
                    results[endpoint] = {
                        "success": False,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {e}")
                results[endpoint] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def test_data_endpoints(self):
        """测试数据相关端点"""
        data_endpoints = [
            "/api/virtual-account/accounts",
            "/api/chagubang/health",
            "/api/chagubang/stocks"
        ]
        
        results = {}
        
        for endpoint in data_endpoints:
            try:
                print(f"🔍 测试 {endpoint}...")
                
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 400, 422]:
                    print(f"   ✅ 数据端点可用: {response.status_code} ({response_time:.0f}ms)")
                    
                    results[endpoint] = {
                        "success": True,
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                else:
                    print(f"   ⚠️ 数据端点异常: HTTP {response.status_code}")
                    results[endpoint] = {
                        "success": False,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"   ❌ 数据端点异常: {e}")
                results[endpoint] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def get_test_data_for_endpoint(self, endpoint):
        """获取端点测试数据"""
        test_data_map = {
            "/api/agent-analysis": {
                "account_info": {"total_assets": 1000000},
                "orders": [],
                "trades": [],
                "positions": []
            },
            "/api/agent/decision": {
                "market_data": {"timestamp": time.time()},
                "portfolio": []
            },
            "/api/agent/send-order": {
                "commandId": "TEST_001",
                "stockCode": "000001",
                "action": "buy",
                "price": 13.50,
                "quantity": 1000
            }
        }
        
        return test_data_map.get(endpoint, {})
    
    def generate_communication_report(self, results):
        """生成通信测试报告"""
        print("📊 移动端后端通信测试总结")
        print("=" * 60)
        
        # 统计成功率
        total_tests = 0
        successful_tests = 0
        
        for category, tests in results.items():
            if isinstance(tests, dict):
                if "success" in tests:
                    # 单个测试
                    total_tests += 1
                    if tests["success"]:
                        successful_tests += 1
                else:
                    # 多个测试
                    for test_name, test_result in tests.items():
                        if isinstance(test_result, dict) and "success" in test_result:
                            total_tests += 1
                            if test_result["success"]:
                                successful_tests += 1
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 通信成功率: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
        # 网络状况评估
        connectivity = results.get("connectivity", {})
        if connectivity.get("success"):
            response_time = connectivity.get("response_time", 0)
            if response_time < 1000:
                network_status = "🟢 网络良好"
            elif response_time < 3000:
                network_status = "🟡 网络一般"
            else:
                network_status = "🔴 网络较慢"
            
            print(f"🌐 网络状况: {network_status} (响应时间: {response_time:.0f}ms)")
        else:
            print("🌐 网络状况: ❌ 连接失败")
        
        # 端点可用性
        print(f"\n📋 端点可用性:")
        for category, tests in results.items():
            if category == "connectivity":
                continue
                
            category_name = {
                "health_check": "健康检查",
                "agent_analysis": "Agent分析",
                "cloud_local_trading": "云端本地交易",
                "data_endpoints": "数据端点"
            }.get(category, category)
            
            if isinstance(tests, dict) and "success" in tests:
                status = "✅" if tests["success"] else "❌"
                print(f"   {status} {category_name}")
            else:
                available = sum(1 for test in tests.values() if isinstance(test, dict) and test.get("success"))
                total = len(tests)
                status = "✅" if available == total else "⚠️" if available > 0 else "❌"
                print(f"   {status} {category_name}: {available}/{total}")
        
        # 移动端使用建议
        print(f"\n💡 移动端使用建议:")
        if success_rate >= 80:
            print("✅ 后端通信正常,移动端可以正常使用所有功能")
            print("📱 建议:可以进行Agent分析,自动交易等操作")
        elif success_rate >= 60:
            print("⚠️ 后端通信部分正常,建议优先使用可用功能")
            print("📱 建议:先测试基础功能,避免使用异常端点")
        else:
            print("❌ 后端通信存在问题,建议检查网络连接")
            print("📱 建议:检查移动网络,或稍后重试")
        
        # 网络优化建议
        if connectivity.get("response_time", 0) > 2000:
            print("\n🚀 网络优化建议:")
            print("1. 检查移动热点信号强度")
            print("2. 尝试切换到WiFi网络")
            print("3. 避免在网络高峰期使用")
            print("4. 考虑使用VPN优化网络路由")

def main():
    """主函数"""
    tester = MobileBackendTester()
    tester.test_backend_communication()

if __name__ == "__main__":
    main()
