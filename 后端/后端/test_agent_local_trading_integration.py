#!/usr/bin/env python3
"""
Agent本地交易集成测试
测试Agent通过API调用本地交易软件的完整流程
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Dict, List, Any
import requests
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentLocalTradingTester:
    """Agent本地交易集成测试器"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api/local-trading"):
        self.api_base_url = api_base_url
        self.test_results = []
        
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 Agent本地交易集成测试")
        print("=" * 60)
        
        try:
            # 1. 测试API连接
            self._test_api_connection()
            
            # 2. 测试系统状态
            self._test_system_status()
            
            # 3. 测试控制器操作
            self._test_controller_operations()
            
            # 4. 测试数据导出
            self._test_data_export()
            
            # 5. 测试交易执行(模拟)
            self._test_trade_execution()
            
            # 6. 测试投资组合获取
            self._test_portfolio_retrieval()
            
            # 7. 生成测试报告
            self._generate_test_report()
            
        except Exception as e:
            logger.error(f"测试过程异常: {e}")
            self._add_test_result("综合测试", False, f"测试异常: {e}")
    
    def _api_call(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """API调用"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
    
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
    
    def _test_api_connection(self):
        """测试API连接"""
        print("\n🔌 测试API连接...")
        
        try:
            result = self._api_call("/health")
            
            if result.get("status") == "healthy":
                self._add_test_result(
                    "API连接", True, 
                    f"连接正常,本地交易可用: {result.get('local_trading_available', False)}"
                )
            else:
                self._add_test_result("API连接", False, "API状态异常")
                
        except Exception as e:
            self._add_test_result("API连接", False, f"连接失败: {e}")
    
    def _test_system_status(self):
        """测试系统状态"""
        print("\n📊 测试系统状态...")
        
        try:
            result = self._api_call("/status")
            
            # 检查各项状态
            controller_running = result.get("controller_running", False)
            interface_initialized = result.get("local_interface_initialized", False)
            software_active = result.get("trading_software_active", False)
            
            status_msg = f"控制器: {'运行' if controller_running else '停止'}, " \
                        f"接口: {'已初始化' if interface_initialized else '未初始化'}, " \
                        f"软件: {'激活' if software_active else '未激活'}"
            
            # 至少接口要初始化才算成功
            success = interface_initialized
            
            self._add_test_result("系统状态", success, status_msg)
            
        except Exception as e:
            self._add_test_result("系统状态", False, f"状态检查失败: {e}")
    
    def _test_controller_operations(self):
        """测试控制器操作"""
        print("\n🎮 测试控制器操作...")
        
        # 测试启动控制器
        try:
            result = self._api_call("/start", "POST")
            success = result.get("success", False)
            message = result.get("message", "未知结果")
            
            self._add_test_result("启动控制器", success, message)
            
            # 等待一下
            time.sleep(1)
            
        except Exception as e:
            self._add_test_result("启动控制器", False, f"启动失败: {e}")
        
        # 测试停止控制器
        try:
            result = self._api_call("/stop", "POST")
            success = result.get("success", False)
            message = result.get("message", "未知结果")
            
            self._add_test_result("停止控制器", success, message)
            
        except Exception as e:
            self._add_test_result("停止控制器", False, f"停止失败: {e}")
    
    def _test_data_export(self):
        """测试数据导出"""
        print("\n📊 测试数据导出...")
        
        export_types = ["holdings", "transactions", "orders"]
        
        for export_type in export_types:
            try:
                data = {"data_type": export_type}
                result = self._api_call("/export", "POST", data)
                
                success = result.get("success", False)
                message = result.get("message", "未知结果")
                
                self._add_test_result(f"导出{export_type}", success, message)
                
            except Exception as e:
                self._add_test_result(f"导出{export_type}", False, f"导出失败: {e}")
    
    def _test_trade_execution(self):
        """测试交易执行(模拟)"""
        print("\n💰 测试交易执行...")
        
        # 测试买入
        try:
            trade_data = {
                "action": "buy",
                "stock_code": "000001",
                "quantity": 100,
                "price": 10.50
            }
            
            result = self._api_call("/execute", "POST", trade_data)
            
            success = result.get("success", False)
            message = result.get("message", "未知结果")
            
            self._add_test_result("模拟买入", success, message)
            
        except Exception as e:
            self._add_test_result("模拟买入", False, f"买入测试失败: {e}")
        
        # 测试卖出
        try:
            trade_data = {
                "action": "sell",
                "stock_code": "000001",
                "quantity": 100,
                "price": 10.60
            }
            
            result = self._api_call("/execute", "POST", trade_data)
            
            success = result.get("success", False)
            message = result.get("message", "未知结果")
            
            self._add_test_result("模拟卖出", success, message)
            
        except Exception as e:
            self._add_test_result("模拟卖出", False, f"卖出测试失败: {e}")
    
    def _test_portfolio_retrieval(self):
        """测试投资组合获取"""
        print("\n📈 测试投资组合获取...")
        
        try:
            result = self._api_call("/portfolio")
            
            success = result.get("success", False)
            message = result.get("message", "未知结果")
            data_files = result.get("data_files", [])
            
            detail_msg = f"{message}, 数据文件: {len(data_files)}个"
            
            self._add_test_result("投资组合获取", success, detail_msg)
            
        except Exception as e:
            self._add_test_result("投资组合获取", False, f"获取失败: {e}")
    
    def _generate_test_report(self):
        """生成测试报告"""
        print("\n📋 生成测试报告...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
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
        report_file = f"agent_trading_test_report_{int(time.time())}.json"
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
            print(f"\n🎉 所有测试通过!Agent本地交易集成完全正常!")
        elif success_rate >= 70:
            print(f"\n✅ 大部分测试通过,系统基本可用")
        else:
            print(f"\n⚠️ 多项测试失败,需要检查系统配置")
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        failed_results = [r for r in self.test_results if not r["success"]]
        
        # 基于失败的测试生成建议
        for result in failed_results:
            test_name = result["test_name"]
            
            if "API连接" in test_name:
                recommendations.append("检查后端服务是否正常运行")
                recommendations.append("确认API地址配置正确")
            
            elif "系统状态" in test_name:
                recommendations.append("检查本地交易模块是否正确导入")
                recommendations.append("确认working-trader-FIXED相关文件存在")
            
            elif "控制器" in test_name:
                recommendations.append("检查本地交易接口初始化状态")
                recommendations.append("确认交易软件运行环境")
            
            elif "导出" in test_name:
                recommendations.append("检查交易软件是否正常运行")
                recommendations.append("确认导出功能模块正常")
            
            elif "交易执行" in test_name:
                recommendations.append("检查交易软件窗口状态")
                recommendations.append("确认键盘模拟功能正常")
            
            elif "投资组合" in test_name:
                recommendations.append("先执行数据导出操作")
                recommendations.append("检查导出文件是否生成")
        
        # 通用建议
        if not recommendations:
            recommendations.extend([
                "系统运行正常,可以开始使用",
                "建议定期测试确保功能稳定"
            ])
        else:
            recommendations.extend([
                "检查Windows环境和权限设置",
                "确认交易软件版本兼容性",
                "查看详细日志排查问题"
            ])
        
        return list(set(recommendations))  # 去重

def main():
    """主函数"""
    print("🧪 Agent本地交易集成测试工具")
    print("=" * 40)
    
    # 检查API地址
    api_url = input("请输入API地址 [http://localhost:8000/api/local-trading]: ").strip()
    if not api_url:
        api_url = "http://localhost:8000/api/local-trading"
    
    # 创建测试器
    tester = AgentLocalTradingTester(api_url)
    
    # 运行测试
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
