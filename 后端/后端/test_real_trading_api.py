#!/usr/bin/env python3
"""
测试真实交易API
验证Agent是否能获取真实的交易软件数据
"""

import requests
import json
import time

def test_trading_apis():
    """测试交易相关API"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试真实交易API...")
    print("="*60)
    
    # 1. 测试Agent系统初始化
    print("\n1️⃣ 测试Agent系统初始化...")
    try:
        response = requests.post(f"{base_url}/api/agent-trading/init")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   初始化结果: {data.get('status', 'unknown')}")
            print(f"   消息: {data.get('message', 'N/A')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 等待初始化完成
    time.sleep(2)
    
    # 2. 测试获取资金信息
    print("\n2️⃣ 测试获取资金信息...")
    try:
        response = requests.get(f"{base_url}/api/agent-trading/fund")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   API状态: {data.get('status', 'unknown')}")
            print(f"   消息: {data.get('message', 'N/A')}")
            
            if data.get('status') == 'success' and 'data' in data:
                fund_data = data['data']
                print(f"   📊 资金信息:")
                print(f"      总资产: ¥{fund_data.get('total_assets', 0):,.2f}")
                print(f"      可用资金: ¥{fund_data.get('available_cash', 0):,.2f}")
                print(f"      持仓市值: ¥{fund_data.get('market_value', 0):,.2f}")
                print(f"      冻结资金: ¥{fund_data.get('frozen_amount', 0):,.2f}")
            else:
                print(f"   ⚠️ 获取资金信息失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 3. 测试获取持仓信息
    print("\n3️⃣ 测试获取持仓信息...")
    try:
        response = requests.get(f"{base_url}/api/agent-trading/position")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   API状态: {data.get('status', 'unknown')}")
            print(f"   消息: {data.get('message', 'N/A')}")
            
            if data.get('status') == 'success' and 'data' in data:
                position_data = data['data']
                positions = position_data.get('positions', [])
                print(f"   📈 持仓信息:")
                print(f"      持仓数量: {len(positions)} 只股票")
                
                if positions:
                    for i, pos in enumerate(positions[:5]):  # 只显示前5只
                        print(f"      {i+1}. {pos.get('name', 'N/A')} ({pos.get('symbol', 'N/A')})")
                        print(f"         数量: {pos.get('volume', 0)} 股")
                        print(f"         成本价: ¥{pos.get('cost_price', 0):.2f}")
                        print(f"         现价: ¥{pos.get('current_price', 0):.2f}")
                        print(f"         市值: ¥{pos.get('market_value', 0):,.2f}")
                        print(f"         盈亏: ¥{pos.get('profit_loss', 0):,.2f}")
                else:
                    print("      📝 当前无持仓")
            else:
                print(f"   ⚠️ 获取持仓信息失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    # 4. 测试系统状态
    print("\n4️⃣ 测试系统状态...")
    try:
        response = requests.get(f"{base_url}/api/agent-trading/status")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   系统状态: {data.get('status', 'unknown')}")
            
            if 'data' in data:
                status_data = data['data']
                print(f"   📊 系统信息:")
                print(f"      Agent活跃: {status_data.get('active', False)}")
                print(f"      自动交易: {status_data.get('auto_trading_enabled', False)}")
                print(f"      今日交易次数: {status_data.get('daily_trade_count', 0)}")
                print(f"      交易窗口连接: {status_data.get('trading_window_found', False)}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   异常: {str(e)}")
    
    print("\n" + "="*60)
    print("🎯 测试总结:")
    print("✅ 如果上面的API都返回了真实数据,说明Agent可以获取交易软件数据")
    print("📱 移动端现在应该能显示真实的账户和持仓信息")
    print("🔄 如果API返回错误,请检查:")
    print("   1. 后端服务是否正常运行")
    print("   2. 交易软件是否已打开")
    print("   3. Agent系统是否正确初始化")
    print("   4. fixed_balance_reader.py 和 trader_export_real.py 是否可用")
    print("\n💡 重要提示:")
    print("   现在Agent会调用真实的交易软件获取数据:")
    print("   - 资金信息: 调用 fixed_balance_reader.get_balance_fixed()")
    print("   - 持仓信息: 调用 trader_export_real.export_holdings() 并解析CSV文件")
    print("   - 这些都是真实的交易软件数据,不再是模拟数据!")

if __name__ == "__main__":
    test_trading_apis()
