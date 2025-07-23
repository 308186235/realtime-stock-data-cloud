#!/usr/bin/env python3
"""
彻底修复所有localhost地址,改为云端API
"""

import os
import shutil
import re
from datetime import datetime

class LocalhostAddressFixer:
    """localhost地址修复器"""
    
    def __init__(self):
        self.backup_dir = f"localhost_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cloud_api = "https://api.aigupiao.me"
        self.cloud_ws = "wss://api.aigupiao.me/ws"
        
    def fix_all_localhost(self):
        """修复所有localhost地址"""
        print("🔧 彻底修复所有localhost地址")
        print("=" * 50)
        print(f"🎯 目标API: {self.cloud_api}")
        print(f"🎯 目标WebSocket: {self.cloud_ws}")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 需要修复的文件
        files_to_fix = [
            # 主要配置文件
            "炒股养家/env.js",
            "炒股养家/services/unifiedAgentService.js",
            "炒股养家/services/config.js",
            "炒股养家/utils/request.js",
            "炒股养家/auto-trader/request.js",
            
            # 其他前端项目
            "frontend/gupiao1/env.js",
            "frontend/gupiao1/utils/request.js",
            "frontend/gupiao1/auto-trader/request.js",
            "frontend/stock5/env.js",
            "frontend/stock5/utils/request.js",
        ]
        
        fixed_count = 0
        
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                if self._fix_file(file_path):
                    print(f"✅ 已修复: {file_path}")
                    fixed_count += 1
                else:
                    print(f"⚠️ 无需修复: {file_path}")
            else:
                print(f"❌ 文件不存在: {file_path}")
        
        print(f"\n✅ 修复完成!共修复 {fixed_count} 个文件")
        print(f"📁 备份保存在: {self.backup_dir}")
        
        # 验证修复结果
        self._verify_fixes()
        
    def _fix_file(self, file_path):
        """修复单个文件"""
        # 备份原文件
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        
        # 所有需要替换的localhost地址
        replacements = [
            # localhost:8888 (本地交易API)
            ("'http://localhost:8888'", f"'{self.cloud_api}'"),
            ('"http://localhost:8888"', f'"{self.cloud_api}"'),
            ("http://localhost:8888", self.cloud_api),
            
            # localhost:9999 (本地Agent)
            ("'http://localhost:9999'", f"'{self.cloud_api}'"),
            ('"http://localhost:9999"', f'"{self.cloud_api}"'),
            ("http://localhost:9999", self.cloud_api),
            
            # localhost:8000 (旧配置)
            ("'http://localhost:8000'", f"'{self.cloud_api}'"),
            ('"http://localhost:8000"', f'"{self.cloud_api}"'),
            ("http://localhost:8000", self.cloud_api),
            
            # localhost:8080 (代理端口)
            ("'http://localhost:8080'", f"'{self.cloud_api}'"),
            ('"http://localhost:8080"', f'"{self.cloud_api}"'),
            ("http://localhost:8080", self.cloud_api),
            
            # localhost:5000 (旧本地API)
            ("'http://localhost:5000'", f"'{self.cloud_api}'"),
            ('"http://localhost:5000"', f'"{self.cloud_api}"'),
            ("http://localhost:5000", self.cloud_api),
            
            # WebSocket地址
            ("'ws://localhost:9999/ws'", f"'{self.cloud_ws}'"),
            ('"ws://localhost:9999/ws"', f'"{self.cloud_ws}"'),
            ("ws://localhost:9999/ws", self.cloud_ws),
            
            ("'ws://localhost:8888/ws'", f"'{self.cloud_ws}'"),
            ('"ws://localhost:8888/ws"', f'"{self.cloud_ws}"'),
            ("ws://localhost:8888/ws", self.cloud_ws),
            
            ("'ws://localhost:8000/ws'", f"'{self.cloud_ws}'"),
            ('"ws://localhost:8000/ws"', f'"{self.cloud_ws}"'),
            ("ws://localhost:8000/ws", self.cloud_ws),
            
            # 特殊配置项
            ("cloudApiUrl: 'http://localhost:", f"cloudApiUrl: '{self.cloud_api}"),
            ('cloudApiUrl: "http://localhost:', f'cloudApiUrl: "{self.cloud_api}'),
            ("localApiUrl: 'http://localhost:", f"localApiUrl: '{self.cloud_api}"),
            ('localApiUrl: "http://localhost:', f'localApiUrl: "{self.cloud_api}'),
            ("apiBaseUrl: 'http://localhost:", f"apiBaseUrl: '{self.cloud_api}"),
            ('apiBaseUrl: "http://localhost:', f'apiBaseUrl: "{self.cloud_api}'),
            ("baseUrl: 'http://localhost:", f"baseUrl: '{self.cloud_api}"),
            ('baseUrl: "http://localhost:', f'baseUrl: "{self.cloud_api}'),
            
            # WebSocket配置项
            ("websocketUrl: 'ws://localhost:", f"websocketUrl: '{self.cloud_ws}"),
            ('websocketUrl: "ws://localhost:', f'websocketUrl: "{self.cloud_ws}'),
            ("wsUrl: 'ws://localhost:", f"wsUrl: '{self.cloud_ws}"),
            ('wsUrl: "ws://localhost:', f'wsUrl: "{self.cloud_ws}'),
        ]
        
        # 执行替换
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 使用正则表达式处理更复杂的情况
        # 处理端口号后面可能有其他字符的情况
        patterns = [
            (r"'http://localhost:\d+'", f"'{self.cloud_api}'"),
            (r'"http://localhost:\d+"', f'"{self.cloud_api}"'),
            (r"'ws://localhost:\d+[^']*'", f"'{self.cloud_ws}'"),
            (r'"ws://localhost:\d+[^"]*"', f'"{self.cloud_ws}"'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化,写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
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
                
                # 检查是否还有localhost地址
                localhost_patterns = [
                    "localhost:8888",
                    "localhost:9999", 
                    "localhost:8000",
                    "localhost:8080",
                    "localhost:5000"
                ]
                
                for pattern in localhost_patterns:
                    if pattern in content:
                        issues_found.append(f"{file_path}: 仍包含 {pattern}")
                
                # 检查是否包含正确的云端地址
                if self.cloud_api.replace("https://", "") in content:
                    print(f"✅ {file_path}: 配置正确")
                else:
                    issues_found.append(f"{file_path}: 缺少云端API地址")
        
        if issues_found:
            print("\n❌ 发现问题:")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("\n✅ 所有配置文件验证通过!")
        
        print(f"\n🌐 现在前端将连接到:")
        print(f"   API: {self.cloud_api}")
        print(f"   WebSocket: {self.cloud_ws}")

if __name__ == "__main__":
    fixer = LocalhostAddressFixer()
    fixer.fix_all_localhost()
