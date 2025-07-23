#!/usr/bin/env python3
"""
最终修复前端API地址
彻底解决前端仍在调用无法访问的Worker API的问题
"""

import os
import shutil
from datetime import datetime

class FrontendAPIUrlFixer:
    """前端API地址最终修复器"""
    
    def __init__(self):
        self.backup_dir = f"frontend_api_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.local_agent_url = "http://localhost:9999"
        self.local_ws_url = "ws://localhost:9999/ws"
        
    def fix_all_frontend_urls(self):
        """修复所有前端API地址"""
        print("🔧 最终修复前端API地址")
        print("=" * 50)
        print(f"🎯 目标API地址: {self.local_agent_url}")
        print(f"🎯 目标WebSocket: {self.local_ws_url}")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 修复主要配置文件
        self._fix_main_config_files()
        
        # 2. 修复服务配置文件
        self._fix_service_config_files()
        
        # 3. 修复统一Agent服务
        self._fix_unified_agent_service()
        
        # 4. 验证修复结果
        self._verify_fixes()
        
        print(f"\n✅ 前端API地址修复完成！")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print("\n🚀 现在前端将连接到本地Agent后端:")
        print(f"   📡 API: {self.local_agent_url}")
        print(f"   🔌 WebSocket: {self.local_ws_url}")
        
    def _fix_main_config_files(self):
        """修复主要配置文件"""
        print("\n🔧 修复主要配置文件...")
        
        config_files = [
            "炒股养家/env.js",
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self._fix_env_file(config_file)
                print(f"✅ 已修复: {config_file}")
            else:
                print(f"⚠️ 文件不存在: {config_file}")
    
    def _fix_env_file(self, file_path):
        """修复单个env.js文件"""
        # 备份原文件
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换所有错误的API地址
        replacements = [
            # Worker API地址
            ("'https://trading-api.308186235.workers.dev'", f"'{self.local_agent_url}'"),
            ('"https://trading-api.308186235.workers.dev"', f'"{self.local_agent_url}"'),
            ("'wss://trading-api.308186235.workers.dev/ws'", f"'{self.local_ws_url}'"),
            ('"wss://trading-api.308186235.workers.dev/ws"', f'"{self.local_ws_url}"'),
            
            # 其他可能的错误地址
            ("'https://api.aigupiao.me'", f"'{self.local_agent_url}'"),
            ('"https://api.aigupiao.me"', f'"{self.local_agent_url}"'),
            ("'wss://api.aigupiao.me/ws'", f"'{self.local_ws_url}'"),
            ('"wss://api.aigupiao.me/ws"', f'"{self.local_ws_url}"'),
            
            # localhost错误端口
            ("'http://localhost:8000'", f"'{self.local_agent_url}'"),
            ('"http://localhost:8000"', f'"{self.local_agent_url}"'),
            ("'ws://localhost:8000/ws'", f"'{self.local_ws_url}'"),
            ('"ws://localhost:8000/ws"', f'"{self.local_ws_url}"'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_service_config_files(self):
        """修复服务配置文件"""
        print("\n🔧 修复服务配置文件...")
        
        service_files = [
            "炒股养家/services/config.js",
            "frontend/gupiao1/services/config.js",
            "frontend/stock5/services/config.js"
        ]
        
        for service_file in service_files:
            if os.path.exists(service_file):
                self._fix_service_file(service_file)
                print(f"✅ 已修复: {service_file}")
            else:
                print(f"⚠️ 文件不存在: {service_file}")
    
    def _fix_service_file(self, file_path):
        """修复单个服务配置文件"""
        # 备份原文件
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换API基础URL
        replacements = [
            ("const API_BASE_URL = 'https://trading-api.308186235.workers.dev';", 
             f"const API_BASE_URL = '{self.local_agent_url}';"),
            ('const API_BASE_URL = "https://trading-api.308186235.workers.dev";', 
             f'const API_BASE_URL = "{self.local_agent_url}";'),
            ("const baseUrl = 'https://trading-api.308186235.workers.dev';", 
             f"const baseUrl = '{self.local_agent_url}';"),
            ('const baseUrl = "https://trading-api.308186235.workers.dev";', 
             f'const baseUrl = "{self.local_agent_url}";'),
            
            # 其他可能的配置
            ("const API_BASE_URL = 'https://api.aigupiao.me';", 
             f"const API_BASE_URL = '{self.local_agent_url}';"),
            ('const API_BASE_URL = "https://api.aigupiao.me";', 
             f'const API_BASE_URL = "{self.local_agent_url}";'),
            
            # WebSocket配置
            ("const WS_BASE_URL = 'wss://trading-api.308186235.workers.dev/ws';", 
             f"const WS_BASE_URL = '{self.local_ws_url}';"),
            ('const WS_BASE_URL = "wss://trading-api.308186235.workers.dev/ws";', 
             f'const WS_BASE_URL = "{self.local_ws_url}";'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fix_unified_agent_service(self):
        """修复统一Agent服务"""
        print("\n🔧 修复统一Agent服务...")
        
        service_file = "炒股养家/services/unifiedAgentService.js"
        if os.path.exists(service_file):
            # 备份原文件
            backup_name = "unifiedAgentService.js.backup"
            shutil.copy2(service_file, os.path.join(self.backup_dir, backup_name))
            
            # 读取文件
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换API配置
            replacements = [
                ("this.cloudApiUrl = 'https://ai-stock-trading-backend.308186235.workers.dev';", 
                 f"this.cloudApiUrl = '{self.local_agent_url}';"),
                ('this.cloudApiUrl = "https://ai-stock-trading-backend.308186235.workers.dev";', 
                 f'this.cloudApiUrl = "{self.local_agent_url}";'),
                ("this.websocketUrl = 'wss://ai-stock-trading-backend.308186235.workers.dev/ws';", 
                 f"this.websocketUrl = '{self.local_ws_url}';"),
                ('this.websocketUrl = "wss://ai-stock-trading-backend.308186235.workers.dev/ws";', 
                 f'this.websocketUrl = "{self.local_ws_url}";'),
                
                # 本地API地址也更新
                ("this.localApiUrl = 'http://localhost:5000';", 
                 "this.localApiUrl = 'http://localhost:8888';"),
                ('this.localApiUrl = "http://localhost:5000";', 
                 'this.localApiUrl = "http://localhost:8888";'),
            ]
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            # 写回文件
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修复: {service_file}")
        else:
            print(f"⚠️ 文件不存在: {service_file}")
    
    def _verify_fixes(self):
        """验证修复结果"""
        print("\n🔍 验证修复结果...")
        
        files_to_check = [
            "炒股养家/env.js",
            "炒股养家/services/unifiedAgentService.js",
            "frontend/gupiao1/env.js",
            "frontend/stock5/env.js"
        ]
        
        issues_found = []
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否还有错误的API地址
                error_patterns = [
                    "trading-api.308186235.workers.dev",
                    "ai-stock-trading-backend.308186235.workers.dev",
                    "localhost:8000",
                    "localhost:5000"
                ]
                
                for pattern in error_patterns:
                    if pattern in content:
                        issues_found.append(f"{file_path}: 仍包含 {pattern}")
                
                # 检查是否包含正确的地址
                if self.local_agent_url.replace("http://", "") in content:
                    print(f"✅ {file_path}: 配置正确")
                else:
                    issues_found.append(f"{file_path}: 缺少正确的API地址")
        
        if issues_found:
            print("\n❌ 发现问题:")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("\n✅ 所有配置文件验证通过！")

if __name__ == "__main__":
    fixer = FrontendAPIUrlFixer()
    fixer.fix_all_frontend_urls()
