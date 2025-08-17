#!/usr/bin/env python3
"""
修复前端配置，使用可访问的自定义域名
"""

import os
import shutil
from datetime import datetime

class FrontendDomainFixer:
    """前端域名修复器"""
    
    def __init__(self):
        self.backup_dir = f"domain_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.working_domain = "https://api.aigupiao.me"
        self.working_ws = "wss://api.aigupiao.me/ws"
        self.blocked_domain = "https://trading-api.308186235.workers.dev"
        
    def fix_all_configs(self):
        """修复所有配置文件"""
        print("🔧 修复前端配置 - 使用可访问域名")
        print("=" * 50)
        print(f"❌ 被阻止: {self.blocked_domain}")
        print(f"✅ 可访问: {self.working_domain}")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 修复配置文件
        config_files = [
            "炒股养家/env.js",
            "炒股养家/services/config.js",
            "炒股养家/services/unifiedAgentService.js",
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self._fix_config_file(config_file)
                print(f"✅ 已修复: {config_file}")
            else:
                print(f"⚠️ 文件不存在: {config_file}")
        
        print(f"\n✅ 前端配置修复完成！")
        print(f"📁 备份保存在: {self.backup_dir}")
        print(f"\n🌐 现在前端将使用:")
        print(f"   API: {self.working_domain}")
        print(f"   WebSocket: {self.working_ws}")
        
    def _fix_config_file(self, file_path):
        """修复单个配置文件"""
        # 备份原文件
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换所有被阻止的域名
        replacements = [
            # 主要替换
            (f"'{self.blocked_domain}'", f"'{self.working_domain}'"),
            (f'"{self.blocked_domain}"', f'"{self.working_domain}"'),
            (f"'{self.blocked_domain}/ws'", f"'{self.working_ws}'"),
            (f'"{self.blocked_domain}/ws"', f'"{self.working_ws}"'),
            
            # WebSocket替换
            ("'wss://trading-api.308186235.workers.dev/ws'", f"'{self.working_ws}'"),
            ('"wss://trading-api.308186235.workers.dev/ws"', f'"{self.working_ws}"'),
            
            # 其他可能的变体
            ("trading-api.308186235.workers.dev", "api.aigupiao.me"),
            
            # 确保本地API使用正确端口
            ("'http://localhost:9999'", "'http://localhost:8888'"),
            ('"http://localhost:9999"', '"http://localhost:8888"'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    fixer = FrontendDomainFixer()
    fixer.fix_all_configs()
