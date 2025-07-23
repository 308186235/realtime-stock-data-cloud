"""
环境变量验证器
"""

import os
import sys
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EnvValidator:
    """环境变量验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """验证所有环境变量"""
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需的环境变量
        self._validate_required_vars()
        
        # 验证数据库配置
        self._validate_database_config()
        
        # 验证API配置
        self._validate_api_config()
        
        # 验证安全配置
        self._validate_security_config()
        
        # 打印验证结果
        self._print_results()
        
        return len(self.errors) == 0
    
    def _validate_required_vars(self):
        """验证必需的环境变量"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_SERVICE_ROLE_KEY',
            'DATABASE_URL',
            'STOCK_API_KEY',
            'JWT_SECRET_KEY',
            'APP_ENV'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"缺少必需的环境变量: {var}")
    
    def _validate_database_config(self):
        """验证数据库配置"""
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            if not db_url.startswith('postgresql://'):
                self.errors.append("DATABASE_URL必须以postgresql://开头")
            if 'your_password' in db_url.lower():
                self.errors.append("DATABASE_URL包含占位符密码")
    
    def _validate_api_config(self):
        """验证API配置"""
        api_key = os.getenv('STOCK_API_KEY')
        if api_key and api_key in ['your_api_key_here', 'YOUR_API_KEY_HERE']:
            self.errors.append("STOCK_API_KEY不能使用占位符值")
    
    def _validate_security_config(self):
        """验证安全配置"""
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if jwt_secret:
            if len(jwt_secret) < 32:
                self.warnings.append("JWT_SECRET_KEY长度建议至少32个字符")
            if jwt_secret in ['process.env.JWT_SECRET_KEY', 'your_jwt_secret_here']:
                self.errors.append("JWT_SECRET_KEY不能使用默认值")
    
    def _print_results(self):
        """打印验证结果"""
        if self.errors:
            print("❌ 环境变量验证失败:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("⚠️ 环境变量警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ 环境变量验证通过")

def validate_env_on_startup():
    """启动时验证环境变量"""
    validator = EnvValidator()
    is_valid = validator.validate_all()
    
    if not is_valid:
        print("\n请检查环境变量配置后重新启动应用")
        return False
    
    return True

if __name__ == "__main__":
    validate_env_on_startup()
