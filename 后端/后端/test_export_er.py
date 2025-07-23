"""
测试E和R导出功能
"""

from trader_export import export_transactions, export_orders

def test_export_transactions():
    """测试成交数据导出"""
    print("🧪 测试成交数据导出...")
    result = export_transactions()
    if result:
        print("✅ 成交数据导出测试成功")
    else:
        print("❌ 成交数据导出测试失败")
    return result

def test_export_orders():
    """测试委托数据导出"""
    print("\n🧪 测试委托数据导出...")
    result = export_orders()
    if result:
        print("✅ 委托数据导出测试成功")
    else:
        print("❌ 委托数据导出测试失败")
    return result

if __name__ == "__main__":
    print("🧪 测试E和R导出功能")
    print("=" * 50)
    
    # 测试成交数据导出 (E键)
    success_e = test_export_transactions()
    
    # 测试委托数据导出 (R键)
    success_r = test_export_orders()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"成交数据导出 (E): {'✅ 成功' if success_e else '❌ 失败'}")
    print(f"委托数据导出 (R): {'✅ 成功' if success_r else '❌ 失败'}")
    
    if success_e and success_r:
        print("🎉 所有导出功能测试通过!")
    else:
        print("⚠️ 部分导出功能测试失败")
