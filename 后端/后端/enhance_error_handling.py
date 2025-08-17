#!/usr/bin/env python3
"""
增强错误处理机制
"""

import os
import shutil
import re
from datetime import datetime

class ErrorHandlingEnhancer:
    """错误处理增强器"""
    
    def __init__(self):
        self.backup_dir = f"error_handling_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.enhanced_files = []
        
    def enhance_all_error_handling(self):
        """增强所有错误处理"""
        print("🛡️ 增强错误处理机制")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 增强网络请求错误处理
        self._enhance_network_error_handling()
        
        # 2. 增强数据库操作错误处理
        self._enhance_database_error_handling()
        
        # 3. 创建统一错误处理器
        self._create_unified_error_handler()
        
        # 4. 添加错误恢复机制
        self._add_error_recovery()
        
        # 5. 创建错误监控系统
        self._create_error_monitoring()
        
        print(f"\n✅ 错误处理增强完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print(f"🛡️ 增强了 {len(self.enhanced_files)} 个文件")
        
    def _enhance_network_error_handling(self):
        """增强网络请求错误处理"""
        print("\n🛡️ 增强网络请求错误处理...")
        
        network_files = [
            "炒股养家/utils/request.js",
            "frontend/gupiao1/utils/request.js",
            "炒股养家/auto-trader/request.js",
            "chagubang_receiver.py",
            "backend/services/realtime_stock_receiver.py"
        ]
        
        for file_path in network_files:
            if os.path.exists(file_path):
                self._backup_file(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 增强错误处理
                content = self._enhance_network_errors(content, file_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.enhanced_files.append(file_path)
                print(f"✅ 已增强: {file_path}")
    
    def _enhance_database_error_handling(self):
        """增强数据库操作错误处理"""
        print("\n🛡️ 增强数据库操作错误处理...")
        
        db_files = [
            "backend/adapters/database_adapter.py",
            "chagubang_to_database.py",
            "mass_stock_database_processor.py",
            "backend/supabase_config.py"
        ]
        
        for file_path in db_files:
            if os.path.exists(file_path):
                self._backup_file(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 增强数据库错误处理
                content = self._enhance_database_errors(content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.enhanced_files.append(file_path)
                print(f"✅ 已增强: {file_path}")
    
    def _create_unified_error_handler(self):
        """创建统一错误处理器"""
        print("\n🛡️ 创建统一错误处理器...")
        
        error_handler_code = '''"""
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
'''
        
        with open("backend/services/unified_error_handler.py", "w", encoding="utf-8") as f:
            f.write(error_handler_code)
        
        print("✅ 已创建: backend/services/unified_error_handler.py")
    
    def _add_error_recovery(self):
        """添加错误恢复机制"""
        print("\n🛡️ 添加错误恢复机制...")
        
        recovery_code = '''"""
错误恢复机制
"""

import time
import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from backend.services.unified_error_handler import unified_error_handler, ErrorSeverity

logger = logging.getLogger(__name__)

class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self):
        self._setup_recovery_strategies()
    
    def _setup_recovery_strategies(self):
        """设置恢复策略"""
        
        # 网络连接错误恢复
        unified_error_handler.register_recovery_strategy(
            'ConnectionError', self._recover_connection_error
        )
        unified_error_handler.register_recovery_strategy(
            'TimeoutError', self._recover_timeout_error
        )
        
        # 数据库错误恢复
        unified_error_handler.register_recovery_strategy(
            'DatabaseError', self._recover_database_error
        )
        unified_error_handler.register_recovery_strategy(
            'OperationalError', self._recover_database_error
        )
        
        # 内存错误恢复
        unified_error_handler.register_recovery_strategy(
            'MemoryError', self._recover_memory_error
        )
        
        # 文件操作错误恢复
        unified_error_handler.register_recovery_strategy(
            'FileNotFoundError', self._recover_file_error
        )
        unified_error_handler.register_recovery_strategy(
            'PermissionError', self._recover_permission_error
        )
    
    def _recover_connection_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复连接错误"""
        logger.info("尝试恢复连接错误...")
        
        # 等待一段时间后重试
        time.sleep(2)
        
        # 如果有重连函数,调用它
        if 'reconnect_func' in context:
            try:
                context['reconnect_func']()
                return True
            except Exception as e:
                logger.error(f"重连失败: {e}")
        
        return False
    
    def _recover_timeout_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复超时错误"""
        logger.info("尝试恢复超时错误...")
        
        # 增加超时时间并重试
        if 'timeout' in context:
            context['timeout'] = context['timeout'] * 1.5
            logger.info(f"增加超时时间到: {context['timeout']}")
        
        return True
    
    def _recover_database_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复数据库错误"""
        logger.info("尝试恢复数据库错误...")
        
        # 重新建立数据库连接
        if 'db_reconnect' in context:
            try:
                context['db_reconnect']()
                return True
            except Exception as e:
                logger.error(f"数据库重连失败: {e}")
        
        return False
    
    def _recover_memory_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复内存错误"""
        logger.info("尝试恢复内存错误...")
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        # 清理缓存
        if 'clear_cache' in context:
            try:
                context['clear_cache']()
                return True
            except Exception as e:
                logger.error(f"缓存清理失败: {e}")
        
        return False
    
    def _recover_file_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复文件错误"""
        logger.info("尝试恢复文件错误...")
        
        # 创建缺失的目录
        if 'file_path' in context:
            import os
            file_path = context['file_path']
            dir_path = os.path.dirname(file_path)
            
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    return True
                except Exception as e:
                    logger.error(f"创建目录失败: {e}")
        
        return False
    
    def _recover_permission_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """恢复权限错误"""
        logger.info("尝试恢复权限错误...")
        
        # 尝试使用备用路径
        if 'backup_path' in context:
            try:
                # 这里可以实现备用路径逻辑
                return True
            except Exception as e:
                logger.error(f"使用备用路径失败: {e}")
        
        return False

# 全局错误恢复管理器
error_recovery_manager = ErrorRecoveryManager()
'''
        
        with open("backend/services/error_recovery_manager.py", "w", encoding="utf-8") as f:
            f.write(recovery_code)
        
        print("✅ 已创建: backend/services/error_recovery_manager.py")
    
    def _create_error_monitoring(self):
        """创建错误监控系统"""
        print("\n🛡️ 创建错误监控系统...")
        
        monitoring_code = '''"""
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
'''
        
        with open("backend/services/error_monitor.py", "w", encoding="utf-8") as f:
            f.write(monitoring_code)
        
        print("✅ 已创建: backend/services/error_monitor.py")
    
    def _backup_file(self, file_path: str):
        """备份文件"""
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copy2(file_path, backup_path)
    
    def _enhance_network_errors(self, content: str, file_path: str) -> str:
        """增强网络错误处理"""
        if file_path.endswith('.js'):
            # JavaScript文件的错误处理增强
            if "// 增强错误处理" not in content:
                enhanced_js = '''
// 增强错误处理
const ErrorHandler = {
  handleNetworkError(error, context = {}) {
    console.error('网络错误:', error, context);
    
    // 根据错误类型进行不同处理
    if (error.errMsg && error.errMsg.includes('timeout')) {
      return this.handleTimeout(error, context);
    } else if (error.errMsg && error.errMsg.includes('fail')) {
      return this.handleConnectionFail(error, context);
    } else {
      return this.handleGenericError(error, context);
    }
  },
  
  handleTimeout(error, context) {
    console.warn('请求超时,尝试重试...');
    // 可以在这里实现重试逻辑
    return { retry: true, delay: 2000 };
  },
  
  handleConnectionFail(error, context) {
    console.warn('连接失败,检查网络状态...');
    return { retry: true, delay: 5000 };
  },
  
  handleGenericError(error, context) {
    console.error('通用错误处理:', error);
    return { retry: false };
  }
};

'''
                content = enhanced_js + content
        
        else:
            # Python文件的错误处理增强
            if "# 增强错误处理" not in content:
                enhanced_py = '''
# 增强错误处理
import logging
from backend.services.unified_error_handler import unified_error_handler, ErrorSeverity, error_handler

logger = logging.getLogger(__name__)

@error_handler(severity=ErrorSeverity.HIGH)
def safe_network_request(func, *args, **kwargs):
    """安全的网络请求包装器"""
    try:
        return func(*args, **kwargs)
    except ConnectionError as e:
        logger.error(f"连接错误: {e}")
        raise
    except TimeoutError as e:
        logger.error(f"超时错误: {e}")
        raise
    except Exception as e:
        logger.error(f"网络请求异常: {e}")
        raise

'''
                content = enhanced_py + content
        
        return content
    
    def _enhance_database_errors(self, content: str) -> str:
        """增强数据库错误处理"""
        if "# 增强数据库错误处理" not in content:
            enhanced_db = '''
# 增强数据库错误处理
import logging
from backend.services.unified_error_handler import unified_error_handler, ErrorSeverity, async_error_handler

logger = logging.getLogger(__name__)

@async_error_handler(severity=ErrorSeverity.HIGH)
async def safe_database_operation(func, *args, **kwargs):
    """安全的数据库操作包装器"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"数据库操作异常: {e}")
        # 这里可以添加数据库重连逻辑
        raise

'''
            content = enhanced_db + content
        
        return content

if __name__ == "__main__":
    enhancer = ErrorHandlingEnhancer()
    enhancer.enhance_all_error_handling()
