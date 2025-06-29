import win32api
import win32con
import win32clipboard
import win32gui
import time
import pyautogui
import ctypes
from ctypes import wintypes

def test_all_input_methods():
    """测试所有可能的输入方法"""
    print("🧪 输入方法全面测试")
    print("=" * 50)
    
    print("请按以下步骤操作:")
    print("1. 打开交易软件买入界面")
    print("2. 手动点击'证券代码'输入框")
    print("3. 确保光标在输入框中")
    print("4. 按回车开始测试...")
    input()
    
    test_text = "000001"
    
    # 方法1: 剪贴板 + Ctrl+V
    print(f"\n🔸 方法1: 剪贴板 + Ctrl+V")
    test_clipboard_method(test_text)
    check_result("剪贴板方法")
    
    # 方法2: pyautogui
    print(f"\n🔸 方法2: pyautogui")
    test_pyautogui_method(test_text)
    check_result("pyautogui方法")
    
    # 方法3: SendInput API
    print(f"\n🔸 方法3: SendInput API")
    test_sendinput_method(test_text)
    check_result("SendInput方法")
    
    # 方法4: keybd_event 逐字符
    print(f"\n🔸 方法4: keybd_event逐字符")
    test_keybd_event_method(test_text)
    check_result("keybd_event方法")
    
    # 方法5: SendMessage
    print(f"\n🔸 方法5: SendMessage")
    test_sendmessage_method(test_text)
    check_result("SendMessage方法")

def test_clipboard_method(text):
    """测试剪贴板方法"""
    try:
        # 清空输入框
        clear_input_field()
        
        # 设置剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        # 粘贴
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print(f"   ✅ 剪贴板方法执行完成")
        
    except Exception as e:
        print(f"   ❌ 剪贴板方法失败: {e}")

def test_pyautogui_method(text):
    """测试pyautogui方法"""
    try:
        clear_input_field()
        pyautogui.typewrite(str(text), interval=0.05)
        time.sleep(0.3)
        print(f"   ✅ pyautogui方法执行完成")
    except Exception as e:
        print(f"   ❌ pyautogui方法失败: {e}")

def test_sendinput_method(text):
    """测试SendInput方法"""
    try:
        clear_input_field()
        
        # 使用ctypes SendInput
        for char in str(text):
            # 按下
            ctypes.windll.user32.keybd_event(ord(char), 0, 0, 0)
            time.sleep(0.02)
            # 释放
            ctypes.windll.user32.keybd_event(ord(char), 0, 2, 0)  # KEYEVENTF_KEYUP = 2
            time.sleep(0.05)
        
        time.sleep(0.3)
        print(f"   ✅ SendInput方法执行完成")
    except Exception as e:
        print(f"   ❌ SendInput方法失败: {e}")

def test_keybd_event_method(text):
    """测试keybd_event方法"""
    try:
        clear_input_field()
        
        for char in str(text):
            key_code = ord(char)
            win32api.keybd_event(key_code, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.08)
        
        time.sleep(0.3)
        print(f"   ✅ keybd_event方法执行完成")
    except Exception as e:
        print(f"   ❌ keybd_event方法失败: {e}")

def test_sendmessage_method(text):
    """测试SendMessage方法"""
    try:
        clear_input_field()
        
        # 获取当前焦点窗口
        hwnd = win32gui.GetForegroundWindow()
        
        # 尝试WM_SETTEXT
        ctypes.windll.user32.SendMessageW(hwnd, 0x000C, 0, str(text))  # WM_SETTEXT
        time.sleep(0.3)
        
        print(f"   ✅ SendMessage方法执行完成")
    except Exception as e:
        print(f"   ❌ SendMessage方法失败: {e}")

def clear_input_field():
    """清空输入框"""
    try:
        # Ctrl+A 全选
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # Delete
        win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    except:
        pass

def check_result(method_name):
    """检查结果"""
    result = input(f"   {method_name}是否成功输入了'000001'? (y/n): ").strip().lower()
    if result == 'y':
        print(f"   🎉 {method_name} 成功!")
        return True
    else:
        print(f"   ❌ {method_name} 失败")
        return False

def test_focus_and_input():
    """测试焦点和输入的组合"""
    print("\n🎯 焦点+输入组合测试")
    print("=" * 50)
    
    print("请手动点击证券代码输入框，然后按回车...")
    input()
    
    # 检查当前焦点
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    print(f"当前窗口: '{window_title}'")
    
    # 尝试获取焦点控件信息
    try:
        focus_hwnd = win32gui.GetFocus()
        if focus_hwnd:
            print(f"焦点控件句柄: {focus_hwnd}")
        else:
            print("无法获取焦点控件")
    except:
        print("获取焦点信息失败")
    
    # 测试最简单的输入
    print("\n测试最简单的数字输入...")
    try:
        # 直接按数字键
        for digit in "123":
            key_code = ord(digit)
            win32api.keybd_event(key_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        
        print("数字输入完成，请检查是否显示'123'")
        result = input("是否显示了'123'? (y/n): ").strip().lower()
        
        if result == 'y':
            print("✅ 基础数字输入成功!")
            print("问题可能在于:")
            print("1. 剪贴板内容被其他程序干扰")
            print("2. Ctrl+V组合键被拦截")
            print("3. 需要使用数字键而不是字母")
        else:
            print("❌ 连基础输入都失败")
            print("可能的原因:")
            print("1. 交易软件完全阻止程序输入")
            print("2. 需要管理员权限")
            print("3. 输入框有特殊保护")
            
    except Exception as e:
        print(f"数字输入失败: {e}")

if __name__ == "__main__":
    choice = input("选择测试: 1=全面测试, 2=焦点测试: ").strip()
    
    if choice == "1":
        test_all_input_methods()
    elif choice == "2":
        test_focus_and_input()
    else:
        print("无效选择")
