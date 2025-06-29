"""
测试卖出功能
"""

from trader_api import api

def test_sell():
    """测试卖出功能"""
    print("🧪 测试卖出功能")
    print("=" * 40)
    
    # 测试卖出
    print("📉 执行卖出操作...")
    result = api.sell("000001", "100", "10.60")
    
    print(f"\n卖出结果: {'成功' if result else '失败'}")
    
    return result

if __name__ == "__main__":
    test_sell()
