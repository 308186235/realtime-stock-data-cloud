import win32gui
import win32api
import win32con
import time
import ctypes
from ctypes import wintypes, Structure, Union, c_ulong, c_ushort, c_short, c_long, byref

# 定义Windows INPUT结构体
class KEYBDINPUT(Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

class MOUSEINPUT(Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

class HARDWAREINPUT(Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class INPUT_UNION(Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION)
    ]

# 常量定义
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

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
        return new_state != 0
    else:
        print("Caps Lock已开启")
        return True

def send_key_with_sendinput(vk_code, scan_code):
    """使用SendInput发送键盘输入"""
    print(f"使用SendInput发送键: VK={hex(vk_code)}, Scan={hex(scan_code)}")
    
    # 创建INPUT结构体数组
    inputs = (INPUT * 2)()
    
    # 按键按下
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].union.ki.wVk = vk_code
    inputs[0].union.ki.wScan = scan_code
    inputs[0].union.ki.dwFlags = KEYEVENTF_SCANCODE  # 使用扫描码
    inputs[0].union.ki.time = 0
    inputs[0].union.ki.dwExtraInfo = None
    
    # 按键释放
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].union.ki.wVk = vk_code
    inputs[1].union.ki.wScan = scan_code
    inputs[1].union.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    inputs[1].union.ki.time = 0
    inputs[1].union.ki.dwExtraInfo = None
    
    # 发送输入
    result = ctypes.windll.user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    print(f"SendInput结果: {result}")
    return result == 2

def activate_trading_window():
    """激活交易软件窗口"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        print(f"找到交易软件窗口: {hex(hwnd)}")
        # 强制激活窗口
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    else:
        print("❌ 没找到交易软件窗口")
        return False

def test_real_keyboard_input():
    """测试真实键盘输入"""
    print("测试使用SendInput模拟真实键盘输入...")
    
    # 确保Caps Lock开启
    if not ensure_caps_lock_on():
        print("❌ 无法开启Caps Lock")
        return
    
    # 激活交易软件窗口
    if not activate_trading_window():
        return
    
    print("准备发送W键...")
    time.sleep(2)
    
    # W键的虚拟键码和扫描码
    W_VK = 0x57
    W_SCAN = 0x11
    
    print("方法1: SendInput with 扫描码")
    if send_key_with_sendinput(W_VK, W_SCAN):
        print("✅ W键发送成功")
    else:
        print("❌ W键发送失败")
    
    time.sleep(3)
    
    # 测试E键
    print("测试E键...")
    E_VK = 0x45
    E_SCAN = 0x12
    
    if send_key_with_sendinput(E_VK, E_SCAN):
        print("✅ E键发送成功")
    else:
        print("❌ E键发送失败")
    
    time.sleep(3)
    
    # 测试R键
    print("测试R键...")
    R_VK = 0x52
    R_SCAN = 0x13
    
    if send_key_with_sendinput(R_VK, R_SCAN):
        print("✅ R键发送成功")
    else:
        print("❌ R键发送失败")
    
    time.sleep(2)
    print("所有测试完成！观察交易软件是否切换页面")

if __name__ == "__main__":
    test_real_keyboard_input()
