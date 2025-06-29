"""
测试导出功能
"""

from trader_api import api

def test_export():
    """测试导出功能"""
    print("🧪 测试导出功能")
    print("=" * 40)
    
    # 测试单个导出
    print("\n📊 1. 测试持仓数据导出...")
    result1 = api.export_positions()
    print(f"持仓导出结果: {'成功' if result1 else '失败'}")
    
    print("\n📊 2. 测试成交数据导出...")
    result2 = api.export_trades()
    print(f"成交导出结果: {'成功' if result2 else '失败'}")
    
    print("\n📊 3. 测试委托数据导出...")
    result3 = api.export_orders()
    print(f"委托导出结果: {'成功' if result3 else '失败'}")
    
    # 查看导出文件
    print("\n📁 查看导出文件...")
    files = api.get_files()
    for file_type, file_list in files.items():
        type_name = {"holdings": "持仓", "transactions": "成交", "orders": "委托"}[file_type]
        print(f"{type_name}数据: {len(file_list)} 个文件")
        if file_list:
            print(f"  最新: {file_list[-1]}")
    
    return result1 and result2 and result3

if __name__ == "__main__":
    test_export()
