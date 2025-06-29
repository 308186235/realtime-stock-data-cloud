#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于坐标配置的可靠交易系统
通过手动配置关键控件位置实现精确操作
"""

import json
import time
import win32gui
import win32api
import win32con
import pyautogui
from typing import Dict, Any, Optional

class CoordinateBasedTrader:
    """基于坐标配置的交易操作器"""
    
    def __init__(self, config_file: str = "trading_coordinates.json"):
        self.config_file = config_file
        self.config = {}
        self.window_handle = None
        self.window_rect = None
        
        # 禁用pyautogui的安全检查
        pyautogui.FAILSAFE = False
        
    def load_config(self) -> bool:
        """加载坐标配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 配置加载成功: {self.config_file}")
            return True
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在: {self.config_file}")
            print("将启动配置向导...")
            return self.create_config()
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return False
    
    def find_trading_window(self) -> bool:
        """查找交易软件窗口"""
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "网上股票交易系统" in title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if windows:
            self.window_handle, window_title = windows[0]
            
            # 恢复窗口
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(1)
            
            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            # 获取窗口位置
            self.window_rect = win32gui.GetWindowRect(self.window_handle)
            print(f"✅ 找到交易软件: {window_title}")
            print(f"   窗口位置: {self.window_rect}")
            return True
        
        print("❌ 未找到交易软件窗口")
        return False
    
    def create_config(self) -> bool:
        """创建配置向导"""
        print("\n🎯 交易软件坐标配置向导")
        print("=" * 40)
        print("请按照提示配置各个控件的位置")
        print("⚠️ 请确保交易软件已打开并显示买入页面")
        
        if not self.find_trading_window():
            return False
        
        config = {
            "window_title": "网上股票交易系统5.0",
            "window_rect": self.window_rect,
            "controls": {}
        }
        
        # 配置各个控件位置
        controls_to_config = [
            ("stock_code_input", "股票代码输入框"),
            ("price_input", "价格输入框"), 
            ("quantity_input", "数量输入框"),
            ("buy_button", "买入确认按钮"),
            ("sell_button", "卖出确认按钮")
        ]
        
        print("\n📍 开始配置控件位置:")
        print("对于每个控件，请:")
        print("1. 将鼠标移动到对应控件上")
        print("2. 按回车键记录位置")
        
        for control_id, control_name in controls_to_config:
            print(f"\n🎯 配置 {control_name}:")
            input(f"请将鼠标移动到 {control_name} 上，然后按回车...")
            
            # 获取当前鼠标位置
            x, y = pyautogui.position()
            config["controls"][control_id] = {"x": x, "y": y}
            print(f"   已记录位置: ({x}, {y})")
        
        # 保存配置
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.config = config
            print(f"\n✅ 配置已保存到: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def click_control(self, control_id: str) -> bool:
        """点击指定控件"""
        if control_id not in self.config.get("controls", {}):
            print(f"❌ 控件 {control_id} 未配置")
            return False
        
        try:
            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.2)
            
            # 获取控件坐标
            control = self.config["controls"][control_id]
            x, y = control["x"], control["y"]
            
            # 点击控件
            pyautogui.click(x, y)
            time.sleep(0.3)
            
            print(f"✅ 点击控件 {control_id} 位置 ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"❌ 点击控件 {control_id} 失败: {e}")
            return False
    
    def input_text(self, control_id: str, text: str) -> bool:
        """在指定控件中输入文本"""
        if not self.click_control(control_id):
            return False
        
        try:
            # 清空现有内容
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # 输入新文本
            pyautogui.typewrite(str(text))
            time.sleep(0.2)
            
            print(f"✅ 在 {control_id} 中输入: {text}")
            return True
            
        except Exception as e:
            print(f"❌ 在 {control_id} 中输入失败: {e}")
            return False
    
    def execute_buy_order(self, stock_code: str, price: float, quantity: int) -> bool:
        """执行买入订单"""
        print(f"🚀 执行买入订单: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        try:
            # 1. 激活交易软件
            if not self.find_trading_window():
                return False
            
            # 2. 导航到买入页面 (F1)
            print("   导航到买入页面...")
            pyautogui.press('f1')
            time.sleep(1)
            
            # 3. 输入股票代码
            print("   输入股票代码...")
            if not self.input_text("stock_code_input", stock_code):
                return False
            
            # 4. 输入价格
            print("   输入价格...")
            if not self.input_text("price_input", f"{price:.2f}"):
                return False
            
            # 5. 输入数量
            print("   输入数量...")
            if not self.input_text("quantity_input", quantity):
                return False
            
            # 6. 确认买入 (可选)
            confirm = input("   是否确认提交买入订单? (y/n): ")
            if confirm.lower() == 'y':
                print("   点击买入按钮...")
                if self.click_control("buy_button"):
                    print("✅ 买入订单已提交")
                    return True
                else:
                    print("❌ 点击买入按钮失败")
                    return False
            else:
                print("   订单信息已填入，等待手动确认")
                return True
                
        except Exception as e:
            print(f"❌ 执行买入订单失败: {e}")
            return False
    
    def execute_sell_order(self, stock_code: str, price: float, quantity: int) -> bool:
        """执行卖出订单"""
        print(f"🚀 执行卖出订单: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        try:
            # 1. 激活交易软件
            if not self.find_trading_window():
                return False
            
            # 2. 导航到卖出页面 (F2)
            print("   导航到卖出页面...")
            pyautogui.press('f2')
            time.sleep(1)
            
            # 3. 输入股票代码
            print("   输入股票代码...")
            if not self.input_text("stock_code_input", stock_code):
                return False
            
            # 4. 输入价格
            print("   输入价格...")
            if not self.input_text("price_input", f"{price:.2f}"):
                return False
            
            # 5. 输入数量
            print("   输入数量...")
            if not self.input_text("quantity_input", quantity):
                return False
            
            # 6. 确认卖出 (可选)
            confirm = input("   是否确认提交卖出订单? (y/n): ")
            if confirm.lower() == 'y':
                print("   点击卖出按钮...")
                if self.click_control("sell_button"):
                    print("✅ 卖出订单已提交")
                    return True
                else:
                    print("❌ 点击卖出按钮失败")
                    return False
            else:
                print("   订单信息已填入，等待手动确认")
                return True
                
        except Exception as e:
            print(f"❌ 执行卖出订单失败: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """测试配置是否正确"""
        print("🧪 测试配置...")
        
        if not self.load_config():
            return False
        
        if not self.find_trading_window():
            return False
        
        print("测试各个控件位置:")
        
        for control_id, control_info in self.config.get("controls", {}).items():
            print(f"   测试 {control_id}...")
            x, y = control_info["x"], control_info["y"]
            
            # 移动鼠标到控件位置（不点击）
            pyautogui.moveTo(x, y)
            time.sleep(0.5)
            
            confirm = input(f"   鼠标是否在正确的 {control_id} 位置? (y/n): ")
            if confirm.lower() != 'y':
                print(f"   ❌ {control_id} 位置不正确")
                return False
        
        print("✅ 配置测试通过")
        return True

def main():
    print("🎯 基于坐标配置的可靠交易系统")
    print("=" * 50)
    print("这个系统通过精确的坐标配置实现可靠的自动交易")
    print()
    
    trader = CoordinateBasedTrader()
    
    # 测试配置
    if not trader.test_configuration():
        print("❌ 配置测试失败")
        return
    
    # 演示交易操作
    print("\n🚀 演示交易操作:")
    
    # 演示买入
    demo_buy = input("是否演示买入操作? (y/n): ")
    if demo_buy.lower() == 'y':
        trader.execute_buy_order("600000", 10.50, 100)
    
    # 演示卖出
    demo_sell = input("是否演示卖出操作? (y/n): ")
    if demo_sell.lower() == 'y':
        trader.execute_sell_order("600000", 10.60, 100)
    
    print("\n🎉 演示完成!")
    print("💡 这个方法的优势:")
    print("  ✅ 精确定位到具体控件")
    print("  ✅ 可以验证每步操作")
    print("  ✅ 支持手动确认机制")
    print("  ✅ 配置一次，长期使用")

if __name__ == "__main__":
    main()
