#!/usr/bin/env python3
"""
整合依赖包管理
解决多个requirements.txt文件冲突
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class DependencyFixer:
    """依赖包管理修复器"""
    
    def __init__(self):
        self.backup_dir = f"deps_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def fix_dependencies(self):
        """修复依赖包管理"""
        print("📦 整合依赖包管理")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 收集所有requirements文件
        req_files = self._collect_requirements_files()
        
        # 2. 合并依赖包
        merged_deps = self._merge_dependencies(req_files)
        
        # 3. 创建统一的requirements文件
        self._create_unified_requirements(merged_deps)
        
        # 4. 清理重复文件
        self._cleanup_duplicate_files(req_files)
        
        print(f"\n✅ 依赖包管理整合完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        
    def _collect_requirements_files(self):
        """收集所有requirements文件"""
        print("\n🔍 收集requirements文件...")
        
        req_files = []
        search_patterns = [
            "requirements.txt",
            "backend/requirements.txt", 
            "backend/requirements_supabase.txt",
            "requirements_cloud.txt",
            "requirements_local.txt"
        ]
        
        for pattern in search_patterns:
            if os.path.exists(pattern):
                req_files.append(pattern)
                print(f"  📄 发现: {pattern}")
        
        return req_files
    
    def _merge_dependencies(self, req_files):
        """合并依赖包"""
        print("\n🔧 合并依赖包...")
        
        all_deps = {}
        
        for req_file in req_files:
            print(f"  📖 处理: {req_file}")
            
            # 备份原文件
            backup_name = req_file.replace("/", "_").replace("\\", "_") + ".backup"
            shutil.copy2(req_file, os.path.join(self.backup_dir, backup_name))
            
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 解析包名和版本
                        if '==' in line:
                            pkg_name, version = line.split('==', 1)
                        elif '>=' in line:
                            pkg_name, version = line.split('>=', 1)
                            version = f">={version}"
                        else:
                            pkg_name = line
                            version = ""
                        
                        pkg_name = pkg_name.strip()
                        
                        # 处理版本冲突
                        if pkg_name in all_deps:
                            existing_version = all_deps[pkg_name]
                            if existing_version != version and version:
                                print(f"    ⚠️ 版本冲突: {pkg_name} ({existing_version} vs {version})")
                                # 选择更严格的版本(==优于>=)
                                if '==' in version:
                                    all_deps[pkg_name] = version
                                elif '==' not in existing_version:
                                    all_deps[pkg_name] = version
                        else:
                            all_deps[pkg_name] = version
                            
            except Exception as e:
                print(f"    ❌ 处理失败: {e}")
        
        print(f"  ✅ 合并完成,共 {len(all_deps)} 个包")
        return all_deps
    
    def _create_unified_requirements(self, merged_deps):
        """创建统一的requirements文件"""
        print("\n📝 创建统一requirements文件...")
        
        # 按类别组织依赖包
        categories = {
            "web_framework": ["fastapi", "uvicorn", "starlette", "pydantic"],
            "database": ["supabase", "psycopg2", "psycopg2-binary", "sqlalchemy"],
            "http_client": ["requests", "httpx", "aiohttp"],
            "data_processing": ["pandas", "numpy", "redis"],
            "windows_api": ["pywin32", "win32gui", "win32api"],
            "websocket": ["websockets", "python-socketio"],
            "utilities": ["python-dotenv", "schedule", "asyncio"],
            "development": ["pytest", "black", "flake8"]
        }
        
        # 创建主requirements文件
        main_requirements = []
        main_requirements.append("# 智能交易系统 - 统一依赖包配置")
        main_requirements.append(f"# 生成时间: {datetime.now().isoformat()}")
        main_requirements.append("")
        
        # 按类别添加依赖
        for category, packages in categories.items():
            category_deps = []
            for pkg in packages:
                if pkg in merged_deps:
                    version = merged_deps[pkg]
                    if version:
                        category_deps.append(f"{pkg}{version}")
                    else:
                        category_deps.append(pkg)
                    # 从merged_deps中移除已处理的包
                    del merged_deps[pkg]
            
            if category_deps:
                main_requirements.append(f"# {category.replace('_', ' ').title()}")
                main_requirements.extend(category_deps)
                main_requirements.append("")
        
        # 添加其他未分类的包
        if merged_deps:
            main_requirements.append("# 其他依赖")
            for pkg, version in sorted(merged_deps.items()):
                if version:
                    main_requirements.append(f"{pkg}{version}")
                else:
                    main_requirements.append(pkg)
            main_requirements.append("")
        
        # 写入主requirements文件
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(main_requirements))
        
        print("✅ 已创建: requirements.txt")
        
        # 创建开发环境requirements
        dev_requirements = [
            "# 开发环境额外依赖",
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.17.0",
            ""
        ]
        
        with open("requirements-dev.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(dev_requirements))
        
        print("✅ 已创建: requirements-dev.txt")
        
        # 创建生产环境requirements
        prod_requirements = [
            "# 生产环境依赖(基于主requirements)",
            "-r requirements.txt",
            "",
            "# 生产环境特定包",
            "gunicorn>=20.1.0",
            "supervisor>=4.2.0",
            ""
        ]
        
        with open("requirements-prod.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(prod_requirements))
        
        print("✅ 已创建: requirements-prod.txt")
    
    def _cleanup_duplicate_files(self, req_files):
        """清理重复文件"""
        print("\n🧹 清理重复文件...")
        
        # 保留主requirements.txt,移除其他文件
        for req_file in req_files:
            if req_file != "requirements.txt":
                try:
                    os.remove(req_file)
                    print(f"  🗑️ 已删除: {req_file}")
                except Exception as e:
                    print(f"  ❌ 删除失败 {req_file}: {e}")
        
        # 创建依赖管理说明文件
        readme_content = """# 依赖包管理说明

## 文件说明

- `requirements.txt` - 主要依赖包,包含所有核心功能所需的包
- `requirements-dev.txt` - 开发环境额外依赖,包含测试,代码格式化等工具
- `requirements-prod.txt` - 生产环境依赖,基于主requirements并添加生产环境特定包

## 安装说明

### 开发环境
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 生产环境
```bash
pip install -r requirements-prod.txt
```

### 虚拟环境(推荐)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
```

## 维护说明

1. 新增依赖时,请添加到 `requirements.txt` 并指定版本号
2. 开发工具依赖请添加到 `requirements-dev.txt`
3. 定期更新依赖包版本,确保安全性
4. 使用 `pip freeze > requirements-freeze.txt` 生成精确版本快照

## 版本管理

- 使用 `==` 固定版本号确保环境一致性
- 关键依赖包必须指定版本
- 定期检查包的安全更新
"""
        
        with open("DEPENDENCIES.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ 已创建依赖管理说明: DEPENDENCIES.md")

if __name__ == "__main__":
    fixer = DependencyFixer()
    fixer.fix_dependencies()
