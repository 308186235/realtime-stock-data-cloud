"""
统一错误处理器
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorInfo:
    """错误信息"""
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: float
    traceback: str
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_successful: bool = False

class UnifiedErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.error_history = []
        self.error_counts = {}
        self.recovery_strategies = {}
        self.alert_callbacks = []
        
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """注册错误恢复策略"""
        self.recovery_strategies[error_type] = strategy
        logger.info(f"注册恢复策略: {error_type}")
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> ErrorInfo:
        """处理错误"""
        error_type = type(error).__name__
        error_info = ErrorInfo(
            error_type=error_type,
            message=str(error),
            severity=severity,
            timestamp=time.time(),
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        # 记录错误
        self.error_history.append(error_info)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # 记录日志
        log_level = self._get_log_level(severity)
        logger.log(log_level, f"错误处理: {error_type} - {error_info.message}")
        
        # 尝试恢复
        if error_type in self.recovery_strategies:
            try:
                error_info.recovery_attempted = True
                recovery_result = self.recovery_strategies[error_type](error, context)
                error_info.recovery_successful = bool(recovery_result)
                logger.info(f"错误恢复{'成功' if error_info.recovery_successful else '失败'}: {error_type}")
            except Exception as recovery_error:
                logger.error(f"错误恢复失败: {recovery_error}")
        
        # 发送告警
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._send_alerts(error_info)
        
        return error_info
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        level_map = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return level_map.get(severity, logging.WARNING)
    
    def _send_alerts(self, error_info: ErrorInfo):
        """发送告警"""
        for callback in self.alert_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                logger.error(f"告警回调失败: {e}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        return {
            'total_errors': len(self.error_history),
            'error_counts': self.error_counts.copy(),
            'recent_errors': [
                {
                    'type': err.error_type,
                    'message': err.message,
                    'severity': err.severity.value,
                    'timestamp': err.timestamp
                }
                for err in self.error_history[-10:]
            ]
        }

def error_handler(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Dict[str, Any] = None):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = unified_error_handler.handle_error(
                    e, context or {'function': func.__name__}, severity
                )
                
                # 根据严重程度决定是否重新抛出异常
                if severity == ErrorSeverity.CRITICAL:
                    raise
                elif severity == ErrorSeverity.HIGH and not error_info.recovery_successful:
                    raise
                
                return None
        return wrapper
    return decorator

def async_error_handler(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       context: Dict[str, Any] = None):
    """异步错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_info = unified_error_handler.handle_error(
                    e, context or {'function': func.__name__}, severity
                )
                
                if severity == ErrorSeverity.CRITICAL:
                    raise
                elif severity == ErrorSeverity.HIGH and not error_info.recovery_successful:
                    raise
                
                return None
        return wrapper
    return decorator

# 全局错误处理器实例
unified_error_handler = UnifiedErrorHandler()
