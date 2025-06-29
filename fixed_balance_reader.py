"""
修复版Win API余额获取器 - 获取后切换回买卖页面
"""

import win32gui
import win32api
import win32con
import time
import re
from datetime import datetime

class FixedBalanceReader:
    def __init__(self):
        self.window_handle = None
        
    def find_and_activate_trading_window(self):
        """查找并激活交易软件窗口"""
        print(" 开始查找交易软件窗口...")

        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                print(f"   检查窗口: {title}")
                # 更宽松的匹配条件
                if ("网上股票交易系统" in title or
                    "股票交易" in title or
                    "东吴" in title or
                    "交易系统" in title):
                    print(f"   ✅ 找到匹配窗口: {title}")
                    windows.append((hwnd, title))
            return True

        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        print(f" 总共找到 {len(windows)} 个匹配窗口")

        if windows:
            self.window_handle, window_title = windows[0]

            try:
                # 如果窗口最小化，先恢复
                if win32gui.IsIconic(self.window_handle):
                    win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                    time.sleep(1)

                # 尝试多种方法激活窗口
                try:
                    # 方法1: 直接设置前台窗口
                    win32gui.SetForegroundWindow(self.window_handle)
                except:
                    try:
                        # 方法2: 先置顶再设置前台
                        win32gui.SetWindowPos(self.window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        time.sleep(0.1)
                        win32gui.SetWindowPos(self.window_handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        time.sleep(0.1)
                        win32gui.SetForegroundWindow(self.window_handle)
                    except:
                        # 方法3: 只是确保窗口可见，不强制激活
                        win32gui.ShowWindow(self.window_handle, win32con.SW_SHOW)
                        win32gui.BringWindowToTop(self.window_handle)

                time.sleep(0.5)
                print(f" 找到交易软件: {window_title}")
                return True

            except Exception as e:
                print(f" 激活窗口时出现问题: {e}")
                # 即使激活失败，也继续尝试操作
                print(f" 找到交易软件: {window_title} (可能未完全激活)")
                return True

        return False
    
    def navigate_to_funds_page(self):
        """导航到F4资金页面获取余额"""
        print(" 按F4进入资金页面获取余额...")
        win32api.keybd_event(0x73, 0, 0, 0)  # F4
        time.sleep(0.05)
        win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(2)
        return True
    
    def navigate_to_trading_page(self):
        """获取余额后切换到F1买卖页面"""
        print(" 获取余额后切换到F1买卖页面...")
        win32api.keybd_event(0x70, 0, 0, 0)  # F1
        time.sleep(0.05)
        win32api.keybd_event(0x70, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(2)
        print(" 已切换到F1买卖页面(确保W/E/R键有效)")
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
        if len(numbers) >= 3:
            balance_info['total_assets'] = numbers[0]
            balance_info['frozen_amount'] = numbers[1]
            balance_info['available_cash'] = numbers[2]
            
            for num in numbers[3:]:
                if num > 0 and num != balance_info['available_cash']:
                    balance_info['market_value'] = num
                    break
        
        if balance_info['total_assets'] == 0 and balance_info['available_cash'] > 0:
            balance_info['total_assets'] = balance_info['available_cash'] + balance_info['market_value']
        
        return balance_info
    
    def get_account_balance(self):
        """获取账户余额 - 修复版(获取后切换回买卖页面)"""
        print(" 修复版Win API获取账户余额")
        print("=" * 50)

        # 1. 查找并激活交易软件
        if not self.find_and_activate_trading_window():
            print("❌ 无法找到或激活交易软件窗口")
            return None

        print(f"✅ 交易软件窗口句柄: {self.window_handle}")
        
        # 2. 导航到F4资金页面
        if not self.navigate_to_funds_page():
            return None
        
        # 3. 获取窗口文本
        texts = self.get_window_texts()
        
        # 4. 解析余额数据
        balance_info = self.smart_parse_balance(texts)
        
        # 5. 【关键修复】获取余额后切换回F1买卖页面
        self.navigate_to_trading_page()
        
        # 6. 添加元数据
        balance_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        balance_info['data_source'] = 'Win API (修复版)'
        
        # 7. 显示结果
        print("\\n 账户余额:")
        print(f"可用资金: {balance_info['available_cash']:,.2f}")
        print(f"总资产: {balance_info['total_assets']:,.2f}")
        print(f"股票市值: {balance_info['market_value']:,.2f}")
        print(f"冻结资金: {balance_info['frozen_amount']:,.2f}")
        print(" 修复: 获取余额后已切换回买卖页面")
        
        return balance_info

def get_balance_fixed():
    """修复版获取账户余额"""
    reader = FixedBalanceReader()
    return reader.get_account_balance()

if __name__ == "__main__":
    print(" 测试修复版Win API余额获取")
    balance = get_balance_fixed()
    
    if balance and balance['available_cash'] > 0:
        print("\\n 修复版测试成功!")
        print(" 余额获取正常")
        print(" 已切换回买卖页面")
        print(" W/E/R键现在应该有效")
    else:
        print("\\n 需要进一步调试")
