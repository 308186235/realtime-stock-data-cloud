import win32gui
import win32api
import win32con
import time

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if caps_state == 0:
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    return True

def switch_to_trading_software():
    """切换到交易软件"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    return False

def click_center_area():
    """点击交易软件中央区域"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        print("   已点击中央区域")

def test_w_with_different_conditions():
    """测试不同条件下的W键"""
    print("🔍 测试W键在不同条件下的表现")
    
    ensure_caps_lock_on()
    
    conditions = [
        ("直接发送W键", lambda: None),
        ("点击中央后发送W键", click_center_area),
        ("等待1秒后发送W键", lambda: time.sleep(1)),
        ("点击中央+等待1秒后发送W键", lambda: (click_center_area(), time.sleep(1))),
    ]
    
    for i, (desc, prep_func) in enumerate(conditions, 1):
        print(f"\n{'='*50}")
        print(f"测试 {i}: {desc}")
        print(f"{'='*50}")
        
        # 切换到交易软件
        if not switch_to_trading_software():
            print("❌ 无法切换到交易软件")
            continue
        
        # 执行准备操作
        if prep_func:
            prep_func()
        
        print("准备发送W键...")
        time.sleep(1)
        
        # 发送W键
        print("发送W键...")
        win32api.keybd_event(0x57, 0, 0, 0)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("W键发送完成！等待3秒观察...")
        time.sleep(3)
        
        result = input("W键是否切换了页面？(y/n): ").strip().lower()
        if result == 'y':
            print(f"✅ 成功！条件: {desc}")
            return desc
        else:
            print(f"❌ 失败！条件: {desc}")
    
    print("\n❌ 所有条件都失败了")
    return None

def test_manual_comparison():
    """测试手动按键对比"""
    print(f"\n{'='*50}")
    print("手动按键对比测试")
    print(f"{'='*50}")
    
    ensure_caps_lock_on()
    switch_to_trading_software()
    
    print("现在请您手动按W键，观察是否切换页面")
    input("按回车继续...")
    
    manual_result = input("手动按W键是否切换了页面？(y/n): ").strip().lower()
    
    if manual_result == 'y':
        print("✅ 手动按键可以切换页面")
        print("问题可能在于程序发送的按键与手动按键有差异")
        
        print("\n现在测试程序发送的按键...")
        time.sleep(2)
        
        print("发送W键...")
        win32api.keybd_event(0x57, 0, 0, 0)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        time.sleep(3)
        program_result = input("程序发送的W键是否切换了页面？(y/n): ").strip().lower()
        
        if program_result == 'y':
            print("✅ 程序发送的按键也可以工作")
        else:
            print("❌ 程序发送的按键不工作，需要找到差异")
    else:
        print("❌ 手动按键也不能切换页面")
        print("可能是交易软件设置问题或快捷键被禁用")

if __name__ == "__main__":
    print("🔍 W键详细测试")
    print("请确保交易软件已经打开")
    input("按回车开始测试...")
    
    # 测试不同条件
    working_condition = test_w_with_different_conditions()
    
    # 手动对比测试
    test_manual_comparison()
    
    if working_condition:
        print(f"\n✅ 找到工作条件: {working_condition}")
    else:
        print("\n❌ 未找到工作条件，需要进一步调查")
