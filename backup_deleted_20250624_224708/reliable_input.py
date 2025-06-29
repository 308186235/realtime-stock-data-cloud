import win32api
import win32con
import win32clipboard
import win32gui
import time
import pyautogui

def safe_clipboard_input(text, max_retries=3):
    """安全的剪贴板输入，带重试和验证"""
    print(f"   🔄 安全输入: {text}")
    
    # 保存原剪贴板内容
    original_clipboard = ""
    try:
        win32clipboard.OpenClipboard()
        original_clipboard = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    except:
        pass
    
    for attempt in range(max_retries):
        try:
            print(f"   尝试 {attempt + 1}/{max_retries}...")
            
            # 1. 设置剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(str(text))
            win32clipboard.CloseClipboard()
            time.sleep(0.1)
            
            # 2. 验证剪贴板内容
            win32clipboard.OpenClipboard()
            clipboard_content = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            if clipboard_content != str(text):
                print(f"   ❌ 剪贴板验证失败: 期望'{text}', 实际'{clipboard_content}'")
                continue
            
            # 3. 确保窗口焦点
            ensure_trading_window_focus()
            time.sleep(0.1)
            
            # 4. 全选当前内容
            print("   📋 全选...")
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # 5. 粘贴
            print("   📋 粘贴...")
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)
            
            # 6. 验证输入结果（通过再次全选复制来验证）
            if verify_input_result(text):
                print(f"   ✅ 输入成功: {text}")
                break
            else:
                print(f"   ❌ 输入验证失败，重试...")
                
        except Exception as e:
            print(f"   ❌ 输入异常: {e}")
            
        time.sleep(0.2)  # 重试间隔
    
    else:
        print(f"   ❌ 输入失败，尝试备用方法...")
        return keyboard_input_fallback(text)
    
    # 恢复原剪贴板内容
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(original_clipboard)
        win32clipboard.CloseClipboard()
    except:
        pass
    
    return True

def verify_input_result(expected_text):
    """验证输入结果"""
    try:
        # 全选当前内容
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # 复制到剪贴板
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('C'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 检查剪贴板内容
        win32clipboard.OpenClipboard()
        actual_text = win32clipboard.GetClipboardData().strip()
        win32clipboard.CloseClipboard()
        
        return actual_text == str(expected_text).strip()
        
    except Exception as e:
        print(f"   验证异常: {e}")
        return False

def keyboard_input_fallback(text):
    """键盘输入备用方法"""
    print(f"   ⌨️ 键盘输入备用方法: {text}")
    
    try:
        # 先清空
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('A'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # 逐字符输入
        for char in str(text):
            if char.isdigit():
                # 数字键
                key_code = ord(char)
                win32api.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.08)
            elif char == '.':
                # 小数点
                win32api.keybd_event(0xBE, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.08)
        
        time.sleep(0.2)
        return True
        
    except Exception as e:
        print(f"   ❌ 键盘输入失败: {e}")
        return False

def ensure_trading_window_focus():
    """确保交易软件窗口获得焦点"""
    try:
        # 查找交易软件窗口
        hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
        if hwnd:
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            
            # 点击窗口中央确保焦点
            rect = win32gui.GetWindowRect(hwnd)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            pyautogui.click(center_x, center_y)
            time.sleep(0.1)
            
            return True
    except Exception as e:
        print(f"   窗口焦点设置失败: {e}")
    
    return False

def enhanced_buy_stock(code, quantity):
    """增强版买入操作 - 更可靠的输入"""
    print(f"\n🚀 增强版买入操作")
    print(f"代码: {code}, 数量: {quantity}")
    print("-" * 40)
    
    try:
        # 1. 确保窗口焦点
        if not ensure_trading_window_focus():
            print("❌ 无法获取交易软件焦点")
            return False
        
        # 2. 进入买入界面 F2-F1
        print("\n1. 进入买入界面...")
        win32api.keybd_event(0x71, 0, 0, 0)  # F2
        time.sleep(0.05)
        win32api.keybd_event(0x71, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x70, 0, 0, 0)  # F1
        time.sleep(0.05)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.8)  # 等待界面切换
        
        # 3. 输入股票代码
        print("\n2. 输入股票代码...")
        if not safe_clipboard_input(code):
            print("❌ 股票代码输入失败")
            return False
        
        # 4. Tab到价格字段（跳过）
        print("\n3. 跳过价格字段...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 5. Tab到数量字段
        print("\n4. 切换到数量字段...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 6. 输入数量
        print("\n5. 输入数量...")
        if not safe_clipboard_input(quantity):
            print("❌ 数量输入失败")
            return False
        
        # 7. Tab离开输入框
        print("\n6. 离开输入框...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 8. 确认买入 Shift+B
        print("\n7. 确认买入...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(0x42, 0, 0, 0)  # B
        time.sleep(0.02)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("\n✅ 买入操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

def enhanced_sell_stock(code, quantity):
    """增强版卖出操作 - 更可靠的输入"""
    print(f"\n🔴 增强版卖出操作")
    print(f"代码: {code}, 数量: {quantity}")
    print("-" * 40)
    
    try:
        # 1. 确保窗口焦点
        if not ensure_trading_window_focus():
            print("❌ 无法获取交易软件焦点")
            return False
        
        # 2. 进入卖出界面 F1-F2
        print("\n1. 进入卖出界面...")
        win32api.keybd_event(0x70, 0, 0, 0)  # F1
        time.sleep(0.05)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x71, 0, 0, 0)  # F2
        time.sleep(0.05)
        win32api.keybd_event(0x71, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.8)  # 等待界面切换
        
        # 3. 输入股票代码
        print("\n2. 输入股票代码...")
        if not safe_clipboard_input(code):
            print("❌ 股票代码输入失败")
            return False
        
        # 4. Tab到价格字段（跳过）
        print("\n3. 跳过价格字段...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 5. Tab到数量字段
        print("\n4. 切换到数量字段...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 6. 输入数量
        print("\n5. 输入数量...")
        if not safe_clipboard_input(quantity):
            print("❌ 数量输入失败")
            return False
        
        # 7. Tab离开输入框
        print("\n6. 离开输入框...")
        win32api.keybd_event(0x09, 0, 0, 0)  # Tab
        time.sleep(0.05)
        win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 8. 确认卖出 Shift+S
        print("\n7. 确认卖出...")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(0x53, 0, 0, 0)  # S
        time.sleep(0.02)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print("\n✅ 卖出操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 卖出操作失败: {e}")
        return False

def test_reliable_input():
    """测试可靠输入"""
    print("🧪 测试可靠输入功能")
    print("=" * 40)
    
    # 测试买入
    test_buy = input("测试买入？(y/n): ").strip().lower()
    if test_buy == 'y':
        code = input("股票代码 (默认000001): ").strip() or "000001"
        quantity = input("数量 (默认100): ").strip() or "100"
        enhanced_buy_stock(code, quantity)
    
    # 测试卖出
    test_sell = input("测试卖出？(y/n): ").strip().lower()
    if test_sell == 'y':
        code = input("股票代码 (默认000001): ").strip() or "000001"
        quantity = input("数量 (默认100): ").strip() or "100"
        enhanced_sell_stock(code, quantity)

if __name__ == "__main__":
    test_reliable_input()
