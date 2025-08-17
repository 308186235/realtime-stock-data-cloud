"""
资源管理器 - 统一管理系统资源,防止泄漏
"""

import asyncio
import logging
import weakref
from contextlib import asynccontextmanager, contextmanager
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ResourceManager:
    """统一资源管理器"""
    
    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._cleanup_callbacks: List[callable] = []
        self._active_connections = weakref.WeakSet()
        
    def register_resource(self, name: str, resource: Any, cleanup_func: callable = None):
        """注册资源"""
        self._resources[name] = resource
        if cleanup_func:
            self._cleanup_callbacks.append(cleanup_func)
        logger.debug(f"注册资源: {name}")
    
    def get_resource(self, name: str) -> Any:
        """获取资源"""
        return self._resources.get(name)
    
    async def cleanup_all(self):
        """清理所有资源"""
        logger.info("开始清理所有资源...")
        
        for callback in self._cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"资源清理失败: {e}")
        
        self._resources.clear()
        self._cleanup_callbacks.clear()
        logger.info("资源清理完成")
    
    @asynccontextmanager
    async def managed_resource(self, resource_factory, cleanup_func=None):
        """上下文管理器"""
        resource = None
        try:
            resource = await resource_factory() if asyncio.iscoroutinefunction(resource_factory) else resource_factory()
            yield resource
        finally:
            if resource and cleanup_func:
                try:
                    if asyncio.iscoroutinefunction(cleanup_func):
                        await cleanup_func(resource)
                    else:
                        cleanup_func(resource)
                except Exception as e:
                    logger.error(f"资源清理失败: {e}")

# 全局资源管理器实例
resource_manager = ResourceManager()
