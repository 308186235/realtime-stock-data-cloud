import win32gui
import win32api
import win32con
import time

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

def test_w_key_to_mdi():
    print("测试发送W键到MDI Frame窗口...")
    
    # 确保Caps Lock开启
    if not ensure_caps_lock_on():
        print("❌ 无法开启Caps Lock")
        return
    
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
            return False
        return True
    
    win32gui.EnumChildWindows(main_hwnd, enum_child_proc, None)
    
    if not mdi_hwnd:
        print("❌ 没找到MDI Frame窗口")
        return
    
    print(f"✅ MDI Frame窗口: {hex(mdi_hwnd)}")
    
    print("准备发送W键...")
    time.sleep(1)
    
    # 发送W键到MDI Frame
    print("发送W键到MDI Frame...")
    win32api.PostMessage(mdi_hwnd, win32con.WM_CHAR, ord('W'), 0)
    time.sleep(2)
    
    print("发送完成！观察交易软件是否切换到持仓页面")
    
    # 再测试E键
    print("测试E键...")
    win32api.PostMessage(mdi_hwnd, win32con.WM_CHAR, ord('E'), 0)
    time.sleep(2)
    
    # 再测试R键
    print("测试R键...")
    win32api.PostMessage(mdi_hwnd, win32con.WM_CHAR, ord('R'), 0)
    time.sleep(2)
    
    print("所有测试完成！")

if __name__ == "__main__":
    test_w_key_to_mdi()
