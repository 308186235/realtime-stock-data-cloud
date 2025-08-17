#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare隧道诊断工具
"""

import requests
import socket
import subprocess
import time
import json
from datetime import datetime

class CloudflareDiagnostic:
    def __init__(self):
        self.domain = "aigupiao.me"
        self.local_port = 8081
        self.results = {}
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def test_local_server(self):
        """测试本地服务器"""
        self.log("🔍 测试本地服务器...")
        try:
            response = requests.get(f"http://localhost:{self.local_port}/api/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ 本地服务器正常")
                self.results['local_server'] = True
                return True
            else:
                self.log(f"❌ 本地服务器响应异常: {response.status_code}")
                self.results['local_server'] = False
                return False
        except Exception as e:
            self.log(f"❌ 本地服务器连接失败: {e}")
            self.results['local_server'] = False
            return False
    
    def test_dns_resolution(self):
        """测试DNS解析"""
        self.log("🔍 测试DNS解析...")
        try:
            ips = socket.gethostbyname_ex(self.domain)[2]
            self.log(f"✅ DNS解析成功: {ips}")
            self.results['dns_resolution'] = True
            self.results['dns_ips'] = ips
            return True
        except Exception as e:
            self.log(f"❌ DNS解析失败: {e}")
            self.results['dns_resolution'] = False
            return False
    
    def test_tunnel_status(self):
        """测试隧道状态"""
        self.log("🔍 测试Cloudflare隧道状态...")
        try:
            result = subprocess.run(
                ["cloudflared.exe", "tunnel", "info", "aigupiao"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.log("✅ 隧道状态正常")
                self.results['tunnel_status'] = True
                return True
            else:
                self.log(f"❌ 隧道状态异常: {result.stderr}")
                self.results['tunnel_status'] = False
                return False
        except Exception as e:
            self.log(f"❌ 隧道状态检查失败: {e}")
            self.results['tunnel_status'] = False
            return False
    
    def test_domain_access(self):
        """测试域名访问"""
        self.log("🔍 测试域名访问...")
        
        # 测试HTTP
        try:
            response = requests.get(f"http://{self.domain}/api/health", timeout=10)
            self.log(f"HTTP访问: {response.status_code}")
            self.results['http_access'] = response.status_code
        except Exception as e:
            self.log(f"❌ HTTP访问失败: {e}")
            self.results['http_access'] = False
        
        # 测试HTTPS
        try:
            response = requests.get(f"https://{self.domain}/api/health", timeout=10)
            self.log(f"HTTPS访问: {response.status_code}")
            self.results['https_access'] = response.status_code
            if response.status_code == 200:
                self.log("✅ HTTPS访问成功")
                return True
        except Exception as e:
            self.log(f"❌ HTTPS访问失败: {e}")
            self.results['https_access'] = False
        
        return False
    
    def test_port_connectivity(self):
        """测试端口连通性"""
        self.log("🔍 测试端口连通性...")
        
        # 测试本地端口
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', self.local_port))
            sock.close()
            
            if result == 0:
                self.log(f"✅ 本地端口 {self.local_port} 可访问")
                self.results['local_port'] = True
            else:
                self.log(f"❌ 本地端口 {self.local_port} 不可访问")
                self.results['local_port'] = False
        except Exception as e:
            self.log(f"❌ 端口测试失败: {e}")
            self.results['local_port'] = False
    
    def generate_report(self):
        """生成诊断报告"""
        self.log("\n" + "="*50)
        self.log("📊 诊断报告")
        self.log("="*50)
        
        for key, value in self.results.items():
            status = "✅" if value else "❌"
            self.log(f"{status} {key}: {value}")
        
        # 生成建议
        self.log("\n💡 建议:")
        
        if not self.results.get('local_server'):
            self.log("- 检查本地服务器是否正常运行")
        
        if not self.results.get('tunnel_status'):
            self.log("- 重启Cloudflare隧道")
        
        if not self.results.get('https_access'):
            self.log("- 检查Cloudflare SSL/TLS设置")
            self.log("- 确认隧道配置正确")
        
        # 保存报告
        with open('diagnostic_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.log("\n📄 详细报告已保存到: diagnostic_report.json")
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        self.log("🚀 开始Cloudflare隧道诊断...")
        self.log("="*50)
        
        self.test_local_server()
        time.sleep(1)
        
        self.test_port_connectivity()
        time.sleep(1)
        
        self.test_dns_resolution()
        time.sleep(1)
        
        self.test_tunnel_status()
        time.sleep(1)
        
        self.test_domain_access()
        time.sleep(1)
        
        self.generate_report()

if __name__ == "__main__":
    diagnostic = CloudflareDiagnostic()
    diagnostic.run_full_diagnostic()
