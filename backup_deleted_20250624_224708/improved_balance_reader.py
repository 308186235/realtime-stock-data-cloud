"""
改进版Win API账户余额获取器 - 修复文本解析逻辑
"""

import win32gui
import win32api
import win32con
import time
import re
from datetime import datetime

class ImprovedBalanceReader:
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
            
            print(f" 找到并激活交易软件: {window_title}")
            return True
        
        print(" 未找到交易软件窗口")
        return False
    
    def navigate_to_funds_page(self):
        """导航到资金页面"""
        print(" 按F4进入资金页面...")
        win32api.keybd_event(0x73, 0, 0, 0)  # F4按下
        time.sleep(0.05)
        win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)  # F4释放
        time.sleep(2)  # 等待页面加载
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
    
    def parse_balance_data(self, texts):
        """解析余额数据 - 改进版"""
        balance_info = {
            'available_cash': 0.0,
            'total_assets': 0.0,
            'market_value': 0.0,
            'frozen_amount': 0.0
        }
        
        print(" 解析余额数据...")
        print(f"获取到的文本: {texts}")
        
        # 查找标签和对应的数值
        for i, text in enumerate(texts):
            # 检查是否是数字
            if re.match(r'^[0-9,]+\.?[0-9]*$', text):
                try:
                    amount = float(text.replace(',', ''))
                    
                    # 查找前面的标签
                    for j in range(max(0, i-5), i):
                        label = texts[j]
                        
                        if '可用金额' in label or '可用资金' in label:
                            balance_info['available_cash'] = amount
                            print(f"    可用资金: {amount:,.2f}")
                            break
                        elif '资金余额' in label:
                            balance_info['total_assets'] = amount
                            print(f"    资金余额: {amount:,.2f}")
                            break
                        elif '股票市值' in label or '市值' in label:
                            balance_info['market_value'] = amount
                            print(f"    股票市值: {amount:,.2f}")
                            break
                        elif '冻结金额' in label or '冻结资金' in label:
                            balance_info['frozen_amount'] = amount
                            print(f"    冻结资金: {amount:,.2f}")
                            break
                            
                except ValueError:
                    continue
        
        # 如果总资产为0，用可用资金+市值计算
        if balance_info['total_assets'] == 0.0:
            balance_info['total_assets'] = balance_info['available_cash'] + balance_info['market_value']
        
        return balance_info
    
    def get_account_balance(self):
        """获取账户余额"""
        print(" Win API获取账户余额")
        print("=" * 40)
        
        # 1. 查找并激活交易软件
        if not self.find_and_activate_trading_window():
            return None
        
        # 2. 导航到资金页面
        if not self.navigate_to_funds_page():
            return None
        
        # 3. 获取窗口文本
        texts = self.get_window_texts()
        
        # 4. 解析余额数据
        balance_info = self.parse_balance_data(texts)
        
        # 5. 添加元数据
        balance_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        balance_info['data_source'] = 'Win API'
        
        # 6. 显示结果
        print("\\n 账户余额:")
        print(f"可用资金: {balance_info['available_cash']:,.2f}")
        print(f"总资产: {balance_info['total_assets']:,.2f}")
        print(f"股票市值: {balance_info['market_value']:,.2f}")
        print(f"冻结资金: {balance_info['frozen_amount']:,.2f}")
        print(f"更新时间: {balance_info['update_time']}")
        
        return balance_info

# 便捷接口
def get_balance_via_winapi():
    """获取账户余额的便捷接口"""
    reader = ImprovedBalanceReader()
    return reader.get_account_balance()

if __name__ == "__main__":
    print(" 测试改进版Win API余额获取")
    balance = get_balance_via_winapi()
    
    if balance and balance['available_cash'] > 0:
        print("\\n 成功获取到账户余额!")
    else:
        print("\\n 余额获取可能有问题")
