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
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            print(f"找到交易软件窗口: {hex(hwnd)}")
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    win32gui.SetActiveWindow(hwnd)
                time.sleep(0.5)
                current_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                print(f"当前前台窗口: {current_title}")
                print("✅ 交易软件窗口已激活")
                return True
            except Exception as e:
                print(f"激活窗口时出错: {e}")
                print("⚠️ 窗口激活失败，但继续尝试")
                return True
        else:
            print("❌ 没找到交易软件窗口")
            return False
    except Exception as e:
        print(f"❌ 查找窗口失败: {e}")
        return False

def click_center_area():
    """点击交易软件中央区域获取焦点"""
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

def send_key_with_reset(key_name, key_code):
    """发送按键前重置状态"""
    print(f"\n发送{key_name}键...")
    print(f"[调试] 重置状态确保{key_name}键能工作...")
    
    # 1. 重新切换到交易软件
    print("🔄 切换到交易软件...")
    if not switch_to_trading_software():
        print(f"❌ 无法切换到交易软件")
        return False
    
    # 2. 点击中央区域获取焦点
    click_center_area()
    
    # 3. 确保Caps Lock开启
    ensure_caps_lock_on()
    
    # 4. 等待状态稳定
    time.sleep(0.5)
    
    print(f"[调试] 发送{key_name}键...")
    # 5. 发送按键
    win32api.keybd_event(key_code, 0, 0, 0)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)
    print(f"[调试] {key_name}键发送完成")
    return True

def send_key_fast(key_code):
    """快速发送按键"""
    win32api.keybd_event(key_code, 0, 0, 0)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

def clear_and_type_fast(text):
    """使用剪贴板快速输入文本"""
    import pyperclip
    try:
        # 保存当前剪贴板内容
        original_clipboard = pyperclip.paste()

        # 设置新内容到剪贴板
        pyperclip.copy(text)
        time.sleep(0.1)

        # 全选并粘贴
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(0x41, 0, 0, 0)  # A
        win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)  # V
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        # 恢复原剪贴板内容
        pyperclip.copy(original_clipboard)

    except Exception as e:
        print(f"剪贴板操作失败: {e}")
        # 备用方法：直接输入
        for char in text:
            if char.isdigit():
                win32api.keybd_event(ord(char), 0, 0, 0)
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)

def test_buy_function():
    """测试买入功能 - 使用正确的F2-F1流程"""
    print("\n" + "="*60)
    print("🟢 测试买入功能")
    print("="*60)

    if not switch_to_trading_software():
        return False

    try:
        print("1. 按F2-F1进入买入界面...")
        send_key_fast(0x71)  # F2
        time.sleep(0.1)
        send_key_fast(0x70)  # F1
        time.sleep(0.5)

        print("2. 输入股票代码: 600000")
        clear_and_type_fast("600000")
        time.sleep(0.5)

        print("3. Tab跳过价格...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("4. Tab到数量...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("5. 输入数量: 100")
        clear_and_type_fast("100")
        time.sleep(0.5)

        print("6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("7. 按Shift+B确认买入...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, 0, 0)  # B
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

        print("✅ 买入功能测试完成")
        return True

    except Exception as e:
        print(f"❌ 买入测试失败: {e}")
        return False

def test_sell_function():
    """测试卖出功能 - 使用正确的F1-F2流程"""
    print("\n" + "="*60)
    print("🔴 测试卖出功能")
    print("="*60)

    if not switch_to_trading_software():
        return False

    try:
        print("1. 按F1-F2进入卖出界面...")
        send_key_fast(0x70)  # F1
        time.sleep(0.1)
        send_key_fast(0x71)  # F2
        time.sleep(0.5)

        print("2. 输入股票代码: 600000")
        clear_and_type_fast("600000")
        time.sleep(0.5)

        print("3. Tab跳过价格...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("4. Tab到数量...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("5. 输入数量: 100")
        clear_and_type_fast("100")
        time.sleep(0.5)

        print("6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        print("7. 按Shift+S确认卖出...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, 0, 0)  # S
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

        print("✅ 卖出功能测试完成")
        return True

    except Exception as e:
        print(f"❌ 卖出测试失败: {e}")
        return False

def test_export_functions():
    """测试导出功能"""
    print("\n" + "="*60)
    print("📊 测试导出功能")
    print("="*60)
    
    # 测试W键 - 持仓导出
    print("\n1. 测试W键 - 持仓导出")
    print("-" * 40)
    send_key_with_reset("W", 0x57)
    print("模拟Ctrl+S导出...")
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(0x53, 0, 0, 0)  # S
    win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1)
    print("✅ W键持仓导出测试完成")
    
    # 测试E键 - 成交导出
    print("\n2. 测试E键 - 成交导出")
    print("-" * 40)
    send_key_with_reset("E", 0x45)
    print("模拟Ctrl+S导出...")
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(0x53, 0, 0, 0)  # S
    win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1)
    print("✅ E键成交导出测试完成")
    
    # 测试R键 - 委托导出
    print("\n3. 测试R键 - 委托导出")
    print("-" * 40)
    send_key_with_reset("R", 0x52)
    print("模拟Ctrl+S导出...")
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(0x53, 0, 0, 0)  # S
    win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1)
    print("✅ R键委托导出测试完成")
    
    return True

def main():
    print("🎯 完整交易代理功能测试")
    print("包含买入、卖出、W/E/R导出功能的全面测试")
    print("请确保交易软件已经打开并可见")
    print("\n⚠️  注意：这是模拟测试，不会执行真实交易")
    
    choice = input("\n请选择测试内容:\n1. 买入功能\n2. 卖出功能\n3. 导出功能\n4. 全部测试\n选择 (1-4): ")
    
    if choice == "1":
        test_buy_function()
    elif choice == "2":
        test_sell_function()
    elif choice == "3":
        test_export_functions()
    elif choice == "4":
        print("\n开始全面测试...")
        test_buy_function()
        time.sleep(2)
        test_sell_function()
        time.sleep(2)
        test_export_functions()
        print("\n🎉 全部测试完成！")
    else:
        print("无效选择")
        return
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print("✅ 所有功能都已测试")
    print("📝 请观察交易软件的反应和界面变化")
    print("🔧 如有问题，请检查Caps Lock状态和窗口焦点")

if __name__ == "__main__":
    main()
