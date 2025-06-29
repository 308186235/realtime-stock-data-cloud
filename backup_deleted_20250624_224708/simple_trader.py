import win32api
import win32con
import win32gui
import time
import os
from datetime import datetime

def switch_to_trading_software():
    try:
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if '交易' in window_text or '股票' in window_text:
                    windows.append((hwnd, window_text))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            hwnd, title = windows[0]
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        return False
    except:
        return False

def generate_unique_filename(prefix):
    timestamp = datetime.now().strftime('%m%d_%H%M%S')
    return f'{prefix}_{timestamp}.csv'

def export_holdings():
    print('导出持仓数据')
    
    # 切换到交易软件
    if not switch_to_trading_software():
        print('无法切换到交易软件')
        return False
    
    try:
        # 直接按W键（Caps Lock已开启）
        print('按W键...')
        win32api.keybd_event(0x57, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        
        # 生成文件名
        filename = generate_unique_filename('持仓数据')
        
        # 按Ctrl+S
        print('按Ctrl+S...')
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('S'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        
        # 输入文件名
        print(f'输入文件名: {filename}')
        for char in filename:
            win32api.keybd_event(ord(char.upper()), 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
        
        # 按回车
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
        
        # 按N
        win32api.keybd_event(ord('N'), 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(ord('N'), 0, win32con.KEYEVENTF_KEYUP, 0)
        
        print(f'导出完成: {filename}')
        return True
        
    except Exception as e:
        print(f'导出失败: {e}')
        return False

def main():
    # 程序开始时开启Caps Lock一次
    print('开启Caps Lock...')
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if caps_state == 0:
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        print('Caps Lock已开启，程序运行期间保持开启')
    else:
        print('Caps Lock已经开启')
    
    while True:
        print('\n选择操作:')
        print('1. 导出持仓')
        print('2. 退出')
        
        choice = input('请选择: ')
        
        if choice == '1':
            export_holdings()
        elif choice == '2':
            break
        else:
            print('无效选择')

if __name__ == '__main__':
    main()
