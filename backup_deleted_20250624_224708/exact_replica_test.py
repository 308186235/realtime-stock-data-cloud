import win32gui
import win32api
import win32con
import time

def ensure_caps_lock_on():
    """确保Caps Lock开启 - 与程序中完全相同"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if caps_state == 0:
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    return True

def switch_to_trading_software():
    """切换到交易软件 - 与程序中完全相同"""
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # 验证是否成功
            current_hwnd = win32gui.GetForegroundWindow()
            current_title = win32gui.GetWindowText(current_hwnd)
            print(f"✅ 成功切换到: {current_title}")
            
            return hwnd == current_hwnd
        else:
            print("❌ 没找到交易软件窗口")
            return False
    except Exception as e:
        print(f"❌ 切换窗口失败: {e}")
        return False

def click_center_area():
    """点击交易软件中央区域获取焦点 - 与程序中完全相同"""
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
        return True
    return False

def exact_replica_w_key():
    """完全复制程序中W键的发送流程"""
    print("🔄 切换到交易软件...")
    if not switch_to_trading_software():
        print("❌ 初始切换失败")
        return False
    
    print("\n📊 导出持仓数据")
    print("----------------------------------------")
    print("🔄 切换到交易软件...")
    switch_to_trading_software()  # 再次切换，模拟程序流程
    
    print("\n开始导出持仓...")
    print("1. 按W键进入持仓页面...")
    print("   发送W键...")
    print("   [调试] 重置状态确保W键能工作...")
    
    # 1. 重新切换到交易软件
    print("🔄 切换到交易软件...")
    if not switch_to_trading_software():
        print("   ❌ 无法切换到交易软件")
        return False
    
    # 2. 点击中央区域获取焦点
    click_center_area()
    
    # 3. 确保Caps Lock开启
    ensure_caps_lock_on()
    
    # 4. 等待状态稳定
    time.sleep(0.5)
    
    print("   [调试] 发送W键...")
    # 5. 发送W键 - 与程序中完全相同
    win32api.keybd_event(0x57, 0, 0, 0)  # W键按下 (虚拟键码)
    win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W键释放
    time.sleep(0.2)  # 快速切换，0.2秒后开始导出
    print("   [调试] W键发送完成")
    
    print("   等待持仓页面加载完成...")
    
    return True

def exact_replica_e_key():
    """完全复制程序中E键的发送流程"""
    print("\n📊 导出成交数据")
    print("----------------------------------------")
    print("🔄 切换到交易软件...")
    switch_to_trading_software()
    
    print("开始导出成交...")
    print("1. 按E键进入成交页面...")
    print("   [调试] 重置状态确保E键能工作...")
    
    # 1. 重新切换到交易软件
    print("🔄 切换到交易软件...")
    if not switch_to_trading_software():
        print("   ❌ 无法切换到交易软件")
        return False
    
    # 2. 点击中央区域获取焦点
    click_center_area()
    
    # 3. 确保Caps Lock开启
    ensure_caps_lock_on()
    
    # 4. 等待状态稳定
    time.sleep(0.5)
    
    print("   [调试] 发送E键...")
    # 5. 发送E键
    win32api.keybd_event(0x45, 0, 0, 0)  # E键按下 (虚拟键码)
    win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E键释放
    time.sleep(0.2)  # 快速切换，0.2秒后开始导出
    print("   [调试] E键发送完成")
    
    print("   等待成交页面加载完成...")
    
    return True

def exact_replica_r_key():
    """完全复制程序中R键的发送流程"""
    print("\n📊 导出委托数据")
    print("----------------------------------------")
    print("🔄 切换到交易软件...")
    switch_to_trading_software()
    
    print("开始导出委托...")
    print("1. 按R键进入委托页面...")
    print("   [调试] 重置状态确保R键能工作...")
    
    # 1. 重新切换到交易软件
    print("🔄 切换到交易软件...")
    if not switch_to_trading_software():
        print("   ❌ 无法切换到交易软件")
        return False
    
    # 2. 点击中央区域获取焦点
    click_center_area()
    
    # 3. 确保Caps Lock开启
    ensure_caps_lock_on()
    
    # 4. 等待状态稳定
    time.sleep(0.5)
    
    print("   [调试] 发送R键...")
    # 5. 发送R键
    win32api.keybd_event(0x52, 0, 0, 0)  # R键按下 (虚拟键码)
    win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)  # R键释放
    time.sleep(0.2)  # 快速切换，0.2秒后开始导出
    print("   [调试] R键发送完成")
    
    print("   等待委托页面加载完成...")
    
    return True

def main():
    print("🔍 完全复制程序流程的W/E/R键测试")
    print("这个测试完全模拟working_trader_FIXED.py中的状态和流程")
    print("请确保交易软件已经打开")
    input("按回车开始测试...")
    
    # 测试W键
    print("\n" + "="*60)
    print("测试W键 - 完全复制程序流程")
    print("="*60)
    exact_replica_w_key()
    result_w = input("W键是否切换了页面？(y/n): ").strip().lower() == 'y'
    
    # 测试E键
    print("\n" + "="*60)
    print("测试E键 - 完全复制程序流程")
    print("="*60)
    exact_replica_e_key()
    result_e = input("E键是否切换了页面？(y/n): ").strip().lower() == 'y'
    
    # 测试R键
    print("\n" + "="*60)
    print("测试R键 - 完全复制程序流程")
    print("="*60)
    exact_replica_r_key()
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
    elif any([result_w, result_e, result_r]):
        print("\n🤔 部分成功，说明状态重置有效但可能还有其他因素")
    else:
        print("\n❌ 全部失败，需要进一步调查其他可能的原因")

if __name__ == "__main__":
    main()
