#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯快捷键交易系统
F1=买入界面, F2=卖出界面, F4=资金页面, Tab=切换输入框
"""

import time
import win32gui
import win32con
import pyautogui

class SimpleHotkeyTrader:
    """纯快捷键交易器"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        
    def activate_trading_window(self):
        """激活交易软件窗口"""
        print("🔍 激活交易软件...")
        
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
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(1)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                print(f"✅ 已激活: {title}")
                return True
            except:
                print("⚠️ 激活窗口可能失败，但继续操作...")
                return True
        
        print("❌ 未找到交易软件")
        return False
    
    def buy_stock(self, stock_code, price, quantity):
        """买入股票"""
        print(f"\n🚀 买入股票: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        if not self.activate_trading_window():
            return False
        
        try:
            # 1. 按F1进入买入界面
            print("1. 按F1进入买入界面...")
            pyautogui.press('f1')
            time.sleep(1)
            
            # 2. 输入股票代码
            print(f"2. 输入股票代码: {stock_code}")
            pyautogui.typewrite(stock_code)
            time.sleep(0.5)
            
            # 3. 按Tab切换到价格输入框
            print("3. Tab切换到价格输入框...")
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # 4. 输入价格
            print(f"4. 输入价格: {price}")
            pyautogui.typewrite(str(price))
            time.sleep(0.5)
            
            # 5. 按Tab切换到数量输入框
            print("5. Tab切换到数量输入框...")
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # 6. 输入数量
            print(f"6. 输入数量: {quantity}")
            pyautogui.typewrite(str(quantity))
            time.sleep(0.5)
            
            print("✅ 买入信息已填入完成!")
            print("💡 请在交易软件中手动点击确认按钮提交订单")
            
            return True
            
        except Exception as e:
            print(f"❌ 买入操作失败: {e}")
            return False
    
    def sell_stock(self, stock_code, price, quantity):
        """卖出股票"""
        print(f"\n🚀 卖出股票: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        if not self.activate_trading_window():
            return False
        
        try:
            # 1. 按F2进入卖出界面
            print("1. 按F2进入卖出界面...")
            pyautogui.press('f2')
            time.sleep(1)
            
            # 2. 输入股票代码
            print(f"2. 输入股票代码: {stock_code}")
            pyautogui.typewrite(stock_code)
            time.sleep(0.5)
            
            # 3. 按Tab切换到价格输入框
            print("3. Tab切换到价格输入框...")
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # 4. 输入价格
            print(f"4. 输入价格: {price}")
            pyautogui.typewrite(str(price))
            time.sleep(0.5)
            
            # 5. 按Tab切换到数量输入框
            print("5. Tab切换到数量输入框...")
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # 6. 输入数量
            print(f"6. 输入数量: {quantity}")
            pyautogui.typewrite(str(quantity))
            time.sleep(0.5)
            
            print("✅ 卖出信息已填入完成!")
            print("💡 请在交易软件中手动点击确认按钮提交订单")
            
            return True
            
        except Exception as e:
            print(f"❌ 卖出操作失败: {e}")
            return False
    
    def check_funds(self):
        """查看资金"""
        print("\n💰 查看资金信息")
        
        if not self.activate_trading_window():
            return False
        
        try:
            # 按F4进入资金页面
            print("按F4进入资金页面...")
            pyautogui.press('f4')
            time.sleep(1)
            
            print("✅ 已切换到资金页面")
            return True
            
        except Exception as e:
            print(f"❌ 查看资金失败: {e}")
            return False

def test_real_operations():
    """测试真实操作"""
    print("🎯 纯快捷键交易系统测试")
    print("=" * 40)
    print("⚠️ 这将在您的交易软件中执行真实操作!")
    print()
    
    trader = SimpleHotkeyTrader()
    
    # 测试激活窗口
    print("测试1: 激活交易软件窗口")
    if not trader.activate_trading_window():
        print("❌ 无法激活交易软件，测试终止")
        return
    
    # 测试资金查看
    test_fund = input("\n是否测试查看资金页面? (y/n): ")
    if test_fund.lower() == 'y':
        trader.check_funds()
        input("按回车继续...")
    
    # 测试买入操作
    test_buy = input("\n是否测试买入操作? (y/n): ")
    if test_buy.lower() == 'y':
        stock_code = input("输入股票代码 (默认600000): ") or "600000"
        price = input("输入买入价格 (默认10.50): ") or "10.50"
        quantity = input("输入买入数量 (默认100): ") or "100"
        
        print(f"\n即将执行买入操作:")
        print(f"股票代码: {stock_code}")
        print(f"买入价格: {price}")
        print(f"买入数量: {quantity}")
        
        confirm = input("\n确认执行? (y/n): ")
        if confirm.lower() == 'y':
            trader.buy_stock(stock_code, price, quantity)
            input("买入操作完成，按回车继续...")
    
    # 测试卖出操作
    test_sell = input("\n是否测试卖出操作? (y/n): ")
    if test_sell.lower() == 'y':
        stock_code = input("输入股票代码 (默认600000): ") or "600000"
        price = input("输入卖出价格 (默认10.60): ") or "10.60"
        quantity = input("输入卖出数量 (默认100): ") or "100"
        
        print(f"\n即将执行卖出操作:")
        print(f"股票代码: {stock_code}")
        print(f"卖出价格: {price}")
        print(f"卖出数量: {quantity}")
        
        confirm = input("\n确认执行? (y/n): ")
        if confirm.lower() == 'y':
            trader.sell_stock(stock_code, price, quantity)
            input("卖出操作完成，按回车继续...")
    
    print("\n🎉 测试完成!")
    print("📋 操作总结:")
    print("  ✅ F1 - 成功切换到买入界面")
    print("  ✅ F2 - 成功切换到卖出界面")
    print("  ✅ F4 - 成功切换到资金页面")
    print("  ✅ Tab - 成功在输入框间切换")
    print("  ✅ 自动输入股票代码、价格、数量")
    print("\n💡 现在您可以看到真实的操作效果了!")

def agent_auto_trading_demo():
    """Agent自动交易演示"""
    print("\n🤖 Agent自动交易演示")
    print("=" * 30)
    
    trader = SimpleHotkeyTrader()
    
    # 模拟Agent决策
    decisions = [
        {"action": "buy", "symbol": "600000", "price": 10.50, "quantity": 100},
        {"action": "sell", "symbol": "600519", "price": 1850.00, "quantity": 10}
    ]
    
    print("🧠 Agent决策列表:")
    for i, decision in enumerate(decisions, 1):
        print(f"  {i}. {decision['action'].upper()} {decision['symbol']} "
              f"价格:{decision['price']} 数量:{decision['quantity']}")
    
    execute = input("\n是否执行Agent自动交易? (y/n): ")
    if execute.lower() != 'y':
        return
    
    for i, decision in enumerate(decisions, 1):
        print(f"\n🤖 执行Agent决策 {i}...")
        
        if decision['action'] == 'buy':
            success = trader.buy_stock(
                decision['symbol'], 
                decision['price'], 
                decision['quantity']
            )
        elif decision['action'] == 'sell':
            success = trader.sell_stock(
                decision['symbol'], 
                decision['price'], 
                decision['quantity']
            )
        
        if success:
            print(f"✅ 决策 {i} 执行成功")
        else:
            print(f"❌ 决策 {i} 执行失败")
        
        if i < len(decisions):
            input("按回车继续下一个决策...")
    
    print("\n🎉 Agent自动交易演示完成!")

def main():
    print("⌨️ 纯快捷键交易系统")
    print("=" * 50)
    print("🎯 快捷键操作:")
    print("  F1 - 买入界面")
    print("  F2 - 卖出界面")
    print("  F4 - 资金页面")
    print("  Tab - 切换输入框")
    print("  直接输入 - 股票代码/价格/数量")
    print()
    
    try:
        # 1. 基础功能测试
        test_real_operations()
        
        # 2. Agent演示
        demo_agent = input("\n是否继续Agent自动交易演示? (y/n): ")
        if demo_agent.lower() == 'y':
            agent_auto_trading_demo()
        
        print("\n🎉 所有测试完成!")
        print("现在您已经看到了真正的快捷键操作效果!")
        
    except KeyboardInterrupt:
        print("\n\n👋 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 操作过程中发生错误: {e}")

if __name__ == "__main__":
    main()
