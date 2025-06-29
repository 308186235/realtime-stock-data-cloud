import win32api
import win32con
import win32gui
import time

def send_key_simple(key_code):
    """发送单个按键"""
    win32api.keybd_event(key_code, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def type_number(number):
    """输入数字"""
    print(f"   输入数字: {number}")
    
    # 先清空
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('A'), 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    
    send_key_simple(win32con.VK_DELETE)
    
    # 逐字符输入
    for char in str(number):
        if char.isdigit():
            send_key_simple(ord(char))
        elif char == '.':
            send_key_simple(0xBE)  # 小数点
    
    print(f"   ✅ 输入完成: {number}")

def easy_buy_stock(code, quantity):
    """简化的买入操作 - 手动定位"""
    print(f"\n🚀 简化买入操作")
    print(f"股票代码: {code}")
    print(f"买入数量: {quantity}")
    print("-" * 40)
    
    # 检查焦点
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    print(f"当前窗口: {window_title}")
    
    if "交易" not in window_title and "股票" not in window_title:
        print("⚠️ 请先点击交易软件窗口!")
        input("点击交易软件后按回车继续...")
    
    try:
        # 1. F2-F1 进入买入界面
        print("\n1. 进入买入界面...")
        send_key_simple(0x71)  # F2
        send_key_simple(0x70)  # F1
        time.sleep(0.5)
        
        # 2. 输入股票代码 (应该已经在证券代码框)
        print("\n2. 输入股票代码...")
        type_number(code)
        time.sleep(0.5)
        
        # 3. 手动定位到数量框
        print("\n3. 🖱️ 手动定位:")
        print("   请用鼠标点击'买入数量'输入框")
        print("   确保光标在数量输入框中闪烁")
        print("   然后按回车继续...")
        input("✅ 光标在数量框中了吗？按回车继续...")
        
        # 4. 输入数量
        print("\n4. 输入买入数量...")
        type_number(quantity)
        time.sleep(0.5)
        
        # 5. 完成
        print("\n✅ 输入完成!")
        print("📋 请检查:")
        print(f"   - 证券代码框: {code}")
        print(f"   - 买入数量框: {quantity}")
        print("   - 如果正确，请手动点击'买入[B]'按钮")
        print("   - 程序不会自动点击，避免误操作")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def easy_sell_stock(code, quantity):
    """简化的卖出操作 - 手动定位"""
    print(f"\n🚀 简化卖出操作")
    print(f"股票代码: {code}")
    print(f"卖出数量: {quantity}")
    print("-" * 40)
    
    # 检查焦点
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    print(f"当前窗口: {window_title}")
    
    if "交易" not in window_title and "股票" not in window_title:
        print("⚠️ 请先点击交易软件窗口!")
        input("点击交易软件后按回车继续...")
    
    try:
        # 1. F1-F2 进入卖出界面
        print("\n1. 进入卖出界面...")
        send_key_simple(0x70)  # F1
        send_key_simple(0x71)  # F2
        time.sleep(0.5)
        
        # 2. 输入股票代码
        print("\n2. 输入股票代码...")
        type_number(code)
        time.sleep(0.5)
        
        # 3. 手动定位到数量框
        print("\n3. 🖱️ 手动定位:")
        print("   请用鼠标点击'卖出数量'输入框")
        print("   确保光标在数量输入框中闪烁")
        print("   然后按回车继续...")
        input("✅ 光标在数量框中了吗？按回车继续...")
        
        # 4. 输入数量
        print("\n4. 输入卖出数量...")
        type_number(quantity)
        time.sleep(0.5)
        
        # 5. 完成
        print("\n✅ 输入完成!")
        print("📋 请检查:")
        print(f"   - 证券代码框: {code}")
        print(f"   - 卖出数量框: {quantity}")
        print("   - 如果正确，请手动点击'卖出[S]'按钮")
        print("   - 程序不会自动点击，避免误操作")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def main():
    """主程序"""
    print("🎯 简化交易程序")
    print("=" * 50)
    print("✨ 特点:")
    print("   - 只自动输入股票代码")
    print("   - 手动点击数量输入框定位")
    print("   - 自动输入数量")
    print("   - 不自动点击买入/卖出按钮")
    print("   - 避免误操作，更安全")
    print("=" * 50)
    
    while True:
        print("\n📋 请选择:")
        print("1. 买入股票")
        print("2. 卖出股票")
        print("3. 退出程序")

        choice = input("\n选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n📈 买入股票")
            code = input("股票代码 (默认000001): ").strip() or "000001"
            quantity = input("买入数量 (默认100): ").strip() or "100"
            easy_buy_stock(code, quantity)
            
        elif choice == "2":
            print("\n📉 卖出股票")
            code = input("股票代码 (默认000001): ").strip() or "000001"
            quantity = input("卖出数量 (默认100): ").strip() or "100"
            easy_sell_stock(code, quantity)
            
        elif choice == "3":
            print("\n👋 退出程序")
            break

        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
