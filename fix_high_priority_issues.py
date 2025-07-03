#!/usr/bin/env python3
"""
修复HIGH级别问题
"""

import os
import shutil
from datetime import datetime

class HighPriorityFixer:
    """HIGH级别问题修复器"""
    
    def __init__(self):
        self.backup_dir = f"high_priority_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def fix_all_high_issues(self):
        """修复所有HIGH级别问题"""
        print("🟠 修复HIGH级别问题")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 配置Supabase service_role密钥
        self._fix_supabase_service_key()
        
        # 2. 修复数据库连接字符串
        self._fix_database_connection_string()
        
        # 3. 修复其他配置文件中的硬编码
        self._fix_remaining_hardcoded_configs()
        
        print(f"\n✅ HIGH级别问题修复完成！")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        
    def _fix_supabase_service_key(self):
        """修复Supabase service_role密钥配置"""
        print("\n🔧 修复Supabase service_role密钥...")
        
        file_path = "backend/supabase_config.py"
        if os.path.exists(file_path):
            # 备份原文件
            shutil.copy2(file_path, os.path.join(self.backup_dir, "supabase_config.py.backup"))
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换空的service_key
            updated_content = content.replace(
                'self.service_key = ""  # 需要从设置中获取service_role key',
                'self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")'
            )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已修复: {file_path}")
    
    def _fix_database_connection_string(self):
        """修复数据库连接字符串"""
        print("\n🔧 修复数据库连接字符串...")
        
        file_path = "backend/supabase_config.py"
        if os.path.exists(file_path):
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换占位符
            updated_content = content.replace(
                '"postgresql://postgres:[YOUR_PASSWORD]@db.zzukfxwavknskqcepsjb.supabase.co:5432/postgres"',
                'os.getenv("DATABASE_URL")'
            )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已修复数据库连接字符串")
    
    def _fix_remaining_hardcoded_configs(self):
        """修复其他配置文件中的硬编码"""
        print("\n🔧 修复其他硬编码配置...")
        
        # 修复前端Supabase配置
        frontend_config = "frontend/src/config/supabase.js"
        if os.path.exists(frontend_config):
            # 备份原文件
            shutil.copy2(frontend_config, os.path.join(self.backup_dir, "supabase.js.backup"))
            
            # 读取文件
            with open(frontend_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换硬编码配置
            updated_content = content.replace(
                "const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://zzukfxwavknskqcepsjb.supabase.co'",
                "const supabaseUrl = process.env.REACT_APP_SUPABASE_URL"
            ).replace(
                "const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'",
                "const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY"
            )
            
            # 添加错误检查
            if "if (!supabaseUrl || !supabaseAnonKey)" not in updated_content:
                updated_content = updated_content.replace(
                    "// 创建Supabase客户端",
                    """// 检查必要的环境变量
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing required Supabase environment variables');
}

// 创建Supabase客户端"""
                )
            
            # 写回文件
            with open(frontend_config, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已修复: {frontend_config}")

if __name__ == "__main__":
    fixer = HighPriorityFixer()
    fixer.fix_all_high_issues()
