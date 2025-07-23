#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单交易热键系统
通过键盘快捷键快速执行买卖操作
适用于华宝证券智投版等交易软件
"""

import keyboard
import pyautogui
import time
import json
import win32gui
import win32con
from datetime import datetime

class SimpleTradingHotkeys:
    def __init__(self):
        self.is_running = False
        self.trading_window = None
        self.config_file = "trading_config.json"
        self.load_config()
        
        # 设置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 默认配置
            self.config = {
                "default_quantity": 100,
                "default_stocks": {
                    "1": {"code": "000001", "name": "平安银行"},
                    "2": {"code": "000002", "name": "万科A"},
                    "3": {"code": "600036", "name": "招商银行"},
                    "4": {"code": "600519", "name": "贵州茅台"},
                    "5": {"code": "000858", "name": "五粮液"}
                },
                "hotkeys": {
                    "buy_1": "ctrl+shift+1",
                    "sell_1": "ctrl+alt+1",
                    "buy_2": "ctrl+shift+2", 
                    "sell_2": "ctrl+alt+2",
                    "emergency_stop": "ctrl+shift+esc"
                }
            }
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def find_trading_window(self):
        """查找交易窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "华宝证券" in window_text or "交易" in window_text:
                    self.trading_window = hwnd
                    return False
            return True
        
        win32gui.EnumWindows(enum_windows_callback, [])
        return self.trading_window is not None
    
    def activate_trading_window(self):
        """激活交易窗口"""
        if self.trading_window:
            try:
                win32gui.SetForegroundWindow(self.trading_window)
                win32gui.ShowWindow(self.trading_window, win32con.SW_RESTORE)
                time.sleep(0.5)
                return True
            except:
                return False
        return False
    
    def quick_buy(self, stock_key):
        """快速买入"""
        if stock_key not in self.config["default_stocks"]:
            print(f"❌ 未配置股票 {stock_key}")
            return
        
        stock = self.config["default_stocks"][stock_key]
        print(f"🔥 快速买入: {stock['name']} ({stock['code']})")
        
        if not self.find_trading_window():
            print("❌ 未找到交易窗口")
            return
        
        if not self.activate_trading_window():
            print("❌ 无法激活交易窗口")
            return
        
        # 模拟按键序列
        try:
            # 按F1进入买入界面(很多交易软件的快捷键)
            pyautogui.press('f1')
            time.sleep(0.5)
            
            # 输入股票代码
            pyautogui.typewrite(stock['code'])
            time.sleep(0.3)
            
            # Tab到数量输入框
            pyautogui.press('tab')
            time.sleep(0.2)
            
            # 输入数量
            pyautogui.typewrite(str(self.config["default_quantity"]))
            time.sleep(0.3)
            
            # Tab到价格输入框(通常会自动填入当前价格)
            pyautogui.press('tab')
            time.sleep(0.2)
            
            print(f"✅ 已填入买入信息,请手动确认价格并点击买入")
            
        except Exception as e:
            print(f"❌ 买入操作失败: {e}")
    
    def quick_sell(self, stock_key):
        """快速卖出"""
        if stock_key not in self.config["default_stocks"]:
            print(f"❌ 未配置股票 {stock_key}")
            return
        
        stock = self.config["default_stocks"][stock_key]
        print(f"🔥 快速卖出: {stock['name']} ({stock['code']})")
        
        if not self.find_trading_window():
            print("❌ 未找到交易窗口")
            return
        
        if not self.activate_trading_window():
            print("❌ 无法激活交易窗口")
            return
        
        # 模拟按键序列
        try:
            # 按F2进入卖出界面(很多交易软件的快捷键)
            pyautogui.press('f2')
            time.sleep(0.5)
            
            # 输入股票代码
            pyautogui.typewrite(stock['code'])
            time.sleep(0.3)
            
            # Tab到数量输入框
            pyautogui.press('tab')
            time.sleep(0.2)
            
            # 输入数量
            pyautogui.typewrite(str(self.config["default_quantity"]))
            time.sleep(0.3)
            
            # Tab到价格输入框
            pyautogui.press('tab')
            time.sleep(0.2)
            
            print(f"✅ 已填入卖出信息,请手动确认价格并点击卖出")
            
        except Exception as e:
            print(f"❌ 卖出操作失败: {e}")
    
    def emergency_stop(self):
        """紧急停止"""
        print("🚨 紧急停止所有操作!")
        pyautogui.press('esc')
        pyautogui.press('esc')
        pyautogui.press('esc')
    
    def setup_hotkeys(self):
        """设置热键"""
        print("🔧 设置交易热键...")
        
        # 买入热键
        keyboard.add_hotkey('ctrl+shift+1', lambda: self.quick_buy('1'))
        keyboard.add_hotkey('ctrl+shift+2', lambda: self.quick_buy('2'))
        keyboard.add_hotkey('ctrl+shift+3', lambda: self.quick_buy('3'))
        keyboard.add_hotkey('ctrl+shift+4', lambda: self.quick_buy('4'))
        keyboard.add_hotkey('ctrl+shift+5', lambda: self.quick_buy('5'))
        
        # 卖出热键
        keyboard.add_hotkey('ctrl+alt+1', lambda: self.quick_sell('1'))
        keyboard.add_hotkey('ctrl+alt+2', lambda: self.quick_sell('2'))
        keyboard.add_hotkey('ctrl+alt+3', lambda: self.quick_sell('3'))
        keyboard.add_hotkey('ctrl+alt+4', lambda: self.quick_sell('4'))
        keyboard.add_hotkey('ctrl+alt+5', lambda: self.quick_sell('5'))
        
        # 紧急停止
        keyboard.add_hotkey('ctrl+shift+esc', self.emergency_stop)
        
        print("✅ 热键设置完成!")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*60)
        print("🚀 华宝证券智投版 - 交易热键系统")
        print("="*60)
        print("\n📋 快捷键说明:")
        print("-" * 40)
        
        for key, stock in self.config["default_stocks"].items():
            print(f"买入 {stock['name']}: Ctrl+Shift+{key}")
            print(f"卖出 {stock['name']}: Ctrl+Alt+{key}")
            print()
        
        print("紧急停止: Ctrl+Shift+Esc")
        print("\n⚠️  注意事项:")
        print("1. 请确保交易软件已经登录")
        print("2. 热键只会填入股票代码和数量,价格需要手动确认")
        print("3. 请在确认价格无误后再点击买入/卖出按钮")
        print("4. 默认交易数量:", self.config["default_quantity"], "股")
        print("\n按 Ctrl+C 退出程序")
        print("="*60)
    
    def run(self):
        """运行热键系统"""
        self.show_help()
        self.setup_hotkeys()
        self.is_running = True
        
        try:
            print("\n🟢 交易热键系统已启动,等待热键输入...")
            keyboard.wait()  # 等待热键输入
        except KeyboardInterrupt:
            print("\n🔴 交易热键系统已停止")
            self.is_running = False

