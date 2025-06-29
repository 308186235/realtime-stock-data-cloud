#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确的交易软件控件定位测试
需要定位具体的输入框和按钮位置
"""

import time
import sys
import win32gui
import win32api
import win32con
import pyautogui
from PIL import Image
import cv2
import numpy as np

class PreciseTradingTest:
    def __init__(self):
        self.window_handle = None
        self.window_title = ""
        self.window_rect = None
        
    def find_trading_window(self):
        """查找并分析交易软件窗口"""
        print("🔍 查找交易软件窗口...")
        
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "网上股票交易系统" in title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        if not windows:
            print("❌ 未找到交易软件窗口")
            return False
        
        self.window_handle, self.window_title = windows[0]
        print(f"✅ 找到交易软件: {self.window_title}")
        
        # 恢复并激活窗口
        if win32gui.IsIconic(self.window_handle):
            print("📱 恢复最小化窗口...")
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            time.sleep(1)
        
        # 激活窗口
        win32gui.SetForegroundWindow(self.window_handle)
        time.sleep(0.5)
        
        # 获取窗口位置和大小
        self.window_rect = win32gui.GetWindowRect(self.window_handle)
        print(f"📐 窗口位置: {self.window_rect}")
        
        return True
    
    def capture_window_screenshot(self):
        """截取交易软件窗口截图"""
        print("📸 截取交易软件窗口截图...")
        
        try:
            # 确保窗口在前台
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            # 截取整个屏幕
            screenshot = pyautogui.screenshot()
            
            # 裁剪出交易软件窗口
            left, top, right, bottom = self.window_rect
            
            # 调整坐标（处理可能的负坐标）
            if left < 0 or top < 0:
                print("⚠️ 窗口坐标异常，使用全屏截图")
                window_screenshot = screenshot
            else:
                window_screenshot = screenshot.crop((left, top, right, bottom))
            
            # 保存截图
            screenshot_path = "trading_window_screenshot.png"
            window_screenshot.save(screenshot_path)
            print(f"✅ 截图已保存: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def analyze_window_structure(self):
        """分析交易软件窗口结构"""
        print("🔍 分析交易软件窗口结构...")
        
        try:
            # 枚举子窗口
            child_windows = []
            
            def enum_child_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    try:
                        class_name = win32gui.GetClassName(hwnd)
                        window_text = win32gui.GetWindowText(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'handle': hwnd,
                            'class': class_name,
                            'text': window_text,
                            'rect': rect
                        })
                    except:
                        pass
                return True
            
            win32gui.EnumChildWindows(self.window_handle, enum_child_callback, child_windows)
            
            print(f"📋 找到 {len(child_windows)} 个子窗口:")
            
            # 分析可能的输入框
            input_controls = []
            for i, window in enumerate(child_windows[:10]):  # 只显示前10个
                print(f"  {i+1}. 类名: {window['class']}")
                print(f"     文本: '{window['text']}'")
                print(f"     位置: {window['rect']}")
                
                # 识别可能的输入框
                if any(keyword in window['class'].lower() for keyword in ['edit', 'input', 'text']):
                    input_controls.append(window)
                    print(f"     🎯 可能的输入框!")
                print()
            
            if input_controls:
                print(f"✅ 找到 {len(input_controls)} 个可能的输入框")
                return input_controls
            else:
                print("⚠️ 未找到明显的输入框控件")
                return []
                
        except Exception as e:
            print(f"❌ 分析窗口结构失败: {e}")
            return []
    
    def test_click_positioning(self):
        """测试点击定位功能"""
        print("🎯 测试点击定位功能...")
        
        if not self.window_rect:
            print("❌ 窗口位置信息不可用")
            return False
        
        left, top, right, bottom = self.window_rect
        
        # 如果窗口坐标异常，使用屏幕中心
        if left < 0 or top < 0:
            print("⚠️ 窗口坐标异常，使用屏幕中心进行测试")
            screen_width, screen_height = pyautogui.size()
            test_x = screen_width // 2
            test_y = screen_height // 2
        else:
            # 计算窗口中心点
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            test_x = center_x
            test_y = center_y
        
        print(f"   测试点击位置: ({test_x}, {test_y})")
        
        response = input("   是否测试点击定位? (会在交易软件中点击) (y/n): ")
        if response.lower() != 'y':
            print("   跳过点击测试")
            return True
        
        try:
            # 确保窗口激活
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
            
            print("   执行测试点击...")
            pyautogui.click(test_x, test_y)
            time.sleep(0.5)
            
            print("   ✅ 点击定位测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 点击定位测试失败: {e}")
            return False
    
    def suggest_improvements(self):
        """建议改进方案"""
        print("💡 改进建议:")
        print()
        print("🔧 为了实现精确的交易操作，需要:")
        print("  1. 📸 图像识别 - 识别买入/卖出按钮位置")
        print("  2. 🎯 控件定位 - 精确定位股票代码、价格、数量输入框")
        print("  3. 📋 OCR文字识别 - 读取当前页面信息")
        print("  4. 🔄 状态检测 - 确认操作是否成功执行")
        print()
        print("🛠️ 可选的实现方案:")
        print("  方案1: 使用图像模板匹配定位控件")
        print("  方案2: 使用Windows UI Automation API")
        print("  方案3: 使用坐标配置文件(需要手动配置)")
        print("  方案4: 结合OCR和图像识别的智能定位")
        print()
        print("⚠️ 当前限制:")
        print("  - 需要交易软件界面保持可见")
        print("  - 不同分辨率可能需要重新配置")
        print("  - 软件界面更新可能影响定位准确性")
    
    def create_coordinate_config(self):
        """创建坐标配置向导"""
        print("📝 坐标配置向导")
        print("   这将帮助您手动配置交易界面的关键位置")
        
        response = input("   是否启动配置向导? (y/n): ")
        if response.lower() != 'y':
            return
        
        print("\n🎯 配置步骤:")
        print("1. 请在交易软件中打开买入页面")
        print("2. 将鼠标移动到股票代码输入框")
        print("3. 记录鼠标位置坐标")
        
        input("准备好后按回车继续...")
        
        # 获取当前鼠标位置
        mouse_x, mouse_y = pyautogui.position()
        print(f"当前鼠标位置: ({mouse_x}, {mouse_y})")
        
        config = {
            "window_title": self.window_title,
            "stock_code_input": {"x": mouse_x, "y": mouse_y},
            "price_input": {"x": 0, "y": 0},
            "quantity_input": {"x": 0, "y": 0},
            "buy_button": {"x": 0, "y": 0},
            "sell_button": {"x": 0, "y": 0}
        }
        
        print("💾 配置已初始化，需要完善其他控件位置")
        print("   建议使用专门的配置工具完成完整配置")
    
    def run_precise_test(self):
        """运行精确测试"""
        print("🎯 精确交易软件定位测试")
        print("=" * 50)
        
        # 1. 查找交易软件窗口
        if not self.find_trading_window():
            return False
        
        # 2. 截取窗口截图
        screenshot_path = self.capture_window_screenshot()
        
        # 3. 分析窗口结构
        input_controls = self.analyze_window_structure()
        
        # 4. 测试点击定位
        self.test_click_positioning()
        
        # 5. 建议改进方案
        self.suggest_improvements()
        
        # 6. 配置向导
        self.create_coordinate_config()
        
        print("\n" + "=" * 50)
        print("📊 精确测试完成")
        print("\n🔍 发现的问题:")
        print("  ❌ 当前系统无法精确定位交易界面控件")
        print("  ❌ 需要更精确的控件识别和定位机制")
        print("  ❌ 盲目发送按键可能导致误操作")
        
        print("\n✅ 建议的解决方案:")
        print("  1. 实现图像识别定位系统")
        print("  2. 使用UI Automation API")
        print("  3. 创建坐标配置文件")
        print("  4. 添加操作确认机制")
        
        return True

def main():
    print("🎯 精确交易软件定位测试")
    print("⚠️ 重要说明:")
    print("  - 本测试将深入分析交易软件界面结构")
    print("  - 识别当前系统的定位能力和限制")
    print("  - 提供精确控制的改进建议")
    print("  - 不会执行任何真实交易操作")
    print()
    
    try:
        tester = PreciseTradingTest()
        tester.run_precise_test()
        
        print("\n🎯 结论:")
        print("您的观察是正确的！当前系统确实存在定位不精确的问题。")
        print("需要实现更精确的控件定位机制才能安全可靠地进行自动交易。")
        
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
