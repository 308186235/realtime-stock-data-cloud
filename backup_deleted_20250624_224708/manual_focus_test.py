import win32api
import win32con
import win32clipboard
import win32gui
import time

def test_manual_input():
    """手动焦点测试 - 用户手动点击后测试输入"""
    print("🧪 手动焦点输入测试")
    print("=" * 50)
    
    print("步骤:")
    print("1. 请手动打开交易软件的买入界面")
    print("2. 手动点击'证券代码'输入框")
    print("3. 确保光标在输入框中闪烁")
    print("4. 然后按回车继续测试...")
    input()
    
    # 测试股票代码输入
    print("\n🔤 测试输入股票代码: 000001")
    test_input_to_current_focus("000001")
    
    print("\n请检查证券代码输入框是否显示: 000001")
    result1 = input("是否正确显示？(y/n): ").strip().lower()
    
    if result1 == 'y':
        print("✅ 股票代码输入成功!")
        
        print("\n现在请手动点击'买入数量'输入框，然后按回车...")
        input()
        
        print("\n🔢 测试输入数量: 100")
        test_input_to_current_focus("100")
        
        print("\n请检查买入数量输入框是否显示: 100")
        result2 = input("是否正确显示？(y/n): ").strip().lower()
        
        if result2 == 'y':
            print("✅ 数量输入也成功!")
            print("🎉 输入方法验证成功!")
        else:
            print("❌ 数量输入失败")
    else:
        print("❌ 股票代码输入失败")
        print("可能的原因:")
        print("- 输入框不接受程序输入")
        print("- 需要特殊的输入方法")
        print("- 交易软件有安全限制")

def test_input_to_current_focus(text):
    """测试输入到当前焦点"""
    print(f"   📋 测试剪贴板输入: {text}")
    
    try:
        # 1. 检查当前焦点
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前窗口: '{window_title}'")
        
        # 2. 设置剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        # 3. 验证剪贴板
        win32clipboard.OpenClipboard()
        clipboard_content = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        print(f"   剪贴板内容: '{clipboard_content}'")
        
        # 4. 全选并粘贴
        print("   执行 Ctrl+A...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        print("   执行 Ctrl+V...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print("   ✅ 剪贴板操作完成")
        
        # 如果剪贴板失败，尝试键盘输入
        print("   🔄 同时测试键盘输入...")
        test_keyboard_input_to_current_focus(text)
        
    except Exception as e:
        print(f"   ❌ 剪贴板输入失败: {e}")

def test_keyboard_input_to_current_focus(text):
    """测试键盘输入到当前焦点"""
    print(f"   ⌨️ 测试键盘输入: {text}")
    
    try:
        # 清空
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
        
        # 逐字符输入
        for char in str(text):
            if char.isdigit():
                key_code = ord(char)
                win32api.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.08)
        
        print("   ✅ 键盘输入完成")
        
    except Exception as e:
        print(f"   ❌ 键盘输入失败: {e}")

def test_alternative_methods():
    """测试其他输入方法"""
    print("\n🔬 测试其他输入方法")
    print("=" * 50)
    
    print("请手动点击证券代码输入框，然后按回车...")
    input()
    
    # 方法1: SendMessage
    print("\n方法1: 尝试SendMessage...")
    try:
        hwnd = win32gui.GetForegroundWindow()
        # 尝试发送WM_SETTEXT消息
        import ctypes
        ctypes.windll.user32.SendMessageW(hwnd, 0x000C, 0, "000001")  # WM_SETTEXT
        print("   SendMessage完成")
    except Exception as e:
        print(f"   SendMessage失败: {e}")
    
    # 方法2: 模拟真实用户输入
    print("\n方法2: 模拟真实用户输入...")
    try:
        import pyautogui
        pyautogui.typewrite("000001", interval=0.1)
        print("   pyautogui输入完成")
    except Exception as e:
        print(f"   pyautogui失败: {e}")
    
    print("\n请检查哪种方法有效果...")

def comprehensive_test():
    """综合测试"""
    print("🎯 综合输入测试")
    print("=" * 50)
    
    print("这个测试将帮助确定:")
    print("1. 交易软件是否接受程序输入")
    print("2. 哪种输入方法有效")
    print("3. 是否需要特殊处理")
    
    choice = input("\n选择测试: 1=手动焦点测试, 2=其他方法测试: ").strip()
    
    if choice == "1":
        test_manual_input()
    elif choice == "2":
        test_alternative_methods()
    else:
        print("无效选择")

if __name__ == "__main__":
    comprehensive_test()
