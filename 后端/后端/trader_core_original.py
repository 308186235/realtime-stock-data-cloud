"""
交易核心功能 - 完全复制原版逻辑
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

        # 尝试设置前台窗口(可能会失败,这是正常的)
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        except:
            pass

        # 强制切换方法:直接激活窗口
        print("   强制激活交易软件窗口...")
        try:
            # 方法1: 强制置顶并激活
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(0.1)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(0.1)

            # 方法2: 强制设置前台窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)

        except Exception as e:
            print(f"   强制激活失败: {e}")
            # 备用方法:点击窗口中心
            try:
                rect = win32gui.GetWindowRect(hwnd)
                center_x = (rect[0] + rect[2]) // 2
                center_y = (rect[1] + rect[3]) // 2
                win32api.SetCursorPos((center_x, center_y))
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                time.sleep(0.3)
            except:
                pass

        # 最终验证
        current_hwnd = win32gui.GetForegroundWindow()
        current_title = win32gui.GetWindowText(current_hwnd)
        print(f"   最终窗口: {current_title}")

        if "交易" in current_title or "股票" in current_title:
            print(f"✅ 强制切换成功: {current_title}")
            return True
        else:
            print(f"⚠️ 强制切换可能失败,继续执行...")
            return True  # 继续执行,让键盘输入自己判断

    except Exception as e:
        print(f"❌ 切换失败: {e}")
        print("📋 请手动点击交易软件窗口,然后按回车继续...")
        input("按回车继续...")
        return True  # 假设用户已经切换了

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if caps_state == 0:
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    return True

def click_center_area():
    """点击交易软件中央区域获取焦点"""
    hwnd = win32gui.FindWindow(None, "网上股票交易系统5.0")
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2

        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        return True
    return False

def click_table_area():
    """点击表格区域获得焦点"""
    print("   点击表格区域...")

    # 首先强制切换到交易软件窗口
    if not switch_to_trading_software():
        print("   ❌ 无法切换到交易软件窗口")
        return False

    # 获取交易软件窗口
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        # 获取窗口矩形
        rect = win32gui.GetWindowRect(hwnd)
        # 计算表格区域的大概位置(窗口右侧中央区域)
        x = rect[0] + (rect[2] - rect[0]) * 0.7  # 窗口宽度的70%位置
        y = rect[1] + (rect[3] - rect[1]) * 0.5  # 窗口高度的50%位置

        # 点击该位置
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.1)

        print("   表格区域点击完成")
        return True

    print("   ❌ 无法获取窗口信息")
    return False

def generate_unique_filename(base_name, extension=".csv"):
    """生成带时间戳的唯一文件名"""
    timestamp = datetime.datetime.now().strftime("%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

def cleanup_old_export_files():
    """清理过期的导出文件(15点后为过期)"""
    try:
        print("🧹 清理过期导出文件...")

        # 获取当前时间
        now = datetime.datetime.now()

        # 判断过期时间:今天15点
        today_3pm = datetime.datetime.combine(now.date(), datetime.time(15, 0))

        # 如果现在还没到15点,则以昨天15点为过期时间
        if now < today_3pm:
            from datetime import timedelta
            yesterday_3pm = today_3pm - timedelta(days=1)
            cutoff_time = yesterday_3pm
            print(f"   当前时间: {now.strftime('%H:%M')}")
            print(f"   过期标准: 昨天15:00后的文件")
        else:
            cutoff_time = today_3pm
            print(f"   当前时间: {now.strftime('%H:%M')}")
            print(f"   过期标准: 今天15:00后的文件")

        # 查找所有导出文件
        patterns = [
            "持仓数据_*.csv",
            "成交数据_*.csv",
            "委托数据_*.csv",
            "测试过期文件_*.csv"  # 包含测试文件
        ]

        deleted_count = 0
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    # 获取文件修改时间
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                    # 如果文件在15点后,删除它
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

def clear_and_type_fast(text):
    """使用剪贴板快速输入文本 - 修复版"""
    print(f"   📋 剪贴板输入: {text}")

    try:
        # 保存原剪贴板内容
        original_clipboard = ""
        try:
            win32clipboard.OpenClipboard()
            original_clipboard = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
        except:
            pass

        # 将文本复制到剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.1)

        # 验证剪贴板内容
        win32clipboard.OpenClipboard()
        clipboard_content = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        if clipboard_content != str(text):
            print(f"   ❌ 剪贴板设置失败")
            raise Exception("剪贴板验证失败")

        print(f"   ✅ 剪贴板已设置: '{text}'")

        # 检查当前焦点窗口
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")

        # 如果不是交易软件,提醒用户
        if "交易系统" not in window_title:
            print(f"   ⚠️ 警告: 当前焦点不在交易软件!")

        # Ctrl+A 全选
        print(f"   执行全选...")
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('A'), 0, 0, 0)  # A down
        time.sleep(0.02)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.1)

        # Ctrl+V 粘贴
        print(f"   执行粘贴...")
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('V'), 0, 0, 0)  # V down
        time.sleep(0.02)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.3)

        print(f"   ✅ 粘贴完成")

        # 恢复原剪贴板内容
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(original_clipboard)
            win32clipboard.CloseClipboard()
        except:
            pass

    except Exception as e:
        print(f"   ❌ 剪贴板输入失败: {e}")
        print(f"   🔄 切换到键盘输入...")
        clear_and_type_slow(text)

def clear_and_type_slow(text):
    """逐字符输入文本(可靠方法)- 修复版"""
    print(f"   ⌨️ 键盘输入: {text}")

    try:
        # 检查当前焦点窗口
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")

        # 如果不是交易软件,提醒用户
        if "交易系统" not in window_title:
            print(f"   ⚠️ 警告: 当前焦点不在交易软件!")

        # Ctrl+A 全选
        print(f"   清空当前内容...")
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        time.sleep(0.05)
        win32api.keybd_event(ord('A'), 0, 0, 0)  # A down (大写A)
        time.sleep(0.05)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
        time.sleep(0.05)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.1)

        # 按Delete确保清空
        win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        # 逐字符输入
        print(f"   逐字符输入: {text}")
        for i, char in enumerate(str(text)):
            print(f"     输入字符 {i+1}/{len(text)}: '{char}'")

            if char.isdigit():
                # 输入数字
                win32api.keybd_event(ord(char), 0, 0, 0)  # 按下
                time.sleep(0.02)
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
                time.sleep(0.05)  # 字符间延迟 - 加快速度
            elif char == '.':
                # 输入小数点
                win32api.keybd_event(0xBE, 0, 0, 0)  # 按下
                time.sleep(0.02)
                win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
                time.sleep(0.05)
            elif char == '_':
                # 输入下划线
                win32api.keybd_event(0xBD, 0, 0, 0)  # 按下
                time.sleep(0.05)
                win32api.keybd_event(0xBD, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
                time.sleep(0.1)

        time.sleep(0.3)  # 输入完成后等待
        print(f"   ✅ 键盘输入完成: {text}")

    except Exception as e:
        print(f"   ❌ 键盘输入失败: {e}")

# 为了兼容性,保留原函数名
def clear_and_type(text):
    """清空并输入文本 - 优先使用剪贴板方法"""
    # 如果包含中文,使用剪贴板方法
    if any('\u4e00' <= char <= '\u9fff' for char in str(text)):
        clear_and_type_fast(text)
    else:
        clear_and_type_slow(text)
