"""
错误监控系统
"""

import time
import threading
import logging
from typing import Dict, List, Any
from collections import defaultdict, deque
from backend.services.unified_error_handler import unified_error_handler, ErrorInfo

logger = logging.getLogger(__name__)

class ErrorMonitor:
    """错误监控器"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.error_patterns = defaultdict(list)
        self.error_rates = defaultdict(deque)
        self.monitoring = False
        self.monitor_thread = None
        
        # 监控配置
        self.rate_window = 300  # 5分钟窗口
        self.rate_threshold = 10  # 5分钟内超过10个同类错误则告警
        
    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("错误监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("错误监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._analyze_error_patterns()
                self._check_error_rates()
                time.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"错误监控异常: {e}")
                time.sleep(30)
    
    def _analyze_error_patterns(self):
        """分析错误模式"""
        recent_errors = unified_error_handler.error_history[-100:]
        
        # 按错误类型分组
        error_groups = defaultdict(list)
        for error in recent_errors:
            error_groups[error.error_type].append(error)
        
        # 检查是否有异常模式
        for error_type, errors in error_groups.items():
            if len(errors) >= 5:  # 同类错误超过5个
                recent_time = time.time() - 300  # 5分钟内
                recent_errors_count = sum(
                    1 for err in errors if err.timestamp > recent_time
                )
                
                if recent_errors_count >= 3:
                    logger.warning(f"检测到错误模式: {error_type} 在5分钟内出现{recent_errors_count}次")
    
    def _check_error_rates(self):
        """检查错误率"""
        current_time = time.time()
        
        # 清理过期的错误记录
        for error_type in list(self.error_rates.keys()):
            rate_queue = self.error_rates[error_type]
            while rate_queue and current_time - rate_queue[0] > self.rate_window:
                rate_queue.popleft()
        
        # 添加新的错误记录
        for error in unified_error_handler.error_history[-10:]:
            if current_time - error.timestamp <= 60:  # 1分钟内的错误
                self.error_rates[error.error_type].append(error.timestamp)
        
        # 检查错误率
        for error_type, timestamps in self.error_rates.items():
            if len(timestamps) >= self.rate_threshold:
                logger.error(f"错误率告警: {error_type} 在{self.rate_window}秒内出现{len(timestamps)}次")
    
    def get_error_report(self) -> Dict[str, Any]:
        """获取错误报告"""
        current_time = time.time()
        recent_errors = [
            err for err in unified_error_handler.error_history
            if current_time - err.timestamp <= 3600  # 1小时内
        ]
        
        error_summary = defaultdict(int)
        for error in recent_errors:
            error_summary[error.error_type] += 1
        
        return {
            'total_recent_errors': len(recent_errors),
            'error_types': dict(error_summary),
            'error_rates': {
                error_type: len(timestamps)
                for error_type, timestamps in self.error_rates.items()
            },
            'timestamp': current_time
        }

# 全局错误监控器
error_monitor = ErrorMonitor()
