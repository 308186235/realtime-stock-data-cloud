import win32api
import win32con
import win32clipboard
import win32gui
import time

def debug_clipboard_input(text):
    """调试版剪贴板输入"""
    print(f"🔍 调试输入: {text}")
    
    try:
        # 1. 检查剪贴板状态
        print("1. 检查剪贴板...")
        try:
            win32clipboard.OpenClipboard()
            original = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            print(f"   原剪贴板内容: '{original}'")
        except Exception as e:
            print(f"   ❌ 读取剪贴板失败: {e}")
            original = ""
        
        # 2. 设置剪贴板
        print("2. 设置剪贴板...")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        print(f"   ✅ 剪贴板已设置: '{text}'")
        time.sleep(0.1)
        
        # 3. 验证剪贴板
        print("3. 验证剪贴板...")
        win32clipboard.OpenClipboard()
        clipboard_content = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        print(f"   剪贴板验证: '{clipboard_content}'")
        
        if clipboard_content != str(text):
            print(f"   ❌ 剪贴板验证失败!")
            return False
        
        # 4. 检查窗口焦点
        print("4. 检查窗口焦点...")
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点窗口: '{window_title}'")
        
        # 5. 全选操作
        print("5. 执行全选...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        print("   ✅ 全选完成")
        
        # 6. 粘贴操作
        print("6. 执行粘贴...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
        print("   ✅ 粘贴完成")
        
        # 7. 验证输入结果
        print("7. 验证输入结果...")
        time.sleep(0.2)
        
        # 全选当前内容
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # 复制到剪贴板验证
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('C'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 检查结果
        win32clipboard.OpenClipboard()
        result_text = win32clipboard.GetClipboardData().strip()
        win32clipboard.CloseClipboard()
        print(f"   输入结果: '{result_text}'")
        
        if result_text == str(text).strip():
            print("   ✅ 输入验证成功!")
            return True
        else:
            print(f"   ❌ 输入验证失败! 期望'{text}', 实际'{result_text}'")
            return False
            
        # 8. 恢复原剪贴板
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(original)
            win32clipboard.CloseClipboard()
        except:
            pass
            
    except Exception as e:
        print(f"❌ 调试输入异常: {e}")
        return False

def debug_keyboard_input(text):
    """调试版键盘输入"""
    print(f"⌨️ 调试键盘输入: {text}")
    
    try:
        # 1. 检查窗口焦点
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")
        
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
        print("   逐字符输入...")
        for i, char in enumerate(str(text)):
            print(f"     输入字符 {i+1}/{len(text)}: '{char}'")
            
            if char.isdigit():
                key_code = ord(char)
                win32api.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
            elif char == '.':
                win32api.keybd_event(0xBE, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
        
        print("   ✅ 键盘输入完成")
        time.sleep(0.3)
        return True
        
    except Exception as e:
        print(f"❌ 键盘输入异常: {e}")
        return False

def test_input_methods():
    """测试输入方法"""
    print("🧪 输入方法调试测试")
    print("=" * 50)
    
    print("请先手动点击交易软件的输入框，然后按回车继续...")
    input()
    
    # 测试剪贴板方法
    print("\n📋 测试剪贴板输入方法")
    print("-" * 30)
    test_text = "000001"
    success = debug_clipboard_input(test_text)
    
    if not success:
        print("\n⌨️ 剪贴板失败，测试键盘输入方法")
        print("-" * 30)
        debug_keyboard_input(test_text)
    
    print("\n请检查交易软件中是否正确显示了: 000001")
    
    # 测试数量输入
    print("\n请手动点击数量输入框，然后按回车继续...")
    input()
    
    print("\n📋 测试数量输入")
    print("-" * 30)
    test_quantity = "100"
    success = debug_clipboard_input(test_quantity)
    
    if not success:
        print("\n⌨️ 剪贴板失败，测试键盘输入方法")
        print("-" * 30)
        debug_keyboard_input(test_quantity)
    
    print("\n请检查交易软件中是否正确显示了: 100")

if __name__ == "__main__":
    test_input_methods()
