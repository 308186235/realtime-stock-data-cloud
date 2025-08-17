# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Tunnel 完整诊断工具
基于MCP检索的问题排查所有可能的故障点
"""

import subprocess
import socket
import requests
import time
import json
from datetime import datetime

class CloudflareTunnelDiagnostic:
    def __init__(self):
        self.domain = "aigupiao.me"
        self.local_port = 8000
        self.results = {}
        
    def log(self, message, level="INFO"):
        """日志输出"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m", 
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{colors['RESET']}")
    
    def run_command(self, command, timeout=15):
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
    
    def check_cloudflared_installation(self):
        """检查cloudflared是否安装"""
        self.log("🔍 检查cloudflared安装状态...")
        
        success, stdout, stderr = self.run_command("cloudflared.exe --version")
        if success:
            version = stdout.strip()
            self.log(f"✅ cloudflared已安装: {version}", "SUCCESS")
            self.results['cloudflared_installed'] = True
            return True
        else:
            self.log("❌ cloudflared未安装或不在PATH中", "ERROR")
            self.results['cloudflared_installed'] = False
            return False
    
    def check_dns_resolution(self):
        """检查DNS解析"""
        self.log("🔍 检查DNS解析...")
        
        try:
            ip_address = socket.gethostbyname(self.domain)
            self.log(f"✅ DNS解析成功: {self.domain} -> {ip_address}", "SUCCESS")
            self.results['dns_resolution'] = {
                'status': 'SUCCESS',
                'ip_address': ip_address
            }
            return ip_address
        except socket.gaierror as e:
            self.log(f"❌ DNS解析失败: {e}", "ERROR")
            self.results['dns_resolution'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return None
    
    def check_tunnel_authentication(self):
        """检查隧道认证状态"""
        self.log("🔍 检查Cloudflare认证状态...")
        
        # 检查认证文件是否存在
        import os
        cert_path = os.path.expanduser("~/.cloudflared/cert.pem")
        
        if os.path.exists(cert_path):
            self.log("✅ 找到认证证书文件", "SUCCESS")
            self.results['authentication'] = True
            return True
        else:
            self.log("❌ 未找到认证证书,需要先登录", "ERROR")
            self.log("💡 运行: cloudflared tunnel login", "INFO")
            self.results['authentication'] = False
            return False
    
    def check_tunnel_exists(self):
        """检查隧道是否存在"""
        self.log("🔍 检查隧道配置...")
        
        # 尝试获取隧道信息
        success, stdout, stderr = self.run_command("cloudflared.exe tunnel list")
        
        if success:
            if "aigupiao" in stdout:
                self.log("✅ 找到aigupiao隧道", "SUCCESS")
                self.results['tunnel_exists'] = True
                return True
            else:
                self.log("⚠️ 未找到aigupiao隧道", "WARNING")
                self.results['tunnel_exists'] = False
                return False
        else:
            self.log(f"❌ 无法获取隧道列表: {stderr}", "ERROR")
            self.results['tunnel_exists'] = False
            return False
    
    def check_tunnel_running(self):
        """检查隧道是否在运行"""
        self.log("🔍 检查隧道运行状态...")
        
        # 检查进程
        success, stdout, stderr = self.run_command("tasklist | findstr cloudflared")
        
        if success and "cloudflared.exe" in stdout:
            self.log("✅ cloudflared进程正在运行", "SUCCESS")
            self.results['tunnel_running'] = True
            return True
        else:
            self.log("❌ cloudflared进程未运行", "ERROR")
            self.results['tunnel_running'] = False
            return False
    
    def check_local_server(self):
        """检查本地服务器"""
        self.log("🔍 检查本地API服务器...")
        
        try:
            response = requests.get(f"http://127.0.0.1:{self.local_port}/api/auth/test", timeout=5)
            if response.status_code == 200:
                self.log("✅ 本地API服务器正常", "SUCCESS")
                self.results['local_server'] = True
                return True
            else:
                self.log(f"❌ 本地API服务器响应异常: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ 本地API服务器连接失败: {e}", "ERROR")
        
        self.results['local_server'] = False
        return False
    
    def test_domain_access(self):
        """测试域名访问"""
        self.log("🔍 测试域名访问...")
        
        test_urls = [
            f"https://{self.domain}",
            f"https://{self.domain}/api/auth/test",
            f"http://{self.domain}",
            f"http://{self.domain}/api/auth/test"
        ]
        
        for url in test_urls:
            try:
                self.log(f"测试: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {url} 访问成功", "SUCCESS")
                    self.results['domain_access'] = True
                    return True
                else:
                    self.log(f"❌ {url} 响应: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ {url} 失败: {e}", "ERROR")
        
        self.results['domain_access'] = False
        return False
    
    def check_cloudflare_quick_tunnel(self):
        """检查快速隧道功能"""
        self.log("🔍 测试Cloudflare快速隧道...")
        
        try:
            # 启动快速隧道(非阻塞)
            process = subprocess.Popen(
                ["cloudflared.exe", "tunnel", "--url", f"http://localhost:{self.local_port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.log("⏳ 等待快速隧道启动...")
            time.sleep(10)
            
            if process.poll() is None:
                self.log("✅ 快速隧道启动成功", "SUCCESS")
                # 终止进程
                process.terminate()
                self.results['quick_tunnel'] = True
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"❌ 快速隧道启动失败: {stderr}", "ERROR")
                self.results['quick_tunnel'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ 快速隧道测试失败: {e}", "ERROR")
            self.results['quick_tunnel'] = False
            return False
    
    def generate_diagnosis_report(self):
        """生成诊断报告"""
        self.log("\n" + "="*60)
        self.log("📊 Cloudflare Tunnel 诊断报告", "INFO")
        self.log("="*60)
        
        # 基本检查
        self.log("\n🔧 基础环境:")
        self.log(f"  cloudflared安装: {'✅' if self.results.get('cloudflared_installed') else '❌'}")
        self.log(f"  本地API服务器: {'✅' if self.results.get('local_server') else '❌'}")
        self.log(f"  DNS解析: {'✅' if self.results.get('dns_resolution', {}).get('status') == 'SUCCESS' else '❌'}")
        
        # 隧道状态
        self.log("\n🌐 隧道状态:")
        self.log(f"  认证状态: {'✅' if self.results.get('authentication') else '❌'}")
        self.log(f"  隧道配置: {'✅' if self.results.get('tunnel_exists') else '❌'}")
        self.log(f"  隧道运行: {'✅' if self.results.get('tunnel_running') else '❌'}")
        self.log(f"  快速隧道: {'✅' if self.results.get('quick_tunnel') else '❌'}")
        
        # 访问测试
        self.log("\n🌍 访问测试:")
        self.log(f"  域名访问: {'✅' if self.results.get('domain_access') else '❌'}")
        
        # 问题诊断
        self.log("\n🔍 问题分析:")
        
        if not self.results.get('cloudflared_installed'):
            self.log("  ❌ cloudflared未安装 - 需要下载安装", "ERROR")
        
        if not self.results.get('local_server'):
            self.log("  ❌ 本地服务器未运行 - 需要启动API服务器", "ERROR")
        
        if not self.results.get('authentication'):
            self.log("  ❌ 未认证 - 需要运行: cloudflared tunnel login", "ERROR")
        
        if not self.results.get('tunnel_exists'):
            self.log("  ❌ 隧道未配置 - 需要创建隧道", "ERROR")
        
        if not self.results.get('tunnel_running'):
            self.log("  ❌ 隧道未运行 - 需要启动隧道", "ERROR")
        
        if self.results.get('dns_resolution', {}).get('status') != 'SUCCESS':
            self.log("  ❌ DNS解析失败 - 域名配置问题", "ERROR")
        
        # 建议方案
        self.log("\n💡 建议方案:")
        
        if self.results.get('quick_tunnel'):
            self.log("  ✅ 推荐使用快速隧道(无需域名配置)", "SUCCESS")
            self.log("  📝 命令: cloudflared tunnel --url http://localhost:8000", "INFO")
        elif self.results.get('cloudflared_installed') and self.results.get('local_server'):
            self.log("  ⚠️ 可以尝试快速隧道", "WARNING")
            self.log("  📝 命令: cloudflared tunnel --url http://localhost:8000", "INFO")
        else:
            self.log("  ❌ 需要先解决基础环境问题", "ERROR")
        
        return self.results
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        self.log("🚀 开始Cloudflare Tunnel诊断...")
        
        # 1. 基础检查
        self.check_cloudflared_installation()
        self.check_local_server()
        self.check_dns_resolution()
        
        # 2. 隧道检查
        if self.results.get('cloudflared_installed'):
            self.check_tunnel_authentication()
            self.check_tunnel_exists()
            self.check_tunnel_running()
            self.check_cloudflare_quick_tunnel()
        
        # 3. 访问测试
        self.test_domain_access()
        
        # 4. 生成报告
        return self.generate_diagnosis_report()

if __name__ == "__main__":
    diagnostic = CloudflareTunnelDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # 保存结果
    with open('cloudflare_diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 诊断结果已保存到: cloudflare_diagnostic_results.json")
