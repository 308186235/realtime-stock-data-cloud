import os
from pathlib import Path
from typing import Dict, Any, Optional

class SecureConfigLoader:
    """安全的配置加载器"""
    
    def __init__(self):
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        return {
            # 应用配置
            "app": {
                "name": os.getenv("APP_NAME", "智能交易系统"),
                "env": os.getenv("APP_ENV", "development"),
                "debug": os.getenv("DEBUG", "false").lower() == "true"
            },
            
            # 数据库配置
            "database": {
                "url": os.getenv("DATABASE_URL"),
                "supabase_url": os.getenv("SUPABASE_URL"),
                "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY"),
                "supabase_service_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            },
            
            # API配置
            "api": {
                "stock_key": os.getenv("STOCK_API_KEY"),
                "stock_key_test": os.getenv("STOCK_API_KEY_TEST"),
                "chagubang_token": os.getenv("CHAGUBANG_TOKEN"),
                "chagubang_host": os.getenv("CHAGUBANG_HOST", "l1.chagubang.com"),
                "chagubang_port": int(os.getenv("CHAGUBANG_PORT", "6380"))
            },
            
            # 安全配置
            "security": {
                "jwt_secret": os.getenv("JWT_SECRET_KEY"),
                "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
                "access_token_expire": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            },
            
            # 服务端口配置
            "ports": {
                "api": int(os.getenv("API_PORT", "8000")),
                "agent_backend": int(os.getenv("AGENT_BACKEND_PORT", "9999")),
                "trading_api": int(os.getenv("TRADING_API_PORT", "8888"))
            }
        }
    
    def _validate_config(self):
        """验证配置完整性"""
        required_configs = [
            ("database.supabase_url", "SUPABASE_URL"),
            ("database.supabase_anon_key", "SUPABASE_ANON_KEY"),
            ("security.jwt_secret", "JWT_SECRET_KEY")
        ]
        
        missing_configs = []
        for config_path, env_var in required_configs:
            if not self._get_nested_config(config_path):
                missing_configs.append(env_var)
        
        if missing_configs:
            print("❌ 配置验证失败，缺少以下环境变量:")
            for config in missing_configs:
                print(f"  - {config}")
            print("请检查.env文件配置")
        else:
            print("✅ 配置验证通过")
    
    def _get_nested_config(self, path: str) -> Any:
        """获取嵌套配置值"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value
    
    def get_database_config(self) -> Dict:
        """获取数据库配置"""
        return self.config["database"]
    
    def get_api_config(self) -> Dict:
        """获取API配置"""
        return self.config["api"]
    
    def get_security_config(self) -> Dict:
        """获取安全配置"""
        return self.config["security"]
    
    def get_port_config(self) -> Dict:
        """获取端口配置"""
        return self.config["ports"]
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.config["app"]["env"] == "production"
    
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.config["app"]["debug"]

# 全局配置实例
secure_config = SecureConfigLoader()
