"""
配置验证器
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationResult:
    """配置验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_vars: List[str]

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.required_vars = {
            # 数据库配置
            'SUPABASE_URL': 'Supabase数据库URL',
            'SUPABASE_ANON_KEY': 'Supabase匿名密钥',
            'SUPABASE_SERVICE_ROLE_KEY': 'Supabase服务角色密钥',
            'DATABASE_URL': '数据库连接URL',
            
            # API配置
            'STOCK_API_KEY': '股票数据API密钥',
            'JWT_SECRET_KEY': 'JWT密钥',
            
            # 应用配置
            'APP_ENV': '应用环境',
        }
        
        self.optional_vars = {
            'STOCK_API_KEY_TEST': '测试环境API密钥',
            'CHAGUBANG_TOKEN': '茶股帮Token',
            'REDIS_URL': 'Redis连接URL',
            'DEBUG': '调试模式',
        }
        
        self.validation_rules = {
            'SUPABASE_URL': self._validate_url,
            'DATABASE_URL': self._validate_database_url,
            'JWT_SECRET_KEY': self._validate_jwt_secret,
            'APP_ENV': self._validate_app_env,
        }
    
    def validate_configuration(self) -> ConfigValidationResult:
        """验证配置"""
        errors = []
        warnings = []
        missing_vars = []
        
        # 检查必需的环境变量
        for var_name, description in self.required_vars.items():
            value = os.getenv(var_name)
            if not value:
                missing_vars.append(var_name)
                errors.append(f"缺少必需的环境变量: {var_name} ({description})")
            else:
                # 运行特定验证规则
                if var_name in self.validation_rules:
                    validation_error = self.validation_rules[var_name](value)
                    if validation_error:
                        errors.append(f"{var_name}: {validation_error}")
        
        # 检查可选的环境变量
        for var_name, description in self.optional_vars.items():
            value = os.getenv(var_name)
            if not value:
                warnings.append(f"建议设置环境变量: {var_name} ({description})")
        
        # 检查.env文件是否存在
        if not os.path.exists('.env'):
            warnings.append("未找到.env文件,建议从.env.template复制并配置")
        
        is_valid = len(errors) == 0
        
        return ConfigValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_vars=missing_vars
        )
    
    def _validate_url(self, url: str) -> Optional[str]:
        """验证URL格式"""
        if not url.startswith(('http://', 'https://')):
            return "URL必须以http://或https://开头"
        return None
    
    def _validate_database_url(self, url: str) -> Optional[str]:
        """验证数据库URL"""
        if not url.startswith('postgresql://'):
            return "数据库URL必须以postgresql://开头"
        if 'your_password' in url or 'YOUR_PASSWORD' in url:
            return "数据库URL包含占位符密码,请设置真实密码"
        return None
    
    def _validate_jwt_secret(self, secret: str) -> Optional[str]:
        """验证JWT密钥"""
        if len(secret) < 32:
            return "JWT密钥长度应至少32个字符"
        if secret in ['process.env.JWT_SECRET_KEY', 'your_jwt_secret_here']:
            return "JWT密钥不能使用默认值"
        return None
    
    def _validate_app_env(self, env: str) -> Optional[str]:
        """验证应用环境"""
        valid_envs = ['development', 'production', 'testing']
        if env not in valid_envs:
            return f"应用环境必须是: {', '.join(valid_envs)}"
        return None
    
    def print_validation_report(self, result: ConfigValidationResult):
        """打印验证报告"""
        print("⚙️ 配置验证报告")
        print("=" * 40)
        
        if result.is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
        
        if result.errors:
            print("
🚨 错误:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("
⚠️ 警告:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.missing_vars:
            print(f"
📋 缺少的环境变量: {', '.join(result.missing_vars)}")

# 全局配置验证器
config_validator = ConfigValidator()

def validate_config_on_startup():
    """启动时验证配置"""
    result = config_validator.validate_configuration()
    config_validator.print_validation_report(result)
    
    if not result.is_valid:
        logger.error("配置验证失败,请检查环境变量设置")
        return False
    
    return True
