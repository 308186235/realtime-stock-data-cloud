"""
关键指标监控系统
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import statistics

@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: float
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_points: int = 1000):
        self.metrics: Dict[str, deque] = {}
        self.max_points = max_points
        self.lock = threading.Lock()
        
        # 预定义的关键指标
        self.key_metrics = [
            "trading.orders.total",
            "trading.orders.success_rate",
            "trading.pnl.daily",
            "system.cpu.usage",
            "system.memory.usage",
            "api.requests.count",
            "api.requests.response_time",
            "market_data.latency",
            "database.connections.active",
            "errors.count"
        ]
        
        # 初始化指标存储
        for metric in self.key_metrics:
            self.metrics[metric] = deque(maxlen=max_points)
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """记录指标"""
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = deque(maxlen=self.max_points)
            
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
            
            self.metrics[metric_name].append(point)
    
    def get_metric_stats(self, metric_name: str, time_window: int = 3600) -> Dict[str, Any]:
        """获取指标统计"""
        with self.lock:
            if metric_name not in self.metrics:
                return {}
            
            current_time = time.time()
            window_start = current_time - time_window
            
            # 过滤时间窗口内的数据
            points = [
                p for p in self.metrics[metric_name]
                if p.timestamp >= window_start
            ]
            
            if not points:
                return {}
            
            values = [p.value for p in points]
            
            return {
                "metric_name": metric_name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "median": statistics.median(values),
                "latest": values[-1] if values else 0,
                "time_window": time_window
            }
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """获取所有指标摘要"""
        summary = {}
        
        for metric_name in self.key_metrics:
            stats = self.get_metric_stats(metric_name)
            if stats:
                summary[metric_name] = stats
        
        return summary
    
    def check_metric_thresholds(self) -> List[Dict[str, Any]]:
        """检查指标阈值"""
        alerts = []
        
        # 定义阈值规则
        thresholds = {
            "trading.orders.success_rate": {"min": 0.8, "type": "min"},
            "system.cpu.usage": {"max": 0.8, "type": "max"},
            "system.memory.usage": {"max": 0.9, "type": "max"},
            "api.requests.response_time": {"max": 5000, "type": "max"},
            "market_data.latency": {"max": 1000, "type": "max"},
            "errors.count": {"max": 10, "type": "max"}
        }
        
        for metric_name, threshold in thresholds.items():
            stats = self.get_metric_stats(metric_name, 300)  # 5分钟窗口
            
            if not stats:
                continue
            
            if threshold["type"] == "max" and stats["latest"] > threshold["max"]:
                alerts.append({
                    "metric": metric_name,
                    "type": "threshold_exceeded",
                    "current_value": stats["latest"],
                    "threshold": threshold["max"],
                    "severity": "high"
                })
            elif threshold["type"] == "min" and stats["latest"] < threshold["min"]:
                alerts.append({
                    "metric": metric_name,
                    "type": "threshold_below",
                    "current_value": stats["latest"],
                    "threshold": threshold["min"],
                    "severity": "high"
                })
        
        return alerts

class SystemMetricsCollector:
    """系统指标收集器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.running = False
        self.collection_thread = None
    
    def start_collection(self, interval: int = 60):
        """开始收集系统指标"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collect_loop,
            args=(interval,),
            daemon=True
        )
        self.collection_thread.start()
    
    def stop_collection(self):
        """停止收集"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
    
    def _collect_loop(self, interval: int):
        """收集循环"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                print(f"系统指标收集错误: {e}")
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        import psutil
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.record_metric("system.cpu.usage", cpu_percent / 100)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.metrics_collector.record_metric("system.memory.usage", memory.percent / 100)
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        self.metrics_collector.record_metric("system.disk.usage", disk.percent / 100)
        
        # 网络IO
        net_io = psutil.net_io_counters()
        self.metrics_collector.record_metric("system.network.bytes_sent", net_io.bytes_sent)
        self.metrics_collector.record_metric("system.network.bytes_recv", net_io.bytes_recv)

# 全局指标收集器
metrics_collector = MetricsCollector()
system_metrics_collector = SystemMetricsCollector(metrics_collector)

# 便捷函数
def record_trading_metric(metric_name: str, value: float, tags: Optional[Dict] = None):
    """记录交易指标"""
    metrics_collector.record_metric(f"trading.{metric_name}", value, tags)

def record_api_metric(metric_name: str, value: float, tags: Optional[Dict] = None):
    """记录API指标"""
    metrics_collector.record_metric(f"api.{metric_name}", value, tags)

def record_system_metric(metric_name: str, value: float, tags: Optional[Dict] = None):
    """记录系统指标"""
    metrics_collector.record_metric(f"system.{metric_name}", value, tags)
