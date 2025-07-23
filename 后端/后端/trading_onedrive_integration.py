#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易系统OneDrive集成
自动同步交易数据到OneDrive个人账户
"""

import os
import subprocess
import sys
import time
import json
import schedule
import threading
from pathlib import Path
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onedrive_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TradingOneDriveSync:
    def __init__(self):
        # rclone配置
        self.rclone_path = r"C:\Users\锋\Downloads\rclone-v1.70.2-windows-amd64 (1)\rclone-v1.70.2-windows-amd64\rclone.exe"
        self.remote_name = "onedrive_personal"
        
        # 路径配置
        self.local_trading_data = Path("C:/mnt/onedrive/TradingData")
        self.remote_trading_data = f"{self.remote_name}:TradingData"
        
        # 交易数据文件模式
        self.trading_files = [
            "latest_balance.json",
            "latest_positions.json",
            "委托数据_*.csv",
            "持仓数据_*.csv",
            "*.xls"
        ]
        
        # 确保本地目录存在
        self.local_trading_data.mkdir(parents=True, exist_ok=True)
        
        # 同步状态
        self.last_sync_time = None
        self.sync_interval = 300  # 5分钟同步一次
        
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
            logging.error(f"rclone命令执行失败: {e}")
            return False, "", str(e)
    
    def test_connection(self):
        """测试OneDrive连接"""
        logging.info("测试OneDrive连接...")
        success, stdout, stderr = self.run_rclone_command(['ls', f'{self.remote_name}:'])
        if success:
            logging.info("OneDrive连接成功!")
            return True
        else:
            logging.error(f"OneDrive连接失败: {stderr}")
            return False
    
    def sync_to_onedrive(self):
        """同步交易数据到OneDrive"""
        try:
            logging.info("开始同步交易数据到OneDrive...")

            # 检查本地是否有新文件
            local_files = list(self.local_trading_data.glob("*"))
            if not local_files:
                logging.info("本地没有交易数据文件")
                return True

            # 使用rclone copy逐个上传文件,避免OneNote冲突
            success_count = 0
            for file_path in local_files:
                if file_path.is_file() and not file_path.name.endswith(('.log', '.tmp')):
                    file_success, stdout, stderr = self.run_rclone_command([
                        'copy',
                        str(file_path),
                        self.remote_trading_data,
                        '--progress'
                    ])

                    if file_success:
                        success_count += 1
                        logging.info(f"文件上传成功: {file_path.name}")
                    else:
                        logging.error(f"文件上传失败 {file_path.name}: {stderr}")

            if success_count > 0:
                self.last_sync_time = datetime.now()
                logging.info(f"同步到OneDrive完成! 成功上传文件数量: {success_count}/{len(local_files)}")
                return True
            else:
                logging.error("没有文件成功上传")
                return False

        except Exception as e:
            logging.error(f"同步过程出错: {e}")
            return False
    
    def backup_trading_data(self):
        """备份交易数据"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_remote = f"{self.remote_name}:TradingData/backup/{timestamp}"
            
            logging.info(f"创建交易数据备份: {timestamp}")
            
            success, stdout, stderr = self.run_rclone_command([
                'copy',
                str(self.local_trading_data),
                backup_remote,
                '--progress'
            ])
            
            if success:
                logging.info(f"备份创建成功: {backup_remote}")
                return True
            else:
                logging.error(f"备份创建失败: {stderr}")
                return False
                
        except Exception as e:
            logging.error(f"备份过程出错: {e}")
            return False
    
    def upload_file(self, file_path, remote_path=None):
        """上传单个文件到OneDrive"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logging.error(f"文件不存在: {file_path}")
                return False
            
            if remote_path is None:
                remote_path = f"{self.remote_trading_data}/{file_path.name}"
            
            logging.info(f"上传文件: {file_path.name}")
            
            success, stdout, stderr = self.run_rclone_command([
                'copy',
                str(file_path),
                remote_path,
                '--progress'
            ])
            
            if success:
                logging.info(f"文件上传成功: {file_path.name}")
                return True
            else:
                logging.error(f"文件上传失败: {stderr}")
                return False
                
        except Exception as e:
            logging.error(f"上传文件出错: {e}")
            return False
    
    def get_sync_status(self):
        """获取同步状态"""
        status = {
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "local_files_count": len(list(self.local_trading_data.glob("*"))),
            "connection_status": self.test_connection()
        }
        return status
    
    def create_status_report(self):
        """创建状态报告"""
        try:
            status = self.get_sync_status()
            status["report_time"] = datetime.now().isoformat()
            
            report_file = self.local_trading_data / "sync_status.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            
            # 上传状态报告
            self.upload_file(report_file)
            
            logging.info("状态报告已创建并上传")
            return True
            
        except Exception as e:
            logging.error(f"创建状态报告失败: {e}")
            return False
    
    def scheduled_sync(self):
        """定时同步任务"""
        logging.info("执行定时同步任务...")
        
        # 同步到OneDrive
        if self.sync_to_onedrive():
            # 创建状态报告
            self.create_status_report()
        
        logging.info("定时同步任务完成")
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        logging.info("启动OneDrive同步调度器...")
        
        # 每5分钟同步一次
        schedule.every(5).minutes.do(self.scheduled_sync)
        
        # 每小时创建一次备份
        schedule.every().hour.do(self.backup_trading_data)
        
        # 运行调度器
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def run_once(self):
        """运行一次同步"""
        logging.info("执行一次性同步...")
        
        if not self.test_connection():
            logging.error("OneDrive连接失败")
            return False
        
        # 同步数据
        success = self.sync_to_onedrive()
        
        # 创建状态报告
        self.create_status_report()
        
        return success

def main():
    print("============================================================")
    print("🔄 交易系统OneDrive集成")
    print("============================================================")
    
    sync = TradingOneDriveSync()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "once":
            # 运行一次同步
            if sync.run_once():
                print("✅ 同步完成!")
            else:
                print("❌ 同步失败!")
                
        elif command == "schedule":
            # 启动定时同步
            print("🕐 启动定时同步服务...")
            sync.start_scheduler()
            
        elif command == "backup":
            # 创建备份
            if sync.backup_trading_data():
                print("✅ 备份完成!")
            else:
                print("❌ 备份失败!")
                
        elif command == "status":
            # 显示状态
            status = sync.get_sync_status()
            print("📊 同步状态:")
            print(json.dumps(status, ensure_ascii=False, indent=2))
            
        else:
            print("❌ 未知命令")
            print("可用命令: once, schedule, backup, status")
    else:
        # 默认运行一次同步
        sync.run_once()

if __name__ == "__main__":
    main()
