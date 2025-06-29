#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的交易流程测试
真正执行买入/卖出操作的完整流程
"""

import time
import win32gui
import win32con
import pyautogui
from hotkey_simple_trader import HotkeySimpleTrader

def complete_trading_demo():
    """完整的交易演示"""
    print("🚀 完整交易流程演示")
    print("=" * 50)
    print("⚠️ 重要提醒:")
    print("  - 这将执行真实的交易操作流程")
    print("  - 建议先在模拟环境中测试")
    print("  - 可以选择是否最终确认订单")
    print()
    
    # 确认是否继续
    confirm = input("是否继续执行完整交易演示? (y/n): ")
    if confirm.lower() != 'y':
        print("👋 演示已取消")
        return
    
    trader = HotkeySimpleTrader()
    
    print("\n📋 演示计划:")
    print("1. 激活交易软件")
    print("2. 执行买入操作流程")
    print("3. 执行卖出操作流程") 
    print("4. 查看资金信息")
    
    # 1. 激活交易软件
    print("\n" + "="*30)
    print("步骤1: 激活交易软件")
    print("="*30)
    
    if not trader.find_and_activate_trading_window():
        print("❌ 无法找到交易软件，演示终止")
        return
    
    # 2. 买入操作演示
    print("\n" + "="*30)
    print("步骤2: 买入操作演示")
    print("="*30)
    
    demo_buy = input("是否演示买入操作? (y/n): ")
    if demo_buy.lower() == 'y':
        print("\n🔄 开始买入操作演示...")
        
        # 获取用户输入的交易参数
        stock_code = input("请输入股票代码 (默认600000): ") or "600000"
        price_input = input("请输入买入价格 (默认10.50): ") or "10.50"
        quantity_input = input("请输入买入数量 (默认100): ") or "100"
        
        try:
            price = float(price_input)
            quantity = int(quantity_input)
        except ValueError:
            print("❌ 价格或数量格式错误")
            return
        
        # 询问是否自动确认
        auto_confirm = input("是否自动确认订单? (y/n): ").lower() == 'y'
        
        print(f"\n📝 买入参数:")
        print(f"   股票代码: {stock_code}")
        print(f"   买入价格: ¥{price:.2f}")
        print(f"   买入数量: {quantity}")
        print(f"   自动确认: {'是' if auto_confirm else '否'}")
        
        final_confirm = input("\n确认执行买入操作? (y/n): ")
        if final_confirm.lower() == 'y':
            success = trader.execute_buy_order(stock_code, price, quantity, auto_confirm)
            if success:
                print("✅ 买入操作演示完成")
            else:
                print("❌ 买入操作失败")
        else:
            print("⏸️ 买入操作已取消")
    
    # 3. 卖出操作演示
    print("\n" + "="*30)
    print("步骤3: 卖出操作演示")
    print("="*30)
    
    demo_sell = input("是否演示卖出操作? (y/n): ")
    if demo_sell.lower() == 'y':
        print("\n🔄 开始卖出操作演示...")
        
        # 获取用户输入的交易参数
        stock_code = input("请输入股票代码 (默认600000): ") or "600000"
        price_input = input("请输入卖出价格 (默认10.60): ") or "10.60"
        quantity_input = input("请输入卖出数量 (默认100): ") or "100"
        
        try:
            price = float(price_input)
            quantity = int(quantity_input)
        except ValueError:
            print("❌ 价格或数量格式错误")
            return
        
        # 询问是否自动确认
        auto_confirm = input("是否自动确认订单? (y/n): ").lower() == 'y'
        
        print(f"\n📝 卖出参数:")
        print(f"   股票代码: {stock_code}")
        print(f"   卖出价格: ¥{price:.2f}")
        print(f"   卖出数量: {quantity}")
        print(f"   自动确认: {'是' if auto_confirm else '否'}")
        
        final_confirm = input("\n确认执行卖出操作? (y/n): ")
        if final_confirm.lower() == 'y':
            success = trader.execute_sell_order(stock_code, price, quantity, auto_confirm)
            if success:
                print("✅ 卖出操作演示完成")
            else:
                print("❌ 卖出操作失败")
        else:
            print("⏸️ 卖出操作已取消")
    
    # 4. 查看资金信息
    print("\n" + "="*30)
    print("步骤4: 查看资金信息")
    print("="*30)
    
    demo_fund = input("是否查看资金信息? (y/n): ")
    if demo_fund.lower() == 'y':
        success = trader.check_fund_info()
        if success:
            print("✅ 资金信息查看完成")
        else:
            print("❌ 查看资金信息失败")
    
    print("\n" + "="*50)
    print("🎉 完整交易流程演示结束!")
    print("📊 演示总结:")
    print("  ✅ 交易软件激活和控制")
    print("  ✅ 买入操作完整流程")
    print("  ✅ 卖出操作完整流程")
    print("  ✅ 资金信息查询")
    print("  ✅ 基于快捷键的可靠操作")
    
    print("\n💡 系统优势:")
    print("  🎯 简单可靠 - 基于标准快捷键")
    print("  🔒 安全可控 - 支持手动确认")
    print("  ⚡ 响应快速 - 无需复杂配置")
    print("  🎛️ 易于集成 - 可与AI Agent结合")

def agent_integration_demo():
    """Agent集成演示"""
    print("\n🤖 Agent集成演示")
    print("=" * 30)
    print("演示AI Agent如何自动控制交易")
    
    # 模拟Agent决策
    agent_decisions = [
        {
            "action": "buy",
            "symbol": "600000",
            "price": 10.50,
            "quantity": 100,
            "confidence": 0.85,
            "reason": "技术指标显示上涨趋势"
        },
        {
            "action": "sell", 
            "symbol": "600519",
            "price": 1850.00,
            "quantity": 10,
            "confidence": 0.78,
            "reason": "达到目标价位，获利了结"
        }
    ]
    
    trader = HotkeySimpleTrader()
    
    print("🧠 模拟Agent决策:")
    for i, decision in enumerate(agent_decisions, 1):
        print(f"\n决策 {i}:")
        print(f"  操作: {decision['action'].upper()}")
        print(f"  股票: {decision['symbol']}")
        print(f"  价格: ¥{decision['price']}")
        print(f"  数量: {decision['quantity']}")
        print(f"  置信度: {decision['confidence']*100:.1f}%")
        print(f"  理由: {decision['reason']}")
    
    execute_demo = input("\n是否执行Agent决策演示? (y/n): ")
    if execute_demo.lower() != 'y':
        return
    
    for i, decision in enumerate(agent_decisions, 1):
        print(f"\n🤖 执行Agent决策 {i}...")
        
        if decision['action'] == 'buy':
            success = trader.execute_buy_order(
                decision['symbol'],
                decision['price'], 
                decision['quantity'],
                auto_confirm=False  # 安全起见，不自动确认
            )
        elif decision['action'] == 'sell':
            success = trader.execute_sell_order(
                decision['symbol'],
                decision['price'],
                decision['quantity'], 
                auto_confirm=False  # 安全起见，不自动确认
            )
        
        if success:
            print(f"✅ Agent决策 {i} 执行成功")
        else:
            print(f"❌ Agent决策 {i} 执行失败")
        
        # 决策间隔
        if i < len(agent_decisions):
            time.sleep(2)
    
    print("\n🎉 Agent集成演示完成!")
    print("💡 这展示了AI Agent如何:")
    print("  🧠 生成交易决策")
    print("  🎯 自动执行操作")
    print("  🔒 保持安全控制")
    print("  📊 提供决策理由")

def main():
    print("🎯 完整交易系统测试")
    print("=" * 50)
    print("这将演示真正的交易操作流程")
    print()
    
    try:
        # 1. 完整交易演示
        complete_trading_demo()
        
        # 2. Agent集成演示
        agent_demo = input("\n是否继续Agent集成演示? (y/n): ")
        if agent_demo.lower() == 'y':
            agent_integration_demo()
        
        print("\n🎉 所有演示完成!")
        print("现在您已经看到了完整的交易操作流程。")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
