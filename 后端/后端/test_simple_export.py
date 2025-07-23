#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单导出测试
测试单个导出功能是否能正常工作
"""

import sys
import traceback
from datetime import datetime

def test_single_export():
    """测试单个导出功能"""
    print("🚀 开始测试单个导出功能")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        from trader_export import export_holdings
        
        print("✅ 导入export_holdings成功")
        print("⚠️ 注意:这将实际操作交易软件!")
        print("⚠️ 请确保交易软件已打开并处于正常状态")
        
        # 询问用户是否继续
        response = input("\n是否继续执行持仓导出测试?(y/N): ").strip().lower()
        
        if response != 'y':
            print("❌ 用户取消测试")
            return False
        
        print("\n🔄 开始执行持仓导出...")
        print("=" * 30)
        
        # 执行持仓导出
        result = export_holdings()
        
        print("=" * 30)
        if result:
            print("✅ 持仓导出测试成功!")
            print("📁 请检查当前目录是否生成了新的持仓数据文件")
        else:
            print("❌ 持仓导出测试失败")
            print("💡 可能的原因:")
            print("   1. 交易软件未正确响应")
            print("   2. 窗口焦点问题")
            print("   3. 按键发送失败")
            print("   4. 导出对话框未正确处理")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        traceback.print_exc()
        return False

def test_balance_reader():
    """测试余额读取功能"""
    print("\n🚀 开始测试余额读取功能")
    print("=" * 50)
    
    try:
        from fixed_balance_reader import FixedBalanceReader
        
        print("✅ 导入FixedBalanceReader成功")
        print("⚠️ 注意:这将实际操作交易软件!")
        
        # 询问用户是否继续
        response = input("\n是否继续执行余额读取测试?(y/N): ").strip().lower()
        
        if response != 'y':
            print("❌ 用户取消测试")
            return False
        
        print("\n🔄 开始执行余额读取...")
        print("=" * 30)
        
        # 创建余额读取器
        balance_reader = FixedBalanceReader()
        
        # 执行余额读取
        balance_data = balance_reader.get_account_balance()
        
        print("=" * 30)
        if balance_data:
            print("✅ 余额读取测试成功!")
            print("💰 读取到的余额数据:")
            for key, value in balance_data.items():
                print(f"   {key}: {value}")
        else:
            print("❌ 余额读取测试失败")
            print("💡 可能的原因:")
            print("   1. 交易软件未正确响应")
            print("   2. 余额页面未正确导航")
            print("   3. 数据解析失败")
            print("   4. 窗口文本获取失败")
        
        return balance_data is not None
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        traceback.print_exc()
        return False

def check_recent_files():
    """检查最近生成的文件"""
    print("\n🔍 检查最近生成的文件...")
    print("=" * 50)
    
    import os
    import glob
    from datetime import datetime, timedelta
    
    # 获取当前时间
    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=5)
    
    # 查找最近5分钟内的文件
    recent_files = []
    
    for pattern in ['*.csv', '*.xls', '*.json']:
        files = glob.glob(pattern)
        for file in files:
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(file))
                if mtime > five_minutes_ago:
                    recent_files.append((file, mtime))
            except:
                continue
    
    # 按时间排序
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    if recent_files:
        print(f"📁 最近5分钟内生成的文件 ({len(recent_files)} 个):")
        for file, mtime in recent_files:
            print(f"   {mtime.strftime('%H:%M:%S')} - {file}")
    else:
        print("📁 最近5分钟内没有新文件生成")
    
    return len(recent_files) > 0

def main():
    """主测试函数"""
    print("🚀 简单导出功能测试")
    print("=" * 60)
    print("⚠️ 重要提醒:")
    print("   1. 请确保交易软件已经打开")
    print("   2. 请确保软件处于正常登录状态")
    print("   3. 测试过程中请不要操作鼠标键盘")
    print("   4. 如有问题请按Ctrl+C中断")
    print("=" * 60)
    
    # 检查测试前的文件状态
    print("📋 测试前文件检查:")
    files_before = check_recent_files()
    
    # 选择测试项目
    print("\n📋 请选择要测试的功能:")
    print("   1. 持仓导出测试")
    print("   2. 余额读取测试")
    print("   3. 两个都测试")
    print("   0. 退出")
    
    choice = input("\n请输入选择 (0-3): ").strip()
    
    export_result = False
    balance_result = False
    
    if choice == '1':
        export_result = test_single_export()
    elif choice == '2':
        balance_result = test_balance_reader()
    elif choice == '3':
        export_result = test_single_export()
        if export_result:
            balance_result = test_balance_reader()
    elif choice == '0':
        print("👋 退出测试")
        return
    else:
        print("❌ 无效选择")
        return
    
    # 检查测试后的文件状态
    print("\n📋 测试后文件检查:")
    files_after = check_recent_files()
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    if choice in ['1', '3']:
        print(f"持仓导出测试: {'✅ 成功' if export_result else '❌ 失败'}")
    
    if choice in ['2', '3']:
        print(f"余额读取测试: {'✅ 成功' if balance_result else '❌ 失败'}")
    
    print(f"文件生成情况: {'✅ 有新文件' if files_after else '❌ 无新文件'}")
    
    # 总体评估
    if (choice == '1' and export_result) or \
       (choice == '2' and balance_result) or \
       (choice == '3' and export_result and balance_result):
        print("\n🎉 测试成功!模块化功能工作正常")
    else:
        print("\n⚠️ 测试发现问题,需要进一步调试")
        print("\n💡 调试建议:")
        print("   1. 检查交易软件是否正确响应按键")
        print("   2. 检查窗口焦点是否正确")
        print("   3. 检查导出路径和权限")
        print("   4. 查看详细错误信息")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
