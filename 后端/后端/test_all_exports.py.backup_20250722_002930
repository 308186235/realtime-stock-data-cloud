"""
测试所有导出功能 (W/E/R)
"""

from trader_export import export_holdings, export_transactions, export_orders
import glob
import os

def check_export_files():
    """检查导出文件"""
    print("\n🔍 检查导出文件...")
    
    # 检查各种类型的文件
    file_types = {
        "持仓数据": "持仓数据_*.csv",
        "成交数据": "成交数据_*.csv", 
        "委托数据": "委托数据_*.csv"
    }
    
    for file_type, pattern in file_types.items():
        files = glob.glob(pattern)
        if files:
            # 按修改时间排序，显示最新的
            files.sort(key=os.path.getmtime, reverse=True)
            latest_file = files[0]
            file_size = os.path.getsize(latest_file)
            print(f"✅ {file_type}: {latest_file} ({file_size} 字节)")
        else:
            print(f"❌ {file_type}: 未找到文件")

def test_all_exports():
    """测试所有导出功能"""
    print("🧪 测试所有导出功能 (W/E/R)")
    print("=" * 60)
    
    results = {}
    
    # 测试持仓数据导出 (W键)
    print("\n📊 测试持仓数据导出 (W键)...")
    try:
        results['holdings'] = export_holdings()
        print(f"持仓数据导出: {'✅ 成功' if results['holdings'] else '❌ 失败'}")
    except Exception as e:
        print(f"持仓数据导出: ❌ 异常 - {e}")
        results['holdings'] = False
    
    # 测试成交数据导出 (E键)
    print("\n📊 测试成交数据导出 (E键)...")
    try:
        results['transactions'] = export_transactions()
        print(f"成交数据导出: {'✅ 成功' if results['transactions'] else '❌ 失败'}")
    except Exception as e:
        print(f"成交数据导出: ❌ 异常 - {e}")
        results['transactions'] = False
    
    # 测试委托数据导出 (R键)
    print("\n📊 测试委托数据导出 (R键)...")
    try:
        results['orders'] = export_orders()
        print(f"委托数据导出: {'✅ 成功' if results['orders'] else '❌ 失败'}")
    except Exception as e:
        print(f"委托数据导出: ❌ 异常 - {e}")
        results['orders'] = False
    
    # 检查导出文件
    check_export_files()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"持仓数据导出 (W): {'✅ 成功' if results['holdings'] else '❌ 失败'}")
    print(f"成交数据导出 (E): {'✅ 成功' if results['transactions'] else '❌ 失败'}")
    print(f"委托数据导出 (R): {'✅ 成功' if results['orders'] else '❌ 失败'}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 所有导出功能测试通过! ({success_count}/{total_count})")
    else:
        print(f"⚠️ 部分导出功能测试失败 ({success_count}/{total_count})")
    
    return results

if __name__ == "__main__":
    test_all_exports()
