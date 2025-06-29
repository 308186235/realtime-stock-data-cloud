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

def find_all_target_windows():
    """找到所有可能的目标窗口"""
    main_hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if not main_hwnd:
        print("❌ 没找到主窗口")
        return []
    
    target_windows = []
    
    def enum_all_children(hwnd, level=0):
        def enum_child_proc(child_hwnd, param):
            class_name = win32gui.GetClassName(child_hwnd)
            window_text = win32gui.GetWindowText(child_hwnd)
            
            # 收集可能的目标窗口
            if any(cls in class_name for cls in ['AfxMDIFrame', 'CVirtualGridCtrl', 'AfxWnd', 'CCustomTabCtrl']):
                target_windows.append({
                    'hwnd': child_hwnd,
                    'class': class_name,
                    'text': window_text,
                    'level': level
                })
            
            # 递归枚举子窗口
            enum_all_children(child_hwnd, level + 1)
            return True
        
        win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
    
    enum_all_children(main_hwnd)
    return target_windows

def test_all_windows():
    print("测试发送W键到所有可能的窗口...")
    
    # 确保Caps Lock开启
    if not ensure_caps_lock_on():
        print("❌ 无法开启Caps Lock")
        return
    
    # 找到所有目标窗口
    windows = find_all_target_windows()
    print(f"找到 {len(windows)} 个可能的目标窗口")
    
    for i, window in enumerate(windows):
        print(f"\n{i+1}. 测试窗口: {hex(window['hwnd'])}")
        print(f"   类名: {window['class']}")
        print(f"   文本: '{window['text']}'")
        print(f"   层级: {window['level']}")
        
        # 发送W键
        try:
            result = win32api.PostMessage(window['hwnd'], win32con.WM_CHAR, ord('W'), 0)
            print(f"   发送结果: {result}")
            time.sleep(1)  # 短暂等待观察效果
        except Exception as e:
            print(f"   发送失败: {e}")
    
    print("\n所有窗口测试完成！观察交易软件是否有任何反应")

if __name__ == "__main__":
    test_all_windows()
