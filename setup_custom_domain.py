#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置app.aigupiao.me自定义域名
解决SSL证书问题
"""

import subprocess
import json
from datetime import datetime

class CustomDomainSetup:
    """自定义域名配置器"""
    
    def __init__(self):
        self.project_name = "ai-stock-trading-app"
        self.custom_domain = "app.aigupiao.me"
        self.temp_url = "https://6ddf02df.ai-stock-trading-app.pages.dev"
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_project_status(self):
        """检查项目状态"""
        self.log("🔍 检查项目状态...")
        
        try:
            result = subprocess.run([
                'wrangler', 'pages', 'project', 'list'
            ], capture_output=True, text=True, check=True)
            
            self.log("✅ 项目列表获取成功")
            print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ 获取项目列表失败: {e}", "ERROR")
            return False
            
    def setup_dns_instructions(self):
        """提供DNS配置说明"""
        self.log("📋 DNS配置说明")
        
        print("\n" + "="*60)
        print("🌐 DNS配置指南")
        print("="*60)
        print("请在Cloudflare DNS管理中添加以下记录：")
        print()
        print("类型: CNAME")
        print("名称: app")
        print("目标: 6ddf02df.ai-stock-trading-app.pages.dev")
        print("代理状态: 已代理 (橙色云朵)")
        print("TTL: 自动")
        print()
        print("或者使用A记录：")
        print("类型: A")
        print("名称: app") 
        print("IPv4地址: 104.21.x.x (Cloudflare IP)")
        print("代理状态: 已代理")
        print("="*60)
        
    def create_manual_setup_guide(self):
        """创建手动设置指南"""
        self.log("📝 创建手动设置指南...")
        
        guide = {
            "setup_time": datetime.now().isoformat(),
            "project_info": {
                "name": self.project_name,
                "temp_url": self.temp_url,
                "target_domain": self.custom_domain
            },
            "manual_steps": [
                {
                    "step": 1,
                    "title": "登录Cloudflare Pages控制台",
                    "action": "访问 https://dash.cloudflare.com/pages",
                    "description": "找到 ai-stock-trading-app 项目"
                },
                {
                    "step": 2,
                    "title": "添加自定义域名",
                    "action": "点击项目 → Custom domains → Set up a custom domain",
                    "description": f"输入域名: {self.custom_domain}"
                },
                {
                    "step": 3,
                    "title": "配置DNS记录",
                    "action": "在Cloudflare DNS中添加CNAME记录",
                    "description": "app → 6ddf02df.ai-stock-trading-app.pages.dev"
                },
                {
                    "step": 4,
                    "title": "等待SSL证书",
                    "action": "等待5-10分钟",
                    "description": "Cloudflare自动配置SSL证书"
                }
            ],
            "verification_urls": [
                f"https://{self.custom_domain}",
                f"https://{self.custom_domain}/agent-console.html"
            ],
            "troubleshooting": {
                "ssl_error": "如果出现SSL错误，等待证书配置完成",
                "dns_propagation": "DNS传播可能需要几分钟时间",
                "cache_clear": "清除浏览器缓存后重试"
            }
        }
        
        with open("custom_domain_setup_guide.json", 'w', encoding='utf-8') as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
            
        self.log("✅ 设置指南已生成: custom_domain_setup_guide.json")
        
    def test_current_deployment(self):
        """测试当前部署"""
        self.log("🧪 测试当前部署...")
        
        import requests
        
        test_urls = [
            self.temp_url,
            f"{self.temp_url}/agent-console.html"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {url} - 访问正常")
                else:
                    self.log(f"⚠️ {url} - HTTP {response.status_code}")
            except Exception as e:
                self.log(f"❌ {url} - 访问失败: {e}")
                
    def run_setup(self):
        """运行设置流程"""
        self.log("🚀 开始自定义域名设置")
        print("="*60)
        
        # 1. 检查项目状态
        self.check_project_status()
        
        # 2. 测试当前部署
        self.test_current_deployment()
        
        # 3. 提供DNS配置说明
        self.setup_dns_instructions()
        
        # 4. 创建手动设置指南
        self.create_manual_setup_guide()
        
        print("\n🎯 下一步操作：")
        print("1. 访问 Cloudflare Pages 控制台")
        print("2. 为项目添加自定义域名 app.aigupiao.me")
        print("3. 配置DNS记录")
        print("4. 等待SSL证书配置完成")
        print("\n✨ 临时访问地址（HTTPS）：")
        print(f"   {self.temp_url}")
        print(f"   {self.temp_url}/agent-console.html")

def main():
    """主函数"""
    setup = CustomDomainSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
