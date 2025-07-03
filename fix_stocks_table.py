#!/usr/bin/env python3
"""
修复stocks表并添加基础数据
"""

import requests
import json
from datetime import datetime

# Supabase配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

def add_basic_stocks():
    """添加基础股票数据"""
    print("🔧 添加基础股票数据...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    # 基础股票数据
    stocks_data = [
        {
            'code': 'sz000001',
            'name': '平安银行',
            'current_price': 0,
            'volume': 0,
            'change_percent': 0,
            'last_updated': datetime.now().isoformat()
        },
        {
            'code': 'sh600519',
            'name': '贵州茅台',
            'current_price': 0,
            'volume': 0,
            'change_percent': 0,
            'last_updated': datetime.now().isoformat()
        },
        {
            'code': 'sz300750',
            'name': '宁德时代',
            'current_price': 0,
            'volume': 0,
            'change_percent': 0,
            'last_updated': datetime.now().isoformat()
        },
        {
            'code': 'sz002415',
            'name': '海康威视',
            'current_price': 0,
            'volume': 0,
            'change_percent': 0,
            'last_updated': datetime.now().isoformat()
        },
        {
            'code': 'sh688599',
            'name': '天合光能',
            'current_price': 0,
            'volume': 0,
            'change_percent': 0,
            'last_updated': datetime.now().isoformat()
        }
    ]
    
    try:
        response = requests.post(f'{SUPABASE_URL}/rest/v1/stocks', 
                               headers=headers, json=stocks_data)
        
        if response.status_code in [200, 201]:
            print(f"✅ 成功添加 {len(stocks_data)} 条股票基础数据")
            return True
        else:
            print(f"❌ 添加失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 添加异常: {e}")
        return False

def test_api_and_sync():
    """测试API并同步数据"""
    print("\n🔄 测试API并同步数据...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    try:
        # 获取API数据
        api_response = requests.get('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001')
        if api_response.status_code != 200:
            print("❌ API请求失败")
            return False
            
        api_data = api_response.json()
        stock = api_data.get('data', [{}])[0]
        
        print(f"✅ 获取API数据: {stock.get('stock_code')} - {stock.get('current_price')}")
        
        # 更新数据库
        update_data = {
            'current_price': float(stock.get('current_price', 0)),
            'volume': int(stock.get('volume', 0)),
            'change_percent': float(stock.get('change_percent', 0)),
            'last_updated': datetime.now().isoformat()
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/stocks?code=eq.sz000001',
            headers=headers,
            json=update_data
        )
        
        if response.status_code in [200, 204]:
            print("✅ 数据库更新成功")
            return True
        else:
            print(f"❌ 数据库更新失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def verify_data():
    """验证数据"""
    print("\n📊 验证数据...")
    
    headers = {
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    try:
        response = requests.get(f'{SUPABASE_URL}/rest/v1/stocks?select=*', headers=headers)
        if response.status_code == 200:
            stocks = response.json()
            print(f"✅ 数据库中有 {len(stocks)} 条股票记录")
            
            for stock in stocks:
                print(f"  📈 {stock.get('code')}: {stock.get('name')} - {stock.get('current_price')}")
            
            return len(stocks) > 0
        else:
            print(f"❌ 验证失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 修复stocks表并测试数据同步...")
    print("=" * 50)
    
    # 添加基础数据
    add_success = add_basic_stocks()
    
    # 测试API同步
    sync_success = test_api_and_sync()
    
    # 验证数据
    verify_success = verify_data()
    
    print("\n" + "=" * 50)
    print("📋 修复结果总结:")
    print(f"基础数据添加: {'✅ 成功' if add_success else '❌ 失败'}")
    print(f"API数据同步: {'✅ 成功' if sync_success else '❌ 失败'}")
    print(f"数据验证: {'✅ 成功' if verify_success else '❌ 失败'}")
    
    if all([add_success, sync_success, verify_success]):
        print("🎉 stocks表修复完成！数据同步正常！")
    else:
        print("🔧 需要进一步检查和修复")

if __name__ == '__main__':
    main()
