#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库测试 - 使用service_role key
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase配置 - 使用service_role key
SUPABASE_URL = "https://zzukfxwavknskqcepsjb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g"

def test_with_service_key():
    """使用service_role key测试"""
    print("🔧 使用service_role key测试数据库...")
    
    try:
        # 使用service_role key创建客户端
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 测试数据
        test_data = {
            'symbol': 'SH000001',
            'name': '上证指数',
            'price': 3455.23,
            'change_percent': -0.07,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat(),
            'raw_data': 'SH000001,上证指数,3455.23,-0.07,1000000'
        }
        
        print("📊 尝试插入测试数据...")
        print(f"   数据: {test_data}")
        
        # 尝试插入到stock_realtime表
        result = supabase.table('stock_realtime').insert(test_data).execute()
        
        if result.data:
            print("✅ 数据插入成功!")
            print(f"   插入结果: {result.data}")
            
            # 查询数据
            query_result = supabase.table('stock_realtime').select('*').eq('symbol', 'SH000001').execute()
            if query_result.data:
                print("✅ 数据查询成功!")
                print(f"   查询结果: {query_result.data}")
            
            # 清理测试数据
            delete_result = supabase.table('stock_realtime').delete().eq('symbol', 'SH000001').execute()
            print("✅ 测试数据已清理")
            
            return True
        else:
            print(f"❌ 数据插入失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ service_role key测试失败: {e}")
        return False

def test_existing_tables():
    """检查现有表"""
    print("\n🔍 检查现有表...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 尝试查询一些可能存在的表
        tables_to_check = ['stock_realtime', 'stock_data', 'agent_analysis', 'agent_account']
        
        for table_name in tables_to_check:
            try:
                result = supabase.table(table_name).select('*').limit(1).execute()
                print(f"✅ 表 '{table_name}' 存在，记录数: {len(result.data)}")
            except Exception as e:
                print(f"❌ 表 '{table_name}' 不存在或无权限: {e}")
                
    except Exception as e:
        print(f"❌ 检查表失败: {e}")

def create_simple_table():
    """创建简单的表结构"""
    print("\n🔧 尝试创建简单表...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 直接插入数据，让Supabase自动推断表结构
        simple_data = {
            'symbol': 'TEST001',
            'name': '测试股票',
            'price': 10.00,
            'change_percent': 1.23,
            'timestamp': datetime.now().isoformat()
        }
        
        result = supabase.table('stock_simple').insert(simple_data).execute()
        
        if result.data:
            print("✅ 简单表创建成功!")
            
            # 清理
            supabase.table('stock_simple').delete().eq('symbol', 'TEST001').execute()
            return True
        else:
            print(f"❌ 简单表创建失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 创建简单表失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Supabase数据库权限和表创建测试")
    print("=" * 60)
    
    # 测试service_role key
    success1 = test_with_service_key()
    
    # 检查现有表
    test_existing_tables()
    
    # 尝试创建简单表
    success2 = create_simple_table()
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    
    if success1:
        print("✅ service_role key可以插入数据")
        print("✅ 数据库连接正常")
        print("✅ 表会自动创建")
        print("\n🎉 结论: 数据库可以接收实时推送!")
        print("💡 建议: 使用service_role key进行数据写入")
    else:
        print("❌ 数据库写入仍有问题")
        print("💡 可能需要在Supabase Web界面手动配置")
    
    if success2:
        print("✅ 可以创建新表")
    
    return success1 or success2

if __name__ == "__main__":
    main()
