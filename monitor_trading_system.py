#!/usr/bin/env python3
"""
OneDrive交易系统监控脚本
实时监控系统状态和数据同步
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class TradingSystemMonitor:
    """交易系统监控器"""
    
    def __init__(self):
        self.onedrive_path = Path("C:/mnt/onedrive/TradingData")
        self.rclone_exe = Path("E:/交易8/rclone/rclone-v1.70.2-windows-amd64/rclone.exe")
        self.log_file = Path("E:/交易8/rclone.log")
        self.cloud_api = "https://api.aigupiao.me"
        
    def check_rclone_process(self):
        """检查rclone进程状态"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq rclone.exe'],
                capture_output=True, text=True
            )
            
            if 'rclone.exe' in result.stdout:
                return True, "rclone进程正在运行"
            else:
                return False, "rclone进程未运行"
                
        except Exception as e:
            return False, f"检查rclone进程失败: {e}"
    
    def check_mount_status(self):
        """检查挂载状态"""
        try:
            if not self.onedrive_path.exists():
                return False, "挂载目录不存在"
            
            # 测试读写权限
            test_file = self.onedrive_path / "monitor_test.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"monitor test {datetime.now()}")
            
            if test_file.exists():
                test_file.unlink()
                return True, "挂载正常，具有读写权限"
            else:
                return False, "挂载写入测试失败"
                
        except Exception as e:
            return False, f"挂载测试失败: {e}"
    
    def check_data_files(self):
        """检查数据文件状态"""
        files_status = {}
        
        data_files = [
            "latest_positions.json",
            "latest_balance.json"
        ]
        
        for filename in data_files:
            file_path = self.onedrive_path / filename
            
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    files_status[filename] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "timestamp": data.get("timestamp", "未知"),
                        "valid_json": True
                    }
                except Exception as e:
                    files_status[filename] = {
                        "exists": True,
                        "error": str(e),
                        "valid_json": False
                    }
            else:
                files_status[filename] = {
                    "exists": False
                }
        
        return files_status
    
    def check_cloud_api(self):
        """检查云端API状态"""
        endpoints = [
            ("持仓API", f"{self.cloud_api}/api/local-trading/positions"),
            ("余额API", f"{self.cloud_api}/api/local-trading/balance")
        ]
        
        api_status = {}
        
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    api_status[name] = {
                        "status": "正常",
                        "status_code": 200,
                        "response_time": response.elapsed.total_seconds(),
                        "has_data": bool(data),
                        "timestamp": data.get("timestamp", "未知")
                    }
                else:
                    api_status[name] = {
                        "status": "异常",
                        "status_code": response.status_code,
                        "error": response.text[:100]
                    }
                    
            except Exception as e:
                api_status[name] = {
                    "status": "连接失败",
                    "error": str(e)
                }
        
        return api_status
    
    def get_system_status(self):
        """获取系统整体状态"""
        print("🔍 检查系统状态...")
        
        # 检查rclone进程
        rclone_ok, rclone_msg = self.check_rclone_process()
        
        # 检查挂载状态
        mount_ok, mount_msg = self.check_mount_status()
        
        # 检查数据文件
        files_status = self.check_data_files()
        
        # 检查云端API
        api_status = self.check_cloud_api()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "rclone": {"status": rclone_ok, "message": rclone_msg},
            "mount": {"status": mount_ok, "message": mount_msg},
            "files": files_status,
            "api": api_status
        }
    
    def display_status(self, status):
        """显示系统状态"""
        print("\n" + "=" * 60)
        print("📊 OneDrive交易系统状态监控")
        print("=" * 60)
        print(f"⏰ 检查时间: {status['timestamp']}")
        print()
        
        # rclone进程状态
        rclone_icon = "✅" if status['rclone']['status'] else "❌"
        print(f"{rclone_icon} rclone进程: {status['rclone']['message']}")
        
        # 挂载状态
        mount_icon = "✅" if status['mount']['status'] else "❌"
        print(f"{mount_icon} OneDrive挂载: {status['mount']['message']}")
        
        # 数据文件状态
        print("\n📁 数据文件状态:")
        for filename, file_info in status['files'].items():
            if file_info.get('exists'):
                if file_info.get('valid_json'):
                    print(f"   ✅ {filename}")
                    print(f"      大小: {file_info['size']} 字节")
                    print(f"      修改时间: {file_info['modified']}")
                    print(f"      数据时间: {file_info['timestamp']}")
                else:
                    print(f"   ❌ {filename} (JSON格式错误)")
            else:
                print(f"   ❌ {filename} (文件不存在)")
        
        # 云端API状态
        print("\n🌐 云端API状态:")
        for api_name, api_info in status['api'].items():
            if api_info['status'] == '正常':
                print(f"   ✅ {api_name}")
                print(f"      响应时间: {api_info['response_time']:.2f}秒")
                print(f"      数据时间: {api_info['timestamp']}")
            else:
                print(f"   ❌ {api_name}: {api_info['status']}")
                if 'error' in api_info:
                    print(f"      错误: {api_info['error']}")
        
        # 整体状态评估
        print("\n📊 系统整体状态:")
        all_ok = (
            status['rclone']['status'] and 
            status['mount']['status'] and
            all(f.get('valid_json', False) for f in status['files'].values() if f.get('exists')) and
            all(api['status'] == '正常' for api in status['api'].values())
        )
        
        if all_ok:
            print("   🎉 系统运行正常，所有组件工作正常")
        else:
            print("   ⚠️ 系统存在问题，请检查上述异常项目")
        
        print("=" * 60)
    
    def run_continuous_monitor(self, interval=30):
        """运行连续监控"""
        print("🚀 启动OneDrive交易系统连续监控")
        print(f"📋 监控间隔: {interval}秒")
        print("📋 按 Ctrl+C 停止监控")
        print()
        
        try:
            while True:
                status = self.get_system_status()
                self.display_status(status)
                
                print(f"\n⏳ 等待 {interval} 秒后进行下次检查...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
    
    def run_single_check(self):
        """运行单次检查"""
        status = self.get_system_status()
        self.display_status(status)
        
        return all([
            status['rclone']['status'],
            status['mount']['status'],
            any(f.get('valid_json', False) for f in status['files'].values() if f.get('exists'))
        ])

def main():
    """主函数"""
    monitor = TradingSystemMonitor()
    
    print("🔍 OneDrive交易系统监控")
    print("=" * 40)
    print("1. 单次检查")
    print("2. 连续监控 (30秒间隔)")
    print("3. 连续监控 (60秒间隔)")
    print("=" * 40)
    
    choice = input("请选择监控模式 (1-3): ").strip()
    
    if choice == "1":
        success = monitor.run_single_check()
        if success:
            print("\n🎯 系统检查完成！")
        else:
            print("\n💥 系统存在问题，请检查！")
    elif choice == "2":
        monitor.run_continuous_monitor(30)
    elif choice == "3":
        monitor.run_continuous_monitor(60)
    else:
        print("❌ 无效选择")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
