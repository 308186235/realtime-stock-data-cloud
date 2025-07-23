#!/usr/bin/env python3
"""
测试虚拟账户API
"""

import requests
import json

def test_virtual_account_api():
    """测试虚拟账户API"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试虚拟账户API...")
    
    # 测试获取虚拟账户列表
    try:
        response = requests.get(f"{base_url}/api/virtual-account/accounts")
        print(f"📋 获取账户列表: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   账户数量: {len(data)}")
            if data:
                print(f"   第一个账户: {data[0].get('account_name', 'N/A')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 测试获取账户详情
    try:
        response = requests.get(f"{base_url}/api/virtual-account/accounts/1")
        print(f"📊 获取账户详情: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                account = data["data"]
                print(f"   账户名: {account.get('account_name', 'N/A')}")
                print(f"   总资产: {account.get('total_assets', 0)}")
                print(f"   可用资金: {account.get('available_cash', 0)}")
                print(f"   持仓市值: {account.get('market_value', 0)}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 测试获取持仓列表
    try:
        response = requests.get(f"{base_url}/api/virtual-account/accounts/1/positions")
        print(f"📈 获取持仓列表: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                positions = data["data"]
                print(f"   持仓数量: {len(positions)}")
                if positions:
                    print(f"   第一只股票: {positions[0].get('name', 'N/A')} ({positions[0].get('symbol', 'N/A')})")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")

def create_mock_data():
    """创建模拟数据用于测试"""
    print("🔧 创建模拟数据...")
    
    # 这里可以直接插入数据库或调用API创建
    mock_account = {
        "account_name": "东吴秀才",
        "broker_type": "dongwu_xiucai",
        "total_assets": 120000.00,
        "available_cash": 80000.00
    }
    
    try:
        response = requests.post("http://localhost:8000/api/virtual-account/accounts", 
                               json=mock_account)
        print(f"创建账户: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   账户创建成功: {data.get('data', {}).get('account_name', 'N/A')}")
            else:
                print(f"   创建失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试虚拟账户系统...")
    
    # 首先尝试创建模拟数据
    create_mock_data()
    
    print("\n" + "="*50 + "\n")
    
    # 然后测试API
    test_virtual_account_api()
    
    print("\n✅ 测试完成!")
    print("\n💡 如果API正常工作,移动端应该能显示真实数据")
    print("📱 请检查移动端交易页面的账户信息是否已更新")
