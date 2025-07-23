"""
增强性能监控器
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int
    active_threads: int
    
class EnhancedPerformanceMonitor:
    """增强性能监控器"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.monitoring = False
        self.monitor_thread = None
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_mb': 500.0,
            'response_time': 2000.0
        }
        self.alert_callbacks = []
    
    def start_monitoring(self, interval=1.0):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self, interval):
        """监控循环"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._check_alerts(metrics)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"性能监控错误: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        process = psutil.Process()
        
        # CPU和内存
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # 磁盘IO
        disk_io = process.io_counters()
        disk_io_read = disk_io.read_bytes if disk_io else 0
        disk_io_write = disk_io.write_bytes if disk_io else 0
        
        # 网络IO(系统级别)
        net_io = psutil.net_io_counters()
        network_sent = net_io.bytes_sent if net_io else 0
        network_recv = net_io.bytes_recv if net_io else 0
        
        # 线程数
        active_threads = process.num_threads()
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_io_read=disk_io_read,
            disk_io_write=disk_io_write,
            network_sent=network_sent,
            network_recv=network_recv,
            active_threads=active_threads
        )
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"内存使用率过高: {metrics.memory_percent:.1f}%")
        
        if metrics.memory_mb > self.alert_thresholds['memory_mb']:
            alerts.append(f"内存使用量过高: {metrics.memory_mb:.1f}MB")
        
        for alert in alerts:
            logger.warning(f"性能告警: {alert}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metrics)
                except Exception as e:
                    logger.error(f"告警回调失败: {e}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_average_metrics(self, last_n=60) -> Dict:
        """获取平均指标"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-last_n:]
        
        return {
            'avg_cpu': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory_mb': sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            'avg_threads': sum(m.active_threads for m in recent_metrics) / len(recent_metrics)
        }

# 全局性能监控器
enhanced_monitor = EnhancedPerformanceMonitor()
