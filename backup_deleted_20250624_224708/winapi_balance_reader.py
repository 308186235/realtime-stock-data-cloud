"""
Win API账户余额获取器 - 基于现有代码增强
"""

import win32gui
import win32api
import win32con
import win32clipboard
import time
import re
from datetime import datetime

class WinAPIBalanceReader:
    def __init__(self):
        self.window_handle = None
        self.window_title = ""
        
    def find_and_activate_trading_window(self):
        """查找并激活交易软件窗口"""
        print(" 查找交易软件窗口...")
        
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "网上股票交易系统" in title or "股票交易" in title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if not windows:
            print(" 未找到交易软件窗口！")
            return False
        
        self.window_handle, self.window_title = windows[0]
        print(f" 找到交易软件: {self.window_title}")
        
        try:
            # 激活窗口
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(1)
            
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            print(" 交易软件已激活")
            return True
            
        except Exception as e:
            print(f" 激活窗口失败: {e}")
            return False
    
    def send_key(self, vk_code):
        """发送按键"""
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    
    def navigate_to_funds_page(self):
        """导航到资金页面"""
        print(" 导航到资金页面...")
        
        # 按F4进入资金界面
        print("   按F4进入资金界面...")
        self.send_key(0x73)  # F4键
        time.sleep(2)  # 等待页面加载
        
        # 验证是否成功切换
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd == self.window_handle:
            print(" 成功切换到资金页面")
            return True
        else:
            print(" 页面切换可能不完全，但继续尝试...")
            return True
    
    def get_window_text_content(self):
        """获取窗口文本内容"""
        try:
            # 方法1: 尝试获取窗口文本
            window_text = win32gui.GetWindowText(self.window_handle)
            print(f"窗口标题文本: {window_text}")
            
            # 方法2: 枚举子窗口获取文本
            child_texts = []
            
            def enum_child_proc(hwnd, param):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        text = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)
                        if text and len(text.strip()) > 0:
                            child_texts.append({
                                'text': text,
                                'class': class_name,
                                'hwnd': hwnd
                            })
                except:
                    pass
                return True
            
            win32gui.EnumChildWindows(self.window_handle, enum_child_proc, None)
            
            print(f"找到 {len(child_texts)} 个包含文本的子窗口:")
            for i, item in enumerate(child_texts[:10]):  # 只显示前10个
                print(f"   {i+1}. [{item['class']}] {item['text']}")
            
            return child_texts
            
        except Exception as e:
            print(f" 获取窗口文本失败: {e}")
            return []
    
    def extract_balance_from_text(self, text_items):
        """从文本中提取余额信息"""
        balance_info = {
            'available_cash': 0.0,
            'total_assets': 0.0,
            'market_value': 0.0,
            'frozen_amount': 0.0
        }
        
        # 定义余额相关的关键词和正则表达式
        patterns = {
            'available_cash': [
                r'可用资金[：:]\s*([0-9,]+\.?[0-9]*)',
                r'可用[：:]\s*([0-9,]+\.?[0-9]*)',
                r'资金余额[：:]\s*([0-9,]+\.?[0-9]*)'
            ],
            'total_assets': [
                r'总资产[：:]\s*([0-9,]+\.?[0-9]*)',
                r'资产总值[：:]\s*([0-9,]+\.?[0-9]*)'
            ],
            'market_value': [
                r'市值[：:]\s*([0-9,]+\.?[0-9]*)',
                r'持仓市值[：:]\s*([0-9,]+\.?[0-9]*)'
            ],
            'frozen_amount': [
                r'冻结[：:]\s*([0-9,]+\.?[0-9]*)',
                r'冻结资金[：:]\s*([0-9,]+\.?[0-9]*)'
            ]
        }
        
        print(" 分析文本内容提取余额信息...")
        
        for item in text_items:
            text = item['text']
            
            # 检查每种类型的余额信息
            for balance_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            # 提取数字，去除逗号
                            amount_str = match.group(1).replace(',', '')
                            amount = float(amount_str)
                            balance_info[balance_type] = amount
                            print(f"    找到{balance_type}: {amount:,.2f} (来源: {text})")
                        except ValueError:
                            continue
        
        return balance_info
    
    def try_copy_screen_content(self):
        """尝试复制屏幕内容"""
        try:
            print(" 尝试复制屏幕内容...")
            
            # 全选 (Ctrl+A)
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)
            
            # 复制 (Ctrl+C)
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('C'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)
            
            # 获取剪贴板内容
            win32clipboard.OpenClipboard()
            try:
                clipboard_data = win32clipboard.GetClipboardData()
                print(f" 剪贴板内容长度: {len(clipboard_data)} 字符")
                return clipboard_data
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            print(f" 复制屏幕内容失败: {e}")
            return ""
    
    def get_account_balance(self):
        """获取账户余额 - 主函数"""
        print(" 开始获取账户余额")
        print("=" * 50)
        
        # 1. 查找并激活交易软件
        if not self.find_and_activate_trading_window():
            return None
        
        # 2. 导航到资金页面
        if not self.navigate_to_funds_page():
            return None
        
        # 3. 获取窗口文本内容
        text_items = self.get_window_text_content()
        
        # 4. 从文本中提取余额信息
        balance_info = self.extract_balance_from_text(text_items)
        
        # 5. 如果文本提取失败，尝试复制屏幕内容
        if all(v == 0.0 for v in balance_info.values()):
            print(" 从窗口文本未提取到余额信息，尝试复制屏幕内容...")
            clipboard_content = self.try_copy_screen_content()
            if clipboard_content:
                # 将剪贴板内容作为文本项处理
                clipboard_items = [{'text': clipboard_content, 'class': 'clipboard', 'hwnd': 0}]
                balance_info = self.extract_balance_from_text(clipboard_items)
        
        # 6. 添加获取时间
        balance_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        balance_info['data_source'] = 'Win API'
        
        # 7. 显示结果
        self.display_balance_result(balance_info)
        
        return balance_info
    
    def display_balance_result(self, balance_info):
        """显示余额结果"""
        print("\\n 账户余额信息:")
        print("-" * 40)
        print(f"可用资金: {balance_info['available_cash']:,.2f}")
        print(f"总资产: {balance_info['total_assets']:,.2f}")
        print(f"持仓市值: {balance_info['market_value']:,.2f}")
        print(f"冻结资金: {balance_info['frozen_amount']:,.2f}")
        print(f"更新时间: {balance_info['update_time']}")
        print(f"数据来源: {balance_info['data_source']}")

# 全局实例
balance_reader = WinAPIBalanceReader()

def get_account_balance_via_winapi():
    """获取账户余额的便捷接口"""
    return balance_reader.get_account_balance()

# 测试函数
if __name__ == "__main__":
    print(" 测试Win API账户余额获取")
    
    # 获取账户余额
    balance = get_account_balance_via_winapi()
    
    if balance:
        print("\\n 账户余额获取成功!")
        print(f"可用资金: {balance['available_cash']:,.2f}")
    else:
        print("\\n 账户余额获取失败")
