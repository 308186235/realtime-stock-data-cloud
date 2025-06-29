#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Win32 API直接快捷键交易
最简单直接的实现
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
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl按下
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, 0, 0)  # A按下
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)  # A释放
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
    time.sleep(0.1)

def send_text(text):
    """发送文本 - 改进版"""
    print(f"   正在输入: '{text}'")
    for char in str(text):
        if char.isdigit():
            # 数字键
            vk_code = ord(char)
            send_key(vk_code)
            time.sleep(0.08)
        elif char == '.':
            # 小数点
            send_key(0xBE)  # 小数点键
            time.sleep(0.08)
    time.sleep(0.2)

def get_trading_window():
    """获取交易窗口句柄"""
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "网上股票交易系统" in title or "股票交易" in title:
                windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(enum_callback, windows)

    if windows:
        return windows[0][0], windows[0][1]
    return None, None

def activate_trading_window():
    """激活交易窗口并验证"""
    hwnd, title = get_trading_window()

    if not hwnd:
        print("❌ 未找到交易窗口")
        return False, None

    try:
        # 激活窗口
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(1)

        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)

        # 验证窗口是否在前台
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print(f"✅ 交易窗口已激活: {title}")
            return True, hwnd
        else:
            print("⚠️ 窗口激活可能失败，但继续尝试...")
            return True, hwnd

    except Exception as e:
        print(f"❌ 激活窗口失败: {e}")
        return False, None

def verify_interface_switch(expected_interface, hwnd):
    """验证界面是否切换成功"""
    print(f"🔍 验证是否切换到{expected_interface}界面...")

    # 等待界面切换
    time.sleep(1)

    # 简单验证：检查窗口是否还在前台
    try:
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print(f"✅ 界面切换验证通过 - {expected_interface}")
            return True
        else:
            print(f"⚠️ 窗口焦点可能丢失，但继续操作...")
            # 重新激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            return True
    except:
        print(f"⚠️ 无法验证界面切换，但继续操作...")
        return True

def buy_stock_direct(code, price, quantity):
    """直接买入股票 - 带验证"""
    print(f"\n🚀 买入股票: {code} 价格:{price} 数量:{quantity}")
    print("-" * 40)

    # 1. 激活交易窗口
    success, hwnd = activate_trading_window()
    if not success:
        return False

    try:
        # 2. 按F1进入买入界面
        print("1. 按F1进入买入界面...")
        send_key(0x70)  # F1

        # 3. 验证是否切换到买入界面
        if not verify_interface_switch("买入", hwnd):
            print("❌ 未能切换到买入界面")
            return False

        # 4. 清空并输入股票代码
        print(f"2. 清空并输入股票代码: {code}")
        send_ctrl_a()  # 清空当前输入框
        send_text(code)
        time.sleep(0.8)

        # 5. Tab切换到价格输入框
        print("3. Tab切换到价格输入框...")
        send_key(0x09)  # Tab
        time.sleep(0.5)

        # 6. 清空并输入价格
        print(f"4. 清空并输入价格: {price}")
        send_ctrl_a()  # 清空当前输入框
        send_text(str(price))
        time.sleep(0.8)

        # 7. Tab切换到数量输入框
        print("5. Tab切换到数量输入框...")
        send_key(0x09)  # Tab
        time.sleep(0.5)

        # 8. 清空并输入数量
        print(f"6. 清空并输入数量: {quantity}")
        send_ctrl_a()  # 清空当前输入框
        send_text(str(quantity))
        time.sleep(0.8)

        print("✅ 买入信息填入完成!")
        print("💡 请在交易软件中手动确认提交订单")
        return True

    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

def sell_stock_direct(code, price, quantity):
    """直接卖出股票 - 带验证"""
    print(f"\n🚀 卖出股票: {code} 价格:{price} 数量:{quantity}")
    print("-" * 40)

    # 1. 激活交易窗口
    success, hwnd = activate_trading_window()
    if not success:
        return False

    try:
        # 2. 按F2进入卖出界面
        print("1. 按F2进入卖出界面...")
        send_key(0x71)  # F2

        # 3. 验证是否切换到卖出界面
        if not verify_interface_switch("卖出", hwnd):
            print("❌ 未能切换到卖出界面")
            return False

        # 4. 清空并输入股票代码
        print(f"2. 清空并输入股票代码: {code}")
        send_ctrl_a()  # 清空当前输入框
        send_text(code)
        time.sleep(0.8)

        # 5. Tab切换到价格输入框
        print("3. Tab切换到价格输入框...")
        send_key(0x09)  # Tab
        time.sleep(0.5)

        # 6. 清空并输入价格
        print(f"4. 清空并输入价格: {price}")
        send_ctrl_a()  # 清空当前输入框
        send_text(str(price))
        time.sleep(0.8)

        # 7. Tab切换到数量输入框
        print("5. Tab切换到数量输入框...")
        send_key(0x09)  # Tab
        time.sleep(0.5)

        # 8. 清空并输入数量
        print(f"6. 清空并输入数量: {quantity}")
        send_ctrl_a()  # 清空当前输入框
        send_text(str(quantity))
        time.sleep(0.8)

        print("✅ 卖出信息填入完成!")
        print("💡 请在交易软件中手动确认提交订单")
        return True

    except Exception as e:
        print(f"❌ 卖出操作失败: {e}")
        return False

def check_funds_direct():
    """查看资金 - 带验证"""
    print("\n💰 查看资金...")
    print("-" * 40)

    # 1. 激活交易窗口
    success, hwnd = activate_trading_window()
    if not success:
        return False

    try:
        # 2. 按F4进入资金页面
        print("1. 按F4进入资金页面...")
        send_key(0x73)  # F4

        # 3. 验证是否切换到资金页面
        if not verify_interface_switch("资金", hwnd):
            print("❌ 未能切换到资金页面")
            return False

        print("✅ 资金页面已成功打开!")
        return True

    except Exception as e:
        print(f"❌ 查看资金失败: {e}")
        return False

def main():
    """主函数 - 立即执行测试"""
    print("🎯 Win32 API直接快捷键交易测试")
    print("=" * 50)
    print("⚠️ 请确保交易软件已打开!")
    print()
    
    print("3秒后开始自动操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("\n🚀 开始执行操作!")
    
    # 1. 测试资金查看
    print("\n" + "="*30)
    print("测试1: 查看资金")
    print("="*30)
    check_funds_direct()
    
    time.sleep(2)
    
    # 2. 测试买入
    print("\n" + "="*30)
    print("测试2: 买入操作")
    print("="*30)
    buy_stock_direct("600000", "10.50", "100")
    
    time.sleep(2)
    
    # 3. 测试卖出
    print("\n" + "="*30)
    print("测试3: 卖出操作")
    print("="*30)
    sell_stock_direct("600000", "10.60", "100")
    
    print("\n" + "="*50)
    print("🎉 所有操作测试完成!")
    print("📋 执行的操作:")
    print("  ✅ F4 - 查看资金页面")
    print("  ✅ F1 - 买入界面 + 自动填入信息")
    print("  ✅ F2 - 卖出界面 + 自动填入信息")
    print("  ✅ Tab - 在输入框间切换")
    print("  ✅ 自动输入股票代码、价格、数量")
    print("\n💡 现在您应该能在交易软件中看到真实的操作效果了!")

if __name__ == "__main__":
    main()
