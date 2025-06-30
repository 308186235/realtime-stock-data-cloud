"""
测试Supabase连接和基本功能
"""
import asyncio
import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.supabase import (
    get_admin_client, 
    get_anon_client, 
    test_connection,
    SupabaseManager
)

async def test_basic_connection():
    """测试基本连接"""
    print("🔗 测试Supabase基本连接...")
    
    try:
        # 测试管理员客户端
        admin_client = get_admin_client()
        print("✅ 管理员客户端创建成功")
        
        # 测试匿名客户端
        anon_client = get_anon_client()
        print("✅ 匿名客户端创建成功")
        
        # 测试连接
        connection_ok = await test_connection()
        if connection_ok:
            print("✅ 数据库连接测试成功")
        else:
            print("❌ 数据库连接测试失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        return False

def test_table_operations():
    """测试表操作"""
    print("\n📊 测试数据库表操作...")
    
    try:
        manager = SupabaseManager()
        
        # 测试查询系统配置表
        print("🔍 测试查询系统配置表...")
        configs = manager.get_record('system_config')
        print(f"✅ 系统配置表查询成功，记录数: {len(configs)}")
        
        # 测试创建系统配置
        print("➕ 测试创建系统配置...")
        test_config = {
            'key': 'test_connection',
            'value': {'status': 'connected', 'timestamp': '2025-01-01T00:00:00Z'},
            'description': '连接测试配置'
        }
        
        created_config = manager.create_record('system_config', test_config)
        if created_config:
            print(f"✅ 系统配置创建成功，ID: {created_config.get('key')}")
            
            # 测试更新配置
            print("🔄 测试更新系统配置...")
            updated_data = {
                'value': {'status': 'updated', 'timestamp': '2025-01-01T01:00:00Z'},
                'description': '更新后的连接测试配置'
            }
            
            # 使用key作为标识符更新
            result = manager.client.table('system_config').update(updated_data).eq('key', 'test_connection').execute()
            if result.data:
                print("✅ 系统配置更新成功")
            
            # 测试删除配置
            print("🗑️ 测试删除系统配置...")
            delete_result = manager.client.table('system_config').delete().eq('key', 'test_connection').execute()
            if delete_result.data:
                print("✅ 系统配置删除成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 表操作测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_stock_data_operations():
    """测试股票数据操作"""
    print("\n📈 测试股票数据操作...")
    
    try:
        manager = SupabaseManager()
        
        # 测试创建股票信息
        print("➕ 测试创建股票信息...")
        test_stock = {
            'code': '000001',
            'name': '平安银行',
            'market': 'SZ',
            'sector': '金融',
            'industry': '银行'
        }
        
        created_stock = manager.create_record('stocks', test_stock)
        if created_stock:
            print(f"✅ 股票信息创建成功: {created_stock.get('name')}")
            
            # 测试查询股票
            print("🔍 测试查询股票信息...")
            stocks = manager.get_record('stocks', {'code': '000001'})
            if stocks:
                print(f"✅ 股票查询成功: {stocks[0].get('name')}")
            
            # 清理测试数据
            print("🧹 清理测试数据...")
            manager.client.table('stocks').delete().eq('code', '000001').execute()
            print("✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票数据操作测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Supabase集成测试...\n")
    
    # 测试基本连接
    connection_ok = await test_basic_connection()
    if not connection_ok:
        print("\n❌ 基本连接测试失败，停止后续测试")
        return
    
    # 测试表操作
    table_ops_ok = test_table_operations()
    if not table_ops_ok:
        print("\n⚠️ 表操作测试失败")
    
    # 测试股票数据操作
    stock_ops_ok = test_stock_data_operations()
    if not stock_ops_ok:
        print("\n⚠️ 股票数据操作测试失败")
    
    # 总结
    print("\n" + "="*50)
    if connection_ok and table_ops_ok and stock_ops_ok:
        print("🎉 所有测试通过！Supabase集成成功！")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
