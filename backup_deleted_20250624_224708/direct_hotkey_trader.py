#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接快捷键交易 - 最简单版本
F1买入 F2卖出 F4资金 Tab切换
"""

import time
import keyboard
import pyautogui

def buy_stock(code, price, quantity):
    """买入股票 - 直接操作"""
    print(f"买入: {code} 价格:{price} 数量:{quantity}")
    
    # F1进入买入界面
    keyboard.press_and_release('f1')
    time.sleep(1)
    
    # 输入股票代码
    pyautogui.typewrite(code)
    time.sleep(0.5)
    
    # Tab到价格
    keyboard.press_and_release('tab')
    time.sleep(0.3)
    
    # 输入价格
    pyautogui.typewrite(str(price))
    time.sleep(0.5)
    
    # Tab到数量
    keyboard.press_and_release('tab')
    time.sleep(0.3)
    
    # 输入数量
    pyautogui.typewrite(str(quantity))
    time.sleep(0.5)
    
    print("✅ 买入信息已填入")

def sell_stock(code, price, quantity):
    """卖出股票 - 直接操作"""
    print(f"卖出: {code} 价格:{price} 数量:{quantity}")
    
    # F2进入卖出界面
    keyboard.press_and_release('f2')
    time.sleep(1)
    
    # 输入股票代码
    pyautogui.typewrite(code)
    time.sleep(0.5)
    
    # Tab到价格
    keyboard.press_and_release('tab')
    time.sleep(0.3)
    
    # 输入价格
    pyautogui.typewrite(str(price))
    time.sleep(0.5)
    
    # Tab到数量
    keyboard.press_and_release('tab')
    time.sleep(0.3)
    
    # 输入数量
    pyautogui.typewrite(str(quantity))
    time.sleep(0.5)
    
    print("✅ 卖出信息已填入")

def check_funds():
    """查看资金"""
    print("查看资金...")
    keyboard.press_and_release('f4')
    time.sleep(1)
    print("✅ 已切换到资金页面")

# 立即测试
if __name__ == "__main__":
    print("🚀 直接快捷键交易测试")
    print("3秒后开始操作，请确保交易软件在前台...")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("开始操作!")
    
    # 测试买入
    buy_stock("600000", "10.50", "100")
    
    time.sleep(2)
    
    # 测试卖出
    sell_stock("600000", "10.60", "100")
    
    time.sleep(2)
    
    # 测试资金
    check_funds()
    
    print("🎉 测试完成!")
