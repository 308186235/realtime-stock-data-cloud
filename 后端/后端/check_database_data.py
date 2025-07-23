#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Supabase数据库中的股票数据
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client, Client

# Supabase配置
SUPABASE_URL = "https://process.env.SUPABASE_URL"
SUPABASE_KEY = "process.env.SUPABASE_ANON_KEY

def check_database_data():
    """检查数据库中的股票数据"""
    try:
        print("🔍 检查Supabase数据库中的股票数据...")
        print("=" * 50)
        
        # 创建Supabase客户端
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 检查stock_data表
        print("📊 检查stock_data表...")
        
        # 获取总记录数
        total_response = supabase.table('stock_data').select('*', count='exact').execute()
        total_count = total_response.count if hasattr(total_response, 'count') else len(total_response.data)
        print(f"   总记录数: {total_count}")
        
        # 获取最新的10条记录
        latest_response = supabase.table('stock_data').select('*').order('updated_at', desc=True).limit(10).execute()
        latest_data = latest_response.data
        
        if latest_data:
            print(f"   最新记录数: {len(latest_data)}")
            print("   最新10条记录:")
            for i, record in enumerate(latest_data[:5], 1):
                symbol = record.get('symbol', 'N/A')
                name = record.get('name', 'N/A')
                price = record.get('price', 0)
                change_percent = record.get('change_percent', 0)
                updated_at = record.get('updated_at', 'N/A')
                print(f"   {i}. {symbol} {name}: ¥{price} ({change_percent:+.2f}%) - {updated_at}")
        else:
            print("   ❌ 没有找到任何记录")
            
        # 检查今天的数据
        today = datetime.now().strftime('%Y-%m-%d')
        today_response = supabase.table('stock_data').select('*').gte('updated_at', f'{today}T00:00:00').execute()
        today_count = len(today_response.data)
        print(f"   今天的记录数: {today_count}")
        
        # 检查不同股票代码的数量
        symbols_response = supabase.table('stock_data').select('symbol').execute()
        unique_symbols = set(record['symbol'] for record in symbols_response.data if record.get('symbol'))
        print(f"   不同股票数量: {len(unique_symbols)}")
        
        # 检查最近1小时的数据
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        recent_response = supabase.table('stock_data').select('*').gte('updated_at', one_hour_ago).execute()
        recent_count = len(recent_response.data)
        print(f"   最近1小时记录数: {recent_count}")
        
        # 显示一些统计信息
        if latest_data:
            print("\n📈 数据统计:")
            prices = [float(record.get('price', 0)) for record in latest_data if record.get('price')]
            if prices:
                print(f"   价格范围: ¥{min(prices):.2f} - ¥{max(prices):.2f}")
                
            changes = [float(record.get('change_percent', 0)) for record in latest_data if record.get('change_percent')]
            if changes:
                positive_changes = [c for c in changes if c > 0]
                negative_changes = [c for c in changes if c < 0]
                print(f"   涨跌统计: 上涨{len(positive_changes)}只, 下跌{len(negative_changes)}只")
        
        print("\n✅ 数据库检查完成!")
        
        # 检查数据是否实时更新
        if recent_count > 0:
            print("🎉 数据库正在接收实时数据推送!")
        else:
            print("⚠️  最近1小时没有新数据,可能需要检查数据推送服务")
            
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
        return False

if __name__ == "__main__":
    check_database_data()