# 配置管理器
class TradingConfigManager:
    def __init__(self):
        self.hotkey_system = SimpleTradingHotkeys()
    
    def configure_stocks(self):
        """配置股票"""
        print("\n📝 配置常用股票")
        print("-" * 30)
        
        for i in range(1, 6):
            print(f"\n配置股票 {i}:")
            code = input("股票代码: ").strip()
            name = input("股票名称: ").strip()
            
            if code and name:
                self.hotkey_system.config["default_stocks"][str(i)] = {
                    "code": code,
                    "name": name
                }
                print(f"✅ 已配置: {name} ({code})")
            else:
                print("❌ 跳过配置")
        
        self.hotkey_system.save_config()
        print("\n✅ 股票配置已保存")
    
    def configure_quantity(self):
        """配置默认数量"""
        current = self.hotkey_system.config["default_quantity"]
        print(f"\n📊 当前默认交易数量: {current} 股")
        
        new_quantity = input("请输入新的默认数量 (直接回车保持不变): ").strip()
        
        if new_quantity and new_quantity.isdigit():
            self.hotkey_system.config["default_quantity"] = int(new_quantity)
            self.hotkey_system.save_config()
            print(f"✅ 默认交易数量已更新为: {new_quantity} 股")
        else:
            print("❌ 保持原设置")
    
    def show_config_menu(self):
        """显示配置菜单"""
        while True:
            print("\n🔧 交易系统配置")
            print("=" * 30)
            print("1. 配置常用股票")
            print("2. 配置默认交易数量")
            print("3. 查看当前配置")
            print("4. 启动交易热键系统")
            print("5. 退出")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == '1':
                self.configure_stocks()
            elif choice == '2':
                self.configure_quantity()
            elif choice == '3':
                self.show_current_config()
            elif choice == '4':
                self.hotkey_system.run()
                break
            elif choice == '5':
                print("👋 退出配置")
                break
            else:
                print("❌ 无效选择")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n📋 当前配置:")
        print("-" * 30)
        print(f"默认交易数量: {self.hotkey_system.config['default_quantity']} 股")
        print("\n配置的股票:")
        
        for key, stock in self.hotkey_system.config["default_stocks"].items():
            print(f"  {key}. {stock['name']} ({stock['code']})")

if __name__ == "__main__":
    print("🚀 华宝证券智投版 - 交易自动化系统")
    print("选择运行模式:")
    print("1. 直接启动热键系统")
    print("2. 配置管理")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == '1':
        hotkey_system = SimpleTradingHotkeys()
        hotkey_system.run()
    elif choice == '2':
        config_manager = TradingConfigManager()
        config_manager.show_config_menu()
    else:
        print("❌ 无效选择")
