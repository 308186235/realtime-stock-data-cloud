#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的交易代理 - 确保在交易软件中操作
"""

import time
import win32api
import win32con
import win32gui

def find_and_activate_trading_window():
    """查找并强制激活交易软件窗口"""
    print("🔍 查找交易软件窗口...")
    
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "网上股票交易系统" in title or "股票交易" in title:
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    
    if not windows:
        print("❌ 未找到交易软件窗口！请先打开交易软件")
        return None
    
    hwnd, title = windows[0]
    print(f"✅ 找到交易软件: {title}")
    
    try:
        # 强制激活窗口
        print("🎯 强制激活交易软件窗口...")
        
        # 如果窗口最小化，先恢复
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(1)
        
        # 置顶窗口
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        time.sleep(0.5)
        
        # 设置为前台窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        # 取消置顶
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
        # 验证激活成功
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print("✅ 交易软件已成功激活并置于前台")
            return hwnd
        else:
            print("⚠️ 窗口激活可能不完全，但继续尝试...")
            return hwnd
            
    except Exception as e:
        print(f"❌ 激活窗口失败: {e}")
        return None

def verify_window_active(hwnd, interface_name):
    """验证交易窗口是否仍然活跃"""
    try:
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == hwnd:
            print(f"✅ 验证通过: {interface_name}界面窗口仍然活跃")
            return True
        else:
            print(f"⚠️ 窗口焦点丢失，重新激活...")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            return True
    except:
        print(f"⚠️ 无法验证窗口状态")
        return False

def send_key(vk_code):
    """发送按键"""
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def clear_and_input(text):
    """清空并输入文本"""
    print(f"   输入: {text}")
    # Ctrl+A 全选
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    win32api.keybd_event(0x41, 0, 0, 0)  # A down
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)  # A up
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
    time.sleep(0.1)
    
    # 输入文本
    for char in str(text):
        if char.isdigit():
            send_key(ord(char))
        elif char == '.':
            send_key(0xBE)  # 小数点
        time.sleep(0.05)
    time.sleep(0.3)

def buy_stock(code, price, quantity):
    """买入股票 - 真正在交易软件中操作"""
    print(f"\n🚀 执行买入操作")
    print(f"股票代码: {code}")
    print(f"价格: {price}")
    print(f"数量: {quantity}")
    print("-" * 50)
    
    # 1. 激活交易软件
    hwnd = find_and_activate_trading_window()
    if not hwnd:
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        # 2. 按F1进入买入界面
        print("\n1️⃣ 按F1进入买入界面...")
        send_key(0x70)  # F1
        time.sleep(1.5)
        verify_window_active(hwnd, "买入")
        
        # 3. 输入股票代码
        print("\n2️⃣ 输入股票代码...")
        clear_and_input(code)
        verify_window_active(hwnd, "买入")
        
        # 4. Tab到价格
        print("\n3️⃣ Tab切换到价格...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        verify_window_active(hwnd, "买入")
        
        # 5. 输入价格
        print("\n4️⃣ 输入价格...")
        clear_and_input(price)
        verify_window_active(hwnd, "买入")
        
        # 6. Tab到数量
        print("\n5️⃣ Tab切换到数量...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        verify_window_active(hwnd, "买入")
        
        # 7. 输入数量
        print("\n6️⃣ 输入数量...")
        clear_and_input(quantity)
        verify_window_active(hwnd, "买入")
        
        print("\n✅ 买入信息填入完成!")
        print("💡 请在交易软件中确认并提交订单")
        return True
        
    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

def sell_stock(code, price, quantity):
    """卖出股票 - 真正在交易软件中操作"""
    print(f"\n🚀 执行卖出操作")
    print(f"股票代码: {code}")
    print(f"价格: {price}")
    print(f"数量: {quantity}")
    print("-" * 50)
    
    # 1. 激活交易软件
    hwnd = find_and_activate_trading_window()
    if not hwnd:
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        # 2. 按F2进入卖出界面
        print("\n1️⃣ 按F2进入卖出界面...")
        send_key(0x71)  # F2
        time.sleep(1.5)
        verify_window_active(hwnd, "卖出")
        
        # 3. 输入股票代码
        print("\n2️⃣ 输入股票代码...")
        clear_and_input(code)
        verify_window_active(hwnd, "卖出")
        
        # 4. Tab到价格
        print("\n3️⃣ Tab切换到价格...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        verify_window_active(hwnd, "卖出")
        
        # 5. 输入价格
        print("\n4️⃣ 输入价格...")
        clear_and_input(price)
        verify_window_active(hwnd, "卖出")
        
        # 6. Tab到数量
        print("\n5️⃣ Tab切换到数量...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        verify_window_active(hwnd, "卖出")
        
        # 7. 输入数量
        print("\n6️⃣ 输入数量...")
        clear_and_input(quantity)
        verify_window_active(hwnd, "卖出")
        
        print("\n✅ 卖出信息填入完成!")
        print("💡 请在交易软件中确认并提交订单")
        return True
        
    except Exception as e:
        print(f"❌ 卖出操作失败: {e}")
        return False

def check_funds():
    """查看资金"""
    print(f"\n💰 查看资金")
    print("-" * 50)
    
    # 1. 激活交易软件
    hwnd = find_and_activate_trading_window()
    if not hwnd:
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        # 2. 按F4进入资金界面
        print("\n1️⃣ 按F4进入资金界面...")
        send_key(0x73)  # F4
        time.sleep(1.5)
        verify_window_active(hwnd, "资金")
        
        print("\n✅ 资金页面已打开!")
        return True
        
    except Exception as e:
        print(f"❌ 查看资金失败: {e}")
        return False

def main():
    """主程序"""
    print("🎯 真正的交易代理")
    print("=" * 60)
    print("⚠️ 确保交易软件已打开并可见!")
    print()
    
    while True:
        print("\n请选择操作:")
        print("1. 买入股票")
        print("2. 卖出股票") 
        print("3. 查看资金")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            code = input("股票代码: ").strip() or "600000"
            price = input("买入价格: ").strip() or "10.50"
            quantity = input("买入数量: ").strip() or "100"
            buy_stock(code, price, quantity)
            
        elif choice == "2":
            code = input("股票代码: ").strip() or "600000"
            price = input("卖出价格: ").strip() or "10.60"
            quantity = input("卖出数量: ").strip() or "100"
            sell_stock(code, price, quantity)
            
        elif choice == "3":
            check_funds()
            
        elif choice == "4":
            print("👋 退出程序")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()
