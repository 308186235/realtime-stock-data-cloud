#!/usr/bin/env python3
"""
测试简化的OneDrive方案
"""

import os
import json
import requests
from datetime import datetime

def test_local_onedrive_save():
    """测试本地保存到OneDrive文件夹"""
    print("🔧 测试本地保存到OneDrive文件夹")
    print("=" * 50)
    
    # 模拟OneDrive路径
    possible_paths = [
        os.path.expanduser("~/OneDrive/TradingData"),
        os.path.expanduser("~/OneDrive - Personal/TradingData"),
        "C:/Users/{}/OneDrive/TradingData".format(os.getenv('USERNAME', 'User')),
        "./OneDrive_TradingData"  # 备用路径
    ]
    
    onedrive_path = None
    for path in possible_paths:
        parent_dir = os.path.dirname(path)
        if os.path.exists(parent_dir) or path.startswith('./'):
            os.makedirs(path, exist_ok=True)
            onedrive_path = path
            print(f"✅ 使用OneDrive路径: {path}")
            break
    
    if not onedrive_path:
        print("❌ 无法找到或创建OneDrive路径")
        return False
    
    # 测试数据
    test_data = {
        "positions": {
            "data_type": "positions",
            "timestamp": datetime.now().isoformat(),
            "source": "local_computer",
            "data": {
                "positions": [
                    {
                        "stock_code": "000001",
                        "stock_name": "平安银行",
                        "quantity": 1000,
                        "current_price": 13.50,
                        "market_value": 13500
                    }
                ],
                "summary": {
                    "total_market_value": 13500
                }
            }
        },
        "balance": {
            "data_type": "balance",
            "timestamp": datetime.now().isoformat(),
            "source": "local_computer",
            "data": {
                "balance": {
                    "total_assets": 125680.5,
                    "available_cash": 23450.8,
                    "market_value": 102229.7,
                    "frozen_amount": 0
                }
            }
        }
    }
    
    # 保存测试文件
    success_count = 0
    for data_type, data in test_data.items():
        filename = f"latest_{data_type}.json"
        file_path = os.path.join(onedrive_path, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 保存成功: {filename}")
            success_count += 1
            
            # 验证文件
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   📊 文件大小: {file_size} 字节")
            
        except Exception as e:
            print(f"❌ 保存失败 {filename}: {e}")
    
    print(f"\n📊 保存结果: {success_count}/{len(test_data)} 成功")
    return success_count == len(test_data)

def test_cloud_worker_access():
    """测试云端Worker访问"""
    print("\n🔧 测试云端Worker访问OneDrive数据")
    print("=" * 50)
    
    # 测试端点
    endpoints = [
        {
            "name": "持仓数据",
            "url": "https://api.aigupiao.me/api/local-trading/positions"
        },
        {
            "name": "余额数据", 
            "url": "https://api.aigupiao.me/api/local-trading/balance"
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
                
                if data.get("success"):
                    print("   ✅ 请求成功")
                    
                    data_content = data.get("data", {})
                    source = data_content.get("source", "unknown")
                    
                    print(f"   📊 数据源: {source}")
                    
                    if source == "local_computer_via_onedrive":
                        print("   🎉 成功通过OneDrive获取本地数据!")
                        success_count += 1
                    elif source == "local_computer_via_supabase":
                        print("   ⚠️ 使用Supabase备用数据")
                    elif source.startswith("backup"):
                        print("   ⚠️ 使用备用数据")
                    else:
                        print(f"   ❓ 未知数据源: {source}")
                    
                    # 显示数据摘要
                    if "positions" in data_content:
                        positions = data_content.get("positions", [])
                        print(f"   📈 持仓: {len(positions)} 只股票")
                    
                    if "balance" in data_content:
                        balance = data_content.get("balance", {})
                        total_assets = balance.get("total_assets", 0)
                        print(f"   💰 总资产: {total_assets}")
                    
                else:
                    print(f"   ❌ 请求失败: {data.get('error', '未知错误')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    print(f"\n📊 访问结果: {success_count}/{len(endpoints)} 通过OneDrive获取")
    return success_count

def check_onedrive_status():
    """检查OneDrive状态"""
    print("\n🔧 检查OneDrive状态")
    print("-" * 30)
    
    # 检查OneDrive进程
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq OneDrive.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'OneDrive.exe' in result.stdout:
            print("✅ OneDrive客户端正在运行")
        else:
            print("⚠️ OneDrive客户端未运行")
    except:
        print("❓ 无法检查OneDrive进程状态")
    
    # 检查OneDrive文件夹
    onedrive_paths = [
        os.path.expanduser("~/OneDrive"),
        os.path.expanduser("~/OneDrive - Personal"),
        "C:/Users/{}/OneDrive".format(os.getenv('USERNAME', 'User'))
    ]
    
    for path in onedrive_paths:
        if os.path.exists(path):
            print(f"✅ 找到OneDrive文件夹: {path}")
            
            # 检查TradingData文件夹
            trading_data_path = os.path.join(path, "TradingData")
            if os.path.exists(trading_data_path):
                print(f"✅ TradingData文件夹存在")
                
                # 列出文件
                try:
                    files = os.listdir(trading_data_path)
                    print(f"   📁 文件: {files}")
                except:
                    print("   ❌ 无法读取文件列表")
            else:
                print(f"⚠️ TradingData文件夹不存在")
            break
    else:
        print("❌ 未找到OneDrive文件夹")

def main():
    """主函数"""
    print("🎯 OneDrive简化方案测试")
    print("=" * 60)
    
    # 1. 检查OneDrive状态
    check_onedrive_status()
    
    # 2. 测试本地保存
    local_success = test_local_onedrive_save()
    
    # 3. 测试云端访问
    cloud_success = test_cloud_worker_access()
    
    # 4. 总结
    print(f"\n{'='*60}")
    print(f"🎯 测试总结")
    print(f"{'='*60}")
    
    if local_success:
        print("✅ 本地保存到OneDrive: 成功")
    else:
        print("❌ 本地保存到OneDrive: 失败")
    
    if cloud_success > 0:
        print(f"✅ 云端通过OneDrive获取数据: {cloud_success} 个端点成功")
    else:
        print("❌ 云端通过OneDrive获取数据: 失败")
    
    if local_success and cloud_success > 0:
        print("\n🎉 OneDrive方案基本可行！")
        print("📝 下一步:")
        print("1. 配置Microsoft Graph API凭证")
        print("2. 确保OneDrive正常同步")
        print("3. 运行本地交易服务器进行实际测试")
    else:
        print("\n⚠️ OneDrive方案需要进一步配置")
        print("📝 建议:")
        print("1. 检查OneDrive客户端是否正常运行")
        print("2. 确认OneDrive文件夹路径")
        print("3. 配置Microsoft Graph API")

if __name__ == "__main__":
    main()
