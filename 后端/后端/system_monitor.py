#!/usr/bin/env python3
"""
混合交易系统监控和告警系统
监控本地服务,云端服务,网络连接和交易状态
"""

import requests
import psutil
import time
import json
import logging
from datetime import datetime, timedelta
import threading
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.config = {
            # 本地服务配置
            "local_services": {
                "交易API": "http://localhost:5000/health",
                "主API": "http://localhost:8000/health", 
                "交易系统": "http://localhost:8888/health",
                "Agent后端": "http://localhost:9999/health"
            },
            
            # 云端服务配置
            "cloud_services": {
                "云端API": "https://api.aigupiao.me/health",
                "股票数据": "https://api.aigupiao.me/api/stock/quote?symbol=000001",
                "Agent状态": "https://api.aigupiao.me/api/agent/status"
            },
            
            # 监控阈值
            "thresholds": {
                "cpu_percent": 80,
                "memory_percent": 85,
                "disk_percent": 90,
                "response_time": 10,  # 秒
                "error_rate": 0.1     # 10%
            },
            
            # 告警配置
            "alerts": {
                "enabled": True,
                "email": {
                    "enabled": False,  # 需要配置SMTP
                    "smtp_server": "smtp.qq.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_email": ""
                },
                "log_alerts": True,
                "console_alerts": True
            }
        }
        
        self.status_history = []
        self.alert_history = []
        self.running = False
        
    def check_system_resources(self):
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resources = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available": memory.available / (1024**3),  # GB
                "disk_free": disk.free / (1024**3)  # GB
            }
            
            # 检查阈值
            alerts = []
            if cpu_percent > self.config["thresholds"]["cpu_percent"]:
                alerts.append(f"CPU使用率过高: {cpu_percent:.1f}%")
            
            if memory.percent > self.config["thresholds"]["memory_percent"]:
                alerts.append(f"内存使用率过高: {memory.percent:.1f}%")
            
            if disk.percent > self.config["thresholds"]["disk_percent"]:
                alerts.append(f"磁盘使用率过高: {disk.percent:.1f}%")
            
            return resources, alerts
            
        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return None, [f"系统资源检查失败: {e}"]
    
    def check_service_health(self, service_name, url):
        """检查服务健康状态"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=self.config["thresholds"]["response_time"])
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    status = data.get('status', 'unknown')
                except:
                    status = 'responding'
                
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "http_status": response.status_code,
                    "service_status": status
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "http_status": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": "响应超时"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error", 
                "error": "连接失败"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_cloudflare_tunnel(self):
        """检查Cloudflare隧道状态"""
        try:
            from zero_trust_manager import ZeroTrustManager
            manager = ZeroTrustManager()
            tunnel_status = manager.get_tunnel_status()
            
            if tunnel_status.get('tunnel_connected'):
                return {
                    "status": "connected",
                    "uptime": tunnel_status.get('uptime', 'unknown'),
                    "process_running": tunnel_status.get('process_running', False)
                }
            else:
                return {
                    "status": "disconnected",
                    "process_running": tunnel_status.get('process_running', False),
                    "error": "隧道未连接"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"隧道状态检查失败: {e}"
            }
    
    def check_trading_software(self):
        """检查交易软件状态"""
        try:
            # 检查是否有交易软件进程
            trading_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(keyword in proc.info['name'].lower() for keyword in ['trade', '交易', 'stock', '股票']):
                        trading_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name']
                        })
                except:
                    continue
            
            if trading_processes:
                return {
                    "status": "running",
                    "processes": trading_processes,
                    "count": len(trading_processes)
                }
            else:
                return {
                    "status": "not_running",
                    "error": "未检测到交易软件进程"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"交易软件检查失败: {e}"
            }
    
    def send_alert(self, alert_type, message, details=None):
        """发送告警"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "details": details
        }
        
        self.alert_history.append(alert)
        
        # 控制台告警
        if self.config["alerts"]["console_alerts"]:
            print(f"🚨 [{alert_type}] {message}")
            if details:
                print(f"   详情: {details}")
        
        # 日志告警
        if self.config["alerts"]["log_alerts"]:
            logger.warning(f"ALERT [{alert_type}] {message}")
            if details:
                logger.warning(f"ALERT DETAILS: {details}")
        
        # 邮件告警 (如果配置)
        if self.config["alerts"]["email"]["enabled"]:
            self.send_email_alert(alert_type, message, details)
    
    def send_email_alert(self, alert_type, message, details):
        """发送邮件告警 (简化版本)"""
        try:
            # 简化版本:仅记录到日志,实际邮件功能需要额外配置
            logger.warning(f"EMAIL ALERT [{alert_type}] {message}")
            if details:
                logger.warning(f"EMAIL ALERT DETAILS: {json.dumps(details, ensure_ascii=False)}")

        except Exception as e:
            logger.error(f"邮件告警处理失败: {e}")
    
    def run_monitoring_cycle(self):
        """执行一次监控周期"""
        cycle_start = datetime.now()
        status = {
            "timestamp": cycle_start.isoformat(),
            "system_resources": {},
            "local_services": {},
            "cloud_services": {},
            "cloudflare_tunnel": {},
            "trading_software": {},
            "alerts": []
        }
        
        logger.info("🔍 开始监控周期")
        
        # 1. 检查系统资源
        resources, resource_alerts = self.check_system_resources()
        status["system_resources"] = resources
        for alert in resource_alerts:
            self.send_alert("SYSTEM_RESOURCE", alert)
            status["alerts"].append(alert)
        
        # 2. 检查本地服务
        for service_name, url in self.config["local_services"].items():
            service_status = self.check_service_health(service_name, url)
            status["local_services"][service_name] = service_status
            
            if service_status["status"] != "healthy":
                alert_msg = f"{service_name}服务异常: {service_status.get('error', '未知错误')}"
                self.send_alert("LOCAL_SERVICE", alert_msg, service_status)
                status["alerts"].append(alert_msg)
        
        # 3. 检查云端服务
        for service_name, url in self.config["cloud_services"].items():
            service_status = self.check_service_health(service_name, url)
            status["cloud_services"][service_name] = service_status
            
            if service_status["status"] != "healthy":
                alert_msg = f"{service_name}服务异常: {service_status.get('error', '未知错误')}"
                self.send_alert("CLOUD_SERVICE", alert_msg, service_status)
                status["alerts"].append(alert_msg)
        
        # 4. 检查Cloudflare隧道
        tunnel_status = self.check_cloudflare_tunnel()
        status["cloudflare_tunnel"] = tunnel_status
        
        if tunnel_status["status"] != "connected":
            alert_msg = f"Cloudflare隧道异常: {tunnel_status.get('error', '未知错误')}"
            self.send_alert("TUNNEL", alert_msg, tunnel_status)
            status["alerts"].append(alert_msg)
        
        # 5. 检查交易软件
        trading_status = self.check_trading_software()
        status["trading_software"] = trading_status
        
        if trading_status["status"] != "running":
            alert_msg = f"交易软件状态异常: {trading_status.get('error', '未知错误')}"
            self.send_alert("TRADING_SOFTWARE", alert_msg, trading_status)
            status["alerts"].append(alert_msg)
        
        # 保存状态历史
        self.status_history.append(status)
        
        # 保持历史记录在合理范围内 (最近100次)
        if len(self.status_history) > 100:
            self.status_history = self.status_history[-100:]
        
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        logger.info(f"✅ 监控周期完成,耗时: {cycle_duration:.2f}秒,告警数: {len(status['alerts'])}")
        
        return status
    
    def start_monitoring(self, interval=60):
        """启动监控"""
        logger.info(f"🚀 启动系统监控,检查间隔: {interval}秒")
        self.running = True
        
        while self.running:
            try:
                self.run_monitoring_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("👋 监控已停止")
                break
            except Exception as e:
                logger.error(f"监控周期异常: {e}")
                time.sleep(10)  # 异常后短暂等待
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("⏹️ 监控停止请求已发送")
    
    def get_status_report(self):
        """获取状态报告"""
        if not self.status_history:
            return {"error": "暂无监控数据"}
        
        latest_status = self.status_history[-1]
        
        # 计算统计信息
        recent_alerts = [alert for alert in self.alert_history 
                        if datetime.fromisoformat(alert["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        report = {
            "latest_status": latest_status,
            "monitoring_summary": {
                "total_cycles": len(self.status_history),
                "alerts_24h": len(recent_alerts),
                "last_check": latest_status["timestamp"]
            },
            "recent_alerts": recent_alerts[-10:]  # 最近10个告警
        }
        
        return report

def main():
    """主函数"""
    monitor = SystemMonitor()
    
    print("🔧 混合交易系统监控启动")
    print("=" * 50)
    print("监控项目:")
    print("  - 系统资源 (CPU, 内存, 磁盘)")
    print("  - 本地服务 (交易API, 主API, 交易系统, Agent)")
    print("  - 云端服务 (API, 股票数据, Agent状态)")
    print("  - Cloudflare隧道")
    print("  - 交易软件进程")
    print("=" * 50)
    print("按 Ctrl+C 停止监控")
    print()
    
    try:
        # 先执行一次检查
        status = monitor.run_monitoring_cycle()
        
        # 显示初始状态
        print("📊 初始状态检查完成:")
        print(f"  系统资源: CPU {status['system_resources'].get('cpu_percent', 0):.1f}%, "
              f"内存 {status['system_resources'].get('memory_percent', 0):.1f}%")
        print(f"  本地服务: {sum(1 for s in status['local_services'].values() if s['status'] == 'healthy')}/{len(status['local_services'])} 正常")
        print(f"  云端服务: {sum(1 for s in status['cloud_services'].values() if s['status'] == 'healthy')}/{len(status['cloud_services'])} 正常")
        print(f"  隧道状态: {status['cloudflare_tunnel']['status']}")
        print(f"  交易软件: {status['trading_software']['status']}")
        print(f"  告警数量: {len(status['alerts'])}")
        print()
        
        # 启动持续监控
        monitor.start_monitoring(interval=60)
        
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
    except Exception as e:
        print(f"\n❌ 监控启动失败: {e}")

if __name__ == "__main__":
    main()
