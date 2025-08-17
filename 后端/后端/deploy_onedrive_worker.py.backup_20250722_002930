#!/usr/bin/env python3
"""
部署OneDrive API Worker到Cloudflare
"""

import os
import json
import requests
from pathlib import Path

class CloudflareWorkerDeployer:
    """Cloudflare Worker部署器"""
    
    def __init__(self):
        # Cloudflare配置 (需要从环境变量或配置文件获取)
        self.account_id = "YOUR_ACCOUNT_ID"  # 需要替换
        self.api_token = "YOUR_API_TOKEN"    # 需要替换
        self.worker_name = "onedrive-trading-api"
        self.subdomain = "onedrive-api"
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/javascript"
        }
    
    def read_worker_script(self):
        """读取Worker脚本"""
        script_path = Path("onedrive-api-worker.js")
        
        if not script_path.exists():
            raise FileNotFoundError("Worker脚本文件不存在: onedrive-api-worker.js")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def deploy_worker(self):
        """部署Worker"""
        print("🚀 开始部署OneDrive API Worker...")
        
        try:
            # 读取脚本内容
            script_content = self.read_worker_script()
            print(f"✅ 读取Worker脚本成功，大小: {len(script_content)} 字符")
            
            # 部署Worker
            deploy_url = f"{self.base_url}/workers/scripts/{self.worker_name}"
            
            response = requests.put(
                deploy_url,
                headers=self.headers,
                data=script_content
            )
            
            if response.status_code == 200:
                print("✅ Worker部署成功！")
                result = response.json()
                print(f"   Worker ID: {result.get('result', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Worker部署失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 部署过程中出现异常: {e}")
            return False
    
    def setup_custom_domain(self):
        """设置自定义域名"""
        print("🌐 配置自定义域名...")
        
        try:
            # 这里需要根据实际的域名配置API来实现
            # 由于域名配置比较复杂，这里提供手动配置指导
            
            print("📋 请手动完成以下域名配置:")
            print(f"1. 在Cloudflare Dashboard中找到Worker: {self.worker_name}")
            print("2. 点击 'Add Custom Domain'")
            print("3. 添加域名: api.aigupiao.me")
            print("4. 或者添加子域名: onedrive-api.aigupiao.me")
            print("5. 确认DNS记录已正确配置")
            
            return True
            
        except Exception as e:
            print(f"❌ 域名配置失败: {e}")
            return False
    
    def test_deployment(self):
        """测试部署"""
        print("🧪 测试Worker部署...")
        
        # 测试URL列表
        test_urls = [
            f"https://{self.worker_name}.{self.account_id}.workers.dev/",
            f"https://{self.worker_name}.{self.account_id}.workers.dev/health",
            f"https://{self.worker_name}.{self.account_id}.workers.dev/api/local-trading/positions",
            f"https://{self.worker_name}.{self.account_id}.workers.dev/api/local-trading/balance"
        ]
        
        success_count = 0
        
        for url in test_urls:
            try:
                print(f"\n🔍 测试: {url}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ 响应成功: {response.status_code}")
                    success_count += 1
                    
                    # 显示响应数据
                    try:
                        data = response.json()
                        if 'message' in data:
                            print(f"   消息: {data['message']}")
                        if 'timestamp' in data:
                            print(f"   时间: {data['timestamp']}")
                    except:
                        print(f"   响应: {response.text[:100]}...")
                else:
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        print(f"\n📊 测试结果: {success_count}/{len(test_urls)} 成功")
        return success_count > 0
    
    def generate_deployment_info(self):
        """生成部署信息"""
        print("\n" + "=" * 60)
        print("📋 OneDrive API Worker 部署信息")
        print("=" * 60)
        
        print(f"Worker名称: {self.worker_name}")
        print(f"默认URL: https://{self.worker_name}.{self.account_id}.workers.dev/")
        print(f"自定义域名: https://api.aigupiao.me/ (需要手动配置)")
        
        print("\n📋 API端点:")
        endpoints = [
            ("根路径", "/"),
            ("健康检查", "/health"),
            ("持仓数据", "/api/local-trading/positions"),
            ("余额数据", "/api/local-trading/balance"),
            ("OneDrive测试", "/api/onedrive/test")
        ]
        
        for name, path in endpoints:
            print(f"   {name}: {path}")
        
        print("\n📋 功能特性:")
        features = [
            "OneDrive实时数据读取",
            "Microsoft Graph API集成",
            "智能缓存机制",
            "CORS支持",
            "错误处理和备用数据"
        ]
        
        for feature in features:
            print(f"   ✅ {feature}")
        
        print("\n📋 下一步操作:")
        print("1. 配置自定义域名 (api.aigupiao.me)")
        print("2. 测试API端点访问")
        print("3. 更新前端应用的API地址")
        print("4. 验证OneDrive数据读取")
        
        print("=" * 60)
    
    def run_deployment(self):
        """运行完整部署流程"""
        print("🚀 OneDrive API Worker 部署流程")
        print("=" * 60)
        
        # 1. 部署Worker
        print("\n📋 步骤1: 部署Worker")
        if not self.deploy_worker():
            print("❌ Worker部署失败，停止流程")
            return False
        
        # 2. 配置域名
        print("\n📋 步骤2: 配置域名")
        self.setup_custom_domain()
        
        # 3. 测试部署
        print("\n📋 步骤3: 测试部署")
        if not self.test_deployment():
            print("⚠️ 部署测试未完全成功，但Worker已部署")
        
        # 4. 生成部署信息
        self.generate_deployment_info()
        
        return True

def main():
    """主函数"""
    print("🔧 注意: 此脚本需要配置Cloudflare API凭据")
    print("请在脚本中设置正确的 account_id 和 api_token")
    print()
    
    choice = input("是否继续部署? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("部署已取消")
        return
    
    deployer = CloudflareWorkerDeployer()
    success = deployer.run_deployment()
    
    if success:
        print("\n🎯 部署流程完成！")
        print("\n📋 手动配置步骤:")
        print("1. 登录 Cloudflare Dashboard")
        print("2. 找到 Workers & Pages")
        print("3. 选择刚部署的Worker")
        print("4. 配置自定义域名")
        print("5. 测试API访问")
    else:
        print("\n💥 部署过程中出现问题！")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
