import win32gui
import win32api
import win32con
import time

def test_mdi_frame():
    print("测试发送W键到MDI Frame窗口...")
    
    # 找主窗口
    main_hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if not main_hwnd:
        print("❌ 没找到主窗口")
        return
    
    print(f"✅ 主窗口: {hex(main_hwnd)}")
    
    # 找MDI Frame子窗口
    mdi_hwnd = None
    def enum_child_proc(child_hwnd, param):
        nonlocal mdi_hwnd
        class_name = win32gui.GetClassName(child_hwnd)
        if class_name == "AfxMDIFrame140s":
            mdi_hwnd = child_hwnd
            return False  # 停止枚举
        return True
    
    win32gui.EnumChildWindows(main_hwnd, enum_child_proc, None)
    
    if not mdi_hwnd:
        print("❌ 没找到MDI Frame窗口")
        return
    
    print(f"✅ MDI Frame窗口: {hex(mdi_hwnd)}")
    
    # 确保Caps Lock开启
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    print(f"Caps Lock状态: {caps_state}")
    if caps_state == 0:
        print("⚠️ Caps Lock未开启，请手动开启后重试")
        return
    
    print("准备发送W键到MDI Frame窗口...")
    time.sleep(2)
    
    # 方法1: PostMessage WM_CHAR 'W'
    print("方法1: PostMessage WM_CHAR 'W'")
    result = win32api.PostMessage(mdi_hwnd, win32con.WM_CHAR, ord('W'), 0)
    print(f"结果: {result}")
    time.sleep(3)
    
    # 方法2: PostMessage WM_KEYDOWN/UP
    print("方法2: PostMessage WM_KEYDOWN/UP")
    result1 = win32api.PostMessage(mdi_hwnd, win32con.WM_KEYDOWN, 0x57, 0)
    time.sleep(0.1)
    result2 = win32api.PostMessage(mdi_hwnd, win32con.WM_KEYUP, 0x57, 0)
    print(f"KEYDOWN: {result1}, KEYUP: {result2}")
    time.sleep(3)
    
    # 方法3: SendMessage
    print("方法3: SendMessage WM_CHAR 'W'")
    result = win32gui.SendMessage(mdi_hwnd, win32con.WM_CHAR, ord('W'), 0)
    print(f"结果: {result}")
    time.sleep(3)
    
    print("测试完成！如果Caps Lock开着，应该已经切换到持仓页面")

if __name__ == "__main__":
    test_mdi_frame()
