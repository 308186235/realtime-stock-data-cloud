"""
测试余额获取功能
"""

from fixed_balance_reader import get_balance_fixed

def test_balance():
    """测试余额获取"""
    print("🧪 测试余额获取功能")
    print("=" * 50)
    
    try:
        print("📊 开始获取账户余额...")
        balance = get_balance_fixed()
        
        if balance and isinstance(balance, dict):
            print("\n✅ 余额获取成功!")
            print("-" * 30)
            print(f"可用资金: {balance.get('available_cash', 0):,.2f}")
            print(f"总资产: {balance.get('total_assets', 0):,.2f}")
            print(f"股票市值: {balance.get('market_value', 0):,.2f}")
            print(f"冻结资金: {balance.get('frozen_amount', 0):,.2f}")
            print(f"更新时间: {balance.get('update_time', 'N/A')}")
            print(f"数据来源: {balance.get('data_source', 'N/A')}")
            
            # 检查数据有效性
            available_cash = balance.get('available_cash', 0)
            total_assets = balance.get('total_assets', 0)
            
            if available_cash > 0 or total_assets > 0:
                print("\n🎉 余额数据有效!")
                return True
            else:
                print("\n⚠️ 余额数据为0,可能获取失败")
                return False
        else:
            print("\n❌ 余额获取失败或返回数据格式错误")
            return False
            
    except Exception as e:
        print(f"\n❌ 余额获取异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_balance()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 余额获取测试通过!")
    else:
        print("❌ 余额获取测试失败!")
