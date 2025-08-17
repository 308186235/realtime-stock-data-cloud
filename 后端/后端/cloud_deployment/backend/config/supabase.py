import os
from typing import Optional

class SupabaseConfig:
    """安全的Supabase配置类"""
    
    def __init__(self):
        # 从环境变量获取所有配置
        self.url = self._get_required_env("SUPABASE_URL")
        self.anon_key = self._get_required_env("SUPABASE_ANON_KEY")
        self.service_role_key = self._get_required_env("SUPABASE_SERVICE_ROLE_KEY")
        self.database_url = self._get_required_env("DATABASE_URL")
        
        # 可选配置
        self.timeout = int(os.getenv("SUPABASE_TIMEOUT", "30"))
        self.max_connections = int(os.getenv("SUPABASE_MAX_CONNECTIONS", "20"))
        
    def _get_required_env(self, key: str) -> str:
        """获取必需的环境变量"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def get_client_config(self) -> dict:
        """获取客户端配置"""
        return {
            "url": self.url,
            "key": self.anon_key,
            "timeout": self.timeout
        }
    
    def get_admin_config(self) -> dict:
        """获取管理员配置"""
        return {
            "url": self.url,
            "key": self.service_role_key,
            "timeout": self.timeout
        }
    
    def get_database_config(self) -> dict:
        """获取数据库配置"""
        return {
            "url": self.database_url,
            "max_connections": self.max_connections
        }

# 全局配置实例
try:
    config = SupabaseConfig()
except ValueError as e:
    print(f"❌ Supabase配置错误: {e}")
    print("请检查.env文件中的环境变量配置")
    config = None

# 导出配置
SUPABASE_URL = config.url if config else None
SUPABASE_ANON_KEY = config.anon_key if config else None
SUPABASE_SERVICE_ROLE_KEY = config.service_role_key if config else None
DATABASE_URL = config.database_url if config else None
