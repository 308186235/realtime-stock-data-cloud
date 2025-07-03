#!/usr/bin/env python3
"""
修复CRITICAL级别安全问题
"""

import os
import json
import shutil
from datetime import datetime

class CriticalSecurityFixer:
    """CRITICAL安全问题修复器"""
    
    def __init__(self):
        self.backup_dir = f"security_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def fix_all_critical_issues(self):
        """修复所有CRITICAL级别问题"""
        print("🚨 修复CRITICAL级别安全问题")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 修复前端API密钥暴露
        self._fix_frontend_api_key_exposure()
        
        # 2. 修复数据库密码明文存储
        self._fix_database_password_exposure()
        
        # 3. 创建环境变量模板
        self._create_env_template()
        
        # 4. 更新配置文件使用环境变量
        self._update_config_files()
        
        print(f"\n✅ CRITICAL问题修复完成！")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print("\n🔑 下一步操作:")
        print("1. 创建 .env 文件并配置正确的密钥")
        print("2. 从代码仓库中删除敏感信息")
        print("3. 重新生成API密钥和数据库密码")
        
    def _fix_frontend_api_key_exposure(self):
        """修复前端API密钥暴露"""
        print("\n🔧 修复前端API密钥暴露...")
        
        file_path = "炒股养家/services/apiKeyManager.js"
        if os.path.exists(file_path):
            # 备份原文件
            shutil.copy2(file_path, os.path.join(self.backup_dir, "apiKeyManager.js.backup"))
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换硬编码的API密钥
            updated_content = content.replace(
                "key: 'QT_wat5QfcJ6N9pDZM5',",
                "key: process.env.STOCK_API_KEY || 'YOUR_API_KEY_HERE',"
            )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已修复: {file_path}")
        
        # 修复api_keys.json
        if os.path.exists("api_keys.json"):
            shutil.move("api_keys.json", os.path.join(self.backup_dir, "api_keys.json.backup"))
            
            # 创建安全的配置文件
            safe_config = {
                "current_key": "prod",
                "keys": {
                    "prod": {
                        "key": "${STOCK_API_KEY}",
                        "name": "生产环境",
                        "expire": "2025-07-26"
                    },
                    "test": {
                        "key": "${STOCK_API_KEY_TEST}",
                        "name": "测试环境", 
                        "expire": "2025-06-27"
                    }
                }
            }
            
            with open("api_keys.json", 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2, ensure_ascii=False)
            
            print("✅ 已修复: api_keys.json")
    
    def _fix_database_password_exposure(self):
        """修复数据库密码暴露"""
        print("\n🔧 修复数据库密码暴露...")
        
        files_to_fix = [
            "backend/supabase_config.py",
            "backend/config/supabase.py"
        ]
        
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                # 备份原文件
                backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
                shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
                
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换硬编码的配置
                replacements = [
                    ('self.url = "https://zzukfxwavknskqcepsjb.supabase.co"', 
                     'self.url = os.getenv("SUPABASE_URL")'),
                    ('self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw"',
                     'self.key = os.getenv("SUPABASE_ANON_KEY")'),
                    ('self.service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g"',
                     'self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")'),
                    ('self.db_url = "postgresql://postgres:[YOUR_PASSWORD]@db.zzukfxwavknskqcepsjb.supabase.co:5432/postgres"',
                     'self.db_url = os.getenv("DATABASE_URL")'),
                    ('WuFeng1234567890oO', '${DATABASE_PASSWORD}'),
                    ('SUPABASE_URL = "https://zzukfxwavknskqcepsjb.supabase.co"',
                     'SUPABASE_URL = os.getenv("SUPABASE_URL")'),
                    ('SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw"',
                     'SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")'),
                    ('SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g"',
                     'SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")')
                ]
                
                updated_content = content
                for old, new in replacements:
                    updated_content = updated_content.replace(old, new)
                
                # 确保导入os模块
                if 'import os' not in updated_content and 'os.getenv' in updated_content:
                    # 在文件开头添加import os
                    lines = updated_content.split('\n')
                    import_line = 'import os'
                    if import_line not in lines:
                        # 找到第一个import语句的位置
                        insert_pos = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                insert_pos = i
                                break
                        lines.insert(insert_pos, import_line)
                        updated_content = '\n'.join(lines)
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ 已修复: {file_path}")
    
    def _create_env_template(self):
        """创建环境变量模板"""
        print("\n🔧 创建环境变量模板...")
        
        env_template = """# 环境变量配置文件
# 复制此文件为 .env 并填入真实值

# 应用配置
APP_ENV=production
DEBUG=false

# 数据库配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
DATABASE_URL=postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres
DATABASE_PASSWORD=your_secure_password_here

# API密钥
STOCK_API_KEY=your_stock_api_key_here
STOCK_API_KEY_TEST=your_test_api_key_here

# JWT配置
JWT_SECRET_KEY=your_very_secure_jwt_secret_key_here

# 其他配置
CHAGUBANG_HOST=l1.chagubang.com
CHAGUBANG_PORT=6380

# 安全提醒:
# 1. 不要将 .env 文件提交到代码仓库
# 2. 定期更换密钥和密码
# 3. 使用强密码和复杂的JWT密钥
"""
        
        with open(".env.template", "w", encoding="utf-8") as f:
            f.write(env_template)
        
        print("✅ 已创建: .env.template")
        
        # 创建.gitignore确保.env不被提交
        gitignore_content = """
# 环境变量文件
.env
.env.local
.env.production
.env.development

# 敏感配置文件
api_keys.json
config/secrets.json

# 备份文件
security_backup_*
audit_report.json
"""
        
        if os.path.exists(".gitignore"):
            with open(".gitignore", "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            if ".env" not in existing_content:
                with open(".gitignore", "a", encoding="utf-8") as f:
                    f.write(gitignore_content)
                print("✅ 已更新: .gitignore")
        else:
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            print("✅ 已创建: .gitignore")
    
    def _update_config_files(self):
        """更新配置文件使用环境变量"""
        print("\n🔧 更新配置文件...")
        
        # 更新JWT配置
        settings_file = "backend/config/settings.py"
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换默认JWT密钥
            updated_content = content.replace(
                'JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt")',
                'JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")\nif not JWT_SECRET_KEY:\n    raise ValueError("JWT_SECRET_KEY environment variable is required")'
            )
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已更新: {settings_file}")

if __name__ == "__main__":
    fixer = CriticalSecurityFixer()
    fixer.fix_all_critical_issues()
