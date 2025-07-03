"""
交易软件导出功能 - 真正的原版逻辑
完全复制working_trader_FIXED.py中的导出函数,不做任何修改
"""

import win32api
import win32con
import time

from trader_core_original import (
    switch_to_trading_software,
    ensure_caps_lock_on,
    click_center_area,
    click_table_area,
    generate_unique_filename,
    cleanup_old_export_files,
    clear_and_type,
    send_key_fast
)

def export_holdings():
    """导出持仓数据 - 完全复制原版"""
    print("\n📊 导出持仓数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("\n开始导出持仓...")

    try:
        # 1. 按W键进入持仓页面
        print("1. 按W键进入持仓页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   发送W键...")
        print("   [调试] 重置状态确保W键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送W键...")
        # 5. 发送W键
        win32api.keybd_event(0x57, 0, 0, 0)  # W键按下 (虚拟键码)
        win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] W键发送完成")

        print("   等待持仓页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("持仓数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名
        print("4. 输入文件名...")
        clear_and_type(filename)
        time.sleep(0.1)

        # 6. 按回车保存
        print("5. 按回车保存...")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(1.0)  # 等待文件保存

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)
        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 持仓数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_transactions():
    """导出成交数据 - 完全复制原版"""
    print("\n📊 导出成交数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("开始导出成交...")

    try:
        # 1. 按E键进入成交页面
        print("1. 按E键进入成交页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 重置状态确保E键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送E键...")
        # 5. 发送E键
        win32api.keybd_event(0x45, 0, 0, 0)  # E键按下 (虚拟键码)
        win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] E键发送完成")

        print("   等待成交页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("成交数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名
        print("4. 输入文件名...")
        clear_and_type(filename)
        time.sleep(0.1)

        # 6. 按回车保存
        print("5. 按回车保存...")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(1.0)  # 等待文件保存

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)
        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 成交数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

def export_orders():
    """导出委托数据 - 完全复制原版"""
    print("\n📊 导出委托数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件,请手动点击交易软件窗口后重试")
        return False

    print("开始导出委托...")

    try:
        # 1. 按R键进入委托页面
        print("1. 按R键进入委托页面...")
        ensure_caps_lock_on()
        time.sleep(0.02)

        print("   [调试] 重置状态确保R键能工作...")

        # 1. 重新切换到交易软件
        if not switch_to_trading_software():
            print("   ❌ 无法切换到交易软件")
            return False

        # 2. 点击中央区域获取焦点
        click_center_area()

        # 3. 确保Caps Lock开启
        ensure_caps_lock_on()

        # 4. 等待状态稳定
        time.sleep(0.5)

        print("   [调试] 发送R键...")
        # 5. 发送R键
        win32api.keybd_event(0x52, 0, 0, 0)  # R键按下 (虚拟键码)
        win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)  # R键释放
        time.sleep(0.1)  # 等待0.1秒后开始导出
        print("   [调试] R键发送完成")

        print("   等待委托页面加载完成...")

        # 2. 生成文件名
        filename = generate_unique_filename("委托数据")
        print(f"文件名: {filename}")

        # 3. 点击表格区域
        print("2. 点击表格区域...")
        click_table_area()
        time.sleep(0.1)

        # 4. 按Ctrl+S导出
        print("3. 按Ctrl+S导出...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, 0, 0)  # S键按下
        time.sleep(0.01)
        win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)  # S键释放
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl释放
        time.sleep(0.5)  # 等待导出对话框

        # 5. 输入文件名
        print("4. 输入文件名...")
        clear_and_type(filename)
        time.sleep(0.1)

        # 6. 按回车保存
        print("5. 按回车保存...")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(1.0)  # 等待文件保存

        # 7. 按N关闭确认对话框
        print("6. 按N关闭确认对话框...")
        win32api.keybd_event(0x4E, 0, 0, 0)  # N键按下 (虚拟键码)
        win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)  # N键释放
        time.sleep(0.3)

        print(f"\n✅ 委托数据导出完成! 文件: {filename}")
        return True

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False
