"""
实时股票系统性能监控和自动优化
"""
import asyncio
import time
import logging
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import json
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    network_sent_mb: float
    network_recv_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    active_connections: int
    request_rate: float
    error_rate: float
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '=='
    duration: int  # 持续时间(秒)
    severity: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        # 配置
        self.monitor_interval = 5  # 5秒监控间隔
        self.metrics_retention = 3600  # 保留1小时数据
        self.alert_cooldown = 300  # 5分钟告警冷却
        
        # 数据存储
        self.metrics_history: deque = deque(maxlen=self.metrics_retention // self.monitor_interval)
        self.response_times: deque = deque(maxlen=1000)
        self.request_counts: deque = deque(maxlen=60)  # 1分钟窗口
        self.error_counts: deque = deque(maxlen=60)
        
        # 告警管理
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_callbacks: List[Callable] = []
        
        # 运行状态
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        
        # 性能统计
        self.stats = {
            'monitor_start_time': 0,
            'total_requests': 0,
            'total_errors': 0,
            'avg_response_time': 0,
            'peak_cpu': 0,
            'peak_memory': 0,
            'alerts_triggered': 0
        }
        
        # 初始化默认告警规则
        self._init_default_alert_rules()
    
    def _init_default_alert_rules(self):
        """初始化默认告警规则"""
        default_rules = [
            AlertRule('高CPU使用率', 'cpu_percent', 80.0, '>', 60, 'high'),
            AlertRule('高内存使用率', 'memory_percent', 85.0, '>', 60, 'high'),
            AlertRule('高错误率', 'error_rate', 5.0, '>', 30, 'medium'),
            AlertRule('响应时间过长', 'response_time_avg', 2000.0, '>', 30, 'medium'),
            AlertRule('连接数过多', 'active_connections', 1000, '>', 60, 'low'),
            AlertRule('极高CPU使用率', 'cpu_percent', 95.0, '>', 30, 'critical'),
            AlertRule('极高内存使用率', 'memory_percent', 95.0, '>', 30, 'critical')
        ]
        self.alert_rules.extend(default_rules)
    
    async def start(self):
        """启动性能监控"""
        try:
            logger.info("启动性能监控器...")
            
            self.running = True
            self.stats['monitor_start_time'] = time.time()
            
            # 启动监控任务
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            
            # 启动自动优化任务
            self.optimization_task = asyncio.create_task(self._optimization_loop())
            
            logger.info("性能监控器启动成功")
            
        except Exception as e:
            logger.error(f"启动性能监控器失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止性能监控"""
        logger.info("停止性能监控器...")
        
        self.running = False
        
        # 取消任务
        if self.monitor_task:
            self.monitor_task.cancel()
        if self.optimization_task:
            self.optimization_task.cancel()
        
        logger.info("性能监控器已停止")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 收集性能指标
                metrics = await self._collect_metrics()
                
                # 存储指标
                self.metrics_history.append(metrics)
                
                # 检查告警
                await self._check_alerts(metrics)
                
                # 更新统计
                self._update_stats(metrics)
                
                # 等待下一个监控周期
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"监控循环错误: {str(e)}")
                await asyncio.sleep(1)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        try:
            # 系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            disk = psutil.disk_io_counters()
            
            # 应用指标
            current_time = time.time()
            
            # 计算请求速率
            recent_requests = [count for count in self.request_counts if count > current_time - 60]
            request_rate = len(recent_requests)
            
            # 计算错误率
            recent_errors = [count for count in self.error_counts if count > current_time - 60]
            error_rate = (len(recent_errors) / max(len(recent_requests), 1)) * 100
            
            # 计算响应时间统计
            recent_response_times = list(self.response_times)
            response_time_avg = statistics.mean(recent_response_times) if recent_response_times else 0
            response_time_p95 = statistics.quantiles(recent_response_times, n=20)[18] if len(recent_response_times) > 20 else 0
            response_time_p99 = statistics.quantiles(recent_response_times, n=100)[98] if len(recent_response_times) > 100 else 0
            
            return PerformanceMetrics(
                timestamp=current_time,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                network_sent_mb=network.bytes_sent / 1024 / 1024,
                network_recv_mb=network.bytes_recv / 1024 / 1024,
                disk_io_read_mb=disk.read_bytes / 1024 / 1024 if disk else 0,
                disk_io_write_mb=disk.write_bytes / 1024 / 1024 if disk else 0,
                active_connections=0,  # 需要从应用获取
                request_rate=request_rate,
                error_rate=error_rate,
                response_time_avg=response_time_avg,
                response_time_p95=response_time_p95,
                response_time_p99=response_time_p99
            )
            
        except Exception as e:
            logger.error(f"收集性能指标失败: {str(e)}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=0, memory_percent=0, memory_used_mb=0,
                network_sent_mb=0, network_recv_mb=0,
                disk_io_read_mb=0, disk_io_write_mb=0,
                active_connections=0, request_rate=0, error_rate=0,
                response_time_avg=0, response_time_p95=0, response_time_p99=0
            )
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警规则"""
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # 获取指标值
            metric_value = getattr(metrics, rule.metric, 0)
            
            # 检查阈值
            triggered = False
            if rule.operator == '>':
                triggered = metric_value > rule.threshold
            elif rule.operator == '<':
                triggered = metric_value < rule.threshold
            elif rule.operator == '>=':
                triggered = metric_value >= rule.threshold
            elif rule.operator == '<=':
                triggered = metric_value <= rule.threshold
            elif rule.operator == '==':
                triggered = metric_value == rule.threshold
            
            if triggered:
                # 检查是否在冷却期
                if rule.name in self.active_alerts:
                    last_alert = self.active_alerts[rule.name]
                    if (current_time - last_alert).total_seconds() < self.alert_cooldown:
                        continue
                
                # 触发告警
                await self._trigger_alert(rule, metric_value, metrics)
                self.active_alerts[rule.name] = current_time
                self.stats['alerts_triggered'] += 1
    
    async def _trigger_alert(self, rule: AlertRule, value: float, metrics: PerformanceMetrics):
        """触发告警"""
        alert_data = {
            'rule_name': rule.name,
            'metric': rule.metric,
            'current_value': value,
            'threshold': rule.threshold,
            'severity': rule.severity,
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(metrics)
        }
        
        logger.warning(f"告警触发: {rule.name} - {rule.metric}={value} {rule.operator} {rule.threshold}")
        
        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                logger.error(f"告警回调执行失败: {str(e)}")
    
    async def _optimization_loop(self):
        """自动优化循环"""
        while self.running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                if len(self.metrics_history) < 10:
                    continue
                
                # 分析最近的性能数据
                recent_metrics = list(self.metrics_history)[-10:]
                
                # 自动优化建议
                optimizations = await self._analyze_and_optimize(recent_metrics)
                
                if optimizations:
                    logger.info(f"性能优化建议: {optimizations}")
                
            except Exception as e:
                logger.error(f"自动优化循环错误: {str(e)}")
    
    async def _analyze_and_optimize(self, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """分析并生成优化建议"""
        optimizations = []
        
        # 计算平均值
        avg_cpu = statistics.mean([m.cpu_percent for m in metrics_list])
        avg_memory = statistics.mean([m.memory_percent for m in metrics_list])
        avg_response_time = statistics.mean([m.response_time_avg for m in metrics_list])
        avg_error_rate = statistics.mean([m.error_rate for m in metrics_list])
        
        # CPU优化建议
        if avg_cpu > 70:
            optimizations.append("CPU使用率过高，建议增加工作进程数或优化算法")
        
        # 内存优化建议
        if avg_memory > 80:
            optimizations.append("内存使用率过高，建议增加内存或优化数据结构")
        
        # 响应时间优化建议
        if avg_response_time > 1000:
            optimizations.append("响应时间过长，建议添加缓存或优化数据库查询")
        
        # 错误率优化建议
        if avg_error_rate > 2:
            optimizations.append("错误率过高，建议检查错误日志并修复问题")
        
        return optimizations
    
    def _update_stats(self, metrics: PerformanceMetrics):
        """更新统计信息"""
        self.stats['peak_cpu'] = max(self.stats['peak_cpu'], metrics.cpu_percent)
        self.stats['peak_memory'] = max(self.stats['peak_memory'], metrics.memory_percent)
        
        if self.response_times:
            self.stats['avg_response_time'] = statistics.mean(self.response_times)
    
    def record_request(self, response_time: float, is_error: bool = False):
        """记录请求"""
        current_time = time.time()
        
        self.response_times.append(response_time)
        self.request_counts.append(current_time)
        self.stats['total_requests'] += 1
        
        if is_error:
            self.error_counts.append(current_time)
            self.stats['total_errors'] += 1
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules.append(rule)
    
    def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, duration: int = 3600) -> List[PerformanceMetrics]:
        """获取历史指标"""
        current_time = time.time()
        cutoff_time = current_time - duration
        
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        current_metrics = self.get_current_metrics()
        recent_metrics = self.get_metrics_history(3600)  # 最近1小时
        
        report = {
            'current_metrics': asdict(current_metrics) if current_metrics else None,
            'stats': self.stats.copy(),
            'alert_summary': {
                'total_rules': len(self.alert_rules),
                'active_alerts': len(self.active_alerts),
                'recent_alerts': self.stats['alerts_triggered']
            },
            'performance_summary': {},
            'recommendations': []
        }
        
        if recent_metrics:
            # 性能摘要
            report['performance_summary'] = {
                'avg_cpu': statistics.mean([m.cpu_percent for m in recent_metrics]),
                'avg_memory': statistics.mean([m.memory_percent for m in recent_metrics]),
                'avg_response_time': statistics.mean([m.response_time_avg for m in recent_metrics]),
                'avg_error_rate': statistics.mean([m.error_rate for m in recent_metrics]),
                'peak_cpu': max([m.cpu_percent for m in recent_metrics]),
                'peak_memory': max([m.memory_percent for m in recent_metrics])
            }
            
            # 生成建议
            summary = report['performance_summary']
            if summary['avg_cpu'] > 70:
                report['recommendations'].append('考虑增加CPU资源或优化计算密集型操作')
            if summary['avg_memory'] > 80:
                report['recommendations'].append('考虑增加内存或优化内存使用')
            if summary['avg_response_time'] > 1000:
                report['recommendations'].append('考虑添加缓存或优化数据库查询')
            if summary['avg_error_rate'] > 2:
                report['recommendations'].append('检查并修复导致错误的问题')
        
        return report

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()
