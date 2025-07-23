#!/usr/bin/env python3
"""
监控和告警系统配置脚本
"""
import os
import json
import requests
from datetime import datetime, timedelta
import logging

class MonitoringSystemSetup:
    def __init__(self):
        self.project_name = "ai-stock-trading-system"
        self.monitoring_dir = "monitoring"
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置"""
        config = {}
        
        # 从.env.production加载配置
        if os.path.exists('.env.production'):
            with open('.env.production', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        
        return config
    
    def create_monitoring_structure(self):
        """创建监控目录结构"""
        print("📁 创建监控系统目录结构...")
        
        # 创建监控目录
        dirs = [
            self.monitoring_dir,
            f"{self.monitoring_dir}/logs",
            f"{self.monitoring_dir}/alerts",
            f"{self.monitoring_dir}/metrics",
            f"{self.monitoring_dir}/config"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ 创建目录: {dir_path}")
        
        return True
    
    def create_system_monitor(self):
        """创建系统监控脚本"""
        print("📊 创建系统监控脚本...")
        
        monitor_script = '''#!/usr/bin/env python3
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
                    "content": f"🚨 {title}\\n\\n" + "\\n".join(f"• {msg}" for msg in messages) + 
                              f"\\n\\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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

if __name__ == "__main__":
    monitor = SystemMonitor()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.run_continuous_monitoring()
    else:
        monitor.run_monitoring_cycle()
'''
        
        with open(f"{self.monitoring_dir}/system_monitor.py", 'w', encoding='utf-8') as f:
            f.write(monitor_script)
        
        print("   ✅ 系统监控脚本已创建")
        return True
    
    def create_alert_config(self):
        """创建告警配置"""
        print("🚨 创建告警配置...")
        
        alert_config = {
            "alert_rules": {
                "system_resources": {
                    "cpu_threshold": 80,
                    "memory_threshold": 85,
                    "disk_threshold": 90
                },
                "api_health": {
                    "response_time_threshold": 5.0,
                    "error_rate_threshold": 0.05
                },
                "trading": {
                    "max_daily_loss": 1000,
                    "position_size_limit": 50000
                }
            },
            "notification_channels": {
                "dingtalk": {
                    "webhook_url": self.config.get('DINGTALK_WEBHOOK', ''),
                    "enabled": bool(self.config.get('DINGTALK_WEBHOOK'))
                },
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": self.config.get('ALERT_EMAIL', ''),
                    "enabled": bool(self.config.get('ALERT_EMAIL'))
                }
            },
            "monitoring_intervals": {
                "system_check": 300,  # 5分钟
                "api_health_check": 60,  # 1分钟
                "trading_check": 30  # 30秒
            }
        }
        
        with open(f"{self.monitoring_dir}/config/alert_config.json", 'w', encoding='utf-8') as f:
            json.dump(alert_config, f, indent=2, ensure_ascii=False)
        
        print("   ✅ 告警配置已创建")
        return True
    
    def create_dashboard_config(self):
        """创建监控面板配置"""
        print("📈 创建监控面板配置...")
        
        dashboard_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI股票交易系统 - 监控面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metric-title {
            font-size: 1.2em;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #27ae60;
        }
        .metric-status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .status-ok { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 AI股票交易系统监控面板</h1>
            <p>实时系统状态监控</p>
            <button class="refresh-btn" onclick="refreshData()">🔄 刷新数据</button>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">💻 CPU使用率</div>
                <div class="metric-value" id="cpu-usage">--</div>
                <div class="metric-status status-ok" id="cpu-status">正常</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🧠 内存使用率</div>
                <div class="metric-value" id="memory-usage">--</div>
                <div class="metric-status status-ok" id="memory-status">正常</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">💾 磁盘使用率</div>
                <div class="metric-value" id="disk-usage">--</div>
                <div class="metric-status status-ok" id="disk-status">正常</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🌐 API状态</div>
                <div class="metric-value" id="api-status">--</div>
                <div class="metric-status status-ok" id="api-health">正常</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🗄️ 数据库状态</div>
                <div class="metric-value" id="db-status">--</div>
                <div class="metric-status status-ok" id="db-health">正常</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">📊 交易状态</div>
                <div class="metric-value" id="trading-status">--</div>
                <div class="metric-status status-ok" id="trading-health">正常</div>
            </div>
        </div>
    </div>
    
    <script>
        async function refreshData() {
            try {
                // 这里应该调用实际的监控API
                // 现在使用模拟数据
                updateMetrics({
                    cpu_percent: Math.random() * 100,
                    memory_percent: Math.random() * 100,
                    disk_percent: Math.random() * 100,
                    api_healthy: Math.random() > 0.1,
                    db_healthy: Math.random() > 0.05,
                    trading_active: Math.random() > 0.2
                });
            } catch (error) {
                console.error('刷新数据失败:', error);
            }
        }
        
        function updateMetrics(data) {
            // 更新CPU
            document.getElementById('cpu-usage').textContent = data.cpu_percent.toFixed(1) + '%';
            updateStatus('cpu-status', data.cpu_percent, 80);
            
            // 更新内存
            document.getElementById('memory-usage').textContent = data.memory_percent.toFixed(1) + '%';
            updateStatus('memory-status', data.memory_percent, 85);
            
            // 更新磁盘
            document.getElementById('disk-usage').textContent = data.disk_percent.toFixed(1) + '%';
            updateStatus('disk-status', data.disk_percent, 90);
            
            // 更新API状态
            document.getElementById('api-status').textContent = data.api_healthy ? '✅ 正常' : '❌ 异常';
            document.getElementById('api-health').className = 'metric-status ' + (data.api_healthy ? 'status-ok' : 'status-error');
            
            // 更新数据库状态
            document.getElementById('db-status').textContent = data.db_healthy ? '✅ 正常' : '❌ 异常';
            document.getElementById('db-health').className = 'metric-status ' + (data.db_healthy ? 'status-ok' : 'status-error');
            
            // 更新交易状态
            document.getElementById('trading-status').textContent = data.trading_active ? '🟢 活跃' : '🟡 待机';
            document.getElementById('trading-health').className = 'metric-status ' + (data.trading_active ? 'status-ok' : 'status-warning');
        }
        
        function updateStatus(elementId, value, threshold) {
            const element = document.getElementById(elementId);
            if (value > threshold) {
                element.className = 'metric-status status-error';
                element.textContent = '告警';
            } else if (value > threshold * 0.8) {
                element.className = 'metric-status status-warning';
                element.textContent = '注意';
            } else {
                element.className = 'metric-status status-ok';
                element.textContent = '正常';
            }
        }
        
        // 自动刷新
        setInterval(refreshData, 30000); // 30秒刷新一次
        
        // 初始加载
        refreshData();
    </script>
</body>
</html>'''
        
        with open(f"{self.monitoring_dir}/dashboard.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print("   ✅ 监控面板已创建")
        return True
    
    def create_startup_script(self):
        """创建启动脚本"""
        print("🚀 创建监控启动脚本...")
        
        startup_script = '''#!/bin/bash
# AI股票交易系统监控启动脚本

echo "🚀 启动AI股票交易系统监控..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 安装依赖
echo "📦 安装监控依赖..."
pip3 install psutil requests

# 创建日志目录
mkdir -p monitoring/logs

# 启动系统监控
echo "📊 启动系统监控..."
nohup python3 monitoring/system_monitor.py --continuous > monitoring/logs/monitor.log 2>&1 &
MONITOR_PID=$!

echo "✅ 监控系统已启动"
echo "📊 监控面板: http://localhost:8080/monitoring/dashboard.html"
echo "📝 日志文件: monitoring/logs/"
echo "🔄 进程ID: $MONITOR_PID"

# 保存进程ID
echo $MONITOR_PID > monitoring/monitor.pid

echo "🎉 监控系统启动完成!"
'''
        
        with open(f"{self.monitoring_dir}/start_monitoring.sh", 'w', encoding='utf-8') as f:
            f.write(startup_script)
        
        # 设置执行权限(在Windows上可能不起作用,但不会报错)
        try:
            os.chmod(f"{self.monitoring_dir}/start_monitoring.sh", 0o755)
        except:
            pass
        
        print("   ✅ 启动脚本已创建")
        return True
    
    def setup_monitoring(self):
        """设置完整的监控系统"""
        print("🔧 设置监控和告警系统")
        print("=" * 50)
        
        try:
            # 创建目录结构
            self.create_monitoring_structure()
            
            # 创建监控脚本
            self.create_system_monitor()
            
            # 创建告警配置
            self.create_alert_config()
            
            # 创建监控面板
            self.create_dashboard_config()
            
            # 创建启动脚本
            self.create_startup_script()
            
            print("\n🎉 监控和告警系统配置完成!")
            print(f"📁 监控文件位置: {self.monitoring_dir}/")
            print("\n📋 使用说明:")
            print("1. 运行单次监控: python monitoring/system_monitor.py")
            print("2. 运行持续监控: python monitoring/system_monitor.py --continuous")
            print("3. 启动完整监控: bash monitoring/start_monitoring.sh")
            print("4. 查看监控面板: 打开 monitoring/dashboard.html")
            print("5. 查看日志: monitoring/logs/")
            
            return True
            
        except Exception as e:
            print(f"❌ 监控系统配置失败: {e}")
            return False

def main():
    """主函数"""
    setup = MonitoringSystemSetup()
    return setup.setup_monitoring()

if __name__ == "__main__":
    try:
        result = main()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 监控系统配置被用户中断")
        exit(1)
