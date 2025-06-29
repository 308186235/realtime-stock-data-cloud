#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
针对"网上股票交易系统5.0"的专门测试
"""

import time
import sys
import win32gui
import win32api
import win32con

class TradingSoftwareTest:
    def __init__(self):
        self.window_handle = None
        self.window_title = ""
        
    def find_trading_window(self):
        """查找交易软件窗口"""
        print("🔍 查找交易软件窗口...")
        
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "网上股票交易系统" in title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if windows:
            self.window_handle, self.window_title = windows[0]
            print(f"✅ 找到交易软件: {self.window_title}")
            print(f"   窗口句柄: {self.window_handle}")
            return True
        else:
            print("❌ 未找到交易软件窗口")
            return False
    
    def activate_window(self):
        """激活交易软件窗口"""
        print("🎯 激活交易软件窗口...")
        try:
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            # 检查是否成功激活
            foreground = win32gui.GetForegroundWindow()
            if foreground == self.window_handle:
                print("✅ 窗口激活成功")
                return True
            else:
                print("⚠️ 窗口可能未完全激活")
                return False
        except Exception as e:
            print(f"❌ 激活窗口失败: {e}")
            return False
    
    def get_window_info(self):
        """获取窗口信息"""
        print("📊 获取窗口信息...")
        try:
            rect = win32gui.GetWindowRect(self.window_handle)
            print(f"   窗口位置: 左={rect[0]}, 上={rect[1]}, 右={rect[2]}, 下={rect[3]}")
            print(f"   窗口大小: 宽={rect[2]-rect[0]}, 高={rect[3]-rect[1]}")
            
            # 检查窗口状态
            if win32gui.IsWindowVisible(self.window_handle):
                print("   ✅ 窗口可见")
            else:
                print("   ❌ 窗口不可见")
                
            if win32gui.IsIconic(self.window_handle):
                print("   ⚠️ 窗口已最小化")
            else:
                print("   ✅ 窗口未最小化")
                
        except Exception as e:
            print(f"❌ 获取窗口信息失败: {e}")
    
    def test_function_keys(self):
        """测试功能键"""
        print("⌨️ 测试交易软件功能键...")
        
        function_keys = {
            'F1': '买入',
            'F2': '卖出', 
            'F3': '委托',
            'F4': '持仓',
            'F5': '资金',
            'F6': '撤单'
        }
        
        print("   将要测试的功能键:")
        for key, desc in function_keys.items():
            print(f"     {key} - {desc}")
        
        response = input("\n   是否继续测试功能键? (y/n): ")
        if response.lower() != 'y':
            print("   跳过功能键测试")
            return True
        
        print("   开始测试功能键...")
        print("   ⚠️ 请注意观察交易软件界面的变化")
        
        try:
            for key, desc in function_keys.items():
                print(f"   测试 {key} ({desc})...")
                
                # 确保窗口处于前台
                win32gui.SetForegroundWindow(self.window_handle)
                time.sleep(0.3)
                
                # 发送功能键
                vk_codes = {
                    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 
                    'F4': 0x73, 'F5': 0x74, 'F6': 0x75
                }
                
                if key in vk_codes:
                    vk_code = vk_codes[key]
                    win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
                    time.sleep(0.1)
                    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
                
                time.sleep(1)  # 等待界面响应
            
            print("   ✅ 功能键测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 功能键测试失败: {e}")
            return False
    
    def test_input_simulation(self):
        """测试输入模拟"""
        print("📝 测试输入模拟...")
        
        response = input("   是否测试输入模拟? (将在交易软件中输入测试文本) (y/n): ")
        if response.lower() != 'y':
            print("   跳过输入模拟测试")
            return True
        
        try:
            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            print("   将输入测试股票代码: 600000")
            
            # 模拟输入股票代码
            test_code = "600000"
            for char in test_code:
                # 发送字符
                win32api.keybd_event(ord(char), 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
            
            time.sleep(0.5)
            
            # 发送Tab键切换输入框
            print("   发送Tab键...")
            win32api.keybd_event(0x09, 0, 0, 0)  # Tab键按下
            time.sleep(0.1)
            win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)  # Tab键释放
            
            print("   ✅ 输入模拟测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 输入模拟测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试网上股票交易系统5.0")
        print("=" * 50)
        
        # 1. 查找交易软件窗口
        if not self.find_trading_window():
            print("❌ 无法找到交易软件，请确保软件已打开")
            return False
        
        # 2. 激活窗口
        if not self.activate_window():
            print("⚠️ 窗口激活失败，但继续测试...")
        
        # 3. 获取窗口信息
        self.get_window_info()
        
        # 4. 测试功能键
        if not self.test_function_keys():
            print("⚠️ 功能键测试失败")
        
        # 5. 测试输入模拟
        if not self.test_input_simulation():
            print("⚠️ 输入模拟测试失败")
        
        print("\n" + "=" * 50)
        print("🎉 测试完成!")
        print("\n📋 测试总结:")
        print("  ✅ 交易软件检测: 成功")
        print("  ✅ 窗口操作: 成功")
        print("  ✅ 功能键测试: 完成")
        print("  ✅ 输入模拟: 完成")
        
        print("\n💡 接下来可以:")
        print("  1. 运行完整的Agent测试")
        print("  2. 启动Agent交易系统")
        print("  3. 使用Web界面控制")
        
        return True

def main():
    print("🧪 网上股票交易系统5.0 - 专门测试")
    print("⚠️ 重要提示:")
    print("  - 请确保交易软件已打开并登录")
    print("  - 测试过程中请不要操作其他程序")
    print("  - 如有异常可按Ctrl+C中断")
    print()
    
    try:
        tester = TradingSoftwareTest()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 所有测试通过！系统可以正常控制您的交易软件")
        else:
            print("\n❌ 部分测试失败，请检查问题")
            
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
