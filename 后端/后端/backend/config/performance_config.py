"""
性能优化配置
"""

import os
from typing import Dict, Any

class PerformanceConfig:
    """性能优化配置"""
    
    # 内存管理配置
    MEMORY_CONFIG = {
        'max_memory_mb': int(os.getenv('MAX_MEMORY_MB', '500')),
        'memory_check_interval': float(os.getenv('MEMORY_CHECK_INTERVAL', '1.0')),
        'cleanup_threshold_mb': int(os.getenv('CLEANUP_THRESHOLD_MB', '400')),
        'force_cleanup_threshold_mb': int(os.getenv('FORCE_CLEANUP_THRESHOLD_MB', '450'))
    }
    
    # 数据库连接池配置
    DATABASE_CONFIG = {
        'min_connections': int(os.getenv('DB_MIN_CONNECTIONS', '5')),
        'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', '20')),
        'connection_timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', '30')),
        'idle_timeout': int(os.getenv('DB_IDLE_TIMEOUT', '300'))
    }
    
    # 缓存配置
    CACHE_CONFIG = {
        'max_cache_size': int(os.getenv('MAX_CACHE_SIZE', '1000')),
        'cache_ttl': int(os.getenv('CACHE_TTL', '300')),
        'cleanup_interval': int(os.getenv('CACHE_CLEANUP_INTERVAL', '60'))
    }
    
    # 并发配置
    CONCURRENCY_CONFIG = {
        'max_workers': int(os.getenv('MAX_WORKERS', '10')),
        'queue_size': int(os.getenv('QUEUE_SIZE', '1000')),
        'batch_size': int(os.getenv('BATCH_SIZE', '100'))
    }
    
    # 监控配置
    MONITORING_CONFIG = {
        'enable_monitoring': os.getenv('ENABLE_MONITORING', 'true').lower() == 'true',
        'monitoring_interval': float(os.getenv('MONITORING_INTERVAL', '1.0')),
        'alert_cpu_threshold': float(os.getenv('ALERT_CPU_THRESHOLD', '80.0')),
        'alert_memory_threshold': float(os.getenv('ALERT_MEMORY_THRESHOLD', '85.0'))
    }
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            'memory': cls.MEMORY_CONFIG,
            'database': cls.DATABASE_CONFIG,
            'cache': cls.CACHE_CONFIG,
            'concurrency': cls.CONCURRENCY_CONFIG,
            'monitoring': cls.MONITORING_CONFIG
        }

# 全局配置实例
perf_config = PerformanceConfig()
