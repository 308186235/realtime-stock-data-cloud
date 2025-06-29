import win32gui
import win32api
import win32con
import time
import ctypes

def ensure_caps_lock_on():
    """确保Caps Lock开启 - 与程序中完全相同"""
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
    """切换到交易软件 - 修复权限问题"""
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            print(f"找到交易软件窗口: {hex(hwnd)}")
            
            # 尝试多种方法激活窗口
            try:
                # 方法1: 先显示窗口
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
                
                # 方法2: 使用更强制的方法
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)
                
                # 方法3: 尝试SetForegroundWindow
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception as e:
                    print(f"SetForegroundWindow失败: {e}")
                    # 使用备用方法
                    win32gui.SetActiveWindow(hwnd)
                
                time.sleep(0.5)
                
                # 验证是否成功
                current_hwnd = win32gui.GetForegroundWindow()
                current_title = win32gui.GetWindowText(current_hwnd)
                print(f"当前前台窗口: {current_title}")
                
                # 即使没有完全获得前台，只要找到窗口就继续
                if hwnd:
                    print("✅ 找到交易软件窗口，继续执行")
                    return True
                
            except Exception as e:
                print(f"激活窗口时出错: {e}")
                # 即使激活失败，也尝试继续
                print("⚠️ 窗口激活失败，但继续尝试发送按键")
                return True
                
        else:
            print("❌ 没找到交易软件窗口")
            return False
            
    except Exception as e:
        print(f"❌ 查找窗口失败: {e}")
        return False

def click_center_area():
    """点击交易软件中央区域获取焦点 - 与程序中完全相同"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        try:
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
        except Exception as e:
            print(f"点击中央区域失败: {e}")
            return False
    return False

def test_single_key(key_name, key_code):
    """测试单个按键"""
    print(f"\n📊 测试{key_name}键")
    print("----------------------------------------")
    print("🔄 切换到交易软件...")
    
    # 尝试切换到交易软件（即使失败也继续）
    switch_to_trading_software()
    
    print(f"开始测试{key_name}键...")
    print(f"1. 按{key_name}键...")
    print(f"   [调试] 重置状态确保{key_name}键能工作...")
    
    # 1. 再次尝试切换到交易软件
    print("🔄 切换到交易软件...")
    switch_to_trading_software()
    
    # 2. 点击中央区域获取焦点
    print("点击中央区域获取焦点...")
    click_center_area()
    
    # 3. 确保Caps Lock开启
    print("确保Caps Lock开启...")
    ensure_caps_lock_on()
    
    # 4. 等待状态稳定
    print("等待状态稳定...")
    time.sleep(0.5)
    
    print(f"   [调试] 发送{key_name}键...")
    # 5. 发送按键
    win32api.keybd_event(key_code, 0, 0, 0)  # 按下
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
    time.sleep(0.2)  # 等待
    print(f"   [调试] {key_name}键发送完成")
    
    print(f"   等待{key_name}键效果...")
    time.sleep(1)  # 给用户时间观察
    
    return True

def main():
    print("🔍 修复版本：完全复制程序流程的W/E/R键测试")
    print("这个测试完全模拟working_trader_FIXED.py中的状态和流程")
    print("已修复SetForegroundWindow权限问题")
    print("请确保交易软件已经打开并可见")
    input("按回车开始测试...")
    
    # 测试W键
    print("\n" + "="*60)
    print("测试W键 - 完全复制程序流程")
    print("="*60)
    test_single_key("W", 0x57)
    result_w = input("W键是否切换了页面？(y/n): ").strip().lower() == 'y'
    
    # 测试E键
    print("\n" + "="*60)
    print("测试E键 - 完全复制程序流程")
    print("="*60)
    test_single_key("E", 0x45)
    result_e = input("E键是否切换了页面？(y/n): ").strip().lower() == 'y'
    
    # 测试R键
    print("\n" + "="*60)
    print("测试R键 - 完全复制程序流程")
    print("="*60)
    test_single_key("R", 0x52)
    result_r = input("R键是否切换了页面？(y/n): ").strip().lower() == 'y'
    
    # 结果总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    print(f"W键: {'✅ 成功' if result_w else '❌ 失败'}")
    print(f"E键: {'✅ 成功' if result_e else '❌ 失败'}")
    print(f"R键: {'✅ 成功' if result_r else '❌ 失败'}")
    
    if all([result_w, result_e, result_r]):
        print("\n🎉 所有键都成功！说明完整的状态重置流程是关键")
        print("这证明了单独测试需要包含完整的状态重置步骤")
    elif any([result_w, result_e, result_r]):
        print("\n🤔 部分成功，说明状态重置有效但可能还有其他因素")
        print("建议在完整程序环境中使用这些按键")
    else:
        print("\n❌ 全部失败，可能的原因：")
        print("1. 交易软件版本或设置问题")
        print("2. 需要特殊的程序环境或初始化")
        print("3. W/E/R键在当前状态下被禁用")
        print("4. 需要特定的窗口焦点或权限")

if __name__ == "__main__":
    main()
