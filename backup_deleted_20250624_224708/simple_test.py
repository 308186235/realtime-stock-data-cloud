#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的交易软件检测测试
"""

import time
import sys

try:
    import win32gui
    print("✅ win32gui 导入成功")
except ImportError:
    print("❌ 缺少 pywin32，正在安装...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"])
    import win32gui

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
                    '华泰', '中信', '东吴', '网上股票'
                ]):
                    windows.append((hwnd, title))
            except:
                pass
        return True
    
    win32gui.EnumWindows(enum_callback, windows)
    return windows

def main():
    print("🚀 交易软件检测测试")
    print("=" * 40)
    
    # 查找交易软件窗口
    windows = find_trading_windows()
    
    if not windows:
        print("❌ 未找到交易软件窗口")
        print("请确保交易软件已打开")
        return False
    
    print(f"✅ 找到 {len(windows)} 个交易软件窗口:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"  {i}. {title} (句柄: {hwnd})")
    
    # 测试窗口激活
    if windows:
        hwnd, title = windows[0]
        print(f"\n🎯 测试激活窗口: {title}")
        try:
            win32gui.SetForegroundWindow(hwnd)
            print("✅ 窗口激活成功")
        except Exception as e:
            print(f"❌ 窗口激活失败: {e}")
    
    print("\n🎉 基础检测完成!")
    return True

if __name__ == "__main__":
    main()
