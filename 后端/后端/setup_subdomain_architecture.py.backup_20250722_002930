#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置子域名架构
自动化配置AI股票交易系统的子域名结构
"""

import os
import json
import shutil
from pathlib import Path

class SubdomainArchitectureSetup:
    def __init__(self):
        self.root_dir = Path(".")
        self.subdomains = {
            'app': {
                'description': '主前端应用',
                'type': 'frontend',
                'priority': 1,
                'tech_stack': 'Vue3/uni-app'
            },
            'api': {
                'description': '后端API服务', 
                'type': 'backend',
                'priority': 1,
                'tech_stack': 'FastAPI/Python'
            },
            'mobile': {
                'description': '移动端H5应用',
                'type': 'frontend',
                'priority': 2,
                'tech_stack': 'uni-app/H5'
            },
            'admin': {
                'description': '管理后台',
                'type': 'frontend', 
                'priority': 3,
                'tech_stack': 'Vue3/React'
            },
            'ws': {
                'description': 'WebSocket实时数据',
                'type': 'service',
                'priority': 2,
                'tech_stack': 'WebSocket/Python'
            },
            'docs': {
                'description': 'API文档中心',
                'type': 'static',
                'priority': 3,
                'tech_stack': 'Static/Markdown'
            }
        }
        
    def log(self, message, level="INFO"):
        """日志输出"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m", 
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{level}] {message}{colors['RESET']}")
        
    def create_subdomain_structure(self):
        """创建子域名目录结构"""
        self.log("🏗️ 创建子域名目录结构...")
        
        # 创建主目录
        subdomains_dir = self.root_dir / "subdomains"
        subdomains_dir.mkdir(exist_ok=True)
        
        for subdomain, config in self.subdomains.items():
            subdomain_dir = subdomains_dir / subdomain
            subdomain_dir.mkdir(exist_ok=True)
            
            # 创建基础文件
            if config['type'] == 'frontend':
                self.create_frontend_template(subdomain_dir, subdomain, config)
            elif config['type'] == 'backend':
                self.create_backend_template(subdomain_dir, subdomain, config)
            elif config['type'] == 'static':
                self.create_static_template(subdomain_dir, subdomain, config)
                
            self.log(f"✅ {subdomain}.aigupiao.me - {config['description']}")
            
    def create_frontend_template(self, dir_path, subdomain, config):
        """创建前端模板"""
        # 创建index.html
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['description']} - AI股票交易系统</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 600px;
        }}
        .logo {{ font-size: 3rem; margin-bottom: 1rem; }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
        .subtitle {{ font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.9; }}
        .info {{ background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0; }}
        .btn {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white; border: none; padding: 1rem 2rem;
            border-radius: 25px; cursor: pointer; margin: 0.5rem;
            transition: transform 0.3s ease;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>{config['description']}</h1>
        <p class="subtitle">{subdomain}.aigupiao.me</p>
        
        <div class="info">
            <h3>📋 服务信息</h3>
            <p>类型: {config['type']}</p>
            <p>技术栈: {config['tech_stack']}</p>
            <p>优先级: P{config['priority']}</p>
            <p>状态: 🚧 开发中</p>
        </div>
        
        <button class="btn" onclick="goToMain()">返回主站</button>
        <button class="btn" onclick="showInfo()">服务信息</button>
        
        <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">
            <p>🌐 AI股票交易系统 - 子域名架构</p>
            <p>📅 创建时间: <span id="createTime"></span></p>
        </div>
    </div>

    <script>
        document.getElementById('createTime').textContent = new Date().toLocaleString('zh-CN');
        
        function goToMain() {{
            window.location.href = 'https://aigupiao.me';
        }}
        
        function showInfo() {{
            alert(`🔧 服务详情:\\n\\n📍 域名: {subdomain}.aigupiao.me\\n🏷️ 类型: {config['type']}\\n⚙️ 技术栈: {config['tech_stack']}\\n📊 优先级: P{config['priority']}\\n\\n🚧 当前状态: 开发中\\n📅 预计上线: 待定`);
        }}
    </script>
</body>
</html>"""
        
        with open(dir_path / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # 创建配置文件
        config_content = {
            "name": f"{subdomain}.aigupiao.me",
            "type": config['type'],
            "description": config['description'],
            "tech_stack": config['tech_stack'],
            "priority": config['priority'],
            "status": "development",
            "created_at": "2024-12-30"
        }
        
        with open(dir_path / "config.json", "w", encoding="utf-8") as f:
            json.dump(config_content, f, indent=2, ensure_ascii=False)
            
    def create_backend_template(self, dir_path, subdomain, config):
        """创建后端模板"""
        # 创建简单的API响应页面
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['description']} - API服务</title>
    <style>
        body {{ font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 2rem; }}
        .terminal {{ background: #000; padding: 1rem; border-radius: 5px; border: 1px solid #333; }}
        .api-info {{ background: #222; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
        .endpoint {{ color: #00aaff; }}
        .method {{ color: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="terminal">
        <h1>🔧 {config['description']}</h1>
        <p>域名: {subdomain}.aigupiao.me</p>
        <p>状态: 🚧 开发中</p>
        
        <div class="api-info">
            <h3>📡 API端点 (计划中)</h3>
            <p><span class="method">GET</span> <span class="endpoint">/api/health</span> - 健康检查</p>
            <p><span class="method">GET</span> <span class="endpoint">/api/stocks</span> - 股票数据</p>
            <p><span class="method">POST</span> <span class="endpoint">/api/trade</span> - 交易接口</p>
            <p><span class="method">GET</span> <span class="endpoint">/api/account</span> - 账户信息</p>
        </div>
        
        <div class="api-info">
            <h3>🔒 认证方式</h3>
            <p>Bearer Token / JWT</p>
        </div>
        
        <div class="api-info">
            <h3>📊 技术栈</h3>
            <p>{config['tech_stack']}</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(dir_path / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
    def create_static_template(self, dir_path, subdomain, config):
        """创建静态站点模板"""
        self.create_frontend_template(dir_path, subdomain, config)
        
    def create_cloudflare_pages_configs(self):
        """创建Cloudflare Pages配置文件"""
        self.log("📄 创建Cloudflare Pages配置...")
        
        for subdomain, config in self.subdomains.items():
            if config['type'] in ['frontend', 'static']:
                # 创建_redirects文件
                redirects_content = f"""# {subdomain}.aigupiao.me redirects
/api/* https://api.aigupiao.me/api/:splat 200
/* /index.html 200
"""
                
                subdomain_dir = self.root_dir / "subdomains" / subdomain
                with open(subdomain_dir / "_redirects", "w", encoding="utf-8") as f:
                    f.write(redirects_content)
                    
    def create_dns_configuration_guide(self):
        """创建DNS配置指南"""
        self.log("📋 创建DNS配置指南...")
        
        dns_guide = """# Cloudflare DNS配置指南

## 🌐 子域名DNS记录配置

### A记录 (指向Cloudflare Pages)
```
类型    名称    内容                代理状态
A       app     104.21.x.x         已代理  
A       api     104.21.x.x         已代理
A       mobile  104.21.x.x         已代理
A       admin   104.21.x.x         已代理
A       ws      104.21.x.x         已代理
A       docs    104.21.x.x         已代理
```

### CNAME记录 (别名指向)
```
类型     名称        内容                代理状态
CNAME    www         aigupiao.me        已代理
CNAME    data        api.aigupiao.me    已代理
CNAME    status      app.aigupiao.me    已代理
```

## 🔧 Cloudflare Pages项目配置

### 1. app.aigupiao.me
- 构建命令: `echo "Static deployment"`
- 构建输出目录: `subdomains/app`
- 自定义域名: `app.aigupiao.me`

### 2. api.aigupiao.me  
- 部署到: Railway/Render/Cloudflare Workers
- 自定义域名: `api.aigupiao.me`

### 3. mobile.aigupiao.me
- 构建命令: `echo "Mobile deployment"`
- 构建输出目录: `subdomains/mobile`
- 自定义域名: `mobile.aigupiao.me`

## 📋 配置步骤

1. 登录Cloudflare Dashboard
2. 选择域名: aigupiao.me
3. 进入DNS设置
4. 添加上述DNS记录
5. 进入Pages设置
6. 为每个子域名创建独立的Pages项目
7. 配置自定义域名

## 🔒 SSL证书

Cloudflare会自动为所有子域名提供SSL证书，包括通配符证书 *.aigupiao.me
"""
        
        with open(self.root_dir / "DNS_CONFIGURATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(dns_guide)
            
    def create_deployment_scripts(self):
        """创建部署脚本"""
        self.log("🚀 创建部署脚本...")
        
        # 创建主部署脚本
        deploy_script = """#!/bin/bash
# AI股票交易系统 - 子域名部署脚本

echo "🚀 开始部署子域名架构..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 提交当前更改..."
    git add .
    git commit -m "子域名架构部署: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

echo "✅ 部署完成！"
echo "📋 下一步:"
echo "1. 在Cloudflare Pages中为每个子域名创建项目"
echo "2. 配置DNS记录"
echo "3. 设置自定义域名"

echo ""
echo "🌐 子域名列表:"
echo "• app.aigupiao.me - 主前端应用"
echo "• api.aigupiao.me - 后端API服务"
echo "• mobile.aigupiao.me - 移动端应用"
echo "• admin.aigupiao.me - 管理后台"
echo "• ws.aigupiao.me - WebSocket服务"
echo "• docs.aigupiao.me - 文档中心"
"""
        
        with open(self.root_dir / "deploy_subdomains.sh", "w", encoding="utf-8") as f:
            f.write(deploy_script)
            
        # 设置执行权限 (在Windows上可能不需要)
        try:
            os.chmod(self.root_dir / "deploy_subdomains.sh", 0o755)
        except:
            pass
            
    def run_setup(self):
        """运行完整设置"""
        self.log("🎯 开始设置子域名架构...")
        self.log("="*60)
        
        # 1. 创建目录结构
        self.create_subdomain_structure()
        
        # 2. 创建配置文件
        self.create_cloudflare_pages_configs()
        
        # 3. 创建DNS指南
        self.create_dns_configuration_guide()
        
        # 4. 创建部署脚本
        self.create_deployment_scripts()
        
        self.log("="*60)
        self.log("🎉 子域名架构设置完成！", "SUCCESS")
        self.log("📁 已创建 subdomains/ 目录结构", "SUCCESS")
        self.log("📋 已创建 DNS_CONFIGURATION_GUIDE.md", "SUCCESS")
        self.log("🚀 已创建 deploy_subdomains.sh 部署脚本", "SUCCESS")
        
        self.log("\n📋 下一步操作:")
        self.log("1. 运行: bash deploy_subdomains.sh")
        self.log("2. 在Cloudflare中配置DNS记录")
        self.log("3. 为每个子域名创建Pages项目")
        self.log("4. 配置自定义域名")

if __name__ == "__main__":
    setup = SubdomainArchitectureSetup()
    setup.run_setup()
