#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试输入功能
"""

import time
import win32api
import win32con
import win32gui

def send_key(vk_code):
    """发送按键"""
    win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放

def send_ctrl_a():
    """发送Ctrl+A组合键"""
    print("   执行Ctrl+A清空...")
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl按下
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, 0, 0)  # A按下
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)  # A释放
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
    time.sleep(0.2)

def send_text_careful(text):
    """小心地发送文本"""
    print(f"   正在逐字符输入: '{text}'")
    for i, char in enumerate(str(text)):
        print(f"     输入第{i+1}个字符: '{char}'")
        if char.isdigit():
            # 数字键
            vk_code = ord(char)
            send_key(vk_code)
            time.sleep(0.15)  # 更长的延迟
        elif char == '.':
            # 小数点
            send_key(0xBE)  # 小数点键
            time.sleep(0.15)
    print(f"   输入完成: '{text}'")
    time.sleep(0.5)

def activate_trading_window():
    """激活交易窗口"""
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "网上股票交易系统" in title:
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    
    if windows:
        hwnd, title = windows[0]
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            print(f"✅ 交易窗口已激活: {title}")
            return True, hwnd
        except:
            print("⚠️ 窗口激活可能失败")
            return True, hwnd
    
    print("❌ 未找到交易窗口")
    return False, None

def test_sell_input():
    """专门测试卖出界面的输入"""
    print("🧪 测试卖出界面输入")
    print("=" * 40)
    
    # 激活窗口
    success, hwnd = activate_trading_window()
    if not success:
        return
    
    print("\n5秒后开始操作，请确保交易软件在前台...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        # 1. 按F2进入卖出界面
        print("\n1. 按F2进入卖出界面...")
        send_key(0x71)  # F2
        time.sleep(2)  # 等待界面切换

        # 验证是否切换成功
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print("✅ 验证：卖出界面切换成功")
        else:
            print("⚠️ 警告：窗口焦点可能丢失，重新激活...")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        
        # 2. 输入股票代码
        print("\n2. 输入股票代码: 600000")
        send_ctrl_a()
        send_text_careful("600000")
        
        # 3. Tab到价格
        print("\n3. Tab切换到价格输入框...")
        send_key(0x09)  # Tab
        time.sleep(1)

        # 验证窗口焦点
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            print("⚠️ 重新激活交易窗口...")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
        
        # 4. 输入价格
        print("\n4. 输入价格: 10.60")
        send_ctrl_a()
        send_text_careful("10.60")
        
        # 5. Tab到数量
        print("\n5. Tab切换到数量输入框...")
        send_key(0x09)  # Tab
        time.sleep(1)

        # 验证窗口焦点
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            print("⚠️ 重新激活交易窗口...")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
        
        # 6. 输入数量
        print("\n6. 输入数量: 100")
        send_ctrl_a()
        send_text_careful("100")
        
        print("\n✅ 输入测试完成!")
        print("请检查交易软件中的输入是否正确:")
        print("  股票代码: 600000")
        print("  价格: 10.60")
        print("  数量: 100")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_sell_input()
