#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控DNS传播状态
"""

import requests
import socket
import time

def check_dns_propagation():
    """检查DNS传播状态"""
    print("🔍 检查DNS传播状态...")
    
    try:
        # 获取当前解析
        domain_ip = socket.gethostbyname('aigupiao.me')
        ngrok_ip = socket.gethostbyname('5db1-116-169-10-245.ngrok-free.app')
        
        print(f"📡 aigupiao.me → {domain_ip}")
        print(f"📡 ngrok地址 → {ngrok_ip}")
        
        if domain_ip == ngrok_ip:
            print("✅ DNS传播完成！域名正确解析到ngrok")
            return True
        else:
            print("⏳ DNS还在传播中...")
            return False
            
    except Exception as e:
        print(f"❌ DNS检查失败: {e}")
        return False

def test_domain_access():
    """测试域名访问"""
    print("🧪 测试域名访问...")
    
    try:
        response = requests.get("https://aigupiao.me/api/health", 
                              timeout=10,
                              headers={'ngrok-skip-browser-warning': 'true'})
        print(f"📡 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 域名访问成功！")
            print(f"✅ 响应: {response.json()}")
            return True
        else:
            print(f"⚠️ 响应: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ 域名访问失败: {e}")
        return False

def monitor_dns():
    """监控DNS传播"""
    print("🚀 开始监控DNS传播...")
    print("=" * 50)
    
    max_attempts = 10  # 最多检查10次（10分钟）
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 第 {attempt} 次检查 ({time.strftime('%H:%M:%S')})")
        print("-" * 30)
        
        # 检查DNS传播
        dns_ok = check_dns_propagation()
        
        if dns_ok:
            print("\n🎉 DNS传播完成！测试域名访问...")
            if test_domain_access():
                print("\n🎯 完美！域名完全可用！")
                print("🌐 您现在可以通过 https://aigupiao.me 访问您的交易系统")
                break
        
        if attempt < max_attempts:
            print(f"\n⏰ 等待60秒后再次检查...")
            time.sleep(60)
        else:
            print(f"\n⚠️ 已检查{max_attempts}次，DNS可能需要更长时间传播")
            print("💡 建议：")
            print("   1. 继续等待5-10分钟")
            print("   2. 或者临时使用ngrok地址访问")
    
    print("\n" + "=" * 50)
    print("📋 监控结束")

if __name__ == "__main__":
    monitor_dns()
