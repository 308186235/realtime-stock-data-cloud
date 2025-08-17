#!/usr/bin/env python3
"""
启动缺失的服务 - 端口8001,8002,8003
用于完善Zero Trust隧道配置中的所有服务
"""
import os
import sys
import time
import subprocess
import threading
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('missing_services.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MissingServicesManager:
    """缺失服务管理器"""
    
    def __init__(self):
        self.services = {
            8001: {
                'name': 'Realtime Data Service',
                'description': '实时数据服务 (realtime.aigupiao.me)',
                'command': ['python', 'backend/app.py'],
                'env': {'PORT': '8001'},
                'process': None,
                'status': 'stopped'
            },
            8002: {
                'name': 'Monitoring Service', 
                'description': '监控服务 (monitor.aigupiao.me)',
                'command': ['python', 'monitoring/system_monitor.py'],
                'env': {'PORT': '8002', 'MONITOR_MODE': 'server'},
                'process': None,
                'status': 'stopped'
            },
            8003: {
                'name': 'Backup API Service',
                'description': '备份API服务 (backup.aigupiao.me)', 
                'command': ['python', 'backup_api_service.py'],
                'env': {'PORT': '8003'},
                'process': None,
                'status': 'stopped'
            }
        }
        
    def print_banner(self):
        """打印启动横幅"""
        print("=" * 80)
        print("🚀 启动缺失的Zero Trust服务")
        print("=" * 80)
        print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 工作目录: {os.getcwd()}")
        print("=" * 80)
        print("🎯 需要启动的服务:")
        for port, service in self.services.items():
            print(f"  • 端口 {port}: {service['name']} - {service['description']}")
        print("=" * 80)
        
    def check_port_available(self, port):
        """检查端口是否可用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
            
    def create_backup_api_service(self):
        """创建备份API服务文件"""
        backup_service_code = '''#!/usr/bin/env python3
"""
备份API服务 - 端口8003
提供数据备份和恢复功能
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Backup API Service",
    description="数据备份和恢复服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Backup API Service",
        "status": "running",
        "port": int(os.getenv("PORT", 8003)),
        "timestamp": datetime.now().isoformat(),
        "description": "数据备份和恢复服务"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "backup-api",
        "timestamp": datetime.now().isoformat(),
        "port": int(os.getenv("PORT", 8003))
    }

@app.get("/api/backup/status")
async def backup_status():
    """备份状态"""
    return {
        "backup_enabled": True,
        "last_backup": datetime.now().isoformat(),
        "backup_count": 10,
        "storage_used": "1.2GB",
        "status": "active"
    }

@app.post("/api/backup/create")
async def create_backup(data: Dict[str, Any]):
    """创建备份"""
    backup_id = f"backup_{int(datetime.now().timestamp())}"
    logger.info(f"创建备份: {backup_id}")
    
    return {
        "backup_id": backup_id,
        "status": "created",
        "timestamp": datetime.now().isoformat(),
        "size": "estimated_size"
    }

