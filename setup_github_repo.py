"""
GitHub仓库设置和推送脚本
自动创建Git仓库并推送到GitHub
"""
import os
import subprocess
import sys
from datetime import datetime

class GitHubRepoSetup:
    """GitHub仓库设置器"""
    
    def __init__(self):
        self.repo_name = "realtime-stock-data-cloud"
        self.description = "云端实时股票数据推送服务 - API Key: QT_wat5QfcJ6N9pDZM5"
        self.current_dir = os.getcwd()
        
    def check_git_installed(self):
        """检查Git是否安装"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git已安装: {result.stdout.strip()}")
                return True
            else:
                print("❌ Git未安装")
                return False
        except FileNotFoundError:
            print("❌ Git未安装或不在PATH中")
            return False
    
    def init_git_repo(self):
        """初始化Git仓库"""
        try:
            # 检查是否已经是Git仓库
            if os.path.exists('.git'):
                print("✅ Git仓库已存在")
                return True
            
            # 初始化Git仓库
            result = subprocess.run(['git', 'init'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Git仓库初始化成功")
                return True
            else:
                print(f"❌ Git仓库初始化失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 初始化Git仓库时出错: {str(e)}")
            return False
    
    def create_gitignore(self):
        """创建.gitignore文件"""
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.env.local
.env.development
.env.production

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# 项目特定
data/
logs/
*.log
temp/
tmp/

# 敏感信息
config/secrets.py
.env.secret
"""
        
        try:
            with open('.gitignore', 'w', encoding='utf-8') as f:
                f.write(gitignore_content.strip())
            print("✅ .gitignore文件已创建")
            return True
        except Exception as e:
            print(f"❌ 创建.gitignore失败: {str(e)}")
            return False
    
    def add_and_commit(self):
        """添加文件并提交"""
        try:
            # 添加所有文件
            result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ 添加文件失败: {result.stderr}")
                return False
            
            # 提交
            commit_message = f"Initial commit: 云端实时股票数据服务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 文件已提交到本地仓库")
                return True
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 提交过程中出错: {str(e)}")
            return False
    
    def show_github_instructions(self):
        """显示GitHub操作指南"""
        print("\n" + "="*80)
        print("🌐 GitHub仓库创建指南")
        print("="*80)
        
        print("\n📋 步骤1: 在GitHub上创建仓库")
        print("1. 访问 https://github.com")
        print("2. 点击右上角的 '+' 按钮")
        print("3. 选择 'New repository'")
        print("4. 填写仓库信息:")
        print(f"   - Repository name: {self.repo_name}")
        print(f"   - Description: {self.description}")
        print("   - Public/Private: 选择Public (免费部署)")
        print("   - ❌ 不要勾选 'Initialize this repository with a README'")
        print("   - ❌ 不要添加 .gitignore 或 license")
        print("5. 点击 'Create repository'")
        
        print("\n📋 步骤2: 连接本地仓库到GitHub")
        print("复制并执行以下命令 (替换YOUR_USERNAME为您的GitHub用户名):")
        print()
        print("```bash")
        print(f"git remote add origin https://github.com/YOUR_USERNAME/{self.repo_name}.git")
        print("git branch -M main")
        print("git push -u origin main")
        print("```")
        
        print("\n📋 步骤3: 验证推送成功")
        print("1. 刷新GitHub仓库页面")
        print("2. 确认所有文件都已上传")
        print("3. 检查README_CLOUD_DEPLOY.md是否显示正确")
        
        print("\n📋 步骤4: 部署到云端")
        print("选择以下平台之一进行部署:")
        print()
        print("🚂 Railway (推荐):")
        print("1. 访问 https://railway.app")
        print("2. 点击 'New Project' -> 'Deploy from GitHub repo'")
        print("3. 选择您的仓库")
        print("4. 设置环境变量:")
        print("   MARKET_DATA_API_KEY=QT_wat5QfcJ6N9pDZM5")
        print("   ENVIRONMENT=production")
        print("   REALTIME_DATA_ENABLED=true")
        print("5. 等待部署完成")
        print()
        print("🎨 Render (备选):")
        print("1. 访问 https://render.com")
        print("2. 点击 'New' -> 'Web Service'")
        print("3. 连接GitHub仓库")
        print("4. 配置:")
        print("   Build Command: pip install -r requirements_cloud.txt")
        print("   Start Command: python cloud_app.py")
        print("5. 设置环境变量 (同上)")
        
        print("\n📋 步骤5: 测试部署")
        print("部署完成后访问:")
        print("- 服务首页: https://your-app.platform.com/")
        print("- 健康检查: https://your-app.platform.com/api/health")
        print("- 监控面板: https://your-app.platform.com/static/cloud_test.html")
        
        print("="*80)
    
    def create_deployment_files_list(self):
        """创建部署文件清单"""
        files_to_check = [
            'cloud_app.py',
            'requirements_cloud.txt',
            'railway.json',
            'render.yaml',
            'Dockerfile',
            'Procfile',
            'runtime.txt',
            'static/cloud_test.html',
            'backend/api/routers/cloud_realtime_api.py',
            'README_CLOUD_DEPLOY.md'
        ]
        
        print("\n📁 检查部署文件:")
        missing_files = []
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} (缺失)")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️ 缺失 {len(missing_files)} 个文件，可能影响部署")
            return False
        else:
            print("\n✅ 所有部署文件都已准备就绪")
            return True
    
    def setup_repository(self):
        """设置仓库"""
        print("🚀 开始设置GitHub仓库...")
        print(f"📂 当前目录: {self.current_dir}")
        print(f"📦 仓库名称: {self.repo_name}")
        print()
        
        # 检查Git
        if not self.check_git_installed():
            print("请先安装Git: https://git-scm.com/downloads")
            return False
        
        # 检查部署文件
        if not self.create_deployment_files_list():
            print("⚠️ 部分文件缺失，但可以继续...")
        
        # 初始化Git仓库
        if not self.init_git_repo():
            return False
        
        # 创建.gitignore
        if not self.create_gitignore():
            return False
        
        # 添加并提交
        if not self.add_and_commit():
            return False
        
        # 显示GitHub指南
        self.show_github_instructions()
        
        return True

def main():
    """主函数"""
    setup = GitHubRepoSetup()
    
    print("🌐 云端实时股票数据服务 - GitHub仓库设置")
    print("API Key: QT_wat5QfcJ6N9pDZM5")
    print("="*60)
    
    try:
        success = setup.setup_repository()
        
        if success:
            print("\n🎉 本地Git仓库设置完成！")
            print("📋 请按照上述指南在GitHub上创建仓库并推送代码")
            print("🚀 然后选择Railway或Render进行云端部署")
        else:
            print("\n❌ 仓库设置失败，请检查错误信息")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 设置过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()
