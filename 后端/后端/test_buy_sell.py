"""
测试买卖功能
注意:这是真实交易功能测试,请谨慎使用!
建议在模拟账户或小金额测试
"""

from trader_buy_sell import buy_stock, sell_stock

def test_buy_interface():
    """测试买入界面(不实际执行买入)"""
    print("🧪 测试买入界面操作")
    print("=" * 50)
    print("⚠️ 注意:这将测试买入界面操作")
    print("⚠️ 请确保在模拟账户或准备好的测试环境中运行")
    
    # 测试参数
    test_code = "000001"  # 平安银行
    test_price = "10.50"
    test_quantity = "100"
    
    print(f"\n📊 测试参数:")
    print(f"股票代码: {test_code}")
    print(f"买入价格: {test_price}")
    print(f"买入数量: {test_quantity}")
    
    confirm = input("\n❓ 确认要测试买入界面吗?(输入 'YES' 确认): ")
    if confirm != "YES":
        print("❌ 测试取消")
        return False
    
    try:
        result = buy_stock(test_code, test_price, test_quantity)
        if result:
            print("✅ 买入界面测试完成")
            print("⚠️ 请检查交易软件中的输入是否正确")
            print("⚠️ 如果不需要实际买入,请在交易软件中取消操作")
        else:
            print("❌ 买入界面测试失败")
        return result
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_sell_interface():
    """测试卖出界面(不实际执行卖出)"""
    print("\n🧪 测试卖出界面操作")
    print("=" * 50)
    print("⚠️ 注意:这将测试卖出界面操作")
    print("⚠️ 请确保在模拟账户或准备好的测试环境中运行")
    
    # 测试参数
    test_code = "000001"  # 平安银行
    test_price = "10.60"
    test_quantity = "100"
    
    print(f"\n📊 测试参数:")
    print(f"股票代码: {test_code}")
    print(f"卖出价格: {test_price}")
    print(f"卖出数量: {test_quantity}")
    
    confirm = input("\n❓ 确认要测试卖出界面吗?(输入 'YES' 确认): ")
    if confirm != "YES":
        print("❌ 测试取消")
        return False
    
    try:
        result = sell_stock(test_code, test_price, test_quantity)
        if result:
            print("✅ 卖出界面测试完成")
            print("⚠️ 请检查交易软件中的输入是否正确")
            print("⚠️ 如果不需要实际卖出,请在交易软件中取消操作")
        else:
            print("❌ 卖出界面测试失败")
        return result
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 交易买卖功能测试")
    print("=" * 60)
    print("⚠️ 重要提醒:")
    print("⚠️ 1. 这是真实交易功能测试")
    print("⚠️ 2. 请确保在模拟账户中测试")
    print("⚠️ 3. 测试完成后请检查交易软件中的输入")
    print("⚠️ 4. 如不需要实际交易,请在软件中取消操作")
    print("=" * 60)
    
    while True:
        print("\n📋 测试选项:")
        print("1. 测试买入界面")
        print("2. 测试卖出界面")
        print("3. 退出测试")
        
        choice = input("\n请选择测试项目 (1-3): ").strip()
        
        if choice == "1":
            test_buy_interface()
        elif choice == "2":
            test_sell_interface()
        elif choice == "3":
            print("👋 退出测试")
            break
        else:
            print("❌ 无效选择,请输入 1-3")

if __name__ == "__main__":
    main()
