"""
交易程序导出模块
提供持仓,成交,委托数据导出功能
"""

import win32api
import win32con
import win32gui
import time
from trader_core_original import (
    switch_to_trading_software,
    clear_and_type,
    send_key_fast,
    generate_unique_filename,
    cleanup_old_export_files,
    click_center_area,
    click_table_area,
    ensure_caps_lock_on
)

def export_holdings():
    """导出持仓数据"""
    print("\n📊 导出持仓数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
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

        # 5. 输入文件名（不包含路径）
        print("4. 输入文件名...")
        print(f"   准备输入文件名: {filename}")
        clear_and_type(filename)
        time.sleep(0.5)  # 增加等待时间

        # 6. 按回车保存
        print("5. 按回车保存...")
        print(f"   保存文件: {filename}")
        send_key_fast(win32con.VK_RETURN)
        time.sleep(2.0)  # 增加等待时间确保文件保存完成

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
    """导出成交数据"""
    print("\n📊 导出成交数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
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
    """导出委托数据"""
    print("\n📊 导出委托数据")
    print("-" * 40)

    # 清理过期文件
    cleanup_old_export_files()

    # 自动切换到交易软件
    if not switch_to_trading_software():
        print("❌ 无法切换到交易软件，请手动点击交易软件窗口后重试")
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

def export_all_data():
    """
    导出所有数据(持仓,成交,委托)
    
    Returns:
        dict: 各项导出结果
    """
    print("\n🎯 导出所有数据")
    print("=" * 50)
    
    results = {
        "holdings": False,
        "transactions": False,
        "orders": False
    }
    
    # 导出持仓数据
    print("\n📊 1/3 导出持仓数据...")
    results["holdings"] = export_holdings()
    time.sleep(1.0)
    
    # 导出成交数据
    print("\n📊 2/3 导出成交数据...")
    results["transactions"] = export_transactions()
    time.sleep(1.0)
    
    # 导出委托数据
    print("\n📊 3/3 导出委托数据...")
    results["orders"] = export_orders()
    
    # 总结
    success_count = sum(results.values())
    print(f"\n✅ 导出完成! 成功: {success_count}/3")
    
    for data_type, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {data_type}")
    
    return results

def get_export_files():
    """
    获取当前目录下的导出文件列表

    Returns:
        dict: 按类型分组的文件列表
    """
    import glob

    files = {
        "holdings": glob.glob("持仓数据_*.csv"),
        "transactions": glob.glob("成交数据_*.csv"),
        "orders": glob.glob("委托数据_*.csv")
    }

    return files

def read_csv_file(file_path):
    """
    读取CSV文件内容

    Args:
        file_path (str): CSV文件路径

    Returns:
        list: CSV数据行列表，如果失败返回None
    """
    try:
        import csv
        import os

        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None

        with open(file_path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            data = list(reader)

        print(f"✅ 成功读取文件: {file_path}")
        print(f"   共 {len(data)} 行数据")

        return data

    except Exception as e:
        print(f"❌ 读取文件失败: {file_path}")
        print(f"   错误: {e}")
        return None

def get_latest_export_file(file_type="holdings"):
    """
    获取最新的导出文件

    Args:
        file_type (str): 文件类型 ("holdings", "transactions", "orders")

    Returns:
        str: 最新文件路径，如果没有文件返回None
    """
    import glob
    import os

    patterns = {
        "holdings": "持仓数据_*.csv",
        "transactions": "成交数据_*.csv",
        "orders": "委托数据_*.csv"
    }

    if file_type not in patterns:
        print(f"❌ 不支持的文件类型: {file_type}")
        return None

    # 检查多个可能的路径
    search_paths = [
        ".",  # 当前目录
        os.path.expanduser("~/Documents"),  # 用户文档目录
        os.path.expanduser("~/Desktop"),    # 用户桌面目录
    ]

    all_files = []

    for search_path in search_paths:
        if os.path.exists(search_path):
            pattern_path = os.path.join(search_path, patterns[file_type])
            files = glob.glob(pattern_path)
            all_files.extend(files)
            if files:
                print(f"✅ 在 {search_path} 找到 {len(files)} 个文件")

    if not all_files:
        print(f"❌ 没有找到 {file_type} 类型的导出文件")
        return None

    # 按修改时间排序，获取最新的
    latest_file = max(all_files, key=os.path.getmtime)
    print(f"✅ 找到最新文件: {latest_file}")

    return latest_file

# 测试函数
if __name__ == "__main__":
    print("🧪 测试导出模块")
    
    # 测试单个导出
    print("\n=== 测试持仓导出 ===")
    result = export_holdings()
    print(f"持仓导出结果: {result}")
    
    # 测试获取文件列表
    print("\n=== 获取导出文件 ===")
    files = get_export_files()
    for file_type, file_list in files.items():
        print(f"{file_type}: {len(file_list)} 个文件")
        for file in file_list[:3]:  # 只显示前3个
            print(f"  - {file}")
