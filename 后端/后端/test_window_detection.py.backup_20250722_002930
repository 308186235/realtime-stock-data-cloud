#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试窗口检测
检测当前运行的所有窗口，找到东吴证券软件
"""

import win32gui
import win32con

def list_all_windows():
    """列出所有可见窗口"""
    print("🔍 检测所有可见窗口:")
    print("=" * 60)
    
    windows = []
    
    def enum_windows_proc(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            if window_text:  # 只显示有标题的窗口
                windows.append((hwnd, window_text, class_name))
        return True
    
    win32gui.EnumWindows(enum_windows_proc, windows)
    
    # 按窗口标题排序
    windows.sort(key=lambda x: x[1])
    
    for i, (hwnd, title, class_name) in enumerate(windows, 1):
        print(f"{i:3d}. 句柄: {hwnd:8d} | 类名: {class_name:20s} | 标题: {title}")
    
    return windows

def find_trading_software():
    """查找交易软件窗口"""
    print("\n🎯 查找交易软件窗口:")
    print("=" * 60)
    
    windows = []
    
    def enum_windows_proc(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # 检查多种可能的窗口标题
            trading_keywords = [
                "东吴证券", "网上股票交易系统", "网上交易", 
                "股票交易", "证券交易", "交易系统",
                "Dongwu", "Securities", "Trading"
            ]
            
            for keyword in trading_keywords:
                if keyword in window_text:
                    windows.append((hwnd, window_text, class_name, keyword))
                    break
        return True
    
    win32gui.EnumWindows(enum_windows_proc, windows)
    
    if windows:
        print("✅ 找到交易软件窗口:")
        for i, (hwnd, title, class_name, keyword) in enumerate(windows, 1):
            print(f"  {i}. 句柄: {hwnd}")
            print(f"     标题: {title}")
            print(f"     类名: {class_name}")
            print(f"     匹配关键词: {keyword}")
            print()
        return True
    else:
        print("❌ 未找到交易软件窗口")
        print("可能的原因:")
        print("1. 交易软件未启动")
        print("2. 交易软件窗口标题不包含预期的关键词")
        print("3. 交易软件窗口不可见")
        return False

def test_specific_window_title():
    """测试特定窗口标题"""
    print("\n🔍 测试特定窗口标题检测:")
    print("=" * 60)
    
    # 您提供的窗口标题
    target_title = "网上股票交易系统5.0 - 东吴"
    
    def enum_windows_proc(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if target_title in window_text or window_text in target_title:
                windows.append((hwnd, window_text))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_proc, windows)
    
    if windows:
        print(f"✅ 找到目标窗口: {target_title}")
        for hwnd, title in windows:
            print(f"  句柄: {hwnd}")
            print(f"  完整标题: {title}")
        return True
    else:
        print(f"❌ 未找到目标窗口: {target_title}")
        
        # 尝试部分匹配
        print("\n🔍 尝试部分匹配:")
        partial_keywords = ["网上股票交易", "东吴", "交易系统5.0"]
        
        for keyword in partial_keywords:
            print(f"\n检查关键词: {keyword}")
            found = False
            
            def enum_partial(hwnd, windows):
                nonlocal found
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if keyword in window_text:
                        print(f"  ✅ 找到: {window_text}")
                        windows.append((hwnd, window_text))
                        found = True
                return True
            
            partial_windows = []
            win32gui.EnumWindows(enum_partial, partial_windows)
            
            if not found:
                print(f"  ❌ 未找到包含 '{keyword}' 的窗口")
        
        return False

def main():
    """主函数"""
    print("🎯 东吴证券交易软件窗口检测工具")
    print("=" * 80)
    
    # 1. 列出所有窗口
    all_windows = list_all_windows()
    
    # 2. 查找交易软件
    find_trading_software()
    
    # 3. 测试特定标题
    test_specific_window_title()
    
    print("\n📋 检测总结:")
    print(f"- 总共检测到 {len(all_windows)} 个可见窗口")
    print("- 如果未找到交易软件，请检查:")
    print("  1. 东吴证券软件是否正在运行")
    print("  2. 软件窗口是否可见（未最小化）")
    print("  3. 窗口标题是否与预期一致")

if __name__ == "__main__":
    main()
