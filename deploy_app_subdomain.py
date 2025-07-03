#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署app.aigupiao.me子域名到Cloudflare Pages
包含Agent分析控制台
"""

import os
import shutil
import subprocess
import json
from datetime import datetime

class AppSubdomainDeployer:
    """app.aigupiao.me部署器"""
    
    def __init__(self):
        self.project_name = "ai-stock-trading-app"
        self.subdomain = "app.aigupiao.me"
        self.source_dir = "subdomains/app"
        self.build_dir = "dist/app"
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def prepare_build_directory(self):
        """准备构建目录"""
        self.log("🔧 准备构建目录...")
        
        # 清理并创建构建目录
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir, exist_ok=True)
        
        # 复制源文件
        if os.path.exists(self.source_dir):
            for file in os.listdir(self.source_dir):
                src_path = os.path.join(self.source_dir, file)
                dst_path = os.path.join(self.build_dir, file)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
                    self.log(f"✅ 复制文件: {file}")
        
        # 创建_redirects文件用于SPA路由
        redirects_content = """
# SPA路由重定向
/agent-console /agent-console.html 200
/* /index.html 200
"""
        with open(os.path.join(self.build_dir, "_redirects"), 'w', encoding='utf-8') as f:
            f.write(redirects_content.strip())
        
        self.log("✅ 构建目录准备完成")
        
    def create_wrangler_config(self):
        """创建Wrangler配置文件"""
        self.log("📝 创建Wrangler配置...")
        
        config = {
            "name": self.project_name,
            "compatibility_date": "2024-01-01",
            "pages_build_output_dir": self.build_dir
        }
        
        config_path = "wrangler-app.toml"
        with open(config_path, 'w', encoding='utf-8') as f:
            # 写入TOML格式
            f.write(f'name = "{config["name"]}"\n')
            f.write(f'compatibility_date = "{config["compatibility_date"]}"\n')
            f.write(f'pages_build_output_dir = "{config["pages_build_output_dir"]}"\n')
            f.write('\n[env.production]\n')
            f.write('name = "ai-stock-trading-app"\n')
        
        self.log(f"✅ 配置文件创建: {config_path}")
        return config_path
        
    def deploy_to_cloudflare(self):
        """部署到Cloudflare Pages"""
        self.log("🚀 开始部署到Cloudflare Pages...")
        
        try:
            # 检查wrangler是否安装
            result = subprocess.run(['wrangler', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log(f"✅ Wrangler版本: {result.stdout.strip()}")
            
            # 部署到Pages
            deploy_cmd = [
                'wrangler', 'pages', 'deploy', self.build_dir,
                '--project-name', self.project_name,
                '--compatibility-date', '2024-01-01'
            ]
            
            self.log("📤 执行部署命令...")
            result = subprocess.run(deploy_cmd, capture_output=True, text=True, check=True)
            
            self.log("✅ 部署成功！")
            self.log(f"📋 部署输出:\n{result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ 部署失败: {e}", "ERROR")
            self.log(f"错误输出: {e.stderr}", "ERROR")
            return False
        except FileNotFoundError:
            self.log("❌ 未找到wrangler命令，请先安装Cloudflare CLI", "ERROR")
            self.log("安装命令: npm install -g wrangler", "INFO")
            return False
            
    def setup_custom_domain(self):
        """设置自定义域名"""
        self.log("🌐 设置自定义域名...")
        
        try:
            # 添加自定义域名
            domain_cmd = [
                'wrangler', 'pages', 'domain', 'add',
                self.subdomain,
                '--project-name', self.project_name
            ]
            
            result = subprocess.run(domain_cmd, capture_output=True, text=True, check=True)
            self.log(f"✅ 域名设置成功: {self.subdomain}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"⚠️ 域名设置可能失败: {e}", "WARNING")
            self.log("请手动在Cloudflare Pages控制台设置自定义域名", "INFO")
            return False
            
    def generate_deployment_report(self):
        """生成部署报告"""
        self.log("📊 生成部署报告...")
        
        report = {
            "deployment_time": datetime.now().isoformat(),
            "project_name": self.project_name,
            "subdomain": self.subdomain,
            "build_directory": self.build_dir,
            "features": [
                "Agent分析控制台",
                "OneDrive数据支持",
                "实时API连接",
                "持仓和余额查询",
                "响应式设计"
            ],
            "urls": {
                "production": f"https://{self.subdomain}",
                "agent_console": f"https://{self.subdomain}/agent-console",
                "api_endpoint": "https://api.aigupiao.me"
            },
            "next_steps": [
                "验证DNS解析",
                "测试Agent控制台功能",
                "检查API连接状态",
                "配置SSL证书（自动）"
            ]
        }
        
        report_file = "app_deployment_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 部署报告已生成: {report_file}")
        
        # 显示关键信息
        print("\n" + "="*60)
        print("🎉 app.aigupiao.me 部署完成！")
        print("="*60)
        print(f"🌐 主页面: https://{self.subdomain}")
        print(f"🤖 Agent控制台: https://{self.subdomain}/agent-console")
        print(f"📡 API端点: https://api.aigupiao.me")
        print("="*60)
        
    def run_deployment(self):
        """运行完整部署流程"""
        self.log("🚀 开始app.aigupiao.me部署流程")
        print("="*60)
        
        try:
            # 1. 准备构建目录
            self.prepare_build_directory()
            
            # 2. 创建配置文件
            self.create_wrangler_config()
            
            # 3. 部署到Cloudflare
            if self.deploy_to_cloudflare():
                # 4. 设置自定义域名
                self.setup_custom_domain()
                
                # 5. 生成报告
                self.generate_deployment_report()
                
                self.log("✅ 部署流程完成！", "SUCCESS")
                return True
            else:
                self.log("❌ 部署失败", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 部署过程中发生错误: {e}", "ERROR")
            return False

def main():
    """主函数"""
    deployer = AppSubdomainDeployer()
    success = deployer.run_deployment()
    
    if success:
        print("\n🎉 部署成功！请访问 https://app.aigupiao.me 查看结果")
    else:
        print("\n💥 部署失败！请检查错误信息并重试")

if __name__ == "__main__":
    main()
