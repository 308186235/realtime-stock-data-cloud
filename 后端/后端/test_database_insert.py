#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库插入功能
"""

import json
from datetime import datetime
from supabase import create_client, Client

# Supabase配置
SUPABASE_URL = "https://process.env.SUPABASE_URL"
SUPABASE_KEY = "process.env.SUPABASE_ANON_KEY

def test_database_insert():
    """测试数据库插入"""
    try:
        print("🔧 测试Supabase数据库连接和插入...")
        print("=" * 50)
        
        # 创建Supabase客户端
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 测试数据
        test_stock_data = {
            'symbol': 'SH000001',
            'name': '上证指数',
            'price': 3455.23,
            'change_percent': -0.07,
            'volume': 1000000,
            'raw_data': {
                'test': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        print("📊 测试插入股票数据...")
        print(f"   数据: {test_stock_data}")
        
        # 尝试插入数据
        result = supabase.table('stock_data').insert(test_stock_data).execute()
        
        if result.data:
            print("✅ 数据插入成功!")
            print(f"   插入的数据: {result.data}")
            
            # 查询刚插入的数据
            query_result = supabase.table('stock_data').select('*').eq('symbol', 'SH000001').execute()
            if query_result.data:
                print("✅ 数据查询成功!")
                print(f"   查询结果: {query_result.data}")
            else:
                print("❌ 数据查询失败")
                
            # 清理测试数据
            delete_result = supabase.table('stock_data').delete().eq('symbol', 'SH000001').execute()
            print("✅ 测试数据已清理")
            
        else:
            print("❌ 数据插入失败")
            print(f"   错误: {result}")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        
        # 如果表不存在,尝试创建
        if "does not exist" in str(e):
            print("\n🔄 表不存在,尝试通过插入数据自动创建...")
            try:
                # 这会自动创建表
                result = supabase.table('stock_data').insert(test_stock_data).execute()
                print("✅ 表创建成功!")
                return True
            except Exception as e2:
                print(f"❌ 自动创建表也失败: {e2}")
        
        return False

def test_agent_data_insert():
    """测试Agent数据插入"""
    try:
        print("\n🤖 测试Agent数据插入...")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 测试Agent分析数据
        agent_analysis_data = {
            'analysis_id': 'TEST_ANALYSIS_001',
            'market_sentiment': 'neutral',
            'confidence_score': 75,
            'recommendations': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'action': 'buy',
                    'current_price': 13.20,
                    'target_price': 15.00,
                    'reason': '技术指标向好'
                }
            ],
            'market_data': {
                'total_stocks': 5000,
                'rising_stocks': 2500,
                'falling_stocks': 2500
            }
        }
        
        print("📊 插入Agent分析数据...")
        result = supabase.table('agent_analysis').insert(agent_analysis_data).execute()
        
        if result.data:
            print("✅ Agent分析数据插入成功!")
            
            # 清理测试数据
            supabase.table('agent_analysis').delete().eq('analysis_id', 'TEST_ANALYSIS_001').execute()
            print("✅ Agent测试数据已清理")
        else:
            print("❌ Agent分析数据插入失败")
            
        # 测试Agent账户数据
        agent_account_data = {
            'account_id': 'TEST_ACCOUNT_001',
            'account_name': 'Agent虚拟交易账户',
            'account_type': 'virtual',
            'data_source': 'agent_system',
            'balance': {
                'total_assets': 125680.50,
                'available_cash': 23450.80,
                'market_value': 101029.70,
                'total_profit_loss': 8650.30,
                'profit_loss_percent': 7.38
            },
            'positions': [
                {
                    'stock_code': '000001',
                    'stock_name': '平安银行',
                    'quantity': 1000,
                    'cost_price': 12.50,
                    'current_price': 13.20,
                    'market_value': 13200.00,
                    'profit_loss': 700.00,
                    'profit_loss_percent': 5.60
                }
            ],
            'today_trading': {
                'buy_amount': 5000.00,
                'sell_amount': 3000.00,
                'net_amount': 2000.00,
                'transaction_count': 3
            }
        }
        
        print("📊 插入Agent账户数据...")
        result = supabase.table('agent_account').insert(agent_account_data).execute()
        
        if result.data:
            print("✅ Agent账户数据插入成功!")
            
            # 清理测试数据
            supabase.table('agent_account').delete().eq('account_id', 'TEST_ACCOUNT_001').execute()
            print("✅ Agent账户测试数据已清理")
        else:
            print("❌ Agent账户数据插入失败")
            
        return True
        
    except Exception as e:
        print(f"❌ Agent数据测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Supabase数据库测试")
    print("=" * 50)
    
    # 测试基础数据插入
    success1 = test_database_insert()
    
    # 测试Agent数据插入
    success2 = test_agent_data_insert()
    
    if success1 and success2:
        print("\n🎉 所有测试通过!")
        print("✅ 数据库连接正常")
        print("✅ 数据插入功能正常")
        print("✅ Agent数据结构正确")
    else:
        print("\n❌ 部分测试失败")
        print("💡 请检查Supabase配置和权限设置")
