#!/usr/bin/env python3
"""
测试自定义域名访问
"""

import requests
import time

def test_domains():
    """测试不同域名"""
    domains = [
        "https://api.aigupiao.me",
        "https://trading-api.308186235.workers.dev",
        "https://app.aigupiao.me"
    ]
    
    print("🧪 测试域名访问")
    print("=" * 50)
    
    for domain in domains:
        print(f"\n📡 测试: {domain}")
        
        try:
            response = requests.get(domain, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 成功: {response.status_code}")
                try:
                    data = response.json()
                    if data.get("success"):
                        print("✅ 响应正常: JSON格式正确")
                    else:
                        print("⚠️ 响应异常: success字段为false")
                except:
                    print("⚠️ 响应格式: 非JSON")
                    print(f"   内容: {response.text[:100]}...")
            else:
                print(f"❌ 失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ 超时")
        except requests.exceptions.ConnectionError:
            print("🔌 连接错误")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 测试完成")

if __name__ == "__main__":
    test_domains()
