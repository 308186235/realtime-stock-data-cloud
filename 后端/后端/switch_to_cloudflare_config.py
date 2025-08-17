#!/usr/bin/env python3
"""
切换到Cloudflare配置工具
将所有Netlify配置替换为Cloudflare配置
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List

class CloudflareConfigSwitcher:
    """Cloudflare配置切换器"""
    
    def __init__(self):
        self.cloudflare_domains = {
            "main": "aigupiao.me",
            "api": "api.aigupiao.me",
            "app": "app.aigupiao.me",
            "mobile": "mobile.aigupiao.me",
            "admin": "admin.aigupiao.me"
        }
        
        self.netlify_patterns = [
            r'netlify',
            r'\.netlify\.app',
            r'\.netlify\.com',
            r'netlify-functions',
            r'Netlify交易账户',
            r'NTF888888'
        ]
        
    def run_switch(self):
        """运行切换"""
        print("🔄 切换到Cloudflare配置...")
        print("=" * 50)
        
        # 1. 更新前端环境配置
        self._update_frontend_configs()
        
        # 2. 更新API配置
        self._update_api_configs()
        
        # 3. 更新后端CORS配置
        self._update_backend_cors()
        
        # 4. 创建Cloudflare部署配置
        self._create_cloudflare_configs()
        
        # 5. 删除Netlify相关文件
        self._cleanup_netlify_files()
        
        # 6. 生成配置报告
        self._generate_config_report()
        
        print("\n✅ 切换到Cloudflare配置完成!")
    
    def _update_frontend_configs(self):
        """更新前端配置"""
        print("\n🎨 更新前端配置...")
        
        frontend_configs = [
            "炒股养家/env.js",
            "frontend/gupiao1/env.js", 
            "frontend/stock5/env.js"
        ]
        
        for config_file in frontend_configs:
            if os.path.exists(config_file):
                self._update_env_file(config_file)
                print(f"✅ 更新: {config_file}")
    
    def _update_env_file(self, file_path):
        """更新环境配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换API地址
        content = re.sub(
            r"apiBaseUrl:\s*['\"][^'\"]*['\"]",
            f"apiBaseUrl: 'https://{self.cloudflare_domains['api']}'",
            content
        )
        
        # 替换WebSocket地址
        content = re.sub(
            r"wsUrl:\s*['\"][^'\"]*['\"]",
            f"wsUrl: 'wss://{self.cloudflare_domains['api']}/ws'",
            content
        )
        
        # 移除Netlify相关配置
        for pattern in self.netlify_patterns:
            content = re.sub(pattern, 'cloudflare', content, flags=re.IGNORECASE)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _update_api_configs(self):
        """更新API配置"""
        print("\n🔌 更新API配置...")
        
        api_files = [
            "炒股养家/services/config.js",
            "frontend/gupiao1/services/config.js",
            "frontend/stock5/services/config.js"
        ]
        
        for api_file in api_files:
            if os.path.exists(api_file):
                self._update_api_file(api_file)
                print(f"✅ 更新: {api_file}")
    
    def _update_api_file(self, file_path):
        """更新API配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换基础URL
        content = re.sub(
            r"baseUrl\s*=.*",
            f"const baseUrl = 'https://{self.cloudflare_domains['api']}';",
            content
        )
        
        # 替换API_BASE_URL
        content = re.sub(
            r"API_BASE_URL.*=.*",
            f"const API_BASE_URL = 'https://{self.cloudflare_domains['api']}';",
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _update_backend_cors(self):
        """更新后端CORS配置"""
        print("\n🌐 更新后端CORS配置...")
        
        backend_files = [
            "backend/app.py",
            "cloud_app.py",
            "backend/start_server.py"
        ]
        
        for backend_file in backend_files:
            if os.path.exists(backend_file):
                self._update_cors_file(backend_file)
                print(f"✅ 更新: {backend_file}")
    
    def _update_cors_file(self, file_path):
        """更新CORS配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建新的CORS origins
        new_origins = [
            f"https://{domain}" for domain in self.cloudflare_domains.values()
        ]
        new_origins.extend([
            "http://localhost:8080",
            "http://localhost:3000",
            "capacitor://localhost",
            "ionic://localhost"
        ])
        
        # 替换origins配置
        origins_str = ',\n    '.join([f'"{origin}"' for origin in new_origins])
        
        cors_pattern = r'origins\s*=\s*\[.*?\]'
        new_cors = f'origins = [\n    {origins_str}\n]'
        
        content = re.sub(cors_pattern, new_cors, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_cloudflare_configs(self):
        """创建Cloudflare配置文件"""
        print("\n☁️ 创建Cloudflare配置文件...")
        
        # 创建wrangler.toml for Cloudflare Workers
        wrangler_config = f"""name = "aigupiao-api"
main = "src/index.js"
compatibility_date = "2023-12-01"

[env.production]
name = "aigupiao-api"
route = "api.{self.cloudflare_domains['main']}/*"

[[env.production.kv_namespaces]]
binding = "STOCK_DATA"
id = "your-kv-namespace-id"

[env.production.vars]
ENVIRONMENT = "production"
API_BASE_URL = "https://{self.cloudflare_domains['api']}"
"""
        
        with open("wrangler.toml", "w", encoding="utf-8") as f:
            f.write(wrangler_config)
        
        # 创建Cloudflare Pages配置
        pages_config = f"""# Cloudflare Pages配置

## 构建设置
- 构建命令: `npm run build`
- 构建输出目录: `dist`
- 根目录: `/`

## 环境变量
- NODE_ENV: production
- API_BASE_URL: https://{self.cloudflare_domains['api']}
- WS_URL: wss://{self.cloudflare_domains['api']}/ws

## 自定义域名
- {self.cloudflare_domains['app']}
- {self.cloudflare_domains['mobile']}
- {self.cloudflare_domains['admin']}

## 重定向规则
/api/* https://{self.cloudflare_domains['api']}/api/:splat 200
/* /index.html 200
"""
        
        with open("cloudflare-pages-config.md", "w", encoding="utf-8") as f:
            f.write(pages_config)
        
        # 创建_redirects文件
        redirects_content = f"""# Cloudflare Pages重定向
/api/* https://{self.cloudflare_domains['api']}/api/:splat 200
/* /index.html 200
"""
        
        with open("_redirects", "w", encoding="utf-8") as f:
            f.write(redirects_content)
        
        print("✅ 创建: wrangler.toml")
        print("✅ 创建: cloudflare-pages-config.md")
        print("✅ 创建: _redirects")
    
    def _cleanup_netlify_files(self):
        """清理Netlify相关文件"""
        print("\n🗑️ 清理Netlify相关文件...")
        
        netlify_files = [
            "netlify.toml",
            "_netlify",
            "netlify-final",
            "netlify-trading",
            "netlify-trading-fixed",
            "netlify-cli-deploy",
            "netlify-simple-test"
        ]
        
        for item in netlify_files:
            if os.path.exists(item):
                try:
                    if os.path.isdir(item):
                        import shutil
                        shutil.rmtree(item)
                        print(f"✅ 删除目录: {item}")
                    else:
                        os.remove(item)
                        print(f"✅ 删除文件: {item}")
                except Exception as e:
                    print(f"⚠️ 删除失败 {item}: {e}")
    
    def _generate_config_report(self):
        """生成配置报告"""
        print("\n📋 生成配置报告...")
        
        report = {
            "timestamp": "2025-07-02T05:00:00",
            "migration": "Netlify to Cloudflare",
            "cloudflare_domains": self.cloudflare_domains,
            "updated_files": [
                "炒股养家/env.js",
                "frontend/gupiao1/env.js",
                "frontend/stock5/env.js",
                "炒股养家/services/config.js",
                "backend/app.py",
                "cloud_app.py"
            ],
            "created_files": [
                "wrangler.toml",
                "cloudflare-pages-config.md",
                "_redirects"
            ],
            "removed_files": [
                "netlify.toml",
                "netlify-* directories"
            ],
            "deployment_instructions": {
                "frontend": f"Deploy to Cloudflare Pages: {self.cloudflare_domains['app']}",
                "api": f"Deploy to Cloudflare Workers: {self.cloudflare_domains['api']}",
                "dns": "Configure DNS in Cloudflare dashboard"
            }
        }
        
        with open("cloudflare_migration_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("📄 配置报告已保存: cloudflare_migration_report.json")
    
    def create_deployment_guide(self):
        """创建部署指南"""
        print("\n📖 创建部署指南...")
        
        guide = f"""# Cloudflare部署指南

## 🌐 域名架构

### 主要域名
- **主域名**: {self.cloudflare_domains['main']}
- **API服务**: {self.cloudflare_domains['api']} (Cloudflare Workers)
- **前端应用**: {self.cloudflare_domains['app']} (Cloudflare Pages)
- **移动端**: {self.cloudflare_domains['mobile']} (Cloudflare Pages)
- **管理后台**: {self.cloudflare_domains['admin']} (Cloudflare Pages)

## 🚀 部署步骤

### 1. Cloudflare Workers (API服务)
```bash
# 安装Wrangler CLI
npm install -g wrangler

# 登录Cloudflare
wrangler login

# 部署API服务
wrangler publish
```

### 2. Cloudflare Pages (前端应用)
1. 连接GitHub仓库到Cloudflare Pages
2. 设置构建命令: `npm run build`
3. 设置输出目录: `dist`
4. 配置自定义域名: {self.cloudflare_domains['app']}

### 3. DNS配置
在Cloudflare DNS中添加:
- A记录: {self.cloudflare_domains['main']} → Cloudflare IP
- CNAME记录: api → {self.cloudflare_domains['main']}
- CNAME记录: app → {self.cloudflare_domains['main']}
- CNAME记录: mobile → {self.cloudflare_domains['main']}
- CNAME记录: admin → {self.cloudflare_domains['main']}

## 🔧 环境变量

### Cloudflare Workers
- ENVIRONMENT: production
- API_BASE_URL: https://{self.cloudflare_domains['api']}

### Cloudflare Pages
- NODE_ENV: production
- API_BASE_URL: https://{self.cloudflare_domains['api']}
- WS_URL: wss://{self.cloudflare_domains['api']}/ws

## 📱 移动应用配置

更新移动应用中的API地址:
```javascript
const API_CONFIG = {{
  baseURL: 'https://{self.cloudflare_domains['api']}',
  wsURL: 'wss://{self.cloudflare_domains['api']}/ws'
}};
```

## 🔍 验证部署

1. 访问 https://{self.cloudflare_domains['app']} 检查前端
2. 访问 https://{self.cloudflare_domains['api']}/health 检查API
3. 测试WebSocket连接: wss://{self.cloudflare_domains['api']}/ws

## ⚠️ 注意事项

- 所有Netlify配置已移除
- 使用Cloudflare的全球CDN加速
- 支持自动HTTPS和SSL证书
- WebSocket连接通过Cloudflare Workers
"""
        
        with open("CLOUDFLARE_DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(guide)
        
        print("📄 部署指南已保存: CLOUDFLARE_DEPLOYMENT_GUIDE.md")

def main():
    """主函数"""
    print("🔄 Netlify到Cloudflare配置切换工具")
    print("=" * 50)
    
    switcher = CloudflareConfigSwitcher()
    
    # 运行切换
    switcher.run_switch()
    
    # 创建部署指南
    switcher.create_deployment_guide()
    
    print("\n" + "=" * 60)
    print("🎉 配置切换完成!")
    print()
    print("✅ 已切换到Cloudflare配置")
    print("✅ 已移除所有Netlify相关文件")
    print("✅ 已创建Cloudflare部署配置")
    print()
    print("📋 下一步:")
    print("1. 部署API到Cloudflare Workers")
    print("2. 部署前端到Cloudflare Pages") 
    print("3. 配置DNS记录")
    print("4. 测试所有域名访问")

if __name__ == "__main__":
    main()
