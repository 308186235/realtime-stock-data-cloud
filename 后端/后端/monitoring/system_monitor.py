#!/usr/bin/env python3
"""
AI股票交易系统监控脚本
"""
import psutil
import requests
import json
import time
import logging
from datetime import datetime
import os

class SystemMonitor:
    def __init__(self):
        self.api_endpoint = "http://localhost:8000"
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.alert_webhook = os.getenv('DINGTALK_WEBHOOK', '')
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring/logs/system_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_system_resources(self):
        """检查系统资源"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # 检查告警阈值
            alerts = []
            if cpu_percent > 80:
                alerts.append(f"CPU使用率过高: {cpu_percent:.1f}%")
            if memory_percent > 85:
                alerts.append(f"内存使用率过高: {memory_percent:.1f}%")
            if disk_percent > 90:
                alerts.append(f"磁盘使用率过高: {disk_percent:.1f}%")
            
            if alerts:
                self.send_alert("系统资源告警", alerts)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"系统资源检查失败: {e}")
            return None
    
    def check_api_health(self):
        """检查API健康状态"""
        try:
            # 检查主API
            response = requests.get(f"{self.api_endpoint}/api/health", timeout=10)
            api_healthy = response.status_code == 200
            
            # 检查Supabase连接
            supabase_healthy = False
            if self.supabase_url:
                try:
                    supabase_response = requests.get(f"{self.supabase_url}/rest/v1/", timeout=10)
                    supabase_healthy = supabase_response.status_code in [200, 401]  # 401是正常的,表示需要认证
                except:
                    pass
            
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'api_healthy': api_healthy,
                'supabase_healthy': supabase_healthy,
                'api_response_time': response.elapsed.total_seconds() if api_healthy else None
            }
            
            # 检查告警
            if not api_healthy:
                self.send_alert("API服务异常", ["主API服务无响应"])
            if not supabase_healthy:
                self.send_alert("数据库连接异常", ["Supabase连接失败"])
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"API健康检查失败: {e}")
            self.send_alert("监控系统异常", [f"API健康检查失败: {e}"])
            return None
    
    def send_alert(self, title, messages):
        """发送告警通知"""
        if not self.alert_webhook:
            self.logger.warning("未配置告警Webhook,跳过告警发送")
            return
        
        try:
            alert_data = {
                "msgtype": "text",
                "text": {
                    "content": f"🚨 {title}\n\n" + "\n".join(f"• {msg}" for msg in messages) + 
                              f"\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            response = requests.post(self.alert_webhook, json=alert_data, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"告警发送成功: {title}")
            else:
                self.logger.error(f"告警发送失败: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"发送告警失败: {e}")
    
    def save_metrics(self, metrics):
        """保存监控指标"""
        try:
            metrics_file = f"monitoring/metrics/metrics_{datetime.now().strftime('%Y%m%d')}.json"
            
            # 读取现有数据
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # 添加新指标
            data.append(metrics)
            
            # 保存数据
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存监控指标失败: {e}")
    
    def run_monitoring_cycle(self):
        """运行一次监控周期"""
        self.logger.info("开始监控周期")
        
        # 检查系统资源
        system_metrics = self.check_system_resources()
        if system_metrics:
            self.save_metrics({'type': 'system', **system_metrics})
        
        # 检查API健康状态
        health_metrics = self.check_api_health()
        if health_metrics:
            self.save_metrics({'type': 'health', **health_metrics})
        
        self.logger.info("监控周期完成")
    
    def run_continuous_monitoring(self, interval=300):
        """运行持续监控"""
        self.logger.info(f"开始持续监控,间隔: {interval}秒")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("监控被用户中断")
        except Exception as e:
            self.logger.error(f"监控过程中发生错误: {e}")

def create_monitoring_server():
    """创建监控服务器"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import os
    import threading

    app = FastAPI(
        title="System Monitoring Service",
        description="系统监控服务",
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

    # 创建监控实例
    monitor = SystemMonitor()

    @app.on_event("startup")
    async def startup_event():
        """启动时开始监控"""
        threading.Thread(target=monitor.run_continuous_monitoring, daemon=True).start()

    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": "System Monitoring Service",
            "status": "running",
            "port": int(os.getenv("PORT", 8002)),
            "timestamp": datetime.now().isoformat(),
            "description": "系统监控服务"
        }

    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": "monitoring",
            "timestamp": datetime.now().isoformat(),
            "port": int(os.getenv("PORT", 8002))
        }

    @app.get("/api/metrics/current")
    async def get_current_metrics():
        """获取当前系统指标"""
        return monitor.get_current_metrics()

    @app.get("/api/metrics/history")
    async def get_metrics_history():
        """获取历史指标"""
        try:
            with open(monitor.metrics_file, 'r', encoding='utf-8') as f:
                return {"metrics": [json.loads(line) for line in f.readlines()[-100:]]}
        except Exception as e:
            return {"error": str(e), "metrics": []}

    return app

if __name__ == "__main__":
    # 检查是否以服务器模式运行
    if os.getenv("MONITOR_MODE") == "server":
        # 服务器模式
        app = create_monitoring_server()
        PORT = int(os.getenv("PORT", 8002))
        print(f"🚀 启动监控服务器,端口: {PORT}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=PORT,
            log_level="info",
            access_log=True
        )
    else:
        # 命令行模式
        monitor = SystemMonitor()

        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
            monitor.run_continuous_monitoring()
        else:
            monitor.run_monitoring_cycle()
