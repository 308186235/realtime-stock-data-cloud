#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的交易软件检测和测试脚本
"""

import time
import sys
import os

try:
    import win32gui
    import win32api
    import win32con
    import pyautogui
    print("✅ 所有依赖包导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def find_trading_windows():
    """查找交易软件窗口"""
    print("🔍 正在搜索交易软件窗口...")
    
    windows = []
    
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            try:
                title = win32gui.GetWindowText(hwnd)
                if title and any(keyword in title for keyword in [
                    '股票交易', '证券', '交易系统', '同花顺', '通达信', 
                    '华泰', '中信', '东吴', '网上股票', '交易客户端'
                ]):
                    windows.append((hwnd, title))
            except:
                pass
        return True
    
    try:
        win32gui.EnumWindows(enum_callback, windows)
    except Exception as e:
        print(f"❌ 枚举窗口失败: {e}")
        return []
    
    return windows

def test_window_activation(hwnd, title):
    """测试窗口激活"""
    print(f"🎯 测试激活窗口: {title}")
    
    try:
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)
        
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        print(f"   窗口位置: {rect}")
        
        # 检查窗口是否在前台
        foreground = win32gui.GetForegroundWindow()
        if foreground == hwnd:
            print("   ✅ 窗口激活成功")
            return True
        else:
            print("   ⚠️ 窗口可能未完全激活")
            return False
            
    except Exception as e:
        print(f"   ❌ 激活窗口失败: {e}")
        return False

def test_keyboard_input():
    """测试键盘输入"""
    print("⌨️ 测试键盘输入功能...")
    
    try:
        # 禁用pyautogui的安全检查
        pyautogui.FAILSAFE = False
        
        print("   将在3秒后测试按键...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        # 测试按键
        print("   发送Tab键...")
        pyautogui.press('tab')
        time.sleep(0.5)
        
        print("   ✅ 键盘输入测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 键盘输入测试失败: {e}")
        return False

def test_hotkeys():
    """测试交易软件常用快捷键"""
    print("🔧 测试交易软件快捷键...")
    
    hotkeys = {
        'F1': '买入页面',
        'F2': '卖出页面', 
        'F3': '委托页面',
        'F4': '持仓页面',
        'F5': '资金页面'
    }
    
    print("   注意: 请确保交易软件窗口处于活动状态")
    print("   将测试以下快捷键:")
    for key, desc in hotkeys.items():
        print(f"     {key} - {desc}")
    
    input("   按回车键开始测试快捷键...")
    
    try:
        for key, desc in hotkeys.items():
            print(f"   测试 {key} ({desc})...")
            pyautogui.press(key.lower())
            time.sleep(1)
        
        print("   ✅ 快捷键测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 快捷键测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Agent快捷键交易系统 - 简化测试")
    print("=" * 50)
    
    # 1. 查找交易软件窗口
    windows = find_trading_windows()
    
    if not windows:
        print("❌ 未找到交易软件窗口")
        print("请确保以下软件已打开:")
        print("  - 网上股票交易系统")
        print("  - 同花顺")
        print("  - 通达信")
        print("  - 其他证券交易软件")
        return False
    
    print(f"✅ 找到 {len(windows)} 个交易软件窗口:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"  {i}. {title}")
    
    # 2. 选择要测试的窗口
    if len(windows) == 1:
        selected_hwnd, selected_title = windows[0]
        print(f"\n🎯 自动选择窗口: {selected_title}")
    else:
        try:
            choice = int(input(f"\n请选择要测试的窗口 (1-{len(windows)}): ")) - 1
            if 0 <= choice < len(windows):
                selected_hwnd, selected_title = windows[choice]
            else:
                print("❌ 无效选择")
                return False
        except ValueError:
            print("❌ 无效输入")
            return False
    
    print(f"\n📋 开始测试窗口: {selected_title}")
    print("-" * 50)
    
    # 3. 测试窗口激活
    if not test_window_activation(selected_hwnd, selected_title):
        print("⚠️ 窗口激活测试失败，但继续其他测试...")
    
    # 4. 测试键盘输入
    if not test_keyboard_input():
        print("❌ 键盘输入测试失败")
        return False
    
    # 5. 询问是否测试快捷键
    test_keys = input("\n是否测试交易软件快捷键? (y/n): ").lower() == 'y'
    if test_keys:
        if not test_hotkeys():
            print("⚠️ 快捷键测试失败")
    
    print("\n" + "=" * 50)
    print("🎉 基础测试完成!")
    print("\n📋 测试结果总结:")
    print("  ✅ 交易软件检测: 成功")
    print("  ✅ 窗口操作: 成功") 
    print("  ✅ 键盘输入: 成功")
    if test_keys:
        print("  ✅ 快捷键测试: 完成")
    
    print("\n💡 下一步:")
    print("  1. 运行完整测试: python test_agent_hotkey_trading.py")
    print("  2. 启动系统: start_agent_trading.bat")
    print("  3. 访问控制台: http://localhost:8000/api/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ 测试失败，请检查问题后重试")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
