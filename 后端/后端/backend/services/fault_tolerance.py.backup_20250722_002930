"""
容错和自动重连机制
"""
import asyncio
import time
import logging
import random
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    FAILED = "failed"

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

@dataclass
class HealthCheckConfig:
    """健康检查配置"""
    interval: float = 30.0
    timeout: float = 10.0
    failure_threshold: int = 3

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0
        
    async def call(self, func: Callable, *args, **kwargs):
        """执行函数调用"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = "half_open"
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is open")
        
        if self.state == "half_open":
            if self.half_open_calls >= self.config.half_open_max_calls:
                raise Exception("Circuit breaker half-open limit exceeded")
            self.half_open_calls += 1
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 成功调用
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = "open"
            
            raise e

class RetryMechanism:
    """重试机制"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute(self, func: Callable, *args, **kwargs):
        """执行带重试的函数调用"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_retries:
                    break
                
                # 计算延迟时间
                delay = min(
                    self.config.base_delay * (self.config.exponential_base ** attempt),
                    self.config.max_delay
                )
                
                # 添加抖动
                if self.config.jitter:
                    delay *= (0.5 + random.random() * 0.5)
                
                logger.warning(f"重试 {attempt + 1}/{self.config.max_retries}, 延迟 {delay:.2f}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise last_exception

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.services: Dict[str, Dict] = {}
        self.running = False
        self.check_task: Optional[asyncio.Task] = None
        
    def register_service(self, name: str, check_func: Callable, critical: bool = True):
        """注册服务健康检查"""
        self.services[name] = {
            'check_func': check_func,
            'critical': critical,
            'status': ServiceStatus.HEALTHY,
            'failure_count': 0,
            'last_check': 0,
            'last_success': time.time()
        }
    
    async def start(self):
        """启动健康检查"""
        self.running = True
        self.check_task = asyncio.create_task(self._check_loop())
        logger.info("健康检查器已启动")
    
    async def stop(self):
        """停止健康检查"""
        self.running = False
        if self.check_task:
            self.check_task.cancel()
        logger.info("健康检查器已停止")
    
    async def _check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.config.interval)
            except Exception as e:
                logger.error(f"健康检查循环错误: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_all_services(self):
        """检查所有服务"""
        for name, service in self.services.items():
            try:
                # 执行健康检查
                check_func = service['check_func']
                
                start_time = time.time()
                if asyncio.iscoroutinefunction(check_func):
                    result = await asyncio.wait_for(check_func(), timeout=self.config.timeout)
                else:
                    result = check_func()
                
                # 检查成功
                service['failure_count'] = 0
                service['last_check'] = time.time()
                service['last_success'] = time.time()
                
                if service['status'] != ServiceStatus.HEALTHY:
                    service['status'] = ServiceStatus.HEALTHY
                    logger.info(f"服务 {name} 恢复健康")
                
            except Exception as e:
                # 检查失败
                service['failure_count'] += 1
                service['last_check'] = time.time()
                
                # 更新状态
                if service['failure_count'] >= self.config.failure_threshold:
                    if service['critical']:
                        service['status'] = ServiceStatus.FAILED
                    else:
                        service['status'] = ServiceStatus.DEGRADED
                    
                    logger.error(f"服务 {name} 健康检查失败: {str(e)}")
    
    def get_service_status(self, name: str) -> ServiceStatus:
        """获取服务状态"""
        return self.services.get(name, {}).get('status', ServiceStatus.FAILED)
    
    def get_overall_status(self) -> ServiceStatus:
        """获取整体状态"""
        if not self.services:
            return ServiceStatus.HEALTHY
        
        critical_services = [s for s in self.services.values() if s['critical']]
        
        # 检查关键服务
        for service in critical_services:
            if service['status'] == ServiceStatus.FAILED:
                return ServiceStatus.FAILED
            elif service['status'] == ServiceStatus.DEGRADED:
                return ServiceStatus.DEGRADED
        
        return ServiceStatus.HEALTHY

class FaultToleranceManager:
    """容错管理器"""
    
    def __init__(self):
        # 组件
        self.retry_mechanism = RetryMechanism(RetryConfig())
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.health_checker = HealthChecker(HealthCheckConfig())
        
        # 配置
        self.fallback_handlers: Dict[str, Callable] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        
        # 状态
        self.running = False
        self.recovery_task: Optional[asyncio.Task] = None
        
        # 统计
        self.stats = {
            'total_retries': 0,
            'total_circuit_breaks': 0,
            'total_fallbacks': 0,
            'total_recoveries': 0,
            'start_time': 0
        }
    
    async def start(self):
        """启动容错管理器"""
        try:
            self.running = True
            self.stats['start_time'] = time.time()
            
            # 启动健康检查
            await self.health_checker.start()
            
            # 启动恢复任务
            self.recovery_task = asyncio.create_task(self._recovery_loop())
            
            logger.info("容错管理器启动成功")
            
        except Exception as e:
            logger.error(f"启动容错管理器失败: {str(e)}")
            raise
    
    async def stop(self):
        """停止容错管理器"""
        self.running = False
        
        # 停止健康检查
        await self.health_checker.stop()
        
        # 停止恢复任务
        if self.recovery_task:
            self.recovery_task.cancel()
        
        logger.info("容错管理器已停止")
    
    def register_service(self, name: str, check_func: Callable, critical: bool = True):
        """注册服务"""
        # 注册健康检查
        self.health_checker.register_service(name, check_func, critical)
        
        # 创建熔断器
        self.circuit_breakers[name] = CircuitBreaker(CircuitBreakerConfig())
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """注册降级处理器"""
        self.fallback_handlers[service_name] = fallback_func
    
    def register_recovery(self, service_name: str, recovery_func: Callable):
        """注册恢复处理器"""
        self.recovery_handlers[service_name] = recovery_func
    
    async def execute_with_fault_tolerance(self, service_name: str, func: Callable, *args, **kwargs):
        """执行带容错的函数调用"""
        try:
            # 检查服务状态
            service_status = self.health_checker.get_service_status(service_name)
            
            if service_status == ServiceStatus.FAILED:
                # 服务失败，尝试降级
                return await self._execute_fallback(service_name, *args, **kwargs)
            
            # 使用熔断器和重试机制
            circuit_breaker = self.circuit_breakers.get(service_name)
            
            if circuit_breaker:
                return await circuit_breaker.call(
                    self.retry_mechanism.execute, func, *args, **kwargs
                )
            else:
                return await self.retry_mechanism.execute(func, *args, **kwargs)
                
        except Exception as e:
            logger.error(f"服务 {service_name} 执行失败: {str(e)}")
            
            # 尝试降级处理
            try:
                return await self._execute_fallback(service_name, *args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"降级处理也失败: {str(fallback_error)}")
                raise e
    
    async def _execute_fallback(self, service_name: str, *args, **kwargs):
        """执行降级处理"""
        fallback_func = self.fallback_handlers.get(service_name)
        
        if not fallback_func:
            raise Exception(f"服务 {service_name} 无可用的降级处理")
        
        self.stats['total_fallbacks'] += 1
        logger.info(f"执行服务 {service_name} 的降级处理")
        
        if asyncio.iscoroutinefunction(fallback_func):
            return await fallback_func(*args, **kwargs)
        else:
            return fallback_func(*args, **kwargs)
    
    async def _recovery_loop(self):
        """恢复循环"""
        while self.running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                # 检查需要恢复的服务
                for service_name, service in self.health_checker.services.items():
                    if service['status'] == ServiceStatus.FAILED:
                        # 尝试恢复
                        await self._attempt_recovery(service_name)
                
            except Exception as e:
                logger.error(f"恢复循环错误: {str(e)}")
    
    async def _attempt_recovery(self, service_name: str):
        """尝试恢复服务"""
        recovery_func = self.recovery_handlers.get(service_name)
        
        if not recovery_func:
            return
        
        try:
            logger.info(f"尝试恢复服务: {service_name}")
            
            if asyncio.iscoroutinefunction(recovery_func):
                await recovery_func()
            else:
                recovery_func()
            
            self.stats['total_recoveries'] += 1
            logger.info(f"服务 {service_name} 恢复成功")
            
        except Exception as e:
            logger.error(f"服务 {service_name} 恢复失败: {str(e)}")
    
    def get_fault_tolerance_report(self) -> Dict[str, Any]:
        """获取容错报告"""
        return {
            'overall_status': self.health_checker.get_overall_status().value,
            'services': {
                name: {
                    'status': service['status'].value,
                    'failure_count': service['failure_count'],
                    'last_success': service['last_success']
                }
                for name, service in self.health_checker.services.items()
            },
            'circuit_breakers': {
                name: {
                    'state': cb.state,
                    'failure_count': cb.failure_count
                }
                for name, cb in self.circuit_breakers.items()
            },
            'stats': self.stats.copy(),
            'uptime': time.time() - self.stats['start_time'] if self.stats['start_time'] > 0 else 0
        }

# 全局容错管理器实例
fault_tolerance_manager = FaultToleranceManager()
