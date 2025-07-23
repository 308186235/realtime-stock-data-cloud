#!/usr/bin/env python3
"""
云端本地集成测试
测试云端Agent与本地交易系统的完整通信流程
"""

import os
import sys
import json
import time
import asyncio
import logging
import requests
import websockets
from datetime import datetime
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudLocalIntegrationTester:
    """云端本地集成测试器"""
    
    def __init__(self):
        self.cloud_api_url = "https://api.aigupiao.me/api/cloud-local-trading"
        self.local_api_url = "http://localhost:8888"
        self.test_results = []
        
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 云端本地集成综合测试")
        print("=" * 60)
        
        try:
            # 1. 测试本地服务器
            self._test_local_server()
            
            # 2. 测试云端API
            self._test_cloud_api()
            
            # 3. 测试云端到本地通信
            asyncio.run(self._test_cloud_to_local_communication())
            
            # 4. 测试Agent集成
            self._test_agent_integration()
            
            # 5. 生成测试报告
            self._generate_test_report()
            
        except Exception as e:
            logger.error(f"测试过程异常: {e}")
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
    
    def _test_local_server(self):
        """测试本地服务器"""
        print("\n🖥️ 测试本地服务器...")
        
        try:
            # 测试健康检查
            response = requests.get(f"{self.local_api_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                local_trading_available = data.get("local_trading_available", False)
                
                self._add_test_result(
                    "本地服务器健康检查", True,
                    f"服务正常，本地交易可用: {local_trading_available}"
                )
            else:
                self._add_test_result(
                    "本地服务器健康检查", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "本地服务器健康检查", False,
                f"连接失败: {e}"
            )
        
        # 测试本地状态
        try:
            response = requests.get(f"{self.local_api_url}/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self._add_test_result(
                    "本地状态获取", True,
                    f"状态获取成功，交易软件激活: {data.get('trading_software_active', False)}"
                )
            else:
                self._add_test_result(
                    "本地状态获取", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "本地状态获取", False,
                f"获取失败: {e}"
            )
    
    def _test_cloud_api(self):
        """测试云端API"""
        print("\n☁️ 测试云端API...")
        
        try:
            # 测试云端状态
            response = requests.get(f"{self.cloud_api_url}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                local_connections = data.get("local_connections", 0)
                
                self._add_test_result(
                    "云端API状态", True,
                    f"API正常，本地连接数: {local_connections}"
                )
            else:
                self._add_test_result(
                    "云端API状态", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "云端API状态", False,
                f"连接失败: {e}"
            )
        
        # 测试云端文档
        try:
            response = requests.get(f"{self.cloud_api_url}/docs", timeout=10)
            
            if response.status_code == 200:
                self._add_test_result(
                    "云端API文档", True,
                    "API文档可访问"
                )
            else:
                self._add_test_result(
                    "云端API文档", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "云端API文档", False,
                f"访问失败: {e}"
            )
    
    async def _test_cloud_to_local_communication(self):
        """测试云端到本地通信"""
        print("\n🔗 测试云端到本地通信...")
        
        # 测试连接测试接口
        try:
            response = requests.post(f"{self.cloud_api_url}/test-connection", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                self._add_test_result(
                    "云端到本地连接测试", success,
                    data.get("message", "连接测试完成")
                )
            else:
                self._add_test_result(
                    "云端到本地连接测试", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "云端到本地连接测试", False,
                f"测试失败: {e}"
            )
        
        # 测试获取本地状态
        try:
            response = requests.get(f"{self.cloud_api_url}/local-status", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                self._add_test_result(
                    "云端获取本地状态", success,
                    data.get("message", "状态获取完成")
                )
            else:
                self._add_test_result(
                    "云端获取本地状态", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "云端获取本地状态", False,
                f"获取失败: {e}"
            )
    
    def _test_agent_integration(self):
        """测试Agent集成"""
        print("\n🤖 测试Agent集成...")
        
        # 测试Agent买入接口
        try:
            trade_data = {
                "stock_code": "000001",
                "quantity": 100,
                "price": 10.50,
                "agent_id": "test_agent"
            }
            
            response = requests.post(
                f"{self.cloud_api_url}/agent/buy",
                params=trade_data,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                self._add_test_result(
                    "Agent买入接口", success,
                    data.get("message", "买入指令测试完成")
                )
            else:
                self._add_test_result(
                    "Agent买入接口", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "Agent买入接口", False,
                f"测试失败: {e}"
            )
        
        # 测试Agent导出接口
        try:
            response = requests.post(
                f"{self.cloud_api_url}/agent/export/holdings",
                params={"agent_id": "test_agent"},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                self._add_test_result(
                    "Agent导出接口", success,
                    data.get("message", "导出指令测试完成")
                )
            else:
                self._add_test_result(
                    "Agent导出接口", False,
                    f"HTTP {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self._add_test_result(
                "Agent导出接口", False,
                f"测试失败: {e}"
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
            "test_type": "云端本地集成测试",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.test_results,
            "architecture": {
                "cloud_api": self.cloud_api_url,
                "local_api": self.local_api_url,
                "communication": "HTTP + WebSocket"
            },
            "recommendations": self._generate_recommendations()
        }
        
        # 保存报告
        report_file = f"cloud_local_integration_test_{int(time.time())}.json"
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
            print(f"\n🎉 所有测试通过！云端本地集成完全正常！")
        elif success_rate >= 70:
            print(f"\n✅ 大部分测试通过，系统基本可用")
        else:
            print(f"\n⚠️ 多项测试失败，需要检查系统配置")
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        failed_results = [r for r in self.test_results if not r["success"]]
        
        # 基于失败的测试生成建议
        for result in failed_results:
            test_name = result["test_name"]
            
            if "本地服务器" in test_name:
                recommendations.append("启动本地交易服务器: python local_trading_server.py")
                recommendations.append("检查本地服务器端口8888是否被占用")
            
            elif "云端API" in test_name:
                recommendations.append("检查云端API部署状态")
                recommendations.append("确认Cloudflare Workers配置正确")
            
            elif "云端到本地" in test_name:
                recommendations.append("检查WebSocket连接配置")
                recommendations.append("确认本地服务器已连接到云端")
            
            elif "Agent" in test_name:
                recommendations.append("检查Agent API路由配置")
                recommendations.append("确认本地交易模块可用")
        
        # 通用建议
        if not recommendations:
            recommendations.extend([
                "系统集成测试通过，可以开始使用",
                "建议配置淘宝股票数据推送服务",
                "测试完整的数据流和交易执行"
            ])
        else:
            recommendations.extend([
                "确保本地交易软件正常运行",
                "检查网络连接和防火墙设置",
                "查看详细日志排查问题"
            ])
        
        return list(set(recommendations))  # 去重

def main():
    """主函数"""
    print("🧪 云端本地集成测试工具")
    print("=" * 40)
    print("测试云端Agent与本地交易系统的完整通信")
    print()
    
    # 检查配置
    cloud_url = input("云端API地址 [https://api.aigupiao.me/api/cloud-local-trading]: ").strip()
    if not cloud_url:
        cloud_url = "https://api.aigupiao.me/api/cloud-local-trading"
    
    local_url = input("本地API地址 [http://localhost:8888]: ").strip()
    if not local_url:
        local_url = "http://localhost:8888"
    
    # 创建测试器
    tester = CloudLocalIntegrationTester()
    tester.cloud_api_url = cloud_url
    tester.local_api_url = local_url
    
    print(f"\n🔗 测试配置:")
    print(f"  云端API: {cloud_url}")
    print(f"  本地API: {local_url}")
    print()
    
    # 运行测试
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
