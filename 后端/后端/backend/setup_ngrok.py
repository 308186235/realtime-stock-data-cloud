# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ngrok内网穿透设置脚本
用于将本地服务暴露到公网
"""

import subprocess
import time
import requests
import json
import os

def check_ngrok_installed():
    """检查ngrok是否已安装"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok已安装")
            print(f"版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ ngrok未安装")
            return False
    except FileNotFoundError:
        print("❌ ngrok未安装")
        return False

def download_ngrok():
    """下载并安装ngrok"""
    print("📥 正在下载ngrok...")
    print("请访问: https://ngrok.com/download")
    print("1. 下载Windows版本的ngrok")
    print("2. 解压到当前目录或添加到PATH")
    print("3. 注册ngrok账号获取authtoken")
    print("4. 运行: ngrok authtoken <your-token>")
    
def start_ngrok_tunnel():
    """启动ngrok隧道"""
    print("🚀 启动ngrok隧道...")
    
    try:
        # 启动ngrok隧道
        process = subprocess.Popen(
            ['ngrok', 'http', '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ 等待ngrok启动...")
        time.sleep(3)
        
        # 获取ngrok状态
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"✅ ngrok隧道已启动!")
                    print(f"🌐 公网地址: {public_url}")
                    print(f"🔗 本地地址: http://localhost:8000")
                    
                    # 测试连接
                    test_url = f"{public_url}/api/health"
                    try:
                        test_response = requests.get(test_url, timeout=10)
                        if test_response.status_code == 200:
                            print(f"✅ 公网访问测试成功!")
                            print(f"📊 健康检查: {test_response.json()}")
                        else:
                            print(f"⚠️ 公网访问测试失败: {test_response.status_code}")
                    except Exception as e:
                        print(f"⚠️ 公网访问测试失败: {e}")
                    
                    return public_url
                else:
                    print("❌ 未找到活动的隧道")
            else:
                print("❌ 无法获取ngrok状态")
        except Exception as e:
            print(f"❌ 获取ngrok状态失败: {e}")
            
    except FileNotFoundError:
        print("❌ ngrok命令未找到,请先安装ngrok")
        return None
    except Exception as e:
        print(f"❌ 启动ngrok失败: {e}")
        return None

def update_cloudflare_dns(public_url):
    """更新Cloudflare DNS记录的说明"""
    if not public_url:
        return
        
    # 提取域名部分
    domain = public_url.replace('https://', '').replace('http://', '')
    
    print("\n" + "="*60)
    print("📋 Cloudflare DNS配置说明")
    print("="*60)
    print(f"1. 登录Cloudflare控制台: https://dash.cloudflare.com")
    print(f"2. 选择域名: aigupiao.me")
    print(f"3. 进入DNS设置")
    print(f"4. 添加CNAME记录:")
    print(f"   类型: CNAME")
    print(f"   名称: @")
    print(f"   内容: {domain}")
    print(f"   代理状态: 已代理 (橙色云朵)")
    print(f"5. 或者添加A记录指向ngrok的IP")
    print("="*60)

def main():
    """主函数"""
    print("🌐 ngrok内网穿透设置")
    print("="*50)
    
    # 检查ngrok是否安装
    if not check_ngrok_installed():
        download_ngrok()
        return
    
    # 启动ngrok隧道
    public_url = start_ngrok_tunnel()
    
    if public_url:
        # 提供DNS配置说明
        update_cloudflare_dns(public_url)
        
        print(f"\n🎉 设置完成!")
        print(f"📱 您现在可以通过以下地址访问服务:")
        print(f"   本地: http://localhost:8000")
        print(f"   公网: {public_url}")
        print(f"\n⚠️ 注意: ngrok免费版有连接数限制")
        print(f"💡 建议: 考虑升级到付费版或使用其他内网穿透服务")
        
        # 保持运行
        print(f"\n按Ctrl+C停止ngrok隧道...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n👋 ngrok隧道已停止")
    else:
        print(f"\n❌ ngrok设置失败")
        print(f"💡 请检查:")
        print(f"   1. ngrok是否正确安装")
        print(f"   2. 是否已设置authtoken")
        print(f"   3. 网络连接是否正常")

if __name__ == "__main__":
    main()