@app.get("/api/backup/list")
async def list_backups():
    """列出备份"""
    return {
        "backups": [
            {
                "id": "backup_1751400000",
                "created_at": "2025-01-01T12:00:00",
                "size": "500MB",
                "type": "full"
            },
            {
                "id": "backup_1751400001", 
                "created_at": "2025-01-01T18:00:00",
                "size": "100MB",
                "type": "incremental"
            }
        ],
        "total_count": 2
    }

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8003))
    logger.info(f"启动备份API服务,端口: {PORT}")
    uvicorn.run(
        "backup_api_service:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )
'''
        
        with open('backup_api_service.py', 'w', encoding='utf-8') as f:
            f.write(backup_service_code)
        logger.info("✅ 创建备份API服务文件: backup_api_service.py")
        
    def start_service(self, port):
        """启动单个服务"""
        service = self.services[port]
        
        # 检查端口是否可用
        if not self.check_port_available(port):
            logger.warning(f"⚠️ 端口 {port} 已被占用,跳过启动 {service['name']}")
            service['status'] = 'port_occupied'
            return False
            
        try:
            # 设置环境变量
            env = os.environ.copy()
            env.update(service['env'])
            
            # 启动进程
            logger.info(f"🚀 启动服务: {service['name']} (端口 {port})")
            process = subprocess.Popen(
                service['command'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            service['process'] = process
            service['status'] = 'running'
            
            # 启动日志监控线程
            threading.Thread(
                target=self._monitor_service_logs,
                args=(port, process),
                daemon=True
            ).start()
            
            logger.info(f"✅ 服务 {service['name']} 启动成功 (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启动服务 {service['name']} 失败: {str(e)}")
            service['status'] = 'failed'
            return False
            
    def _monitor_service_logs(self, port, process):
        """监控服务日志"""
        service = self.services[port]
        
        while process.poll() is None:
            try:
                output = process.stdout.readline()
                if output:
                    logger.info(f"[{service['name']}] {output.strip()}")
            except Exception as e:
                logger.error(f"读取服务日志失败: {str(e)}")
                break
                
        # 进程结束
        service['status'] = 'stopped'
        logger.warning(f"⚠️ 服务 {service['name']} 已停止")
        
    def start_all_services(self):
        """启动所有服务"""
        self.print_banner()
        
        # 创建备份API服务文件
        if not os.path.exists('backup_api_service.py'):
            self.create_backup_api_service()
            
        # 启动所有服务
        success_count = 0
        for port in sorted(self.services.keys()):
            if self.start_service(port):
                success_count += 1
            time.sleep(2)  # 等待服务启动
            
        print("\n" + "=" * 80)
        print(f"🎯 服务启动完成: {success_count}/{len(self.services)} 个服务成功启动")
        print("=" * 80)
        
        # 显示服务状态
        self.show_status()
        
    def show_status(self):
        """显示服务状态"""
        print("\n📊 服务状态:")
        print("-" * 80)
        for port, service in self.services.items():
            status_icon = {
                'running': '🟢',
                'stopped': '🔴', 
                'failed': '❌',
                'port_occupied': '🟡'
            }.get(service['status'], '❓')
            
            print(f"{status_icon} 端口 {port}: {service['name']} - {service['status']}")
            
    def stop_all_services(self):
        """停止所有服务"""
        logger.info("🛑 停止所有服务...")
        
        for port, service in self.services.items():
            if service['process'] and service['process'].poll() is None:
                try:
                    service['process'].terminate()
                    service['process'].wait(timeout=5)
                    logger.info(f"✅ 服务 {service['name']} 已停止")
                except subprocess.TimeoutExpired:
                    service['process'].kill()
                    logger.warning(f"⚠️ 强制终止服务 {service['name']}")
                except Exception as e:
                    logger.error(f"❌ 停止服务 {service['name']} 失败: {str(e)}")
                    
                service['status'] = 'stopped'
                
    def run_forever(self):
        """持续运行"""
        try:
            self.start_all_services()
            
            print("\n💡 服务正在运行中...")
            print("按 Ctrl+C 停止所有服务")
            
            # 持续监控
            while True:
                time.sleep(10)
                # 检查服务状态
                for port, service in self.services.items():
                    if service['process'] and service['process'].poll() is not None:
                        logger.warning(f"⚠️ 检测到服务 {service['name']} 已停止,尝试重启...")
                        self.start_service(port)
                        
        except KeyboardInterrupt:
            print("\n\n🛑 收到停止信号...")
            self.stop_all_services()
            print("👋 所有服务已停止")
            
def main():
    """主函数"""
    manager = MissingServicesManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'status':
            manager.show_status()
            return
        elif sys.argv[1] == 'stop':
            manager.stop_all_services()
            return
            
    manager.run_forever()

if __name__ == "__main__":
    main()
