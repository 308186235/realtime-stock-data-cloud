#!/usr/bin/env python3
"""
测试TraderAPI的导出功能
"""

import sys
import os

def test_trader_api():
    """测试TraderAPI的导出功能"""
    print("🔧 测试TraderAPI的导出功能")
    print("=" * 40)
    
    try:
        # 导入TraderAPI
        from trader_api import TraderAPI, api
        print("✅ TraderAPI导入成功")
        
        # 测试API状态
        print(f"\n📊 API版本: {api.version}")
        
        # 获取状态
        status = api.get_status()
        print(f"📊 API状态: {status}")
        
        # 测试导出功能
        print(f"\n🔥 测试导出功能...")
        
        export_types = ["holdings", "balance", "all"]
        
        for export_type in export_types:
            print(f"\n🔥 测试导出: {export_type}")
            
            try:
                if hasattr(api, 'export_data'):
                    result = api.export_data(export_type)
                    print(f"   ✅ 成功: {result}")
                else:
                    print(f"   ❌ API没有export_data方法")
                    
                    # 检查有哪些方法
                    methods = [method for method in dir(api) if not method.startswith('_')]
                    print(f"   📋 可用方法: {methods}")
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
        
        # 测试直接导入的函数
        print(f"\n🔥 测试直接导入的导出函数...")
        
        try:
            from trader_export import export_holdings, export_transactions, export_orders, export_all_data
            print("✅ 导出函数导入成功")
            
            # 测试export_holdings
            print(f"\n🔥 测试export_holdings...")
            try:
                result = export_holdings()
                print(f"   ✅ 成功: {result}")
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                
        except ImportError as e:
            print(f"❌ 导出函数导入失败: {e}")
        
    except ImportError as e:
        print(f"❌ TraderAPI导入失败: {e}")
        print(f"📁 当前目录: {os.getcwd()}")
        print(f"📁 Python路径: {sys.path}")
        
        # 检查文件是否存在
        files_to_check = [
            "trader_api.py",
            "trader_export.py", 
            "trader_buy_sell.py",
            "trader_core.py"
        ]
        
        for file in files_to_check:
            if os.path.exists(file):
                print(f"   ✅ {file} 存在")
            else:
                print(f"   ❌ {file} 不存在")

if __name__ == "__main__":
    test_trader_api()
