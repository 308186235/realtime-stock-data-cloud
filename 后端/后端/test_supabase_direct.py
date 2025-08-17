#!/usr/bin/env python3
"""
直接测试Supabase连接和数据操作
"""

import requests
import json
from datetime import datetime

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://process.env.SUPABASE_URL',
    'anon_key': 'process.env.SUPABASE_ANON_KEY
    'service_key': 'process.env.SUPABASE_ANON_KEY
}

def test_supabase_connection():
    """测试Supabase连接"""
    print("🔧 测试Supabase连接")
    print("=" * 50)
    
    headers = {
        'apikey': SUPABASE_CONFIG['service_key'],
        'Authorization': f"Bearer {SUPABASE_CONFIG['service_key']}",
        'Content-Type': 'application/json'
    }
    
    # 1. 测试基本连接
    print("\n📊 1. 测试基本连接")
    try:
        response = requests.get(
            f"{SUPABASE_CONFIG['url']}/rest/v1/",
            headers=headers,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ Supabase连接成功")
        else:
            print(f"⚠️ 连接响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    # 2. 查看现有表
    print("\n📊 2. 查看现有表")
    try:
        # 尝试查看一些可能存在的表
        tables_to_check = ['users', 'profiles', 'posts', 'trading_data', 'stock_data']
        
        for table in tables_to_check:
            try:
                response = requests.get(
                    f"{SUPABASE_CONFIG['url']}/rest/v1/{table}",
                    params={'limit': 1},
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"✅ 表 '{table}' 存在")
                elif response.status_code == 404:
                    print(f"❌ 表 '{table}' 不存在")
                else:
                    print(f"⚠️ 表 '{table}' 状态: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 检查表 '{table}' 失败: {e}")
                
    except Exception as e:
        print(f"❌ 查看表失败: {e}")
    
    # 3. 尝试使用现有表存储数据
    print("\n📊 3. 尝试创建简单数据存储")
    
    # 使用profiles表或创建简单的键值存储
    test_data = {
        'id': 'trading_positions',
        'data': json.dumps({
            'positions': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'quantity': 1000,
                    'current_price': 13.50,
                    'market_value': 13500
                }
            ],
            'timestamp': datetime.now().isoformat()
        })
    }
    
    # 尝试不同的表结构
    simple_tables = ['profiles', 'users']
    
    for table in simple_tables:
        try:
            response = requests.post(
                f"{SUPABASE_CONFIG['url']}/rest/v1/{table}",
                json=test_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ 成功在表 '{table}' 中存储数据")
                break
            else:
                print(f"❌ 表 '{table}' 存储失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 表 '{table}' 存储异常: {e}")

def create_simple_storage():
    """创建简单的键值存储方案"""
    print("\n🔧 创建简单存储方案")
    print("-" * 30)
    
    # 使用Supabase的实时功能或简单的HTTP存储
    # 我们可以使用一个简单的JSON存储方案
    
    storage_data = {
        'trading_positions': {
            'positions': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'quantity': 1000,
                    'available_quantity': 1000,
                    'cost_price': 13.20,
                    'current_price': 13.50,
                    'market_value': 13500,
                    'profit_loss': 300,
                    'profit_loss_ratio': 2.27,
                    'source': 'local_trading_export'
                }
            ],
            'summary': {
                'total_market_value': 13500,
                'total_profit_loss': 300,
                'total_cost': 13200
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'local_computer'
        },
        'trading_balance': {
            'balance': {
                'total_assets': 125680.5,
                'available_cash': 23450.8,
                'market_value': 102229.7,
                'frozen_amount': 0,
                'source': 'local_trading_export'
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'local_computer'
        }
    }
    
    print("📊 准备存储的数据:")
    print(json.dumps(storage_data, indent=2, ensure_ascii=False))
    
    # 保存到本地文件作为备用
    try:
        with open('trading_data_backup.json', 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2, ensure_ascii=False)
        print("✅ 数据已保存到本地备份文件")
    except Exception as e:
        print(f"❌ 本地备份失败: {e}")

if __name__ == "__main__":
    test_supabase_connection()
    create_simple_storage()
