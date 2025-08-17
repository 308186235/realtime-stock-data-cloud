#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易配置管理器
支持北交所开关,交易时间控制等功能
"""

import sys
import os
import time
from datetime import datetime
import logging

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_agent_simple import SupabaseClient, TRADING_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingConfigManager:
    """交易配置管理器"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.load_config()
    
    def load_config(self):
        """从数据库加载配置"""
        try:
            configs = self.supabase.select('trading_config', limit=20)
            for config in configs:
                key = config.get('config_key')
                value = config.get('config_value')
                
                if key == 'enable_beijing_exchange':
                    TRADING_CONFIG['enable_beijing_exchange'] = value.lower() == 'true'
                elif key == 'trading_start_time':
                    TRADING_CONFIG['trading_start_time'] = value
                elif key == 'trading_end_time':
                    TRADING_CONFIG['trading_end_time'] = value
                elif key == 'analysis_interval':
                    TRADING_CONFIG['analysis_interval'] = int(value)
                    
            logger.info("📋 配置加载完成")
            self.show_current_config()
        except Exception as e:
            logger.warning(f"配置加载失败,使用默认配置: {e}")
    
    def save_config(self, key: str, value: str):
        """保存配置到数据库"""
        try:
            config_data = {
                'config_key': key,
                'config_value': value,
                'updated_at': datetime.now().isoformat()
            }

            # 直接插入新配置(如果key重复会自动覆盖)
            if self.supabase.insert('trading_config', config_data):
                logger.info(f"✅ 配置已保存: {key} = {value}")
                return True
            else:
                logger.error(f"❌ 配置保存失败: {key}")
                return False
        except Exception as e:
            logger.error(f"保存配置错误: {e}")
            return False
    
    def toggle_beijing_exchange(self, enable: bool = None):
        """切换北交所交易权限"""
        if enable is None:
            # 切换当前状态
            enable = not TRADING_CONFIG['enable_beijing_exchange']
        
        TRADING_CONFIG['enable_beijing_exchange'] = enable
        status = "开启" if enable else "关闭"
        
        if self.save_config('enable_beijing_exchange', str(enable).lower()):
            logger.info(f"🔧 北交所交易权限已{status}")
            return True
        return False
    
    def set_trading_time(self, start_time: str = None, end_time: str = None):
        """设置交易时间"""
        if start_time:
            TRADING_CONFIG['trading_start_time'] = start_time
            self.save_config('trading_start_time', start_time)
            
        if end_time:
            TRADING_CONFIG['trading_end_time'] = end_time
            self.save_config('trading_end_time', end_time)
            
        logger.info(f"⏰ 交易时间已更新: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
    
    def set_analysis_interval(self, interval: int):
        """设置分析间隔"""
        TRADING_CONFIG['analysis_interval'] = interval
        if self.save_config('analysis_interval', str(interval)):
            logger.info(f"⏱️ 分析间隔已设置为: {interval}秒")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n" + "="*60)
        print("📋 当前交易配置")
        print("="*60)
        print(f"🏢 北交所交易权限: {'✅ 开启' if TRADING_CONFIG['enable_beijing_exchange'] else '❌ 关闭'}")
        print(f"⏰ 交易时间: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
        print(f"⏱️ 分析间隔: {TRADING_CONFIG['analysis_interval']}秒")
        print(f"🔄 重连间隔: {TRADING_CONFIG['reconnect_interval']}秒")
        print(f"🔢 最大重连次数: {TRADING_CONFIG['max_reconnect_attempts']}次")
        print("="*60)
    
    def is_trading_time(self):
        """检查是否在交易时间内"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # 检查是否是工作日
        if now.weekday() >= 5:  # 周六日
            return False, "非工作日"
            
        # 检查时间范围
        start_time = TRADING_CONFIG['trading_start_time']
        end_time = TRADING_CONFIG['trading_end_time']
        
        if start_time <= current_time <= end_time:
            return True, "交易时间内"
        else:
            return False, f"非交易时间 (交易时间: {start_time}-{end_time})"

def main():
    """主菜单"""
    config_manager = TradingConfigManager()
    
    while True:
        print("\n" + "="*60)
        print("🔧 交易配置管理器")
        print("="*60)
        print("1. 查看当前配置")
        print("2. 切换北交所交易权限")
        print("3. 设置交易时间")
        print("4. 设置分析间隔")
        print("5. 检查交易时间状态")
        print("6. 测试数据库连接")
        print("0. 退出")
        print("="*60)
        
        try:
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == '0':
                print("👋 再见!")
                break
            elif choice == '1':
                config_manager.show_current_config()
            elif choice == '2':
                current_status = "开启" if TRADING_CONFIG['enable_beijing_exchange'] else "关闭"
                print(f"\n当前北交所权限: {current_status}")
                toggle = input("是否切换? (y/n): ").strip().lower()
                if toggle == 'y':
                    config_manager.toggle_beijing_exchange()
            elif choice == '3':
                print(f"\n当前交易时间: {TRADING_CONFIG['trading_start_time']} - {TRADING_CONFIG['trading_end_time']}")
                start = input("输入开始时间 (格式: HH:MM, 回车跳过): ").strip()
                end = input("输入结束时间 (格式: HH:MM, 回车跳过): ").strip()
                
                if start or end:
                    config_manager.set_trading_time(
                        start if start else None,
                        end if end else None
                    )
            elif choice == '4':
                print(f"\n当前分析间隔: {TRADING_CONFIG['analysis_interval']}秒")
                try:
                    interval = int(input("输入新的分析间隔(秒): "))
                    config_manager.set_analysis_interval(interval)
                except ValueError:
                    print("❌ 请输入有效的数字")
            elif choice == '5':
                is_trading, reason = config_manager.is_trading_time()
                status = "✅ 是" if is_trading else "❌ 否"
                print(f"\n当前是否为交易时间: {status}")
                print(f"原因: {reason}")
            elif choice == '6':
                try:
                    result = config_manager.supabase.select('trading_config', limit=1)
                    print("✅ 数据库连接正常")
                except Exception as e:
                    print(f"❌ 数据库连接失败: {e}")
            else:
                print("❌ 无效选择,请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
