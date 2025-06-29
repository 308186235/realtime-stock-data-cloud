import win32gui
import win32api
import win32con
import time
import ctypes
from ctypes import wintypes

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    print(f"当前Caps Lock状态: {caps_state}")
    
    if caps_state == 0:
        print("开启Caps Lock...")
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        new_state = win32api.GetKeyState(win32con.VK_CAPITAL)
        print(f"开启后Caps Lock状态: {new_state}")
        return new_state != 0
    else:
        print("Caps Lock已开启")
        return True

def activate_trading_window():
    """激活交易软件窗口"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        print(f"找到交易软件窗口: {hex(hwnd)}")
        # 多种方式激活窗口
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)
        time.sleep(1.0)
        
        # 验证窗口是否真的在前台
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print("✅ 交易软件窗口已激活")
            return True
        else:
            print(f"⚠️ 当前前台窗口: {hex(current_hwnd)}")
            return False
    else:
        print("❌ 没找到交易软件窗口")
        return False

def test_multiple_methods():
    """测试多种发送W键的方法"""
    print("测试多种硬件级别的键盘输入方法...")
    
    # 确保Caps Lock开启
    if not ensure_caps_lock_on():
        print("❌ 无法开启Caps Lock")
        return
    
    # 激活交易软件窗口
    if not activate_trading_window():
        print("❌ 无法激活交易软件窗口")
        return
    
    print("准备测试W键...")
    time.sleep(2)
    
    # 方法1: 使用MapVirtualKey获取正确的扫描码
    print("方法1: 使用MapVirtualKey获取扫描码")
    scan_code = win32api.MapVirtualKey(0x57, 0)  # W键
    print(f"W键扫描码: {hex(scan_code)}")
    
    win32api.keybd_event(0x57, scan_code, 0, 0)  # 按下
    time.sleep(0.05)
    win32api.keybd_event(0x57, scan_code, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    time.sleep(3)
    
    # 方法2: 使用KEYEVENTF_SCANCODE标志
    print("方法2: 使用KEYEVENTF_SCANCODE标志")
    win32api.keybd_event(0, scan_code, win32con.KEYEVENTF_SCANCODE, 0)  # 按下
    time.sleep(0.05)
    win32api.keybd_event(0, scan_code, win32con.KEYEVENTF_SCANCODE | win32con.KEYEVENTF_KEYUP, 0)  # 释放
    time.sleep(3)
    
    # 方法3: 使用ctypes直接调用keybd_event
    print("方法3: 使用ctypes直接调用keybd_event")
    user32 = ctypes.windll.user32
    user32.keybd_event(0x57, scan_code, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x57, scan_code, 2, 0)  # 2 = KEYEVENTF_KEYUP
    time.sleep(3)
    
    # 方法4: 尝试发送Unicode字符
    print("方法4: 发送Unicode字符")
    win32api.keybd_event(0, ord('W'), win32con.KEYEVENTF_UNICODE, 0)
    time.sleep(0.05)
    win32api.keybd_event(0, ord('W'), win32con.KEYEVENTF_UNICODE | win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(3)
    
    # 方法5: 模拟按住Shift+w (大写W)
    print("方法5: 模拟Shift+W")
    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
    time.sleep(0.01)
    win32api.keybd_event(0x57, scan_code, 0, 0)  # W按下
    time.sleep(0.05)
    win32api.keybd_event(0x57, scan_code, win32con.KEYEVENTF_KEYUP, 0)  # W释放
    time.sleep(0.01)
    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
    time.sleep(3)
    
    print("所有W键测试方法完成！")
    
    # 现在测试一个已知能工作的键（比如N键）作为对比
    print("对比测试: 发送N键（已知能工作）")
    n_scan_code = win32api.MapVirtualKey(0x4E, 0)  # N键
    win32api.keybd_event(0x4E, n_scan_code, 0, 0)  # 按下
    time.sleep(0.05)
    win32api.keybd_event(0x4E, n_scan_code, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    time.sleep(2)
    
    print("测试完成！观察交易软件是否有任何反应")

if __name__ == "__main__":
    test_multiple_methods()
