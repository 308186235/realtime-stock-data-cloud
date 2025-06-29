#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单快速交易代理 - 基于能工作的版本，只缩短时间
"""

import time
import datetime
import win32api
import win32con
import win32gui
import win32clipboard

def send_key_fast(vk_code):
    """快速发送按键"""
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.01)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.01)

def ensure_caps_lock_on():
    """确保Caps Lock开启"""
    caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
    print(f"   当前Caps Lock状态: {caps_state}")
    
    if caps_state == 0:  # Caps Lock关闭
        print("   开启Caps Lock...")
        send_key_fast(win32con.VK_CAPITAL)
        time.sleep(0.1)
        new_caps_state = win32api.GetKeyState(win32con.VK_CAPITAL)
        print(f"   开启后Caps Lock状态: {new_caps_state}")
    else:
        print("   Caps Lock已开启")

def click_table_area():
    """点击表格区域获得焦点"""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0] + (rect[2] - rect[0]) * 0.7  # 窗口宽度的70%位置
        y = rect[1] + (rect[3] - rect[1]) * 0.5  # 窗口高度的50%位置
        
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return True
    return False

def generate_unique_filename(base_name, extension=".csv"):
    """生成带时间戳的唯一文件名"""
    timestamp = datetime.datetime.now().strftime("%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

def clear_and_type(text):
    """使用剪贴板快速输入文本"""
    try:
        # 将文本复制到剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(text))
        win32clipboard.CloseClipboard()
        time.sleep(0.02)

        # Ctrl+A 全选
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('A'), 0, 0, 0)  # A down
        time.sleep(0.01)
        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.02)

        # Ctrl+V 粘贴
        win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        win32api.keybd_event(ord('V'), 0, 0, 0)  # V down
        time.sleep(0.01)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        time.sleep(0.02)
    except Exception as e:
        print(f"输入失败: {e}")

def export_holdings():
    """导出持仓数据 - 快速版本"""
    print("\n📊 导出持仓数据")
    print("-" * 40)
    
    print("请手动点击交易软件窗口，确保它是活动状态！")
    print("等待1秒...")
    time.sleep(1)
    
    print("开始导出持仓...")
    
    try:
        # 1. 按W键进入持仓页面
        print("1. 按W键进入持仓页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)
        
        win32api.keybd_event(0x57, 0, 0, 0)  # W键按下
        time.sleep(0.01)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W键释放
        time.sleep(0.2)
        
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
        win32api.keybd_event(ord('n'), 0, 0, 0)  # n键按下
        time.sleep(0.02)
        win32api.keybd_event(ord('n'), 0, win32con.KEYEVENTF_KEYUP, 0)  # n键释放
        time.sleep(0.3)
        
        print(f"\n✅ 持仓数据导出完成! 文件: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_transactions():
    """导出成交数据 - 快速版本"""
    print("\n📊 导出成交数据")
    print("-" * 40)
    
    print("请手动点击交易软件窗口，确保它是活动状态！")
    print("等待1秒...")
    time.sleep(1)
    
    print("开始导出成交...")
    
    try:
        # 1. 按E键进入成交页面
        print("1. 按E键进入成交页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)
        
        win32api.keybd_event(0x45, 0, 0, 0)  # E键按下
        time.sleep(0.01)
        win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E键释放
        time.sleep(0.2)
        
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
        win32api.keybd_event(ord('n'), 0, 0, 0)  # n键按下
        time.sleep(0.02)
        win32api.keybd_event(ord('n'), 0, win32con.KEYEVENTF_KEYUP, 0)  # n键释放
        time.sleep(0.3)
        
        print(f"\n✅ 成交数据导出完成! 文件: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_orders():
    """导出委托数据 - 快速版本"""
    print("\n📊 导出委托数据")
    print("-" * 40)
    
    print("请手动点击交易软件窗口，确保它是活动状态！")
    print("等待1秒...")
    time.sleep(1)
    
    print("开始导出委托...")
    
    try:
        # 1. 按R键进入委托页面
        print("1. 按R键进入委托页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)
        
        win32api.keybd_event(0x52, 0, 0, 0)  # R键按下
        time.sleep(0.01)
        win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)  # R键释放
        time.sleep(0.2)
        
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
        win32api.keybd_event(ord('n'), 0, 0, 0)  # n键按下
        time.sleep(0.02)
        win32api.keybd_event(ord('n'), 0, win32con.KEYEVENTF_KEYUP, 0)  # n键释放
        time.sleep(0.3)
        
        print(f"\n✅ 委托数据导出完成! 文件: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def main():
    """主程序"""
    print("🎯 简单快速交易代理")
    print("=" * 50)
    
    while True:
        print("\n请选择:")
        print("1. 导出持仓")
        print("2. 导出成交")
        print("3. 导出委托")
        print("4. 退出")

        choice = input("选择 (1-4): ").strip()
        
        if choice == "1":
            export_holdings()
        elif choice == "2":
            export_transactions()
        elif choice == "3":
            export_orders()
        elif choice == "4":
            print("退出")
            break
        else:
            print("无效选择")

if __name__ == "__main__":
    main()
