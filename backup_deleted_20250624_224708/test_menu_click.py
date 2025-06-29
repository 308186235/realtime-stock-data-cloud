import win32gui
import win32api
import win32con
import time

def find_trading_window():
    """找到交易软件窗口"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        print(f"找到交易软件窗口: {hex(hwnd)}")
        return hwnd
    return None

def click_at_position(x, y):
    """在指定位置点击"""
    print(f"点击位置: ({x}, {y})")
    
    # 移动鼠标到指定位置
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    
    # 执行点击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.5)

def test_menu_navigation():
    """测试通过菜单导航"""
    print("测试通过菜单/标签页点击来切换页面...")
    
    hwnd = find_trading_window()
    if not hwnd:
        print("❌ 没找到交易软件窗口")
        return
    
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    
    # 获取窗口位置和大小
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    
    print(f"窗口位置: ({left}, {top}) 大小: {width}x{height}")
    
    # 尝试点击可能的标签页位置
    # 通常标签页在窗口顶部区域
    
    print("尝试点击可能的持仓标签...")
    # 点击窗口左上角区域（可能的持仓标签）
    click_x = left + 100
    click_y = top + 100
    click_at_position(click_x, click_y)
    time.sleep(2)
    
    print("尝试点击可能的成交标签...")
    # 点击稍微右边一点（可能的成交标签）
    click_x = left + 200
    click_y = top + 100
    click_at_position(click_x, click_y)
    time.sleep(2)
    
    print("尝试点击可能的委托标签...")
    # 点击再右边一点（可能的委托标签）
    click_x = left + 300
    click_y = top + 100
    click_at_position(click_x, click_y)
    time.sleep(2)
    
    # 尝试右键菜单
    print("尝试右键菜单...")
    click_x = left + width // 2
    click_y = top + height // 2
    
    # 右键点击
    win32api.SetCursorPos((click_x, click_y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    time.sleep(1)
    
    print("测试完成！观察是否有菜单出现或页面切换")

def test_alternative_keys():
    """测试其他可能的快捷键"""
    print("测试其他可能的快捷键...")
    
    hwnd = find_trading_window()
    if not hwnd:
        return
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    
    # 测试一些可能的替代快捷键
    alternative_keys = [
        (0x31, "1键"),  # 数字1
        (0x32, "2键"),  # 数字2  
        (0x33, "3键"),  # 数字3
        (win32con.VK_F1, "F1键"),
        (win32con.VK_F2, "F2键"),
        (win32con.VK_F3, "F3键"),
        (win32con.VK_TAB, "Tab键"),
    ]
    
    for vk_code, key_name in alternative_keys:
        print(f"测试 {key_name}...")
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
    
    print("替代快捷键测试完成！")

if __name__ == "__main__":
    test_menu_navigation()
    print("\n" + "="*50 + "\n")
    test_alternative_keys()
