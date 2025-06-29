#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的交易操作系统
基于您的实际交易软件界面进行操作
"""

import time
import win32gui
import win32con
import pyautogui
import win32api

class RealTradingOperation:
    """真正的交易操作器"""
    
    def __init__(self):
        self.window_handle = None
        pyautogui.FAILSAFE = False
        
    def find_trading_window(self):
        """查找交易软件窗口"""
        print("🔍 查找交易软件窗口...")
        
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "网上股票交易系统" in title or "股票交易" in title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if windows:
            self.window_handle, window_title = windows[0]
            print(f"✅ 找到交易软件: {window_title}")
            
            # 激活窗口
            try:
                if win32gui.IsIconic(self.window_handle):
                    win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                    time.sleep(1)
                
                win32gui.SetForegroundWindow(self.window_handle)
                time.sleep(0.5)
                print("✅ 交易软件已激活")
                return True
            except Exception as e:
                print(f"⚠️ 激活窗口时出现问题: {e}")
                return True
        
        print("❌ 未找到交易软件窗口")
        return False
    
    def click_buy_menu(self):
        """点击左侧的买入股票菜单"""
        print("🖱️ 点击买入股票菜单...")
        
        # 根据您的界面，买入股票菜单大概在左侧
        # 我们需要找到"买入股票"文字的位置
        try:
            # 先激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.3)
            
            # 获取窗口位置
            rect = win32gui.GetWindowRect(self.window_handle)
            left, top, right, bottom = rect
            
            # 估算买入股票菜单的位置（左侧菜单区域）
            menu_x = left + 60  # 左侧菜单大概位置
            menu_y = top + 100  # 买入股票选项大概位置
            
            print(f"   点击位置: ({menu_x}, {menu_y})")
            pyautogui.click(menu_x, menu_y)
            time.sleep(1)
            
            print("✅ 已点击买入股票菜单")
            return True
            
        except Exception as e:
            print(f"❌ 点击买入菜单失败: {e}")
            return False
    
    def input_stock_code_direct(self, stock_code):
        """直接在股票代码输入框输入"""
        print(f"📝 输入股票代码: {stock_code}")
        
        try:
            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.3)
            
            # 获取窗口位置
            rect = win32gui.GetWindowRect(self.window_handle)
            left, top, right, bottom = rect
            
            # 根据您的界面，股票代码输入框大概在右上方
            code_input_x = left + 300  # 估算位置
            code_input_y = top + 120
            
            print(f"   点击股票代码输入框: ({code_input_x}, {code_input_y})")
            pyautogui.click(code_input_x, code_input_y)
            time.sleep(0.3)
            
            # 清空并输入
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(stock_code)
            time.sleep(0.5)
            
            print(f"✅ 股票代码已输入: {stock_code}")
            return True
            
        except Exception as e:
            print(f"❌ 输入股票代码失败: {e}")
            return False
    
    def input_price_direct(self, price):
        """直接在价格输入框输入"""
        print(f"💰 输入价格: {price}")
        
        try:
            # 获取窗口位置
            rect = win32gui.GetWindowRect(self.window_handle)
            left, top, right, bottom = rect
            
            # 价格输入框位置（估算）
            price_input_x = left + 300
            price_input_y = top + 160
            
            print(f"   点击价格输入框: ({price_input_x}, {price_input_y})")
            pyautogui.click(price_input_x, price_input_y)
            time.sleep(0.3)
            
            # 清空并输入
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(f"{price:.2f}")
            time.sleep(0.5)
            
            print(f"✅ 价格已输入: {price:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ 输入价格失败: {e}")
            return False
    
    def input_quantity_direct(self, quantity):
        """直接在数量输入框输入"""
        print(f"🔢 输入数量: {quantity}")
        
        try:
            # 获取窗口位置
            rect = win32gui.GetWindowRect(self.window_handle)
            left, top, right, bottom = rect
            
            # 数量输入框位置（估算）
            quantity_input_x = left + 300
            quantity_input_y = top + 200
            
            print(f"   点击数量输入框: ({quantity_input_x}, {quantity_input_y})")
            pyautogui.click(quantity_input_x, quantity_input_y)
            time.sleep(0.3)
            
            # 清空并输入
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(str(quantity))
            time.sleep(0.5)
            
            print(f"✅ 数量已输入: {quantity}")
            return True
            
        except Exception as e:
            print(f"❌ 输入数量失败: {e}")
            return False
    
    def click_buy_button(self):
        """点击买入确认按钮"""
        print("🚀 点击买入确认按钮...")
        
        try:
            # 获取窗口位置
            rect = win32gui.GetWindowRect(self.window_handle)
            left, top, right, bottom = rect
            
            # 买入按钮位置（估算）
            buy_button_x = left + 350
            buy_button_y = top + 250
            
            print(f"   点击买入按钮: ({buy_button_x}, {buy_button_y})")
            pyautogui.click(buy_button_x, buy_button_y)
            time.sleep(1)
            
            print("✅ 已点击买入按钮")
            return True
            
        except Exception as e:
            print(f"❌ 点击买入按钮失败: {e}")
            return False
    
    def execute_real_buy_order(self, stock_code, price, quantity, confirm=False):
        """执行真实的买入订单"""
        print(f"\n🚀 执行真实买入订单")
        print(f"   股票代码: {stock_code}")
        print(f"   价格: ¥{price:.2f}")
        print(f"   数量: {quantity}")
        print("-" * 40)
        
        try:
            # 1. 查找并激活交易软件
            if not self.find_trading_window():
                return False
            
            # 2. 点击买入股票菜单
            if not self.click_buy_menu():
                return False
            
            # 3. 输入股票代码
            if not self.input_stock_code_direct(stock_code):
                return False
            
            # 4. 输入价格
            if not self.input_price_direct(price):
                return False
            
            # 5. 输入数量
            if not self.input_quantity_direct(quantity):
                return False
            
            # 6. 确认买入
            if confirm:
                confirm_final = input("⚠️ 确认提交买入订单? 这将执行真实交易! (yes/no): ")
                if confirm_final.lower() == 'yes':
                    if self.click_buy_button():
                        print("✅ 买入订单已提交!")
                        return True
                    else:
                        print("❌ 提交订单失败")
                        return False
                else:
                    print("⏸️ 订单未提交，信息已填入")
                    return True
            else:
                print("✅ 买入信息已填入，等待手动确认")
                return True
                
        except Exception as e:
            print(f"❌ 执行买入订单失败: {e}")
            return False
    
    def interactive_position_setup(self):
        """交互式位置设置"""
        print("\n🎯 交互式位置设置")
        print("请按照提示设置各个控件的精确位置")
        
        if not self.find_trading_window():
            return False
        
        print("\n📍 请将鼠标移动到以下位置，然后按回车记录坐标:")
        
        positions = {}
        
        # 记录各个控件位置
        controls = [
            ("buy_menu", "买入股票菜单"),
            ("stock_code_input", "股票代码输入框"),
            ("price_input", "价格输入框"),
            ("quantity_input", "数量输入框"),
            ("buy_button", "买入确认按钮")
        ]
        
        for control_id, control_name in controls:
            input(f"\n请将鼠标移动到 {control_name} 上，然后按回车...")
            x, y = pyautogui.position()
            positions[control_id] = (x, y)
            print(f"✅ {control_name} 位置已记录: ({x}, {y})")
        
        # 保存位置配置
        import json
        with open("trading_positions.json", "w", encoding="utf-8") as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 位置配置已保存到 trading_positions.json")
        return positions

def main():
    print("🎯 真正的交易操作系统")
    print("=" * 50)
    print("这将在您的实际交易软件中执行真实操作")
    print()
    
    trader = RealTradingOperation()
    
    # 选择操作模式
    print("请选择操作模式:")
    print("1. 交互式位置设置（推荐首次使用）")
    print("2. 直接执行买入操作")
    print("3. 测试窗口激活")
    
    choice = input("\n请输入选择 (1-3): ")
    
    if choice == "1":
        # 交互式位置设置
        trader.interactive_position_setup()
        
    elif choice == "2":
        # 直接执行买入操作
        print("\n📝 请输入买入参数:")
        stock_code = input("股票代码 (默认600000): ") or "600000"
        price_input = input("买入价格 (默认10.50): ") or "10.50"
        quantity_input = input("买入数量 (默认100): ") or "100"
        
        try:
            price = float(price_input)
            quantity = int(quantity_input)
        except ValueError:
            print("❌ 价格或数量格式错误")
            return
        
        confirm = input("是否自动确认订单? (y/n): ").lower() == 'y'
        
        trader.execute_real_buy_order(stock_code, price, quantity, confirm)
        
    elif choice == "3":
        # 测试窗口激活
        trader.find_trading_window()
        
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
