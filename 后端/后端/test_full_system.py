"""
完整交易系统功能测试
包含:余额获取,导出功能,买卖功能演示
"""

from trader_export import export_holdings, export_transactions, export_orders
from trader_buy_sell import buy_stock, sell_stock
from fixed_balance_reader import get_balance_fixed
import time

def test_balance():
    """测试余额获取"""
    print("🧪 测试余额获取功能")
    print("=" * 50)
    
    try:
        balance = get_balance_fixed()
        if balance and balance.get('available_cash', 0) >= 0:
            print("✅ 余额获取成功!")
            return True
        else:
            print("❌ 余额获取失败")
            return False
    except Exception as e:
        print(f"❌ 余额获取异常: {e}")
        return False

def test_exports():
    """测试导出功能"""
    print("\n🧪 测试导出功能")
    print("=" * 50)
    
    results = {}
    
    # 测试持仓导出
    print("📊 测试持仓导出...")
    try:
        results['holdings'] = export_holdings()
        print(f"持仓导出: {'✅ 成功' if results['holdings'] else '❌ 失败'}")
    except Exception as e:
        print(f"持仓导出: ❌ 异常 - {e}")
        results['holdings'] = False
    
    time.sleep(1)  # 间隔1秒
    
    # 测试成交导出
    print("\n📊 测试成交导出...")
    try:
        results['transactions'] = export_transactions()
        print(f"成交导出: {'✅ 成功' if results['transactions'] else '❌ 失败'}")
    except Exception as e:
        print(f"成交导出: ❌ 异常 - {e}")
        results['transactions'] = False
    
    time.sleep(1)  # 间隔1秒
    
    # 测试委托导出
    print("\n📊 测试委托导出...")
    try:
        results['orders'] = export_orders()
        print(f"委托导出: {'✅ 成功' if results['orders'] else '❌ 失败'}")
    except Exception as e:
        print(f"委托导出: ❌ 异常 - {e}")
        results['orders'] = False
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📊 导出功能测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def demo_trading():
    """演示买卖功能(安全模式)"""
    print("\n🎭 买卖功能演示")
    print("=" * 50)
    print("⚠️ 注意:这是演示模式")
    print("⚠️ 演示完成后请在交易软件中取消操作")
    
    confirm = input("\n❓ 确认要演示买卖功能吗?(输入 'demo' 确认): ")
    if confirm.lower() != "demo":
        print("❌ 演示取消")
        return False
    
    # 演示买入
    print("\n🚀 演示买入操作...")
    try:
        buy_result = buy_stock("000001", "10.50", "100")
        print(f"买入演示: {'✅ 完成' if buy_result else '❌ 失败'}")
    except Exception as e:
        print(f"买入演示: ❌ 异常 - {e}")
        buy_result = False
    
    time.sleep(2)  # 间隔2秒
    
    # 演示卖出
    print("\n🚀 演示卖出操作...")
    try:
        sell_result = sell_stock("000001", "10.60", "100")
        print(f"卖出演示: {'✅ 完成' if sell_result else '❌ 失败'}")
    except Exception as e:
        print(f"卖出演示: ❌ 异常 - {e}")
        sell_result = False
    
    if buy_result and sell_result:
        print("\n✅ 买卖功能演示完成!")
        print("⚠️ 请检查交易软件中的操作,如不需要实际交易请取消")
        return True
    else:
        print("\n❌ 买卖功能演示失败")
        return False

def main():
    """主测试函数"""
    print("🧪 完整交易系统功能测试")
    print("=" * 60)
    print("📋 测试项目:")
    print("1. 余额获取功能")
    print("2. 导出功能(W/E/R)")
    print("3. 买卖功能演示(安全模式)")
    print("=" * 60)
    
    results = {}
    
    # 1. 测试余额获取
    results['balance'] = test_balance()
    
    # 2. 测试导出功能
    results['exports'] = test_exports()
    
    # 3. 演示买卖功能
    results['trading'] = demo_trading()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 完整系统测试结果:")
    print("-" * 40)
    print(f"余额获取: {'✅ 成功' if results['balance'] else '❌ 失败'}")
    print(f"导出功能: {'✅ 成功' if results['exports'] else '❌ 失败'}")
    print(f"买卖演示: {'✅ 完成' if results['trading'] else '❌ 失败'}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 完整系统测试通过! ({success_count}/{total_count})")
        print("🎯 所有核心功能正常工作!")
    else:
        print(f"\n⚠️ 部分功能测试失败 ({success_count}/{total_count})")
    
    print("\n📋 核心文件:")
    print("✅ backup_deleted_20250624_224708/working_trader_FIXED.py - 原版源代码")
    print("✅ trader_core_original.py - 核心功能模块")
    print("✅ trader_export.py - 导出功能模块")
    print("✅ trader_buy_sell.py - 买卖功能模块")
    print("✅ fixed_balance_reader.py - 余额获取模块")

if __name__ == "__main__":
    main()
