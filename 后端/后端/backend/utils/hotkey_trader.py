#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷键交易模块 - 通过快捷键自动执行东吴证券交易操作
支持买入,卖出,查询持仓,查询资金等功能
"""

import win32gui
import win32con
import win32api
import time
import sys
import os
import json
import re
import pyautogui
import threading
import keyboard
from datetime import datetime

# 定义东吴证券常用功能键
DONGWU_HOTKEYS = {
    'BUY': 'F1',          # 买入页面
    'SELL': 'F2',         # 卖出页面
    'ORDER': 'F3',        # 委托页面
    'POSITION': 'F4',     # 持仓页面
    'FUND': 'F5',         # 资金页面
    'CANCEL': 'F6',       # 撤单页面
    'CONFIRM': 'Enter',   # 确认操作
    'TAB': 'Tab',         # 切换输入框
    'ESCAPE': 'Esc'       # 取消操作
}

class HotkeyTrader:
    """快捷键交易工具,支持自动买入卖出,一键交易等功能"""
    
    def __init__(self, config_file=None):
        """初始化快捷键交易工具"""
        self.config = self._load_config(config_file)
        self.trading_active = False
        self.hotkey_thread = None
        self.last_operation = None
        self.last_operation_time = None
        
        # 保存窗口信息
        self.dongwu_window = None
        self.window_title = ""
        
    def _load_config(self, config_file=None):
        """加载配置文件"""
        default_config = {
            "窗口标题": ["东吴证券", "网上股票交易系统"],
            "快捷键": {
                "买入": "F1",
                "卖出": "F2",
                "委托": "F3",
                "资金": "F4",
                "持仓": "F5"
            },
            "默认交易参数": {
                "最小交易数量": 100,
                "数量倍数": 100,
                "价格精度": 2,
                "延迟时间": 0.3
            },
            "自定义快捷键": {
                "一键买入": "ctrl+1",
                "一键卖出": "ctrl+2",
                "一键查持仓": "ctrl+3",
                "一键查资金": "ctrl+4"
            },
            "安全设置": {
                "操作间隔最小时间": 1,  # 秒
                "最大单笔交易额": 100000,  # 元
                "需要二次确认的金额": 50000  # 元
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置,优先使用用户配置
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                print(f"✅ 已加载用户配置: {config_file}")
            except Exception as e:
                print(f"❌ 加载配置失败: {e}")
        
        return default_config
    
    def find_dongwu_window(self):
        """查找东吴证券交易窗口"""
        print("🔍 正在查找东吴证券交易窗口...")
        
        window_titles = self.config["窗口标题"]
        dongwu_windows = []
        
        def find_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                for title in window_titles:
                    if title in window_text:
                        windows.append((hwnd, window_text))
                        break
            return True
        
        win32gui.EnumWindows(find_window_callback, dongwu_windows)
        
        if not dongwu_windows:
            print("❌ 未找到东吴证券交易窗口")
            return False
        
        self.dongwu_window, self.window_title = dongwu_windows[0]
        print(f"✅ 找到东吴证券窗口: {self.window_title}")
        return True
    
    def send_key(self, key, alt=False, ctrl=False):
        """向东吴证券窗口发送按键"""
        if not self.dongwu_window and not self.find_dongwu_window():
            return False

        try:
            # 激活窗口 - 使用安全的方法
            try:
                win32gui.SetForegroundWindow(self.dongwu_window)
            except:
                try:
                    # 备用方法:先置顶再设置前台
                    win32gui.SetWindowPos(self.dongwu_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    time.sleep(0.1)
                    win32gui.SetWindowPos(self.dongwu_window, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    time.sleep(0.1)
                    win32gui.SetForegroundWindow(self.dongwu_window)
                except:
                    # 最后的备用方法:只确保窗口可见
                    win32gui.ShowWindow(self.dongwu_window, win32con.SW_SHOW)
                    win32gui.BringWindowToTop(self.dongwu_window)
            time.sleep(0.5)
            
            # 按下修饰键
            if alt:
                win32api.keybd_event(0x12, 0, 0, 0)  # ALT键按下
            if ctrl:
                win32api.keybd_event(0x11, 0, 0, 0)  # CTRL键按下
            
            time.sleep(0.1)
            
            # 功能键映射
            if key.upper().startswith('F') and len(key) <= 3:
                vk_codes = {
                    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
                    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
                    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B
                }
                
                if key.upper() in vk_codes:
                    vk_code = vk_codes[key.upper()]
                    win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
                    time.sleep(0.1)
                    win32api.keybd_event(vk_code, 0, 2, 0)  # 释放
            
            # 回车键
            elif key.upper() == 'ENTER':
                win32api.keybd_event(0x0D, 0, 0, 0)  # 按下
                time.sleep(0.1)
                win32api.keybd_event(0x0D, 0, 2, 0)  # 释放
            
            # Tab键
            elif key.upper() == 'TAB':
                win32api.keybd_event(0x09, 0, 0, 0)  # 按下
                time.sleep(0.1)
                win32api.keybd_event(0x09, 0, 2, 0)  # 释放
            
            # ESC键
            elif key.upper() == 'ESC':
                win32api.keybd_event(0x1B, 0, 0, 0)  # 按下
                time.sleep(0.1)
                win32api.keybd_event(0x1B, 0, 2, 0)  # 释放
            
            # 普通字符键
            else:
                for char in key:
                    # 数字键单独处理
                    if char.isdigit():
                        vk_code = ord(char) 
                    else:
                        vk_code = ord(char.upper())
                    
                    win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
                    time.sleep(0.05)
                    win32api.keybd_event(vk_code, 0, 2, 0)  # 释放
                    time.sleep(0.05)
            
            time.sleep(0.1)
            
            # 释放修饰键
            if ctrl:
                win32api.keybd_event(0x11, 0, 2, 0)  # CTRL键释放
            if alt:
                win32api.keybd_event(0x12, 0, 2, 0)  # ALT键释放
            
            time.sleep(self.config["默认交易参数"]["延迟时间"])
            
            self.last_operation = key
            self.last_operation_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"❌ 发送按键失败: {e}")
            return False
    
    def navigate_to_buy(self):
        """导航到买入页面"""
        return self.send_key(self.config["快捷键"]["买入"])
    
    def navigate_to_sell(self):
        """导航到卖出页面"""
        return self.send_key(self.config["快捷键"]["卖出"])
    
    def navigate_to_position(self):
        """导航到持仓页面"""
        return self.send_key(self.config["快捷键"]["持仓"])
    
    def navigate_to_fund(self):
        """导航到资金页面"""
        return self.send_key(self.config["快捷键"]["资金"])
        
    def input_stock_code(self, stock_code):
        """输入股票代码"""
        if not stock_code or not re.match(r'^\d{6}$', stock_code):
            print(f"❌ 无效的股票代码: {stock_code}")
            return False
            
        # 清空当前输入框
        self.send_key('ESC')
        time.sleep(0.2)
        
        # 输入股票代码
        for digit in stock_code:
            self.send_key(digit)
            time.sleep(0.05)
        
        time.sleep(0.5)
        return True
    
    def input_price(self, price):
        """输入价格"""
        if not isinstance(price, (int, float)) or price <= 0:
            print(f"❌ 无效的价格: {price}")
            return False
            
        # 切换到价格输入框
        self.send_key('TAB')
        time.sleep(0.2)
        
        # 清空当前输入框
        self.send_key('ESC')
        time.sleep(0.2)
        
        # 转换价格为字符串并按位输入
        price_str = str(round(price, self.config["默认交易参数"]["价格精度"]))
        for digit in price_str:
            if digit == '.':
                self.send_key('.')
            else:
                self.send_key(digit)
            time.sleep(0.05)
        
        time.sleep(0.3)
        return True
    
    def input_quantity(self, quantity):
        """输入数量"""
        if not isinstance(quantity, int) or quantity <= 0:
            print(f"❌ 无效的数量: {quantity}")
            return False
            
        # 确保数量符合最小交易单位
        min_quantity = self.config["默认交易参数"]["最小交易数量"]
        quantity_multiple = self.config["默认交易参数"]["数量倍数"]
        
        if quantity < min_quantity:
            quantity = min_quantity
            print(f"⚠️ 数量已调整为最小交易单位: {min_quantity}")
        
        if quantity % quantity_multiple != 0:
            quantity = (quantity // quantity_multiple) * quantity_multiple
            print(f"⚠️ 数量已调整为交易单位倍数: {quantity}")
            
        # 切换到数量输入框
        self.send_key('TAB')
        time.sleep(0.2)
        
        # 清空当前输入框
        self.send_key('ESC')
        time.sleep(0.2)
        
        # 输入数量
        quantity_str = str(quantity)
        for digit in quantity_str:
            self.send_key(digit)
            time.sleep(0.05)
        
        time.sleep(0.3)
        return True
    
    def confirm_order(self):
        """确认下单"""
        # 使用回车键确认
        return self.send_key('ENTER')
    
    def execute_buy(self, stock_code, price, quantity):
        """执行买入操作"""
        print(f"🚀 执行买入操作: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        # 安全检查
        if not self._safety_check(price, quantity):
            return False
        
        # 导航到买入页面
        if not self.navigate_to_buy():
            return False
            
        # 输入股票代码
        if not self.input_stock_code(stock_code):
            return False
            
        # 输入价格
        if not self.input_price(price):
            return False
            
        # 输入数量
        if not self.input_quantity(quantity):
            return False
            
        # 确认下单
        if self.confirm_order():
            print(f"✅ 买入委托已提交: {stock_code}, 价格: {price}, 数量: {quantity}")
            return True
        else:
            print("❌ 买入委托提交失败")
            return False
    
    def execute_sell(self, stock_code, price, quantity):
        """执行卖出操作"""
        print(f"🚀 执行卖出操作: {stock_code}, 价格: {price}, 数量: {quantity}")
        
        # 安全检查
        if not self._safety_check(price, quantity):
            return False
        
        # 导航到卖出页面
        if not self.navigate_to_sell():
            return False
            
        # 输入股票代码
        if not self.input_stock_code(stock_code):
            return False
            
        # 输入价格
        if not self.input_price(price):
            return False
            
        # 输入数量
        if not self.input_quantity(quantity):
            return False
            
        # 确认下单
        if self.confirm_order():
            print(f"✅ 卖出委托已提交: {stock_code}, 价格: {price}, 数量: {quantity}")
            return True
        else:
            print("❌ 卖出委托提交失败")
            return False
    
    def _safety_check(self, price, quantity):
        """交易安全检查"""
        # 检查交易金额是否超限
        trade_amount = price * quantity
        max_amount = self.config["安全设置"]["最大单笔交易额"]
        
        if trade_amount > max_amount:
            print(f"⚠️ 安全警告: 交易金额 {trade_amount} 元超过最大限制 {max_amount} 元")
            confirm = input("是否继续交易? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ 交易已取消")
                return False
        
        # 检查是否需要二次确认
        confirm_amount = self.config["安全设置"]["需要二次确认的金额"]
        if trade_amount > confirm_amount:
            confirm = input(f"交易金额 {trade_amount} 元较大,请确认继续 (y/n): ")
            if confirm.lower() != 'y':
                print("❌ 交易已取消")
                return False
        
        # 检查操作间隔时间
        if self.last_operation_time:
            time_diff = (datetime.now() - self.last_operation_time).total_seconds()
            min_interval = self.config["安全设置"]["操作间隔最小时间"]
            
            if time_diff < min_interval:
                wait_time = min_interval - time_diff
                print(f"⏳ 操作过于频繁,等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
        
        return True
    
    def register_hotkeys(self):
        """注册全局快捷键"""
        if self.trading_active:
            print("⚠️ 快捷键已经激活,请勿重复注册")
            return
            
        custom_keys = self.config["自定义快捷键"]
        
        try:
            # 注册一键买入
            keyboard.add_hotkey(custom_keys["一键买入"], self._quick_buy_handler)
            
            # 注册一键卖出
            keyboard.add_hotkey(custom_keys["一键卖出"], self._quick_sell_handler)
            
            # 注册一键查持仓
            keyboard.add_hotkey(custom_keys["一键查持仓"], self._quick_position_handler)
            
            # 注册一键查资金
            keyboard.add_hotkey(custom_keys["一键查资金"], self._quick_fund_handler)
            
            self.trading_active = True
            print(f"✅ 快捷键交易已激活!")
            print(f"📋 {custom_keys['一键买入']}: 一键买入")
            print(f"📋 {custom_keys['一键卖出']}: 一键卖出")
            print(f"📋 {custom_keys['一键查持仓']}: 一键查看持仓")
            print(f"📋 {custom_keys['一键查资金']}: 一键查看资金")
            
        except Exception as e:
            print(f"❌ 注册快捷键失败: {e}")
    
    def _quick_buy_handler(self):
        """一键买入处理函数"""
        if not self.trading_active:
            return
            
        print("\n🔵 触发一键买入快捷键")
        
        # 获取买入参数
        stock_code = input("请输入股票代码: ")
        if not re.match(r'^\d{6}$', stock_code):
            print("❌ 无效的股票代码")
            return
            
        try:
            price = float(input("请输入买入价格: "))
            quantity = int(input("请输入买入数量: "))
        except ValueError:
            print("❌ 无效的价格或数量")
            return
            
        # 执行买入
        self.execute_buy(stock_code, price, quantity)
    
    def _quick_sell_handler(self):
        """一键卖出处理函数"""
        if not self.trading_active:
            return
            
        print("\n🔴 触发一键卖出快捷键")
        
        # 获取卖出参数
        stock_code = input("请输入股票代码: ")
        if not re.match(r'^\d{6}$', stock_code):
            print("❌ 无效的股票代码")
            return
            
        try:
            price = float(input("请输入卖出价格: "))
            quantity = int(input("请输入卖出数量: "))
        except ValueError:
            print("❌ 无效的价格或数量")
            return
            
        # 执行卖出
        self.execute_sell(stock_code, price, quantity)
    
    def _quick_position_handler(self):
        """一键查看持仓处理函数"""
        if not self.trading_active:
            return
            
        print("\n📊 查看持仓信息")
        self.navigate_to_position()
    
    def _quick_fund_handler(self):
        """一键查看资金处理函数"""
        if not self.trading_active:
            return
            
        print("\n💰 查看资金信息")
        self.navigate_to_fund()
    
    def start(self):
        """启动快捷键交易系统"""
        if not self.find_dongwu_window():
            print("❌ 无法启动快捷键交易系统: 未找到东吴证券窗口")
            return False
            
        self.register_hotkeys()
        
        # 启动热键监听线程
        self.hotkey_thread = threading.Thread(target=keyboard.wait)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()
        
        return True
    
    def stop(self):
        """停止快捷键交易系统"""
        if not self.trading_active:
            return
            
        # 清除所有热键
        keyboard.unhook_all()
        self.trading_active = False
        print("🛑 快捷键交易系统已停止")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 东吴证券快捷键交易工具")
    print("=" * 60)
    
    # 获取配置文件路径
    config_file = "config/hotkey_trader_config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # 创建快捷键交易工具
    trader = HotkeyTrader(config_file)
    
    # 启动快捷键交易系统
    if trader.start():
        print("\n✅ 快捷键交易系统已启动")
        print("使用快捷键即可快速交易,按Ctrl+C退出")
        
        try:
            # 保持程序运行
            while trader.trading_active:
                time.sleep(1)
        except KeyboardInterrupt:
            # 捕获Ctrl+C退出
            trader.stop()
            print("\n👋 感谢使用快捷键交易工具,再见!")
    else:
        print("\n❌ 快捷键交易系统启动失败")
    
    print("=" * 60)


if __name__ == "__main__":
    main() 
