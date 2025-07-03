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

def switch_to_trading_software():
    """切换到交易软件"""
    print("🔄 切换到交易软件...")

    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "网上股票交易系统" in title or "交易" in title:
                windows.append((hwnd, title))
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

        # 验证是否成功
        current_hwnd = win32gui.GetForegroundWindow()
        current_title = win32gui.GetWindowText(current_hwnd)

        if "交易" in current_title:
            print(f"✅ 成功切换到: {current_title}")
            return True
        else:
            print(f"⚠️ 当前窗口: {current_title}")
            print(f"🔍 找到交易软件: {title}")
            print("⚠️ 由于Windows安全限制,无法自动切换窗口")
            print("📋 请手动点击交易软件窗口,然后按回车继续...")
            input("按回车继续...")
            return True  # 假设用户已经切换了

    except Exception as e:
        print(f"❌ 切换失败: {e}")
        print("📋 请手动点击交易软件窗口,然后按回车继续...")
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

    # 如果是关闭状态(0),则按一次开启
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

def export_holdings():
    """导出持仓数据"""
    print("\n📊 导出持仓数据")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("\n开始导出持仓...")

    try:
        # 1. 按W键进入持仓页面
        print("1. 按W键进入持仓页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        # 发送W键前再次确保焦点
        switch_to_trading_software()
        time.sleep(0.1)

        print("   发送W键...")
        print("   [调试] 使用与N键相同的方式发送W键...")
        win32api.keybd_event(0x57, 0, 0, 0)  # W键按下 (虚拟键码)

        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W键释放
        time.sleep(2.0)  # 增加等待时间,让页面完全切换
        print("   等待持仓页面加载完成...")
        print("   [调试] 页面切换应该已完成")

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

        print(f"\n✅ 持仓数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_transactions():
    """导出成交数据"""
    print("\n📊 导出成交数据")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("开始导出成交...")

    try:
        # 1. 按E键进入成交页面
        print("1. 按E键进入成交页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 使用与N键相同的方式发送E键...")
        win32api.keybd_event(0x45, 0, 0, 0)  # E键按下 (虚拟键码)

        win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E键释放
        time.sleep(2.0)  # 增加等待时间,让页面完全切换
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

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("开始导出委托...")

    try:
        # 1. 按R键进入委托页面
        print("1. 按R键进入委托页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 使用与N键相同的方式发送R键...")
        win32api.keybd_event(0x52, 0, 0, 0)  # R键按下 (虚拟键码)

        win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)  # R键释放
        time.sleep(2.0)  # 增加等待时间,让页面完全切换
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
    """使用剪贴板快速输入文本"""
    print(f"   输入: {text}")

    try:
        # 将文本复制到剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.05)

        # Ctrl+A 全选
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('A'), 0, 0, 0)  # A down
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.05)

        # Ctrl+V 粘贴
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('V'), 0, 0, 0)  # V down
        time.sleep(0.01)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.05)

    except Exception as e:
        print(f"快速输入失败,使用备用方法: {e}")
        clear_and_type_slow(text)

def clear_and_type_slow(text):
    """逐字符输入文本(可靠方法)"""
    print(f"   逐字符输入: {text}")

    # Ctrl+A 全选
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    time.sleep(0.05)
    win32api.keybd_event(ord('A'), 0, 0, 0)  # A down (大写A)
    time.sleep(0.05)
    win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
    time.sleep(0.05)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
    time.sleep(0.1)

    # 输入每个字符
    for char in str(text):
        if char.isdigit():
            # 输入数字
            win32api.keybd_event(ord(char), 0, 0, 0)  # 按下
            time.sleep(0.05)
            win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
            time.sleep(0.1)  # 字符间延迟
        elif char == '.':
            # 输入小数点
            win32api.keybd_event(0xBE, 0, 0, 0)  # 按下
            time.sleep(0.05)
            win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
            time.sleep(0.1)
        elif char == '_':
            # 输入下划线
            win32api.keybd_event(0xBD, 0, 0, 0)  # 按下
            time.sleep(0.05)
            win32api.keybd_event(0xBD, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
            time.sleep(0.1)

    time.sleep(0.2)  # 输入完成后等待

# 为了兼容性,保留原函数名
def clear_and_type(text):
    """清空并输入文本 - 使用剪贴板方法"""
    clear_and_type_fast(text)

def buy_stock(code, price, quantity):
    """买入股票"""
    print(f"\n🚀 买入操作")
    print(f"代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 40)

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("\n开始买入操作...")

    try:
        # 2. 按F2-F1进入买入界面
        print("\n1. 按F2-F1进入买入界面...")
        send_key_fast(0x71)  # F2
        time.sleep(0.1)
        send_key_fast(0x70)  # F1
        time.sleep(0.5)

        # 3. 输入股票代码
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)  # 增加等待时间确保股票代码输入完成

        # 4. Tab(跳过价格)
        print("\n3. Tab...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)  # 增加等待时间

        # 5. Tab到数量
        print("\n4. Tab...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)  # 增加等待时间

        # 6. 输入数量
        print("\n5. 输入数量...")
        clear_and_type(quantity)
        time.sleep(0.5)  # 增加等待时间确保数量输入完成

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 按B确认买入
        print("\n7. 按B确认买入...")
        # 按住Shift + B 产生大写B
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, 0, 0)  # B键按下
        time.sleep(0.01)
        win32api.keybd_event(0x42, 0, win32con.KEYEVENTF_KEYUP, 0)  # B键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        
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
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("\n开始卖出操作...")

    try:
        # 2. 按F1-F2进入卖出界面
        print("\n1. 按F1-F2进入卖出界面...")
        send_key_fast(0x70)  # F1
        time.sleep(0.1)
        send_key_fast(0x71)  # F2
        time.sleep(0.5)

        # 3. 输入股票代码
        print("\n2. 输入股票代码...")
        clear_and_type(code)
        time.sleep(0.5)  # 增加等待时间确保股票代码输入完成

        # 4. Tab(跳过价格)
        print("\n3. Tab...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)  # 增加等待时间

        # 5. Tab到数量
        print("\n4. Tab...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)  # 增加等待时间

        # 6. 输入数量
        print("\n5. 输入数量...")
        clear_and_type(quantity)
        time.sleep(0.5)  # 增加等待时间确保数量输入完成

        # 7. 按Tab离开输入框
        print("\n6. Tab离开输入框...")
        send_key_fast(0x09)  # Tab
        time.sleep(0.3)

        # 8. 按S确认卖出
        print("\n7. 按S确认卖出...")
        # 按住Shift + S 产生大写S
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Shift按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Shift释放
        
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
