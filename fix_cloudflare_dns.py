#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Cloudflare DNS配置
"""

import subprocess
import time

def fix_cloudflare_dns():
    """修复Cloudflare DNS配置"""
    print("🔧 修复Cloudflare DNS配置...")
    
    tunnel_id = "1b454ed3-f4a8-4db9-bdb1-887f91e9e471"
    
    print("\n📋 需要执行的DNS配置步骤:")
    print("=" * 50)
    
    print("\n1️⃣ 删除多余的CNAME记录")
    print("   - 保留: aigupiao.me")
    print("   - 删除: 应用程序接口, 后端, 测试")
    
    print("\n2️⃣ 配置隧道路由")
    print("   执行以下命令:")
    
    commands = [
        f"cloudflared.exe tunnel route dns {tunnel_id} aigupiao.me",
        f"cloudflared.exe tunnel route dns {tunnel_id} www.aigupiao.me"
    ]
    
    for cmd in commands:
        print(f"   {cmd}")
    
    print("\n3️⃣ 验证配置")
    print("   cloudflared.exe tunnel info aigupiao")
    
    print("\n🤖 自动执行配置...")
    
    # 自动执行路由配置
    for cmd in commands:
        print(f"\n执行: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ 成功")
                if result.stdout:
                    print(f"输出: {result.stdout.strip()}")
            else:
                print("❌ 失败")
                if result.stderr:
                    print(f"错误: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    print("\n⏳ 等待DNS传播...")
    time.sleep(5)
    
    # 验证配置
    print("\n🔍 验证隧道配置...")
    try:
        result = subprocess.run("cloudflared.exe tunnel info aigupiao", 
                              shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ 隧道信息:")
            print(result.stdout)
        else:
            print("❌ 获取隧道信息失败")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 验证失败: {e}")

def test_domain_access():
    """测试域名访问"""
    print("\n🧪 测试域名访问...")
    
    import requests
    
    test_urls = [
        "https://aigupiao.me/api/auth/test",
        "https://www.aigupiao.me/api/auth/test"
    ]
    
    for url in test_urls:
        print(f"\n测试: {url}")
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                print(f"✅ 成功: {response.status_code}")
                print(f"响应: {response.text[:100]}...")
            else:
                print(f"❌ 失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    print("🚀 开始修复Cloudflare DNS配置...")
    
    fix_cloudflare_dns()
    
    print("\n" + "=" * 50)
    print("💡 手动操作建议:")
    print("1. 登录 https://dash.cloudflare.com")
    print("2. 选择域名 aigupiao.me")
    print("3. 进入 DNS 管理")
    print("4. 删除多余的CNAME记录，只保留:")
    print("   - aigupiao.me (CNAME)")
    print("   - www.aigupiao.me (CNAME)")
    print("5. 确保都指向隧道ID")
    print("6. 等待5-10分钟DNS传播")
    
    # 等待用户确认
    input("\n按Enter键测试域名访问...")
    test_domain_access()
    
    print("\n🎉 配置完成！")
    print("如果仍有问题，请等待DNS完全传播（最多30分钟）")
