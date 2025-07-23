#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化配置测试 - 测试北交所开关功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_agent_simple import SupabaseAgentSystem, TRADING_CONFIG

def test_beijing_exchange_toggle():
    """测试北交所开关功能"""
    print("🧪 测试北交所开关功能")
    print("="*50)
    
    # 创建系统实例
    system = SupabaseAgentSystem()
    
    # 显示当前配置
    print(f"当前北交所权限: {'✅ 开启' if TRADING_CONFIG['enable_beijing_exchange'] else '❌ 关闭'}")
    
    # 测试数据清洗 - 北交所股票
    test_stocks = [
        {
            'symbol': 'BJ430001',  # 北交所股票
            'name': '测试北交所股票',
            'price': 10.5,
            'volume': 1000000,
            'amount': 10500000,
            'change_percent': 5.2
        },
        {
            'symbol': 'SZ000001',  # 深交所股票
            'name': '平安银行',
            'price': 12.8,
            'volume': 2000000,
            'amount': 25600000,
            'change_percent': 3.5
        }
    ]
    
    print("\n🔍 测试数据清洗(北交所关闭状态):")
    for stock in test_stocks:
        is_valid, reason = system._clean_stock_data(stock)
        status = "✅ 通过" if is_valid else f"❌ 过滤: {reason}"
        print(f"  {stock['symbol']} ({stock['name']}): {status}")
    
    # 切换北交所权限
    print(f"\n🔧 切换北交所权限...")
    TRADING_CONFIG['enable_beijing_exchange'] = True
    print(f"北交所权限已开启: {'✅ 开启' if TRADING_CONFIG['enable_beijing_exchange'] else '❌ 关闭'}")
    
    print("\n🔍 测试数据清洗(北交所开启状态):")
    for stock in test_stocks:
        is_valid, reason = system._clean_stock_data(stock)
        status = "✅ 通过" if is_valid else f"❌ 过滤: {reason}"
        print(f"  {stock['symbol']} ({stock['name']}): {status}")
    
    # 恢复原状态
    TRADING_CONFIG['enable_beijing_exchange'] = False
    print(f"\n🔄 恢复原状态: {'✅ 开启' if TRADING_CONFIG['enable_beijing_exchange'] else '❌ 关闭'}")

def test_trading_time():
    """测试交易时间检查"""
    print("\n⏰ 测试交易时间检查")
    print("="*50)
    
    system = SupabaseAgentSystem()
    is_trading = system.is_trading_time()
    
    from datetime import datetime
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"交易时间: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
    print(f"是否为交易时间: {'✅ 是' if is_trading else '❌ 否'}")

def main():
    """主测试函数"""
    print("🚀 AI股票交易系统 - 配置功能测试")
    print("="*60)
    
    # 测试北交所开关
    test_beijing_exchange_toggle()
    
    # 测试交易时间
    test_trading_time()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成!")
    print("\n📋 功能说明:")
    print("1. ❌ 北交所关闭时:BJ开头的股票会被过滤")
    print("2. ✅ 北交所开启时:BJ开头的股票可以通过数据清洗")
    print("3. ⏰ 交易时间检查:只在工作日09:10-15:00运行")
    print("4. 🔧 配置可以动态切换,无需重启系统")

if __name__ == "__main__":
    main()
