#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易代理 - 最终版本
用户需要手动点击交易软件，然后运行操作
"""

import time
import win32api
import win32con
import win32gui

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

def verify_trading_window():
    """验证当前是否在交易软件窗口"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if "网上股票交易系统" in title or "股票交易" in title:
            print(f"✅ 当前窗口: {title}")
            return True, hwnd
        else:
            print(f"⚠️ 当前窗口: {title}")
            print("❌ 这不是交易软件窗口!")
            return False, None
    except:
        print("❌ 无法获取当前窗口信息")
        return False, None

def buy_stock(code, price, quantity):
    """买入股票"""
    print(f"\n🚀 执行买入操作")
    print(f"股票代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 50)
    
    print("📋 操作步骤:")
    print("1. 请手动点击交易软件窗口")
    print("2. 确保交易软件在前台")
    print("3. 按回车开始自动操作")
    input("按回车继续...")
    
    # 验证窗口
    is_trading, hwnd = verify_trading_window()
    if not is_trading:
        print("❌ 请先点击交易软件窗口!")
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        print("\n1️⃣ 按F1进入买入界面...")
        send_key(0x70)  # F1
        time.sleep(1.5)
        
        print("2️⃣ 输入股票代码...")
        clear_and_input(code)
        
        print("3️⃣ Tab切换到价格...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        
        print("4️⃣ 输入价格...")
        clear_and_input(price)
        
        print("5️⃣ Tab切换到数量...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        
        print("6️⃣ 输入数量...")
        clear_and_input(quantity)
        
        print("\n✅ 买入信息填入完成!")
        print("💡 请在交易软件中确认并提交订单")
        return True
        
    except Exception as e:
        print(f"❌ 买入操作失败: {e}")
        return False

def sell_stock(code, price, quantity):
    """卖出股票"""
    print(f"\n🚀 执行卖出操作")
    print(f"股票代码: {code}, 价格: {price}, 数量: {quantity}")
    print("-" * 50)
    
    print("📋 操作步骤:")
    print("1. 请手动点击交易软件窗口")
    print("2. 确保交易软件在前台")
    print("3. 按回车开始自动操作")
    input("按回车继续...")
    
    # 验证窗口
    is_trading, hwnd = verify_trading_window()
    if not is_trading:
        print("❌ 请先点击交易软件窗口!")
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        print("\n1️⃣ 按F2进入卖出界面...")
        send_key(0x71)  # F2
        time.sleep(1.5)
        
        print("2️⃣ 输入股票代码...")
        clear_and_input(code)
        
        print("3️⃣ Tab切换到价格...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        
        print("4️⃣ 输入价格...")
        clear_and_input(price)
        
        print("5️⃣ Tab切换到数量...")
        send_key(0x09)  # Tab
        time.sleep(0.5)
        
        print("6️⃣ 输入数量...")
        clear_and_input(quantity)
        
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
    
    print("📋 操作步骤:")
    print("1. 请手动点击交易软件窗口")
    print("2. 确保交易软件在前台")
    print("3. 按回车开始自动操作")
    input("按回车继续...")
    
    # 验证窗口
    is_trading, hwnd = verify_trading_window()
    if not is_trading:
        print("❌ 请先点击交易软件窗口!")
        return False
    
    print("\n⏰ 3秒后开始操作...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        print("\n1️⃣ 按F4进入资金界面...")
        send_key(0x73)  # F4
        time.sleep(1.5)
        
        print("\n✅ 资金页面已打开!")
        return True
        
    except Exception as e:
        print(f"❌ 查看资金失败: {e}")
        return False

def main():
    """主程序"""
    print("🎯 交易代理 - 最终版本")
    print("=" * 60)
    print("💡 使用说明:")
    print("   1. 确保交易软件已打开")
    print("   2. 选择操作后，手动点击交易软件窗口")
    print("   3. 程序会自动执行键盘操作")
    print()
    
    while True:
        print("\n请选择操作:")
        print("1. 买入股票")
        print("2. 卖出股票") 
        print("3. 查看资金")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
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
            check_funds()
            
        elif choice == "4":
            print("👋 退出程序")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()
