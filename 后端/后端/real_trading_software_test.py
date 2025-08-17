#!/usr/bin/env python3
"""
真实交易软件测试
检查交易软件状态并进行真实数据导出测试
"""

import os
import time
import json
import psutil
import requests
from datetime import datetime
from pathlib import Path

class RealTradingSoftwareTest:
    """真实交易软件测试器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.cloud_api = "https://api.aigupiao.me"
        
    def check_trading_software_running(self):
        """检查交易软件是否运行"""
        print("🔍 检查交易软件运行状态...")
        
        # 常见交易软件进程名
        trading_processes = [
            "xiadan.exe",      # 下单软件
            "trade.exe",       # 交易软件
            "client.exe",      # 客户端
            "trading.exe",     # 交易程序
            "stock.exe",       # 股票软件
            "broker.exe",      # 券商软件
            "eastmoney.exe",   # 东方财富
            "tonghuashun.exe", # 同花顺
            "great.exe",       # 大智慧
            "zd.exe",          # 招商证券
            "gtja.exe",        # 国泰君安
        ]
        
        running_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                for trading_proc in trading_processes:
                    if trading_proc.lower() in proc_name:
                        running_processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'exe': proc.info['exe']
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if running_processes:
            print("✅ 发现运行中的交易软件:")
            for proc in running_processes:
                print(f"   📊 {proc['name']} (PID: {proc['pid']})")
                if proc['exe']:
                    print(f"      路径: {proc['exe']}")
            return True, running_processes
        else:
            print("❌ 未发现运行中的交易软件")
            print("📋 请确保以下之一正在运行:")
            for proc_name in trading_processes[:5]:  # 显示前5个常见的
                print(f"   • {proc_name}")
            return False, []
    
    def check_existing_export_files(self):
        """检查现有的导出文件"""
        print("\n📁 检查现有导出文件...")
        
        files_to_check = [
            "latest_positions.json",
            "latest_balance.json"
        ]
        
        existing_files = {}
        
        for filename in files_to_check:
            file_path = self.onedrive_path / filename
            
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    existing_files[filename] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "timestamp": data.get("timestamp", "未知"),
                        "source": data.get("source", "未知"),
                        "data_type": data.get("data_type", "未知")
                    }
                    
                    print(f"✅ {filename}")
                    print(f"   修改时间: {existing_files[filename]['modified']}")
                    print(f"   数据时间: {existing_files[filename]['timestamp']}")
                    print(f"   数据来源: {existing_files[filename]['source']}")
                    print(f"   文件大小: {existing_files[filename]['size']} 字节")
                    
                except Exception as e:
                    existing_files[filename] = {
                        "exists": True,
                        "error": str(e)
                    }
                    print(f"❌ {filename}: 读取错误 - {e}")
            else:
                existing_files[filename] = {"exists": False}
                print(f"❌ {filename}: 文件不存在")
        
        return existing_files
    
    def test_cloud_api_current_data(self):
        """测试云端API当前数据"""
        print("\n🌐 测试云端API当前数据...")
        
        endpoints = [
            ("持仓数据API", f"{self.cloud_api}/api/local-trading/positions"),
            ("余额数据API", f"{self.cloud_api}/api/local-trading/balance"),
            ("Agent完整数据API", f"{self.cloud_api}/api/agent/complete-data")
        ]
        
        api_results = {}
        
        for name, url in endpoints:
            print(f"\n🔥 测试: {name}")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    api_results[name] = {
                        "success": True,
                        "status_code": 200,
                        "response_time": response.elapsed.total_seconds(),
                        "data": data
                    }
                    
                    print(f"✅ 响应成功: {response.status_code}")
                    print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
                    
                    # 分析响应数据
                    if 'data' in data:
                        response_data = data['data']
                        
                        if 'timestamp' in response_data:
                            print(f"   数据时间: {response_data['timestamp']}")
                        
                        if 'source' in response_data:
                            print(f"   数据来源: {response_data['source']}")
                        
                        if 'api_source' in response_data:
                            print(f"   API来源: {response_data['api_source']}")
                        
                        # 特定数据分析
                        if 'positions' in response_data:
                            positions = response_data['positions']
                            print(f"   持仓数量: {len(positions)} 只")
                        
                        if 'balance' in response_data:
                            balance = response_data['balance']
                            total_assets = balance.get('total_assets', 0)
                            print(f"   总资产: ¥{total_assets:,.2f}")
                        
                        if 'trading_data' in response_data:
                            trading_data = response_data['trading_data']
                            print(f"   交易数据: 包含持仓和余额信息")
                
                else:
                    api_results[name] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                api_results[name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ 请求异常: {e}")
        
        return api_results
    
    def provide_real_export_guidance(self):
        """提供真实导出指导"""
        print("\n" + "=" * 60)
        print("📋 真实交易软件数据导出指导")
        print("=" * 60)
        
        print("\n🎯 要进行真实测试,请按以下步骤操作:")
        
        print("\n📋 步骤1: 启动交易软件")
        print("   1. 打开您的交易软件")
        print("   2. 登录您的交易账户")
        print("   3. 确保能看到持仓和余额信息")
        
        print("\n📋 步骤2: 配置导出路径")
        print("   1. 在交易软件中找到数据导出功能")
        print("   2. 将导出路径设置为: C:/mnt/onedrive/TradingData/")
        print("   3. 或者导出到其他位置后复制到OneDrive目录")
        
        print("\n📋 步骤3: 导出数据")
        print("   1. 导出持仓数据 → latest_positions.json")
        print("   2. 导出余额数据 → latest_balance.json")
        print("   3. 确保文件格式为JSON")
        
        print("\n📋 步骤4: 验证导出")
        print("   1. 检查文件是否存在于OneDrive目录")
        print("   2. 运行本测试脚本验证")
        print("   3. 测试云端API是否能读取新数据")
        
        print("\n🔧 如果交易软件不支持直接导出JSON:")
        print("   1. 导出为CSV或TXT格式")
        print("   2. 使用转换脚本转为JSON格式")
        print("   3. 或手动创建JSON文件进行测试")
        
        print("=" * 60)
    
    def run_real_test(self):
        """运行真实测试"""
        print("🚀 真实交易软件数据导出测试")
        print("=" * 60)
        
        # 1. 检查交易软件状态
        print("📋 步骤1: 检查交易软件状态")
        software_running, processes = self.check_trading_software_running()
        
        # 2. 检查现有文件
        print("\n📋 步骤2: 检查现有导出文件")
        existing_files = self.check_existing_export_files()
        
        # 3. 测试云端API
        print("\n📋 步骤3: 测试云端API当前数据")
        api_results = self.test_cloud_api_current_data()
        
        # 4. 生成测试报告
        print("\n" + "=" * 60)
        print("📊 真实测试状态报告")
        print("=" * 60)
        
        print(f"⏰ 测试时间: {datetime.now().isoformat()}")
        
        print(f"\n🖥️ 交易软件状态:")
        if software_running:
            print(f"   ✅ 发现 {len(processes)} 个交易相关进程")
            print("   📋 可以进行真实数据导出")
        else:
            print("   ❌ 未发现交易软件运行")
            print("   📋 需要先启动交易软件")
        
        print(f"\n📁 导出文件状态:")
        file_count = sum(1 for f in existing_files.values() if f.get("exists"))
        print(f"   📊 现有文件: {file_count}/2")
        
        for filename, info in existing_files.items():
            if info.get("exists"):
                if "error" not in info:
                    age = datetime.now() - info["modified"]
                    print(f"   ✅ {filename}: {age.total_seconds()/60:.1f}分钟前")
                else:
                    print(f"   ❌ {filename}: 读取错误")
            else:
                print(f"   ❌ {filename}: 不存在")
        
        print(f"\n🌐 云端API状态:")
        api_success = sum(1 for r in api_results.values() if r.get("success"))
        print(f"   📊 API成功率: {api_success}/{len(api_results)}")
        
        for api_name, result in api_results.items():
            if result.get("success"):
                print(f"   ✅ {api_name}: 正常")
            else:
                print(f"   ❌ {api_name}: 失败")
        
        # 5. 提供指导
        if not software_running:
            self.provide_real_export_guidance()
        else:
            print(f"\n🎯 下一步操作:")
            print("   1. 在交易软件中导出最新数据")
            print("   2. 重新运行此测试验证")
            print("   3. 检查云端API是否获取到新数据")
        
        return {
            "software_running": software_running,
            "files_exist": file_count > 0,
            "api_working": api_success > 0
        }

def main():
    """主函数"""
    print("🔍 真实交易软件数据导出测试")
    print("这将检查真实的交易软件状态和数据导出情况")
    print()
    
    tester = RealTradingSoftwareTest()
    results = tester.run_real_test()
    
    print(f"\n📊 测试总结:")
    if results["software_running"] and results["api_working"]:
        print("🎉 系统准备就绪,可以进行真实数据导出测试!")
    elif results["api_working"]:
        print("⚠️ 云端API正常,但需要启动交易软件进行真实导出")
    else:
        print("💥 需要检查交易软件和云端API状态")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
