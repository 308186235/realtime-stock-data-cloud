#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查部署状态
监控Cloudflare Pages部署进度
"""

import requests
import time
from datetime import datetime

def check_website_status():
    """检查网站状态"""
    urls = [
        "https://aigupiao.me",
        "https://bei-fen.pages.dev"
    ]
    
    print("🔍 检查网站状态...")
    print("="*60)
    
    for url in urls:
        try:
            print(f"\n📡 测试: {url}")
            
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            
            if status_code == 200:
                content_length = len(response.text)
                print(f"✅ 状态: {status_code} OK")
                print(f"📄 内容长度: {content_length} 字符")
                
                # 检查内容类型
                if "AI股票交易系统" in response.text:
                    print("🎯 内容: 新的前端页面已部署 ✅")
                elif "<!DOCTYPE html>" in response.text:
                    print("📄 内容: HTML页面存在")
                else:
                    print("⚠️  内容: 可能是空白或错误页面")
                    
                # 检查关键功能
                if "Agent控制台" in response.text:
                    print("🤖 功能: Agent控制台 ✅")
                if "账户" in response.text:
                    print("💰 功能: 账户管理 ✅")
                if "持仓" in response.text:
                    print("📊 功能: 持仓管理 ✅")
                    
            else:
                print(f"❌ 状态: {status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ 超时: {url}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 连接错误: {url}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "="*60)

def monitor_deployment():
    """监控部署状态"""
    print("🚀 开始监控部署状态...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print("💡 Cloudflare Pages通常需要1-3分钟完成部署")
    print("\n按 Ctrl+C 停止监控\n")
    
    try:
        check_count = 0
        while True:
            check_count += 1
            print(f"🔄 第 {check_count} 次检查 - {datetime.now().strftime('%H:%M:%S')}")
            
            check_website_status()
            
            if check_count >= 10:
                print("✋ 已检查10次,停止监控")
                break
                
            print("⏳ 等待30秒后再次检查...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n⏹️  监控已停止")

def test_specific_features():
    """测试特定功能"""
    print("🧪 测试特定功能...")
    
    base_url = "https://aigupiao.me"
    
    # 测试页面响应时间
    try:
        start_time = time.time()
        response = requests.get(base_url, timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        print(f"⚡ 响应时间: {response_time:.2f}ms")
        
        if response_time < 1000:
            print("🚀 响应速度: 优秀")
        elif response_time < 3000:
            print("👍 响应速度: 良好")
        else:
            print("🐌 响应速度: 需要优化")
            
    except Exception as e:
        print(f"❌ 响应时间测试失败: {e}")

def show_deployment_summary():
    """显示部署总结"""
    print("\n" + "="*60)
    print("📋 部署总结")
    print("="*60)
    print("🎯 域名: aigupiao.me")
    print("🚀 平台: Cloudflare Pages")
    print("📦 仓库: https://github.com/308186235/Bei-fen.git")
    print("🔄 自动部署: 已启用")
    print("📱 移动端: 已适配")
    print("🔒 HTTPS: 已启用")
    print("\n✅ 主要功能:")
    print("   • 🏠 首页展示")
    print("   • 🤖 Agent控制台")
    print("   • 💰 账户管理")
    print("   • 📊 持仓管理")
    print("   • ⚙️ 系统设置")
    print("\n🔧 技术栈:")
    print("   • 前端: HTML5 + CSS3 + JavaScript")
    print("   • 部署: Cloudflare Pages")
    print("   • 域名: Cloudflare DNS")
    print("   • 证书: Cloudflare SSL")
    print("\n📈 下一步计划:")
    print("   1. 完善uni-app构建流程")
    print("   2. 集成后端API接口")
    print("   3. 添加实时数据功能")
    print("   4. 优化移动端体验")
    print("="*60)

if __name__ == "__main__":
    print("🎉 AI股票交易系统 - 部署状态检查")
    print("="*60)
    
    # 立即检查一次
    check_website_status()
    
    # 测试功能
    test_specific_features()
    
    # 显示总结
    show_deployment_summary()
    
    # 询问是否监控
    choice = input("\n🤔 是否开始监控部署状态?(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        monitor_deployment()
    else:
        print("✅ 检查完成!")
        print("💡 可以访问 https://aigupiao.me 查看最新部署")
