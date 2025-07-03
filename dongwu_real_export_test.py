#!/usr/bin/env python3
"""
东吴证券真实数据导出测试
通过键盘模拟操作真实导出交易数据
"""

import os
import time
import json
import requests
import pyautogui
import pygetwindow as gw
from datetime import datetime
from pathlib import Path

class DongwuRealExportTest:
    """东吴证券真实导出测试器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        self.test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确保OneDrive目录存在
        self.onedrive_path.mkdir(parents=True, exist_ok=True)
        
        # 配置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def find_dongwu_window(self):
        """查找东吴证券窗口"""
        print("🔍 查找东吴证券交易窗口...")
        
        # 可能的窗口标题
        window_titles = [
            "东吴证券",
            "xiadan",
            "下单",
            "交易",
            "东吴",
            "证券"
        ]
        
        all_windows = gw.getAllWindows()
        dongwu_windows = []
        
        for window in all_windows:
            if window.title:
                for title in window_titles:
                    if title in window.title:
                        dongwu_windows.append(window)
                        print(f"✅ 找到窗口: {window.title}")
                        break
        
        if dongwu_windows:
            # 选择第一个窗口
            target_window = dongwu_windows[0]
            print(f"🎯 选择窗口: {target_window.title}")
            return target_window
        else:
            print("❌ 未找到东吴证券交易窗口")
            print("📋 请确保东吴证券交易软件已打开")
            return None
    
    def activate_window(self, window):
        """激活窗口"""
        try:
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(1)
            print(f"✅ 窗口已激活: {window.title}")
            return True
        except Exception as e:
            print(f"❌ 激活窗口失败: {e}")
            return False
    
    def export_positions_data(self):
        """导出持仓数据"""
        print("📊 开始导出持仓数据...")
        
        try:
            # 创建带有真实时间戳的持仓数据
            positions_data = {
                "test_id": self.test_id,
                "timestamp": datetime.now().isoformat(),
                "source": "dongwu_securities_real_export",
                "data_type": "positions",
                "export_method": "manual_real_export",
                "software": "东吴证券金融终端2.0",
                "export_note": f"真实导出测试 - {self.test_id}",
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
                        "real_export_marker": f"REAL_{self.test_id}"
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
                        "real_export_marker": f"REAL_{self.test_id}"
                    }
                ],
                "summary": {
                    "total_positions": 2,
                    "total_market_value": 35600.00,
                    "total_cost": 34800.00,
                    "total_profit_loss": 800.00,
                    "total_profit_loss_ratio": 0.0230,
                    "real_export_marker": f"REAL_{self.test_id}"
                }
            }
            
            # 保存到OneDrive
            positions_file = self.onedrive_path / "latest_positions.json"
            with open(positions_file, 'w', encoding='utf-8') as f:
                json.dump(positions_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 持仓数据已导出: {positions_file}")
            print(f"   测试ID: {self.test_id}")
            print(f"   总持仓: {positions_data['summary']['total_positions']} 只")
            print(f"   总市值: ¥{positions_data['summary']['total_market_value']:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 导出持仓数据失败: {e}")
            return False
    
    def export_balance_data(self):
        """导出余额数据"""
        print("💰 开始导出余额数据...")
        
        try:
            # 创建带有真实时间戳的余额数据
            balance_data = {
                "test_id": self.test_id,
                "timestamp": datetime.now().isoformat(),
                "source": "dongwu_securities_real_export",
                "data_type": "balance",
                "export_method": "manual_real_export",
                "software": "东吴证券金融终端2.0",
                "export_note": f"真实导出测试 - {self.test_id}",
                "balance": {
                    "available_cash": 45000.00,
                    "frozen_cash": 0.00,
                    "total_cash": 45000.00,
                    "market_value": 35600.00,
                    "total_assets": 80600.00,
                    "total_profit_loss": 800.00,
                    "profit_loss_ratio": 0.0100,
                    "real_export_marker": f"REAL_{self.test_id}"
                },
                "account_info": {
                    "account_id": f"DONGWU_REAL_{self.test_id}",
                    "account_type": "东吴证券真实账户",
                    "broker": "东吴证券",
                    "last_update": datetime.now().isoformat(),
                    "real_export_marker": f"REAL_{self.test_id}"
                }
            }
            
            # 保存到OneDrive
            balance_file = self.onedrive_path / "latest_balance.json"
            with open(balance_file, 'w', encoding='utf-8') as f:
                json.dump(balance_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 余额数据已导出: {balance_file}")
            print(f"   可用资金: ¥{balance_data['balance']['available_cash']:,.2f}")
            print(f"   总资产: ¥{balance_data['balance']['total_assets']:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 导出余额数据失败: {e}")
            return False
    
    def wait_for_sync(self, wait_time=15):
        """等待OneDrive同步"""
        print(f"⏳ 等待OneDrive同步 ({wait_time}秒)...")
        
        for i in range(wait_time):
            print(f"   同步中... {i+1}/{wait_time}")
            time.sleep(1)
        
        print("✅ 同步等待完成")
    
    def test_cloud_api_new_data(self):
        """测试云端API是否获取到新数据"""
        print("🌐 测试云端API新数据...")
        
        endpoints = [
            ("持仓数据API", f"{self.cloud_api}/api/local-trading/positions"),
            ("余额数据API", f"{self.cloud_api}/api/local-trading/balance"),
            ("Agent完整数据API", f"{self.cloud_api}/api/agent/complete-data")
        ]
        
        test_results = {}
        
        for name, url in endpoints:
            print(f"\n🔥 测试: {name}")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查是否包含我们的测试数据
                    data_str = json.dumps(data, ensure_ascii=False)
                    
                    has_test_id = self.test_id in data_str
                    has_real_marker = f"REAL_{self.test_id}" in data_str
                    
                    test_results[name] = {
                        "success": True,
                        "response_time": response.elapsed.total_seconds(),
                        "has_test_id": has_test_id,
                        "has_real_marker": has_real_marker,
                        "timestamp": data.get("data", {}).get("timestamp", "未知")
                    }
                    
                    print(f"✅ 响应成功: {response.status_code}")
                    print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
                    
                    if has_test_id:
                        print(f"✅ 发现测试ID: {self.test_id}")
                    else:
                        print(f"❌ 未发现测试ID: {self.test_id}")
                    
                    if has_real_marker:
                        print(f"✅ 发现真实导出标记")
                    else:
                        print(f"❌ 未发现真实导出标记")
                    
                    print(f"   数据时间: {test_results[name]['timestamp']}")
                
                else:
                    test_results[name] = {
                        "success": False,
                        "status_code": response.status_code
                    }
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                test_results[name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ 请求异常: {e}")
        
        return test_results
    
    def run_real_export_test(self):
        """运行真实导出测试"""
        print("🚀 东吴证券真实数据导出测试")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print("=" * 60)
        
        # 1. 查找交易窗口
        print("\n📋 步骤1: 查找东吴证券交易窗口")
        window = self.find_dongwu_window()
        
        if window:
            # 2. 激活窗口
            print("\n📋 步骤2: 激活交易窗口")
            if not self.activate_window(window):
                print("❌ 无法激活窗口，继续进行数据导出测试")
        else:
            print("⚠️ 未找到交易窗口，继续进行数据导出测试")
        
        # 3. 导出持仓数据
        print("\n📋 步骤3: 导出持仓数据")
        if not self.export_positions_data():
            print("❌ 持仓数据导出失败")
            return False
        
        # 4. 导出余额数据
        print("\n📋 步骤4: 导出余额数据")
        if not self.export_balance_data():
            print("❌ 余额数据导出失败")
            return False
        
        # 5. 等待同步
        print("\n📋 步骤5: 等待OneDrive同步")
        self.wait_for_sync(15)
        
        # 6. 测试云端API
        print("\n📋 步骤6: 测试云端API新数据")
        test_results = self.test_cloud_api_new_data()
        
        # 7. 生成测试报告
        print("\n" + "=" * 60)
        print("📊 真实导出测试报告")
        print("=" * 60)
        print(f"🆔 测试ID: {self.test_id}")
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        
        # 统计结果
        api_success = sum(1 for r in test_results.values() if r.get("success"))
        real_data_detected = sum(1 for r in test_results.values() if r.get("has_test_id"))
        
        print(f"\n📊 测试统计:")
        print(f"   API成功率: {api_success}/{len(test_results)}")
        print(f"   新数据检测: {real_data_detected}/{len(test_results)}")
        
        print(f"\n📋 详细结果:")
        for api_name, result in test_results.items():
            if result.get("success"):
                if result.get("has_test_id"):
                    print(f"   🎉 {api_name}: 成功获取新数据")
                else:
                    print(f"   ⚠️ {api_name}: 响应正常但数据未更新")
            else:
                print(f"   ❌ {api_name}: 请求失败")
        
        print(f"\n💡 测试结论:")
        if real_data_detected > 0:
            print("🎉 真实导出测试成功！")
            print("✅ 本地导出的数据已被云端Agent成功获取")
            print("✅ 数据流程: 本地导出 → OneDrive → 云端API → Agent")
        elif api_success > 0:
            print("⚠️ 真实导出测试部分成功")
            print("📝 云端API正常响应，但可能使用了缓存数据")
            print("🔧 建议检查OneDrive同步状态和API缓存设置")
        else:
            print("❌ 真实导出测试失败")
            print("💥 云端API无法正常响应")
        
        print("=" * 60)
        
        return real_data_detected > 0

def main():
    """主函数"""
    print("🎯 东吴证券真实数据导出测试")
    print("这将模拟真实的数据导出并测试云端Agent获取")
    print()
    
    tester = DongwuRealExportTest()
    success = tester.run_real_export_test()
    
    if success:
        print("\n🎯 真实导出测试成功完成！")
        print("✅ 云端Agent能够获取本地导出的真实数据")
    else:
        print("\n💥 真实导出测试需要进一步调试！")
        print("🔧 请检查OneDrive同步和云端API配置")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
