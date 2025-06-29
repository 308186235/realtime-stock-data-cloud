#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能真正工作的交易代理
"""

import time
import win32api
import win32con
import win32gui
import datetime
import win32clipboard
import pyautogui  # 添加PyAutoGUI库用于更可靠的键盘输入

# 配置PyAutoGUI
pyautogui.FAILSAFE = True  # 启用安全模式
pyautogui.PAUSE = 0.1  # 设置操作间隔

# 尝试导入uiautomation库 - 专门的Windows UI自动化库
try:
    import uiautomation as auto
    UIAUTOMATION_AVAILABLE = True
    print("✅ uiautomation库可用")
except ImportError:
    UIAUTOMATION_AVAILABLE = False
    print("⚠️ uiautomation库不可用，将使用备用方法")

# 导入ctypes用于最底层的Windows API调用
import ctypes
from ctypes import wintypes, Structure, Union, c_ulong, c_ushort, c_short, c_long, byref

# 定义Windows INPUT结构体 - 用于SendInput API
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
        ("dx", c_long),
        ("dy", c_long),
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

# Windows常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

def send_key_with_sendinput(vk_code):
    """使用Windows SendInput API发送按键 - 最底层的方法"""
    try:
        # 获取user32.dll
        user32 = ctypes.windll.user32

        # 创建INPUT结构体数组
        inputs = (INPUT * 2)()

        # 按键按下
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].union.ki.wVk = vk_code
        inputs[0].union.ki.wScan = 0
        inputs[0].union.ki.dwFlags = 0
        inputs[0].union.ki.time = 0
        inputs[0].union.ki.dwExtraInfo = None

        # 按键释放
        inputs[1].type = INPUT_KEYBOARD
        inputs[1].union.ki.wVk = vk_code
        inputs[1].union.ki.wScan = 0
        inputs[1].union.ki.dwFlags = KEYEVENTF_KEYUP
        inputs[1].union.ki.time = 0
        inputs[1].union.ki.dwExtraInfo = None

        # 发送输入
        result = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
        return result == 2  # 成功发送2个输入事件

    except Exception as e:
        print(f"   [调试] SendInput失败: {e}")
        return False

def find_and_click_trading_button(button_text):
    """使用UIAutomation直接找到并点击交易软件中的按钮"""
    try:
        print(f"   [调试] 尝试找到并点击'{button_text}'按钮...")

        # 找到交易软件窗口
        trading_window = auto.WindowControl(searchDepth=1, Name="网上股票交易系统5.0")
        if not trading_window.Exists(3, 1):
            print("   [调试] 找不到交易软件窗口")
            return False

        print("   [调试] 找到交易软件窗口")

        # 尝试找到包含指定文本的按钮或控件
        # 方法1: 直接找按钮
        try:
            button = trading_window.ButtonControl(searchDepth=5, Name=button_text)
            if button.Exists(2):
                print(f"   [调试] 找到按钮: {button_text}")
                button.Click()
                time.sleep(2.0)
                return True
        except:
            pass

        # 方法2: 找包含文本的任何控件
        try:
            control = trading_window.Control(searchDepth=5, Compare=lambda c, d: button_text in c.Name)
            if control.Exists(2):
                print(f"   [调试] 找到控件: {control.Name}")
                control.Click()
                time.sleep(2.0)
                return True
        except:
            pass

        # 方法3: 遍历所有可点击的控件
        try:
            print("   [调试] 遍历所有控件寻找匹配项...")
            for control in trading_window.GetChildren():
                if button_text in control.Name:
                    print(f"   [调试] 找到匹配控件: {control.Name}")
                    control.Click()
                    time.sleep(2.0)
                    return True
        except Exception as e:
            print(f"   [调试] 遍历控件失败: {e}")

        print(f"   [调试] 未找到'{button_text}'按钮")
        return False

    except Exception as e:
        print(f"   [调试] UIAutomation查找按钮失败: {e}")
        return False

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

        # 尝试设置前台窗口（可能会失败，这是正常的）
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        except:
            pass

        # 强制切换方法：直接激活窗口
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
            # 备用方法：点击窗口中心
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
            print(f"⚠️ 强制切换可能失败，继续执行...")
            return True  # 继续执行，让键盘输入自己判断

    except Exception as e:
        print(f"❌ 切换失败: {e}")
        print("📋 请手动点击交易软件窗口，然后按回车继续...")
        input("按回车继续...")
        return True  # 假设用户已经切换了

def send_key_fast(vk_code):
    """快速发送按键"""
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.01)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    # 检查当前状态
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    print(f"   当前Caps Lock状态: {caps_state}")

    # 如果是关闭状态(0)，则按一次开启
    if caps_state == 0:
        print("   开启Caps Lock...")
        win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)  # 按下
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
        time.sleep(0.1)

        # 检查是否成功开启
        new_state = win32api.GetKeyState(win32con.VK_CAPITAL)
        print(f"   开启后Caps Lock状态: {new_state}")
    else:
        print("   Caps Lock已开启")

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
        # 计算表格区域的大概位置（窗口右侧中央区域）
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
    """清理过期的导出文件（15点后为过期）"""
    try:
        import glob
        import os
        from datetime import datetime, time

        print("🧹 清理过期导出文件...")

        # 获取当前时间
        now = datetime.now()

        # 判断过期时间：今天15点
        today_3pm = datetime.combine(now.date(), time(15, 0))

        # 如果现在还没到15点，则以昨天15点为过期时间
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
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # 如果文件在15点后，删除它
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        print(f"   🗑️ 删除过期文件: {file_path}")
                        deleted_count += 1

                except Exception as e:
                    print(f"   ❌ 删除文件失败 {file_path}: {e}")

        if deleted_count > 0:
            print(f"   ✅ 清理完成，删除了 {deleted_count} 个过期文件")
        else:
            print(f"   ✅ 没有过期文件需要清理")

    except Exception as e:
        print(f"   ❌ 清理过期文件失败: {e}")

def export_holdings():
    """导出持仓数据"""
    print("\n📊 导出持仓数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("\n开始导出持仓...")

    try:
        # 1. 按W键进入持仓页面
        print("1. 按W键进入持仓页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   发送W键...")
        print("   [调试] 重置状态确保W键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送W键...")
        # 5. 发送W键
        win32api.keybd_event(0x57, 0, 0, 0)  # W键按下 (虚拟键码)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] W键发送完成")

        print("   等待持仓页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("持仓数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名（不包含路径）
        print("4. 输入文件名...")
        print(f"   准备输入文件名: {filename}")
        clear_and_type(filename)
        time.sleep(0.5)  # 增加等待时间

        # 6. 按回车保存
        print("5. 按回车保存...")
        print(f"   保存文件: {filename}")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(2.0)  # 增加等待时间确保文件保存完成

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)

        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 持仓数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_transactions():
    """导出成交数据"""
    print("\n📊 导出成交数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("开始导出成交...")

    try:
        # 1. 按E键进入成交页面
        print("1. 按E键进入成交页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 重置状态确保E键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送E键...")
        # 5. 发送E键
        win32api.keybd_event(0x45, 0, 0, 0)  # E键按下 (虚拟键码)
        win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] E键发送完成")

        print("   等待成交页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("成交数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名
        print("4. 输入文件名...")
        clear_and_type(filename)
        time.sleep(0.1)

        # 6. 按回车保存
        print("5. 按回车保存...")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(1.0)  # 等待文件保存

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)

        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 成交数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_orders():
    """导出委托数据"""
    print("\n📊 导出委托数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("开始导出委托...")

    try:
        # 1. 按R键进入委托页面
        print("1. 按R键进入委托页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 重置状态确保R键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送R键...")
        # 5. 发送R键
        win32api.keybd_event(0x52, 0, 0, 0)  # R键按下 (虚拟键码)
        win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)  # R键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] R键发送完成")

        print("   等待委托页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("委托数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名
        print("4. 输入文件名...")
        clear_and_type(filename)
        time.sleep(0.1)

        # 6. 按回车保存
        print("5. 按回车保存...")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(1.0)  # 等待文件保存

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)

        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 委托数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

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

        # 如果不是交易软件，提醒用户
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
    """逐字符输入文本（可靠方法）- 修复版"""
    print(f"   ⌨️ 键盘输入: {text}")

    try:
        # 检查当前焦点窗口
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        print(f"   当前焦点: '{window_title}'")

        # 如果不是交易软件，提醒用户
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

# 为了兼容性，保留原函数名
def clear_and_type(text):
    """清空并输入文本 - 优先使用剪贴板方法"""
    # 如果包含中文，使用剪贴板方法
    if any('\u4e00' <= char <= '\u9fff' for char in str(text)):
        clear_and_type_fast(text)
    else:
        clear_and_type_slow(text)

def buy_stock(code, price, quantity):
    """买入股票"""
    print(f"\n🚀 买入操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("\n开始买入操作...")

    try:
        # 2. 按F2-F1进入买入界面
        print("\n1. 按F2-F1进入买入界面...")
        send_key_fast(0x71)  # F2
        time.sleep(0.1)
        send_key_fast(0x70)  # F1
        time.sleep(0.5)

        # 3. 输入股票代码 (应该已经在证券代码框)
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 4. Tab到买入数量框 (2次Tab)
        print("\n3. Tab到买入数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 5. 输入数量
        print("\n4. 输入买入数量...")
        clear_and_type(quantity)
        time.sleep(0.5)

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 自动按B键确认买入
        print("\n7. 按B键确认买入...")
        # 按住Shift + B 产生大写B
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, 0, 0)  # B键按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)  # B键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)
        
        print("\n✅ 买入操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def sell_stock(code, price, quantity):
    """卖出股票"""
    print(f"\n🚀 卖出操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
        return False

    print("\n开始卖出操作...")

    try:
        # 2. 按F1-F2进入卖出界面
        print("\n1. 按F1-F2进入卖出界面...")
        send_key_fast(0x70)  # F1
        time.sleep(0.1)
        send_key_fast(0x71)  # F2
        time.sleep(0.5)

        # 3. 输入股票代码 (应该已经在证券代码框)
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)

        # 4. Tab到卖出数量框 (2次Tab)
        print("\n3. Tab到卖出数量框...")

        # 2次Tab到达数量框
        for i in range(2):
            print(f"   Tab {i+1}/2...")
            send_key_fast(0x09)  # Tab
            time.sleep(0.3)

        # 5. 输入数量
        print("\n4. 输入卖出数量...")
        clear_and_type(quantity)
        time.sleep(0.5)

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 自动按S键确认卖出
        print("\n7. 按S键确认卖出...")
        # 按住Shift + S 产生大写S
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        time.sleep(0.5)
        
        print("\n✅ 卖出操作完成!")
        print("请检查交易软件中的输入是否正确")
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def main():
    """主程序"""
    print("🎯 能工作的交易代理")
    print("=" * 50)
    
    while True:
        print("\n请选择:")
        print("1. 买入")
        print("2. 卖出")
        print("3. 导出持仓")
        print("4. 导出成交")
        print("5. 导出委托")
        print("6. 退出")

        choice = input("选择 (1-6): ").strip()
        
        if choice == "1":
            code = input("股票代码 (默认600000): ").strip() or "600000"
            price = input("买入价格 (默认10.50): ").strip() or "10.50"
            quantity = input("买入数量 (默认100): ").strip() or "100"
            buy_stock(code, price, quantity)
            
        elif choice == "2":
            code = input("股票代码 (默认600000): ").strip() or "600000"
            price = input("卖出价格 (默认10.60): ").strip() or "10.60"
            quantity = input("卖出数量 (默认100): ").strip() or "100"
            sell_stock(code, price, quantity)
            
        elif choice == "3":
            export_holdings()

        elif choice == "4":
            export_transactions()

        elif choice == "5":
            export_orders()

        elif choice == "6":
            print("退出")
            break

        else:
            print("无效选择")

if __name__ == "__main__":
    main()
