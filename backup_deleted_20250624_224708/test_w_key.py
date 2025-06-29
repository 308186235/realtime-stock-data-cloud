import win32gui
import win32api
import win32con
import time

def test_w_key():
    print("测试W键发送...")
    
    # 找交易软件窗口
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if not hwnd:
        print("❌ 没找到交易软件窗口")
        return
    
    print(f"✅ 找到交易软件窗口: {hex(hwnd)}")
    
    # 检查窗口是否可见
    if not win32gui.IsWindowVisible(hwnd):
        print("❌ 窗口不可见")
        return
    
    print("✅ 窗口可见")
    
    # 获取窗口标题确认
    title = win32gui.GetWindowText(hwnd)
    print(f"窗口标题: {title}")
    
    print("准备发送W键...")
    time.sleep(2)
    
    # 方法1: PostMessage WM_CHAR
    print("发送方法1: PostMessage WM_CHAR 'W'")
    result = win32api.PostMessage(hwnd, win32con.WM_CHAR, ord('W'), 0)
    print(f"发送结果: {result}")
    time.sleep(2)
    
    # 方法2: PostMessage WM_CHAR 'w'
    print("发送方法2: PostMessage WM_CHAR 'w'")
    result = win32api.PostMessage(hwnd, win32con.WM_CHAR, ord('w'), 0)
    print(f"发送结果: {result}")
    time.sleep(2)
    
    # 方法3: PostMessage WM_KEYDOWN/UP
    print("发送方法3: PostMessage WM_KEYDOWN/UP")
    result1 = win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, 0x57, 0)
    time.sleep(0.1)
    result2 = win32api.PostMessage(hwnd, win32con.WM_KEYUP, 0x57, 0)
    print(f"KEYDOWN结果: {result1}, KEYUP结果: {result2}")
    time.sleep(2)
    
    # 方法4: SendMessage
    print("发送方法4: SendMessage WM_CHAR")
    result = win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord('W'), 0)
    print(f"发送结果: {result}")
    time.sleep(2)
    
    print("所有方法测试完成！")
    print("如果Caps Lock开着，交易软件应该已经切换到持仓页面")

if __name__ == "__main__":
    test_w_key()
