import win32api
import win32con
import win32clipboard
import win32gui
import time
import pyautogui

def ensure_trading_focus():
    """确保交易软件获得焦点"""
    print("🎯 确保交易软件焦点...")
    
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if not hwnd:
            print("❌ 找不到交易软件窗口")
            return False
        
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # 获取窗口位置并点击中央
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        print(f"   点击交易软件中央: ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)
        
        # 验证焦点
        current_hwnd = win32gui.GetForegroundWindow()
        current_title = win32gui.GetWindowText(current_hwnd)
        print(f"   当前焦点: '{current_title}'")
        
        if "交易系统" in current_title:
            print("   ✅ 交易软件已获得焦点")
            return True
        else:
            print("   ❌ 焦点仍不在交易软件")
            return False
            
    except Exception as e:
        print(f"   ❌ 设置焦点失败: {e}")
        return False

def reliable_clipboard_input(text):
    """可靠的剪贴板输入"""
    print(f"📋 可靠剪贴板输入: {text}")
    
    # 1. 确保交易软件焦点
    if not ensure_trading_focus():
        return False
    
    try:
        # 2. 保存原剪贴板
        original_clipboard = ""
        try:
            win32clipboard.OpenClipboard()
            original_clipboard = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
        except:
            pass
        
        # 3. 设置剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        # 4. 验证剪贴板
        win32clipboard.OpenClipboard()
        clipboard_content = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        
        if clipboard_content != str(text):
            print(f"   ❌ 剪贴板设置失败")
            return False
        
        print(f"   ✅ 剪贴板已设置: '{text}'")
        
        # 5. 再次确保焦点（防止被其他程序抢夺）
        ensure_trading_focus()
        
        # 6. 全选
        print("   执行全选...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 7. 粘贴
        print("   执行粘贴...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print(f"   ✅ 输入完成: {text}")
        
        # 8. 恢复原剪贴板
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(original_clipboard)
            win32clipboard.CloseClipboard()
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"   ❌ 剪贴板输入失败: {e}")
        return False

def reliable_keyboard_input(text):
    """可靠的键盘输入"""
    print(f"⌨️ 可靠键盘输入: {text}")
    
    # 1. 确保交易软件焦点
    if not ensure_trading_focus():
        return False
    
    try:
        # 2. 清空当前内容
        print("   清空内容...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 3. 逐字符输入
        print(f"   逐字符输入: {text}")
        for char in str(text):
            if char.isdigit():
                key_code = ord(char)
                win32api.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.08)
            elif char == '.':
                win32api.keybd_event(0xBE, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.08)
        
        print(f"   ✅ 键盘输入完成: {text}")
        time.sleep(0.2)
        return True
        
    except Exception as e:
        print(f"   ❌ 键盘输入失败: {e}")
        return False

def smart_input(text):
    """智能输入 - 自动选择最佳方法"""
    print(f"🧠 智能输入: {text}")
    
    # 方法1: 尝试剪贴板输入
    if reliable_clipboard_input(text):
        return True
    
    print("   剪贴板方法失败，尝试键盘输入...")
    
    # 方法2: 尝试键盘输入
    if reliable_keyboard_input(text):
        return True
    
    print(f"   ❌ 所有输入方法都失败了!")
    return False

def test_buy_with_fixed_input():
    """测试修复后的买入操作"""
    print("🧪 测试修复后的买入操作")
    print("=" * 50)
    
    try:
        # 1. 确保交易软件焦点
        if not ensure_trading_focus():
            print("❌ 无法获取交易软件焦点")
            return
        
        # 2. 进入买入界面
        print("\n1. 进入买入界面 (F2-F1)...")
        win32api.keybd_event(0x71, 0, 0, 0)  # F2
        time.sleep(0.05)
        win32api.keybd_event(0x71, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x70, 0, 0, 0)  # F1
        time.sleep(0.05)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)  # 等待界面切换
        
        # 3. 输入股票代码
        print("\n2. 输入股票代码...")
        if not smart_input("000001"):
            print("❌ 股票代码输入失败")
            return
        
        # 4. Tab到价格字段
        print("\n3. Tab到价格字段...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 5. Tab到数量字段
        print("\n4. Tab到数量字段...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 6. 输入数量
        print("\n5. 输入数量...")
        if not smart_input("100"):
            print("❌ 数量输入失败")
            return
        
        # 7. Tab离开输入框
        print("\n6. Tab离开输入框...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print("\n✅ 买入操作输入完成!")
        print("请检查交易软件中是否正确显示:")
        print("  股票代码: 000001")
        print("  数量: 100")
        
        # 询问是否确认买入
        confirm = input("\n是否确认买入？(y/n): ").strip().lower()
        if confirm == 'y':
            print("\n7. 确认买入 (Shift+B)...")
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(0x42, 0, 0, 0)  # B
            time.sleep(0.02)
            win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            print("✅ 买入确认完成!")
        else:
            print("❌ 用户取消买入")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_simple_input():
    """简单输入测试"""
    print("🧪 简单输入测试")
    print("=" * 50)
    
    print("请手动点击交易软件的任意输入框，然后按回车继续...")
    input()
    
    # 测试股票代码输入
    print("\n测试输入股票代码: 000001")
    smart_input("000001")
    
    print("\n请检查是否正确显示 000001，然后按回车继续...")
    input()
    
    # 测试数量输入
    print("\n测试输入数量: 100")
    smart_input("100")
    
    print("\n请检查是否正确显示 100")

if __name__ == "__main__":
    choice = input("选择测试: 1=简单输入测试, 2=完整买入测试: ").strip()
    
    if choice == "1":
        test_simple_input()
    elif choice == "2":
        test_buy_with_fixed_input()
    else:
        print("无效选择")
