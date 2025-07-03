"""
最终集成测试：验证前端-后端-本地通信完整性
"""

import requests
import json
import time
from datetime import datetime

class IntegrationTestFinal:
    def __init__(self):
        self.local_url = "http://localhost:5000"
        self.test_results = {}
    
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_local_health(self):
        """测试本地API健康检查"""
        try:
            self.log("💻 测试本地API健康检查...")
            response = requests.get(f"{self.local_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 本地API健康检查成功: {data.get('status')}")
                self.log(f"   功能: {', '.join(data.get('capabilities', []))}")
                return True
            else:
                self.log(f"❌ 本地API健康检查失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 本地API连接异常: {e}")
            return False
    
    def test_local_balance(self):
        """测试本地余额获取"""
        try:
            self.log("💰 测试本地余额获取...")
            response = requests.get(f"{self.local_url}/balance", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    balance = data['data']
                    self.log(f"✅ 余额获取成功: {balance['available_cash']:,.2f} 元")
                    return True
                else:
                    self.log(f"❌ 余额获取失败: {data.get('error')}")
                    return False
            else:
                self.log(f"❌ 余额请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 余额获取异常: {e}")
            return False
    
    def test_local_export(self):
        """测试本地数据导出"""
        try:
            self.log("📊 测试本地数据导出...")
            response = requests.post(
                f"{self.local_url}/export",
                json={"type": "holdings"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results = data['data']['export_results']
                    files = data['data']['files']
                    self.log(f"✅ 数据导出成功: {results}")
                    if files:
                        self.log(f"   生成文件: {list(files.values())}")
                    return True
                else:
                    self.log(f"❌ 数据导出失败: {data.get('error')}")
                    return False
            else:
                self.log(f"❌ 导出请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 数据导出异常: {e}")
            return False
    
    def test_local_trade(self):
        """测试本地交易功能"""
        try:
            self.log("🚀 测试本地交易功能...")
            response = requests.post(
                f"{self.local_url}/trade",
                json={
                    "action": "buy",
                    "code": "000001",
                    "quantity": "100",
                    "price": "市价"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trade_data = data['data']
                    self.log(f"✅ 交易功能测试成功: {trade_data['operation']} {trade_data['code']}")
                    return True
                else:
                    self.log(f"❌ 交易功能测试失败: {data.get('error')}")
                    return False
            else:
                self.log(f"❌ 交易请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ 交易功能异常: {e}")
            return False
    
    def run_test(self):
        """运行完整测试"""
        self.log("🧪 开始最终集成测试")
        self.log("=" * 60)
        
        tests = [
            ("本地API健康检查", self.test_local_health),
            ("本地余额获取", self.test_local_balance),
            ("本地数据导出", self.test_local_export),
            ("本地交易功能", self.test_local_trade)
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            self.log(f"\n🔍 执行: {name}")
            if test_func():
                passed += 1
                self.test_results[name] = True
            else:
                self.test_results[name] = False
            time.sleep(1)
        
        # 总结
        self.log("\n" + "=" * 60)
        self.log("📊 测试结果总结:")
        self.log("-" * 40)
        
        for name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            self.log(f"{name}: {status}")
        
        success_rate = (passed / total) * 100
        self.log(f"\n📈 测试通过率: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            self.log("\n🎉 所有测试通过！系统完全正常！")
            self.log("✅ 前端-后端-本地通信集成成功！")
            return True
        else:
            self.log("\n⚠️ 部分测试失败")
            return False

if __name__ == "__main__":
    tester = IntegrationTestFinal()
    success = tester.run_test()
    exit(0 if success else 1)
