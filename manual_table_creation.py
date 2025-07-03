#!/usr/bin/env python3
"""
手动创建数据库表的替代方案
由于Supabase REST API不支持DDL，我们通过其他方式创建表
"""

import requests
import json
from datetime import datetime

# Supabase配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

def create_manual_workaround():
    """创建手动解决方案"""
    print("🔧 创建数据库表的手动解决方案...")
    
    print("\n📋 需要在Supabase控制台执行的SQL:")
    print("=" * 60)
    
    sql_commands = [
        """
-- 1. 创建股票推送日志表
CREATE TABLE IF NOT EXISTS stock_push_logs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10,3),
    volume BIGINT,
    push_timestamp TIMESTAMP,
    received_at TIMESTAMP DEFAULT NOW(),
    api_key_used VARCHAR(50),
    batch_id INTEGER,
    file_path VARCHAR(255),
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
        """,
        """
-- 2. 创建实时股票数据表
CREATE TABLE IF NOT EXISTS real_time_stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    current_price DECIMAL(10,3),
    yesterday_close DECIMAL(10,3),
    today_open DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    volume BIGINT,
    amount BIGINT,
    turnover_rate DECIMAL(5,2),
    pe_ratio DECIMAL(8,2),
    pb_ratio DECIMAL(8,2),
    market_cap DECIMAL(15,2),
    change_amount DECIMAL(10,3),
    change_percent DECIMAL(5,2),
    data_source VARCHAR(50),
    data_quality_score INTEGER,
    market_status VARCHAR(20),
    trading_date DATE,
    data_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
        """,
        """
-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_push_logs_symbol ON stock_push_logs(symbol);
CREATE INDEX IF NOT EXISTS idx_real_time_stock_symbol ON real_time_stock_data(symbol);
        """,
        """
-- 4. 插入测试数据
INSERT INTO stock_push_logs (symbol, price, volume, push_timestamp, api_key_used, processed) VALUES
('sz000001', 12.30, 1000000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true),
('sh600519', 1405.10, 500000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true),
('sz300750', 251.50, 800000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true);
        """
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n-- 步骤 {i}:")
        print(sql.strip())
    
    print("\n" + "=" * 60)
    print("📝 执行步骤:")
    print("1. 打开 https://zzukfxwavknskqcepsjb.supabase.co")
    print("2. 进入 SQL Editor")
    print("3. 复制粘贴上面的SQL命令")
    print("4. 点击 Run 执行")
    print("5. 运行 python create_tables_api.py 验证")

def test_alternative_approach():
    """测试替代方案 - 使用现有表结构"""
    print("\n🔄 测试替代方案...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    # 尝试使用stocks表存储一些实时数据
    print("📊 尝试在stocks表中存储实时数据...")
    
    try:
        # 获取API数据
        api_response = requests.get('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001')
        if api_response.status_code == 200:
            api_data = api_response.json()
            stock = api_data.get('data', [{}])[0]
            
            print(f"✅ 获取API数据: {stock.get('stock_code')} - {stock.get('current_price')}")
            
            # 更新stocks表中的数据
            update_data = {
                'name': stock.get('stock_name', ''),
                'current_price': stock.get('current_price', 0),
                'last_updated': datetime.now().isoformat()
            }
            
            # 尝试更新现有记录
            response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/stocks?code=eq.sz000001',
                headers=headers,
                json=update_data
            )
            
            if response.status_code in [200, 204]:
                print("✅ 成功更新stocks表中的实时数据")
                return True
            else:
                print(f"⚠️ 更新失败: {response.status_code} - {response.text}")
                
        else:
            print("❌ 无法获取API数据")
            
    except Exception as e:
        print(f"❌ 替代方案测试失败: {e}")
    
    return False

def create_simplified_solution():
    """创建简化解决方案"""
    print("\n🎯 创建简化的数据整合解决方案...")
    
    # 创建一个简化的数据同步脚本
    simplified_script = '''#!/usr/bin/env python3
"""
简化的数据同步脚本 - 使用现有表结构
"""

import requests
import json
from datetime import datetime

SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

def sync_data():
    """同步数据到现有表"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    # 获取API数据
    api_response = requests.get('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001,sh600519,sz300750')
    api_data = api_response.json()
    
    for stock in api_data.get('data', []):
        # 更新stocks表
        update_data = {
            'name': stock.get('stock_name'),
            'current_price': stock.get('current_price'),
            'last_updated': datetime.now().isoformat()
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/stocks?code=eq.{stock.get("stock_code")}',
            headers=headers,
            json=update_data
        )
        
        print(f"更新 {stock.get('stock_code')}: {response.status_code}")

if __name__ == '__main__':
    sync_data()
'''
    
    with open('simplified_sync.py', 'w', encoding='utf-8') as f:
        f.write(simplified_script)
    
    print("✅ 创建了简化同步脚本: simplified_sync.py")
    
    return True

def main():
    """主函数"""
    print("🚀 数据库表创建解决方案...")
    print("=" * 60)
    
    # 显示手动创建表的方法
    create_manual_workaround()
    
    # 测试替代方案
    alternative_success = test_alternative_approach()
    
    # 创建简化解决方案
    simplified_success = create_simplified_solution()
    
    print("\n" + "=" * 60)
    print("📋 解决方案总结:")
    print("1. ✅ 手动SQL脚本已准备 - 需要在Supabase控制台执行")
    print(f"2. {'✅' if alternative_success else '❌'} 替代方案测试 - 使用现有表结构")
    print(f"3. {'✅' if simplified_success else '❌'} 简化同步脚本已创建")
    
    print("\n🎯 推荐执行顺序:")
    print("1. 在Supabase控制台执行SQL创建表")
    print("2. 运行 python create_tables_api.py 验证")
    print("3. 运行 python simplified_sync.py 测试同步")
    print("4. 重新运行推送数据处理脚本")

if __name__ == '__main__':
    main()
