"""
交易核心功能模块 - 基于trader_core_original.py
提供核心的窗口操作和键盘输入功能
"""

import win32api
import win32con
import win32gui
import win32clipboard
import time
import datetime
import glob
import os

def send_key_fast(vk_code):
    """快速发送按键"""
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.01)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)

def switch_to_trading_software():
    """切换到交易软件"""
    print("🔄 切换到交易软件...")

    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # 精确匹配交易软件
            if "网上股票交易系统5.0" in title or "网上股票交易系统" in title:
                windows.append((hwnd, title))
                print(f"   🔍 找到匹配窗口: {title}")
        return True

    windows = []
    win32gui.EnumWindows(enum_callback, windows)

    if not windows:
        print("❌ 未找到交易软件")
        return False

    hwnd, title = windows[0]
    try:
        # 尝试温和的窗口激活
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)

        # 尝试置顶窗口
        try:
            win32gui.BringWindowToTop(hwnd)
            time.sleep(0.5)
        except:
            pass

        # 设置焦点
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        except:
            pass

        print(f"✅ 成功切换到: {title}")
        return True

    except Exception as e:
        print(f"❌ 切换失败: {e}")
        return False

def clear_and_type(text):
    """清空并输入文本"""
    # 全选
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(0x41, 0, 0, 0)  # A
    time.sleep(0.01)
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    
    # 输入文本
    for char in str(text):
        if char.isdigit():
            # 数字键
            vk_code = ord(char)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)
        elif char == '.':
            # 小数点
            win32api.keybd_event(0xBE, 0, 0, 0)  # VK_OEM_PERIOD
            time.sleep(0.01)
            win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.02)

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if caps_state == 0:  # Caps Lock关闭
        print("   开启Caps Lock...")
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

def generate_unique_filename(prefix):
    """生成唯一文件名"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"

def cleanup_old_export_files():
    """清理过期的导出文件"""
    try:
        current_time = datetime.datetime.now()
        cutoff_time = current_time.replace(hour=15, minute=0, second=0, microsecond=0)
        
        # 如果当前时间在15点之前，使用前一天的15点作为截止时间
        if current_time < cutoff_time:
            cutoff_time = cutoff_time - datetime.timedelta(days=1)
        
        patterns = ["持仓数据_*.csv", "成交数据_*.csv", "委托数据_*.csv"]
        
        deleted_count = 0
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        print(f"   🗑️ 删除过期文件: {file_path}")
                        deleted_count += 1
                except Exception as e:
                    print(f"   ❌ 删除文件失败 {file_path}: {e}")
        
        if deleted_count > 0:
            print(f"   ✅ 清理完成,删除了 {deleted_count} 个过期文件")
        else:
            print(f"   ✅ 没有过期文件需要清理")
            
    except Exception as e:
        print(f"   ❌ 清理过期文件失败: {e}")

def get_current_focus():
    """获取当前焦点窗口信息"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        return hwnd, title
    except Exception as e:
        print(f"获取焦点窗口失败: {e}")
        return None, ""

def click_center_area():
    """点击中心区域"""
    try:
        # 获取屏幕尺寸
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        # 计算中心点
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # 点击中心
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.1)
        
    except Exception as e:
        print(f"点击中心区域失败: {e}")

def click_table_area():
    """点击表格区域"""
    try:
        # 获取屏幕尺寸
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        # 计算表格区域（屏幕中下部分）
        table_x = screen_width // 2
        table_y = int(screen_height * 0.6)
        
        # 点击表格区域
        win32api.SetCursorPos((table_x, table_y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.1)
        
    except Exception as e:
        print(f"点击表格区域失败: {e}")

if __name__ == "__main__":
    print("🧪 交易核心功能模块测试")
    print("=" * 50)
    
    # 测试基础功能
    hwnd, title = get_current_focus()
    print(f"当前焦点窗口: {title}")
    
    # 测试切换到交易软件
    if switch_to_trading_software():
        print("✅ 交易软件切换测试成功")
    else:
        print("❌ 交易软件切换测试失败")
    
    print("✅ 核心功能模块测试完成")
