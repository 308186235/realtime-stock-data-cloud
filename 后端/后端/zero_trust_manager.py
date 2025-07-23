# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Zero Trust 管理和维护工具
提供系统管理,故障排除和维护功能
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zero_trust_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ZeroTrustManager:
    """Zero Trust管理器"""
    
    def __init__(self):
        self.config = {
            'cloudflared_path': 'cloudflared.exe',
            'config_file': 'config.yml',
            'tunnel_name': 'aigupiao-tunnel',
            'log_file': 'zero_trust_manager.log',
            'backup_dir': 'backups',
            'monitor_script': 'zero_trust_connection_monitor.py'
        }
        
        # 确保备份目录存在
        os.makedirs(self.config['backup_dir'], exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """统一日志输出"""
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "SUCCESS":
            logger.info(f"✅ {message}")
        else:
            logger.info(message)
    
    def run_command(self, command: str, timeout: int = 30) -> tuple:
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令执行超时"
        except Exception as e:
            return False, "", str(e)
    
    def get_tunnel_status(self) -> Dict:
        """获取隧道状态"""
        self.log("🔍 检查隧道状态...")
        
        status = {
            'process_running': False,
            'tunnel_connected': False,
            'process_info': None,
            'connection_count': 0,
            'uptime': None
        }
        
        # 检查cloudflared进程
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                if 'cloudflared' in proc.info['name'].lower():
                    status['process_running'] = True
                    status['process_info'] = {
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(proc.info['cmdline']),
                        'create_time': datetime.fromtimestamp(proc.info['create_time']).isoformat()
                    }
                    
                    # 计算运行时间
                    uptime_seconds = time.time() - proc.info['create_time']
                    status['uptime'] = str(timedelta(seconds=int(uptime_seconds)))
                    break
        except Exception as e:
            self.log(f"检查进程失败: {e}", "ERROR")
        
        # 检查隧道连接
        success, stdout, stderr = self.run_command(f"{self.config['cloudflared_path']} tunnel info {self.config['tunnel_name']}")
        if success:
            status['tunnel_connected'] = True
            # 解析连接信息
            lines = stdout.split('\n')
            for line in lines:
                if 'connections' in line.lower():
                    try:
                        status['connection_count'] = int(line.split()[-1])
                    except:
                        pass
        
        return status
    
    def start_tunnel(self) -> bool:
        """启动隧道"""
        self.log("🚀 启动隧道服务...")
        
        # 检查是否已经运行
        status = self.get_tunnel_status()
        if status['process_running']:
            self.log("隧道已在运行中", "WARNING")
            return True
        
        try:
            # 启动隧道
            cmd = [
                self.config['cloudflared_path'],
                'tunnel',
                '--config', self.config['config_file'],
                'run'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 等待启动
            time.sleep(8)
            
            # 验证启动成功
            if process.poll() is None:
                self.log("隧道启动成功", "SUCCESS")
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"隧道启动失败: {stderr.decode('utf-8', errors='ignore')}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"启动隧道异常: {e}", "ERROR")
            return False
    
    def stop_tunnel(self) -> bool:
        """停止隧道"""
        self.log("🛑 停止隧道服务...")
        
        try:
            # 使用taskkill停止进程
            success, stdout, stderr = self.run_command("taskkill /f /im cloudflared.exe")
            
            if success or "not found" in stderr:
                self.log("隧道已停止", "SUCCESS")
                return True
            else:
                self.log(f"停止隧道失败: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"停止隧道异常: {e}", "ERROR")
            return False
    
    def restart_tunnel(self) -> bool:
        """重启隧道"""
        self.log("🔄 重启隧道服务...")
        
        # 停止隧道
        if not self.stop_tunnel():
            self.log("停止隧道失败,强制继续", "WARNING")
        
        # 等待进程完全停止
        time.sleep(3)
        
        # 启动隧道
        return self.start_tunnel()
    
    def backup_config(self) -> bool:
        """备份配置文件"""
        self.log("💾 备份配置文件...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_files = [
                self.config['config_file'],
                'zero-trust-policies.yml',
                'zero_trust_config.json',
                'wrangler.toml'
            ]
            
            for file_path in backup_files:
                if os.path.exists(file_path):
                    backup_name = f"{os.path.splitext(file_path)[0]}_{timestamp}{os.path.splitext(file_path)[1]}"
                    backup_path = os.path.join(self.config['backup_dir'], backup_name)
                    
                    with open(file_path, 'r', encoding='utf-8') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    
                    self.log(f"已备份: {file_path} -> {backup_path}")
            
            self.log("配置备份完成", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"备份失败: {e}", "ERROR")
            return False
    
    def check_system_health(self) -> Dict:
        """检查系统健康状态"""
        self.log("🏥 检查系统健康状态...")
        
        health = {
            'timestamp': datetime.now().isoformat(),
            'tunnel_status': self.get_tunnel_status(),
            'disk_usage': {},
            'memory_usage': {},
            'network_status': {},
            'log_file_size': 0,
            'config_files_exist': {}
        }
        
        try:
            # 磁盘使用情况
            disk_usage = psutil.disk_usage('.')
            health['disk_usage'] = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': (disk_usage.used / disk_usage.total) * 100
            }
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            health['memory_usage'] = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            }
            
            # 检查配置文件
            config_files = [
                self.config['config_file'],
                'zero-trust-policies.yml',
                'wrangler.toml'
            ]
            
            for file_path in config_files:
                health['config_files_exist'][file_path] = os.path.exists(file_path)
            
            # 日志文件大小
            if os.path.exists(self.config['log_file']):
                health['log_file_size'] = os.path.getsize(self.config['log_file'])
            
        except Exception as e:
            self.log(f"健康检查异常: {e}", "ERROR")
        
        return health
    
    def cleanup_logs(self, days: int = 7) -> bool:
        """清理旧日志文件"""
        self.log(f"🧹 清理 {days} 天前的日志文件...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0
            
            # 查找日志文件
            log_patterns = ['*.log', '*_test_report_*.json', 'zero_trust_*.log']
            
            for pattern in log_patterns:
                import glob
                for file_path in glob.glob(pattern):
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            cleaned_count += 1
                            self.log(f"已删除: {file_path}")
                    except Exception as e:
                        self.log(f"删除文件失败 {file_path}: {e}", "WARNING")
            
            self.log(f"清理完成,删除了 {cleaned_count} 个文件", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"清理日志失败: {e}", "ERROR")
            return False
    
    def start_monitoring(self) -> bool:
        """启动监控服务"""
        self.log("📊 启动监控服务...")
        
        if not os.path.exists(self.config['monitor_script']):
            self.log(f"监控脚本不存在: {self.config['monitor_script']}", "ERROR")
            return False
        
        try:
            # 启动监控脚本
            subprocess.Popen([
                sys.executable,
                self.config['monitor_script']
            ], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            self.log("监控服务已启动", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"启动监控失败: {e}", "ERROR")
            return False
    
    def generate_status_report(self) -> str:
        """生成状态报告"""
        self.log("📋 生成状态报告...")
        
        health = self.check_system_health()
        
        report = f"""
Cloudflare Zero Trust 系统状态报告
生成时间: {health['timestamp']}

隧道状态:
- 进程运行: {'✅' if health['tunnel_status']['process_running'] else '❌'}
- 隧道连接: {'✅' if health['tunnel_status']['tunnel_connected'] else '❌'}
- 运行时间: {health['tunnel_status']['uptime'] or 'N/A'}
- 连接数: {health['tunnel_status']['connection_count']}

系统资源:
- 磁盘使用: {health['disk_usage']['percent']:.1f}%
- 内存使用: {health['memory_usage']['percent']:.1f}%
- 日志文件大小: {health['log_file_size'] / 1024 / 1024:.1f} MB

配置文件:
"""
        
        for file_path, exists in health['config_files_exist'].items():
            report += f"- {file_path}: {'✅' if exists else '❌'}\n"
        
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Cloudflare Zero Trust 管理工具')
    parser.add_argument('action', choices=[
        'status', 'start', 'stop', 'restart', 'backup', 'health', 
        'cleanup', 'monitor', 'report'
    ], help='要执行的操作')
    parser.add_argument('--days', type=int, default=7, help='清理日志的天数(默认7天)')
    
    args = parser.parse_args()
    
    manager = ZeroTrustManager()
    
    try:
        if args.action == 'status':
            status = manager.get_tunnel_status()
            print(f"隧道状态: {'运行中' if status['process_running'] else '已停止'}")
            if status['uptime']:
                print(f"运行时间: {status['uptime']}")
        
        elif args.action == 'start':
            success = manager.start_tunnel()
            sys.exit(0 if success else 1)
        
        elif args.action == 'stop':
            success = manager.stop_tunnel()
            sys.exit(0 if success else 1)
        
        elif args.action == 'restart':
            success = manager.restart_tunnel()
            sys.exit(0 if success else 1)
        
        elif args.action == 'backup':
            success = manager.backup_config()
            sys.exit(0 if success else 1)
        
        elif args.action == 'health':
            health = manager.check_system_health()
            print(json.dumps(health, indent=2, ensure_ascii=False, default=str))
        
        elif args.action == 'cleanup':
            success = manager.cleanup_logs(args.days)
            sys.exit(0 if success else 1)
        
        elif args.action == 'monitor':
            success = manager.start_monitoring()
            sys.exit(0 if success else 1)
        
        elif args.action == 'report':
            report = manager.generate_status_report()
            print(report)
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n操作异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
