"""
专门测试委托数据导出
"""

from trader_export_real import export_orders

def test_orders_only():
    """专门测试委托数据导出"""
    print("🧪 专门测试委托数据导出")
    print("=" * 40)
    
    # 测试委托导出
    print("\n📊 测试委托数据导出...")
    result = export_orders()
    print(f"委托导出结果: {'✅ 成功' if result else '❌ 失败'}")
    
    # 检查文件是否生成
    import glob
    files = glob.glob("委托数据_*.csv")
    print(f"\n📁 委托文件数量: {len(files)}")
    if files:
        latest_file = max(files)
        print(f"最新文件: {latest_file}")
        
        # 检查文件大小
        import os
        size = os.path.getsize(latest_file)
        print(f"文件大小: {size} 字节")
        
        if size > 0:
            print("✅ 文件有内容")
        else:
            print("⚠️ 文件为空")
    else:
        print("❌ 没有找到委托数据文件")
    
    return result

if __name__ == "__main__":
    test_orders_only()
