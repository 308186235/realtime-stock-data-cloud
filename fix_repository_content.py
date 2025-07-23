#!/usr/bin/env python3
"""
修复GitHub仓库内容 - 将真正的项目文件移动到仓库中
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class RepositoryContentFixer:
    """仓库内容修复器"""
    
    def __init__(self):
        self.frontend_repo = "stock-trading-frontend"
        self.backend_repo = "stock-trading-backend"
        self.backup_dir = f"repo_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def fix_frontend_repository(self):
        """修复前端仓库内容"""
        print("🔧 修复前端仓库内容...")
        print("=" * 50)
        
        # 创建备份
        if os.path.exists(self.frontend_repo):
            shutil.copytree(self.frontend_repo, f"{self.backup_dir}/frontend_backup")
            print(f"✅ 创建前端备份: {self.backup_dir}/frontend_backup")
        
        # 1. 复制关键配置文件
        self._copy_frontend_config_files()
        
        # 2. 复制炒股养家项目内容
        self._copy_chaoguyangja_content()
        
        # 3. 复制其他前端项目内容
        self._copy_other_frontend_content()
        
        # 4. 创建完整的package.json
        self._create_complete_package_json()
        
        print("✅ 前端仓库内容修复完成")
    
    def _copy_frontend_config_files(self):
        """复制前端配置文件"""
        print("📄 复制前端配置文件...")
        
        config_files = [
            ("炒股养家_template_backup/App.vue", "App.vue"),
            ("炒股养家_template_backup/main.js", "main.js"),
            ("炒股养家_template_backup/pages.json", "pages.json"),
            ("炒股养家_template_backup/manifest.json", "manifest.json"),
            ("炒股养家_template_backup/uni.scss", "uni.scss"),
            ("炒股养家_template_backup/index.html", "index.html"),
        ]
        
        for src, dst in config_files:
            if os.path.exists(src):
                dst_path = os.path.join(self.frontend_repo, dst)
                shutil.copy2(src, dst_path)
                print(f"  ✅ 复制: {src} → {dst_path}")
            else:
                print(f"  ⚠️ 文件不存在: {src}")
    
    def _copy_chaoguyangja_content(self):
        """复制炒股养家项目内容"""
        print("📁 复制炒股养家项目内容...")
        
        source_dirs = [
            "移动端/炒股养家/pages",
            "移动端/炒股养家/components", 
            "移动端/炒股养家/utils",
            "移动端/炒股养家/services",
            "移动端/炒股养家/static",
            "移动端/炒股养家/auto-trader",
            "移动端/炒股养家/portfolio",
        ]
        
        for src_dir in source_dirs:
            if os.path.exists(src_dir):
                dst_dir = os.path.join(self.frontend_repo, os.path.basename(src_dir))
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                print(f"  ✅ 复制目录: {src_dir} → {dst_dir}")
            else:
                print(f"  ⚠️ 目录不存在: {src_dir}")
    
    def _copy_other_frontend_content(self):
        """复制其他前端项目内容"""
        print("📁 复制其他前端内容...")
        
        # 复制环境配置文件
        env_files = [
            "移动端/src/index.js",
            "移动端/static/logo.png",
        ]
        
        for src_file in env_files:
            if os.path.exists(src_file):
                # 创建目标目录结构
                rel_path = os.path.relpath(src_file, "移动端")
                dst_path = os.path.join(self.frontend_repo, rel_path)
                dst_dir = os.path.dirname(dst_path)
                
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src_file, dst_path)
                print(f"  ✅ 复制文件: {src_file} → {dst_path}")
    
    def _create_complete_package_json(self):
        """创建完整的package.json"""
        print("📦 创建完整的package.json...")
        
        package_json = {
            "name": "stock-trading-frontend",
            "version": "1.0.0",
            "description": "股票交易系统前端 - 基于uni-app开发的移动端应用",
            "main": "main.js",
            "scripts": {
                "dev:h5": "uni build --watch",
                "build:h5": "uni build",
                "dev:mp-weixin": "uni build -p mp-weixin --watch",
                "build:mp-weixin": "uni build -p mp-weixin",
                "dev:app": "uni build -p app --watch",
                "build:app": "uni build -p app"
            },
            "dependencies": {
                "@dcloudio/uni-app": "^3.0.0",
                "@dcloudio/uni-components": "^3.0.0",
                "@dcloudio/uni-h5": "^3.0.0",
                "@dcloudio/uni-mp-weixin": "^3.0.0",
                "vue": "^3.2.0",
                "vuex": "^4.0.0",
                "axios": "^1.0.0"
            },
            "devDependencies": {
                "@dcloudio/uni-cli-shared": "^3.0.0",
                "@dcloudio/vite-plugin-uni": "^3.0.0",
                "vite": "^4.0.0"
            },
            "keywords": [
                "uni-app",
                "vue",
                "stock-trading",
                "mobile-app"
            ],
            "author": "Stock Trading System",
            "license": "MIT"
        }
        
        package_path = os.path.join(self.frontend_repo, "package.json")
        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 创建: {package_path}")
    
    def fix_backend_repository(self):
        """修复后端仓库内容"""
        print("\n🔧 修复后端仓库内容...")
        print("=" * 50)
        
        # 创建备份
        if os.path.exists(self.backend_repo):
            shutil.copytree(self.backend_repo, f"{self.backup_dir}/backend_backup")
            print(f"✅ 创建后端备份: {self.backup_dir}/backend_backup")
        
        # 1. 复制真正的后端文件
        self._copy_real_backend_content()
        
        # 2. 创建完整的requirements.txt
        self._create_complete_requirements()
        
        print("✅ 后端仓库内容修复完成")
    
    def _copy_real_backend_content(self):
        """复制真正的后端内容"""
        print("📁 复制真正的后端内容...")
        
        # 主要后端文件
        backend_files = [
            ("后端/后端/main.py", "main.py"),
            ("后端/后端/config.py", "config.py"),
            ("后端/后端/requirements.txt", "requirements.txt"),
            ("后端/后端/Dockerfile", "Dockerfile"),
            ("后端/后端/docker-compose.yml", "docker-compose.yml"),
        ]
        
        for src, dst in backend_files:
            if os.path.exists(src):
                dst_path = os.path.join(self.backend_repo, dst)
                shutil.copy2(src, dst_path)
                print(f"  ✅ 复制文件: {src} → {dst_path}")
        
        # 后端目录
        backend_dirs = [
            ("后端/后端/api", "api"),
            ("后端/后端/backend", "backend"),
            ("后端/后端/database", "database"),
            ("后端/后端/middleware", "middleware"),
            ("后端/后端/tests", "tests"),
        ]
        
        for src_dir, dst_name in backend_dirs:
            if os.path.exists(src_dir):
                dst_dir = os.path.join(self.backend_repo, dst_name)
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                print(f"  ✅ 复制目录: {src_dir} → {dst_dir}")
    
    def _create_complete_requirements(self):
        """创建完整的requirements.txt"""
        print("📦 创建完整的requirements.txt...")
        
        requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
            "python-multipart>=0.0.6",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "websockets>=12.0",
            "pandas>=2.1.0",
            "numpy>=1.24.0",
            "aiofiles>=23.2.1",
            "httpx>=0.25.0"
        ]
        
        req_path = os.path.join(self.backend_repo, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
        
        print(f"  ✅ 创建: {req_path}")
    
    def run_fix(self):
        """运行修复"""
        print("🚀 开始修复GitHub仓库内容...")
        print("=" * 60)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 修复前端仓库
        self.fix_frontend_repository()
        
        # 修复后端仓库  
        self.fix_backend_repository()
        
        print(f"\n🎉 仓库内容修复完成!")
        print(f"📁 备份目录: {self.backup_dir}")
        print("\n📋 下一步:")
        print("1. 检查修复后的仓库内容")
        print("2. 提交并推送到GitHub")
        print("3. 验证项目可以正常运行")

if __name__ == "__main__":
    fixer = RepositoryContentFixer()
    fixer.run_fix()
