#!/usr/bin/env python3
"""
测试新部署的API Worker
"""

import requests
import json

def test_api():
    base_url = "https://api.aigupiao.me"
    
    print("🧪 测试新部署的API Worker")
    print("=" * 50)
    print(f"测试URL: {base_url}")
    print()
    
    # 测试端点 - 简化版本
    endpoints = [
        "/",
        "/api/agent-analysis",
        "/api/account-balance",
        "/api/chagubang/health"
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"测试: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"  ✅ 成功 - {data.get('timestamp', '')}")
                    success_count += 1
                else:
                    print(f"  ❌ API返回错误: {data.get('error', '未知错误')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ 超时")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 请求失败: {e}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    print()
    print(f"📊 测试结果: {success_count}/{len(endpoints)} 成功")
    
    if success_count == len(endpoints):
        print("🎉 所有API端点都正常工作!")
        print()
        print("📋 下一步:")
        print("1. 更新Cloudflare路由配置")
        print("2. 将api.aigupiao.me指向新的Worker")
        print("3. 前端应用将恢复正常")
        return True
    else:
        print("⚠️ 部分端点有问题,需要检查")
        return False

if __name__ == "__main__":
    test_api()
