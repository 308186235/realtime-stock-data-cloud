"""
交易程序买卖模块
提供买入,卖出股票的功能
"""

import win32api
import win32con
import time
from trader_core import switch_to_trading_software, clear_and_type, send_key_fast, get_current_focus

def buy_stock(code, price, quantity):
    """
    买入股票
    
    Args:
        code (str): 股票代码
        price (str): 买入价格
        quantity (str): 买入数量
    
    Returns:
        bool: 操作是否成功
    """
    print(f"\n🚀 买入股票")
    print(f"股票代码: {code}")
    print(f"买入价格: {price}")
    print(f"买入数量: {quantity}")
    print("-" * 40)

    # 获取当前焦点
    hwnd, current_title = get_current_focus()
    print(f"当前焦点: '{current_title}'")

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    try:
        # 1. F2-F1 进入买入界面
        print("\n1. F2-F1 进入买入界面...")
        send_key_fast(0x71)  # F2
        send_key_fast(0x70)  # F1
        time.sleep(0.5)

        # 2. 输入股票代码
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 3. Tab到买入数量框 (2次Tab跳过价格框)
        print("\n3. Tab到买入数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 4. 输入买入数量
        print("\n4. 输入买入数量...")
        clear_and_type(quantity)
        time.sleep(0.5)

        # 5. Tab跳出数量框
        print("\n5. Tab跳出数量框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 6. 自动按B键确认买入
        print("\n6. 按B键确认买入...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, 0, 0)  # B键按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)  # B键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)

        print("✅ 买入操作完成!")
        return True

    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

def sell_stock(code, price, quantity):
    """
    卖出股票
    
    Args:
        code (str): 股票代码
        price (str): 卖出价格
        quantity (str): 卖出数量
    
    Returns:
        bool: 操作是否成功
    """
    print(f"\n🚀 卖出股票")
    print(f"股票代码: {code}")
    print(f"卖出价格: {price}")
    print(f"卖出数量: {quantity}")
    print("-" * 40)

    # 获取当前焦点
    hwnd, current_title = get_current_focus()
    print(f"当前焦点: '{current_title}'")

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    try:
        # 1. F1-F2 进入卖出界面
        print("\n1. F1-F2 进入卖出界面...")
        send_key_fast(0x70)  # F1
        send_key_fast(0x71)  # F2
        time.sleep(0.5)

        # 2. 输入股票代码
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 3. Tab到卖出数量框 (2次Tab跳过价格框)
        print("\n3. Tab到卖出数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 4. 输入卖出数量
        print("\n4. 输入卖出数量...")
        clear_and_type(quantity)
        time.sleep(0.5)

        # 5. Tab跳出数量框
        print("\n5. Tab跳出数量框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 6. 自动按S键确认卖出
        print("\n6. 按S键确认卖出...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)

        print("✅ 卖出操作完成!")
        return True

    except Exception as e:
        print(f"❌ 卖出操作失败: {e}")
        return False

def quick_buy(code, quantity, price="市价"):
    """
    快速买入(简化参数)
    
    Args:
        code (str): 股票代码
        quantity (str): 买入数量
        price (str): 买入价格,默认"市价"
    
    Returns:
        bool: 操作是否成功
    """
    return buy_stock(code, price, quantity)

def quick_sell(code, quantity, price="市价"):
    """
    快速卖出(简化参数)
    
    Args:
        code (str): 股票代码
        quantity (str): 卖出数量
        price (str): 卖出价格,默认"市价"
    
    Returns:
        bool: 操作是否成功
    """
    return sell_stock(code, price, quantity)

# 测试函数
if __name__ == "__main__":
    print("🧪 测试买卖模块")
    
    # 测试买入
    print("\n=== 测试买入 ===")
    result = buy_stock("000001", "10.50", "100")
    print(f"买入结果: {result}")
    
    # 测试卖出
    print("\n=== 测试卖出 ===")
    result = sell_stock("000001", "10.60", "100")
    print(f"卖出结果: {result}")
