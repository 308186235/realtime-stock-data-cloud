#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于快捷键的简单交易系统
F1=买入界面, F2=卖出界面, F4=资金页面, Tab=切换输入框
"""

import time
import win32gui
import win32api
import win32con
import pyautogui
from typing import Dict, Any

class HotkeySimpleTrader:
    """基于快捷键的简单交易器"""
    
    def __init__(self):
        self.window_handle = None
        self.window_title = ""
        
        # 禁用pyautogui的安全检查
        pyautogui.FAILSAFE = False
        
    def find_and_activate_trading_window(self) -> bool:
        """查找并激活交易软件窗口"""
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
            print("❌ 未找到交易软件窗口")
            return False
        
        self.window_handle, self.window_title = windows[0]
        print(f"✅ 找到交易软件: {self.window_title}")
        
        try:
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(self.window_handle):
                print("📱 恢复最小化窗口...")
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(1)
            
            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            print("✅ 交易软件窗口已激活")
            return True
            
        except Exception as e:
            print(f"⚠️ 激活窗口时出现问题: {e}")
            print("但继续尝试操作...")
            return True
    
    def navigate_to_buy_page(self) -> bool:
        """导航到买入页面 (F1)"""
        print("🔄 导航到买入页面 (F1)...")
        try:
            pyautogui.press('f1')
            time.sleep(1)  # 等待页面加载
            print("✅ 已切换到买入页面")
            return True
        except Exception as e:
            print(f"❌ 导航到买入页面失败: {e}")
            return False
    
    def navigate_to_sell_page(self) -> bool:
        """导航到卖出页面 (F2)"""
        print("🔄 导航到卖出页面 (F2)...")
        try:
            pyautogui.press('f2')
            time.sleep(1)  # 等待页面加载
            print("✅ 已切换到卖出页面")
            return True
        except Exception as e:
            print(f"❌ 导航到卖出页面失败: {e}")
            return False
    
    def navigate_to_fund_page(self) -> bool:
        """导航到资金页面 (F4)"""
        print("🔄 导航到资金页面 (F4)...")
        try:
            pyautogui.press('f4')
            time.sleep(1)  # 等待页面加载
            print("✅ 已切换到资金页面")
            return True
        except Exception as e:
            print(f"❌ 导航到资金页面失败: {e}")
            return False
    
    def input_stock_code(self, stock_code: str) -> bool:
        """输入股票代码（通常是第一个输入框）"""
        print(f"📝 输入股票代码: {stock_code}")
        try:
            # 清空当前输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # 输入股票代码
            pyautogui.typewrite(stock_code)
            time.sleep(0.3)
            
            print(f"✅ 股票代码已输入: {stock_code}")
            return True
        except Exception as e:
            print(f"❌ 输入股票代码失败: {e}")
            return False
    
    def tab_to_next_field(self) -> bool:
        """Tab切换到下一个输入框"""
        try:
            pyautogui.press('tab')
            time.sleep(0.2)
            return True
        except Exception as e:
            print(f"❌ Tab切换失败: {e}")
            return False
    
    def input_price(self, price: float) -> bool:
        """输入价格"""
        print(f"💰 输入价格: {price}")
        try:
            # 清空当前输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # 输入价格（保留2位小数）
            price_str = f"{price:.2f}"
            pyautogui.typewrite(price_str)
            time.sleep(0.3)
            
            print(f"✅ 价格已输入: {price_str}")
            return True
        except Exception as e:
            print(f"❌ 输入价格失败: {e}")
            return False
    
    def input_quantity(self, quantity: int) -> bool:
        """输入数量"""
        print(f"🔢 输入数量: {quantity}")
        try:
            # 清空当前输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # 输入数量
            pyautogui.typewrite(str(quantity))
            time.sleep(0.3)
            
            print(f"✅ 数量已输入: {quantity}")
            return True
        except Exception as e:
            print(f"❌ 输入数量失败: {e}")
            return False
    
    def confirm_order(self, auto_confirm: bool = False) -> bool:
        """确认订单"""
        if auto_confirm:
            print("🚀 自动确认订单...")
            try:
                # 按回车确认
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # 如果有二次确认对话框，再次确认
                pyautogui.press('enter')
                time.sleep(0.3)
                
                print("✅ 订单已自动提交")
                return True
            except Exception as e:
                print(f"❌ 自动确认失败: {e}")
                return False
        else:
            print("⏸️ 等待手动确认...")
            print("   请在交易软件中手动点击确认按钮")
            return True
    
    def execute_buy_order(self, stock_code: str, price: float, quantity: int, auto_confirm: bool = False) -> bool:
        """执行买入订单"""
        print(f"\n🚀 执行买入订单")
        print(f"   股票代码: {stock_code}")
        print(f"   价格: ¥{price:.2f}")
        print(f"   数量: {quantity}")
        print(f"   自动确认: {'是' if auto_confirm else '否'}")
        print("-" * 40)
        
        try:
            # 1. 激活交易软件
            if not self.find_and_activate_trading_window():
                return False
            
            # 2. 导航到买入页面
            if not self.navigate_to_buy_page():
                return False
            
            # 3. 输入股票代码（第一个输入框）
            if not self.input_stock_code(stock_code):
                return False
            
            # 4. Tab切换到价格输入框
            if not self.tab_to_next_field():
                return False
            
            # 5. 输入价格
            if not self.input_price(price):
                return False
            
            # 6. Tab切换到数量输入框
            if not self.tab_to_next_field():
                return False
            
            # 7. 输入数量
            if not self.input_quantity(quantity):
                return False
            
            # 8. 确认订单
            if not self.confirm_order(auto_confirm):
                return False
            
            print("✅ 买入订单执行完成!")
            return True
            
        except Exception as e:
            print(f"❌ 执行买入订单失败: {e}")
            return False
    
    def execute_sell_order(self, stock_code: str, price: float, quantity: int, auto_confirm: bool = False) -> bool:
        """执行卖出订单"""
        print(f"\n🚀 执行卖出订单")
        print(f"   股票代码: {stock_code}")
        print(f"   价格: ¥{price:.2f}")
        print(f"   数量: {quantity}")
        print(f"   自动确认: {'是' if auto_confirm else '否'}")
        print("-" * 40)
        
        try:
            # 1. 激活交易软件
            if not self.find_and_activate_trading_window():
                return False
            
            # 2. 导航到卖出页面
            if not self.navigate_to_sell_page():
                return False
            
            # 3. 输入股票代码（第一个输入框）
            if not self.input_stock_code(stock_code):
                return False
            
            # 4. Tab切换到价格输入框
            if not self.tab_to_next_field():
                return False
            
            # 5. 输入价格
            if not self.input_price(price):
                return False
            
            # 6. Tab切换到数量输入框
            if not self.tab_to_next_field():
                return False
            
            # 7. 输入数量
            if not self.input_quantity(quantity):
                return False
            
            # 8. 确认订单
            if not self.confirm_order(auto_confirm):
                return False
            
            print("✅ 卖出订单执行完成!")
            return True
            
        except Exception as e:
            print(f"❌ 执行卖出订单失败: {e}")
            return False
    
    def check_fund_info(self) -> bool:
        """查看资金信息"""
        print("\n💰 查看资金信息")
        print("-" * 40)
        
        try:
            # 1. 激活交易软件
            if not self.find_and_activate_trading_window():
                return False
            
            # 2. 导航到资金页面
            if not self.navigate_to_fund_page():
                return False
            
            print("✅ 已切换到资金页面，请查看资金信息")
            return True
            
        except Exception as e:
            print(f"❌ 查看资金信息失败: {e}")
            return False

def test_hotkey_trader():
    """测试快捷键交易器"""
    print("🧪 测试快捷键交易系统")
    print("=" * 50)
    
    trader = HotkeySimpleTrader()
    
    # 测试基本功能
    print("\n1. 测试窗口激活...")
    if not trader.find_and_activate_trading_window():
        print("❌ 无法找到交易软件")
        return
    
    print("\n2. 测试页面导航...")
    
    # 测试买入页面
    test_buy_page = input("是否测试买入页面导航? (y/n): ")
    if test_buy_page.lower() == 'y':
        trader.navigate_to_buy_page()
    
    # 测试卖出页面
    test_sell_page = input("是否测试卖出页面导航? (y/n): ")
    if test_sell_page.lower() == 'y':
        trader.navigate_to_sell_page()
    
    # 测试资金页面
    test_fund_page = input("是否测试资金页面导航? (y/n): ")
    if test_fund_page.lower() == 'y':
        trader.check_fund_info()
    
    print("\n3. 测试完整交易流程...")
    
    # 测试买入流程
    test_buy = input("是否测试完整买入流程? (y/n): ")
    if test_buy.lower() == 'y':
        trader.execute_buy_order("600000", 10.50, 100, auto_confirm=False)
    
    # 测试卖出流程
    test_sell = input("是否测试完整卖出流程? (y/n): ")
    if test_sell.lower() == 'y':
        trader.execute_sell_order("600000", 10.60, 100, auto_confirm=False)
    
    print("\n🎉 测试完成!")
    print("💡 系统特点:")
    print("  ✅ 基于标准快捷键，简单可靠")
    print("  ✅ F1买入, F2卖出, F4资金, Tab切换")
    print("  ✅ 支持手动确认，安全可控")
    print("  ✅ 无需复杂配置，即用即可")

def main():
    print("⌨️ 基于快捷键的简单交易系统")
    print("=" * 50)
    print("🎯 快捷键说明:")
    print("  F1 - 买入界面")
    print("  F2 - 卖出界面") 
    print("  F4 - 资金页面")
    print("  Tab - 切换输入框")
    print("  Enter - 确认订单")
    print()
    print("⚠️ 使用前请确保:")
    print("  - 交易软件已打开并登录")
    print("  - 快捷键设置与上述一致")
    print("  - 首次使用建议先测试")
    print()
    
    try:
        test_hotkey_trader()
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
