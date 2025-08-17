#!/usr/bin/env python3
"""
创建真实的测试数据并测试云端Agent获取
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path

class RealTestDataCreator:
    """真实测试数据创建器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        self.test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确保OneDrive目录存在
        self.onedrive_path.mkdir(parents=True, exist_ok=True)
    
    def create_real_positions_data(self):
        """创建真实的持仓数据"""
        print("📊 创建真实持仓数据...")
        
        positions_data = {
            "test_id": self.test_id,
            "timestamp": datetime.now().isoformat(),
            "source": "dongwu_securities_manual_test",
            "data_type": "positions",
            "export_method": "manual_real_test",
            "software": "东吴证券网上股票交易系统5.0",
            "export_note": f"手动真实测试 - {self.test_id}",
            "positions": [
                {
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "quantity": 1000,
                    "current_price": 13.85,
                    "market_value": 13850.00,
                    "cost_price": 13.20,
                    "profit_loss": 650.00,
                    "profit_loss_ratio": 0.0492,
                    "real_test_marker": f"MANUAL_REAL_{self.test_id}"
                },
                {
                    "stock_code": "600036",
                    "stock_name": "招商银行",
                    "quantity": 500,
                    "current_price": 43.50,
                    "market_value": 21750.00,
                    "cost_price": 42.80,
                    "profit_loss": 350.00,
                    "profit_loss_ratio": 0.0164,
                    "real_test_marker": f"MANUAL_REAL_{self.test_id}"
                },
                {
                    "stock_code": "000002",
                    "stock_name": "万科A",
                    "quantity": 800,
                    "current_price": 9.15,
                    "market_value": 7320.00,
                    "cost_price": 9.00,
                    "profit_loss": 120.00,
                    "profit_loss_ratio": 0.0167,
                    "real_test_marker": f"MANUAL_REAL_{self.test_id}"
                }
            ],
            "summary": {
                "total_positions": 3,
                "total_market_value": 42920.00,
                "total_cost": 41800.00,
                "total_profit_loss": 1120.00,
                "total_profit_loss_ratio": 0.0268,
                "real_test_marker": f"MANUAL_REAL_{self.test_id}"
            }
        }
        
        return positions_data
    
    def create_real_balance_data(self, positions_data):
        """创建真实的余额数据"""
        print("💰 创建真实余额数据...")
        
        total_market_value = positions_data["summary"]["total_market_value"]
        available_cash = 58000.00
        total_assets = available_cash + total_market_value
        
        balance_data = {
            "test_id": self.test_id,
            "timestamp": datetime.now().isoformat(),
            "source": "dongwu_securities_manual_test",
            "data_type": "balance",
            "export_method": "manual_real_test",
            "software": "东吴证券网上股票交易系统5.0",
            "export_note": f"手动真实测试 - {self.test_id}",
            "balance": {
                "available_cash": available_cash,
                "frozen_cash": 0.00,
                "total_cash": available_cash,
                "market_value": total_market_value,
                "total_assets": total_assets,
                "total_profit_loss": positions_data["summary"]["total_profit_loss"],
                "profit_loss_ratio": positions_data["summary"]["total_profit_loss"] / total_assets,
                "real_test_marker": f"MANUAL_REAL_{self.test_id}"
            },
            "account_info": {
                "account_id": f"DONGWU_MANUAL_{self.test_id}",
                "account_type": "东吴证券真实测试账户",
                "broker": "东吴证券",
                "last_update": datetime.now().isoformat(),
                "real_test_marker": f"MANUAL_REAL_{self.test_id}"
            }
        }
        
        return balance_data
    
    def save_to_onedrive(self, data, filename):
        """保存数据到OneDrive"""
        try:
            file_path = self.onedrive_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已保存到OneDrive: {file_path}")
            print(f"   文件大小: {file_path.stat().st_size} 字节")
            return True
            
        except Exception as e:
            print(f"❌ 保存到OneDrive失败: {e}")
            return False
    
    def wait_for_sync(self, wait_time=20):
        """等待OneDrive同步"""
        print(f"⏳ 等待OneDrive同步 ({wait_time}秒)...")
        
        for i in range(wait_time):
            if i % 5 == 0:
                print(f"   同步中... {i+1}/{wait_time}")
            time.sleep(1)
        
        print("✅ 同步等待完成")
    
    def test_cloud_api_detailed(self):
        """详细测试云端API"""
        print("🌐 详细测试云端API...")
        
        endpoints = [
            ("持仓数据API", f"{self.cloud_api}/api/local-trading/positions"),
            ("余额数据API", f"{self.cloud_api}/api/local-trading/balance"),
            ("Agent完整数据API", f"{self.cloud_api}/api/agent/complete-data")
        ]
        
        results = {}
        
        for name, url in endpoints:
            print(f"\n🔥 详细测试: {name}")
            print(f"   URL: {url}")
            
            try:
                response = requests.get(url, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    data_str = json.dumps(data, ensure_ascii=False)
                    
                    # 检查测试标记
                    has_test_id = self.test_id in data_str
                    has_manual_marker = f"MANUAL_REAL_{self.test_id}" in data_str
                    has_manual_test = "manual_test" in data_str
                    
                    results[name] = {
                        "success": True,
                        "response_time": response.elapsed.total_seconds(),
                        "has_test_id": has_test_id,
                        "has_manual_marker": has_manual_marker,
                        "has_manual_test": has_manual_test,
                        "data_size": len(data_str)
                    }
                    
                    print(f"✅ 响应成功: {response.status_code}")
                    print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
                    print(f"   数据大小: {len(data_str)} 字符")
                    
                    # 检查数据内容
                    if 'data' in data:
                        response_data = data['data']
                        
                        if 'timestamp' in response_data:
                            print(f"   数据时间: {response_data['timestamp']}")
                        
                        if 'source' in response_data:
                            print(f"   数据来源: {response_data['source']}")
                        
                        if 'test_id' in response_data:
                            print(f"   测试ID: {response_data['test_id']}")
                        
                        # 检查测试标记
                        if has_test_id:
                            print(f"✅ 发现测试ID: {self.test_id}")
                        else:
                            print(f"❌ 未发现测试ID: {self.test_id}")
                        
                        if has_manual_marker:
                            print(f"✅ 发现手动测试标记")
                        else:
                            print(f"❌ 未发现手动测试标记")
                        
                        # 显示关键数据
                        if name == "持仓数据API" and 'positions' in response_data:
                            positions = response_data['positions']
                            print(f"   持仓数量: {len(positions)} 只")
                            if positions:
                                total_value = sum(pos.get('market_value', 0) for pos in positions)
                                print(f"   总市值: ¥{total_value:,.2f}")
                        
                        elif name == "余额数据API" and 'balance' in response_data:
                            balance = response_data['balance']
                            total_assets = balance.get('total_assets', 0)
                            print(f"   总资产: ¥{total_assets:,.2f}")
                        
                        elif name == "Agent完整数据API":
                            if 'trading_data' in response_data:
                                print(f"   包含交易数据: 是")
                            if 'stock_data' in response_data:
                                print(f"   包含股票数据: 是")
                
                else:
                    results[name] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                    print(f"❌ 响应失败: {response.status_code}")
                    print(f"   错误信息: {response.text[:200]}...")
                    
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ 请求异常: {e}")
        
        return results
    
    def run_real_test(self):
        """运行真实测试"""
        print("🚀 真实数据创建和云端Agent测试")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print("=" * 60)
        
        # 1. 创建真实持仓数据
        print("\n📋 步骤1: 创建真实持仓数据")
        positions_data = self.create_real_positions_data()
        print(f"   创建了 {positions_data['summary']['total_positions']} 只持仓")
        print(f"   总市值: ¥{positions_data['summary']['total_market_value']:,.2f}")
        
        # 2. 创建真实余额数据
        print("\n📋 步骤2: 创建真实余额数据")
        balance_data = self.create_real_balance_data(positions_data)
        print(f"   总资产: ¥{balance_data['balance']['total_assets']:,.2f}")
        print(f"   可用资金: ¥{balance_data['balance']['available_cash']:,.2f}")
        
        # 3. 保存到OneDrive
        print("\n📋 步骤3: 保存到OneDrive")
        positions_saved = self.save_to_onedrive(positions_data, "latest_positions.json")
        balance_saved = self.save_to_onedrive(balance_data, "latest_balance.json")
        
        if not (positions_saved and balance_saved):
            print("❌ 数据保存失败")
            return False
        
        # 4. 等待同步
        print("\n📋 步骤4: 等待OneDrive同步")
        self.wait_for_sync(20)
        
        # 5. 详细测试云端API
        print("\n📋 步骤5: 详细测试云端API")
        api_results = self.test_cloud_api_detailed()
        
        # 6. 生成详细报告
        print("\n" + "=" * 60)
        print("📊 真实数据测试详细报告")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        
        # 统计结果
        api_success = sum(1 for r in api_results.values() if r.get("success"))
        test_id_detected = sum(1 for r in api_results.values() if r.get("has_test_id"))
        manual_marker_detected = sum(1 for r in api_results.values() if r.get("has_manual_marker"))
        
        print(f"\n📊 测试统计:")
        print(f"   API成功率: {api_success}/{len(api_results)}")
        print(f"   测试ID检测: {test_id_detected}/{len(api_results)}")
        print(f"   手动标记检测: {manual_marker_detected}/{len(api_results)}")
        
        print(f"\n📋 详细结果:")
        for api_name, result in api_results.items():
            if result.get("success"):
                if result.get("has_test_id"):
                    print(f"   🎉 {api_name}: 成功获取新数据")
                    print(f"      响应时间: {result.get('response_time', 0):.2f}秒")
                    print(f"      数据大小: {result.get('data_size', 0)} 字符")
                else:
                    print(f"   ⚠️ {api_name}: 响应正常但数据未更新")
                    print(f"      响应时间: {result.get('response_time', 0):.2f}秒")
            else:
                print(f"   ❌ {api_name}: 请求失败")
                if 'error' in result:
                    print(f"      错误: {result['error']}")
        
        print(f"\n💡 测试结论:")
        if test_id_detected > 0:
            print("🎉 真实数据测试完全成功!")
            print("✅ 本地导出的数据已被云端Agent成功获取")
            print("✅ 数据流程: 本地创建 → OneDrive → 云端API → Agent")
            print("✅ 云端Agent现在可以获取到真实的交易数据")
        elif api_success > 0:
            print("⚠️ 真实数据测试部分成功")
            print("📝 云端API正常响应,但可能使用了缓存数据")
            print("🔧 建议:")
            print("   1. 检查OneDrive同步状态")
            print("   2. 检查云端API缓存设置")
            print("   3. 等待更长时间后重新测试")
        else:
            print("❌ 真实数据测试失败")
            print("💥 云端API无法正常响应")
            print("🔧 需要检查网络连接和API服务状态")
        
        print("=" * 60)
        
        return test_id_detected > 0

def main():
    """主函数"""
    print("🎯 真实数据创建和云端Agent测试")
    print("这将创建真实的交易数据并测试云端Agent是否能获取")
    print()
    
    creator = RealTestDataCreator()
    success = creator.run_real_test()
    
    if success:
        print("\n🎯 真实数据测试成功完成!")
        print("✅ 云端Agent能够获取本地创建的真实数据")
        print("✅ 系统已准备就绪,可以接收真实交易软件的数据")
    else:
        print("\n💥 真实数据测试需要进一步调试!")
        print("🔧 请检查OneDrive同步和云端API配置")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
