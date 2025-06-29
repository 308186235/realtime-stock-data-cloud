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
    else:
        print("Caps Lock已开启")
    return True

def switch_to_trading_software():
    """切换到交易软件"""
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            print(f"找到交易软件窗口: {hex(hwnd)}")
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # 验证是否成功
            current_hwnd = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_hwnd)
            print(f"当前前台窗口: {current_title}")
            
            return hwnd == current_hwnd
        else:
            print("❌ 没找到交易软件窗口")
            return False
    except Exception as e:
        print(f"❌ 切换窗口失败: {e}")
        return False

def click_center_area():
    """点击交易软件中央区域获取焦点"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        print(f"点击中央区域: ({center_x}, {center_y})")
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        print("中央区域点击完成")
        return True
    return False

def send_key_with_full_setup(key_name, key_code):
    """使用完整设置发送按键 - 与程序中完全相同的流程"""
    print(f"\n{'='*50}")
    print(f"发送 {key_name} 键 - 完整流程")
    print(f"{'='*50}")
    
    print("1. 重新切换到交易软件...")
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件")
        return False
    
    print("2. 点击中央区域获取焦点...")
    click_center_area()
    
    print("3. 确保Caps Lock开启...")
    ensure_caps_lock_on()
    
    print("4. 等待状态稳定...")
    time.sleep(0.5)
    
    print(f"5. 发送 {key_name} 键...")
    win32api.keybd_event(key_code, 0, 0, 0)  # 按下
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    
    print(f"{key_name} 键发送完成！等待0.2秒...")
    time.sleep(0.2)
    
    result = input(f"{key_name} 键是否切换了页面？(y/n): ").strip().lower()
    return result == 'y'

def test_simple_method(key_name, key_code):
    """简单方法测试 - 可能失败的方法"""
    print(f"\n{'='*50}")
    print(f"简单方法测试 {key_name} 键")
    print(f"{'='*50}")
    
    print("直接发送按键...")
    win32api.keybd_event(key_code, 0, 0, 0)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)
    
    result = input(f"简单方法的 {key_name} 键是否切换了页面？(y/n): ").strip().lower()
    return result == 'y'

def main():
    print("🔍 对比测试：为什么单独测试W/E/R键不工作")
    print("请确保交易软件已经打开")
    input("按回车开始测试...")
    
    keys = [
        ("W", 0x57),
        ("E", 0x45),
        ("R", 0x52)
    ]
    
    for key_name, key_code in keys:
        print(f"\n🔄 测试 {key_name} 键...")
        
        # 方法1: 完整流程（与程序中相同）
        full_result = send_key_with_full_setup(key_name, key_code)
        
        # 方法2: 简单方法
        simple_result = test_simple_method(key_name, key_code)
        
        # 结果对比
        print(f"\n📊 {key_name} 键结果对比:")
        print(f"完整流程: {'✅ 成功' if full_result else '❌ 失败'}")
        print(f"简单方法: {'✅ 成功' if simple_result else '❌ 失败'}")
        
        if full_result and not simple_result:
            print(f"🔍 结论: {key_name} 键需要完整的状态设置才能工作")
        elif not full_result and not simple_result:
            print(f"❌ 问题: {key_name} 键两种方法都不工作，需要进一步调查")
        elif simple_result:
            print(f"✅ 好消息: {key_name} 键简单方法也能工作")
        
        input("按回车继续下一个键的测试...")
    
    print("\n🎯 测试完成！")
    print("如果完整流程能工作但简单方法不行，说明需要:")
    print("1. 正确的窗口切换")
    print("2. 中央区域点击获取焦点") 
    print("3. Caps Lock状态确认")
    print("4. 适当的等待时间")

if __name__ == "__main__":
    main()
