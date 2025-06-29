import win32api
import win32con
import time

def send_key(key_code):
    """发送按键"""
    win32api.keybd_event(key_code, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def type_text(text):
    """输入文本"""
    print(f"输入: {text}")
    
    # 清空
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('A'), 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    
    send_key(win32con.VK_DELETE)
    
    # 输入
    for char in str(text):
        if char.isdigit():
            send_key(ord(char))
        elif char == '.':
            send_key(0xBE)

def buy_stock_simple(code, quantity):
    """简单买入"""
    print(f"\n🚀 买入: {code}, 数量: {quantity}")
    print("=" * 40)

    # F2-F1
    print("1. F2-F1进入买入界面...")
    send_key(0x71)  # F2
    send_key(0x70)  # F1
    time.sleep(0.5)

    # 输入代码
    print("2. 输入股票代码...")
    type_text(code)
    time.sleep(0.5)

    # 2次Tab
    print("3. Tab到数量框...")
    send_key(0x09)  # Tab 1
    time.sleep(0.3)
    send_key(0x09)  # Tab 2
    time.sleep(0.3)

    # 输入数量
    print("4. 输入数量...")
    type_text(quantity)
    time.sleep(0.5)

    # 自动点击买入按钮
    print("5. 自动点击买入按钮...")
    # 按B键买入
    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
    time.sleep(0.01)
    win32api.keybd_event(ord('B'), 0, 0, 0)  # B键按下
    time.sleep(0.01)
    win32api.keybd_event(ord('B'), 0, win32con.KEYEVENTF_KEYUP, 0)  # B键释放
    time.sleep(0.01)
    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
    time.sleep(0.5)

    print("✅ 买入操作完成！")

def main():
    print("🎯 简单买入程序")
    print("=" * 30)
    
    code = input("股票代码: ").strip() or "000001"
    quantity = input("买入数量: ").strip() or "100"
    
    buy_stock_simple(code, quantity)

if __name__ == "__main__":
    main()
