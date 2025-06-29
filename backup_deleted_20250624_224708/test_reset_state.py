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

def send_key_with_reset(key_name, vk_code):
    """发送按键前重置状态"""
    print(f"\n发送 {key_name} 键...")
    
    # 重置状态
    print("1. 重新切换到交易软件...")
    switch_to_trading_software()
    
    print("2. 点击中央区域获取焦点...")
    click_center_area()
    
    print("3. 确保Caps Lock开启...")
    ensure_caps_lock_on()
    
    print("4. 等待状态稳定...")
    time.sleep(0.5)
    
    print(f"5. 发送 {key_name} 键...")
    win32api.keybd_event(vk_code, 0, 0, 0)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print(f"{key_name} 键发送完成！等待3秒...")
    time.sleep(3)

def test_sequential_keys():
    """测试连续发送W/E/R键"""
    print("🔍 测试连续发送W/E/R键（每次重置状态）")
    
    keys = [
        ("W", 0x57),
        ("E", 0x45), 
        ("R", 0x52),
        ("W", 0x57),  # 再次测试W键
    ]
    
    results = []
    
    for key_name, vk_code in keys:
        print(f"\n{'='*50}")
        print(f"测试 {key_name} 键")
        print(f"{'='*50}")
        
        send_key_with_reset(key_name, vk_code)
        
        result = input(f"{key_name} 键是否切换了页面？(y/n): ").strip().lower()
        results.append((key_name, result == 'y'))
        
        if result == 'y':
            print(f"✅ {key_name} 键成功！")
        else:
            print(f"❌ {key_name} 键失败！")
    
    # 显示结果
    print(f"\n{'='*50}")
    print("测试结果汇总:")
    print(f"{'='*50}")
    for key_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{key_name} 键: {status}")
    
    return results

def test_without_reset():
    """测试不重置状态的连续按键"""
    print(f"\n{'='*50}")
    print("对比测试：不重置状态的连续按键")
    print(f"{'='*50}")
    
    # 初始设置
    ensure_caps_lock_on()
    switch_to_trading_software()
    click_center_area()
    
    keys = [("W", 0x57), ("E", 0x45), ("R", 0x52)]
    
    for key_name, vk_code in keys:
        print(f"\n直接发送 {key_name} 键...")
        win32api.keybd_event(vk_code, 0, 0, 0)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(2)
        
        result = input(f"{key_name} 键是否切换了页面？(y/n): ").strip().lower()
        status = "✅ 成功" if result == 'y' else "❌ 失败"
        print(f"{key_name} 键: {status}")

if __name__ == "__main__":
    print("🔍 测试状态重置对W/E/R键的影响")
    print("请确保交易软件已经打开")
    input("按回车开始测试...")
    
    # 测试每次重置状态
    results = test_sequential_keys()
    
    # 测试不重置状态
    test_without_reset()
    
    # 分析结果
    success_count = sum(1 for _, success in results if success)
    print(f"\n📊 重置状态方法成功率: {success_count}/{len(results)}")
    
    if success_count > 0:
        print("✅ 重置状态方法有效果！")
    else:
        print("❌ 重置状态方法无效果，需要其他解决方案")
