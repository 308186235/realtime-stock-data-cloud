#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版云端调用系统
核心功能:记住调用时间,根据时间找文件,支持重试
"""

import subprocess
import time
import os
from datetime import datetime, timedelta

class SimpleCloudCaller:
    def __init__(self):
        self.rclone_path = r"C:\Users\锋\Downloads\rclone-v1.70.2-windows-amd64 (1)\rclone-v1.70.2-windows-amd64\rclone.exe"
        self.onedrive_remote = "onedrive_personal:TradingData"
    
    def call_with_time_tracking(self, operation_type):
        """
        带时间跟踪的调用
        operation_type: 'holdings', 'orders', 'transactions', 'balance'
        """
        print(f"🚀 开始调用: {operation_type}")
        
        # 1. 记录调用时间
        call_time = datetime.now()
        print(f"📅 调用时间: {call_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 2. 执行调用
        success = self._execute_operation(operation_type)
        
        if not success:
            print(f"❌ 调用失败")
            return {"success": False, "message": "调用失败"}
        
        print(f"✅ 调用成功")
        
        # 3. 根据时间查找文件
        if operation_type == 'balance':
            # 余额直接返回,不需要查找文件
            return {"success": True, "message": "余额获取成功"}
        
        # 4. 查找对应的导出文件
        expected_filename = self._generate_filename(operation_type, call_time)
        print(f"📁 期望文件: {expected_filename}")
        
        # 5. 等待并查找文件
        found_file = self._wait_and_find_file(operation_type, call_time)
        
        if found_file:
            print(f"✅ 找到文件: {found_file}")
            
            # 6. 下载文件
            if self._download_file(found_file):
                return {
                    "success": True,
                    "message": "调用成功,文件已获取",
                    "filename": found_file,
                    "local_path": f"./downloads/{found_file}"
                }
        
        # 7. 如果没找到文件,尝试重试
        print(f"⚠️ 未找到期望文件,准备重试...")
        return self._retry_operation(operation_type, call_time)
    
    def _execute_operation(self, operation_type):
        """执行具体操作"""
        try:
            if operation_type == 'holdings':
                from trader_export import export_holdings
                return export_holdings()
            elif operation_type == 'orders':
                from trader_export import export_orders
                return export_orders()
            elif operation_type == 'transactions':
                from trader_export import export_transactions
                return export_transactions()
            elif operation_type == 'balance':
                from fixed_balance_reader import FixedBalanceReader
                balance_reader = FixedBalanceReader()
                balance_data = balance_reader.get_account_balance()
                return balance_data is not None
            else:
                return False
        except Exception as e:
            print(f"❌ 执行异常: {e}")
            return False
    
    def _generate_filename(self, operation_type, call_time):
        """生成期望的文件名"""
        time_str = call_time.strftime('%m%d_%H%M%S')
        
        if operation_type == 'holdings':
            return f'持仓数据_{time_str}.csv'
        elif operation_type == 'orders':
            return f'委托数据_{time_str}.csv'
        elif operation_type == 'transactions':
            return f'成交数据_{time_str}.csv'
        else:
            return f'{operation_type}_{time_str}.csv'
    
    def _wait_and_find_file(self, operation_type, call_time, max_wait_seconds=60):
        """等待并查找文件"""
        print(f"⏳ 等待文件生成...")
        
        for wait_seconds in range(0, max_wait_seconds, 10):
            print(f"   检查中... ({wait_seconds}s/{max_wait_seconds}s)")
            
            # 列出OneDrive文件
            files = self._list_onedrive_files()
            
            # 查找匹配的文件
            found_file = self._find_matching_file(files, operation_type, call_time)
            
            if found_file:
                return found_file
            
            time.sleep(10)
        
        return None
    
    def _list_onedrive_files(self):
        """列出OneDrive文件"""
        try:
            result = subprocess.run([
                self.rclone_path, 'ls', self.onedrive_remote
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            filename = ' '.join(parts[1:])
                            files.append(filename)
                return files
            else:
                print(f"❌ 列出文件失败: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ 列出文件异常: {e}")
            return []
    
    def _find_matching_file(self, files, operation_type, call_time):
        """查找匹配的文件"""
        # 生成可能的时间模式(前后5分钟)
        time_patterns = []
        for i in range(-5, 6):
            adjusted_time = call_time + timedelta(minutes=i)
            time_str = adjusted_time.strftime('%m%d_%H%M')
            time_patterns.append(time_str)
        
        # 文件类型映射
        type_map = {
            'holdings': '持仓数据',
            'orders': '委托数据',
            'transactions': '成交数据'
        }
        
        file_prefix = type_map.get(operation_type, operation_type)
        
        # 查找匹配的文件
        for file in files:
            if file_prefix in file:
                for pattern in time_patterns:
                    if pattern in file:
                        return file
        
        return None
    
    def _download_file(self, filename):
        """下载文件"""
        try:
            # 确保下载目录存在
            os.makedirs('./downloads', exist_ok=True)
            
            result = subprocess.run([
                self.rclone_path, 'copy',
                f'{self.onedrive_remote}/{filename}',
                './downloads/'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                local_file = f'./downloads/{filename}'
                if os.path.exists(local_file):
                    print(f"✅ 文件下载成功: {filename}")
                    return True
            
            print(f"❌ 文件下载失败: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return False
    
    def _retry_operation(self, operation_type, original_call_time):
        """重试操作"""
        print(f"🔄 开始重试...")
        
        # 检查是否在交易时间
        current_time = datetime.now()
        if self._is_trading_time(current_time):
            print("⚠️ 交易时间,延迟重试...")
            time.sleep(30)
        
        # 重新执行
        retry_time = datetime.now()
        success = self._execute_operation(operation_type)
        
        if not success:
            return {"success": False, "message": "重试失败"}
        
        print(f"✅ 重试调用成功")
        
        # 等待文件
        time.sleep(20)  # 等待20秒
        found_file = self._wait_and_find_file(operation_type, retry_time, 30)
        
        if found_file:
            print(f"✅ 重试成功,找到文件: {found_file}")
            if self._download_file(found_file):
                return {
                    "success": True,
                    "message": "重试成功",
                    "filename": found_file,
                    "local_path": f"./downloads/{found_file}",
                    "retry": True
                }
        
        return {"success": False, "message": "重试后仍未找到文件"}
    
    def _is_trading_time(self, check_time):
        """检查是否为交易时间"""
        if check_time.weekday() >= 5:  # 周末
            return False
        
        time_str = check_time.strftime('%H:%M')
        morning = '09:30' <= time_str <= '11:30'
        afternoon = '13:00' <= time_str <= '15:00'
        
        return morning or afternoon

def test_simple_caller():
    """测试简化版调用器"""
    print("🚀 测试简化版云端调用器")
    print("=" * 50)
    
    caller = SimpleCloudCaller()
    
    # 测试余额获取
    print("\n💰 测试余额获取:")
    result = caller.call_with_time_tracking('balance')
    print(f"结果: {result}")
    
    # 测试持仓导出
    print("\n📊 测试持仓导出:")
    result = caller.call_with_time_tracking('holdings')
    print(f"结果: {result}")

if __name__ == '__main__':
    test_simple_caller()
