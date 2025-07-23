#!/usr/bin/env python3
"""
处理剩余的HIGH级别问题
"""

import os
import json
import shutil
from datetime import datetime

class RemainingHighIssuesFixer:
    """剩余HIGH级别问题修复器"""
    
    def __init__(self):
        self.backup_dir = f"remaining_high_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def fix_all_remaining_high_issues(self):
        """修复所有剩余HIGH级别问题"""
        print("🔧 处理剩余HIGH级别问题")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 完全清理backend/config/supabase.py中的硬编码
        self._clean_supabase_config()
        
        # 2. 安全处理api_keys.json
        self._secure_api_keys_file()
        
        # 3. 创建安全的配置加载器
        self._create_secure_config_loader()
        
        print(f"\n✅ 剩余HIGH级别问题修复完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        
    def _clean_supabase_config(self):
        """完全清理Supabase配置中的硬编码"""
        print("\n🔧 清理Supabase配置硬编码...")
        
        file_path = "backend/config/supabase.py"
        if os.path.exists(file_path):
            # 备份原文件
            shutil.copy2(file_path, os.path.join(self.backup_dir, "supabase.py.backup"))
            
            # 创建完全安全的配置文件
            secure_config = '''import os
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
'''
            
            # 写入新的安全配置
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(secure_config)
            
            print(f"✅ 已完全清理: {file_path}")
    
    def _secure_api_keys_file(self):
        """安全处理api_keys.json文件"""
        print("\n🔧 安全处理API密钥文件...")
        
        if os.path.exists("api_keys.json"):
            # 备份原文件
            shutil.copy2("api_keys.json", os.path.join(self.backup_dir, "api_keys.json.backup"))
            
            # 删除原文件
            os.remove("api_keys.json")
            print("✅ 已删除不安全的api_keys.json文件")
        
        # 创建安全的API密钥管理器
        secure_api_manager = '''import os
import json
from typing import Dict, Optional
from datetime import datetime

class SecureAPIKeyManager:
    """安全的API密钥管理器"""
    
    def __init__(self):
        self.keys = self._load_keys_from_env()
    
    def _load_keys_from_env(self) -> Dict:
        """从环境变量加载API密钥"""
        return {
            "stock_api": {
                "prod": {
                    "key": os.getenv("STOCK_API_KEY"),
                    "name": "生产环境股票API",
                    "expire": os.getenv("STOCK_API_KEY_EXPIRE", "2025-07-26")
                },
                "test": {
                    "key": os.getenv("STOCK_API_KEY_TEST"),
                    "name": "测试环境股票API",
                    "expire": os.getenv("STOCK_API_KEY_TEST_EXPIRE", "2025-06-27")
                }
            },
            "chagubang": {
                "token": os.getenv("CHAGUBANG_TOKEN"),
                "host": os.getenv("CHAGUBANG_HOST", "l1.chagubang.com"),
                "port": int(os.getenv("CHAGUBANG_PORT", "6380"))
            }
        }
    
    def get_stock_api_key(self, env: str = "prod") -> Optional[str]:
        """获取股票API密钥"""
        key = self.keys.get("stock_api", {}).get(env, {}).get("key")
        if not key:
            print(f"⚠️ 警告: {env}环境股票API密钥未配置")
        return key
    
    def get_chagubang_config(self) -> Dict:
        """获取茶股帮配置"""
        config = self.keys.get("chagubang", {})
        if not config.get("token"):
            print("⚠️ 警告: 茶股帮Token未配置")
        return config
    
    def validate_keys(self) -> bool:
        """验证密钥完整性"""
        issues = []
        
        # 检查股票API密钥
        if not self.keys.get("stock_api", {}).get("prod", {}).get("key"):
            issues.append("生产环境股票API密钥缺失")
        
        # 检查茶股帮配置
        if not self.keys.get("chagubang", {}).get("token"):
            issues.append("茶股帮Token缺失")
        
        if issues:
            print("❌ API密钥验证失败:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✅ API密钥验证通过")
        return True

# 全局API密钥管理器
api_key_manager = SecureAPIKeyManager()
'''
        
        with open("secure_api_manager.py", 'w', encoding='utf-8') as f:
            f.write(secure_api_manager)
        
        print("✅ 已创建安全的API密钥管理器: secure_api_manager.py")
    
    def _create_secure_config_loader(self):
        """创建安全的配置加载器"""
        print("\n🔧 创建安全配置加载器...")
        
        config_loader = '''import os
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
            print("❌ 配置验证失败,缺少以下环境变量:")
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
'''
        
        with open("secure_config.py", 'w', encoding='utf-8') as f:
            f.write(config_loader)
        
        print("✅ 已创建安全配置加载器: secure_config.py")

if __name__ == "__main__":
    fixer = RemainingHighIssuesFixer()
    fixer.fix_all_remaining_high_issues()
