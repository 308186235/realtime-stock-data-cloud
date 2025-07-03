#!/usr/bin/env python3
"""
完整的OneDrive集成测试脚本
测试本地到云端的完整数据流程
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class OneDriveIntegrationTest:
    """OneDrive集成测试管理器"""
    
    def __init__(self):
        self.base_dir = Path("E:/交易8")
        self.mount_point = Path("C:/mnt/onedrive")
        self.trading_data_dir = self.mount_point / "TradingData"
        self.cloud_api = "https://api.aigupiao.me"
        
    def check_mount_status(self):
        """检查挂载状态"""
        print("🔍 检查OneDrive挂载状态...")
        
        if not self.mount_point.exists():
            print(f"❌ 挂载点不存在: {self.mount_point}")
            return False
        
        if not self.trading_data_dir.exists():
            print(f"❌ 交易数据目录不存在: {self.trading_data_dir}")
            return False
        
        # 测试写入权限
        try:
            test_file = self.trading_data_dir / "mount_test.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("mount test")
            
            if test_file.exists():
                test_file.unlink()
                print("✅ OneDrive挂载状态正常")
                return True
            else:
                print("❌ 挂载写入测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 挂载测试异常: {e}")
            return False
    
    def create_test_data(self):
        """创建测试数据"""
        print("📝 创建测试数据...")
        
        # 模拟持仓数据
        positions_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "local_trading_system",
            "data_type": "positions",
            "positions": [
                {
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "quantity": 1000,
                    "current_price": 13.50,
                    "market_value": 13500.00,
                    "cost_price": 13.20,
                    "profit_loss": 300.00,
                    "profit_loss_ratio": 0.0227
                },
                {
                    "stock_code": "000002",
                    "stock_name": "万科A",
                    "quantity": 500,
                    "current_price": 8.90,
                    "market_value": 4450.00,
                    "cost_price": 9.10,
                    "profit_loss": -100.00,
                    "profit_loss_ratio": -0.0220
                }
            ],
            "total_market_value": 17950.00,
            "total_cost": 17600.00,
            "total_profit_loss": 350.00,
            "total_profit_loss_ratio": 0.0199
        }
        
        # 模拟余额数据
        balance_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "local_trading_system",
            "data_type": "balance",
            "balance": {
                "available_cash": 25000.00,
                "frozen_cash": 0.00,
                "total_assets": 42950.00,
                "market_value": 17950.00,
                "total_profit_loss": 350.00,
                "profit_loss_ratio": 0.0082
            }
        }
        
        return positions_data, balance_data
    
    def save_to_onedrive(self, data, filename):
        """保存数据到OneDrive"""
        print(f"💾 保存数据到OneDrive: {filename}")
        
        try:
            file_path = self.trading_data_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已保存: {file_path}")
            
            # 验证文件存在
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✅ 文件验证成功，大小: {file_size} 字节")
                return True
            else:
                print("❌ 文件保存验证失败")
                return False
                
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
    
    def test_cloud_access(self):
        """测试云端访问"""
        print("🌐 测试云端API访问...")
        
        endpoints = [
            {
                "name": "持仓数据",
                "url": f"{self.cloud_api}/api/local-trading/positions",
                "expected_fields": ["positions", "total_market_value"]
            },
            {
                "name": "余额数据",
                "url": f"{self.cloud_api}/api/local-trading/balance",
                "expected_fields": ["balance", "available_cash"]
            }
        ]
        
        success_count = 0
        
        for endpoint in endpoints:
            print(f"\n🔥 测试: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                response = requests.get(endpoint['url'], timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 响应成功: {response.status_code}")
                    
                    # 检查数据结构
                    has_expected_fields = any(
                        field in str(data) for field in endpoint['expected_fields']
                    )
                    
                    if has_expected_fields:
                        print(f"✅ 数据结构验证通过")
                        success_count += 1
                    else:
                        print(f"⚠️ 数据结构可能不完整")
                        print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                        
                elif response.status_code == 503:
                    print(f"⚠️ 服务暂不可用 (503)")
                    print("   这可能是正常的，如果使用备用数据")
                else:
                    print(f"❌ 响应失败: {response.status_code}")
                    print(f"   错误信息: {response.text[:200]}...")
                    
            except requests.exceptions.Timeout:
                print("⏰ 请求超时")
            except requests.exceptions.ConnectionError:
                print("🔌 连接失败")
            except Exception as e:
                print(f"❌ 请求异常: {e}")
        
        print(f"\n📊 云端访问测试结果: {success_count}/{len(endpoints)} 成功")
        return success_count > 0
    
    def test_data_sync_flow(self):
        """测试数据同步流程"""
        print("🔄 测试完整数据同步流程...")
        
        # 1. 创建测试数据
        positions_data, balance_data = self.create_test_data()
        
        # 2. 保存到OneDrive
        positions_saved = self.save_to_onedrive(positions_data, "latest_positions.json")
        balance_saved = self.save_to_onedrive(balance_data, "latest_balance.json")
        
        if not (positions_saved and balance_saved):
            print("❌ 数据保存失败")
            return False
        
        # 3. 等待同步
        print("⏳ 等待OneDrive同步...")
        time.sleep(5)
        
        # 4. 测试云端访问
        cloud_success = self.test_cloud_access()
        
        return cloud_success
    
    def run_complete_test(self):
        """运行完整测试"""
        print("🚀 OneDrive完整集成测试")
        print("=" * 60)
        
        # 1. 检查挂载状态
        print("\n📋 步骤1: 检查挂载状态")
        if not self.check_mount_status():
            print("❌ 挂载状态检查失败")
            return False
        
        # 2. 测试数据同步流程
        print("\n📋 步骤2: 测试数据同步流程")
        if not self.test_data_sync_flow():
            print("❌ 数据同步流程测试失败")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 OneDrive完整集成测试成功！")
        print("=" * 60)
        print("✅ 本地挂载正常")
        print("✅ 数据保存成功")
        print("✅ 云端访问正常")
        print("\n🎯 系统已准备就绪，可以开始使用！")
        print("\n📋 下一步操作:")
        print("1. 修改交易软件导出路径为: C:/mnt/onedrive/TradingData/")
        print("2. 测试真实交易数据导出")
        print("3. 验证云端Agent能正确读取数据")
        
        return True

def main():
    """主函数"""
    tester = OneDriveIntegrationTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎯 测试成功完成！")
    else:
        print("\n💥 测试过程中出现错误！")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
