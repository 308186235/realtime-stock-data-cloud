#!/usr/bin/env python3
"""
设置Supabase数据表
"""

import requests
import json

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://zzukfxwavknskqcepsjb.supabase.co',
    'service_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g'
}

def setup_trading_data_table():
    """设置trading_data表"""
    print("🔧 设置Supabase数据表")
    print("=" * 50)
    
    headers = {
        'apikey': SUPABASE_CONFIG['service_key'],
        'Authorization': f"Bearer {SUPABASE_CONFIG['service_key']}",
        'Content-Type': 'application/json'
    }
    
    # 创建表的SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS trading_data (
        id SERIAL PRIMARY KEY,
        data_type VARCHAR(50) NOT NULL,
        data JSONB NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        source VARCHAR(100) DEFAULT 'local_trading_server',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_trading_data_type ON trading_data(data_type);
    CREATE INDEX IF NOT EXISTS idx_trading_data_timestamp ON trading_data(timestamp);
    
    -- 启用RLS (Row Level Security)
    ALTER TABLE trading_data ENABLE ROW LEVEL SECURITY;
    
    -- 创建策略允许所有操作 (开发环境)
    DROP POLICY IF EXISTS "Allow all operations" ON trading_data;
    CREATE POLICY "Allow all operations" ON trading_data FOR ALL USING (true);
    """
    
    try:
        # 执行SQL
        response = requests.post(
            f"{SUPABASE_CONFIG['url']}/rest/v1/rpc/exec_sql",
            json={"sql": create_table_sql},
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("✅ 数据表创建成功")
        else:
            print(f"⚠️ 数据表创建响应: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 数据表创建失败: {e}")
    
    # 测试插入数据
    print("\n🔧 测试数据插入")
    print("-" * 30)
    
    test_data = {
        'data_type': 'test',
        'data': {
            'message': 'Supabase连接测试',
            'timestamp': '2025-07-03T02:00:00Z'
        },
        'source': 'setup_script'
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_CONFIG['url']}/rest/v1/trading_data",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ 测试数据插入成功")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 测试数据插入失败: {response.status_code}")
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试数据插入异常: {e}")
    
    # 测试查询数据
    print("\n🔧 测试数据查询")
    print("-" * 30)
    
    try:
        response = requests.get(
            f"{SUPABASE_CONFIG['url']}/rest/v1/trading_data",
            params={'limit': 5, 'order': 'timestamp.desc'},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 数据查询成功，找到 {len(data)} 条记录")
            
            for record in data:
                print(f"   📊 {record['data_type']} - {record['timestamp']}")
        else:
            print(f"❌ 数据查询失败: {response.status_code}")
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 数据查询异常: {e}")

def insert_sample_data():
    """插入示例数据"""
    print("\n🔧 插入示例交易数据")
    print("-" * 30)
    
    headers = {
        'apikey': SUPABASE_CONFIG['service_key'],
        'Authorization': f"Bearer {SUPABASE_CONFIG['service_key']}",
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # 示例持仓数据
    positions_data = {
        'data_type': 'positions',
        'data': {
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
            'source': 'local_computer'
        },
        'source': 'setup_script'
    }
    
    # 示例余额数据
    balance_data = {
        'data_type': 'balance',
        'data': {
            'balance': {
                'total_assets': 125680.5,
                'available_cash': 23450.8,
                'market_value': 102229.7,
                'frozen_amount': 0,
                'source': 'local_trading_export'
            },
            'source': 'local_computer'
        },
        'source': 'setup_script'
    }
    
    for data_name, data in [('持仓', positions_data), ('余额', balance_data)]:
        try:
            response = requests.post(
                f"{SUPABASE_CONFIG['url']}/rest/v1/trading_data",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ {data_name}数据插入成功")
            else:
                print(f"❌ {data_name}数据插入失败: {response.status_code}")
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"❌ {data_name}数据插入异常: {e}")

if __name__ == "__main__":
    setup_trading_data_table()
    insert_sample_data()
    print("\n🎉 Supabase设置完成！")
