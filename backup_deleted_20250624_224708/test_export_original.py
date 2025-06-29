"""
测试原版逻辑的导出功能
"""

from trader_export_original import export_holdings

def test_export_original():
    """测试原版导出功能"""
    print("🧪 测试原版导出功能")
    print("=" * 40)
    
    # 测试持仓导出
    print("\n📊 测试持仓数据导出...")
    result = export_holdings()
    print(f"持仓导出结果: {'成功' if result else '失败'}")
    
    return result

if __name__ == "__main__":
    test_export_original()
