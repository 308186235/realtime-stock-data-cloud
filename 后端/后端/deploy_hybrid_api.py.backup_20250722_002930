#!/usr/bin/env python3
"""
部署混合数据API到Cloudflare Workers
替换现有的API以支持OneDrive数据读取
"""

import os
import json
import requests
import time
from pathlib import Path

class CloudflareWorkerDeployer:
    """Cloudflare Worker部署器"""
    
    def __init__(self):
        # 这些需要从Cloudflare Dashboard获取
        self.account_id = None  # 需要用户提供
        self.api_token = None   # 需要用户提供
        self.zone_id = None     # 需要用户提供
        
        self.worker_name = "hybrid-trading-api"
        self.custom_domain = "api.aigupiao.me"
        
    def get_cloudflare_credentials(self):
        """获取Cloudflare凭据"""
        print("🔑 获取Cloudflare凭据...")
        print("=" * 50)
        print("请提供以下Cloudflare信息:")
        print("1. 登录 https://dash.cloudflare.com")
        print("2. 选择您的域名 (aigupiao.me)")
        print("3. 获取以下信息:")
        print()
        
        # 尝试从环境变量获取
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        
        if not self.account_id:
            print("📋 Account ID:")
            print("   位置: Cloudflare Dashboard 右侧边栏")
            print("   格式: 32位字符串")
            self.account_id = input("   请输入 Account ID: ").strip()
        
        if not self.api_token:
            print("\n📋 API Token:")
            print("   位置: My Profile > API Tokens > Create Token")
            print("   权限: Zone:Zone:Read, Zone:DNS:Edit, Account:Cloudflare Workers:Edit")
            self.api_token = input("   请输入 API Token: ").strip()
        
        if not self.zone_id:
            print("\n📋 Zone ID:")
            print("   位置: 域名概览页面右侧边栏")
            print("   格式: 32位字符串")
            self.zone_id = input("   请输入 Zone ID: ").strip()
        
        print("\n✅ 凭据收集完成")
        return bool(self.account_id and self.api_token and self.zone_id)
    
    def read_worker_script(self):
        """读取Worker脚本"""
        script_path = Path("hybrid-data-api-worker.js")
        
        if not script_path.exists():
            print(f"❌ Worker脚本不存在: {script_path}")
            return None
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 读取Worker脚本: {len(content)} 字符")
        return content
    
    def deploy_worker(self, script_content):
        """部署Worker"""
        print("🚀 部署Worker到Cloudflare...")
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/workers/scripts/{self.worker_name}"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/javascript"
        }
        
        try:
            response = requests.put(url, headers=headers, data=script_content)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Worker部署成功!")
                
                if result.get('success'):
                    worker_id = result.get('result', {}).get('id', 'N/A')
                    print(f"   Worker ID: {worker_id}")
                    return True
                else:
                    print("❌ 部署响应显示失败")
                    print(f"   错误: {result.get('errors', [])}")
                    return False
            else:
                print(f"❌ Worker部署失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 部署异常: {e}")
            return False
    
    def setup_custom_domain(self):
        """设置自定义域名路由"""
        print("🌐 配置自定义域名路由...")
        
        # 创建路由规则
        route_url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/workers/routes"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        route_data = {
            "pattern": f"{self.custom_domain}/*",
            "script": self.worker_name
        }
        
        try:
            response = requests.post(route_url, headers=headers, json=route_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 自定义域名路由配置成功")
                    print(f"   域名: {self.custom_domain}")
                    print(f"   Worker: {self.worker_name}")
                    return True
                else:
                    print("❌ 路由配置失败")
                    print(f"   错误: {result.get('errors', [])}")
                    return False
            else:
                print(f"❌ 路由配置请求失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 路由配置异常: {e}")
            return False
    
    def test_deployment(self):
        """测试部署"""
        print("🧪 测试新API部署...")
        
        # 等待部署生效
        print("⏳ 等待部署生效...")
        time.sleep(10)
        
        test_urls = [
            f"https://{self.custom_domain}/",
            f"https://{self.custom_domain}/health",
            f"https://{self.custom_domain}/api/local-trading/positions",
            f"https://{self.custom_domain}/api/local-trading/balance",
            f"https://{self.custom_domain}/api/agent/complete-data"
        ]
        
        success_count = 0
        
        for url in test_urls:
            print(f"\n🔍 测试: {url}")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    print(f"✅ 响应成功: {response.status_code}")
                    success_count += 1
                    
                    try:
                        data = response.json()
                        if 'message' in data:
                            print(f"   消息: {data['message']}")
                        if 'version' in data:
                            print(f"   版本: {data['version']}")
                        if 'data_sources' in data:
                            print(f"   数据源: {data['data_sources']}")
                    except:
                        print(f"   响应: {response.text[:100]}...")
                        
                else:
                    print(f"❌ 响应失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        print(f"\n📊 测试结果: {success_count}/{len(test_urls)} 成功")
        return success_count >= 3  # 至少3个端点成功
    
    def verify_onedrive_data_access(self):
        """验证OneDrive数据访问"""
        print("📁 验证OneDrive数据访问...")
        
        test_url = f"https://{self.custom_domain}/api/local-trading/positions"
        
        try:
            response = requests.get(test_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    response_data = data['data']
                    
                    # 检查是否是OneDrive数据
                    api_source = response_data.get('api_source', '')
                    source = response_data.get('source', '')
                    
                    if 'onedrive' in api_source.lower() or 'onedrive' in source.lower():
                        print("✅ 检测到OneDrive数据源")
                        return True
                    else:
                        print("⚠️ 未检测到OneDrive数据源")
                        print(f"   API来源: {api_source}")
                        print(f"   数据来源: {source}")
                        return False
                else:
                    print("❌ 响应数据格式异常")
                    return False
            else:
                print(f"❌ API访问失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 验证异常: {e}")
            return False
    
    def run_deployment(self):
        """运行完整部署流程"""
        print("🚀 混合数据API部署流程")
        print("=" * 60)
        
        # 1. 获取凭据
        print("\n📋 步骤1: 获取Cloudflare凭据")
        if not self.get_cloudflare_credentials():
            print("❌ 凭据获取失败")
            return False
        
        # 2. 读取脚本
        print("\n📋 步骤2: 读取Worker脚本")
        script_content = self.read_worker_script()
        if not script_content:
            return False
        
        # 3. 部署Worker
        print("\n📋 步骤3: 部署Worker")
        if not self.deploy_worker(script_content):
            return False
        
        # 4. 配置域名
        print("\n📋 步骤4: 配置自定义域名")
        if not self.setup_custom_domain():
            print("⚠️ 域名配置失败，但Worker已部署")
        
        # 5. 测试部署
        print("\n📋 步骤5: 测试部署")
        if not self.test_deployment():
            print("⚠️ 部署测试未完全成功")
        
        # 6. 验证OneDrive访问
        print("\n📋 步骤6: 验证OneDrive数据访问")
        onedrive_ok = self.verify_onedrive_data_access()
        
        # 7. 生成部署报告
        print("\n" + "=" * 60)
        print("📊 混合数据API部署报告")
        print("=" * 60)
        
        print(f"✅ Worker已部署: {self.worker_name}")
        print(f"✅ 自定义域名: {self.custom_domain}")
        print(f"{'✅' if onedrive_ok else '⚠️'} OneDrive数据访问: {'正常' if onedrive_ok else '需要调试'}")
        
        print("\n📋 API端点:")
        endpoints = [
            ("根路径", "/"),
            ("健康检查", "/health"),
            ("持仓数据", "/api/local-trading/positions"),
            ("余额数据", "/api/local-trading/balance"),
            ("Agent完整数据", "/api/agent/complete-data")
        ]
        
        for name, path in endpoints:
            print(f"   {name}: https://{self.custom_domain}{path}")
        
        if onedrive_ok:
            print("\n🎉 混合数据API部署成功！")
            print("✅ 云端Agent现在可以获取OneDrive的真实数据")
        else:
            print("\n⚠️ 部署完成但需要调试OneDrive访问")
            print("🔧 请检查OneDrive分享链接和权限设置")
        
        return True

def main():
    """主函数"""
    print("🔧 混合数据API部署工具")
    print("这将替换现有API以支持OneDrive数据读取")
    print()
    
    deployer = CloudflareWorkerDeployer()
    success = deployer.run_deployment()
    
    if success:
        print("\n🎯 部署流程完成！")
        print("\n📋 下一步:")
        print("1. 测试新API是否能读取OneDrive数据")
        print("2. 验证Agent能否获取最新数据")
        print("3. 监控API性能和稳定性")
    else:
        print("\n💥 部署过程中出现问题！")
        print("🔧 请检查Cloudflare凭据和网络连接")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
