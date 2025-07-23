#!/usr/bin/env python3
"""
Ubuntu云服务器部署脚本
专门针对阿里云Ubuntu系统的混合交易系统部署
"""

import os
import sys
import json
import yaml
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ubuntu_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UbuntuCloudDeployer:
    """Ubuntu云服务器部署器"""
    
    def __init__(self):
        self.config = self.load_config()
        self.deployment_info = {
            'start_time': datetime.now(),
            'os_info': self.get_os_info(),
            'steps_completed': [],
            'steps_failed': []
        }
    
    def load_config(self) -> Dict:
        """加载部署配置"""
        try:
            with open('aliyun_deployment_config.yml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info("✅ 配置文件加载成功")
            return config
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            sys.exit(1)
    
    def get_os_info(self) -> Dict:
        """获取操作系统信息"""
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = f.read()
            
            os_info = {}
            for line in os_release.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os_info[key] = value.strip('"')
            
            # 获取系统资源信息
            import psutil
            os_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
            })
            
            logger.info(f"✅ 系统信息: {os_info.get('PRETTY_NAME', 'Ubuntu')}")
            return os_info
            
        except Exception as e:
            logger.error(f"❌ 获取系统信息失败: {e}")
            return {'error': str(e)}
    
    def update_system(self) -> bool:
        """更新系统包"""
        logger.info("🔄 更新系统包...")
        
        try:
            # 更新包列表
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            logger.info("✅ 包列表更新完成")
            
            # 升级系统包
            subprocess.run(['sudo', 'apt', 'upgrade', '-y'], check=True)
            logger.info("✅ 系统包升级完成")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 系统更新失败: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """安装系统依赖"""
        logger.info("📦 安装系统依赖...")
        
        try:
            # 基础包
            base_packages = [
                'python3.11',
                'python3.11-venv',
                'python3-pip',
                'nginx',
                'supervisor',
                'redis-server',
                'mysql-client',
                'curl',
                'wget',
                'git',
                'htop',
                'vim',
                'unzip',
                'build-essential',
                'libssl-dev',
                'libffi-dev',
                'python3.11-dev'
            ]
            
            logger.info(f"📦 安装基础包: {', '.join(base_packages)}")
            subprocess.run(['sudo', 'apt', 'install', '-y'] + base_packages, check=True)
            
            # 设置Python3.11为默认python3
            subprocess.run(['sudo', 'update-alternatives', '--install', 
                          '/usr/bin/python3', 'python3', '/usr/bin/python3.11', '1'], 
                         check=True)
            
            # 安装pip包
            pip_packages = [
                'fastapi>=0.104.0',
                'uvicorn[standard]>=0.24.0',
                'aiohttp>=3.9.0',
                'requests>=2.31.0',
                'pandas>=2.1.0',
                'numpy>=1.24.0',
                'pyyaml>=6.0',
                'python-multipart>=0.0.6',
                'psutil>=5.9.0',
                'redis>=5.0.0',
                'pymysql>=1.1.0',
                'cryptography>=41.0.0',
                'python-jose[cryptography]>=3.3.0'
            ]
            
            logger.info("📦 安装Python包...")
            subprocess.run(['pip3', 'install', '--upgrade', 'pip'], check=True)
            subprocess.run(['pip3', 'install'] + pip_packages, check=True)
            
            logger.info("✅ 依赖安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 依赖安装失败: {e}")
            return False
    
    def setup_application_directories(self) -> bool:
        """设置应用目录结构"""
        logger.info("📁 设置应用目录...")
        
        try:
            app_config = self.config['application']['cloud_api']
            
            directories = [
                app_config['app_path'],
                app_config['log_path'],
                app_config['pid_path'],
                '/opt/trading-system/config',
                '/opt/trading-system/data',
                '/opt/trading-system/backups',
                '/opt/trading-system/scripts'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                # 设置适当的权限
                subprocess.run(['sudo', 'chown', '-R', 'ubuntu:ubuntu', directory], 
                             check=True)
                logger.info(f"📁 创建目录: {directory}")
            
            logger.info("✅ 应用目录设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 目录设置失败: {e}")
            return False
    
    def deploy_application_code(self) -> bool:
        """部署应用代码"""
        logger.info("🚀 部署应用代码...")
        
        try:
            app_path = self.config['application']['cloud_api']['app_path']
            
            # 复制应用文件
            application_files = [
                'aliyun_hybrid_implementation.py',
                'aliyun_deployment_config.yml'
            ]
            
            for file_name in application_files:
                if Path(file_name).exists():
                    import shutil
                    target_path = Path(app_path) / file_name
                    shutil.copy2(file_name, target_path)
                    logger.info(f"📄 复制文件: {file_name} -> {target_path}")
            
            # 创建Ubuntu专用的启动脚本
            startup_script = f"""#!/bin/bash
# Ubuntu云服务器启动脚本

set -e

APP_PATH="{app_path}"
LOG_PATH="{self.config['application']['cloud_api']['log_path']}"
PID_PATH="{self.config['application']['cloud_api']['pid_path']}"

echo "🚀 启动阿里云混合交易系统 (Ubuntu)"

# 切换到应用目录
cd $APP_PATH

# 设置环境变量
export PYTHONPATH=$APP_PATH:$PYTHONPATH
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"

# 启动应用
echo "📡 启动API服务器..."
uvicorn aliyun_hybrid_implementation:app \\
    --host 0.0.0.0 \\
    --port 8080 \\
    --workers 4 \\
    --log-level info \\
    --access-log \\
    --log-config logging.conf \\
    --pid-file $PID_PATH/app.pid \\
    --daemon

echo "✅ 系统启动完成"
echo "📊 API文档: http://localhost:8080/docs"
echo "🔍 健康检查: http://localhost:8080/api/system/status"
"""
            
            with open(f"{app_path}/start.sh", 'w') as f:
                f.write(startup_script)
            
            # 设置执行权限
            os.chmod(f"{app_path}/start.sh", 0o755)
            
            logger.info("✅ 应用代码部署完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 应用部署失败: {e}")
            return False
    
    def configure_nginx(self) -> bool:
        """配置Nginx反向代理"""
        logger.info("🌐 配置Nginx...")
        
        try:
            nginx_config = f"""
server {{
    listen 80;
    listen 443 ssl http2;
    server_name _;
    
    # SSL配置 (如果有证书)
    # ssl_certificate /etc/ssl/certs/trading-system.crt;
    # ssl_certificate_key /etc/ssl/private/trading-system.key;
    
    # 日志配置
    access_log {self.config['application']['cloud_api']['log_path']}/nginx_access.log;
    error_log {self.config['application']['cloud_api']['log_path']}/nginx_error.log;
    
    # API代理
    location /api/ {{
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }}
    
    # 健康检查
    location /health {{
        proxy_pass http://127.0.0.1:8080/api/system/status;
        access_log off;
    }}
    
    # 静态文件 (如果有前端)
    location / {{
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }}
}}
"""
            
            # 写入Nginx配置
            with open('/tmp/trading-system.conf', 'w') as f:
                f.write(nginx_config)
            
            # 移动到Nginx配置目录
            subprocess.run(['sudo', 'mv', '/tmp/trading-system.conf', 
                          '/etc/nginx/sites-available/trading-system'], check=True)
            
            # 启用站点
            subprocess.run(['sudo', 'ln', '-sf', 
                          '/etc/nginx/sites-available/trading-system',
                          '/etc/nginx/sites-enabled/trading-system'], check=True)
            
            # 删除默认站点
            subprocess.run(['sudo', 'rm', '-f', '/etc/nginx/sites-enabled/default'], 
                         check=False)
            
            # 测试Nginx配置
            subprocess.run(['sudo', 'nginx', '-t'], check=True)
            
            # 重启Nginx
            subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'nginx'], check=True)
            
            logger.info("✅ Nginx配置完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Nginx配置失败: {e}")
            return False
    
    def configure_systemd_service(self) -> bool:
        """配置systemd服务"""
        logger.info("⚙️ 配置systemd服务...")
        
        try:
            app_path = self.config['application']['cloud_api']['app_path']
            log_path = self.config['application']['cloud_api']['log_path']
            
            service_config = f"""[Unit]
Description=Trading System Cloud API
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory={app_path}
Environment=PYTHONPATH={app_path}
Environment=ENVIRONMENT=production
ExecStart={app_path}/start.sh
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

# 日志配置
StandardOutput=append:{log_path}/service.log
StandardError=append:{log_path}/service_error.log

[Install]
WantedBy=multi-user.target
"""
            
            # 写入systemd服务文件
            with open('/tmp/trading-system.service', 'w') as f:
                f.write(service_config)
            
            # 移动到systemd目录
            subprocess.run(['sudo', 'mv', '/tmp/trading-system.service', 
                          '/etc/systemd/system/trading-system.service'], check=True)
            
            # 重新加载systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            # 启用服务
            subprocess.run(['sudo', 'systemctl', 'enable', 'trading-system'], check=True)
            
            logger.info("✅ systemd服务配置完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ systemd服务配置失败: {e}")
            return False
    
    def configure_firewall(self) -> bool:
        """配置防火墙"""
        logger.info("🔥 配置防火墙...")
        
        try:
            # 启用UFW
            subprocess.run(['sudo', 'ufw', '--force', 'enable'], check=True)
            
            # 允许SSH
            subprocess.run(['sudo', 'ufw', 'allow', 'ssh'], check=True)
            
            # 允许HTTP和HTTPS
            subprocess.run(['sudo', 'ufw', 'allow', 'http'], check=True)
            subprocess.run(['sudo', 'ufw', 'allow', 'https'], check=True)
            
            # 允许API端口
            subprocess.run(['sudo', 'ufw', 'allow', '8080'], check=True)
            
            # 显示防火墙状态
            result = subprocess.run(['sudo', 'ufw', 'status'], 
                                  capture_output=True, text=True)
            logger.info(f"🔥 防火墙状态:\n{result.stdout}")
            
            logger.info("✅ 防火墙配置完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 防火墙配置失败: {e}")
            return False
    
    def start_services(self) -> bool:
        """启动服务"""
        logger.info("🚀 启动服务...")
        
        try:
            # 启动Redis
            subprocess.run(['sudo', 'systemctl', 'start', 'redis-server'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'redis-server'], check=True)
            
            # 启动交易系统服务
            subprocess.run(['sudo', 'systemctl', 'start', 'trading-system'], check=True)
            
            # 等待服务启动
            import time
            time.sleep(5)
            
            # 检查服务状态
            result = subprocess.run(['sudo', 'systemctl', 'status', 'trading-system'], 
                                  capture_output=True, text=True)
            
            if 'active (running)' in result.stdout:
                logger.info("✅ 交易系统服务启动成功")
            else:
                logger.warning(f"⚠️ 服务状态: {result.stdout}")
            
            logger.info("✅ 服务启动完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 服务启动失败: {e}")
            return False
    
    def test_deployment(self) -> bool:
        """测试部署"""
        logger.info("🧪 测试部署...")
        
        try:
            import requests
            import time
            
            # 等待服务完全启动
            time.sleep(10)
            
            test_results = {}
            
            # 测试本地API
            try:
                response = requests.get('http://localhost:8080/api/system/status', 
                                      timeout=10)
                test_results['local_api'] = response.status_code == 200
                logger.info(f"✅ 本地API测试: {response.status_code}")
            except Exception as e:
                test_results['local_api'] = False
                logger.error(f"❌ 本地API测试失败: {e}")
            
            # 测试Nginx代理
            try:
                response = requests.get('http://localhost/health', timeout=10)
                test_results['nginx_proxy'] = response.status_code == 200
                logger.info(f"✅ Nginx代理测试: {response.status_code}")
            except Exception as e:
                test_results['nginx_proxy'] = False
                logger.error(f"❌ Nginx代理测试失败: {e}")
            
            # 测试Redis连接
            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0)
                r.ping()
                test_results['redis'] = True
                logger.info("✅ Redis连接测试通过")
            except Exception as e:
                test_results['redis'] = False
                logger.error(f"❌ Redis连接测试失败: {e}")
            
            # 保存测试结果
            with open('/opt/trading-system/deployment_test_results.json', 'w') as f:
                json.dump({
                    'test_time': datetime.now().isoformat(),
                    'results': test_results,
                    'overall_success': all(test_results.values())
                }, f, indent=2)
            
            success = all(test_results.values())
            if success:
                logger.info("✅ 所有测试通过")
            else:
                logger.warning("⚠️ 部分测试失败")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 部署测试失败: {e}")
            return False
    
    def generate_deployment_summary(self):
        """生成部署摘要"""
        logger.info("📊 生成部署摘要...")
        
        end_time = datetime.now()
        duration = end_time - self.deployment_info['start_time']
        
        summary = {
            'deployment_info': {
                'start_time': self.deployment_info['start_time'].isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': round(duration.total_seconds() / 60, 2),
                'os_info': self.deployment_info['os_info']
            },
            'completed_steps': self.deployment_info['steps_completed'],
            'failed_steps': self.deployment_info['steps_failed'],
            'service_endpoints': {
                'api_docs': 'http://your-server-ip/api/docs',
                'health_check': 'http://your-server-ip/health',
                'system_status': 'http://your-server-ip/api/system/status'
            },
            'next_steps': [
                "1. 配置域名和SSL证书",
                "2. 设置数据库连接",
                "3. 配置本地API连接",
                "4. 测试完整的交易流程",
                "5. 设置监控和告警"
            ]
        }
        
        with open('/opt/trading-system/ubuntu_deployment_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        print("\n" + "="*60)
        print("📊 Ubuntu云服务器部署摘要")
        print("="*60)
        print(f"⏱️  部署时长: {duration}")
        print(f"✅ 成功步骤: {len(self.deployment_info['steps_completed'])}")
        print(f"❌ 失败步骤: {len(self.deployment_info['steps_failed'])}")
        print(f"🖥️  系统信息: {self.deployment_info['os_info'].get('PRETTY_NAME', 'Ubuntu')}")
        print("\n🌐 服务端点:")
        for name, url in summary['service_endpoints'].items():
            print(f"   {name}: {url}")
        print("\n📋 后续步骤:")
        for step in summary['next_steps']:
            print(f"   {step}")
        print("="*60)
    
    def deploy(self) -> bool:
        """执行完整部署"""
        logger.info("🚀 开始Ubuntu云服务器部署")
        
        deployment_steps = [
            ("更新系统", self.update_system),
            ("安装依赖", self.install_dependencies),
            ("设置目录", self.setup_application_directories),
            ("部署代码", self.deploy_application_code),
            ("配置Nginx", self.configure_nginx),
            ("配置服务", self.configure_systemd_service),
            ("配置防火墙", self.configure_firewall),
            ("启动服务", self.start_services),
            ("测试部署", self.test_deployment)
        ]
        
        success = True
        for step_name, step_func in deployment_steps:
            logger.info(f"🔄 执行步骤: {step_name}")
            if step_func():
                self.deployment_info['steps_completed'].append(step_name)
                logger.info(f"✅ 步骤完成: {step_name}")
            else:
                self.deployment_info['steps_failed'].append(step_name)
                logger.error(f"❌ 步骤失败: {step_name}")
                success = False
                break
        
        self.generate_deployment_summary()
        
        if success:
            logger.info("🎉 Ubuntu云服务器部署成功!")
        else:
            logger.error("💥 部署过程中出现错误")
        
        return success

def main():
    """主函数"""
    print("🚀 阿里云Ubuntu服务器自动化部署")
    print("="*50)
    
    # 检查是否为Ubuntu系统
    try:
        with open('/etc/os-release', 'r') as f:
            os_release = f.read()
        if 'ubuntu' not in os_release.lower():
            print("❌ 此脚本仅适用于Ubuntu系统")
            return 1
    except:
        print("❌ 无法检测操作系统")
        return 1
    
    deployer = UbuntuCloudDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n🎉 部署完成!")
        print("📊 查看详细报告: /opt/trading-system/ubuntu_deployment_summary.json")
        print("📋 查看日志: ubuntu_deployment.log")
    else:
        print("\n💥 部署失败!")
        print("📋 查看错误日志: ubuntu_deployment.log")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
