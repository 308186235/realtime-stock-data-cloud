"""
测试三个导出功能
"""

from trader_api_real import api

def test_all_exports():
    """测试所有导出功能"""
    print("🧪 测试所有导出功能")
    print("=" * 50)
    
    # 1. 测试持仓导出
    print("\n📊 1. 测试持仓数据导出...")
    result1 = api.export_positions()
    print(f"持仓导出结果: {'✅ 成功' if result1 else '❌ 失败'}")
    
    # 2. 测试成交导出
    print("\n📊 2. 测试成交数据导出...")
    result2 = api.export_trades()
    print(f"成交导出结果: {'✅ 成功' if result2 else '❌ 失败'}")
    
    # 3. 测试委托导出
    print("\n📊 3. 测试委托数据导出...")
    result3 = api.export_orders()
    print(f"委托导出结果: {'✅ 成功' if result3 else '❌ 失败'}")
    
    # 查看导出文件
    print("\n📁 查看导出文件...")
    files = api.get_files()
    for file_type, file_list in files.items():
        type_name = {"holdings": "持仓", "transactions": "成交", "orders": "委托"}[file_type]
        print(f"{type_name}数据: {len(file_list)} 个文件")
        if file_list:
            print(f"  最新: {file_list[-1]}")
    
    # 总结
    success_count = sum([result1, result2, result3])
    print(f"\n🎯 总结: {success_count}/3 项导出成功")
    
    return success_count == 3

if __name__ == "__main__":
    test_all_exports()
