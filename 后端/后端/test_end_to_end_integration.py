#!/usr/bin/env python3
"""
端到端系统集成测试
测试从本地交易软件到云端分析的完整数据流
"""

import requests
import json
import time
from datetime import datetime

class EndToEndTester:
    def __init__(self):
        self.local_api = "http://localhost:5000"  # 本地交易API (Flask)
        self.local_main_api = "http://localhost:8000"  # 本地主API
        self.local_trading_api = "http://localhost:8888"  # 本地交易系统API
        self.local_agent_api = "http://localhost:9999"  # 本地Agent API
        self.cloud_api = "https://api.aigupiao.me"  # 云端API
        
        self.test_results = []
    
    def log_result(self, test_name, success, message, data=None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {message}")
        if data and isinstance(data, dict):
            for key, value in data.items():
                print(f"     {key}: {value}")
    
    def test_local_services_health(self):
        """测试本地服务健康状态"""
        print("\n🔍 测试本地服务健康状态:")
        
        services = [
            ("本地交易API", self.local_api + "/health"),
            ("本地主API", self.local_main_api + "/api/health"),
            ("本地交易系统", self.local_trading_api + "/health"),
            ("本地Agent", self.local_agent_api + "/health")
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"{name}健康检查", True, "服务正常", 
                                  {"状态": data.get('status', 'N/A')})
                else:
                    self.log_result(f"{name}健康检查", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result(f"{name}健康检查", False, f"连接失败: {e}")
    
    def test_local_trading_operations(self):
        """测试本地交易操作"""
        print("\n📈 测试本地交易操作:")
        
        # 测试余额查询
        try:
            response = requests.get(f"{self.local_api}/balance", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    balance_info = data.get('data', {})
                    self.log_result("余额查询", True, "查询成功", 
                                  {"可用资金": f"{balance_info.get('available_cash', 0):,.2f}"})
                else:
                    self.log_result("余额查询", False, "查询失败")
            else:
                self.log_result("余额查询", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("余额查询", False, f"连接失败: {e}")
        
        # 测试模拟买入操作
        try:
            trade_data = {
                "action": "buy",
                "code": "000001",
                "quantity": 100,
                "price": 10.0
            }
            response = requests.post(f"{self.local_api}/trade", json=trade_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("模拟买入", True, "操作成功", 
                                  {"股票代码": trade_data['code'], "数量": trade_data['quantity']})
                else:
                    self.log_result("模拟买入", False, "操作失败")
            else:
                self.log_result("模拟买入", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("模拟买入", False, f"连接失败: {e}")
        
        # 测试数据导出
        try:
            export_data = {"type": "holdings"}
            response = requests.post(f"{self.local_api}/export", json=export_data, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    export_results = data.get('data', {}).get('export_results', {})
                    self.log_result("数据导出", True, "导出成功", 
                                  {"持仓导出": "成功" if export_results.get('holdings') else "失败"})
                else:
                    self.log_result("数据导出", False, "导出失败")
            else:
                self.log_result("数据导出", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("数据导出", False, f"连接失败: {e}")
    
    def test_cloud_connectivity(self):
        """测试云端连接"""
        print("\n☁️ 测试云端连接:")
        
        # 测试云端健康检查
        try:
            response = requests.get(f"{self.cloud_api}/health", timeout=15)
            if response.status_code == 200:
                data = response.json()
                cloud_info = data.get('data', {})
                self.log_result("云端健康检查", True, "连接成功", 
                              {"版本": cloud_info.get('version', 'N/A'),
                               "状态": cloud_info.get('status', 'N/A')})
            else:
                self.log_result("云端健康检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("云端健康检查", False, f"连接失败: {e}")
        
        # 测试云端股票数据
        try:
            response = requests.get(f"{self.cloud_api}/api/stock/quote?symbol=000001", timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.log_result("云端股票数据", True, "获取成功", 
                              {"API响应": "正常"})
            else:
                self.log_result("云端股票数据", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("云端股票数据", False, f"连接失败: {e}")
    
    def test_data_flow_integration(self):
        """测试数据流集成"""
        print("\n🔄 测试数据流集成:")
        
        # 模拟完整的交易流程
        print("     执行完整交易流程...")
        
        # 1. 本地获取余额
        local_balance = None
        try:
            response = requests.get(f"{self.local_api}/balance", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    local_balance = data.get('data', {}).get('available_cash', 0)
                    self.log_result("步骤1-余额获取", True, f"本地余额: {local_balance:,.2f}")
                else:
                    self.log_result("步骤1-余额获取", False, "获取失败")
            else:
                self.log_result("步骤1-余额获取", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("步骤1-余额获取", False, f"连接失败: {e}")
        
        # 2. 云端获取股票信息
        stock_info = None
        try:
            response = requests.get(f"{self.cloud_api}/api/stock/quote?symbol=000001", timeout=10)
            if response.status_code == 200:
                self.log_result("步骤2-股票信息", True, "云端股票信息获取成功")
                stock_info = True
            else:
                self.log_result("步骤2-股票信息", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("步骤2-股票信息", False, f"连接失败: {e}")
        
        # 3. 本地执行交易
        trade_success = False
        if local_balance and stock_info:
            try:
                trade_data = {
                    "action": "buy",
                    "code": "000001", 
                    "quantity": 100,
                    "price": 10.0
                }
                response = requests.post(f"{self.local_api}/trade", json=trade_data, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_result("步骤3-执行交易", True, "本地交易执行成功")
                        trade_success = True
                    else:
                        self.log_result("步骤3-执行交易", False, "交易执行失败")
                else:
                    self.log_result("步骤3-执行交易", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result("步骤3-执行交易", False, f"连接失败: {e}")
        
        # 4. 数据导出和上传
        if trade_success:
            try:
                export_data = {"type": "holdings"}
                response = requests.post(f"{self.local_api}/export", json=export_data, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_result("步骤4-数据导出", True, "交易数据导出成功")
                    else:
                        self.log_result("步骤4-数据导出", False, "数据导出失败")
                else:
                    self.log_result("步骤4-数据导出", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result("步骤4-数据导出", False, f"连接失败: {e}")
        
        # 综合评估
        successful_steps = sum(1 for result in self.test_results[-4:] if result['success'])
        if successful_steps >= 3:
            self.log_result("数据流集成", True, f"集成测试通过 ({successful_steps}/4 步骤成功)")
        else:
            self.log_result("数据流集成", False, f"集成测试失败 ({successful_steps}/4 步骤成功)")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 端到端集成测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {total_tests - successful_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 系统集成测试通过!混合交易系统运行正常。")
        elif success_rate >= 60:
            print("\n⚠️ 系统基本可用,但存在一些问题需要修复。")
        else:
            print("\n❌ 系统集成测试失败,需要重大修复。")
        
        # 保存详细报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate
            },
            "detailed_results": self.test_results
        }
        
        with open("integration_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: integration_test_report.json")

def main():
    """主函数"""
    print(f"🔧 端到端系统集成测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tester = EndToEndTester()
    
    # 执行所有测试
    tester.test_local_services_health()
    tester.test_local_trading_operations()
    tester.test_cloud_connectivity()
    tester.test_data_flow_integration()
    
    # 生成报告
    tester.generate_report()

if __name__ == "__main__":
    main()
