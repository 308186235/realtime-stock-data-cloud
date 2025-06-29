import win32api
import win32con
import win32clipboard
import win32gui
import time

def simple_clipboard_input(text):
    """简单剪贴板输入 - 依赖用户手动点击焦点"""
    print(f"📋 剪贴板输入: {text}")
    
    try:
        # 1. 保存原剪贴板
        original_clipboard = ""
        try:
            win32clipboard.OpenClipboard()
            original_clipboard = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            print(f"   原剪贴板: '{original_clipboard}'")
        except:
            pass
        
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
        print(f"   剪贴板已设置: '{clipboard_content}'")
        
        if clipboard_content != str(text):
            print(f"   ❌ 剪贴板设置失败")
            return False
        
        # 4. 检查当前焦点
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")
        
        # 5. 全选
        print("   执行 Ctrl+A 全选...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 6. 粘贴
        print("   执行 Ctrl+V 粘贴...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print(f"   ✅ 粘贴完成")
        
        # 7. 恢复原剪贴板
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(original_clipboard)
            win32clipboard.CloseClipboard()
            print(f"   剪贴板已恢复")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"   ❌ 剪贴板输入失败: {e}")
        return False

def simple_keyboard_input(text):
    """简单键盘输入"""
    print(f"⌨️ 键盘输入: {text}")
    
    try:
        # 1. 检查当前焦点
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")
        
        # 2. 清空
        print("   清空当前内容...")
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
        for i, char in enumerate(str(text)):
            print(f"     输入字符 {i+1}: '{char}'")
            
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
        
        print(f"   ✅ 键盘输入完成")
        time.sleep(0.3)
        return True
        
    except Exception as e:
        print(f"   ❌ 键盘输入失败: {e}")
        return False

def test_input_step_by_step():
    """分步测试输入"""
    print("🧪 分步测试输入方法")
    print("=" * 50)
    
    # 测试1: 剪贴板输入股票代码
    print("\n📋 测试1: 剪贴板输入股票代码")
    print("请手动点击交易软件的股票代码输入框，然后按回车...")
    input()
    
    success = simple_clipboard_input("000001")
    print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
    
    print("\n请检查交易软件中是否显示 '000001'")
    result = input("是否正确显示？(y/n): ").strip().lower()
    
    if result != 'y':
        print("\n⌨️ 剪贴板失败，尝试键盘输入...")
        print("请再次点击股票代码输入框，然后按回车...")
        input()
        
        simple_keyboard_input("000001")
        print("\n请检查交易软件中是否显示 '000001'")
        input("按回车继续...")
    
    # 测试2: 输入数量
    print("\n📋 测试2: 输入数量")
    print("请手动点击交易软件的数量输入框，然后按回车...")
    input()
    
    success = simple_clipboard_input("100")
    print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
    
    print("\n请检查交易软件中是否显示 '100'")
    result = input("是否正确显示？(y/n): ").strip().lower()
    
    if result != 'y':
        print("\n⌨️ 剪贴板失败，尝试键盘输入...")
        print("请再次点击数量输入框，然后按回车...")
        input()
        
        simple_keyboard_input("100")
        print("\n请检查交易软件中是否显示 '100'")
        input("按回车继续...")
    
    print("\n🎯 测试总结:")
    print("如果两个输入都正确显示，说明输入方法可用!")
    print("如果有问题，可能需要:")
    print("1. 确保点击了正确的输入框")
    print("2. 确保输入框可以接受文本输入")
    print("3. 检查交易软件是否有特殊限制")

def test_with_working_trader():
    """结合working_trader测试"""
    print("🧪 结合working_trader测试")
    print("=" * 50)
    
    print("这将测试修复后的输入方法是否能在working_trader中工作")
    
    # 导入working_trader的函数
    try:
        from working_trader_FIXED import buy_stock
        
        print("\n准备测试买入操作...")
        print("请确保交易软件已打开")
        input("按回车开始...")
        
        # 使用修复后的输入方法
        print("\n🚀 开始买入测试...")
        result = buy_stock_with_fixed_input("000001", "市价", "100")
        
        if result:
            print("✅ 买入测试成功!")
        else:
            print("❌ 买入测试失败!")
            
    except ImportError as e:
        print(f"❌ 无法导入working_trader: {e}")

def buy_stock_with_fixed_input(code, price, quantity):
    """使用修复后输入方法的买入函数"""
    print(f"\n🚀 修复版买入操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)
    
    try:
        # 1. 进入买入界面
        print("\n1. 按F2-F1进入买入界面...")
        win32api.keybd_event(0x71, 0, 0, 0)  # F2
        time.sleep(0.05)
        win32api.keybd_event(0x71, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x70, 0, 0, 0)  # F1
        time.sleep(0.05)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
        
        # 2. 输入股票代码
        print("\n2. 输入股票代码...")
        if not simple_clipboard_input(code):
            print("   剪贴板失败，尝试键盘输入...")
            if not simple_keyboard_input(code):
                print("❌ 股票代码输入失败")
                return False
        
        # 3. Tab到价格
        print("\n3. Tab跳过价格...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 4. Tab到数量
        print("\n4. Tab到数量...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 5. 输入数量
        print("\n5. 输入数量...")
        if not simple_clipboard_input(quantity):
            print("   剪贴板失败，尝试键盘输入...")
            if not simple_keyboard_input(quantity):
                print("❌ 数量输入失败")
                return False
        
        # 6. Tab离开
        print("\n6. Tab离开输入框...")
        win32api.keybd_event(0x09, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        print("\n✅ 输入完成!")
        print("请检查交易软件中的输入是否正确")
        
        confirm = input("是否确认买入？(y/n): ").strip().lower()
        if confirm == 'y':
            print("\n7. 确认买入...")
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(0x42, 0, 0, 0)  # B
            time.sleep(0.02)
            win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            print("✅ 买入确认完成!")
        
        return True
        
    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

if __name__ == "__main__":
    print("选择测试:")
    print("1. 分步测试输入")
    print("2. 完整买入测试")
    
    choice = input("选择 (1-2): ").strip()
    
    if choice == "1":
        test_input_step_by_step()
    elif choice == "2":
        buy_stock_with_fixed_input("000001", "市价", "100")
    else:
        print("无效选择")
