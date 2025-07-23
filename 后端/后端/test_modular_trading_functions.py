#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化交易功能
测试持仓导出,委托导出,成交导出,余额获取
"""

import sys
import traceback
from datetime import datetime

def test_import_modules():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    print("=" * 50)
    
    modules_status = {}
    
    # 1. 测试trader_export模块
    try:
        from trader_export import export_holdings, export_transactions, export_orders, export_all_data
        modules_status['trader_export'] = '✅ 成功'
        print("✅ trader_export 模块导入成功")
        print("   - export_holdings (持仓导出)")
        print("   - export_transactions (成交导出)")
        print("   - export_orders (委托导出)")
        print("   - export_all_data (全部导出)")
    except Exception as e:
        modules_status['trader_export'] = f'❌ 失败: {e}'
        print(f"❌ trader_export 模块导入失败: {e}")
        traceback.print_exc()
    
    # 2. 测试fixed_balance_reader模块
    try:
        from fixed_balance_reader import FixedBalanceReader
        modules_status['fixed_balance_reader'] = '✅ 成功'
        print("✅ fixed_balance_reader 模块导入成功")
        print("   - FixedBalanceReader (余额获取)")
    except Exception as e:
        modules_status['fixed_balance_reader'] = f'❌ 失败: {e}'
        print(f"❌ fixed_balance_reader 模块导入失败: {e}")
        traceback.print_exc()
    
    # 3. 测试trader_core_original模块
    try:
        from trader_core_original import (
            switch_to_trading_software,
            clear_and_type,
            send_key_fast,
            generate_unique_filename,
            cleanup_old_export_files
        )
        modules_status['trader_core_original'] = '✅ 成功'
        print("✅ trader_core_original 模块导入成功")
        print("   - switch_to_trading_software (切换到交易软件)")
        print("   - clear_and_type (清除并输入)")
        print("   - send_key_fast (快速发送按键)")
        print("   - generate_unique_filename (生成唯一文件名)")
        print("   - cleanup_old_export_files (清理旧文件)")
    except Exception as e:
        modules_status['trader_core_original'] = f'❌ 失败: {e}'
        print(f"❌ trader_core_original 模块导入失败: {e}")
        traceback.print_exc()
    
    return modules_status

def test_function_signatures():
    """测试函数签名和基本调用"""
    print("\n🔍 测试函数签名...")
    print("=" * 50)
    
    function_status = {}
    
    try:
        from trader_export import export_holdings, export_transactions, export_orders, export_all_data
        
        # 测试函数是否可调用(不实际执行)
        print("📋 检查导出函数签名:")
        print(f"   export_holdings: {callable(export_holdings)} - {export_holdings.__doc__}")
        print(f"   export_transactions: {callable(export_transactions)} - {export_transactions.__doc__}")
        print(f"   export_orders: {callable(export_orders)} - {export_orders.__doc__}")
        print(f"   export_all_data: {callable(export_all_data)} - {export_all_data.__doc__}")
        
        function_status['export_functions'] = '✅ 函数签名正常'
        
    except Exception as e:
        function_status['export_functions'] = f'❌ 函数签名检查失败: {e}'
        print(f"❌ 导出函数签名检查失败: {e}")
    
    try:
        from fixed_balance_reader import FixedBalanceReader
        
        # 测试类实例化
        balance_reader = FixedBalanceReader()
        print("📋 检查余额读取器:")
        print(f"   FixedBalanceReader 实例化: ✅")
        print(f"   可用方法: {[method for method in dir(balance_reader) if not method.startswith('_')]}")
        
        function_status['balance_reader'] = '✅ 类实例化正常'
        
    except Exception as e:
        function_status['balance_reader'] = f'❌ 余额读取器检查失败: {e}'
        print(f"❌ 余额读取器检查失败: {e}")
    
    return function_status

def test_dependencies():
    """测试依赖项"""
    print("\n🔍 测试依赖项...")
    print("=" * 50)
    
    dependencies_status = {}
    
    # 测试Windows API依赖
    try:
        import win32api
        import win32con
        import win32gui
        dependencies_status['win32api'] = '✅ 可用'
        print("✅ Windows API 模块可用")
        print(f"   - win32api: {win32api.__file__}")
        print(f"   - win32gui: {win32gui.__file__}")
    except Exception as e:
        dependencies_status['win32api'] = f'❌ 不可用: {e}'
        print(f"❌ Windows API 模块不可用: {e}")
    
    # 测试其他依赖
    try:
        import time
        import re
        import os
        from datetime import datetime
        dependencies_status['standard_libs'] = '✅ 可用'
        print("✅ 标准库模块可用")
    except Exception as e:
        dependencies_status['standard_libs'] = f'❌ 不可用: {e}'
        print(f"❌ 标准库模块不可用: {e}")
    
    return dependencies_status

def analyze_potential_issues():
    """分析潜在问题"""
    print("\n🔍 分析潜在问题...")
    print("=" * 50)
    
    issues = []
    
    # 检查文件是否存在
    import os
    required_files = [
        'trader_export.py',
        'fixed_balance_reader.py', 
        'trader_core_original.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            issues.append(f"❌ 缺少文件: {file}")
        else:
            print(f"✅ 文件存在: {file}")
    
    # 检查可能的循环导入
    try:
        import trader_export
        import fixed_balance_reader
        import trader_core_original
        print("✅ 无明显循环导入问题")
    except Exception as e:
        issues.append(f"❌ 可能存在循环导入: {e}")
    
    # 检查Windows环境
    import platform
    if platform.system() != 'Windows':
        issues.append("❌ 非Windows环境,Win32 API不可用")
    else:
        print("✅ Windows环境检查通过")
    
    return issues

def main():
    """主测试函数"""
    print("🚀 开始测试模块化交易功能")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 测试模块导入
    modules_status = test_import_modules()
    
    # 2. 测试函数签名
    function_status = test_function_signatures()
    
    # 3. 测试依赖项
    dependencies_status = test_dependencies()
    
    # 4. 分析潜在问题
    issues = analyze_potential_issues()
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📋 测试报告总结")
    print("=" * 60)
    
    print("\n🔧 模块导入状态:")
    for module, status in modules_status.items():
        print(f"   {module}: {status}")
    
    print("\n🔧 函数检查状态:")
    for func, status in function_status.items():
        print(f"   {func}: {status}")
    
    print("\n🔧 依赖项状态:")
    for dep, status in dependencies_status.items():
        print(f"   {dep}: {status}")
    
    if issues:
        print("\n⚠️ 发现的问题:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ 未发现明显问题")
    
    # 总体评估
    all_modules_ok = all('✅' in status for status in modules_status.values())
    all_functions_ok = all('✅' in status for status in function_status.values())
    all_deps_ok = all('✅' in status for status in dependencies_status.values())
    no_issues = len(issues) == 0
    
    print("\n" + "=" * 60)
    if all_modules_ok and all_functions_ok and all_deps_ok and no_issues:
        print("🎉 所有模块化功能测试通过!")
        print("✅ 持仓导出,委托导出,成交导出,余额获取功能应该可以正常使用")
    else:
        print("⚠️ 发现一些问题需要解决:")
        if not all_modules_ok:
            print("   - 模块导入存在问题")
        if not all_functions_ok:
            print("   - 函数检查存在问题")
        if not all_deps_ok:
            print("   - 依赖项存在问题")
        if not no_issues:
            print("   - 发现其他潜在问题")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
