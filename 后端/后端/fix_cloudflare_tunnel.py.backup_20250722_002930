#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare隧道修复脚本
解决522连接超时错误
"""

import subprocess
import time
import requests
import json
from datetime import datetime

class CloudflareTunnelFixer:
    def __init__(self):
        self.domain = "aigupiao.me"
        self.tunnel_name = "aigupiao"
        self.local_port = 8081
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_command(self, command, timeout=30):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令超时"
        except Exception as e:
            return False, "", str(e)
    
    def check_tunnel_status(self):
        """检查隧道状态"""
        self.log("🔍 检查隧道状态...")
        success, stdout, stderr = self.run_command(f"cloudflared.exe tunnel info {self.tunnel_name}")
        
        if success:
            self.log("✅ 隧道状态正常")
            return True
        else:
            self.log(f"❌ 隧道状态异常: {stderr}")
            return False
    
    def restart_tunnel(self):
        """重启隧道"""
        self.log("🔄 重启Cloudflare隧道...")
        
        # 停止现有隧道进程
        self.log("停止现有隧道进程...")
        self.run_command("taskkill /f /im cloudflared.exe", timeout=10)
        time.sleep(2)
        
        # 重新启动隧道
        self.log("启动新的隧道进程...")
        command = f"start \"Cloudflare隧道\" cloudflared.exe tunnel run {self.tunnel_name}"
        success, stdout, stderr = self.run_command(command)
        
        if success:
            self.log("✅ 隧道重启成功")
            time.sleep(5)  # 等待隧道建立连接
            return True
        else:
            self.log(f"❌ 隧道重启失败: {stderr}")
            return False
    
    def test_local_server(self):
        """测试本地服务器"""
        self.log("🔍 测试本地服务器...")
        try:
            response = requests.get(f"http://localhost:{self.local_port}/api/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ 本地服务器正常")
                return True
            else:
                self.log(f"❌ 本地服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 本地服务器连接失败: {e}")
            return False
    
    def test_domain_access(self):
        """测试域名访问"""
        self.log("🔍 测试域名访问...")
        
        for protocol in ['http', 'https']:
            try:
                url = f"{protocol}://{self.domain}/api/health"
                self.log(f"测试 {url}...")
                
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    self.log(f"✅ {protocol.upper()}访问成功")
                    return True
                else:
                    self.log(f"❌ {protocol.upper()}访问失败: {response.status_code}")
            except Exception as e:
                self.log(f"❌ {protocol.upper()}访问异常: {e}")
        
        return False
    
    def clear_cloudflare_cache(self):
        """清除Cloudflare缓存的说明"""
        self.log("\n💡 如果问题仍然存在，请手动清除Cloudflare缓存:")
        self.log("1. 登录 https://dash.cloudflare.com")
        self.log("2. 选择域名 aigupiao.me")
        self.log("3. 进入 '缓存' 标签页")
        self.log("4. 点击 '清除所有内容'")
        self.log("5. 等待5-10分钟后重试")
    
    def show_manual_dns_fix(self):
        """显示手动DNS修复说明"""
        self.log("\n🔧 手动DNS修复说明:")
        self.log("如果自动修复失败，请手动配置Cloudflare DNS:")
        self.log("1. 登录 https://dash.cloudflare.com")
        self.log("2. 选择域名 aigupiao.me")
        self.log("3. 进入 'DNS' 标签页")
        self.log("4. 删除现有的A记录")
        self.log("5. 添加CNAME记录:")
        self.log("   类型: CNAME")
        self.log("   名称: @")
        self.log(f"   内容: {self.tunnel_name}.cfargotunnel.com")
        self.log("   代理状态: 已代理 (橙色云朵)")
        self.log("6. 保存并等待DNS传播(5-10分钟)")
    
    def run_full_fix(self):
        """运行完整修复流程"""
        self.log("🚀 开始Cloudflare隧道修复...")
        self.log("="*50)
        
        # 1. 检查本地服务器
        if not self.test_local_server():
            self.log("❌ 本地服务器异常，请先修复本地服务器")
            return False
        
        # 2. 检查隧道状态
        tunnel_ok = self.check_tunnel_status()
        
        # 3. 如果隧道有问题，重启隧道
        if not tunnel_ok:
            if not self.restart_tunnel():
                self.log("❌ 隧道重启失败")
                return False
        
        # 4. 等待一段时间让隧道稳定
        self.log("⏳ 等待隧道稳定...")
        time.sleep(10)
        
        # 5. 测试域名访问
        if self.test_domain_access():
            self.log("🎉 修复成功！域名访问正常")
            return True
        else:
            self.log("❌ 域名访问仍然失败")
            self.clear_cloudflare_cache()
            self.show_manual_dns_fix()
            return False

if __name__ == "__main__":
    fixer = CloudflareTunnelFixer()
    fixer.run_full_fix()
