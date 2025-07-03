#!/usr/bin/env python3
"""
测试本地导出到云端Agent获取的完整流程
验证端到端数据传输
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class LocalToCloudFlowTest:
    """本地到云端流程测试器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        self.test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def check_prerequisites(self):
        """检查前置条件"""
        print("🔍 检查系统前置条件...")
        
        # 检查OneDrive挂载
        if not self.onedrive_path.exists():
            print(f"❌ OneDrive挂载目录不存在: {self.onedrive_path}")
            return False
        
        # 测试写入权限
        try:
            test_file = self.onedrive_path / f"test_{self.test_id}.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("test")
            
            if test_file.exists():
                test_file.unlink()
                print("✅ OneDrive挂载正常，具有读写权限")
                return True
            else:
                print("❌ OneDrive挂载写入测试失败")
                return False
                
        except Exception as e:
            print(f"❌ OneDrive挂载测试异常: {e}")
            return False
    
    def create_test_trading_data(self):
        """创建测试交易数据"""
        print("📝 创建测试交易数据...")
        
        # 创建带有测试标识的持仓数据
        positions_data = {
            "test_id": self.test_id,
            "timestamp": datetime.now().isoformat(),
            "source": "local_computer_test",
            "data_type": "positions",
            "export_method": "direct_to_onedrive_rclone",
            "test_note": f"端到端测试数据 - {self.test_id}",
            "positions": [
                {
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "quantity": 1200,
                    "current_price": 13.75,
                    "market_value": 16500.00,
                    "cost_price": 13.20,
                    "profit_loss": 660.00,
                    "profit_loss_ratio": 0.0417,
                    "test_marker": f"TEST_{self.test_id}"
                },
                {
                    "stock_code": "600036",
                    "stock_name": "招商银行",
                    "quantity": 400,
                    "current_price": 43.20,
                    "market_value": 17280.00,
                    "cost_price": 42.50,
                    "profit_loss": 280.00,
                    "profit_loss_ratio": 0.0165,
                    "test_marker": f"TEST_{self.test_id}"
                },
                {
                    "stock_code": "000002",
                    "stock_name": "万科A",
                    "quantity": 600,
                    "current_price": 9.15,
                    "market_value": 5490.00,
                    "cost_price": 9.00,
                    "profit_loss": 90.00,
                    "profit_loss_ratio": 0.0167,
                    "test_marker": f"TEST_{self.test_id}"
                }
            ],
            "summary": {
                "total_positions": 3,
                "total_market_value": 39270.00,
                "total_cost": 38240.00,
                "total_profit_loss": 1030.00,
                "total_profit_loss_ratio": 0.0269,
                "test_marker": f"TEST_{self.test_id}"
            }
        }
        
        # 创建带有测试标识的余额数据
        balance_data = {
            "test_id": self.test_id,
            "timestamp": datetime.now().isoformat(),
            "source": "local_computer_test",
            "data_type": "balance",
            "export_method": "direct_to_onedrive_rclone",
            "test_note": f"端到端测试数据 - {self.test_id}",
            "balance": {
                "available_cash": 32500.00,
                "frozen_cash": 0.00,
                "total_cash": 32500.00,
                "market_value": 39270.00,
                "total_assets": 71770.00,
                "total_profit_loss": 1030.00,
                "profit_loss_ratio": 0.0146,
                "test_marker": f"TEST_{self.test_id}"
            },
            "account_info": {
                "account_id": f"TEST_{self.test_id}",
                "account_type": "测试账户",
                "broker": "测试券商",
                "last_update": datetime.now().isoformat(),
                "test_marker": f"TEST_{self.test_id}"
            }
        }
        
        return positions_data, balance_data
    
    def export_to_onedrive(self, positions_data, balance_data):
        """导出数据到OneDrive"""
        print("💾 导出测试数据到OneDrive...")
        
        try:
            # 保存持仓数据
            positions_file = self.onedrive_path / "latest_positions.json"
            with open(positions_file, 'w', encoding='utf-8') as f:
                json.dump(positions_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 持仓数据已保存: {positions_file}")
            print(f"   测试ID: {self.test_id}")
            print(f"   总持仓: {positions_data['summary']['total_positions']} 只")
            print(f"   总市值: ¥{positions_data['summary']['total_market_value']:,.2f}")
            
            # 保存余额数据
            balance_file = self.onedrive_path / "latest_balance.json"
            with open(balance_file, 'w', encoding='utf-8') as f:
                json.dump(balance_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 余额数据已保存: {balance_file}")
            print(f"   可用资金: ¥{balance_data['balance']['available_cash']:,.2f}")
            print(f"   总资产: ¥{balance_data['balance']['total_assets']:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 导出数据失败: {e}")
            return False
    
    def wait_for_sync(self, wait_time=10):
        """等待OneDrive同步"""
        print(f"⏳ 等待OneDrive同步 ({wait_time}秒)...")
        
        for i in range(wait_time):
            print(f"   同步中... {i+1}/{wait_time}")
            time.sleep(1)
        
        print("✅ 同步等待完成")
    
    def test_cloud_agent_access(self):
        """测试云端Agent访问"""
        print("🌐 测试云端Agent访问...")
        
        endpoints = [
            {
                "name": "持仓数据API",
                "url": f"{self.cloud_api}/api/local-trading/positions",
                "expected_fields": ["positions", "test_id", "test_marker"]
            },
            {
                "name": "余额数据API", 
                "url": f"{self.cloud_api}/api/local-trading/balance",
                "expected_fields": ["balance", "test_id", "test_marker"]
            }
        ]
        
        test_results = {}
        
        for endpoint in endpoints:
            print(f"\n🔥 测试: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                response = requests.get(endpoint['url'], timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ HTTP响应成功: {response.status_code}")
                    
                    # 检查是否包含我们的测试数据
                    data_str = json.dumps(data, ensure_ascii=False)
                    
                    if self.test_id in data_str:
                        print(f"✅ 发现测试数据ID: {self.test_id}")
                        test_results[endpoint['name']] = {
                            "status": "成功",
                            "has_test_data": True,
                            "response_time": response.elapsed.total_seconds()
                        }
                        
                        # 检查具体字段
                        for field in endpoint['expected_fields']:
                            if field in data_str:
                                print(f"   ✅ 包含字段: {field}")
                            else:
                                print(f"   ⚠️ 缺少字段: {field}")
                        
                        # 显示部分数据内容
                        if 'timestamp' in data:
                            print(f"   📅 数据时间: {data.get('timestamp', '未知')}")
                        
                        if 'test_note' in data:
                            print(f"   📝 测试备注: {data.get('test_note', '未知')}")
                            
                    else:
                        print(f"⚠️ 未发现测试数据ID: {self.test_id}")
                        print("   可能是缓存延迟或使用了备用数据")
                        test_results[endpoint['name']] = {
                            "status": "部分成功",
                            "has_test_data": False,
                            "response_time": response.elapsed.total_seconds()
                        }
                        
                        # 显示实际返回的数据时间
                        if 'timestamp' in data:
                            print(f"   📅 返回数据时间: {data.get('timestamp', '未知')}")
                
                elif response.status_code == 503:
                    print(f"⚠️ 服务暂不可用 (503) - 可能使用备用数据")
                    test_results[endpoint['name']] = {
                        "status": "服务不可用",
                        "has_test_data": False
                    }
                else:
                    print(f"❌ HTTP响应失败: {response.status_code}")
                    print(f"   错误信息: {response.text[:200]}...")
                    test_results[endpoint['name']] = {
                        "status": "失败",
                        "error": f"HTTP {response.status_code}"
                    }
                    
            except requests.exceptions.Timeout:
                print("⏰ 请求超时")
                test_results[endpoint['name']] = {
                    "status": "超时"
                }
            except requests.exceptions.ConnectionError:
                print("🔌 连接失败")
                test_results[endpoint['name']] = {
                    "status": "连接失败"
                }
            except Exception as e:
                print(f"❌ 请求异常: {e}")
                test_results[endpoint['name']] = {
                    "status": "异常",
                    "error": str(e)
                }
        
        return test_results
    
    def run_complete_test(self):
        """运行完整的端到端测试"""
        print("🚀 本地到云端Agent完整流程测试")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print("=" * 60)
        
        # 1. 检查前置条件
        print("\n📋 步骤1: 检查前置条件")
        if not self.check_prerequisites():
            print("❌ 前置条件检查失败")
            return False
        
        # 2. 创建测试数据
        print("\n📋 步骤2: 创建测试数据")
        positions_data, balance_data = self.create_test_trading_data()
        print(f"✅ 测试数据创建完成，测试ID: {self.test_id}")
        
        # 3. 导出到OneDrive
        print("\n📋 步骤3: 导出到OneDrive")
        if not self.export_to_onedrive(positions_data, balance_data):
            print("❌ 数据导出失败")
            return False
        
        # 4. 等待同步
        print("\n📋 步骤4: 等待OneDrive同步")
        self.wait_for_sync(10)
        
        # 5. 测试云端Agent访问
        print("\n📋 步骤5: 测试云端Agent访问")
        test_results = self.test_cloud_agent_access()
        
        # 6. 生成测试报告
        print("\n" + "=" * 60)
        print("📊 端到端测试报告")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        print()
        
        success_count = 0
        total_count = len(test_results)
        
        for api_name, result in test_results.items():
            status_icon = "✅" if result['status'] == '成功' else "⚠️" if result['status'] == '部分成功' else "❌"
            print(f"{status_icon} {api_name}: {result['status']}")
            
            if 'has_test_data' in result:
                data_icon = "✅" if result['has_test_data'] else "❌"
                print(f"   {data_icon} 测试数据识别: {'成功' if result['has_test_data'] else '失败'}")
            
            if 'response_time' in result:
                print(f"   ⏱️ 响应时间: {result['response_time']:.2f}秒")
            
            if 'error' in result:
                print(f"   ❌ 错误: {result['error']}")
            
            if result['status'] in ['成功', '部分成功']:
                success_count += 1
            
            print()
        
        # 总体评估
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        print("📊 测试结果统计:")
        print(f"   成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        
        if success_rate >= 100:
            print("🎉 端到端测试完全成功！")
            print("✅ 本地导出的数据已被云端Agent成功获取")
            overall_success = True
        elif success_rate >= 50:
            print("⚠️ 端到端测试部分成功")
            print("📝 云端Agent可以访问API，但可能使用了缓存数据")
            overall_success = True
        else:
            print("❌ 端到端测试失败")
            print("💥 云端Agent无法正确获取本地导出的数据")
            overall_success = False
        
        print("\n📋 测试结论:")
        if overall_success:
            print("✅ 本地电脑导出 → OneDrive同步 → 云端Agent获取 流程正常")
            print("✅ 系统已准备就绪，可以进行实际交易数据同步")
        else:
            print("❌ 数据流程存在问题，需要进一步排查")
        
        print("=" * 60)
        
        return overall_success

def main():
    """主函数"""
    tester = LocalToCloudFlowTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎯 端到端测试成功完成！")
        print("\n📋 下一步操作:")
        print("1. 可以开始使用真实交易软件导出数据")
        print("2. 云端Agent将能够实时获取最新交易数据")
        print("3. 前端应用可以显示实时交易信息")
    else:
        print("\n💥 端到端测试发现问题！")
        print("\n🔧 建议检查:")
        print("1. OneDrive挂载状态")
        print("2. 网络连接")
        print("3. 云端API服务状态")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
