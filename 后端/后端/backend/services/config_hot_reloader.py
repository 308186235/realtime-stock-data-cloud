"""
配置热重载监控器
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.config.unified_config import unified_config

logger = logging.getLogger(__name__)

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变化处理器"""
    
    def __init__(self, reload_callback: Callable):
        self.reload_callback = reload_callback
        self.config_extensions = {'.env', '.json', '.yml', '.yaml'}
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix in self.config_extensions:
            logger.info(f"检测到配置文件变化: {file_path}")
            self.reload_callback(str(file_path))

class ConfigHotReloader:
    """配置热重载器"""
    
    def __init__(self):
        self.observer = Observer()
        self.watching = False
        self.watched_paths = set()
        self.reload_callbacks: List[Callable] = []
        
    def add_reload_callback(self, callback: Callable):
        """添加重载回调"""
        self.reload_callbacks.append(callback)
    
    def start_watching(self, paths: List[str] = None):
        """开始监控配置文件"""
        if self.watching:
            return
        
        if paths is None:
            paths = ['.', 'backend/config']
        
        handler = ConfigFileHandler(self._on_config_changed)
        
        for path in paths:
            if os.path.exists(path):
                self.observer.schedule(handler, path, recursive=True)
                self.watched_paths.add(path)
                logger.info(f"开始监控配置目录: {path}")
        
        self.observer.start()
        self.watching = True
        logger.info("配置热重载监控已启动")
    
    def stop_watching(self):
        """停止监控"""
        if not self.watching:
            return
        
        self.observer.stop()
        self.observer.join()
        self.watching = False
        logger.info("配置热重载监控已停止")
    
    def _on_config_changed(self, file_path: str):
        """配置文件变化回调"""
        try:
            # 等待文件写入完成
            time.sleep(0.1)
            
            # 重新加载配置
            file_name = Path(file_path).stem
            unified_config.reload_config(file_name)
            
            # 调用所有回调函数
            for callback in self.reload_callbacks:
                try:
                    callback(file_path)
                except Exception as e:
                    logger.error(f"配置重载回调失败: {e}")
            
            logger.info(f"配置热重载完成: {file_path}")
            
        except Exception as e:
            logger.error(f"配置热重载失败: {e}")

# 全局配置热重载器
config_hot_reloader = ConfigHotReloader()

def start_config_monitoring():
    """启动配置监控"""
    config_hot_reloader.start_watching()

def stop_config_monitoring():
    """停止配置监控"""
    config_hot_reloader.stop_watching()
