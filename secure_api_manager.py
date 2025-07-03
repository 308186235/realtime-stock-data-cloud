import os
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
