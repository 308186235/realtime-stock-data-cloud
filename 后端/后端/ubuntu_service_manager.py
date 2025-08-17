#!/usr/bin/env python3
"""
Ubuntu服务管理器
管理阿里云Ubuntu服务器上的交易系统服务
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UbuntuServiceManager:
    """Ubuntu服务管理器"""
    
    def __init__(self):
        self.services = {
            'trading-system': 'trading-system.service',
            'nginx': 'nginx.service',
            'redis': 'redis-server.service'
        }
        
        self.app_path = '/opt/trading-system'
        self.log_path = '/var/log/trading-system'
        self.config_path = f'{self.app_path}/config'
    
    def get_service_status(self, service_name: str) -> Dict:
        """获取服务状态"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'status', service_name],
                capture_output=True, text=True
            )
            
            status_info = {
                'service': service_name,
                'active': 'active (running)' in result.stdout,
                'enabled': self.is_service_enabled(service_name),
                'exit_code': result.returncode,
                'output': result.stdout
            }
            
            return status_info
            
        except Exception as e:
            return {
                'service': service_name,
                'active': False,
                'enabled': False,
                'error': str(e)
            }
    
    def is_service_enabled(self, service_name: str) -> bool:
        """检查服务是否已启用"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'is-enabled', service_name],
                capture_output=True, text=True
            )
            return result.returncode == 0 and 'enabled' in result.stdout
        except:
            return False
    
    def start_service(self, service_name: str) -> bool:
        """启动服务"""
        try:
            logger.info(f"🚀 启动服务: {service_name}")
            subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
            logger.info(f"✅ 服务启动成功: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务启动失败: {service_name} - {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """停止服务"""
        try:
            logger.info(f"⏹️ 停止服务: {service_name}")
            subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)
            logger.info(f"✅ 服务停止成功: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务停止失败: {service_name} - {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """重启服务"""
        try:
            logger.info(f"🔄 重启服务: {service_name}")
            subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
            logger.info(f"✅ 服务重启成功: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务重启失败: {service_name} - {e}")
            return False
    
    def enable_service(self, service_name: str) -> bool:
        """启用服务(开机自启)"""
        try:
            logger.info(f"⚙️ 启用服务: {service_name}")
            subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)
            logger.info(f"✅ 服务启用成功: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务启用失败: {service_name} - {e}")
            return False
    
    def disable_service(self, service_name: str) -> bool:
        """禁用服务"""
        try:
            logger.info(f"⚙️ 禁用服务: {service_name}")
            subprocess.run(['sudo', 'systemctl', 'disable', service_name], check=True)
            logger.info(f"✅ 服务禁用成功: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务禁用失败: {service_name} - {e}")
            return False
    
    def get_all_services_status(self) -> Dict:
        """获取所有服务状态"""
        status_report = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        for service_key, service_name in self.services.items():
            status_report['services'][service_key] = self.get_service_status(service_name)
        
        return status_report
    
    def show_logs(self, service_name: str, lines: int = 50) -> bool:
        """显示服务日志"""
        try:
            logger.info(f"📋 显示服务日志: {service_name} (最近{lines}行)")
            subprocess.run(['sudo', 'journalctl', '-u', service_name, '-n', str(lines)], 
                         check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 获取日志失败: {service_name} - {e}")
            return False
    
    def follow_logs(self, service_name: str) -> bool:
        """实时跟踪服务日志"""
        try:
            logger.info(f"📋 实时跟踪日志: {service_name} (Ctrl+C退出)")
            subprocess.run(['sudo', 'journalctl', '-u', service_name, '-f'], 
                         check=True)
            return True
        except KeyboardInterrupt:
            logger.info("📋 日志跟踪已停止")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 日志跟踪失败: {service_name} - {e}")
            return False
    
    def check_system_health(self) -> Dict:
        """检查系统健康状态"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'services': {},
            'network': {},
            'disk_space': {},
            'overall_health': 'unknown'
        }
        
        try:
            # 系统信息
            import psutil
            health_report['system_info'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg()
            }
            
            # 服务状态
            health_report['services'] = self.get_all_services_status()['services']
            
            # 网络检查
            try:
                import requests
                response = requests.get('http://localhost:8080/api/system/status', 
                                      timeout=5)
                health_report['network']['api_accessible'] = response.status_code == 200
            except:
                health_report['network']['api_accessible'] = False
            
            # 磁盘空间检查
            disk_usage = psutil.disk_usage('/')
            health_report['disk_space'] = {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'percent_used': round((disk_usage.used / disk_usage.total) * 100, 2)
            }
            
            # 整体健康评估
            issues = []
            if health_report['system_info']['cpu_percent'] > 80:
                issues.append('high_cpu')
            if health_report['system_info']['memory_percent'] > 85:
                issues.append('high_memory')
            if health_report['disk_space']['percent_used'] > 90:
                issues.append('low_disk_space')
            if not health_report['network']['api_accessible']:
                issues.append('api_not_accessible')
            
            # 检查关键服务
            for service_key, service_status in health_report['services'].items():
                if not service_status.get('active', False):
                    issues.append(f'{service_key}_not_running')
            
            if not issues:
                health_report['overall_health'] = 'healthy'
            elif len(issues) <= 2:
                health_report['overall_health'] = 'warning'
            else:
                health_report['overall_health'] = 'critical'
            
            health_report['issues'] = issues
            
        except Exception as e:
            health_report['error'] = str(e)
            health_report['overall_health'] = 'error'
        
        return health_report
    
    def backup_configuration(self) -> bool:
        """备份配置文件"""
        try:
            backup_dir = f"{self.app_path}/backups"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{backup_dir}/config_backup_{timestamp}"
            
            # 创建备份目录
            Path(backup_path).mkdir(parents=True, exist_ok=True)
            
            # 备份文件列表
            config_files = [
                '/etc/systemd/system/trading-system.service',
                '/etc/nginx/sites-available/trading-system',
                f'{self.app_path}/aliyun_deployment_config.yml',
                f'{self.app_path}/local_api_config.json'
            ]
            
            import shutil
            for config_file in config_files:
                if Path(config_file).exists():
                    filename = Path(config_file).name
                    shutil.copy2(config_file, f"{backup_path}/{filename}")
                    logger.info(f"📄 备份文件: {config_file}")
            
            # 创建备份信息文件
            backup_info = {
                'backup_time': datetime.now().isoformat(),
                'backup_path': backup_path,
                'files_backed_up': [f for f in config_files if Path(f).exists()]
            }
            
            with open(f"{backup_path}/backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"✅ 配置备份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置备份失败: {e}")
            return False
    
    def update_application(self) -> bool:
        """更新应用程序"""
        try:
            logger.info("🔄 更新应用程序...")
            
            # 停止服务
            self.stop_service('trading-system')
            
            # 备份当前配置
            self.backup_configuration()
            
            # 这里应该是实际的更新逻辑
            # 例如从Git拉取最新代码,或者下载新版本
            logger.info("📦 应用程序更新逻辑需要根据实际情况实现")
            
            # 重启服务
            self.start_service('trading-system')
            
            logger.info("✅ 应用程序更新完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 应用程序更新失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Ubuntu服务管理器')
    parser.add_argument('action', choices=[
        'status', 'start', 'stop', 'restart', 'enable', 'disable',
        'logs', 'follow-logs', 'health', 'backup', 'update'
    ], help='要执行的操作')
    parser.add_argument('--service', '-s', choices=[
        'trading-system', 'nginx', 'redis', 'all'
    ], default='all', help='目标服务')
    parser.add_argument('--lines', '-n', type=int, default=50, 
                       help='显示日志行数')
    
    args = parser.parse_args()
    
    manager = UbuntuServiceManager()
    
    if args.action == 'status':
        if args.service == 'all':
            status = manager.get_all_services_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            service_name = manager.services.get(args.service, args.service)
            status = manager.get_service_status(service_name)
            print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.action == 'health':
        health = manager.check_system_health()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        
        # 简化的健康状态显示
        print(f"\n🏥 系统健康状态: {health['overall_health'].upper()}")
        if health.get('issues'):
            print("⚠️ 发现问题:")
            for issue in health['issues']:
                print(f"   - {issue}")
    
    elif args.action == 'backup':
        success = manager.backup_configuration()
        sys.exit(0 if success else 1)
    
    elif args.action == 'update':
        success = manager.update_application()
        sys.exit(0 if success else 1)
    
    elif args.action in ['start', 'stop', 'restart', 'enable', 'disable']:
        if args.service == 'all':
            success = True
            for service_key, service_name in manager.services.items():
                method = getattr(manager, f'{args.action}_service')
                if not method(service_name):
                    success = False
        else:
            service_name = manager.services.get(args.service, args.service)
            method = getattr(manager, f'{args.action}_service')
            success = method(service_name)
        
        sys.exit(0 if success else 1)
    
    elif args.action == 'logs':
        if args.service == 'all':
            for service_key, service_name in manager.services.items():
                print(f"\n{'='*50}")
                print(f"📋 {service_key} 日志:")
                print('='*50)
                manager.show_logs(service_name, args.lines)
        else:
            service_name = manager.services.get(args.service, args.service)
            manager.show_logs(service_name, args.lines)
    
    elif args.action == 'follow-logs':
        if args.service == 'all':
            print("❌ 实时日志跟踪不支持所有服务,请指定具体服务")
            sys.exit(1)
        else:
            service_name = manager.services.get(args.service, args.service)
            manager.follow_logs(service_name)

if __name__ == "__main__":
    main()
