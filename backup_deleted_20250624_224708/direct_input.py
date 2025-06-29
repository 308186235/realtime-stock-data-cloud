import win32api
import win32con
import win32gui
import time

def find_input_controls():
    """查找交易软件中的输入控件"""
    def enum_child_windows(hwnd, results):
        def callback(child_hwnd, _):
            class_name = win32gui.GetClassName(child_hwnd)
            window_text = win32gui.GetWindowText(child_hwnd)
            
            # 查找编辑框控件
            if 'edit' in class_name.lower() or 'input' in class_name.lower():
                results.append({
                    'hwnd': child_hwnd,
                    'class': class_name,
                    'text': window_text
                })
            return True
        
        win32gui.EnumChildWindows(hwnd, callback, None)
        return results
    
    # 查找交易软件主窗口
    main_hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if not main_hwnd:
        return []
    
    # 枚举子窗口
    controls = []
    enum_child_windows(main_hwnd, controls)
    
    print(f"找到 {len(controls)} 个输入控件:")
    for i, ctrl in enumerate(controls):
        print(f"{i}: {ctrl['class']} - {ctrl['text']}")
    
    return controls

def direct_send_text(hwnd, text):
    """直接向控件发送文本"""
    try:
        # 方法1: WM_SETTEXT
        win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, str(text))
        time.sleep(0.1)
        
        # 验证
        result = win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, 256, None)
        if result == str(text):
            print(f"✅ 直接发送成功: {text}")
            return True
        
        # 方法2: 逐字符发送
        win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, "")  # 清空
        for char in str(text):
            win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(0.01)
        
        time.sleep(0.1)
        result = win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, 256, None)
        if result == str(text):
            print(f"✅ 逐字符发送成功: {text}")
            return True
            
        print(f"❌ 直接发送失败: 期望'{text}', 实际'{result}'")
        return False
        
    except Exception as e:
        print(f"❌ 直接发送异常: {e}")
        return False

def smart_input_method(text):
    """智能输入方法 - 自动选择最佳方案"""
    print(f"🧠 智能输入: {text}")
    
    # 方案1: 查找并直接操作输入控件
    controls = find_input_controls()
    if controls:
        # 尝试向第一个编辑框发送
        if direct_send_text(controls[0]['hwnd'], text):
            return True
    
    # 方案2: 模拟键盘输入（当前焦点）
    print("尝试键盘输入...")
    return keyboard_input_with_validation(text)

def keyboard_input_with_validation(text):
    """带验证的键盘输入"""
    try:
        # 清空当前内容
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # 发送Delete确保清空
        win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # 逐字符输入
        for char in str(text):
            if char.isdigit():
                key_code = ord(char)
                win32api.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.03)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
            elif char == '.':
                win32api.keybd_event(0xBE, 0, 0, 0)  # 小数点
                time.sleep(0.03)
                win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
        
        time.sleep(0.2)
        print(f"✅ 键盘输入完成: {text}")
        return True
        
    except Exception as e:
        print(f"❌ 键盘输入失败: {e}")
        return False

def test_input_methods():
    """测试各种输入方法"""
    print("🧪 测试输入方法")
    print("=" * 40)
    
    print("请先手动点击交易软件的股票代码输入框，然后按回车继续...")
    input()
    
    # 测试股票代码输入
    test_code = "000001"
    print(f"\n测试输入股票代码: {test_code}")
    smart_input_method(test_code)
    
    time.sleep(2)
    
    print("\n请手动点击数量输入框，然后按回车继续...")
    input()
    
    # 测试数量输入
    test_quantity = "100"
    print(f"\n测试输入数量: {test_quantity}")
    smart_input_method(test_quantity)

if __name__ == "__main__":
    test_input_methods()
