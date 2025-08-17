#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive同步工具
使用rclone进行OneDrive文件同步,替代挂载方式
"""

import os
import subprocess
import sys
import time
import json
from pathlib import Path

class OneDriveSync:
    def __init__(self):
        # rclone路径
        self.rclone_path = r"C:\Users\锋\Downloads\rclone-v1.70.2-windows-amd64 (1)\rclone-v1.70.2-windows-amd64\rclone.exe"
        self.remote_name = "onedrive_personal"
        self.local_trading_data = Path("C:/mnt/onedrive/TradingData")
        self.remote_trading_data = f"{self.remote_name}:TradingData"
        
        # 确保本地目录存在
        self.local_trading_data.mkdir(parents=True, exist_ok=True)
        
    def run_rclone_command(self, command):
        """执行rclone命令"""
        try:
            full_command = [self.rclone_path] + command
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def test_connection(self):
        """测试OneDrive连接"""
        print("🔍 测试OneDrive连接...")
        success, stdout, stderr = self.run_rclone_command(['ls', f'{self.remote_name}:'])
        if success:
            print("✅ OneDrive连接成功!")
            return True
        else:
            print(f"❌ OneDrive连接失败: {stderr}")
            return False
    
    def sync_from_onedrive(self):
        """从OneDrive同步到本地"""
        print("📥 从OneDrive同步数据到本地...")
        success, stdout, stderr = self.run_rclone_command([
            'sync',
            self.remote_trading_data,
            str(self.local_trading_data),
            '--progress'
        ])
        if success:
            print("✅ 从OneDrive同步完成!")
            return True
        else:
            print(f"❌ 从OneDrive同步失败: {stderr}")
            return False
    
    def sync_to_onedrive(self):
        """同步本地数据到OneDrive"""
        print("📤 同步本地数据到OneDrive...")
        success, stdout, stderr = self.run_rclone_command([
            'sync',
            str(self.local_trading_data),
            self.remote_trading_data,
            '--progress'
        ])
        if success:
            print("✅ 同步到OneDrive完成!")
            return True
        else:
            print(f"❌ 同步到OneDrive失败: {stderr}")
            return False
    
    def copy_file_to_onedrive(self, local_file_path, remote_path=None):
        """复制单个文件到OneDrive"""
        local_file = Path(local_file_path)
        if not local_file.exists():
            print(f"❌ 本地文件不存在: {local_file_path}")
            return False
        
        if remote_path is None:
            remote_path = f"{self.remote_trading_data}/{local_file.name}"
        
        print(f"📤 上传文件: {local_file.name}")
        success, stdout, stderr = self.run_rclone_command([
            'copy',
            str(local_file),
            remote_path,
            '--progress'
        ])
        
        if success:
            print(f"✅ 文件上传成功: {local_file.name}")
            return True
        else:
            print(f"❌ 文件上传失败: {stderr}")
            return False
    
    def list_onedrive_files(self):
        """列出OneDrive中的文件"""
        print("📁 OneDrive文件列表:")
        success, stdout, stderr = self.run_rclone_command(['ls', self.remote_trading_data])
        if success:
            if stdout.strip():
                for line in stdout.strip().split('\n'):
                    print(f"   📄 {line}")
            else:
                print("   (空目录)")
            return True
        else:
            print(f"❌ 无法列出文件: {stderr}")
            return False
    
    def create_trading_data_file(self, filename, data):
        """创建交易数据文件"""
        file_path = self.local_trading_data / filename
        try:
            if isinstance(data, dict):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            print(f"✅ 创建文件: {filename}")
            return True
        except Exception as e:
            print(f"❌ 创建文件失败: {e}")
            return False

def main():
    print("============================================================")
    print("🔄 OneDrive同步工具")
    print("============================================================")
    
    sync = OneDriveSync()
    
    # 测试连接
    if not sync.test_connection():
        print("❌ OneDrive连接失败,请检查配置")
        return
    
    # 列出OneDrive文件
    sync.list_onedrive_files()
    
    # 从OneDrive同步到本地
    sync.sync_from_onedrive()
    
    # 创建测试文件
    test_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "OneDrive同步测试成功",
        "message": "个人OneDrive配置已完成"
    }
    
    if sync.create_trading_data_file("sync_test.json", test_data):
        # 上传测试文件
        sync.copy_file_to_onedrive(sync.local_trading_data / "sync_test.json")
    
    print("\n✅ OneDrive同步工具运行完成!")
    print(f"📁 本地目录: {sync.local_trading_data}")
    print(f"☁️ 远程目录: {sync.remote_trading_data}")

if __name__ == "__main__":
    main()
