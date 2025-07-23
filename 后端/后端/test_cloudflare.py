#!/usr/bin/env python3
"""
测试Cloudflare Zero Trust连接
"""

import requests
import socket
import ssl
from datetime import datetime

def test_domain_resolution():
    """测试域名解析"""
    domains = ['aigupiao.me', 'api.aigupiao.me', 'trading.aigupiao.me', 'agent.aigupiao.me']
    print("🔍 测试域名解析:")
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"  ✅ {domain}: {ip}")
        except Exception as e:
            print(f"  ❌ {domain}: 解析失败 - {e}")

def test_ssl_certificates():
    """测试SSL证书"""
    domains = ['aigupiao.me', 'api.aigupiao.me', 'trading.aigupiao.me', 'agent.aigupiao.me']
    print("\n🔒 测试SSL证书:")
    
    for domain in domains:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    print(f"  ✅ {domain}: SSL证书有效")
        except Exception as e:
            print(f"  ❌ {domain}: SSL证书问题 - {e}")

def test_https_connections():
    """测试HTTPS连接"""
    endpoints = [
        'https://aigupiao.me/health',
        'https://api.aigupiao.me/health', 
        'https://trading.aigupiao.me/health',
        'https://agent.aigupiao.me/health'
    ]
    print("\n🌐 测试HTTPS连接:")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=15)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: 连接成功 (状态码: {response.status_code})")
                try:
                    data = response.json()
                    print(f"     响应: {data}")
                except:
                    print(f"     响应: {response.text[:100]}...")
            else:
                print(f"  ⚠️ {endpoint}: 状态码 {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"  ❌ {endpoint}: 连接超时")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {endpoint}: 连接错误")
        except Exception as e:
            print(f"  ❌ {endpoint}: 连接失败 - {e}")

def test_tunnel_status():
    """测试隧道状态"""
    print("\n🚇 Cloudflare隧道状态:")
    try:
        from zero_trust_manager import ZeroTrustManager
        manager = ZeroTrustManager()
        status = manager.get_tunnel_status()
        print(f"  隧道状态: {status}")
    except Exception as e:
        print(f"  ❌ 隧道状态检查失败: {e}")

if __name__ == "__main__":
    print(f"🔧 Cloudflare Zero Trust连接测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_domain_resolution()
    test_ssl_certificates()
    test_https_connections()
    test_tunnel_status()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
