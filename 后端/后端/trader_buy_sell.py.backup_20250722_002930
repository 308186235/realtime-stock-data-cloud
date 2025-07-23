"""
交易买卖功能模块 - 完全按照原版working_trader_FIXED.py
提供股票买入和卖出功能
"""

import win32api
import win32con
import time
from trader_core_original import (
    switch_to_trading_software,
    clear_and_type,
    send_key_fast
)

def buy_stock(code, price, quantity):
    """买入股票"""
    print(f"\n🚀 买入操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("\n开始买入操作...")

    try:
        # 2. 按F2-F1进入买入界面
        print("\n1. 按F2-F1进入买入界面...")
        send_key_fast(0x71)  # F2
        time.sleep(0.1)
        send_key_fast(0x70)  # F1
        time.sleep(0.5)

        # 3. 输入股票代码 (应该已经在证券代码框)
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 4. Tab到买入数量框 (2次Tab)
        print("\n3. Tab到买入数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 5. 输入数量
        print(f"\n4. 输入买入数量: {quantity} (类型: {type(quantity)})")
        # 确保quantity是字符串
        quantity_str = str(quantity)
        print(f"   转换后的数量: '{quantity_str}'")
        clear_and_type(quantity_str)
        time.sleep(0.5)

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 自动按B键确认买入
        print("\n7. 按B键确认买入...")
        # 按住Shift + B 产生大写B
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, 0, 0)  # B键按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)  # B键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)
        
        print("\n✅ 买入操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def sell_stock(code, price, quantity):
    """卖出股票"""
    print(f"\n🚀 卖出操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("\n开始卖出操作...")

    try:
        # 2. 按F1-F2进入卖出界面
        print("\n1. 按F1-F2进入卖出界面...")
        send_key_fast(0x70)  # F1
        time.sleep(0.1)
        send_key_fast(0x71)  # F2
        time.sleep(0.5)

        # 3. 输入股票代码 (应该已经在证券代码框)
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 4. Tab到卖出数量框 (2次Tab)
        print("\n3. Tab到卖出数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 5. 输入数量
        print(f"\n4. 输入卖出数量: {quantity} (类型: {type(quantity)})")
        # 确保quantity是字符串
        quantity_str = str(quantity)
        print(f"   转换后的数量: '{quantity_str}'")
        clear_and_type(quantity_str)
        time.sleep(0.5)

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 自动按S键确认卖出
        print("\n7. 按S键确认卖出...")
        # 按住Shift + S 产生大写S
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)
        
        print("\n✅ 卖出操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

# 便捷接口
def quick_buy(code, quantity):
    """快速买入（市价）"""
    return buy_stock(code, "市价", quantity)

def quick_sell(code, quantity):
    """快速卖出（市价）"""
    return sell_stock(code, "市价", quantity)

if __name__ == "__main__":
    print("🧪 交易买卖功能模块测试")
    print("=" * 50)
    print("注意：这是测试模式，请确保交易软件已打开")
    print("建议使用模拟账户进行测试")
    
    # 示例用法（注释掉避免意外执行）
    # buy_stock("000001", "10.50", "100")
    # sell_stock("000001", "10.60", "100")
