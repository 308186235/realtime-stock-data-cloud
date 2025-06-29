"""
最终优化版Win API账户余额获取器
"""

import win32gui
import win32api
import win32con
import time
import re
from datetime import datetime

class FinalBalanceReader:
    def __init__(self):
        self.window_handle = None
        
    def find_and_activate_trading_window(self):
        """查找并激活交易软件窗口"""
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
            
            # 激活窗口
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(1)
            
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            print(f" 找到交易软件: {window_title}")
            return True
        
        return False
    
    def navigate_to_funds_page(self):
        """导航到资金页面"""
        print(" 按F4进入资金页面...")
        win32api.keybd_event(0x73, 0, 0, 0)  # F4
        time.sleep(0.05)
        win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(2)
        return True
    
    def get_window_texts(self):
        """获取所有子窗口文本"""
        texts = []
        
        def enum_child_proc(hwnd, param):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    if text and text.strip():
                        texts.append(text.strip())
            except:
                pass
            return True
        
        win32gui.EnumChildWindows(self.window_handle, enum_child_proc, None)
        return texts
    
    def smart_parse_balance(self, texts):
        """智能解析余额数据"""
        balance_info = {
            'available_cash': 0.0,
            'total_assets': 0.0,
            'market_value': 0.0,
            'frozen_amount': 0.0
        }
        
        print(" 智能解析余额数据...")
        
        # 查找所有数字
        numbers = []
        for text in texts:
            if re.match(r'^[0-9,]+\.?[0-9]*$', text):
                try:
                    amount = float(text.replace(',', ''))
                    numbers.append(amount)
                except:
                    continue
        
        print(f"找到的数字: {numbers}")
        
        # 根据常见模式匹配
        # 通常顺序是：资金余额, 冻结金额, 可用金额, 可取金额, 股票市值, 总资产
        if len(numbers) >= 3:
            # 第一个通常是资金余额
            balance_info['total_assets'] = numbers[0]
            
            # 第二个通常是冻结金额
            balance_info['frozen_amount'] = numbers[1]
            
            # 第三个通常是可用金额
            balance_info['available_cash'] = numbers[2]
            
            # 查找股票市值（通常是0.00或者一个较大的数）
            for num in numbers[3:]:
                if num > 0 and num != balance_info['available_cash']:
                    balance_info['market_value'] = num
                    break
        
        # 验证数据合理性
        if balance_info['total_assets'] == 0 and balance_info['available_cash'] > 0:
            balance_info['total_assets'] = balance_info['available_cash'] + balance_info['market_value']
        
        return balance_info
    
    def get_account_balance(self):
        """获取账户余额"""
        print(" Win API获取账户余额")
        print("=" * 40)
        
        if not self.find_and_activate_trading_window():
            return None
        
        if not self.navigate_to_funds_page():
            return None
        
        texts = self.get_window_texts()
        balance_info = self.smart_parse_balance(texts)
        
        balance_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        balance_info['data_source'] = 'Win API'
        
        print("\\n 账户余额:")
        print(f"可用资金: {balance_info['available_cash']:,.2f}")
        print(f"总资产: {balance_info['total_assets']:,.2f}")
        print(f"股票市值: {balance_info['market_value']:,.2f}")
        print(f"冻结资金: {balance_info['frozen_amount']:,.2f}")
        
        return balance_info

def get_balance_winapi():
    """获取账户余额"""
    reader = FinalBalanceReader()
    return reader.get_account_balance()

if __name__ == "__main__":
    print(" 测试最终版Win API余额获取")
    balance = get_balance_winapi()
    
    if balance and balance['available_cash'] > 0:
        print("\\n 成功获取账户余额!")
        print(f" 可用资金: {balance['available_cash']:,.2f}")
    else:
        print("\\n 需要进一步调试")
