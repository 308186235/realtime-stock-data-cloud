"""
统一配置管理器
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from backend.config.config_validator import config_validator

logger = logging.getLogger(__name__)

class UnifiedConfigManager:
    """统一配置管理器"""
    
    def __init__(self):
        self._config_cache = {}
        self._config_files = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置"""
        # 加载环境变量
        self._load_env_config()
        
        # 加载JSON配置文件
        self._load_json_configs()
        
        # 加载YAML配置文件
        self._load_yaml_configs()
        
        # 验证配置
        self._validate_configs()
    
    def _load_env_config(self):
        """加载环境变量配置"""
        env_config = {}
        
        # 从.env文件加载
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_config[key.strip()] = value.strip()
        
        # 合并系统环境变量
        for key, value in os.environ.items():
            env_config[key] = value
        
        self._config_cache['env'] = env_config
    
    def _load_json_configs(self):
        """加载JSON配置文件"""
        json_files = [
            'config.json',
            'backend/config/settings.json',
            'api_keys.json'
        ]
        
        for file_path in json_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    config_name = Path(file_path).stem
                    self._config_cache[config_name] = config
                    self._config_files[config_name] = file_path
                    
                except Exception as e:
                    logger.error(f"加载JSON配置失败 {file_path}: {e}")
    
    def _load_yaml_configs(self):
        """加载YAML配置文件"""
        yaml_files = [
            'config.yml',
            'config.yaml',
            'backend/config/settings.yml'
        ]
        
        for file_path in yaml_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    config_name = Path(file_path).stem
                    self._config_cache[config_name] = config
                    self._config_files[config_name] = file_path
                    
                except Exception as e:
                    logger.error(f"加载YAML配置失败 {file_path}: {e}")
    
    def _validate_configs(self):
        """验证配置"""
        result = config_validator.validate_configuration()
        if not result.is_valid:
            logger.warning("配置验证发现问题,请检查配置")
    
    def get(self, key: str, default: Any = None, config_type: str = 'env') -> Any:
        """获取配置值"""
        config = self._config_cache.get(config_type, {})
        return config.get(key, default)
    
    def get_nested(self, path: str, default: Any = None, config_type: str = 'env') -> Any:
        """获取嵌套配置值 (例: 'database.host')"""
        config = self._config_cache.get(config_type, {})
        
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, config_type: str = 'env'):
        """设置配置值"""
        if config_type not in self._config_cache:
            self._config_cache[config_type] = {}
        
        self._config_cache[config_type][key] = value
    
    def reload_config(self, config_type: Optional[str] = None):
        """重新加载配置"""
        if config_type:
            # 重新加载特定类型的配置
            if config_type == 'env':
                self._load_env_config()
            elif config_type in self._config_files:
                file_path = self._config_files[config_type]
                if file_path.endswith('.json'):
                    self._load_json_configs()
                elif file_path.endswith(('.yml', '.yaml')):
                    self._load_yaml_configs()
        else:
            # 重新加载所有配置
            self._load_all_configs()
        
        logger.info(f"配置重新加载完成: {config_type or 'all'}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config_cache.copy()
    
    def export_config(self, file_path: str, config_type: str = 'env'):
        """导出配置到文件"""
        config = self._config_cache.get(config_type, {})
        
        if file_path.endswith('.json'):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        elif file_path.endswith(('.yml', '.yaml')):
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"配置已导出到: {file_path}")

# 全局配置管理器
unified_config = UnifiedConfigManager()
