#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证DNS配置和域名访问
"""

import requests
import socket
import time
import subprocess

def check_dns_resolution():
    """检查DNS解析"""
    print("🔍 检查DNS解析...")
    try:
        # 检查域名解析
        ip = socket.gethostbyname('aigupiao.me')
        print(f"✅ aigupiao.me 解析到: {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
        return False

def test_domain_access():
    """测试域名访问"""
    print("\n🌐 测试域名访问...")
    
    urls_to_test = [
        "https://aigupiao.me/",
        "https://aigupiao.me/api/health",
        "https://aigupiao.me/api/v1/agent-trading/system-status"
    ]
    
    for url in urls_to_test:
        try:
            print(f"📡 测试: {url}")
            response = requests.get(url, timeout=15, allow_redirects=True)
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'message' in data:
                        print(f"✅ 响应: {data['message']}")
                    elif 'status' in data:
                        print(f"✅ 状态: {data['status']}")
                except:
                    print(f"✅ 响应长度: {len(response.text)} 字符")
            else:
                print(f"⚠️ 响应内容: {response.text[:100]}...")
                
        except requests.exceptions.SSLError as e:
            print(f"🔒 SSL错误: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 连接错误: {e}")
        except requests.exceptions.Timeout as e:
            print(f"⏰ 超时错误: {e}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        print()

def test_ngrok_direct():
    """测试ngrok直接访问"""
    print("🔗 测试ngrok直接访问...")
    ngrok_url = "https://5db1-116-169-10-245.ngrok-free.app"
    
    try:
        response = requests.get(f"{ngrok_url}/api/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ ngrok直接访问正常: {response.status_code}")
            return True
        else:
            print(f"⚠️ ngrok访问异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ngrok访问失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🧪 DNS配置验证")
    print("=" * 50)
    
    # 1. 检查ngrok是否正常
    if not test_ngrok_direct():
        print("❌ ngrok服务异常，请检查ngrok是否正在运行")
        return
    
    # 2. 检查DNS解析
    dns_ok = check_dns_resolution()
    
    # 3. 测试域名访问
    test_domain_access()
    
    print("=" * 50)
    print("📋 验证完成！")
    
    if dns_ok:
        print("✅ DNS配置正常")
        print("💡 如果域名访问失败，请等待DNS传播（2-10分钟）")
    else:
        print("❌ DNS配置需要检查")
        print("💡 请确认Cloudflare DNS记录已正确配置")
    
    print("\n🔧 故障排除：")
    print("1. 确认Cloudflare DNS记录类型为CNAME")
    print("2. 确认内容为: 5db1-116-169-10-245.ngrok-free.app")
    print("3. 确认代理状态为已代理（橙色云朵）")
    print("4. 等待DNS传播完成")
    print("5. 确认ngrok隧道正在运行")

if __name__ == "__main__":
    main()
