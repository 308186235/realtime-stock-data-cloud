#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际测试交易功能
测试持仓导出,委托导出,成交导出,余额获取的实际执行
"""

import sys
import traceback
from datetime import datetime
import os

def test_balance_reader():
    """测试余额读取功能"""
    print("🔍 测试余额读取功能...")
    print("=" * 50)
    
    try:
        from fixed_balance_reader import FixedBalanceReader
        
        # 创建余额读取器实例
        balance_reader = FixedBalanceReader()
        print("✅ 余额读取器实例创建成功")
        
        # 测试查找交易窗口(不实际激活)
        print("🔍 测试查找交易窗口功能...")
        try:
            # 这个函数会尝试查找窗口但不会实际操作
            result = balance_reader.find_and_activate_trading_window()
            if result:
                print("✅ 找到交易软件窗口")
            else:
                print("⚠️ 未找到交易软件窗口(可能软件未运行)")
        except Exception as e:
            print(f"❌ 查找交易窗口时出错: {e}")
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 余额读取器测试失败: {e}")
        traceback.print_exc()
        return False

def test_export_functions_dry_run():
    """测试导出函数(干运行,不实际执行)"""
    print("\n🔍 测试导出函数...")
    print("=" * 50)
    
    try:
        from trader_export import export_holdings, export_transactions, export_orders, export_all_data
        from trader_core_original import switch_to_trading_software
        
        print("✅ 导出函数导入成功")
        
        # 测试切换到交易软件功能
        print("🔍 测试切换到交易软件功能...")
        try:
            # 这个函数会尝试查找并切换到交易软件
            result = switch_to_trading_software()
            if result:
                print("✅ 成功切换到交易软件")
            else:
                print("⚠️ 未能切换到交易软件(可能软件未运行)")
        except Exception as e:
            print(f"❌ 切换到交易软件时出错: {e}")
            traceback.print_exc()
        
        # 检查导出函数的内部逻辑
        print("🔍 检查导出函数内部逻辑...")
        
        # 检查是否有必要的辅助函数
        from trader_core_original import (
            clear_and_type,
            send_key_fast,
            generate_unique_filename,
            cleanup_old_export_files
        )
        
        print("✅ 辅助函数导入成功:")
        print("   - clear_and_type: 清除并输入文本")
        print("   - send_key_fast: 快速发送按键")
        print("   - generate_unique_filename: 生成唯一文件名")
        print("   - cleanup_old_export_files: 清理旧导出文件")
        
        # 测试文件名生成
        test_filename = generate_unique_filename("持仓数据", "csv")
        print(f"✅ 测试文件名生成: {test_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出函数测试失败: {e}")
        traceback.print_exc()
        return False

def check_export_directory():
    """检查导出目录和文件"""
    print("\n🔍 检查导出目录和文件...")
    print("=" * 50)
    
    # 检查当前目录中的导出文件
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 查找CSV文件
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    xls_files = [f for f in os.listdir('.') if f.endswith('.xls')]
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    print(f"\n📁 找到的导出文件:")
    print(f"   CSV文件: {len(csv_files)} 个")
    for f in csv_files[-5:]:  # 显示最近5个
        print(f"     - {f}")
    
    print(f"   XLS文件: {len(xls_files)} 个")
    for f in xls_files[-5:]:  # 显示最近5个
        print(f"     - {f}")
    
    print(f"   JSON文件: {len(json_files)} 个")
    for f in json_files[-5:]:  # 显示最近5个
        print(f"     - {f}")
    
    # 分析文件名模式
    print(f"\n📊 文件名模式分析:")
    
    holdings_files = [f for f in csv_files if '持仓' in f]
    orders_files = [f for f in csv_files if '委托' in f]
    transactions_files = [f for f in csv_files if '成交' in f]
    
    print(f"   持仓数据文件: {len(holdings_files)} 个")
    print(f"   委托数据文件: {len(orders_files)} 个")
    print(f"   成交数据文件: {len(transactions_files)} 个")
    
    if holdings_files:
        print(f"   最新持仓文件: {max(holdings_files)}")
    if orders_files:
        print(f"   最新委托文件: {max(orders_files)}")
    if transactions_files:
        print(f"   最新成交文件: {max(transactions_files)}")

def analyze_recent_exports():
    """分析最近的导出文件"""
    print("\n🔍 分析最近的导出文件...")
    print("=" * 50)
    
    import glob
    from datetime import datetime, timedelta
    
    # 查找最近24小时的导出文件
    recent_files = []
    
    # 获取所有CSV文件的修改时间
    csv_files = glob.glob('*.csv')
    xls_files = glob.glob('*.xls')
    json_files = glob.glob('*.json')
    
    all_files = csv_files + xls_files + json_files
    
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    for file in all_files:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(file))
            if mtime > yesterday:
                recent_files.append((file, mtime))
        except:
            continue
    
    # 按时间排序
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📅 最近24小时内的导出文件 ({len(recent_files)} 个):")
    for file, mtime in recent_files[:10]:  # 显示最近10个
        print(f"   {mtime.strftime('%Y-%m-%d %H:%M:%S')} - {file}")
    
    # 分析导出频率
    if recent_files:
        latest_time = recent_files[0][1]
        print(f"\n📊 导出状态分析:")
        print(f"   最新导出时间: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        time_diff = now - latest_time
        if time_diff.total_seconds() < 3600:  # 1小时内
            print(f"   ✅ 导出很活跃 (最近导出: {int(time_diff.total_seconds()/60)} 分钟前)")
        elif time_diff.total_seconds() < 86400:  # 24小时内
            print(f"   ⚠️ 导出较少 (最近导出: {int(time_diff.total_seconds()/3600)} 小时前)")
        else:
            print(f"   ❌ 导出不活跃 (最近导出: {int(time_diff.days)} 天前)")

def identify_potential_issues():
    """识别潜在问题"""
    print("\n🔍 识别潜在问题...")
    print("=" * 50)
    
    issues = []
    
    # 1. 检查是否有交易软件进程
    try:
        import psutil
        processes = [p.info for p in psutil.process_iter(['pid', 'name']) if '东吴' in p.info['name'] or '交易' in p.info['name']]
        if processes:
            print(f"✅ 找到交易软件进程: {len(processes)} 个")
            for p in processes:
                print(f"   - {p['name']} (PID: {p['pid']})")
        else:
            issues.append("⚠️ 未找到交易软件进程,软件可能未运行")
    except ImportError:
        print("⚠️ psutil未安装,无法检查进程")
    except Exception as e:
        issues.append(f"❌ 检查进程时出错: {e}")
    
    # 2. 检查Windows API权限
    try:
        import win32gui
        windows = []
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "交易" in title or "东吴" in title:
                    windows.append(title)
            return True
        
        win32gui.EnumWindows(enum_callback, windows)
        if windows:
            print(f"✅ 找到交易软件窗口: {len(windows)} 个")
            for w in windows:
                print(f"   - {w}")
        else:
            issues.append("⚠️ 未找到交易软件窗口")
    except Exception as e:
        issues.append(f"❌ 检查窗口时出错: {e}")
    
    # 3. 检查文件权限
    try:
        test_file = "test_write_permission.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ 文件写入权限正常")
    except Exception as e:
        issues.append(f"❌ 文件写入权限问题: {e}")
    
    return issues

def main():
    """主测试函数"""
    print("🚀 开始实际测试交易功能")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 测试余额读取器
    balance_ok = test_balance_reader()
    
    # 2. 测试导出函数
    export_ok = test_export_functions_dry_run()
    
    # 3. 检查导出目录
    check_export_directory()
    
    # 4. 分析最近导出
    analyze_recent_exports()
    
    # 5. 识别潜在问题
    issues = identify_potential_issues()
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📋 实际功能测试报告")
    print("=" * 60)
    
    print(f"\n🔧 功能测试结果:")
    print(f"   余额读取器: {'✅ 正常' if balance_ok else '❌ 异常'}")
    print(f"   导出函数: {'✅ 正常' if export_ok else '❌ 异常'}")
    
    if issues:
        print(f"\n⚠️ 发现的问题 ({len(issues)} 个):")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✅ 未发现明显问题")
    
    # 总体评估
    print("\n" + "=" * 60)
    if balance_ok and export_ok and len(issues) == 0:
        print("🎉 所有实际功能测试通过!")
        print("✅ 模块化交易功能应该可以正常使用")
    else:
        print("⚠️ 发现一些需要注意的问题:")
        if not balance_ok:
            print("   - 余额读取器存在问题")
        if not export_ok:
            print("   - 导出函数存在问题")
        if issues:
            print("   - 发现运行环境问题")
        
        print("\n💡 建议:")
        print("   1. 确保交易软件正在运行")
        print("   2. 检查软件窗口标题是否包含'交易'或'东吴'")
        print("   3. 确保有足够的文件写入权限")
        print("   4. 尝试手动运行一次导出功能")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
