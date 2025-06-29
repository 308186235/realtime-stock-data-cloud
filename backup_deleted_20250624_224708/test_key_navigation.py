#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试W/E/R键页面切换功能
"""

import time
import win32api
import win32con
import win32gui

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

def switch_to_trading_software():
    """切换到交易软件"""
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "网上股票交易系统" in title:
                windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(enum_callback, windows)

    if windows:
        hwnd, title = windows[0]
        print(f"找到交易软件: {title}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    else:
        print("未找到交易软件窗口")
        return False

def test_key_with_multiple_methods(key_name, vk_code):
    """使用多种方法测试按键"""
    print(f"\n🧪 测试{key_name}键页面切换")
    print("=" * 40)
    
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件")
        return False
    
    ensure_caps_lock_on()
    time.sleep(0.5)
    
    print(f"准备发送{key_name}键，请观察交易软件界面变化...")
    input("按回车键继续...")
    
    # 方法1: 标准keybd_event
    print(f"方法1: 标准keybd_event发送{key_name}键...")
    win32api.keybd_event(vk_code, 0, 0, 0)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(2)
    
    response = input(f"页面是否切换到{key_name}对应的页面? (y/n): ")
    if response.lower() == 'y':
        print(f"✅ {key_name}键切换成功!")
        return True
    
    # 方法2: 带扫描码的keybd_event
    print(f"方法2: 带扫描码发送{key_name}键...")
    scan_codes = {'W': 0x11, 'E': 0x12, 'R': 0x13}
    scan_code = scan_codes.get(key_name, 0)
    
    win32api.keybd_event(vk_code, scan_code, 0, 0)
    win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(2)
    
    response = input(f"页面是否切换到{key_name}对应的页面? (y/n): ")
    if response.lower() == 'y':
        print(f"✅ {key_name}键切换成功!")
        return True
    
    # 方法3: PostMessage
    print(f"方法3: PostMessage发送{key_name}键...")
    try:
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            time.sleep(0.1)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            time.sleep(2)
            
            response = input(f"页面是否切换到{key_name}对应的页面? (y/n): ")
            if response.lower() == 'y':
                print(f"✅ {key_name}键切换成功!")
                return True
    except Exception as e:
        print(f"PostMessage方法失败: {e}")
    
    # 方法4: 组合键 Caps Lock + 字母
    print(f"方法4: 同时按住Caps Lock + {key_name}...")
    win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)  # Caps Lock按下
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, 0, 0)  # 字母键按下
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 字母键释放
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Caps Lock释放
    time.sleep(2)
    
    response = input(f"页面是否切换到{key_name}对应的页面? (y/n): ")
    if response.lower() == 'y':
        print(f"✅ {key_name}键切换成功!")
        return True
    
    print(f"❌ 所有方法都无法使{key_name}键生效")
    return False

def main():
    """主程序"""
    print("🔧 交易软件按键测试工具")
    print("=" * 50)
    print("此工具将测试W/E/R键是否能正确切换页面")
    print("请确保交易软件已经打开并登录")
    print("=" * 50)
    
    # 测试W键 (持仓页面)
    w_result = test_key_with_multiple_methods("W", 0x57)
    
    # 测试E键 (成交页面)  
    e_result = test_key_with_multiple_methods("E", 0x45)
    
    # 测试R键 (委托页面)
    r_result = test_key_with_multiple_methods("R", 0x52)
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📋 测试结果总结")
    print("=" * 50)
    print(f"W键 (持仓页面): {'✅ 成功' if w_result else '❌ 失败'}")
    print(f"E键 (成交页面): {'✅ 成功' if e_result else '❌ 失败'}")
    print(f"R键 (委托页面): {'✅ 成功' if r_result else '❌ 失败'}")
    
    if w_result or e_result or r_result:
        print("\n🎉 至少有一个按键工作正常!")
        print("💡 建议: 使用工作正常的方法更新导出脚本")
    else:
        print("\n⚠️ 所有按键测试都失败了")
        print("💡 可能的原因:")
        print("   1. 交易软件版本不支持这些快捷键")
        print("   2. 需要先进入特定的界面或模式")
        print("   3. 快捷键被禁用或更改")
        print("   4. 需要管理员权限")

if __name__ == "__main__":
    main()
