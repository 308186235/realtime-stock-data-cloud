#!/usr/bin/env python3
"""
前端后端通信测试工具
测试前端与后端的完整通信流程
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

class FrontendBackendTester:
    """前端后端通信测试器"""
    
    def __init__(self):
        self.api_base_url = "https://api.aigupiao.me"
        self.frontend_urls = [
            "https://app.aigupiao.me",
            "https://mobile.aigupiao.me", 
            "https://admin.aigupiao.me"
        ]
        self.test_results = []
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 前端后端通信综合测试")
        print("=" * 60)
        
        try:
            # 1. 测试后端API可用性
            self._test_backend_api()
            
            # 2. 测试CORS配置
            self._test_cors_configuration()
            
            # 3. 测试API端点
            self._test_api_endpoints()
            
            # 4. 测试WebSocket连接
            self._test_websocket_connection()
            
            # 5. 测试前端页面访问
            self._test_frontend_pages()
            
            # 6. 生成测试报告
            self._generate_test_report()
            
        except Exception as e:
            print(f"❌ 测试过程异常: {e}")
            self._add_test_result("综合测试", False, f"测试异常: {e}")
    
    def _add_test_result(self, test_name: str, success: bool, message: str):
        """添加测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {message}")
    
    def _test_backend_api(self):
        """测试后端API可用性"""
        print("\n🔧 测试后端API可用性...")
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            
            if response.status_code == 200:
                self._add_test_result(
                    "后端API健康检查", True,
                    f"API正常响应 (状态码: {response.status_code})"
                )
            else:
                self._add_test_result(
                    "后端API健康检查", False,
                    f"API响应异常 (状态码: {response.status_code})"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "后端API健康检查", False,
                f"API连接失败: {e}"
            )
    
    def _test_cors_configuration(self):
        """测试CORS配置"""
        print("\n🌐 测试CORS配置...")
        
        for frontend_url in self.frontend_urls:
            try:
                headers = {
                    'Origin': frontend_url,
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
                
                response = requests.options(
                    f"{self.api_base_url}/api/health",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    # 检查CORS头
                    cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
                    if '*' in cors_headers or frontend_url in cors_headers:
                        self._add_test_result(
                            f"CORS配置 ({frontend_url})", True,
                            "CORS配置正确"
                        )
                    else:
                        self._add_test_result(
                            f"CORS配置 ({frontend_url})", False,
                            f"CORS头不正确: {cors_headers}"
                        )
                else:
                    self._add_test_result(
                        f"CORS配置 ({frontend_url})", False,
                        f"CORS预检失败 (状态码: {response.status_code})"
                    )
            
            except requests.exceptions.RequestException as e:
                self._add_test_result(
                    f"CORS配置 ({frontend_url})", False,
                    f"CORS测试失败: {e}"
                )
    
    def _test_api_endpoints(self):
        """测试API端点"""
        print("\n🔌 测试API端点...")
        
        # 测试主要API端点
        endpoints = [
            ("/api/health", "健康检查"),
            ("/api/market/status", "市场状态"),
            ("/api/agent/status", "Agent状态"),
            ("/api/trading/status", "交易状态"),
            ("/api/data/status", "数据状态")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"{self.api_base_url}{endpoint}",
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    # 检查响应是否包含模拟数据
                    response_text = response.text.lower()
                    if any(word in response_text for word in ['mock', 'fake', 'test', 'demo']):
                        self._add_test_result(
                            f"API端点 {endpoint}", False,
                            "⚠️ 响应包含模拟数据标识"
                        )
                    else:
                        self._add_test_result(
                            f"API端点 {endpoint}", True,
                            f"{description}正常"
                        )
                elif response.status_code == 404:
                    self._add_test_result(
                        f"API端点 {endpoint}", False,
                        "端点不存在"
                    )
                else:
                    self._add_test_result(
                        f"API端点 {endpoint}", False,
                        f"响应异常 (状态码: {response.status_code})"
                    )
            
            except requests.exceptions.RequestException as e:
                self._add_test_result(
                    f"API端点 {endpoint}", False,
                    f"请求失败: {e}"
                )
    
    def _test_websocket_connection(self):
        """测试WebSocket连接"""
        print("\n🔗 测试WebSocket连接...")
        
        try:
            # 简单的WebSocket连接测试
            import websocket
            
            def on_open(ws):
                self._add_test_result(
                    "WebSocket连接", True,
                    "WebSocket连接成功"
                )
                ws.close()
            
            def on_error(ws, error):
                self._add_test_result(
                    "WebSocket连接", False,
                    f"WebSocket连接失败: {error}"
                )
            
            ws = websocket.WebSocketApp(
                "wss://api.aigupiao.me/ws",
                on_open=on_open,
                on_error=on_error
            )
            
            # 设置超时
            ws.run_forever(timeout=5)
            
        except ImportError:
            self._add_test_result(
                "WebSocket连接", False,
                "websocket-client未安装，跳过WebSocket测试"
            )
        except Exception as e:
            self._add_test_result(
                "WebSocket连接", False,
                f"WebSocket测试异常: {e}"
            )
    
    def _test_frontend_pages(self):
        """测试前端页面访问"""
        print("\n🌍 测试前端页面访问...")
        
        for frontend_url in self.frontend_urls:
            try:
                response = requests.get(frontend_url, timeout=10)
                
                if response.status_code == 200:
                    # 检查页面内容
                    content = response.text.lower()
                    
                    # 检查是否包含正确的API配置
                    if 'api.aigupiao.me' in content:
                        self._add_test_result(
                            f"前端页面 ({frontend_url})", True,
                            "页面正常，API配置正确"
                        )
                    else:
                        self._add_test_result(
                            f"前端页面 ({frontend_url})", False,
                            "页面加载但API配置可能不正确"
                        )
                else:
                    self._add_test_result(
                        f"前端页面 ({frontend_url})", False,
                        f"页面访问失败 (状态码: {response.status_code})"
                    )
            
            except requests.exceptions.RequestException as e:
                self._add_test_result(
                    f"前端页面 ({frontend_url})", False,
                    f"页面访问异常: {e}"
                )
    
    def _generate_test_report(self):
        """生成测试报告"""
        print("\n📋 生成测试报告...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "前端后端通信测试",
            "configuration": {
                "api_base_url": self.api_base_url,
                "frontend_urls": self.frontend_urls
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # 保存报告
        report_file = f"frontend_backend_test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 显示摘要
        print(f"\n📊 测试摘要:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {success_rate:.1f}%")
        
        # 显示失败的测试
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ 失败的测试:")
            for result in failed_results:
                print(f"  {result['test_name']}: {result['message']}")
        
        print(f"\n📄 详细报告: {report_file}")
        
        # 总体评估
        if failed_tests == 0:
            print(f"\n🎉 所有测试通过！前端后端通信完全正常！")
        elif success_rate >= 80:
            print(f"\n✅ 大部分测试通过，通信基本正常")
        else:
            print(f"\n⚠️ 多项测试失败，需要检查配置")
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        failed_results = [r for r in self.test_results if not r["success"]]
        
        if not failed_results:
            recommendations.extend([
                "前端后端通信完全正常",
                "可以开始部署和使用系统",
                "建议定期运行通信测试"
            ])
        else:
            for result in failed_results:
                test_name = result["test_name"]
                
                if "API" in test_name:
                    recommendations.append("检查后端服务是否正常运行")
                    recommendations.append("确认API路由配置正确")
                
                elif "CORS" in test_name:
                    recommendations.append("检查后端CORS配置")
                    recommendations.append("确认允许的域名列表")
                
                elif "WebSocket" in test_name:
                    recommendations.append("检查WebSocket服务配置")
                    recommendations.append("确认防火墙设置")
                
                elif "前端页面" in test_name:
                    recommendations.append("检查前端部署状态")
                    recommendations.append("确认Cloudflare Pages配置")
        
        return list(set(recommendations))

def main():
    """主函数"""
    print("🧪 前端后端通信测试工具")
    print("=" * 40)
    
    tester = FrontendBackendTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
