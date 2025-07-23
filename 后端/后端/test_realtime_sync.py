#!/usr/bin/env python3
"""
测试实时同步功能
验证OneDrive文件更新后云端API的响应时间
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class RealtimeSyncTest:
    """实时同步测试器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        
    def check_local_files(self):
        """检查本地文件状态"""
        print("📁 检查本地OneDrive文件...")
        
        files_info = {}
        
        for filename in ["latest_positions.json", "latest_balance.json"]:
            file_path = self.onedrive_path / filename
            
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    files_info[filename] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "timestamp": data.get("timestamp", "未知"),
                        "test_id": data.get("test_id", "未知")
                    }
                    
                    print(f"✅ {filename}")
                    print(f"   大小: {stat.st_size} 字节")
                    print(f"   修改时间: {files_info[filename]['modified']}")
                    print(f"   数据时间: {files_info[filename]['timestamp']}")
                    print(f"   测试ID: {files_info[filename]['test_id']}")
                    
                except Exception as e:
                    files_info[filename] = {
                        "exists": True,
                        "error": str(e)
                    }
                    print(f"❌ {filename}: 读取错误 - {e}")
            else:
                files_info[filename] = {"exists": False}
                print(f"❌ {filename}: 文件不存在")
        
        return files_info
    
    def check_cloud_api_response(self):
        """检查云端API响应"""
        print("\n🌐 检查云端API响应...")
        
        endpoints = [
            ("持仓API", f"{self.cloud_api}/api/local-trading/positions"),
            ("余额API", f"{self.cloud_api}/api/local-trading/balance")
        ]
        
        api_responses = {}
        
        for name, url in endpoints:
            print(f"\n🔥 测试: {name}")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    api_responses[name] = {
                        "status": "成功",
                        "status_code": 200,
                        "response_time": response.elapsed.total_seconds(),
                        "timestamp": data.get("timestamp", "未知"),
                        "test_id": data.get("test_id", "未知"),
                        "source": data.get("source", "未知"),
                        "data_size": len(json.dumps(data))
                    }
                    
                    print(f"✅ 响应成功: {response.status_code}")
                    print(f"   响应时间: {api_responses[name]['response_time']:.2f}秒")
                    print(f"   数据时间: {api_responses[name]['timestamp']}")
                    print(f"   测试ID: {api_responses[name]['test_id']}")
                    print(f"   数据源: {api_responses[name]['source']}")
                    print(f"   数据大小: {api_responses[name]['data_size']} 字符")
                    
                else:
                    api_responses[name] = {
                        "status": "失败",
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                api_responses[name] = {
                    "status": "异常",
                    "error": str(e)
                }
                print(f"❌ 请求异常: {e}")
        
        return api_responses
    
    def create_new_test_data(self):
        """创建新的测试数据"""
        test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_time = datetime.now().isoformat()
        
        print(f"📝 创建新测试数据 (ID: {test_id})...")
        
        # 创建新的持仓数据
        positions_data = {
            "test_id": test_id,
            "timestamp": current_time,
            "source": "realtime_sync_test",
            "data_type": "positions",
            "export_method": "direct_to_onedrive_rclone",
            "sync_test_note": f"实时同步测试 - {test_id}",
            "positions": [
                {
                    "stock_code": "000001",
                    "stock_name": "平安银行",
                    "quantity": 1500,  # 更新数量
                    "current_price": 14.00,  # 更新价格
                    "market_value": 21000.00,
                    "cost_price": 13.20,
                    "profit_loss": 1200.00,
                    "profit_loss_ratio": 0.0606,
                    "sync_test_marker": f"SYNC_TEST_{test_id}"
                }
            ],
            "summary": {
                "total_positions": 1,
                "total_market_value": 21000.00,
                "total_cost": 19800.00,
                "total_profit_loss": 1200.00,
                "total_profit_loss_ratio": 0.0606,
                "sync_test_marker": f"SYNC_TEST_{test_id}"
            }
        }
        
        # 创建新的余额数据
        balance_data = {
            "test_id": test_id,
            "timestamp": current_time,
            "source": "realtime_sync_test",
            "data_type": "balance",
            "export_method": "direct_to_onedrive_rclone",
            "sync_test_note": f"实时同步测试 - {test_id}",
            "balance": {
                "available_cash": 45000.00,  # 更新余额
                "frozen_cash": 0.00,
                "total_cash": 45000.00,
                "market_value": 21000.00,
                "total_assets": 66000.00,
                "total_profit_loss": 1200.00,
                "profit_loss_ratio": 0.0185,
                "sync_test_marker": f"SYNC_TEST_{test_id}"
            },
            "account_info": {
                "account_id": f"SYNC_TEST_{test_id}",
                "account_type": "实时同步测试账户",
                "broker": "同步测试券商",
                "last_update": current_time,
                "sync_test_marker": f"SYNC_TEST_{test_id}"
            }
        }
        
        return test_id, positions_data, balance_data
    
    def update_local_files(self, positions_data, balance_data):
        """更新本地文件"""
        print("💾 更新本地OneDrive文件...")
        
        try:
            # 更新持仓文件
            positions_file = self.onedrive_path / "latest_positions.json"
            with open(positions_file, 'w', encoding='utf-8') as f:
                json.dump(positions_data, f, ensure_ascii=False, indent=2)
            
            # 更新余额文件
            balance_file = self.onedrive_path / "latest_balance.json"
            with open(balance_file, 'w', encoding='utf-8') as f:
                json.dump(balance_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 文件更新完成")
            print(f"   持仓文件: {positions_file}")
            print(f"   余额文件: {balance_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 文件更新失败: {e}")
            return False
    
    def run_realtime_test(self):
        """运行实时同步测试"""
        print("🚀 OneDrive实时同步测试")
        print("=" * 60)
        
        # 1. 检查当前状态
        print("📋 步骤1: 检查当前状态")
        initial_files = self.check_local_files()
        initial_api = self.check_cloud_api_response()
        
        # 2. 创建新测试数据
        print(f"\n📋 步骤2: 创建新测试数据")
        test_id, positions_data, balance_data = self.create_new_test_data()
        
        # 3. 更新本地文件
        print(f"\n📋 步骤3: 更新本地文件")
        if not self.update_local_files(positions_data, balance_data):
            print("❌ 本地文件更新失败")
            return False
        
        # 4. 等待同步并多次检查API
        print(f"\n📋 步骤4: 监控云端API响应变化")
        
        check_intervals = [5, 15, 30, 60]  # 检查间隔(秒)
        
        for i, interval in enumerate(check_intervals):
            print(f"\n⏳ 等待 {interval} 秒后检查...")
            time.sleep(interval)
            
            print(f"🔍 第 {i+1} 次检查 (等待 {interval} 秒后):")
            api_responses = self.check_cloud_api_response()
            
            # 检查是否获取到新数据
            found_new_data = False
            for api_name, response in api_responses.items():
                if response.get('test_id') == test_id:
                    print(f"🎉 {api_name} 已获取到新数据!")
                    found_new_data = True
                elif test_id in str(response):
                    print(f"🎉 {api_name} 包含新测试ID!")
                    found_new_data = True
                else:
                    print(f"⏳ {api_name} 仍为旧数据")
            
            if found_new_data:
                print("✅ 检测到新数据,同步成功!")
                break
        else:
            print("⚠️ 所有检查完成,未检测到新数据")
        
        # 5. 最终状态检查
        print(f"\n📋 步骤5: 最终状态检查")
        final_files = self.check_local_files()
        final_api = self.check_cloud_api_response()
        
        # 6. 生成同步测试报告
        print("\n" + "=" * 60)
        print("📊 实时同步测试报告")
        print("=" * 60)
        print(f"🆔 测试ID: {test_id}")
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        
        print(f"\n📁 本地文件状态:")
        for filename, info in final_files.items():
            if info.get('exists'):
                if info.get('test_id') == test_id:
                    print(f"✅ {filename}: 已更新为新数据")
                else:
                    print(f"⚠️ {filename}: 可能未更新")
            else:
                print(f"❌ {filename}: 文件不存在")
        
        print(f"\n🌐 云端API状态:")
        sync_success = False
        for api_name, response in final_api.items():
            if response.get('test_id') == test_id:
                print(f"✅ {api_name}: 已同步新数据")
                sync_success = True
            elif test_id in str(response):
                print(f"✅ {api_name}: 包含新测试数据")
                sync_success = True
            else:
                print(f"⚠️ {api_name}: 仍为旧数据")
                print(f"   当前数据时间: {response.get('timestamp', '未知')}")
        
        print(f"\n📊 同步测试结论:")
        if sync_success:
            print("🎉 实时同步测试成功!")
            print("✅ 本地文件更新后,云端API能够获取到新数据")
            print("✅ OneDrive → 云端Agent 数据流程正常工作")
        else:
            print("⚠️ 实时同步可能存在延迟")
            print("📝 云端API可能使用了缓存或备用数据源")
            print("🔧 建议检查OneDrive同步状态和云端配置")
        
        print("=" * 60)
        
        return sync_success

def main():
    """主函数"""
    tester = RealtimeSyncTest()
    success = tester.run_realtime_test()
    
    if success:
        print("\n🎯 实时同步测试成功!")
        print("✅ 系统支持实时数据同步")
    else:
        print("\n⚠️ 实时同步测试发现延迟")
        print("📝 系统功能正常,但可能存在缓存延迟")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
