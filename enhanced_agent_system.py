#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版AI股票交易Agent系统
支持：
1. 北交所开关控制
2. 交易时间自动检查
3. 自动重连机制
4. 详细数据清洗统计
"""

import sys
import os
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_agent_simple import SupabaseAgentSystem, TRADING_CONFIG

class EnhancedAgentSystem(SupabaseAgentSystem):
    """增强版Agent系统"""
    
    def __init__(self):
        super().__init__()
        self.session_stats = {
            'start_time': None,
            'total_processed': 0,
            'total_decisions': 0,
            'reconnect_count': 0,
            'filter_stats': {}
        }
    
    def toggle_beijing_exchange(self, enable: bool = None):
        """切换北交所交易权限"""
        if enable is None:
            enable = not TRADING_CONFIG['enable_beijing_exchange']
        
        old_status = TRADING_CONFIG['enable_beijing_exchange']
        TRADING_CONFIG['enable_beijing_exchange'] = enable
        
        if old_status != enable:
            status = "开启" if enable else "关闭"
            print(f"🔧 北交所交易权限已{status}")
            return True
        return False
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n" + "="*60)
        print("📊 AI股票交易Agent系统状态")
        print("="*60)
        print(f"🏢 北交所权限: {'✅ 开启' if TRADING_CONFIG['enable_beijing_exchange'] else '❌ 关闭'}")
        print(f"⏰ 交易时间: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
        print(f"⏱️ 分析间隔: {TRADING_CONFIG['analysis_interval']}秒")
        
        if self.session_stats['start_time']:
            runtime = datetime.now() - self.session_stats['start_time']
            print(f"🕐 运行时间: {runtime}")
            print(f"📈 处理数据: {self.session_stats['total_processed']}条")
            print(f"🎯 生成决策: {self.session_stats['total_decisions']}个")
            print(f"🔄 重连次数: {self.session_stats['reconnect_count']}次")
            
            if self.session_stats['filter_stats']:
                filter_info = ", ".join([f"{reason}: {count}只" for reason, count in self.session_stats['filter_stats'].items()])
                print(f"🔍 过滤统计: {filter_info}")
        
        is_trading = self.is_trading_time()
        print(f"⏰ 交易状态: {'✅ 交易时间内' if is_trading else '❌ 非交易时间'}")
        print("="*60)
    
    def start_enhanced_system(self):
        """启动增强版实时系统"""
        self.session_stats['start_time'] = datetime.now()
        print("🚀 启动增强版AI股票交易Agent系统")
        self.show_system_status()
        
        while self.reconnect_count < TRADING_CONFIG['max_reconnect_attempts']:
            try:
                # 检查交易时间
                if not self.is_trading_time():
                    print("⏰ 当前非交易时间，等待交易时间开始...")
                    print("💡 提示：您可以按 Ctrl+C 退出系统")
                    time.sleep(60)
                    continue
                
                print("✅ 进入交易时间，开始连接数据源...")
                
                # 调用父类的启动方法
                success = self.start_realtime_system()
                
                if not success:
                    self.session_stats['reconnect_count'] += 1
                    if self.session_stats['reconnect_count'] < TRADING_CONFIG['max_reconnect_attempts']:
                        wait_time = TRADING_CONFIG['reconnect_interval']
                        print(f"⏳ {wait_time}秒后尝试重连...")
                        time.sleep(wait_time)
                    else:
                        print("❌ 达到最大重连次数，系统停止")
                        break
                else:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 用户中断，系统停止")
                break
            except Exception as e:
                print(f"❌ 系统错误: {e}")
                break
        
        self.show_final_stats()
    
    def show_final_stats(self):
        """显示最终统计"""
        if self.session_stats['start_time']:
            runtime = datetime.now() - self.session_stats['start_time']
            print("\n" + "="*60)
            print("📊 系统运行总结")
            print("="*60)
            print(f"🕐 总运行时间: {runtime}")
            print(f"📈 总处理数据: {self.session_stats['total_processed']}条")
            print(f"🎯 总生成决策: {self.session_stats['total_decisions']}个")
            print(f"🔄 总重连次数: {self.session_stats['reconnect_count']}次")
            print("="*60)

def main():
    """主菜单"""
    system = EnhancedAgentSystem()
    
    while True:
        print("\n" + "="*60)
        print("🤖 增强版AI股票交易Agent系统")
        print("="*60)
        print("1. 启动实时Agent系统")
        print("2. 查看系统状态")
        print("3. 切换北交所权限")
        print("4. 查看最近决策")
        print("5. 测试数据清洗")
        print("6. 检查交易时间")
        print("0. 退出")
        print("="*60)
        
        try:
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
            elif choice == '1':
                system.start_enhanced_system()
            elif choice == '2':
                system.show_system_status()
            elif choice == '3':
                current_status = "开启" if TRADING_CONFIG['enable_beijing_exchange'] else "关闭"
                print(f"\n当前北交所权限: {current_status}")
                toggle = input("是否切换? (y/n): ").strip().lower()
                if toggle == 'y':
                    system.toggle_beijing_exchange()
            elif choice == '4':
                # 查看最近决策
                try:
                    decisions = system.supabase.select('agent_decisions', limit=5)
                    if decisions:
                        print("\n🎯 最近5个Agent决策:")
                        for i, decision in enumerate(decisions, 1):
                            action = decision.get('action', 'N/A')
                            symbol = decision.get('symbol', 'N/A')
                            reason = decision.get('reason', 'N/A')
                            confidence = decision.get('confidence', 0)
                            timestamp = decision.get('timestamp', 'N/A')
                            print(f"{i}. {action}: {symbol} - {reason}")
                            print(f"   信心度: {confidence}%, 时间: {timestamp}")
                    else:
                        print("📭 暂无决策记录")
                except Exception as e:
                    print(f"❌ 查询决策失败: {e}")
            elif choice == '5':
                # 测试数据清洗
                test_stocks = [
                    {'symbol': 'BJ430001', 'name': '北交所测试', 'price': 10, 'volume': 1000000, 'amount': 10000000, 'change_percent': 5},
                    {'symbol': 'SZ000001', 'name': '平安银行', 'price': 12, 'volume': 2000000, 'amount': 24000000, 'change_percent': 3},
                    {'symbol': 'SH600000', 'name': '浦发银行', 'price': 8, 'volume': 50, 'amount': 400, 'change_percent': 2}  # 成交量过小
                ]
                
                print("\n🔍 数据清洗测试:")
                for stock in test_stocks:
                    is_valid, reason = system._clean_stock_data(stock)
                    status = "✅ 通过" if is_valid else f"❌ 过滤: {reason}"
                    print(f"  {stock['symbol']} ({stock['name']}): {status}")
            elif choice == '6':
                is_trading = system.is_trading_time()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                status = "✅ 是" if is_trading else "❌ 否"
                print(f"\n⏰ 当前时间: {current_time}")
                print(f"交易时间: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
                print(f"是否为交易时间: {status}")
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
